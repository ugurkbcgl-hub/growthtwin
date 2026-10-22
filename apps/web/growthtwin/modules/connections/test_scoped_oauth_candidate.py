"""Scoped TEST boundary: every client, transport and storage call is mocked."""

import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from threading import Event
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlsplit
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import TransactionTestCase, override_settings, skipUnlessDBFeature

from growthtwin.modules.workspaces.models import Workspace

from . import backend
from . import scoped_oauth_candidate as candidate
from .connector_identity import (
    IdentityConflict,
    block_identity,
    get_identity,
    register_google_test_identity,
    rotate_generation,
)
from .google_oauth import ADS_SCOPE, SCOPED_REDIRECT_URI, LocalAuthorizationStore
from .models import ScopedOAuthCandidateAttempt as Attempt


class CandidateFixture:
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="candidate-owner")
        self.workspace = Workspace.objects.create(owner=self.owner, name="Synthetic")
        self.identity = register_google_test_identity(
            owner=self.owner, workspace_id=self.workspace.pk, request_id=uuid4()
        )
        self.attempt_id = uuid4()
        self.session = "fabricated-session"
        self.client_value = {
            "client_id": "fabricated.apps.googleusercontent.com",
            "client_secret": "fabricated-secret",
        }
        self.token = {
            "token_type": "Bearer",
            "access_token": "fabricated-access",
            "refresh_token": "fabricated-refresh",
            "scope": ADS_SCOPE,
        }
        for name in ("_enabled", "_token_path", "_client", "_post", "_write", "_read"):
            mocked = patch.object(backend, name)
            setattr(self, name, mocked.start())
            self.addCleanup(mocked.stop)
        self._token_path.return_value.exists.return_value = False
        self._client.return_value = self.client_value
        self._post.return_value = json.dumps(self.token)
        store = patch.object(candidate, "_store", LocalAuthorizationStore())
        store.start()
        self.addCleanup(store.stop)
        environment = patch.dict(
            candidate.os.environ, {"LOCALAPPDATA": "fabricated-candidate-only"}
        )
        environment.start()
        self.addCleanup(environment.stop)

    def begin(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
            session_key=self.session,
        )
        return candidate.begin_candidate(**(values | changes))

    def prepare(self):
        start = self.begin()
        state = parse_qs(urlsplit(start.authorization_url).query)["state"][0]
        self.query = urlencode({"state": state, "code": "fabricated-code"})
        return start

    def consume(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            session_key=self.session,
            query=self.query,
        )
        return candidate.consume_candidate(**(values | changes))

    def read(self, **changes):
        values = dict(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            attempt_id=self.attempt_id,
            session_key=self.session,
        )
        return candidate.get_candidate(**(values | changes))

    def block(self, owner=None):
        return block_identity(
            owner=owner or self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )

    def rotate(self):
        return rotate_generation(
            owner=self.owner,
            workspace_id=self.workspace.pk,
            connection_id=self.identity.connection_id,
            request_id=uuid4(),
            expected_generation=self.identity.generation,
            expected_revision=self.identity.revision,
        )


