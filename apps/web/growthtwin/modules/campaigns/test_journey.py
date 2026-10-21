"""Read-only stage navigation, ownership and honest stored TEST metadata."""

from copy import deepcopy
from datetime import date
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from growthtwin.modules.workspaces.models import Workspace

from .models import CampaignRehearsal, GoogleDraftApproval, GoogleDraftDispatch
from .services import (
    create_campaign_draft_for_owner,
    generate_creative_version_for_owner,
    select_preferred_creative_for_owner,
)
from .views import SYNTHETIC_CAMPAIGN


class CampaignJourneyTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="journey-campaign-owner"
        )
        self.other = get_user_model().objects.create_user(
            username="journey-campaign-other"
        )
        self.workspace = Workspace.objects.create(owner=self.owner, name="Örnek alan")
        self.draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **SYNTHETIC_CAMPAIGN,
            flight_start=date(2026, 10, 22),
            flight_end=date(2026, 11, 5),
        )
        self.draft, self.version = generate_creative_version_for_owner(
            owner=self.owner, draft_id=self.draft.pk
        )
        self.url = reverse("campaigns:journey", args=[self.draft.pk])
        self.client.force_login(self.owner)

    def choose(self):
        self.draft = select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=self.version["version"],
            key=self.version["variants"][0]["key"],
        )

    def approval(self):
        return GoogleDraftApproval.objects.create(
            draft=self.draft,
            fingerprint="f" * 64,
            target_key="t" * 64,
            payload_json="forbidden-copy",
        )

    def dispatch(self, state="stopped", observed="PAUSED"):
        return GoogleDraftDispatch.objects.create(
            draft=self.draft,
            approval=self.approval(),
            operation_id=uuid4(),
            configuration_key="k" * 64,
            payload_json="forbidden-copy",
            state=state,
            observed_status=observed,
        )

    def test_owner_sees_six_distinct_stages_and_next_creative_action(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        journey = response.context["journey"]
        self.assertEqual(
            [stage.key for stage in journey["stages"]],
            ["campaign", "creative", "plan", "approval", "dispatch", "report"],
        )
        self.assertContains(response, "Güncel reklam metnini seç")
        self.assertContains(response, "Güncel metin seçimi gerekli")
        self.assertContains(response, "Onay kaydı yok")
        self.assertContains(response, "Henüz gönderim kaydı yok")
        self.assertContains(response, "Gerçek veri bağlı değil")
        self.assertContains(response, "5.000,00 TRY")
        self.assertNotContains(response, "<script")
        self.assertContains(response, 'aria-label="Kampanyanın altı adımı"')

    def test_current_preference_does_not_become_publication_approval(self):
        self.choose()
        response = self.client.get(self.url)
        self.assertContains(response, "Güncel inceleme tercihi kayıtlı")
        self.assertContains(response, "Onay kaydı yok")
        self.assertContains(response, "Planı ve onay kapsamını incele")
        self.assertContains(response, "Metin tercihi yayın onayı değildir")

    def test_changed_source_or_selection_version_needs_current_selection(self):
        self.choose()
        self.draft.brief += " Updated synthetic example."
        self.draft.save(update_fields=["brief"])
        self.assertContains(self.client.get(self.url), "Güncel metin seçimi gerekli")
        self.draft, _ = generate_creative_version_for_owner(
            owner=self.owner, draft_id=self.draft.pk
        )
        self.assertContains(self.client.get(self.url), "Güncel metin seçimi gerekli")

    def test_missing_plan_information_is_not_ready(self):
        self.draft.destination_url = ""
        self.draft.save(update_fields=["destination_url"])
        response = self.client.get(self.url)
        self.assertContains(response, "Plan bilgileri eksik")
        self.assertContains(response, "Planın eksiklerini tamamla")

    def test_stored_approval_is_not_declared_current_even_after_source_change(self):
        self.approval()
        self.draft.brief += " Changed synthetic source."
        self.draft.save(update_fields=["brief"])
        response = self.client.get(self.url)
        self.assertContains(response, "Onay kaydı var · Güncelliği kontrol edilmeli")
        self.assertContains(response, "eşleşmesi burada doğrulanmaz")
        self.assertNotContains(response, "forbidden-copy")

    def test_stored_dispatch_has_priority_over_current_creative_changes(self):
        self.dispatch()
        self.draft.brief += " Source changed after TEST intent."
        self.draft.save(update_fields=["brief"])
        response = self.client.get(self.url)
        self.assertContains(response, "Kayıtta durduruldu (TEST)")
        self.assertContains(response, "Önce kayıtlı TEST işlemini kontrol et")
        self.assertContains(response, "eski metin/plan sürümüne ait olabilir")
        self.assertContains(response, "canlı sorgu yapılmadı")
        self.assertEqual(response.context["journey"]["next_href"], "#dispatch-stage")
        self.assertNotContains(response, "forbidden-copy")

    def test_unknown_inconsistent_or_uncertain_dispatch_never_looks_successful(self):
        row = self.dispatch(state="uncertain", observed="")
        for state, observed, label in (
            ("uncertain", "", "Kayıtlı sonuç belirsiz"),
            ("paused", "PAUSED", "Kayıtta duraklatıldı (TEST)"),
            ("stopped", "", "Kayıt var · Durum doğrulanmalı"),
            ("forbidden-copy", "ENABLED", "Kayıt var · Durum doğrulanmalı"),
        ):
            row.state, row.observed_status = state, observed
            row.save(update_fields=["state", "observed_status"])
            response = self.client.get(self.url)
            self.assertContains(response, label)
            self.assertNotContains(response, "forbidden-copy")
            self.assertNotContains(response, "ENABLED")

    def test_anonymous_foreign_missing_and_inactive_access_are_denied(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.url).status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(
            self.client.get(reverse("campaigns:journey", args=[999999])).status_code,
            404,
        )
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_get_head_and_queries_do_not_write_or_fetch_payloads(self):
        self.dispatch()
        before = deepcopy(self.draft.creative_versions)
        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(
                self.url, {"state": "ENABLED", "proof": "forbidden-copy"}
            )
        queries = [query["sql"].upper() for query in captured]
        self.assertFalse(
            any(
                sql.lstrip().startswith(("INSERT", "UPDATE", "DELETE"))
                for sql in queries
            )
        )
        self.assertFalse(any("PAYLOAD_JSON" in sql for sql in queries))
        self.assertEqual(self.client.head(self.url).content, b"")
        self.assertNotContains(response, "forbidden-copy")
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.creative_versions, before)
        self.assertFalse(CampaignRehearsal.objects.exists())
        self.assertEqual(GoogleDraftApproval.objects.count(), 1)
        self.assertEqual(GoogleDraftDispatch.objects.count(), 1)

    def test_post_put_patch_delete_are_405(self):
        for method in (
            self.client.post,
            self.client.put,
            self.client.patch,
            self.client.delete,
        ):
            self.assertEqual(method(self.url).status_code, 405)
        self.assertEqual(GoogleDraftApproval.objects.count(), 0)
        self.assertEqual(GoogleDraftDispatch.objects.count(), 0)

    def test_private_noindex_headers_cover_page_and_errors(self):
        for response in (
            self.client.get(self.url),
            self.client.post(self.url),
            self.client.get(reverse("campaigns:journey", args=[999999])),
        ):
            self.assertIn("no-store", response["Cache-Control"])
            self.assertIn("private", response["Cache-Control"])
            self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    @override_settings(
        GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True, DEBUG=False, ALLOWED_HOSTS=["127.0.0.1"]
    )
    def test_test_links_require_the_existing_exact_loopback_owner_boundary(self):
        self.choose()
        with override_settings(
            GOOGLE_ADS_LOCAL_OWNER_ID=str(self.owner.pk),
            GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(self.workspace.pk),
        ):
            good = dict(HTTP_HOST="127.0.0.1:8002", REMOTE_ADDR="127.0.0.1")
            response = self.client.get(self.url, **good)
            self.assertTrue(response.context["journey"]["test_controls_available"])
            self.assertContains(
                response, reverse("google-local-draft-review") + "?draft="
            )
            for changes in (
                dict(HTTP_HOST="127.0.0.1:8011"),
                dict(REMOTE_ADDR="192.0.2.1"),
                dict(HTTP_X_FORWARDED_FOR="127.0.0.1"),
                dict(HTTP_FORWARDED="for=127.0.0.1"),
            ):
                response = self.client.get(self.url, **(good | changes))
                self.assertFalse(response.context["journey"]["test_controls_available"])
            with override_settings(GOOGLE_ADS_LOCAL_OWNER_ID=str(self.other.pk)):
                self.assertFalse(
                    self.client.get(self.url, **good).context["journey"][
                        "test_controls_available"
                    ]
                )
            with override_settings(DEBUG=True):
                self.assertFalse(
                    self.client.get(self.url, **good).context["journey"][
                        "test_controls_available"
                    ]
                )

    def test_no_credentials_token_calls_or_provider_verification_on_overview(self):
        with (
            patch(
                "growthtwin.modules.connections.backend._read",
                side_effect=AssertionError,
            ),
            patch(
                "growthtwin.modules.connections.backend._post",
                side_effect=AssertionError,
            ),
            patch(
                "growthtwin.modules.connections.verification.configuration_key",
                side_effect=AssertionError,
            ),
            patch(
                "growthtwin.modules.connections.draft_dispatch.perform",
                side_effect=AssertionError,
            ),
        ):
            self.assertEqual(self.client.get(self.url).status_code, 200)

    @override_settings(
        GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True, DEBUG=False, ALLOWED_HOSTS=["127.0.0.1"]
    )
    def test_missing_selection_or_dispatch_explains_unavailable_test_links(self):
        with override_settings(
            GOOGLE_ADS_LOCAL_OWNER_ID=str(self.owner.pk),
            GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(self.workspace.pk),
        ):
            response = self.client.get(
                self.url, HTTP_HOST="127.0.0.1:8002", REMOTE_ADDR="127.0.0.1"
            )
            stages = response.context["journey"]["stages"]
            self.assertIsNone(stages[3].href)
            self.assertIsNone(stages[4].href)
            self.assertContains(response, "Önce güncel metni seç ve planı tamamla.")
            self.assertContains(
                response, "Önce TEST paketini incele ve ayrı gönderim onayını ver."
            )
            self.assertNotContains(response, "Bu ortamda TEST kontrolleri açık değil.")

    def test_list_detail_report_links_and_anchor_targets_are_present(self):
        for name, args in (
            ("campaigns:list", []),
            ("campaigns:detail", [self.draft.pk]),
            ("campaigns:report", [self.draft.pk]),
        ):
            self.assertContains(self.client.get(reverse(name, args=args)), self.url)
        detail = self.client.get(reverse("campaigns:detail", args=[self.draft.pk]))
        self.assertContains(detail, 'id="creative-variants-title"')
        self.assertContains(detail, 'id="plan-summary-title"')

    def test_currency_is_displayed_from_draft_not_inferred_as_try(self):
        self.draft.currency = "USD"
        self.draft.save(update_fields=["currency"])
        self.assertContains(self.client.get(self.url), "5.000,00 USD")
