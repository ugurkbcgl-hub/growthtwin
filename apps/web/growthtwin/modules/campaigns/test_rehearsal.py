"""Focused ownership, freshness and lifecycle coverage for local rehearsals."""

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier
from unittest import skipUnless

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase

from growthtwin.modules.campaigns.models import (
    CampaignRehearsal,
    CampaignRehearsalEvent,
    WorkspaceCampaignDraft,
)
from growthtwin.modules.campaigns.rehearsal import (
    perform_campaign_rehearsal,
    rehearsal_context,
)
from growthtwin.modules.campaigns.services import (
    generate_creative_version_for_owner,
    select_preferred_creative_for_owner,
)
from growthtwin.modules.publishing.fake import start_rehearsal, stop_rehearsal
from growthtwin.modules.workspaces.models import Workspace


class CampaignRehearsalTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="rehearsal-owner")
        self.other = get_user_model().objects.create_user(username="rehearsal-other")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Synthetic")
        self.draft = WorkspaceCampaignDraft.objects.create(
            workspace=self.workspace,
            name="Synthetic repair",
            brand_name="Başkent Bakım",
            brief="Ankara ev bakım teklifleri",
            target_city="Ankara",
            destination_url="https://example.test",
            media_budget_minor=500000,
            flight_start=date(2026, 10, 1),
            flight_end=date(2026, 10, 14),
        )
        self.draft, version = generate_creative_version_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
        )
        self.draft = select_preferred_creative_for_owner(
            owner=self.owner,
            draft_id=self.draft.pk,
            version_number=version["version"],
            key=version["variants"][0]["key"],
        )

    def act(self, action, **overrides):
        self.draft.refresh_from_db()
        context = rehearsal_context(self.draft)
        values = dict(
            owner=self.owner,
            draft_id=self.draft.pk,
            action=action,
            expected_revision=context["revision"],
            expected_fingerprint=context["fingerprint"],
        )
        values.update(overrides)
        return perform_campaign_rehearsal(**values)

    def test_read_context_does_not_create_state(self):
        context = rehearsal_context(self.draft)
        self.assertEqual(context["revision"], 0)
        self.assertTrue(context["can_start"])
        self.assertFalse(CampaignRehearsal.objects.exists())

    def test_failure_retry_keeps_operation_and_receipt_is_deterministic(self):
        failed = self.act("start_failure")
        operation = failed.operation_id
        self.assertEqual(failed.state, "failed")
        running = self.act("retry")
        self.assertEqual(running.state, "running")
        self.assertEqual(running.operation_id, operation)
        self.assertEqual(running.receipt, start_rehearsal(operation).receipt)
        self.assertEqual(running.events.count(), 2)
        self.assertEqual(running.revision, 2)

    def test_stop_terminal_then_start_renews_operation(self):
        running = self.act("start")
        stopped = self.act("stop")
        self.assertEqual(stopped.receipt, stop_rehearsal(running.operation_id).receipt)
        with self.assertRaises(ValidationError):
            self.act("retry")
        fresh = self.act("start")
        self.assertNotEqual(fresh.operation_id, running.operation_id)
        self.assertEqual(fresh.revision, 3)
        self.assertEqual(fresh.events.count(), 3)

    def test_other_owner_cannot_change_state(self):
        with self.assertRaises(WorkspaceCampaignDraft.DoesNotExist):
            self.act("start", owner=self.other)
        self.assertFalse(CampaignRehearsal.objects.exists())

    def test_duplicate_revision_and_invalid_action_do_not_write(self):
        self.act("start")
        for action, revision in (("stop", 0), ("other", 1), ("start", 1)):
            with self.assertRaises(ValidationError):
                self.act(action, expected_revision=revision)
        self.assertEqual(CampaignRehearsalEvent.objects.count(), 1)

    def test_start_requires_current_preference_and_complete_plan(self):
        for field, value in (("preferred_creative_key", ""), ("destination_url", "")):
            original = getattr(self.draft, field)
            setattr(self.draft, field, value)
            self.draft.save(update_fields=[field])
            with self.assertRaises(ValidationError):
                self.act("start")
            self.assertFalse(CampaignRehearsal.objects.exists())
            setattr(self.draft, field, original)
            self.draft.save(update_fields=[field])

    def test_stale_start_fingerprint_does_not_create_state(self):
        old = rehearsal_context(self.draft)["fingerprint"]
        self.draft.media_budget_minor += 1
        self.draft.save(update_fields=["media_budget_minor"])
        with self.assertRaises(ValidationError):
            self.act("start", expected_fingerprint=old)
        self.assertFalse(CampaignRehearsal.objects.exists())

    def test_retry_rejects_budget_and_preference_changes(self):
        self.act("start_failure")
        for field, value in (
            ("media_budget_minor", 600000),
            ("preferred_creative_key", "missing"),
        ):
            original = getattr(self.draft, field)
            setattr(self.draft, field, value)
            self.draft.save(update_fields=[field])
            with self.assertRaises(ValidationError):
                self.act("retry")
            self.assertTrue(rehearsal_context(self.draft)["stale"])
            setattr(self.draft, field, original)
            self.draft.save(update_fields=[field])
        self.assertEqual(CampaignRehearsalEvent.objects.count(), 1)

    def test_stop_works_after_source_edit_and_ignores_fingerprint(self):
        self.act("start_failure")
        self.draft.brief = "Changed synthetic offer"
        self.draft.save(update_fields=["brief"])
        self.assertTrue(rehearsal_context(self.draft)["can_stop"])
        stopped = self.act("stop", expected_fingerprint="stale")
        self.assertEqual(stopped.state, "stopped")

    def test_workspace_delete_cascades_state_and_history(self):
        self.act("start")
        self.workspace.delete()
        self.assertFalse(CampaignRehearsal.objects.exists())
        self.assertFalse(CampaignRehearsalEvent.objects.exists())


