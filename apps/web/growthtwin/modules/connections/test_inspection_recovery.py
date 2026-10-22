"""Metadata-only recovery permits: fabricated receipts and zero I/O boundaries."""

import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, fields
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch
from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, close_old_connections, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature
from django.utils import timezone

from growthtwin.modules.workspaces.models import Workspace

from . import candidate_inspection_recovery as recovery
from . import test_scoped_oauth_candidate as fixtures
from .candidate_retirement import receipt_binding_digest
from .connector_identity import IdentityConflict, register_google_test_identity
from .models import CandidateInspectionPermit as Permit
from .models import ConnectorGeneration, ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


class InspectionFixture(fixtures.CandidateFixture):
    def setUp(self):
        super().setUp()
        now = timezone.now()
        self.row = Attempt.objects.create(
            pk=self.attempt_id,
            connection_id=self.identity.connection_id,
            generation=self.identity.generation,
            expected_revision=self.identity.revision,
            session_key_hash=fixtures.candidate._session_key(self.session),
            client_id_hash=hashlib.sha256(b"fabricated-client-id").hexdigest(),
            state=Attempt.State.CANDIDATE,
            created_at=now,
            expires_at=now + timedelta(minutes=5),
        )
        self.new_session = "fabricated-recovery-session"
        self.request_id = uuid4()
        self.receipt_key = receipt_binding_digest(self.row)

    def metadata_only(self, call, values):
        boundaries = (
            self._enabled,
            self._client,
            self._post,
            self._read,
            self._write,
            self._token_path,
        )
        counts = [mock.call_count for mock in boundaries]
        before = (
            list(Attempt.objects.values()),
            list(ConnectorIdentity.objects.values()),
            list(ConnectorGeneration.objects.values()),
        )
        try:
            return call(**values)
        finally:
            self.assertEqual([mock.call_count for mock in boundaries], counts)
            self.assertEqual(
                (
                    list(Attempt.objects.values()),
                    list(ConnectorIdentity.objects.values()),
                    list(ConnectorGeneration.objects.values()),
                ),
                before,
            )

    def issue(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            request_id=self.request_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
            expected_receipt_key=self.receipt_key,
            session_key=self.new_session,
            recovery_confirmation=True,
        )
        return self.metadata_only(recovery.issue_inspection_permit, values | changes)

    def claim(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            request_id=self.request_id,
            session_key=self.new_session,
        )
        return self.metadata_only(recovery.consume_inspection_permit, values | changes)


