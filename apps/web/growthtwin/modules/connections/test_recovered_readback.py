"""Recovered reader protocol with fabricated metadata and mocked storage only."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, fields, replace
from datetime import timedelta
from pathlib import Path
from threading import Barrier, Event
from unittest.mock import Mock, patch
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, connection, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from . import candidate_recovered_readback as readback
from .candidate_envelope import build_envelope
from .candidate_retirement import receipt_binding_digest
from .connector_identity import IdentityConflict
from .models import CandidateInspectionPermit as Permit
from .models import ConnectorGeneration, ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt
from .test_inspection_recovery import InspectionFixture


class RecoveredFixture(InspectionFixture):
    candidate_age = timedelta(0)

    def setUp(self):
        super().setUp()
        if self.candidate_age:
            self.row.created_at -= self.candidate_age
            self.row.expires_at -= self.candidate_age
            self.row.save(update_fields=["created_at", "expires_at"])
            self.receipt_key = receipt_binding_digest(self.row)
        self.issued = self.issue()
        root = Path.cwd() / "fabricated-storage-only"
        self.locations = readback.storage.StorageLocations(
            root, root / "client.dpapi", root / "legacy.dpapi", root / "candidate.dpapi"
        )
        envelope = build_envelope(
            owner_id=self.owner.pk,
            workspace_id=self.workspace.pk,
            receipt=self.row,
            refresh_token="fabricated-recovered-only",
        )
        for name, result in (
            ("_locations", self.locations),
            ("_legacy_present", False),
            ("_client_key", self.row.client_id_hash),
            ("_read_bounded", envelope),
        ):
            guard = patch.object(readback.storage, name, return_value=result)
            setattr(self, "storage" + name, guard.start())
            self.addCleanup(guard.stop)
        guard = patch(
            "growthtwin.modules.connections.candidate_readback.inspect_candidate",
            side_effect=AssertionError("Origin-session reader forbidden"),
        )
        self.origin_reader = guard.start()
        self.addCleanup(guard.stop)

    def tearDown(self):
        for mocked in (
            self._client,
            self._post,
            self._read,
            self._write,
            self._token_path,
            self.origin_reader,
        ):
            mocked.assert_not_called()
        super().tearDown()

    def inspect(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            request_id=self.request_id,
            session_key=self.new_session,
        )
        return readback.inspect_recovered_candidate(**(values | changes))

    def consumed(self):
        permit = Permit.objects.get(pk=self.request_id)
        self.assertEqual(permit.state, Permit.State.CONSUMED)
        self.assertIsNotNone(permit.consumed_at)

    def mutation_during_read(self, mutation, errors=(IdentityConflict,)):
        envelope = self.storage_read_bounded.return_value

        def read(path):
            self.assertEqual(path, self.locations.candidate)
            mutation()
            return envelope

        self.storage_read_bounded.side_effect = read
        with self.assertRaises(errors):
            self.inspect()
        self.consumed()


@override_settings(
    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
    GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED=True,
    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True,
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
)
class RecoveredReadbackTests(RecoveredFixture, TransactionTestCase):
    def test_match_reads_exact_candidate_once_and_preserves_original_records(self):
        before = (
            list(Attempt.objects.values()),
            list(ConnectorIdentity.objects.values()),
            list(ConnectorGeneration.objects.values()),
        )
        result = self.inspect()
        self.assertEqual(result.disposition, "matches_candidate")
        self.storage_read_bounded.assert_called_once_with(self.locations.candidate)
        self.assertEqual(self.storage_legacy_present.call_count, 2)
        self.assertEqual(self.storage_client_key.call_count, 2)
        self.assertEqual(
            (
                list(Attempt.objects.values()),
                list(ConnectorIdentity.objects.values()),
                list(ConnectorGeneration.objects.values()),
            ),
            before,
        )
        self.assertEqual(
            self.storage_locations.call_args.kwargs["session_key"], self.new_session
        )
        self.assertNotEqual(self.new_session, self.session)
        self.consumed()

    def test_result_is_frozen_allowlisted_and_contains_no_sensitive_material(self):
        result = self.inspect()
        self.assertEqual(
            {f.name for f in fields(result)},
            {"request_id", "attempt_id", "disposition"},
        )
        for forbidden in (
            self.session,
            self.new_session,
            self.receipt_key,
            self.row.client_id_hash,
            "fabricated-recovered-only",
            "dpapi",
            "refresh_token",
        ):
            self.assertNotIn(forbidden, repr(result))
        with self.assertRaises(FrozenInstanceError):
            result.disposition = "other"

    def test_all_storage_probes_run_after_commit_and_outside_database_transaction(self):
        envelope = self.storage_read_bounded.return_value

        def probe(result):
            def call(*args):
                self.assertFalse(connection.in_atomic_block)
                self.consumed()
                return result

            return call

        self.storage_legacy_present.side_effect = probe(False)
        self.storage_client_key.side_effect = probe(self.row.client_id_hash)
        self.storage_read_bounded.side_effect = probe(envelope)
        self.assertEqual(self.inspect().disposition, "matches_candidate")

    def test_repeat_cannot_read_or_renew_consumed_permission(self):
        self.inspect()
        before = list(Permit.objects.values())
        self.storage_read_bounded.reset_mock()
        with self.assertRaises(IdentityConflict):
            self.inspect()
        self.storage_read_bounded.assert_not_called()
        self.assertEqual(before, list(Permit.objects.values()))

    def test_each_switch_requires_exact_true_before_any_storage(self):
        for flag in (
            "GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED",
            "GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED",
            "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED",
            "GOOGLE_ADS_LOCAL_OAUTH_ENABLED",
        ):
            for value in (False, "true", 1, None):
                with override_settings(**{flag: value}):
                    with self.assertRaises(PermissionDenied):
                        self.inspect()
        self.storage_locations.assert_not_called()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_wrong_owner_workspace_session_and_inactive_owner_deny_before_storage(self):
        other = get_user_model().objects.create_user(username="recovered-other")
        workspace = Workspace.objects.create(owner=other, name="Foreign")
        for changes, error in (
            ({"owner": other}, Workspace.DoesNotExist),
            ({"workspace_id": workspace.pk}, Workspace.DoesNotExist),
            ({"owner": AnonymousUser()}, PermissionDenied),
            ({"session_key": self.session}, IdentityConflict),
        ):
            with self.assertRaises(error):
                self.inspect(**changes)
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            self.inspect()
        self.storage_read_bounded.assert_not_called()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_invalid_ids_or_caller_snapshot_path_reader_denied_before_claim(self):
        for name in ("connection_id", "attempt_id", "request_id"):
            for value in (UUID(int=0), "not-uuid"):
                with self.assertRaises(ValueError):
                    self.inspect(**{name: value})
        for name in ("path", "reader", "snapshot", "locations"):
            with self.assertRaises(TypeError):
                self.inspect(**{name: self.issued})
        self.storage_read_bounded.assert_not_called()

    def test_caller_transaction_is_rejected_before_claim(self):
        with transaction.atomic():
            with self.assertRaises(IdentityConflict):
                self.inspect()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
        self.storage_locations.assert_not_called()

    def test_mapping_error_before_claim_cannot_consume_or_read(self):
        self.storage_locations.side_effect = readback.backend.ConnectionUnavailable(
            "Unmapped"
        )
        with self.assertRaises(readback.backend.ConnectionUnavailable):
            self.inspect()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
        self.storage_read_bounded.assert_not_called()

    def test_busy_lock_has_bounded_wait_and_does_not_consume(self):
        lock = Mock()
        lock.acquire.return_value = False
        with patch.object(readback.backend, "_LOCK", lock):
            with self.assertRaises(IdentityConflict):
                self.inspect()
        lock.acquire.assert_called_once_with(timeout=readback.LOCK_WAIT_SECONDS)
        lock.release.assert_not_called()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_expired_permission_denies_before_claim(self):
        with patch.object(
            readback.timezone, "now", return_value=self.issued.expires_at
        ):
            with self.assertRaises(IdentityConflict):
                self.inspect()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
        self.storage_read_bounded.assert_not_called()

    def test_existing_legacy_blocks_candidate_and_client_reads(self):
        self.storage_legacy_present.return_value = True
        self.assertEqual(self.inspect().disposition, "legacy_exists")
        self.storage_client_key.assert_not_called()
        self.storage_read_bounded.assert_not_called()
        self.consumed()

    def test_changed_configured_client_blocks_candidate_read(self):
        self.storage_client_key.return_value = "0" * 64
        self.assertEqual(self.inspect().disposition, "client_changed")
        self.storage_read_bounded.assert_not_called()

    def test_malformed_storage_metadata_is_unreadable(self):
        self.storage_legacy_present.return_value = 1
        self.assertEqual(self.inspect().disposition, "unreadable")
        self.storage_read_bounded.assert_not_called()

    def test_malformed_envelope_is_rejected_without_token_return(self):
        self.storage_read_bounded.return_value = {"refresh_token": "fabricated"}
        self.assertEqual(self.inspect().disposition, "invalid_envelope")

    def test_storage_error_sanitized_and_consumption_never_reopens(self):
        self.storage_read_bounded.side_effect = RuntimeError(
            "fabricated-sensitive-failure"
        )
        result = self.inspect()
        self.assertEqual(result.disposition, "unreadable")
        self.assertNotIn("fabricated-sensitive-failure", repr(result))
        self.consumed()
        with self.assertRaises(IdentityConflict):
            self.inspect()

    def test_legacy_appearance_after_read_prevents_match(self):
        self.storage_legacy_present.side_effect = (False, True)
        self.assertEqual(self.inspect().disposition, "legacy_exists")

    def test_client_change_after_read_prevents_match(self):
        self.storage_client_key.side_effect = (self.row.client_id_hash, "0" * 64)
        self.assertEqual(self.inspect().disposition, "client_changed")

    def test_root_drift_during_read_never_reads_from_shifted_root(self):
        envelope = self.storage_read_bounded.return_value

        def read(path):
            self.storage_locations.return_value = replace(
                self.locations, root=self.locations.root / "changed"
            )
            return envelope

        self.storage_read_bounded.side_effect = read
        with self.assertRaises(IdentityConflict):
            self.inspect()
        self.storage_read_bounded.assert_called_once_with(self.locations.candidate)
        self.assertEqual(self.storage_client_key.call_count, 1)

    def test_mapping_change_before_read_does_not_read_any_candidate(self):
        def client(locations):
            self.storage_locations.return_value = replace(
                self.locations, candidate=self.locations.root / "wrong.dpapi"
            )
            return self.row.client_id_hash

        self.storage_client_key.side_effect = client
        with self.assertRaises(IdentityConflict):
            self.inspect()
        self.storage_read_bounded.assert_not_called()

    def test_second_client_probe_mapping_drift_is_rejected_by_final_check(self):
        calls = 0

        def client(locations):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.storage_locations.return_value = replace(
                    self.locations, root=self.locations.root / "late-change"
                )
            return self.row.client_id_hash

        self.storage_client_key.side_effect = client
        with self.assertRaises(IdentityConflict):
            self.inspect()
        self.storage_read_bounded.assert_called_once_with(self.locations.candidate)
        self.consumed()

    def test_deadline_crossing_inside_metadata_lock_is_rejected(self):
        original = readback.recovery._scope
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            request_id=self.request_id,
            session_key=self.new_session,
        )
        with patch.object(readback, "monotonic", return_value=100) as clock:

            def scope(*args):
                result = original(*args)
                clock.return_value = 160
                return result

            with patch.object(readback.recovery, "_scope", side_effect=scope):
                with self.assertRaises(IdentityConflict):
                    readback._checked(values, deadline=160)
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
        self.storage_read_bounded.assert_not_called()

    def test_postread_owner_transfer_denies_match(self):
        other = get_user_model().objects.create_user(username="new-recovered-owner")
        self.mutation_during_read(
            lambda: Workspace.objects.filter(pk=self.workspace.pk).update(owner=other),
            (Workspace.DoesNotExist,),
        )

    def test_postread_owner_deactivation_denies_match(self):
        self.mutation_during_read(
            lambda: (
                get_user_model()
                .objects.filter(pk=self.owner.pk)
                .update(is_active=False)
            ),
            (PermissionDenied, Workspace.DoesNotExist),
        )

    def test_postread_rotation_denies_match(self):
        self.mutation_during_read(self.rotate)

    def test_postread_block_denies_match(self):
        self.mutation_during_read(self.block)

    def test_postread_receipt_change_denies_match(self):
        self.mutation_during_read(
            lambda: Attempt.objects.filter(pk=self.attempt_id).update(
                session_key_hash="0" * 64
            )
        )

    def test_postread_permit_session_change_denies_match(self):
        self.mutation_during_read(
            lambda: Permit.objects.filter(pk=self.request_id).update(
                session_key_hash="0" * 64
            )
        )

    def test_postread_permit_deadline_change_denies_match(self):
        self.mutation_during_read(
            lambda: Permit.objects.filter(pk=self.request_id).update(
                created_at=self.issued.created_at - timedelta(seconds=1),
                expires_at=self.issued.expires_at - timedelta(seconds=1),
            )
        )

    def test_postread_key_loss_denies_without_rebinding(self):
        def change():
            setting = override_settings(SECRET_KEY="fabricated-replaced-current-key")
            setting.enable()
            self.addCleanup(setting.disable)

        self.mutation_during_read(change)

    def test_postread_flag_loss_denies_match(self):
        def change():
            setting = override_settings(GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED=False)
            setting.enable()
            self.addCleanup(setting.disable)

        self.mutation_during_read(change, (PermissionDenied,))

    def test_postread_expiry_denies_match(self):
        def change():
            clock = patch.object(
                readback.timezone, "now", return_value=self.issued.expires_at
            )
            clock.start()
            self.addCleanup(clock.stop)

        self.mutation_during_read(change)

    def test_postread_clock_before_consumption_denies_match(self):
        def change():
            permit = Permit.objects.get(pk=self.request_id)
            clock = patch.object(
                readback.timezone,
                "now",
                return_value=permit.consumed_at - timedelta(microseconds=1),
            )
            clock.start()
            self.addCleanup(clock.stop)

        self.mutation_during_read(change)

    def test_monotonic_observation_deadline_denies_late_result(self):
        envelope = self.storage_read_bounded.return_value
        with patch.object(readback, "monotonic", return_value=100) as clock:

            def read(path):
                clock.return_value = 100 + readback.OBSERVATION_SECONDS
                return envelope

            self.storage_read_bounded.side_effect = read
            with self.assertRaises(IdentityConflict):
                self.inspect()
        self.consumed()


@override_settings(
    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
    GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED=True,
    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True,
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
)
class OldCandidateReadbackTests(RecoveredFixture, TransactionTestCase):
    candidate_age = timedelta(days=1)

    def test_expired_original_handshake_does_not_expire_current_recovery_permission(
        self,
    ):
        self.assertEqual(self.inspect().disposition, "matches_candidate")


@override_settings(
    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
    GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED=True,
    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True,
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
)
class RecoveredReadbackRaceTests(RecoveredFixture, TransactionTestCase):
    def threaded(self, barrier=None):
        close_old_connections()
        try:
            owner = get_user_model().objects.get(pk=self.owner.pk)
            if barrier:
                barrier.wait(timeout=10)
            try:
                return self.inspect(owner=owner)
            except IdentityConflict:
                return "conflict"
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_readers_read_candidate_at_most_once(self):
        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.threaded(barrier), range(2)))
        self.storage_read_bounded.assert_called_once_with(self.locations.candidate)
        self.assertEqual(sum(result == "conflict" for result in results), 1)
        self.assertEqual(
            sum(
                getattr(r, "disposition", None) == "matches_candidate" for r in results
            ),
            1,
        )
        self.consumed()

    @skipUnlessDBFeature("has_select_for_update")
    def test_rotation_during_read_denies_postread_match(self):
        reading, resume = Event(), Event()
        envelope = self.storage_read_bounded.return_value

        def read(path):
            self.assertFalse(connection.in_atomic_block)
            reading.set()
            if not resume.wait(timeout=10):
                raise AssertionError("Fabricated race did not resume")
            return envelope

        self.storage_read_bounded.side_effect = read
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(self.threaded)
            try:
                self.assertTrue(reading.wait(timeout=10))
                self.rotate()
            finally:
                resume.set()
            self.assertEqual(future.result(timeout=10), "conflict")
        self.consumed()
