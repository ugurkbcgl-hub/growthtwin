"""Advisory readback with fabricated envelopes and mocked encrypted I/O only."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
from threading import Event
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import close_old_connections, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from . import candidate_readback as readback
from . import test_scoped_oauth_candidate as fixtures
from .candidate_envelope import build_envelope, validate_envelope
from .connector_identity import IdentityConflict
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


@override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True)
class CandidateReadbackTests(fixtures.CandidateFixture, TransactionTestCase):
    def ready(self):
        self.prepare()
        self.consume()
        self.envelope = deepcopy(self._write.call_args.args[1])
        self._read.return_value = self.envelope
        self.row = Attempt.objects.get(pk=self.attempt_id)

    def inspect(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            session_key=self.session,
        )
        return readback.inspect_candidate(**(values | changes))

    def valid(self, value):
        return validate_envelope(
            value,
            owner_id=self.owner.pk,
            workspace_id=self.workspace.pk,
            receipt=self.row,
        )

    def test_strict_binding_rejects_each_mismatched_field(self):
        self.ready()
        self.assertTrue(self.valid(self.envelope))
        for key in self.envelope:
            with self.subTest(field=key):
                value = self.envelope | {key: None}
                self.assertFalse(self.valid(value))
                value = self.envelope | {
                    key: "different" if key != "refresh_token" else ""
                }
                self.assertFalse(self.valid(value))

    def test_exact_shape_and_token_bounds(self):
        self.ready()
        for value in (
            None,
            [],
            {},
            {"refresh_token": "fabricated", "scope": self.envelope["scope"]},
            self.envelope | {"access_token": "fabricated"},
            self.envelope | {"client_secret": "fabricated"},
            self.envelope | {"refresh_token": "x" * 8193},
            self.envelope | {"refresh_token": "white space"},
            self.envelope | {"refresh_token": "control\n"},
            self.envelope | {"refresh_token": "unicode-ı"},
            {key: value for key, value in self.envelope.items() if key != "scope"},
        ):
            self.assertFalse(self.valid(value))
        with self.assertRaisesRegex(ValueError, "^Invalid candidate envelope\\.$"):
            build_envelope(
                owner_id=self.owner.pk,
                workspace_id=self.workspace.pk,
                receipt=self.row,
                refresh_token="",
            )

    def test_matching_envelope_is_advisory_and_never_returns_secret(self):
        self.ready()
        before = list(Attempt.objects.values())
        result = self.inspect()
        self.assertEqual(result.disposition, "matches_candidate")
        self.assertNotIn("fabricated-refresh", repr(result))
        self.assertNotIn("dpapi", repr(result))
        self._read.assert_called_once_with(self._write.call_args.args[0])
        self.assertEqual(list(Attempt.objects.values()), before)
        self.assertEqual(ConnectorIdentity.objects.get().state, "quarantined")
        self.assertEqual(self._post.call_count, 1)
        self.assertEqual(self._write.call_count, 1)

    def test_expired_handshake_does_not_expire_stored_candidate(self):
        self.ready()
        with patch.object(
            fixtures.candidate.timezone,
            "now",
            return_value=self.row.expires_at + timedelta(days=1),
        ):
            self.assertEqual(self.inspect().disposition, "matches_candidate")

    def test_disabled_gate_before_read(self):
        self.ready()
        with override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=False):
            with self.assertRaises(fixtures.backend.ConnectionUnavailable):
                self.inspect()
        self._read.assert_not_called()

    def test_wrong_session_and_unknown_attempt_before_read(self):
        self.ready()
        with self.assertRaises(IdentityConflict):
            self.inspect(session_key="another-session")
        with self.assertRaises(Attempt.DoesNotExist):
            self.inspect(attempt_id=uuid4())
        self._read.assert_not_called()

    def test_inactive_owner_denied_before_read(self):
        self.ready()
        self.owner.is_active = False
        self.owner.save(update_fields=["is_active"])
        with self.assertRaises(PermissionDenied):
            self.inspect()
        self._read.assert_not_called()

    def test_foreign_owner_and_workspace_denied_before_io(self):
        self.ready()
        other = get_user_model().objects.create_user(username="other-inspector")
        other_workspace = Workspace.objects.create(owner=other, name="Other")
        self._client.reset_mock()
        with self.assertRaises(Workspace.DoesNotExist):
            self.inspect(owner=other)
        with self.assertRaises(Workspace.DoesNotExist):
            self.inspect(workspace_id=other_workspace.pk)
        self._client.assert_not_called()
        self._read.assert_not_called()

    def test_caller_transaction_denied(self):
        self.ready()
        with transaction.atomic():
            with self.assertRaises(IdentityConflict):
                self.inspect()
        self._read.assert_not_called()

    def test_inconsistent_receipt_denied_before_io(self):
        self.ready()
        Attempt.objects.filter(pk=self.attempt_id).update(reason="storage_uncertain")
        with self.assertRaises(IdentityConflict):
            self.inspect()
        self._read.assert_not_called()

    def test_non_candidate_dispositions_never_read_or_promote_orphan(self):
        self.ready()
        for state, reason, disposition in (
            ("reserved", "", "pending"),
            ("exchanging", "", "reconciliation_required"),
            ("uncertain", "storage_uncertain", "reconciliation_required"),
            ("rejected", "callback_invalid", "rejected"),
        ):
            Attempt.objects.filter(pk=self.attempt_id).update(
                state=state, reason=reason
            )
            self.assertEqual(self.inspect().disposition, disposition)
            self.assertEqual(Attempt.objects.get().state, state)
        self._read.assert_not_called()

    def test_block_and_rotation_deny_before_read(self):
        self.ready()
        self.rotate()
        self.assertEqual(self.inspect().disposition, "scope_changed")
        self._read.assert_not_called()

    def test_legacy_presence_preserved(self):
        self.ready()
        self._token_path.return_value.exists.return_value = True
        self.assertEqual(self.inspect().disposition, "legacy_exists")
        self._read.assert_not_called()

    def test_changed_client_before_read(self):
        self.ready()
        self._client.return_value = self.client_value | {
            "client_id": "other.apps.googleusercontent.com"
        }
        self.assertEqual(self.inspect().disposition, "client_changed")
        self._read.assert_not_called()

    def test_missing_corrupt_or_failed_read_stays_unreadable(self):
        self.ready()
        for error in (
            FileNotFoundError("fabricated-secret"),
            ValueError("fabricated-secret"),
        ):
            self._read.side_effect = error
            result = self.inspect()
            self.assertEqual(result.disposition, "unreadable")
            self.assertNotIn("fabricated-secret", repr(result))
        self.assertEqual(Attempt.objects.get().state, "candidate")

    def test_other_attempt_envelope_rejected(self):
        self.ready()
        self._read.return_value = self.envelope | {"attempt_id": str(uuid4())}
        self.assertEqual(self.inspect().disposition, "invalid_envelope")

    def test_block_during_read_invalidates_match(self):
        self.ready()

        def read(_path):
            self.assertFalse(fixtures.connection.in_atomic_block)
            self.block()
            return self.envelope

        self._read.side_effect = read
        self.assertEqual(self.inspect().disposition, "scope_changed")

    def test_switch_off_during_read_invalidates_match(self):
        self.ready()
        with override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True):

            def read(_path):
                readback.settings.GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED = False
                return self.envelope

            self._read.side_effect = read
            self.assertEqual(self.inspect().disposition, "scope_changed")

    def test_receipt_changed_during_read_denies(self):
        self.ready()

        def read(_path):
            Attempt.objects.filter(pk=self.attempt_id).update(client_id_hash="b" * 64)
            return self.envelope

        self._read.side_effect = read
        with self.assertRaises(IdentityConflict):
            self.inspect()

    def test_legacy_appears_after_read_denies(self):
        self.ready()
        self._token_path.return_value.exists.side_effect = [False, True]
        self.assertEqual(self.inspect().disposition, "legacy_exists")

    def test_client_changes_after_read_denies(self):
        self.ready()
        self._client.side_effect = [
            self.client_value,
            self.client_value | {"client_id": "other.apps.googleusercontent.com"},
        ]
        self.assertEqual(self.inspect().disposition, "client_changed")

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_block_commits_during_read_and_invalidates_match(self):
        self.ready()
        entered, release = Event(), Event()

        def read(_path):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Readback race coordination failed")
            return self.envelope

        def threaded(call):
            close_old_connections()
            try:
                return call(get_user_model().objects.get(pk=self.owner.pk))
            finally:
                close_old_connections()

        self._read.side_effect = read
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(threaded, lambda owner: self.inspect(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                blocked = pool.submit(threaded, lambda owner: self.block(owner=owner))
                self.assertEqual(blocked.result(timeout=10).state, "blocked")
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).disposition, "scope_changed")
