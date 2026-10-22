"""Reserved-only retirement under mocked boundaries and isolated databases."""

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Event
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, close_old_connections
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature
from django.utils import timezone

from growthtwin.modules.workspaces.models import Workspace

from . import candidate_retirement as retirement
from . import test_scoped_oauth_candidate as fixtures
from .connector_identity import (
    IdentityConflict,
    block_identity,
    register_google_test_identity,
    rotate_generation,
)
from .models import ConnectorGeneration, ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


class RetirementFixture(fixtures.CandidateFixture):
    def setUp(self):
        super().setUp()
        self.retirement_id = uuid4()

    def retire(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            request_id=self.retirement_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
            retirement_confirmation=True,
        )
        counts = [
            mock.call_count
            for mock in (
                self._client,
                self._post,
                self._read,
                self._write,
                self._token_path,
            )
        ]
        result = retirement.retire_reserved(**(values | changes))
        self.assertEqual(
            counts,
            [
                mock.call_count
                for mock in (
                    self._client,
                    self._post,
                    self._read,
                    self._write,
                    self._token_path,
                )
            ],
        )
        return result


@override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True)
class CandidateRetirementTests(RetirementFixture, TransactionTestCase):
    def test_retirement_rotates_and_preserves_original_history_without_io(self):
        self.prepare()
        original = Attempt.objects.get()
        result = self.retire()
        self.assertEqual(result.snapshot.state, "rejected")
        self.assertEqual(result.snapshot.reason, "retired_before_exchange")
        self.assertEqual(result.current_identity.revision, self.identity.revision + 1)
        self.assertNotEqual(
            result.current_identity.generation, self.identity.generation
        )
        row = Attempt.objects.get()
        self.assertEqual(
            (row.created_at, row.expires_at, row.generation),
            (original.created_at, original.expires_at, original.generation),
        )
        self.assertEqual(row.retired_generation, result.current_identity.generation)
        self.assertEqual(row.retirement_request_id, self.retirement_id)
        self.assertEqual(ConnectorGeneration.objects.count(), 2)
        self.assertEqual(ConnectorIdentity.objects.get().state, "quarantined")
        self.assertEqual(self.consume().state, "rejected")
        self._post.assert_not_called()
        self._write.assert_not_called()

    def test_exact_replay_returns_current_identity_even_after_rotate_and_block(self):
        self.begin()
        first = self.retire()
        self.assertEqual(self.retire(), first)
        newer = rotate_generation(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            request_id=uuid4(),
            expected_generation=first.current_identity.generation,
            expected_revision=first.current_identity.revision,
        )
        blocked = block_identity(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            expected_generation=newer.generation,
            expected_revision=newer.revision,
        )
        self.assertEqual(self.retire().current_identity, blocked)
        self.assertEqual(ConnectorGeneration.objects.count(), 3)
        with self.assertRaises(IdentityConflict):
            self.retire(request_id=uuid4())

    def test_default_off_and_explicit_typed_confirmation_required(self):
        self.begin()
        with override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=False):
            with self.assertRaises(PermissionDenied):
                self.retire()
        for value in (False, "yes", 1):
            with self.assertRaises(ValueError):
                self.retire(retirement_confirmation=value)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    def test_every_non_reserved_state_denied(self):
        self.begin()
        for state, reason in (
            ("exchanging", ""),
            ("uncertain", "exchange_uncertain"),
            ("candidate", ""),
            ("rejected", "callback_invalid"),
        ):
            Attempt.objects.update(state=state, reason=reason)
            with self.assertRaises(IdentityConflict):
                self.retire()
            self.assertEqual(Attempt.objects.get().state, state)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    def test_expired_and_lost_session_reservation_can_retire_without_extension(self):
        self.begin()
        old = timezone.now() - timedelta(days=1)
        Attempt.objects.update(created_at=old, expires_at=old + timedelta(minutes=5))
        self.retire()
        self.assertEqual(Attempt.objects.get().expires_at, old + timedelta(minutes=5))

    def test_stale_generation_denied(self):
        self.begin()
        self.rotate()
        with self.assertRaises(IdentityConflict):
            self.retire()
        self.assertEqual(Attempt.objects.get().state, "reserved")

    def test_blocked_connector_denied(self):
        self.begin()
        self.block()
        with self.assertRaises(IdentityConflict):
            self.retire()
        self.assertEqual(Attempt.objects.get().state, "reserved")

    def test_other_unresolved_history_blocks_retirement(self):
        self.begin()
        old = Attempt.objects.get()
        Attempt.objects.update(state="uncertain", reason="storage_uncertain")
        newer = self.rotate()
        attempt = uuid4()
        Attempt.objects.create(
            id=attempt,
            connection_id=self.identity.connection_id,
            generation=newer.generation,
            expected_revision=newer.revision,
            session_key_hash=old.session_key_hash,
            client_id_hash=old.client_id_hash,
            created_at=old.created_at,
            expires_at=old.expires_at,
        )
        with self.assertRaises(IdentityConflict):
            self.retire(
                attempt_id=attempt,
                expected_generation=newer.generation,
                expected_revision=newer.revision,
            )
        self.assertEqual(Attempt.objects.get(pk=self.attempt_id).state, "uncertain")

    def test_foreign_owner_unknown_attempt_and_invalid_typed_scope_denied(self):
        self.begin()
        other = get_user_model().objects.create_user(username="retirement-other")
        with self.assertRaises(Workspace.DoesNotExist):
            self.retire(owner=other)
        with self.assertRaises(Attempt.DoesNotExist):
            self.retire(attempt_id=uuid4())
        with self.assertRaises(ValueError):
            self.retire(expected_revision=True)
        with self.assertRaises(ValueError):
            self.retire(request_id=str(uuid4()))
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    def test_request_collision_rolls_back(self):
        self.begin()
        existing = ConnectorGeneration.objects.get().request_id
        with self.assertRaises(IdentityConflict):
            self.retire(request_id=existing)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self.assertEqual(
            ConnectorIdentity.objects.get().generation, self.identity.generation
        )

    def test_other_connector_rotation_request_cannot_be_adopted(self):
        self.begin()
        workspace = Workspace.objects.create(owner=self.owner, name="Other fixture")
        other = register_google_test_identity(
            owner=self.owner, workspace_id=workspace.pk, request_id=uuid4()
        )
        request = uuid4()
        rotate_generation(
            owner=self.owner,
            workspace_id=workspace.pk,
            connection_id=other.connection_id,
            request_id=request,
            expected_generation=other.generation,
            expected_revision=other.revision,
        )
        with self.assertRaises(IdentityConflict):
            self.retire(request_id=request)
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self.assertEqual(ConnectorGeneration.objects.count(), 3)

    def test_final_validation_failure_rolls_back_rotation_and_retirement(self):
        self.begin()
        original = fixtures.candidate._metadata

        def validate(row):
            if row.reason == "retired_before_exchange":
                raise IntegrityError("Fabricated finalization failure")
            return original(row)

        with patch.object(fixtures.candidate, "_metadata", side_effect=validate):
            with self.assertRaises(IntegrityError):
                self.retire()
        self.assertEqual(Attempt.objects.get().state, "reserved")
        self.assertIsNone(Attempt.objects.get().retirement_request_id)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)
        self.assertEqual(
            ConnectorIdentity.objects.get().generation, self.identity.generation
        )

    def test_constraint_and_corrupt_retirement_receipt_fail_closed(self):
        self.begin()
        with self.assertRaises(IntegrityError):
            Attempt.objects.update(retirement_request_id=uuid4())
        self.retire()
        original_generation = Attempt.objects.get().retired_generation
        Attempt.objects.update(retired_generation=uuid4())
        with self.assertRaises(IdentityConflict):
            self.retire()
        Attempt.objects.update(
            retired_generation=original_generation, retirement_request_id=uuid4()
        )
        with self.assertRaises(IdentityConflict):
            self.retire()

    def test_new_attempt_requires_new_generation_and_distinct_id(self):
        self.begin()
        result = self.retire()
        new_id = uuid4()
        self.begin(
            attempt_id=new_id,
            expected_generation=result.current_identity.generation,
            expected_revision=result.current_identity.revision,
        )
        self.assertEqual(Attempt.objects.count(), 2)
        self.assertEqual(Attempt.objects.get(pk=new_id).state, "reserved")
        self._post.assert_not_called()