@override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True)
class ScopedCandidateTests(CandidateFixture, TransactionTestCase):
    def test_disabled_adapter_never_loads_client_or_reserves_attempt(self):
        with override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=False):
            with self.assertRaises(backend.ConnectionUnavailable):
                self.begin()
        self._client.assert_not_called()
        self._post.assert_not_called()
        self.assertEqual(Attempt.objects.count(), 0)

    def test_existing_legacy_grant_is_preserved_before_client_or_exchange(self):
        self._token_path.return_value.exists.return_value = True
        with self.assertRaises(backend.ConnectionUnavailable):
            self.begin()
        self._client.assert_not_called()
        self._read.assert_not_called()
        self._post.assert_not_called()
        self._write.assert_not_called()

    def test_candidate_has_separate_envelope_and_does_not_activate_connection(self):
        start = self.prepare()
        self.assertNotIn("state=", repr(start))
        result = self.consume()
        self.assertEqual(result.state, "candidate")
        self._post.assert_called_once()
        endpoint, fields = self._post.call_args.args
        self.assertEqual(endpoint, "https://oauth2.googleapis.com/token")
        self.assertEqual(fields["redirect_uri"], SCOPED_REDIRECT_URI)
        self.assertEqual(fields["code"], "fabricated-code")
        self.assertIn("code_verifier", fields)
        path, envelope = self._write.call_args.args
        self.assertTrue(path.name.startswith("google-candidate-"))
        self.assertEqual(envelope["schema"], "google-test-candidate-v1")
        self.assertEqual(envelope["connection_id"], str(self.identity.connection_id))
        self.assertEqual(envelope["generation"], str(self.identity.generation))
        self.assertEqual(envelope["attempt_id"], str(self.attempt_id))
        self.assertNotIn("access_token", envelope)
        self.assertNotIn("client_secret", envelope)
        self.assertNotIn("fabricated-refresh", repr(result))
        self.assertEqual(
            get_identity(
                owner=self.owner,
                workspace_id=self.workspace.pk,
                connection_id=self.identity.connection_id,
            ),
            self.identity,
        )
        self._read.assert_not_called()

    def test_callback_replay_does_not_exchange_or_write_twice(self):
        self.prepare()
        first = self.consume()
        self.assertEqual(self.consume(query="ignored replay"), first)
        self._post.assert_called_once()
        self._write.assert_called_once()

    def test_begin_replay_does_not_extend_durable_lifetime(self):
        first = self.begin()
        self.assertEqual(self.begin().snapshot, first.snapshot)
        self.assertEqual(Attempt.objects.count(), 1)
        with self.assertRaises(IdentityConflict):
            self.begin(session_key="different-session")

    def test_wrong_state_or_session_cannot_exchange(self):
        self.prepare()
        with self.assertRaises(IdentityConflict):
            self.consume(session_key="different-session")
        self.assertEqual(self.read().state, "reserved")
        result = self.consume(query=urlencode({"state": "wrong", "code": "fabricated"}))
        self.assertEqual(result.state, "rejected")
        self._post.assert_not_called()
        self._write.assert_not_called()

    def test_expiry_before_exchange_never_loads_callback_client(self):
        start = self.prepare()
        self._client.reset_mock()
        with patch.object(
            candidate.timezone, "now", return_value=start.snapshot.expires_at
        ):
            result = self.consume()
        self.assertEqual((result.state, result.reason), ("rejected", "expired"))
        self._client.assert_not_called()
        self._post.assert_not_called()

    def test_generation_change_before_exchange_denies(self):
        self.prepare()
        self.rotate()
        self.assertEqual(self.consume().reason, "scope_changed")
        self._post.assert_not_called()
        self._write.assert_not_called()

    def test_block_during_exchange_prevents_candidate_write(self):
        self.prepare()

        def post(endpoint, fields):
            self.assertFalse(connection.in_atomic_block)
            self.assertEqual(Attempt.objects.get().state, "exchanging")
            self.block()
            return json.dumps(self.token)

        self._post.side_effect = post
        result = self.consume()
        self.assertEqual((result.state, result.reason), ("uncertain", "scope_changed"))
        self._write.assert_not_called()
        self._post.assert_called_once()

    def test_rotation_during_exchange_prevents_candidate_write(self):
        self.prepare()

        def post(endpoint, fields):
            self.rotate()
            return json.dumps(self.token)

        self._post.side_effect = post
        self.assertEqual(self.consume().state, "uncertain")
        self._write.assert_not_called()

    def test_expiry_during_exchange_prevents_candidate_write(self):
        start = self.prepare()
        clock = [Attempt.objects.get().created_at]

        def post(endpoint, fields):
            clock[0] = start.snapshot.expires_at
            return json.dumps(self.token)

        self._post.side_effect = post
        with patch.object(candidate.timezone, "now", side_effect=lambda: clock[0]):
            result = self.consume()
        self.assertEqual(result.reason, "expired")
        self._write.assert_not_called()

    def test_client_change_after_start_is_rejected_before_exchange(self):
        self.prepare()
        self._client.return_value = {
            **self.client_value,
            "client_id": "changed.apps.googleusercontent.com",
        }
        self.assertEqual(self.consume().state, "rejected")
        self._post.assert_not_called()

    def test_new_legacy_file_after_exchange_is_not_overwritten(self):
        self.prepare()

        def post(endpoint, fields):
            self._token_path.return_value.exists.return_value = True
            return json.dumps(self.token)

        self._post.side_effect = post
        self.assertEqual(self.consume().reason, "legacy_exists")
        self._write.assert_not_called()

    def test_transport_uncertainty_is_sanitized_and_not_retried_or_revoked(self):
        self.prepare()
        self._post.side_effect = backend.ConnectionUnavailable(
            "fabricated-private-detail"
        )
        result = self.consume()
        self.assertEqual(result.state, "uncertain")
        self.assertNotIn("fabricated-private-detail", repr(result))
        self.assertEqual(self.consume(), result)
        self._post.assert_called_once()
        self._write.assert_not_called()
        newer = self.rotate()
        with self.assertRaises(IdentityConflict):
            self.begin(
                attempt_id=uuid4(),
                expected_generation=newer.generation,
                expected_revision=newer.revision,
            )

    def test_invalid_provider_scope_never_writes(self):
        self.prepare()
        self._post.return_value = json.dumps(
            {**self.token, "scope": ADS_SCOPE + " openid"}
        )
        self.assertEqual(self.consume().state, "uncertain")
        self._write.assert_not_called()
        self._post.assert_called_once()

    def test_failed_write_leaves_uncertainty_and_no_automatic_revoke(self):
        self.prepare()
        self._write.side_effect = OSError("fabricated-private-storage-detail")
        result = self.consume()
        self.assertEqual(
            (result.state, result.reason), ("uncertain", "storage_uncertain")
        )
        self.assertEqual(self.consume(), result)
        self._post.assert_called_once()
        self._write.assert_called_once()

    def test_persistence_failure_after_possible_file_write_remains_inert(self):
        self.prepare()
        original = candidate._finish

        def finish(row, state, reason):
            if state == "candidate":
                raise IntegrityError("fabricated commit failure")
            return original(row, state, reason)

        with patch.object(candidate, "_finish", side_effect=finish):
            result = self.consume()
        self.assertEqual(result.state, "uncertain")
        self._write.assert_called_once()
        self.assertEqual(self.consume(), result)
        self._post.assert_called_once()

    def test_foreign_owner_wrong_session_and_caller_transaction_are_denied(self):
        self.prepare()
        other = get_user_model().objects.create_user(username="foreign-candidate-owner")
        with self.assertRaises(Workspace.DoesNotExist):
            self.consume(owner=other)
        with self.assertRaises(IdentityConflict):
            self.read(session_key="another-session")
        with transaction.atomic():
            with self.assertRaises(IdentityConflict):
                self.consume()
        self._post.assert_not_called()

    def test_terminal_metadata_read_does_not_load_credentials(self):
        self.prepare()
        self.consume()
        self._client.reset_mock()
        with override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=False):
            self.assertEqual(self.read().state, "candidate")
        self._client.assert_not_called()
        self._read.assert_not_called()

    def test_changed_immutable_binding_in_exchange_is_not_saved(self):
        self.prepare()

        def post(endpoint, fields):
            Attempt.objects.filter(pk=self.attempt_id).update(session_key_hash="f" * 64)
            return json.dumps(self.token)

        self._post.side_effect = post
        self.assertEqual(self.consume().state, "uncertain")
        self._write.assert_not_called()