@override_settings(GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True)
class InspectionRecoveryTests(InspectionFixture, TransactionTestCase):
    def test_backend_and_existing_reader_hooks_are_never_used(self):
        boundaries = (
            self._enabled,
            self._client,
            self._post,
            self._read,
            self._write,
            self._token_path,
        )
        for mocked in boundaries:
            mocked.reset_mock()
        with patch(
            "growthtwin.modules.connections.candidate_readback.inspect_candidate",
            side_effect=AssertionError("Existing reader must remain disconnected"),
        ) as reader:
            self.issue()
            self.claim()
            reader.assert_not_called()
        for mocked in boundaries:
            mocked.assert_not_called()

    def test_issue_is_metadata_only_binds_new_session_and_preserves_original(self):
        original = Attempt.objects.get(pk=self.attempt_id)
        result = self.issue()
        permit = Permit.objects.get()
        self.assertEqual(result.request_id, self.request_id)
        self.assertEqual(result.state, Permit.State.ISSUED)
        self.assertEqual(result.generation, self.identity.generation)
        self.assertEqual(result.expected_revision, self.identity.revision)
        self.assertEqual(result.expires_at - result.created_at, timedelta(minutes=5))
        self.assertIsNone(result.consumed_at)
        self.assertEqual(permit.owner_id, self.owner.pk)
        self.assertEqual(permit.workspace_id, self.workspace.pk)
        self.assertEqual(permit.receipt_key, self.receipt_key)
        self.assertNotEqual(permit.session_key_hash, self.new_session)
        self.assertNotEqual(permit.session_key_hash, original.session_key_hash)
        self.assertEqual(
            Attempt.objects.get().session_key_hash, original.session_key_hash
        )
        self.assertEqual(
            receipt_binding_digest(Attempt.objects.get()), self.receipt_key
        )
        self.assertEqual(ConnectorIdentity.objects.get().state, "quarantined")

    def test_snapshot_is_frozen_allowlisted_and_never_contains_secret_or_digest(self):
        for snapshot in (self.issue(), self.claim()):
            self.assertEqual(
                {field.name for field in fields(snapshot)},
                {
                    "request_id",
                    "connection_id",
                    "attempt_id",
                    "generation",
                    "expected_revision",
                    "state",
                    "created_at",
                    "expires_at",
                    "consumed_at",
                },
            )
            for forbidden in (
                "fabricated",
                self.new_session,
                self.session,
                self.receipt_key,
                Permit.objects.get().session_key_hash,
                "refresh_token",
                "dpapi",
            ):
                self.assertNotIn(forbidden, repr(snapshot))
            with self.assertRaises(FrozenInstanceError):
                snapshot.state = Permit.State.CONSUMED

    def test_default_off_and_non_boolean_flag_deny_issue_and_consume(self):
        for value in (False, "true", 1, None):
            with override_settings(
                GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=value
            ):
                with self.assertRaises(PermissionDenied):
                    self.issue()
                with self.assertRaises(PermissionDenied):
                    self.claim()
        self.assertEqual(Permit.objects.count(), 0)

    def test_confirmation_must_be_explicit_boolean(self):
        for value in (False, None, 1, "true"):
            with self.assertRaises(ValueError):
                self.issue(recovery_confirmation=value)
        self.assertEqual(Permit.objects.count(), 0)

    def test_invalid_sessions_receipt_keys_uuid_and_revision_fail_before_writes(self):
        for session in (None, "", 1, "x" * 257):
            with self.assertRaises(ValueError):
                self.issue(session_key=session)
            with self.assertRaises(ValueError):
                self.claim(session_key=session)
        for key in (None, "", "g" * 64, "A" * 64, "a" * 63):
            with self.assertRaises(ValueError):
                self.issue(expected_receipt_key=key)
        for field in (
            "connection_id",
            "attempt_id",
            "request_id",
            "expected_generation",
        ):
            for value in (UUID(int=0), "not-a-uuid"):
                with self.assertRaises(ValueError):
                    self.issue(**{field: value})
        for revision in (-1, True, 2**63 - 1):
            with self.assertRaises(ValueError):
                self.issue(expected_revision=revision)
        self.assertEqual(Permit.objects.count(), 0)

    def test_foreign_anonymous_and_inactive_owner_cannot_issue_or_consume(self):
        other = get_user_model().objects.create_user(username="foreign-inspection")
        foreign = Workspace.objects.create(owner=other, name="Foreign fixture")
        self.issue()
        for owner, error in (
            (other, Workspace.DoesNotExist),
            (AnonymousUser(), PermissionDenied),
        ):
            with self.assertRaises(error):
                self.issue(owner=owner)
            with self.assertRaises(error):
                self.claim(owner=owner)
        for method in (self.issue, self.claim):
            with self.assertRaises(Workspace.DoesNotExist):
                method(workspace_id=foreign.pk)
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        for method in (self.issue, self.claim):
            with self.assertRaises(PermissionDenied):
                method()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_wrong_new_session_cannot_replay_or_consume(self):
        self.issue()
        for session in (self.session, "fabricated-other-session"):
            with self.assertRaises(IdentityConflict):
                self.issue(session_key=session)
            with self.assertRaises(IdentityConflict):
                self.claim(session_key=session)
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_original_secret_key_change_can_issue_new_binding_without_rewriting_receipt(
        self,
    ):
        with override_settings(SECRET_KEY="fabricated-old-test-key"):
            old_hash = fixtures.candidate._session_key(self.session)
            Attempt.objects.filter(pk=self.attempt_id).update(session_key_hash=old_hash)
        self.row.refresh_from_db()
        self.receipt_key = receipt_binding_digest(self.row)
        before = list(Attempt.objects.values())
        with override_settings(SECRET_KEY="fabricated-new-test-key"):
            self.issue()
            self.assertEqual(self.claim().state, Permit.State.CONSUMED)
        self.assertEqual(list(Attempt.objects.values()), before)
        self.assertEqual(Attempt.objects.get().session_key_hash, old_hash)

    def test_key_change_after_permit_issue_does_not_rebind_or_renew(self):
        self.issue()
        before = list(Permit.objects.values())
        with override_settings(SECRET_KEY="fabricated-other-current-test-key"):
            with self.assertRaises(IdentityConflict):
                self.issue()
            with self.assertRaises(IdentityConflict):
                self.claim()
        self.assertEqual(list(Permit.objects.values()), before)

    def test_exact_request_replay_is_unchanged_and_distinct_request_cannot_renew(self):
        first = self.issue()
        before = list(Permit.objects.values())
        self.assertEqual(self.issue(), first)
        with self.assertRaises(IdentityConflict):
            self.issue(request_id=uuid4())
        self.assertEqual(list(Permit.objects.values()), before)
        self.assertEqual(Permit.objects.count(), 1)

    def test_expired_permit_replay_is_historical_and_never_extends_or_consumes(self):
        first = self.issue()
        with patch.object(recovery.timezone, "now", return_value=first.expires_at):
            self.assertEqual(self.issue(), first)
            with self.assertRaises(IdentityConflict):
                self.claim()
            with self.assertRaises(IdentityConflict):
                self.issue(request_id=uuid4())
        self.assertEqual(Permit.objects.get().expires_at, first.expires_at)
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_consume_is_once_and_replay_issue_returns_consumed_metadata(self):
        self.issue()
        claimed = self.claim()
        self.assertEqual(claimed.state, Permit.State.CONSUMED)
        self.assertIsNotNone(claimed.consumed_at)
        self.assertEqual(self.issue(), claimed)
        with self.assertRaises(IdentityConflict):
            self.claim()
        with self.assertRaises(IdentityConflict):
            self.issue(request_id=uuid4())
        self.assertEqual(self.issue(), claimed)
        self.assertEqual(Attempt.objects.get().state, Attempt.State.CANDIDATE)

    def test_caller_transaction_is_denied_for_issue_and_consume(self):
        with transaction.atomic():
            with self.assertRaises(IdentityConflict):
                self.issue()
        self.assertEqual(Permit.objects.count(), 0)
        self.issue()
        with transaction.atomic():
            with self.assertRaises(IdentityConflict):
                self.claim()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
        self.claim()
        try:
            with transaction.atomic():
                raise RuntimeError("Fabricated unrelated caller rollback")
        except RuntimeError:
            pass
        self.assertEqual(Permit.objects.get().state, Permit.State.CONSUMED)

    def test_stale_expected_generation_revision_and_receipt_are_denied(self):
        for changes in (
            {"expected_generation": uuid4()},
            {"expected_revision": 1},
            {"expected_receipt_key": "0" * 64},
        ):
            with self.assertRaises(IdentityConflict):
                self.issue(**changes)
        self.assertEqual(Permit.objects.count(), 0)

    def test_candidate_digest_change_prevents_replay_and_consume(self):
        self.issue()
        Attempt.objects.filter(pk=self.attempt_id).update(client_id_hash="0" * 64)
        for method in (self.issue, self.claim):
            with self.assertRaises(IdentityConflict):
                method()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_block_and_generation_rotation_prevent_use(self):
        self.issue()
        self.block()
        for method in (self.issue, self.claim):
            with self.assertRaises(IdentityConflict):
                method()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_generation_rotation_before_issue_leaves_no_permit(self):
        self.rotate()
        with self.assertRaises(IdentityConflict):
            self.issue()
        self.assertEqual(Permit.objects.count(), 0)

    def test_non_candidate_states_never_issue_or_consume(self):
        self.issue()
        for state, reason in (
            (Attempt.State.RESERVED, ""),
            (Attempt.State.EXCHANGING, ""),
            (Attempt.State.UNCERTAIN, "exchange_uncertain"),
            (Attempt.State.REJECTED, "callback_invalid"),
        ):
            Attempt.objects.filter(pk=self.attempt_id).update(
                state=state, reason=reason
            )
            for method in (self.issue, self.claim):
                with self.assertRaises(IdentityConflict):
                    method()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_expired_original_handshake_can_issue_metadata_permit_only(self):
        old = timezone.now() - timedelta(days=2)
        Attempt.objects.filter(pk=self.attempt_id).update(
            created_at=old, expires_at=old + timedelta(minutes=5)
        )
        self.row.refresh_from_db()
        self.receipt_key = receipt_binding_digest(self.row)
        result = self.issue()
        self.assertEqual(result.state, Permit.State.ISSUED)
        self.assertGreater(result.created_at, self.row.expires_at)

    def test_unknown_attempt_connection_and_permit_are_not_created_or_consumed(self):
        with self.assertRaises(Attempt.DoesNotExist):
            self.issue(attempt_id=uuid4())
        with self.assertRaises(ConnectorIdentity.DoesNotExist):
            self.issue(connection_id=uuid4())
        with self.assertRaises(Permit.DoesNotExist):
            self.claim(request_id=uuid4())
        self.assertEqual(Permit.objects.count(), 0)

    def test_competing_non_rejected_attempt_requires_review_before_issue(self):
        Attempt.objects.create(
            pk=uuid4(),
            connection_id=self.identity.connection_id,
            generation=uuid4(),
            expected_revision=0,
            session_key_hash="0" * 64,
            client_id_hash="0" * 64,
            state=Attempt.State.UNCERTAIN,
            reason="exchange_uncertain",
            created_at=self.row.created_at,
            expires_at=self.row.expires_at,
        )
        with self.assertRaises(IdentityConflict):
            self.issue()
        self.assertEqual(Permit.objects.count(), 0)

    def test_request_id_cannot_be_replayed_for_another_scoped_candidate(self):
        self.issue()
        workspace = Workspace.objects.create(owner=self.owner, name="Second fixture")
        identity = register_google_test_identity(
            owner=self.owner, workspace_id=workspace.pk, request_id=uuid4()
        )
        row = Attempt.objects.create(
            pk=uuid4(),
            connection_id=identity.connection_id,
            generation=identity.generation,
            expected_revision=identity.revision,
            session_key_hash="0" * 64,
            client_id_hash="0" * 64,
            state=Attempt.State.CANDIDATE,
            created_at=self.row.created_at,
            expires_at=self.row.expires_at,
        )
        with self.assertRaises(IdentityConflict):
            self.issue(
                workspace_id=workspace.pk,
                connection_id=identity.connection_id,
                attempt_id=row.pk,
                expected_generation=identity.generation,
                expected_revision=identity.revision,
                expected_receipt_key=receipt_binding_digest(row),
            )
        self.assertEqual(Permit.objects.count(), 1)
        self.assertEqual(Permit.objects.get().attempt_id, self.attempt_id)

    def test_corrupt_permit_binding_fails_closed_without_repair(self):
        self.issue()
        original = dict(Permit.objects.values().get())
        for changes in (
            {"generation": uuid4()},
            {"expected_revision": 1},
            {"session_key_hash": "0" * 64},
            {"receipt_key": "0" * 64},
            {"session_key_hash": "not-a-digest"},
            {"receipt_key": "not-a-digest"},
            {"expires_at": original["expires_at"] + timedelta(seconds=1)},
            {
                "created_at": original["created_at"] + timedelta(days=1),
                "expires_at": original["expires_at"] + timedelta(days=1),
            },
        ):
            Permit.objects.filter(pk=self.request_id).update(**changes)
            for method in (self.issue, self.claim):
                with self.assertRaises(IdentityConflict):
                    method()
            Permit.objects.filter(pk=self.request_id).update(
                **{key: original[key] for key in changes}
            )
        self.assertEqual(dict(Permit.objects.values().get()), original)

    def test_db_constraints_enforce_one_attempt_positive_lifetime_and_consumption_shape(
        self,
    ):
        self.issue()
        original = dict(Permit.objects.values().get())
        duplicate = original | {"id": uuid4()}
        with self.assertRaises(IntegrityError), transaction.atomic():
            Permit.objects.create(**duplicate)
        for changes in (
            {"expires_at": original["created_at"]},
            {"state": Permit.State.CONSUMED},
            {"consumed_at": original["created_at"]},
            {"state": "unknown"},
            {"state": Permit.State.CONSUMED, "consumed_at": original["expires_at"]},
        ):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Permit.objects.filter(pk=self.request_id).update(**changes)
        self.assertEqual(dict(Permit.objects.values().get()), original)


