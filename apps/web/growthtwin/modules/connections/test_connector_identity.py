"""Connector metadata only; no credentials or preserved Google database."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from threading import Barrier
from unittest.mock import patch
from uuid import UUID, uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, close_old_connections, transaction
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from .connector_identity import (
    IdentityConflict,
    block_identity,
    get_identity,
    register_google_test_identity,
    rotate_generation,
)
from .models import ConnectorGeneration, ConnectorIdentity


class IdentityFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="identity-owner")
        self.workspace = Workspace.objects.create(
            owner=self.owner, name="Synthetic identity"
        )
        self.request_id = uuid4()

    def register(self, request_id=None):
        return register_google_test_identity(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            request_id=request_id or self.request_id,
        )

    def rotate(self, snapshot, request_id=None, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=snapshot.connection_id,
            request_id=request_id or uuid4(),
            expected_generation=snapshot.generation,
            expected_revision=snapshot.revision,
        )
        return rotate_generation(**(values | changes))

    def block(self, snapshot, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=snapshot.connection_id,
            expected_generation=snapshot.generation,
            expected_revision=snapshot.revision,
        )
        return block_identity(**(values | changes))

    def load(self, snapshot, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=snapshot.connection_id,
        )
        return get_identity(**(values | changes))


class ConnectorIdentityTests(IdentityFixture, TestCase):
    def test_registration_defaults_to_quarantine_and_has_no_secret_fields(self):
        current = self.register()
        self.assertEqual(
            (current.state, current.ordinal, current.revision), ("quarantined", 1, 0)
        )
        self.assertEqual(self.load(current), current)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)
        self.assertEqual(
            set(f.name for f in ConnectorIdentity._meta.fields),
            {
                "id",
                "workspace",
                "provider",
                "generation",
                "ordinal",
                "revision",
                "state",
                "created_at",
            },
        )
        with self.assertRaises(FrozenInstanceError):
            current.state = "open"

    def test_registration_replay_never_creates_second_connection(self):
        original = self.register()
        self.assertEqual(self.register(), original)
        with self.assertRaises(IdentityConflict):
            self.register(uuid4())
        self.assertEqual(ConnectorIdentity.objects.count(), 1)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    def test_rotation_preserves_identity_and_retires_prior_generation(self):
        original = self.register()
        newer = self.rotate(original)
        self.assertEqual(newer.connection_id, original.connection_id)
        self.assertNotEqual(newer.generation, original.generation)
        self.assertEqual(
            (newer.ordinal, newer.revision, newer.state), (2, 1, "quarantined")
        )
        self.assertEqual(ConnectorGeneration.objects.count(), 2)
        with self.assertRaises(IdentityConflict):
            self.rotate(original)
        self.assertEqual(self.load(newer), newer)

    def test_exact_rotation_replay_returns_current_state_after_later_rotation_and_block(
        self,
    ):
        original = self.register()
        operation = uuid4()
        newer = self.rotate(original, operation)
        latest = self.rotate(newer)
        blocked = self.block(latest)
        self.assertEqual(self.rotate(original, operation), blocked)
        self.assertEqual(self.register(), blocked)
        self.assertEqual(ConnectorGeneration.objects.count(), 3)

    def test_rotation_request_cannot_be_reused_with_changed_arguments(self):
        original = self.register()
        operation = uuid4()
        newer = self.rotate(original, operation)
        with self.assertRaises(IdentityConflict):
            self.rotate(newer, operation)
        self.assertEqual(ConnectorGeneration.objects.count(), 2)

    def test_block_is_permanent_and_never_infers_stop_or_revocation(self):
        original = self.register()
        blocked = self.block(original)
        self.assertEqual((blocked.state, blocked.revision), ("blocked", 1))
        self.assertEqual(self.block(blocked), blocked)
        with self.assertRaises(IdentityConflict):
            self.rotate(blocked)
        with self.assertRaises(IdentityConflict):
            self.block(original)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    def test_foreign_workspace_and_connection_cannot_be_read_rotated_or_blocked(self):
        current = self.register()
        other = get_user_model().objects.create_user(username="identity-other")
        elsewhere = Workspace.objects.create(owner=other, name="Other synthetic")
        for action in (
            lambda: self.load(current, owner=other),
            lambda: self.rotate(current, owner=other),
            lambda: self.block(current, owner=other),
        ):
            with self.assertRaises(Workspace.DoesNotExist):
                action()
        for action in (
            lambda: self.load(current, owner=other, workspace_id=elsewhere.pk),
            lambda: self.rotate(current, owner=other, workspace_id=elsewhere.pk),
            lambda: self.block(current, owner=other, workspace_id=elsewhere.pk),
        ):
            with self.assertRaises(ConnectorIdentity.DoesNotExist):
                action()
        self.assertEqual(self.load(current), current)

    def test_inactive_and_stale_owner_objects_are_denied(self):
        current = self.register()
        get_user_model().objects.filter(pk=self.owner.pk).update(is_active=False)
        with self.assertRaises(Workspace.DoesNotExist):
            self.load(current)
        self.owner.is_active = False
        with self.assertRaises(PermissionDenied):
            self.register()

    def test_typed_nonzero_uuid_and_bounded_revision_are_required(self):
        current = self.register()
        for value in (str(uuid4()), UUID(int=0), True, None):
            with self.assertRaises(ValueError):
                register_google_test_identity(
                    owner=self.owner, workspace_id=self.workspace.pk, request_id=value
                )
        for value in (True, -1, "0", 2**63 - 1):
            with self.assertRaises(ValueError):
                self.rotate(current, expected_revision=value)

    def test_global_request_identity_cannot_move_to_another_workspace(self):
        current = self.register()
        elsewhere = Workspace.objects.create(
            owner=self.owner, name="Other owned synthetic"
        )
        with self.assertRaises(IdentityConflict):
            register_google_test_identity(
                owner=self.owner, workspace_id=elsewhere.pk, request_id=self.request_id
            )
        self.assertEqual(ConnectorIdentity.objects.count(), 1)
        self.assertEqual(self.load(current), current)

    def test_metadata_read_and_writes_never_touch_provider_or_credential_adapters(self):
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
            current = self.register()
            current = self.rotate(current)
            current = self.block(current)
            self.assertEqual(self.load(current), current)

    def test_missing_history_or_corrupt_current_generation_fails_closed(self):
        current = self.register()
        ConnectorIdentity.objects.filter(pk=current.connection_id).update(
            generation=uuid4()
        )
        for action in (
            lambda: self.load(current),
            lambda: self.register(),
            lambda: self.rotate(current),
            lambda: self.block(current),
        ):
            with self.assertRaises(IdentityConflict):
                action()

    def test_corrupt_receipt_chain_cannot_rotate(self):
        original = self.register()
        current = self.rotate(original)
        ConnectorGeneration.objects.filter(pk=current.generation).update(
            from_generation=uuid4()
        )
        with self.assertRaises(IdentityConflict):
            self.rotate(current)
        self.assertEqual(ConnectorGeneration.objects.count(), 2)

    def test_failed_receipt_or_generation_collision_rolls_back(self):
        with patch(
            "growthtwin.modules.connections.connector_identity.ConnectorGeneration.objects.create",
            side_effect=RuntimeError,
        ):
            with self.assertRaises(RuntimeError):
                self.register()
        self.assertEqual(ConnectorIdentity.objects.count(), 0)
        original = self.register()
        with patch(
            "growthtwin.modules.connections.connector_identity.uuid4",
            return_value=original.generation,
        ):
            with self.assertRaises(IdentityConflict):
                self.rotate(original)
        self.assertEqual(self.load(original), original)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    def test_database_constraints_reject_open_and_production_provider(self):
        current = self.register()
        for values in (
            {"state": "open"},
            {"provider": "google_ads_live"},
            {"ordinal": 0},
        ):
            with self.assertRaises(IntegrityError), transaction.atomic():
                ConnectorIdentity.objects.filter(pk=current.connection_id).update(
                    **values
                )
        self.assertEqual(self.load(current), current)


class ConnectorIdentityRaceTests(IdentityFixture, TransactionTestCase):
    def threaded(self, call):
        close_old_connections()
        try:
            owner = get_user_model().objects.get(pk=self.owner.pk)
            return call(owner)
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_simultaneous_registration_replays_one_identity_and_generation(self):
        ready = Barrier(2)

        def run(owner):
            ready.wait(timeout=10)
            return register_google_test_identity(
                owner=owner, workspace_id=self.workspace.pk, request_id=self.request_id
            )

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.threaded, run) for _ in range(2)]
            values = [f.result(timeout=15) for f in futures]
        self.assertEqual(values[0], values[1])
        self.assertEqual(ConnectorIdentity.objects.count(), 1)
        self.assertEqual(ConnectorGeneration.objects.count(), 1)

    @skipUnlessDBFeature("has_select_for_update")
    def test_competing_rotations_admit_only_one_current_generation(self):
        current = self.register()
        ready = Barrier(2)

        def run(owner):
            ready.wait(timeout=10)
            try:
                return rotate_generation(
                    owner=owner,
                    workspace_id=self.workspace.pk,
                    connection_id=current.connection_id,
                    request_id=uuid4(),
                    expected_generation=current.generation,
                    expected_revision=current.revision,
                )
            except IdentityConflict:
                return None

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(self.threaded, run) for _ in range(2)]
            values = [f.result(timeout=15) for f in futures]
        self.assertEqual(sum(value is not None for value in values), 1)
        self.assertEqual(ConnectorGeneration.objects.count(), 2)
        self.assertEqual(self.load(current).ordinal, 2)
