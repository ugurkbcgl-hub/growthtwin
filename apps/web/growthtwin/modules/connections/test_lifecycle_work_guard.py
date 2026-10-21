"""Isolated fixture guard checks, including PostgreSQL close/work ordering."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Event
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, transaction
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from .lifecycle_journey import example_id, start_example
from .lifecycle_results import complete_example
from .lifecycle_store import ClosureConflict
from .lifecycle_work_guard import (
    FakeWorkRequest,
    WorkKind,
    perform_fake_work,
    register_fixture_scope,
)
from .models import SyntheticClosureRequest, SyntheticConnectionScope


class GuardFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="guard-owner")
        self.other = get_user_model().objects.create_user(username="guard-other")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Synthetic gate"
        )
        self.scope = register_fixture_scope(
            owner=self.owner, workspace_id=self.workspace.pk
        )
        self.request = FakeWorkRequest(
            self.scope.connection_id, self.scope.generation, 0, WorkKind.CREATE
        )

    def perform(self, request=None, owner=None):
        return perform_fake_work(
            owner=self.owner if owner is None else owner,
            workspace_id=self.workspace.pk,
            request=self.request if request is None else request,
        )

    def close(self):
        return start_example(owner=self.owner, workspace_id=self.workspace.pk)


class SyntheticWorkGuardTests(GuardFixture, TestCase):
    def test_each_typed_fake_work_kind_updates_only_its_scope_counter(self):
        for revision, kind in enumerate(WorkKind):
            result = self.perform(
                replace(self.request, kind=kind, expected_revision=revision)
            )
            self.assertTrue(result.performed)
            self.assertEqual(result.scope.revision, revision + 1)
            self.assertEqual(result.scope.fake_work_count, revision + 1)
        self.assertFalse(SyntheticClosureRequest.objects.exists())

    def test_unknown_or_unregistered_scope_cannot_call_fake(self):
        second = replace(
            self.request,
            connection_id=example_id(self.workspace.pk, "connection", "belirsiz"),
            generation=example_id(self.workspace.pk, "generation", "belirsiz"),
        )
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            side_effect=AssertionError,
        ):
            self.assertEqual(
                self.perform(replace(self.request, connection_id=uuid4())).reason,
                "unknown_fixture_scope",
            )
            self.assertEqual(self.perform(second).reason, "unregistered_scope")
        self.assertEqual(SyntheticConnectionScope.objects.count(), 1)

    def test_old_generation_stale_revision_and_exact_request_replay_do_not_run(self):
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            side_effect=AssertionError,
        ):
            self.assertEqual(
                self.perform(replace(self.request, generation=uuid4())).reason,
                "generation_mismatch",
            )
            self.assertEqual(
                self.perform(replace(self.request, expected_revision=9)).reason,
                "revision_mismatch",
            )
        self.perform()
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            side_effect=AssertionError,
        ):
            self.assertEqual(self.perform().reason, "revision_mismatch")
        self.assertEqual(SyntheticConnectionScope.objects.get().fake_work_count, 1)

    def test_every_kind_and_late_callback_is_blocked_after_closure(self):
        self.close()
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            side_effect=AssertionError,
        ):
            for kind in WorkKind:
                result = self.perform(
                    replace(self.request, kind=kind, expected_revision=1)
                )
                self.assertFalse(result.performed)
                self.assertEqual(result.reason, "closure_blocks_new_work")
        row = SyntheticConnectionScope.objects.get()
        self.assertEqual(row.state, SyntheticConnectionScope.State.BLOCKED)
        self.assertEqual(row.fake_work_count, 0)
        self.assertEqual(row.revision, 1)

    def test_successful_stop_and_register_retry_never_reopen_scope(self):
        record = self.close()
        complete_example(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            request_id=record.identity.request_id,
            operation_id=record.pending.operation_id,
            expected_revision=1,
        )
        again = register_fixture_scope(owner=self.owner, workspace_id=self.workspace.pk)
        self.assertEqual(again.state, SyntheticConnectionScope.State.BLOCKED)
        self.assertEqual(again.revision, 1)
        self.close()
        self.assertEqual(SyntheticConnectionScope.objects.get().revision, 1)
        self.assertFalse(self.perform().performed)

    def test_closure_before_scope_registration_stays_blocked(self):
        closed = start_example(
            owner=self.owner, workspace_id=self.workspace.pk, example="belirsiz"
        )
        registered = register_fixture_scope(
            owner=self.owner, workspace_id=self.workspace.pk, example="belirsiz"
        )
        self.assertEqual(registered.state, SyntheticConnectionScope.State.BLOCKED)
        result = self.perform(
            FakeWorkRequest(
                closed.identity.connection_id,
                closed.identity.generation,
                0,
                WorkKind.CALLBACK_SAVE,
            )
        )
        self.assertFalse(result.performed)

    def test_closure_existence_blocks_even_if_scope_metadata_is_wrongly_open(self):
        self.close()
        SyntheticConnectionScope.objects.update(
            state=SyntheticConnectionScope.State.OPEN
        )
        before = SyntheticConnectionScope.objects.values().get()
        self.assertEqual(self.perform().reason, "closure_blocks_new_work")
        self.assertEqual(SyntheticConnectionScope.objects.values().get(), before)

    def test_quarantine_unknown_state_or_wrong_registry_generation_deny_work(self):
        for state in (SyntheticConnectionScope.State.QUARANTINED, "unsupported"):
            SyntheticConnectionScope.objects.update(state=state)
            self.assertEqual(self.perform().reason, "scope_not_verified")
            self.assertEqual(
                register_fixture_scope(
                    owner=self.owner, workspace_id=self.workspace.pk
                ).state,
                state,
            )
        SyntheticConnectionScope.objects.update(
            state=SyntheticConnectionScope.State.OPEN, generation=uuid4()
        )
        self.assertEqual(self.perform().reason, "generation_mismatch")

    def test_inconsistent_counter_metadata_is_not_trusted(self):
        SyntheticConnectionScope.objects.update(fake_work_count=5, revision=0)
        self.assertEqual(self.perform().reason, "invalid_scope_metadata")

    def test_anonymous_foreign_and_inactive_users_cannot_register_or_run(self):
        for owner in (AnonymousUser(), self.other):
            for call in (
                lambda: self.perform(owner=owner),
                lambda: register_fixture_scope(
                    owner=owner, workspace_id=self.workspace.pk
                ),
            ):
                with self.assertRaises((PermissionDenied, Workspace.DoesNotExist)):
                    call()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            self.perform()
        self.assertEqual(SyntheticConnectionScope.objects.get().fake_work_count, 0)

    def test_other_registered_example_is_not_blocked_by_unrelated_closure(self):
        self.close()
        second = register_fixture_scope(
            owner=self.owner, workspace_id=self.workspace.pk, example="belirsiz"
        )
        result = self.perform(
            FakeWorkRequest(
                second.connection_id, second.generation, 0, WorkKind.REFRESH
            )
        )
        self.assertTrue(result.performed)

    def test_bad_adapter_result_or_failed_cas_does_not_commit_work(self):
        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            return_value="unexpected",
        ):
            with self.assertRaises(ClosureConflict):
                self.perform()
        with patch("django.db.models.query.QuerySet.update", return_value=0):
            with self.assertRaises(ClosureConflict):
                self.perform()
        self.assertEqual(SyntheticConnectionScope.objects.get().fake_work_count, 0)
        self.assertEqual(SyntheticConnectionScope.objects.get().revision, 0)

    def test_failed_closure_rolls_back_scope_block_and_request_together(self):
        with patch(
            "growthtwin.modules.connections.lifecycle_journey.issue_synthetic_ticket",
            side_effect=ClosureConflict,
        ):
            with self.assertRaises(ClosureConflict):
                self.close()
        row = SyntheticConnectionScope.objects.get()
        self.assertEqual(row.state, SyntheticConnectionScope.State.OPEN)
        self.assertEqual(row.revision, 0)
        self.assertFalse(SyntheticClosureRequest.objects.exists())

    def test_no_grants_provider_calls_or_arbitrary_executor_payload(self):
        with (
            patch(
                "growthtwin.modules.connections.backend._read",
                side_effect=AssertionError,
            ),
            patch(
                "growthtwin.modules.connections.backend._post",
                side_effect=AssertionError,
            ),
        ):
            self.perform()
            self.close()
            self.assertFalse(
                self.perform(
                    replace(self.request, kind=WorkKind.CALLBACK_SAVE)
                ).performed
            )
        with self.assertRaises(ValueError):
            FakeWorkRequest(
                self.scope.connection_id, self.scope.generation, True, WorkKind.CREATE
            )
        with self.assertRaises(ValueError):
            replace(self.request, kind="create")


class PostgreSQLWorkClosureRaceTests(GuardFixture, TransactionTestCase):
    def threaded(self, call):
        close_old_connections()
        try:
            owner = get_user_model().objects.get(pk=self.owner.pk)
            return call(owner)
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_closure_intake_wins_and_late_callback_never_invokes_fake(self):
        closing, work_started, allow_commit = Event(), Event(), Event()

        def close(owner):
            with transaction.atomic():
                record = start_example(owner=owner, workspace_id=self.workspace.pk)
                closing.set()
                if not allow_commit.wait(10):
                    raise TimeoutError("Synthetic close race coordination failed.")
                return record

        def work(owner):
            if not closing.wait(10):
                raise TimeoutError("Synthetic close race coordination failed.")
            work_started.set()
            return perform_fake_work(
                owner=owner,
                workspace_id=self.workspace.pk,
                request=replace(self.request, kind=WorkKind.CALLBACK_SAVE),
            )

        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            side_effect=AssertionError,
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                close_future = pool.submit(self.threaded, close)
                work_future = pool.submit(self.threaded, work)
                try:
                    self.assertTrue(work_started.wait(10))
                finally:
                    allow_commit.set()
                close_future.result(timeout=10)
                result = work_future.result(timeout=10)
        self.assertEqual(result.reason, "closure_blocks_new_work")
        self.assertEqual(SyntheticConnectionScope.objects.get().fake_work_count, 0)

    @skipUnlessDBFeature("has_select_for_update")
    def test_prior_fake_finishes_before_close_then_later_work_is_blocked(self):
        inside_fake, close_started, allow_fake = Event(), Event(), Event()

        def fake(kind):
            inside_fake.set()
            if not allow_fake.wait(10):
                raise TimeoutError("Synthetic fake race coordination failed.")
            return kind

        def work(owner):
            return perform_fake_work(
                owner=owner, workspace_id=self.workspace.pk, request=self.request
            )

        def close(owner):
            if not inside_fake.wait(10):
                raise TimeoutError("Synthetic fake race coordination failed.")
            close_started.set()
            return start_example(owner=owner, workspace_id=self.workspace.pk)

        with patch(
            "growthtwin.modules.connections.lifecycle_fake.new_work_result",
            side_effect=fake,
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                work_future = pool.submit(self.threaded, work)
                close_future = pool.submit(self.threaded, close)
                try:
                    self.assertTrue(close_started.wait(10))
                finally:
                    allow_fake.set()
                self.assertTrue(work_future.result(timeout=10).performed)
                close_future.result(timeout=10)
        self.assertFalse(
            self.perform(replace(self.request, expected_revision=2)).performed
        )
        row = SyntheticConnectionScope.objects.get()
        self.assertEqual(row.state, SyntheticConnectionScope.State.BLOCKED)
        self.assertEqual(row.fake_work_count, 1)
        self.assertEqual(row.revision, 2)
