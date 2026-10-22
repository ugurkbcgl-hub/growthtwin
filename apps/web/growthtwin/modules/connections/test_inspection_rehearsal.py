"""Fixed in-memory inspection only: irreversible claims and post-read fences."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, fields, replace
from datetime import timedelta
from threading import Barrier, Event
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, connection, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from . import candidate_inspection_rehearsal as rehearsal
from .candidate_retirement import receipt_binding_digest
from .connector_identity import IdentityConflict
from .models import CandidateInspectionPermit as Permit
from .models import ConnectorGeneration, ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt
from .test_inspection_recovery import InspectionFixture


class RehearsalFixture(InspectionFixture):
    def setUp(self):
        super().setUp()
        self.row.client_id_hash = rehearsal.FIXTURE_CLIENT_HASH
        self.row.save(update_fields=["client_id_hash"])
        self.receipt_key = receipt_binding_digest(self.row)
        self.issued = self.issue()
        for target in (
            "growthtwin.modules.connections.candidate_readback.inspect_candidate",
            "growthtwin.modules.connections.scoped_oauth_candidate._candidate_path",
        ):
            guard = patch(target, side_effect=AssertionError("Real reader forbidden"))
            mocked = guard.start()
            self.addCleanup(guard.stop)
            self.addCleanup(mocked.assert_not_called)

    def tearDown(self):
        for mocked in (
            self._enabled,
            self._client,
            self._post,
            self._read,
            self._write,
            self._token_path,
        ):
            mocked.assert_not_called()
        super().tearDown()

    def run_rehearsal(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            request_id=self.request_id,
            session_key=self.new_session,
        )
        return rehearsal.rehearse_inspection(**(values | changes))

    def assert_consumed(self):
        permit = Permit.objects.get(pk=self.request_id)
        self.assertEqual(permit.state, Permit.State.CONSUMED)
        self.assertIsNotNone(permit.consumed_at)

    def fail_after_read(self, mutation, errors=(IdentityConflict,)):
        original = rehearsal._FixtureProbe.read

        def read(probe, address):
            value = original(probe, address)
            mutation()
            return value

        with patch.object(rehearsal._FixtureProbe, "read", read):
            with self.assertRaises(errors):
                self.run_rehearsal()
        self.assert_consumed()


@override_settings(
    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
    GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED=True,
)
class InspectionRehearsalTests(RehearsalFixture, TransactionTestCase):
    def test_match_is_synthetic_safe_frozen_and_original_records_are_unchanged(self):
        before = (
            list(Attempt.objects.values()),
            list(ConnectorIdentity.objects.values()),
            list(ConnectorGeneration.objects.values()),
        )
        result = self.run_rehearsal()
        self.assertEqual(result.disposition, "synthetic_match")
        self.assertEqual(result.request_id, self.request_id)
        self.assertEqual(result.attempt_id, self.attempt_id)
        self.assertEqual(
            {field.name for field in fields(result)},
            {"request_id", "attempt_id", "disposition"},
        )
        for forbidden in (
            self.new_session,
            self.session,
            self.receipt_key,
            "fabricated-inspection-only",
            "refresh_token",
            "dpapi",
            "path",
        ):
            self.assertNotIn(forbidden, repr(result))
        with self.assertRaises(FrozenInstanceError):
            result.disposition = "matches_candidate"
        self.assertEqual(
            (
                list(Attempt.objects.values()),
                list(ConnectorIdentity.objects.values()),
                list(ConnectorGeneration.objects.values()),
            ),
            before,
        )
        self.assert_consumed()

    def assert_negative_scenario(self, scenario):
        result = self.run_rehearsal(scenario=scenario)
        self.assertEqual(result.disposition, scenario)
        self.assert_consumed()

    def test_fixed_legacy_scenario_consumes_without_real_storage(self):
        self.assert_negative_scenario("legacy_exists")

    def test_fixed_client_change_scenario_consumes_without_real_storage(self):
        self.assert_negative_scenario("client_changed")

    def test_fixed_invalid_envelope_scenario_consumes_without_real_storage(self):
        self.assert_negative_scenario("invalid_envelope")

    def test_fixed_unreadable_scenario_consumes_without_real_storage(self):
        self.assert_negative_scenario("unreadable")

    def test_claim_is_committed_and_probe_calls_have_no_database_transaction(self):
        original = rehearsal._FixtureProbe.read
        original_legacy = rehearsal._FixtureProbe.legacy_present
        original_client = rehearsal._FixtureProbe.client_hash

        def legacy(probe):
            self.assertFalse(connection.in_atomic_block)
            self.assert_consumed()
            return original_legacy(probe)

        def client(probe):
            self.assertFalse(connection.in_atomic_block)
            self.assert_consumed()
            return original_client(probe)

        def read(probe, address):
            self.assertFalse(connection.in_atomic_block)
            self.assert_consumed()
            self.assertEqual(address.owner_id, str(self.owner.pk))
            self.assertEqual(address.workspace_id, str(self.workspace.pk))
            self.assertEqual(address.connection_id, self.identity.connection_id)
            self.assertEqual(address.attempt_id, self.attempt_id)
            self.assertEqual(address.generation, self.identity.generation)
            return original(probe, address)

        with (
            patch.object(rehearsal._FixtureProbe, "read", read),
            patch.object(rehearsal._FixtureProbe, "legacy_present", legacy),
            patch.object(rehearsal._FixtureProbe, "client_hash", client),
        ):
            self.assertEqual(self.run_rehearsal().disposition, "synthetic_match")

    def test_duplicate_never_reads_again_or_renews_permission(self):
        self.run_rehearsal()
        before = list(Permit.objects.values())
        with patch.object(rehearsal._FixtureProbe, "read") as read:
            with self.assertRaises(IdentityConflict):
                self.run_rehearsal()
            read.assert_not_called()
        self.assertEqual(list(Permit.objects.values()), before)

    def test_both_flags_require_exact_true_before_claim(self):
        for flag in (
            "GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED",
            "GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED",
        ):
            for value in (False, None, "true", 1):
                with override_settings(**{flag: value}):
                    with self.assertRaises(PermissionDenied):
                        self.run_rehearsal()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_unknown_scenario_and_caller_supplied_reader_or_snapshot_are_rejected(self):
        for scenario in (None, "", "real", 1, ["match"]):
            with self.assertRaises(ValueError):
                self.run_rehearsal(scenario=scenario)
        for parameter in ("reader", "probe", "snapshot", "path"):
            with self.assertRaises(TypeError):
                self.run_rehearsal(**{parameter: self.issued})
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_nonfixture_client_cannot_consume_even_with_valid_matching_permit(self):
        Attempt.objects.filter(pk=self.attempt_id).update(client_id_hash="0" * 64)
        self.row.refresh_from_db()
        Permit.objects.filter(pk=self.request_id).update(
            receipt_key=receipt_binding_digest(self.row)
        )
        with patch.object(rehearsal._FixtureProbe, "read") as read:
            with self.assertRaises(IdentityConflict):
                self.run_rehearsal()
            read.assert_not_called()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_expired_permission_denies_before_claim_and_probe(self):
        with (
            patch.object(
                rehearsal.timezone, "now", return_value=self.issued.expires_at
            ),
            patch.object(rehearsal._FixtureProbe, "read") as read,
        ):
            with self.assertRaises(IdentityConflict):
                self.run_rehearsal()
            read.assert_not_called()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_wrong_session_owner_or_workspace_denied_before_claim(self):
        other = get_user_model().objects.create_user(username="foreign-rehearsal")
        workspace = Workspace.objects.create(owner=other, name="Foreign")
        for changes, error in (
            ({"session_key": self.session}, IdentityConflict),
            ({"owner": other}, Workspace.DoesNotExist),
            ({"owner": AnonymousUser()}, PermissionDenied),
            ({"workspace_id": workspace.pk}, Workspace.DoesNotExist),
        ):
            with self.assertRaises(error):
                self.run_rehearsal(**changes)
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            self.run_rehearsal()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)

    def test_caller_transaction_cannot_rollback_a_claim(self):
        with transaction.atomic():
            with self.assertRaises(IdentityConflict):
                self.run_rehearsal()
        self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
        self.run_rehearsal()
        try:
            with transaction.atomic():
                raise RuntimeError("Synthetic later rollback")
        except RuntimeError:
            pass
        self.assert_consumed()

    def test_probe_error_is_sanitized_and_claim_remains_unrepeatable(self):
        with patch.object(
            rehearsal._FixtureProbe,
            "read",
            side_effect=RuntimeError("fabricated-sensitive-error"),
        ):
            result = self.run_rehearsal()
        self.assertEqual(result.disposition, "unreadable")
        self.assertNotIn("fabricated-sensitive-error", repr(result))
        self.assert_consumed()
        with self.assertRaises(IdentityConflict):
            self.run_rehearsal()

    def test_probe_initialization_failure_does_not_reopen_committed_claim(self):
        with patch.object(
            rehearsal._FixtureProbe,
            "__init__",
            side_effect=RuntimeError("Fabricated initialization failure"),
        ):
            with self.assertRaises(RuntimeError):
                self.run_rehearsal()
        self.assert_consumed()
        with self.assertRaises(IdentityConflict):
            self.run_rehearsal()

    def test_transient_preread_guard_failure_never_becomes_match(self):
        original = rehearsal._checked
        count = 0

        def check(**values):
            nonlocal count
            count += 1
            if count == 3:
                raise IdentityConflict("Fabricated transient pre-read failure")
            return original(**values)

        with (
            patch.object(rehearsal, "_checked", side_effect=check),
            patch.object(rehearsal._FixtureProbe, "read") as read,
        ):
            self.assertEqual(self.run_rehearsal().disposition, "unreadable")
            read.assert_not_called()
        self.assert_consumed()

    def test_postread_owner_deactivation_denies_match(self):
        self.fail_after_read(
            lambda: (
                get_user_model()
                .objects.filter(pk=self.owner.pk)
                .update(is_active=False)
            ),
            (PermissionDenied, Workspace.DoesNotExist),
        )

    def test_postread_workspace_owner_transfer_denies_match(self):
        other = get_user_model().objects.create_user(username="new-rehearsal-owner")
        self.fail_after_read(
            lambda: Workspace.objects.filter(pk=self.workspace.pk).update(owner=other),
            (Workspace.DoesNotExist,),
        )

    def test_postread_generation_rotation_denies_match(self):
        self.fail_after_read(self.rotate)

    def test_postread_block_denies_match(self):
        self.fail_after_read(self.block)

    def test_postread_original_receipt_session_mutation_denies_match(self):
        self.fail_after_read(
            lambda: Attempt.objects.filter(pk=self.attempt_id).update(
                session_key_hash="0" * 64
            )
        )

    def test_postread_candidate_client_hash_mutation_denies_match(self):
        self.fail_after_read(
            lambda: Attempt.objects.filter(pk=self.attempt_id).update(
                client_id_hash="0" * 64
            )
        )

    def test_postread_permit_session_mutation_denies_match(self):
        self.fail_after_read(
            lambda: Permit.objects.filter(pk=self.request_id).update(
                session_key_hash="0" * 64
            )
        )

    def test_postread_permit_deadline_shift_denies_even_with_valid_lifetime(self):
        self.fail_after_read(
            lambda: Permit.objects.filter(pk=self.request_id).update(
                created_at=self.issued.created_at - timedelta(seconds=1),
                expires_at=self.issued.expires_at - timedelta(seconds=1),
            )
        )

    def test_postread_consumed_timestamp_mutation_denies_match(self):
        def change():
            permit = Permit.objects.get(pk=self.request_id)
            Permit.objects.filter(pk=permit.pk).update(
                consumed_at=permit.consumed_at + timedelta(microseconds=1)
            )

        self.fail_after_read(change)

    def test_postread_secret_key_loss_denies_without_rebinding(self):
        def change():
            override = override_settings(SECRET_KEY="fabricated-different-current-key")
            override.enable()
            self.addCleanup(override.disable)

        self.fail_after_read(change)

    def test_postread_recovery_flag_loss_denies_match(self):
        def change():
            override = override_settings(
                GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=False
            )
            override.enable()
            self.addCleanup(override.disable)

        self.fail_after_read(change, (PermissionDenied,))

    def test_postread_rehearsal_flag_loss_denies_match(self):
        def change():
            override = override_settings(GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED=False)
            override.enable()
            self.addCleanup(override.disable)

        self.fail_after_read(change, (PermissionDenied,))

    def test_postread_expiry_boundary_denies_match(self):
        def change():
            clock = patch.object(
                rehearsal.timezone, "now", return_value=self.issued.expires_at
            )
            clock.start()
            self.addCleanup(clock.stop)

        self.fail_after_read(change)

    def test_postread_clock_before_consumption_denies_match(self):
        def change():
            permit = Permit.objects.get(pk=self.request_id)
            clock = patch.object(
                rehearsal.timezone,
                "now",
                return_value=permit.consumed_at - timedelta(microseconds=1),
            )
            clock.start()
            self.addCleanup(clock.stop)

        self.fail_after_read(change)

    def test_legacy_appearance_after_read_prevents_match(self):
        with patch.object(
            rehearsal._FixtureProbe, "legacy_present", side_effect=(False, True)
        ):
            result = self.run_rehearsal()
        self.assertEqual(result.disposition, "legacy_exists")
        self.assert_consumed()

    def test_client_change_after_read_prevents_match(self):
        with patch.object(
            rehearsal._FixtureProbe,
            "client_hash",
            side_effect=(rehearsal.FIXTURE_CLIENT_HASH, "0" * 64),
        ):
            result = self.run_rehearsal()
        self.assertEqual(result.disposition, "client_changed")

    def test_malformed_postread_storage_checks_are_unreadable(self):
        with patch.object(
            rehearsal._FixtureProbe, "legacy_present", side_effect=(False, 1)
        ):
            self.assertEqual(self.run_rehearsal().disposition, "unreadable")

    def test_malformed_envelope_is_never_match(self):
        with patch.object(rehearsal._FixtureProbe, "read", return_value={}):
            self.assertEqual(self.run_rehearsal().disposition, "invalid_envelope")

    def test_wrong_derived_address_is_unreadable(self):
        original = rehearsal._FixtureProbe.read

        def read(probe, address):
            return original(probe, replace(address, attempt_id=uuid4()))

        with patch.object(rehearsal._FixtureProbe, "read", read):
            self.assertEqual(self.run_rehearsal().disposition, "unreadable")


@override_settings(
    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
    GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED=True,
)
class InspectionRehearsalRaceTests(RehearsalFixture, TransactionTestCase):
    def threaded(self, barrier=None):
        close_old_connections()
        try:
            owner = get_user_model().objects.get(pk=self.owner.pk)
            if barrier:
                barrier.wait(timeout=10)
            try:
                return self.run_rehearsal(owner=owner)
            except IdentityConflict:
                return "conflict"
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_executors_read_at_most_once(self):
        barrier = Barrier(2)
        original = rehearsal._FixtureProbe.read
        with (
            patch.object(
                rehearsal._FixtureProbe, "read", autospec=True, side_effect=original
            ) as read,
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            results = list(pool.map(lambda _: self.threaded(barrier), range(2)))
        self.assertEqual(read.call_count, 1)
        self.assertEqual(sum(result == "conflict" for result in results), 1)
        self.assertEqual(
            sum(
                getattr(result, "disposition", None) == "synthetic_match"
                for result in results
            ),
            1,
        )
        self.assert_consumed()

    @skipUnlessDBFeature("has_select_for_update")
    def test_rotation_during_probe_denies_postread_match(self):
        reading = Event()
        resume = Event()
        original = rehearsal._FixtureProbe.read

        def read(probe, address):
            self.assertFalse(connection.in_atomic_block)
            reading.set()
            if not resume.wait(timeout=10):
                raise AssertionError("Synthetic race did not resume")
            return original(probe, address)

        with (
            patch.object(rehearsal._FixtureProbe, "read", read),
            ThreadPoolExecutor(max_workers=1) as pool,
        ):
            future = pool.submit(self.threaded)
            try:
                self.assertTrue(reading.wait(timeout=10))
                self.rotate()
            finally:
                resume.set()
            self.assertEqual(future.result(timeout=10), "conflict")
        self.assert_consumed()
