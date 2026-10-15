"""Review downloads preserve ownership, selection freshness and draft semantics."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    edit_creative_variant_for_owner,
    generate_creative_version_for_owner,
    select_preferred_creative_for_owner,
)
from growthtwin.modules.campaigns.views import SYNTHETIC_CAMPAIGN
from growthtwin.modules.workspaces.models import Workspace


class CampaignDownloadTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="download-owner")
        self.other = get_user_model().objects.create_user(username="download-other")
        workspace = Workspace.objects.create(owner=self.owner, name="Synthetic")
        self.draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=workspace.pk,
            **SYNTHETIC_CAMPAIGN,
            flight_start=date(2026, 10, 15),
            flight_end=date(2026, 10, 29),
        )
        self.draft, version = generate_creative_version_for_owner(
            owner=self.owner, draft_id=self.draft.pk
        )
        self.variant = version["variants"][0]
        for index, other_variant in enumerate(version["variants"][1:]):
            other_variant["body"] = f"Unselected synthetic copy {index}"
        self.draft.save(update_fields=["creative_versions"])
        self.draft = select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=1,
            key=self.variant["key"],
        )
        self.url = reverse("campaigns:download", args=[self.draft.pk])
        self.query = {"version": "1", "variant": self.variant["key"]}
        self.client.force_login(self.owner)

    def test_owner_downloads_only_selected_copy_without_mutating_history(self):
        before = self.draft.creative_versions
        response = self.client.get(self.url, self.query)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertIn("attachment;", response["Content-Disposition"])
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        text = response.content.decode("utf-8")
        for expected in (
            self.variant["body"],
            "5000.00 TRY",
            "2026-10-15",
            "2026-10-29",
            "YAYINLANMADI",
            "Google Ads'e aktarılacak bir reklam paketi değildir",
            "karakter sınırlarına uyduğu varsayılamaz",
            "hesaplanmadı",
        ):
            self.assertIn(expected, text)
        self.assertNotIn(self.owner.username, text)
        self.assertNotIn("source_hash", text)
        for variant in before[-1]["variants"][1:]:
            self.assertNotIn(f"Metin: {variant['body']}\n", text)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.creative_versions, before)

    def test_other_owner_and_missing_campaign_return_404(self):
        self.client.force_login(self.other)
        response = self.client.get(self.url, self.query)
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(self.variant["body"].encode(), response.content)
        self.assertEqual(
            self.client.get(reverse("campaigns:download", args=[999999])).status_code,
            404,
        )

    def test_anonymous_download_requires_login(self):
        self.client.logout()
        response = self.client.get(self.url, self.query)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("no-store", response["Cache-Control"])

    def test_missing_or_stale_selection_does_not_download(self):
        for query in (
            {},
            {"version": "bad"},
            self.query | {"version": "2"},
            self.query | {"variant": "other"},
        ):
            with self.subTest(query=query):
                response = self.client.get(self.url, query)
                self.assertRedirects(
                    response,
                    reverse("campaigns:detail", args=[self.draft.pk])
                    + "?download=stale",
                )
                self.assertNotIn("Content-Disposition", response)

    def test_source_change_blocks_old_download(self):
        self.draft.brand_name = "Changed synthetic source"
        self.draft.save(update_fields=["brand_name"])
        response = self.client.get(self.url, self.query)
        self.assertEqual(response.status_code, 302)
        detail = self.client.get(reverse("campaigns:detail", args=[self.draft.pk]))
        self.assertNotContains(detail, "Seçili taslağı indir (.txt)")

    def test_edit_requires_new_selection_and_rejects_old_link(self):
        edit_creative_variant_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=1,
            key=self.variant["key"],
            headline="Sentetik yeni başlık",
            body="Sentetik yeni metin",
            call_to_action="İncele",
        )
        self.assertEqual(self.client.get(self.url, self.query).status_code, 302)
        select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=2,
            key=self.variant["key"],
        )
        self.assertEqual(self.client.get(self.url, self.query).status_code, 302)
        response = self.client.get(self.url, self.query | {"version": "2"})
        self.assertContains(response, "Sentetik yeni metin")

    def test_download_rejects_post(self):
        self.assertEqual(self.client.post(self.url, self.query).status_code, 405)

    def test_changed_preference_rejects_old_link_and_missing_preference(self):
        other_key = self.draft.creative_versions[-1]["variants"][1]["key"]
        select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=1,
            key=other_key,
        )
        self.assertEqual(self.client.get(self.url, self.query).status_code, 302)
        self.assertEqual(
            self.client.get(self.url, self.query | {"variant": other_key}).status_code,
            200,
        )
        self.draft.preferred_creative_key = ""
        self.draft.preferred_creative_version = None
        self.draft.save(
            update_fields=["preferred_creative_key", "preferred_creative_version"]
        )
        self.assertEqual(self.client.get(self.url, self.query).status_code, 302)