@override_settings(GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True)
class InspectionRecoveryRaceTests(InspectionFixture, TransactionTestCase):
    def threaded(self, barrier, call):
        close_old_connections()
        try:
            owner = get_user_model().objects.get(pk=self.owner.pk)
            barrier.wait(timeout=10)
            try:
                return call(owner)
            except IdentityConflict:
                return "conflict"
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_distinct_issue_requests_create_one_permit(self):
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda request_id: self.threaded(
                        barrier,
                        lambda owner: self.issue(owner=owner, request_id=request_id),
                    ),
                    (uuid4(), uuid4()),
                )
            )
        self.assertEqual(sum(result == "conflict" for result in results), 1)
        self.assertEqual(
            sum(
                getattr(result, "state", None) == Permit.State.ISSUED
                for result in results
            ),
            1,
        )
        self.assertEqual(Permit.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_consumers_commit_only_one_consumption(self):
        self.issue()
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda _: self.threaded(
                        barrier, lambda owner: self.claim(owner=owner)
                    ),
                    range(2),
                )
            )
        self.assertEqual(sum(result == "conflict" for result in results), 1)
        self.assertEqual(
            sum(
                getattr(result, "state", None) == Permit.State.CONSUMED
                for result in results
            ),
            1,
        )
        self.assertEqual(Permit.objects.count(), 1)
        self.assertEqual(Permit.objects.get().state, Permit.State.CONSUMED)