class CampaignRehearsalConcurrencyTests(TransactionTestCase):
    @skipUnless(connection.vendor == "postgresql", "PostgreSQL row locks required")
    def test_duplicate_start_serializes_on_campaign_row(self):
        owner = get_user_model().objects.create_user(username="concurrent-owner")
        workspace = Workspace.objects.create(owner=owner, name="Synthetic concurrency")
        draft = WorkspaceCampaignDraft.objects.create(
            workspace=workspace,
            name="Synthetic repair",
            brand_name="Başkent Bakım",
            brief="Ankara ev bakım teklifleri",
            target_city="Ankara",
            destination_url="https://example.test",
            media_budget_minor=500000,
            flight_start=date(2026, 10, 1),
            flight_end=date(2026, 10, 14),
        )
        draft, version = generate_creative_version_for_owner(
            owner=owner, draft_id=draft.pk
        )
        draft = select_preferred_creative_for_owner(
            owner=owner,
            draft_id=draft.pk,
            version_number=version["version"],
            key=version["variants"][0]["key"],
        )
        fingerprint = rehearsal_context(draft)["fingerprint"]
        barrier = Barrier(2)

        def start():
            close_old_connections()
            try:
                thread_owner = get_user_model().objects.get(pk=owner.pk)
                barrier.wait(timeout=10)
                try:
                    perform_campaign_rehearsal(
                        owner=thread_owner,
                        draft_id=draft.pk,
                        action="start",
                        expected_revision=0,
                        expected_fingerprint=fingerprint,
                    )
                    return "started"
                except ValidationError:
                    return "stale"
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(start) for _ in range(2)]
            results = [future.result(timeout=20) for future in futures]
        self.assertCountEqual(results, ["started", "stale"])
        self.assertEqual(CampaignRehearsal.objects.get(draft=draft).revision, 1)
        self.assertEqual(CampaignRehearsalEvent.objects.count(), 1)
