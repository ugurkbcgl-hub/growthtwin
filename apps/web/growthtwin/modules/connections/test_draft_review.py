"""Approval binds the reviewed source, local owner and target without dispatch."""

import html
import re
from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from growthtwin.modules.campaigns.models import GoogleDraftApproval
from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    generate_creative_version_for_owner,
    select_preferred_creative_for_owner,
)
from growthtwin.modules.campaigns.views import SYNTHETIC_CAMPAIGN
from growthtwin.modules.workspaces.models import Workspace


class DraftReviewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="review-owner")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Synthetic")
        self.draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **SYNTHETIC_CAMPAIGN,
            flight_start=date(2026, 11, 1),
            flight_end=date(2026, 11, 15),
        )
        _, version = generate_creative_version_for_owner(
            owner=self.owner, draft_id=self.draft.pk
        )
        self.draft = select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=1,
            key=version["variants"][0]["key"],
        )
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.owner)
        self.overrides = override_settings(
            DEBUG=False,
            ALLOWED_HOSTS=["127.0.0.1"],
            GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
            GOOGLE_ADS_LOCAL_OWNER_ID=str(self.owner.pk),
            GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(self.workspace.pk),
        )
        self.overrides.enable()
        self.addCleanup(self.overrides.disable)
        self.target = patch(
            "growthtwin.modules.connections.verification.configuration_key",
            return_value="target-key",
        )
        self.mock_target = self.target.start()
        self.addCleanup(self.target.stop)

    def review(self):
        response = self.client.get(
            "/connections/google/draft-review/",
            {"draft": self.draft.pk},
            HTTP_HOST="127.0.0.1:8002",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Referrer-Policy"], "same-origin")
        page = response.content.decode()
        return {
            "draft": str(self.draft.pk),
            "confirm": "yes",
            "review": html.unescape(
                re.search(r'name="review" value="([^"]+)"', page)[1]
            ),
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
        }

    def submit(self, data):
        return self.client.post(
            "/connections/google/draft-approve/",
            data,
            HTTP_HOST="127.0.0.1:8002",
            HTTP_ORIGIN="http://127.0.0.1:8002",
        )

    def test_approval_is_repeatable_snapshot_without_network(self):
        with patch("growthtwin.modules.connections.backend._post") as external:
            data = self.review()
            self.assertEqual(self.submit(data).status_code, 302)
            original = GoogleDraftApproval.objects.get().payload_json
            self.assertEqual(self.submit(data).status_code, 302)
            self.assertEqual(GoogleDraftApproval.objects.count(), 1)
            self.assertEqual(GoogleDraftApproval.objects.get().payload_json, original)
            external.assert_not_called()

    def test_changed_budget_or_target_rejects_old_review(self):
        data = self.review()
        self.draft.media_budget_minor += 1
        self.draft.save(update_fields=["media_budget_minor"])
        self.assertEqual(self.submit(data).status_code, 409)
        data = self.review()
        self.mock_target.return_value = "changed-target"
        self.assertEqual(self.submit(data).status_code, 409)
        self.assertEqual(GoogleDraftApproval.objects.count(), 0)

    def test_csrf_and_explicit_confirmation_required(self):
        data = self.review()
        data.pop("confirm")
        self.assertEqual(self.submit(data).status_code, 409)
        data["confirm"] = "yes"
        data.pop("csrfmiddlewaretoken")
        self.assertEqual(self.submit(data).status_code, 403)
        self.assertEqual(GoogleDraftApproval.objects.count(), 0)

    def test_other_owner_cannot_review(self):
        other = get_user_model().objects.create_user(username="other-review-owner")
        self.client.force_login(other)
        self.assertEqual(
            self.client.get(
                "/connections/google/draft-review/",
                {"draft": self.draft.pk},
                HTTP_HOST="127.0.0.1:8002",
            ).status_code,
            404,
        )
