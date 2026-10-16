"""HTTP boundaries for the synthetic rehearsal controls."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from growthtwin.modules.campaigns.models import CampaignRehearsal
from growthtwin.modules.campaigns.rehearsal import rehearsal_context
from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    generate_creative_version_for_owner,
    select_preferred_creative_for_owner,
)
from growthtwin.modules.campaigns.views import SYNTHETIC_CAMPAIGN
from growthtwin.modules.workspaces.models import Workspace


class CampaignRehearsalViewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="rehearsal-owner")
        self.other = get_user_model().objects.create_user(username="rehearsal-other")
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
        self.draft = select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=1,
            key=version["variants"][0]["key"],
        )
        self.url = reverse("campaigns:rehearsal", args=[self.draft.pk])
        self.detail_url = reverse("campaigns:detail", args=[self.draft.pk])
        self.payload = {
            "action": "start_failure",
            "revision": 0,
            "fingerprint": rehearsal_context(self.draft)["fingerprint"],
        }
        self.client.force_login(self.owner)

    def test_failure_retry_stop_flow_and_repeated_request(self):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 302)
        self.assertIn("rehearsal=updated", response.url)
        rehearsal = CampaignRehearsal.objects.get(draft=self.draft)
        self.assertEqual(rehearsal.state, "failed")
        operation = rehearsal.operation_id
        self.client.post(self.url, self.payload | {"action": "retry", "revision": 1})
        rehearsal.refresh_from_db()
        self.assertEqual(rehearsal.state, "running")
        self.assertEqual(rehearsal.operation_id, operation)
        self.assertContains(self.client.get(self.detail_url), "reklam çalışmaz")
        response = self.client.post(
            self.url, self.payload | {"action": "retry", "revision": 1}
        )
        self.assertIn("rehearsal=changed", response.url)
        self.assertEqual(rehearsal.events.count(), 2)
        self.client.post(self.url, {"action": "stop", "revision": 2})
        rehearsal.refresh_from_db()
        self.assertEqual(rehearsal.state, "stopped")
        self.assertEqual(rehearsal.events.count(), 3)

    def test_get_is_read_only_and_post_is_required(self):
        self.assertContains(self.client.get(self.detail_url), "Yayın provasını başlat")
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.assertFalse(CampaignRehearsal.objects.exists())

    def test_cross_owner_and_anonymous_requests_cannot_change_state(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 404)
        self.client.logout()
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertFalse(CampaignRehearsal.objects.exists())

    def test_csrf_is_required(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)
        self.assertEqual(csrf_client.post(self.url, self.payload).status_code, 403)
        self.assertFalse(CampaignRehearsal.objects.exists())

    def test_invalid_actions_versions_and_fingerprints_create_no_state(self):
        for override in (
            {"action": "publish"},
            {"revision": "bad"},
            {"fingerprint": "old"},
        ):
            with self.subTest(override=override):
                response = self.client.post(self.url, self.payload | override)
                self.assertIn("rehearsal=changed", response.url)
                self.assertFalse(CampaignRehearsal.objects.exists())
