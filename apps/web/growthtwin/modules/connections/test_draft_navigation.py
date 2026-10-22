"""Protected TEST presentation without credentials or remote requests."""

import json
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from growthtwin.modules.campaigns.models import GoogleDraftApproval, GoogleDraftDispatch

from . import test_draft_review as fixture


class DraftNavigationTests(TestCase):
    setUp = fixture.DraftReviewTests.setUp
    review_data = fixture.DraftReviewTests.review
    approve = fixture.DraftReviewTests.submit

    def get(self, path="/connections/google/draft-status/", **headers):
        return self.client.get(
            path, {"draft": self.draft.pk}, HTTP_HOST="127.0.0.1:8002", **headers
        )

    def store(self, state="stopped", observed="PAUSED"):
        approval = GoogleDraftApproval.objects.create(
            draft=self.draft,
            fingerprint="f" * 64,
            target_key="target-key",
            payload_json="not-readable",
        )
        return GoogleDraftDispatch.objects.create(
            draft=self.draft,
            approval=approval,
            operation_id=uuid4(),
            configuration_key="target-key",
            payload_json="not-readable",
            state=state,
            observed_status=observed,
        )

    def test_review_navigation_is_scoped_and_keeps_consent_form(self):
        response = self.get("/connections/google/draft-review/")
        self.assertEqual(response.status_code, 200)
        for name in ("campaigns:journey", "campaigns:detail", "campaigns:report"):
            self.assertContains(response, reverse(name, args=[self.draft.pk]))
        self.assertContains(response, 'aria-label="Kampanya içinde gezin"')
        self.assertContains(response, 'name="confirm" value="yes" required')
        self.assertContains(response, 'action="/connections/google/draft-approve/"')
        self.assertContains(
            response, "TEST onayı gerçek reklam yayını veya harcama izni değildir"
        )
        self.assertContains(
            response, '<meta name="robots" content="noindex, nofollow">'
        )
        self.assertNotContains(response, "<script")

    def test_status_without_intent_has_no_dispatch_buttons(self):
        response = self.get()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Henüz gönderim kaydı yok")
        self.assertNotContains(response, 'action="/connections/google/draft-dispatch/"')
        self.assertNotContains(response, 'value="create"')

    def test_status_get_does_not_read_payload_credentials_or_write(self):
        self.store()
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
                "growthtwin.modules.connections.draft_dispatch.perform",
                side_effect=AssertionError,
            ),
            CaptureQueriesContext(connection) as captured,
        ):
            response = self.get()
        self.mock_target.assert_not_called()
        queries = [x["sql"].upper() for x in captured]
        self.assertFalse(any("PAYLOAD_JSON" in sql for sql in queries))
        self.assertFalse(
            any(
                sql.lstrip().startswith(("INSERT", "UPDATE", "DELETE"))
                for sql in queries
            )
        )
        self.assertContains(response, "Kayıtta durduruldu (TEST)")
        self.assertContains(response, "Google’a istek gönderilmedi")
        self.assertContains(response, "eski metin/plan sürümüne ait olabilir")
        self.assertNotContains(response, "not-readable")

    def test_unknown_status_is_not_reflected_or_claimed_verified(self):
        self.store(state="unknown-private", observed="ENABLED")
        response = self.get()
        self.assertContains(response, "Kayıt var · Durum doğrulanmalı")
        self.assertNotContains(response, "unknown-private")
        self.assertNotContains(response, "ENABLED")
        self.assertNotContains(response, "Google durumu PAUSED")

    def test_status_controls_survive_changed_source_without_create(self):
        self.store(state="uncertain", observed="")
        self.draft.brief += " Changed synthetic source."
        self.draft.save(update_fields=["brief"])
        response = self.get()
        self.assertContains(response, "Kayıtlı sonuç belirsiz")
        self.assertContains(response, 'value="read"')
        self.assertContains(response, 'value="stop"')
        self.assertNotContains(response, 'value="create"')
        self.assertContains(response, "Belirsiz sonuçta yeniden gönderim oluşturulmaz")

    def test_host_forwarded_foreign_workspace_and_method_guards_remain(self):
        self.assertEqual(self.get(HTTP_X_FORWARDED_FOR="127.0.0.1").status_code, 404)
        self.assertEqual(
            self.client.get(
                "/connections/google/draft-status/",
                {"draft": self.draft.pk},
                HTTP_HOST="127.0.0.1:8011",
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.head(
                "/connections/google/draft-status/", HTTP_HOST="127.0.0.1:8002"
            ).status_code,
            405,
        )
        other = get_user_model().objects.create_user(username="foreign-nav-owner")
        self.client.force_login(other)
        self.assertEqual(self.get().status_code, 404)

    def test_dispatch_post_still_requires_csrf(self):
        self.store()
        self.get()
        with patch("growthtwin.modules.connections.draft_dispatch.perform") as perform:
            response = self.client.post(
                "/connections/google/draft-dispatch/",
                {"draft": self.draft.pk, "action": "stop"},
                HTTP_HOST="127.0.0.1:8002",
                HTTP_ORIGIN="http://127.0.0.1:8002",
            )
        self.assertEqual(response.status_code, 403)
        perform.assert_not_called()

    def test_result_labels_observation_scope_and_keeps_navigation(self):
        self.store()
        self.get()
        profile = {
            "version": "workspace-paused-test-v2-total",
            "period": "CUSTOM_PERIOD",
            "total_micros": 5000000000,
            "start": "2026-11-01",
            "end": "2026-11-15",
        }
        for state, observed, expected, status in (
            ("stopped", "PAUSED", "Bu işlemde Google TEST hesabından PAUSED", 200),
            ("uncertain", "", "Sonuç belirsiz", 409),
            ("unknown-private", "ENABLED", "Kayıtlı durum doğrulanmalı", 200),
        ):
            row = SimpleNamespace(
                state=state,
                observed_status=observed,
                payload_json=json.dumps({"test_profile": profile}),
            )
            with patch(
                "growthtwin.modules.connections.draft_dispatch.perform",
                return_value=row,
            ):
                response = self.client.post(
                    "/connections/google/draft-dispatch/",
                    {
                        "draft": self.draft.pk,
                        "action": "read",
                        "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                    },
                    HTTP_HOST="127.0.0.1:8002",
                    HTTP_ORIGIN="http://127.0.0.1:8002",
                )
            self.assertEqual(response.status_code, status)
            self.assertEqual(response["Referrer-Policy"], "same-origin")
            self.assertContains(response, expected, status_code=status)
            self.assertContains(
                response,
                reverse("campaigns:journey", args=[self.draft.pk]),
                status_code=status,
            )
            self.assertNotContains(response, "unknown-private", status_code=status)

    def test_draft_name_is_escaped_in_shared_shell(self):
        self.draft.name = '<script>alert("fixture")</script>'
        self.draft.save(update_fields=["name"])
        response = self.get()
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert")

    def test_private_headers_on_status_and_denied_requests(self):
        for response in (self.get(), self.get(HTTP_FORWARDED="for=127.0.0.1")):
            self.assertIn("no-store", response["Cache-Control"])
            self.assertIn("private", response["Cache-Control"])
            self.assertEqual(response["Referrer-Policy"], "same-origin")

    def test_incomplete_owned_review_keeps_navigation_and_409(self):
        self.draft.destination_url = ""
        self.draft.save(update_fields=["destination_url"])
        response = self.get("/connections/google/draft-review/")
        self.assertEqual(response.status_code, 409)
        self.assertContains(
            response,
            reverse("campaigns:journey", args=[self.draft.pk]),
            status_code=409,
        )
        self.assertContains(response, "İşlem tamamlanamadı", status_code=409)

    def test_rejected_owned_dispatch_keeps_navigation_without_call(self):
        self.get()
        with patch("growthtwin.modules.connections.draft_dispatch.perform") as perform:
            response = self.client.post(
                "/connections/google/draft-dispatch/",
                {
                    "draft": self.draft.pk,
                    "action": "create",
                    "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                },
                HTTP_HOST="127.0.0.1:8002",
                HTTP_ORIGIN="http://127.0.0.1:8002",
            )
        self.assertEqual(response.status_code, 409)
        perform.assert_not_called()
        self.assertContains(
            response,
            reverse("campaigns:journey", args=[self.draft.pk]),
            status_code=409,
        )

    def test_bad_approval_before_owned_draft_resolution_does_not_add_links(self):
        self.get()
        response = self.approve(
            {
                "draft": self.draft.pk,
                "confirm": "yes",
                "review": "invalid",
                "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
            }
        )
        self.assertEqual(response.status_code, 409)
        self.assertNotContains(
            response,
            reverse("campaigns:journey", args=[self.draft.pk]),
            status_code=409,
        )

    def test_validation_result_keeps_navigation_without_creating_dispatch(self):
        from django.core import signing

        from growthtwin.modules.campaigns.google_draft_payload import (
            build_draft_package,
        )

        from . import draft_review, total_budget

        self.get()
        package = build_draft_package(self.draft)
        token = signing.dumps(
            {
                "owner": str(self.owner.pk),
                "workspace": str(self.workspace.pk),
                "draft": self.draft.pk,
                "target_key": "target-key",
                "budget_key": total_budget.review_key(package),
            },
            salt=draft_review.SALT + "-total-budget",
        )
        with patch(
            "growthtwin.modules.connections.total_budget.validate",
            return_value={"total_micros": 5000000000},
        ):
            response = self.client.post(
                "/connections/google/total-budget-validate/",
                {
                    "draft": self.draft.pk,
                    "review": token,
                    "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
                },
                HTTP_HOST="127.0.0.1:8002",
                HTTP_ORIGIN="http://127.0.0.1:8002",
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, reverse("campaigns:journey", args=[self.draft.pk])
        )
        self.assertContains(response, "Yalnızca istek doğrulaması yapıldı")
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        self.assertFalse(GoogleDraftDispatch.objects.exists())
