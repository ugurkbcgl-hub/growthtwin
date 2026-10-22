"""Fixed example receipts; no real OAuth, grant or provider access."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from growthtwin.modules.workspaces.models import Workspace

from .connector_identity import (
    IdentityConflict,
    block_identity,
    get_identity,
    register_google_test_identity,
    rotate_generation,
)
from .models import ConnectorIdentity
from .models import SyntheticAuthorizationAttempt as Attempt
from .synthetic_authorization import (
    FakeAuthorizationScenario as Scenario,
)
from .synthetic_authorization import (
    begin_example,
    get_example,
    perform_example,
)


class AuthorizationFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="synthetic-auth-owner"
        )
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Synthetic authorization"
        )
        self.identity = register_google_test_identity(
            owner=self.owner, workspace_id=self.workspace.pk, request_id=uuid4()
        )
        self.attempt_id = uuid4()

    def begin(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
            scenario=Scenario.ALLOW,
            synthetic_confirmation=True,
        )
        return begin_example(**(values | changes))

    def perform(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
        )
        return perform_example(**(values | changes))

    def read(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
        )
        return get_example(**(values | changes))

    def rotate(self):
        return rotate_generation(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            request_id=uuid4(),
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )

    def block(self, owner=None):
        return block_identity(
            owner=owner or self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )


@override_settings(SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=True)
class SyntheticAuthorizationTests(AuthorizationFixture, TransactionTestCase):
    def test_default_off_and_unconfirmed_or_untyped_scenarios_do_not_create_attempt(
        self,
    ):
        with override_settings(SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=False):
            with self.assertRaises(PermissionDenied):
                self.begin()
        for changes in (
            {"synthetic_confirmation": False},
            {"synthetic_confirmation": "yes"},
            {"scenario": "allow_example"},
        ):
            with self.assertRaises(ValueError):
                self.begin(**changes)
        self.assertEqual(Attempt.objects.count(), 0)

    def test_exact_begin_replay_keeps_one_attempt_and_original_expiry(self):
        first = self.begin()
        self.assertEqual(self.begin(), first)
        self.assertEqual(first.state, "pending")
        self.assertEqual(Attempt.objects.count(), 1)
        with self.assertRaises(IdentityConflict):
            self.begin(scenario=Scenario.DENY)
        self.assertEqual(self.read(), first)

    def test_new_attempt_cannot_replace_unexpired_current_attempt(self):
        first = self.begin()
        with self.assertRaises(IdentityConflict):
            self.begin(attempt_id=uuid4())
        self.assertEqual(self.read(), first)

    def test_success_is_only_example_and_repeat_never_invokes_fake_again(self):
        self.begin()
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result",
            return_value=True,
        ) as fake:
            completed = self.perform()
            self.assertEqual(self.perform(), completed)
        fake.assert_called_once_with(Scenario.ALLOW)
        self.assertEqual((completed.state, completed.reason), ("accepted", ""))
        current = get_identity(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
        )
        self.assertEqual(current, self.identity)
        self.assertEqual(current.state, "quarantined")

    def test_fixed_denial_and_failure_are_not_success_or_raw_exception(self):
        self.begin(scenario=Scenario.DENY)
        self.assertEqual(self.perform().reason, "example_denied")
        self.identity = self.rotate()
        self.attempt_id = uuid4()
        self.begin()
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result",
            side_effect=RuntimeError("suppressed fixture detail"),
        ):
            result = self.perform()
        self.assertEqual((result.state, result.reason), ("rejected", "fake_failed"))

    def test_expired_before_start_never_invokes_fake(self):
        pending = self.begin()
        with (
            patch(
                "growthtwin.modules.connections.synthetic_authorization.timezone.now",
                return_value=pending.expires_at,
            ),
            patch(
                "growthtwin.modules.connections.synthetic_authorization._fixed_result"
            ) as fake,
        ):
            result = self.perform()
        fake.assert_not_called()
        self.assertEqual((result.state, result.reason), ("expired", "expired"))

    def test_rotation_or_block_before_start_rejects_without_fake(self):
        self.begin()
        self.rotate()
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result"
        ) as fake:
            self.assertEqual(self.perform().reason, "scope_changed")
        fake.assert_not_called()
        # Separate block example in a fresh identity fixture is covered below.

    def test_block_during_fake_rejects_late_success(self):
        self.begin()

        def fake(scenario):
            self.assertFalse(connection.in_atomic_block)
            self.block()
            return True

        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result",
            side_effect=fake,
        ):
            result = self.perform()
        self.assertEqual((result.state, result.reason), ("rejected", "scope_changed"))
        self.assertEqual(ConnectorIdentity.objects.get().state, "blocked")

    def test_rotation_during_fake_rejects_late_success(self):
        self.begin()
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result",
            side_effect=lambda scenario: bool(self.rotate()),
        ):
            result = self.perform()
        self.assertEqual(result.reason, "scope_changed")

    def test_expiry_during_fake_rejects_late_success(self):
        pending = self.begin()
        clock = [timezone.now()]

        def fake(scenario):
            clock[0] = pending.expires_at
            return True

        with (
            patch(
                "growthtwin.modules.connections.synthetic_authorization.timezone.now",
                side_effect=lambda: clock[0],
            ),
            patch(
                "growthtwin.modules.connections.synthetic_authorization._fixed_result",
                side_effect=fake,
            ),
        ):
            result = self.perform()
        self.assertEqual(result.state, "expired")

    def test_disabling_during_fake_rejects_late_success(self):
        self.begin()
        disabled = override_settings(SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=False)

        def fake(scenario):
            disabled.enable()
            return True

        try:
            with patch(
                "growthtwin.modules.connections.synthetic_authorization._fixed_result",
                side_effect=fake,
            ):
                result = self.perform()
        finally:
            disabled.disable()
        self.assertEqual(result.reason, "disabled")

    def test_inflight_replay_or_crash_never_restarts_fake_and_expires(self):
        pending = self.begin()
        Attempt.objects.filter(pk=self.attempt_id).update(state="running")
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result"
        ) as fake:
            self.assertEqual(self.perform().state, "running")
            with patch(
                "growthtwin.modules.connections.synthetic_authorization.timezone.now",
                return_value=pending.expires_at,
            ):
                self.assertEqual(self.perform().state, "expired")
        fake.assert_not_called()

    def test_expired_attempt_can_be_replaced_without_accepting_old_result(self):
        pending = self.begin()
        with patch(
            "growthtwin.modules.connections.synthetic_authorization.timezone.now",
            return_value=pending.expires_at,
        ):
            replacement = self.begin(attempt_id=uuid4())
        self.assertEqual(replacement.state, "pending")
        self.assertEqual(self.read().state, "expired")
        self.assertEqual(
            Attempt.objects.filter(state__in=("pending", "running")).count(), 1
        )

    def test_new_generation_replaces_stale_pending_with_rejection(self):
        self.begin()
        newer = self.rotate()
        replacement = self.begin(
            attempt_id=uuid4(),
            expected_generation=newer.generation,
            expected_revision=newer.revision,
        )
        self.assertEqual(self.read().reason, "scope_changed")
        self.assertEqual(replacement.generation, newer.generation)

    def test_owner_and_workspace_isolation_and_inactive_owner(self):
        self.begin()
        other = get_user_model().objects.create_user(username="synthetic-auth-other")
        for action in (self.read, self.perform, self.begin):
            with self.assertRaises(Workspace.DoesNotExist):
                action(owner=other)
        elsewhere = Workspace.objects.create(owner=other, name="Other synthetic")
        with self.assertRaises(ConnectorIdentity.DoesNotExist):
            self.read(owner=other, workspace_id=elsewhere.pk)
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            self.perform()

    def test_get_is_historical_read_only_even_when_rehearsal_disabled(self):
        pending = self.begin()
        with (
            override_settings(SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=False),
            CaptureQueriesContext(connection) as captured,
        ):
            self.assertEqual(self.read(), pending)
        self.assertFalse(
            any(
                q["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
                for q in captured
            )
        )

    def test_no_credentials_or_provider_adapter_and_no_caller_transaction(self):
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
        ):
            self.begin()
            with transaction.atomic():
                with self.assertRaises(IdentityConflict):
                    self.perform()
            self.assertEqual(self.perform().state, "accepted")

    def test_missing_attempt_cannot_invoke_fake_and_uuid_must_be_typed(self):
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result"
        ) as fake:
            with self.assertRaises(Attempt.DoesNotExist):
                self.perform()
        fake.assert_not_called()
        with self.assertRaises(ValueError):
            self.begin(attempt_id=str(uuid4()))

    def test_metadata_binding_changed_during_fake_cannot_accept_old_result(self):
        self.begin()

        def fake(scenario):
            newer = self.rotate()
            Attempt.objects.filter(pk=self.attempt_id).update(
                generation=newer.generation, expected_revision=newer.revision
            )
            return True

        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result",
            side_effect=fake,
        ):
            result = self.perform()
        self.assertEqual(result.reason, "scope_changed")

    def test_extended_or_corrupt_lifetime_is_rejected(self):
        pending = self.begin()
        Attempt.objects.filter(pk=self.attempt_id).update(
            expires_at=pending.expires_at + timedelta(seconds=1)
        )
        with self.assertRaises(IdentityConflict):
            self.perform()

    def test_database_rejects_non_synthetic_mode_and_second_active_attempt(self):
        self.begin()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Attempt.objects.filter(pk=self.attempt_id).update(mode="oauth")
        original = Attempt.objects.get()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Attempt.objects.create(
                id=uuid4(),
                connection=original.connection,
                generation=original.generation,
                expected_revision=original.expected_revision,
                scenario="allow_example",
                created_at=original.created_at,
                expires_at=original.expires_at,
            )

    def test_corrupt_accepted_scenario_or_completion_time_is_not_replayed(self):
        pending = self.begin(scenario=Scenario.DENY)
        row = Attempt.objects.get()
        Attempt.objects.filter(pk=row.pk).update(
            state="accepted", reason="", completed_at=timezone.now()
        )
        for action in (self.read, self.perform):
            with self.assertRaises(IdentityConflict):
                action()
        for completion in (row.created_at - timedelta(seconds=1), pending.expires_at):
            Attempt.objects.filter(pk=row.pk).update(
                scenario="allow_example", completed_at=completion
            )
            with self.assertRaises(IdentityConflict):
                self.read()

        Attempt.objects.filter(pk=row.pk).update(
            generation=uuid4(), completed_at=timezone.now()
        )
        with self.assertRaises(IdentityConflict):
            self.read()

    def test_unexpected_success_for_deny_scenario_is_fake_failure(self):
        self.begin(scenario=Scenario.DENY)
        with patch(
            "growthtwin.modules.connections.synthetic_authorization._fixed_result",
            return_value=True,
        ):
            result = self.perform()
        self.assertEqual((result.state, result.reason), ("rejected", "fake_failed"))


@override_settings(SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED=True)
class SyntheticAuthorizationRaceTests(AuthorizationFixture, TransactionTestCase):
    def threaded(self, call):
        close_old_connections()
        try:
            return call(get_user_model().objects.get(pk=self.owner.pk))
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_duplicate_while_fake_is_inflight_does_not_execute_twice(self):
        self.begin()
        entered, release = Event(), Event()

        def fake(scenario):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Fixed fake coordination failed")
            return True

        with (
            patch(
                "growthtwin.modules.connections.synthetic_authorization._fixed_result",
                side_effect=fake,
            ) as mocked,
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first = pool.submit(self.threaded, lambda owner: self.perform(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                second = pool.submit(
                    self.threaded, lambda owner: self.perform(owner=owner)
                )
                self.assertEqual(second.result(timeout=10).state, "running")
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).state, "accepted")
        self.assertEqual(mocked.call_count, 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_block_commits_while_fake_waits_and_prevents_late_acceptance(self):
        self.begin()
        entered, release = Event(), Event()

        def fake(scenario):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Fixed fake coordination failed")
            return True

        with (
            patch(
                "growthtwin.modules.connections.synthetic_authorization._fixed_result",
                side_effect=fake,
            ),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first = pool.submit(self.threaded, lambda owner: self.perform(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                blocked = pool.submit(
                    self.threaded, lambda owner: self.block(owner=owner)
                )
                self.assertEqual(blocked.result(timeout=10).state, "blocked")
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).reason, "scope_changed")
        self.assertEqual(self.read().state, "rejected")