@override_settings(GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True)
class ScopedCandidateRaceTests(CandidateFixture, TransactionTestCase):
    def threaded(self, call):
        close_old_connections()
        try:
            return call(get_user_model().objects.get(pk=self.owner.pk))
        finally:
            close_old_connections()

    @skipUnlessDBFeature("has_select_for_update")
    def test_parallel_callbacks_without_process_lock_reserve_one_exchange(self):
        self.prepare()
        entered, release = Event(), Event()

        def post(endpoint, fields):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Candidate race coordination failed")
            return json.dumps(self.token)

        self._post.side_effect = post
        with (
            patch.object(backend, "_LOCK", nullcontext()),
            ThreadPoolExecutor(max_workers=2) as pool,
        ):
            first = pool.submit(self.threaded, lambda owner: self.consume(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                second = pool.submit(
                    self.threaded, lambda owner: self.consume(owner=owner)
                )
                self.assertEqual(second.result(timeout=10).state, "exchanging")
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).state, "candidate")
        self._post.assert_called_once()
        self._write.assert_called_once()

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_block_prevents_candidate_storage(self):
        self.prepare()
        entered, release = Event(), Event()

        def post(endpoint, fields):
            entered.set()
            if not release.wait(10):
                raise TimeoutError("Candidate race coordination failed")
            return json.dumps(self.token)

        self._post.side_effect = post
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(self.threaded, lambda owner: self.consume(owner=owner))
            try:
                self.assertTrue(entered.wait(10))
                blocked = pool.submit(
                    self.threaded, lambda owner: self.block(owner=owner)
                )
                self.assertEqual(blocked.result(timeout=10).state, "blocked")
            finally:
                release.set()
            self.assertEqual(first.result(timeout=10).state, "uncertain")
        self._write.assert_not_called()