@override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True)
class CandidateRetirementRaceTests(RetirementFixture, TransactionTestCase):
    def threaded(self, call):
        close_old_connections()
        try:
            return call(get_user_model().objects.get(pk=self.owner.pk))
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_exchange_commit_wins_then_retirement_is_denied(self):
        self.prepare()
        entered, release = Event(), Event()
        original = self._post.return_value

        def post(*args):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Retirement race coordination failed")
            return original

        self._post.side_effect = post
        with ThreadPoolExecutor(max_workers=1) as pool:
            first = pool.submit(self.threaded, lambda owner: self.consume(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                with self.assertRaises(IdentityConflict):
                    self.retire()
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).state, "candidate")
        self.assertEqual(ConnectorGeneration.objects.count(), 1)
        self._post.assert_called_once()

    @skipUnlessDBFeature("has_select_for_update")
    def test_retirement_commit_wins_then_callback_has_zero_transport(self):
        self.prepare()
        entered, release, callback_started = Event(), Event(), Event()
        original = retirement.rotate_generation

        def rotate(**kwargs):
            result = original(**kwargs)
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Retirement race coordination failed")
            return result

        def callback(owner):
            callback_started.set()
            return self.consume(owner=owner)

        with (
            patch.object(retirement, "rotate_generation", side_effect=rotate),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first = pool.submit(self.threaded, lambda owner: self.retire(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                second = pool.submit(self.threaded, callback)
                self.assertTrue(callback_started.wait(10))
            finally:
                release.set()
            self.assertEqual(
                first.result(timeout=10).snapshot.reason, "retired_before_exchange"
            )
            self.assertEqual(second.result(timeout=10).state, "rejected")
        self._post.assert_not_called()
        self._write.assert_not_called()
        self.assertEqual(ConnectorGeneration.objects.count(), 2)
