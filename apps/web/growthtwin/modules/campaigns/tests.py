"""Tenant isolation for workspace-owned campaign drafts."""

from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import TestCase

from growthtwin.modules.campaigns.models import WorkspaceCampaignDraft
from growthtwin.modules.campaigns.services import (
    create_campaign_draft_for_owner,
    get_campaign_draft_for_owner,
)
from growthtwin.modules.workspaces.models import Workspace


class CampaignDraftOwnershipTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="campaign-owner")
        self.other_user = user_model.objects.create_user(username="other-owner")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Owner space")
        self.other_workspace = Workspace.objects.create(
            owner=self.other_user,
            name="Other space",
        )

    def draft_values(self):
        return {
            "name": "Synthetic home repair search campaign",
            "brief": "Offer repair estimates in Ankara.",
            "target_city": "Ankara",
            "destination_url": "https://example.test/repair",
            "media_budget_minor": 500_000,
            "flight_start": date(2026, 10, 1),
            "flight_end": date(2026, 10, 14),
        }

    def test_owner_can_create_and_retrieve_workspace_campaign(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **self.draft_values(),
        )

        self.assertEqual(draft.workspace, self.workspace)
        self.assertEqual(
            draft.objective, WorkspaceCampaignDraft.Objective.LEAD_GENERATION
        )
        self.assertEqual(draft.channel, WorkspaceCampaignDraft.Channel.GOOGLE_SEARCH)
        self.assertEqual(draft.currency, "TRY")
        self.assertEqual(
            get_campaign_draft_for_owner(owner=self.owner, draft_id=draft.pk),
            draft,
        )

    def test_other_owner_cannot_retrieve_campaign_by_id(self):
        draft = create_campaign_draft_for_owner(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            **self.draft_values(),
        )

        with self.assertRaises(WorkspaceCampaignDraft.DoesNotExist):
            get_campaign_draft_for_owner(owner=self.other_user, draft_id=draft.pk)

    def test_owner_cannot_create_campaign_in_another_workspace(self):
        with self.assertRaises(Workspace.DoesNotExist):
            create_campaign_draft_for_owner(
                owner=self.owner,
                workspace_id=self.other_workspace.pk,
                **self.draft_values(),
            )

    def test_anonymous_user_cannot_create_campaign(self):
        from django.contrib.auth.models import AnonymousUser

        with self.assertRaises(PermissionDenied):
            create_campaign_draft_for_owner(
                owner=AnonymousUser(),
                workspace_id=self.workspace.pk,
                **self.draft_values(),
            )

    def test_invalid_media_budget_is_rejected_before_persistence(self):
        with self.assertRaises(ValidationError):
            create_campaign_draft_for_owner(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                **(self.draft_values() | {"media_budget_minor": 0}),
            )

        self.assertFalse(WorkspaceCampaignDraft.objects.exists())

    def test_end_date_before_start_date_is_rejected(self):
        with self.assertRaises(ValidationError):
            create_campaign_draft_for_owner(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                **(
                    self.draft_values()
                    | {
                        "flight_start": date(2026, 10, 14),
                        "flight_end": date(2026, 10, 1),
                    }
                ),
            )

        self.assertFalse(WorkspaceCampaignDraft.objects.exists())
