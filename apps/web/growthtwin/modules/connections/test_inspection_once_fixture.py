"""One-shot fabricated inspection uses the real session, claim and JSON codec."""

import hashlib
import inspect
import json
import os
import socket
import tempfile
from dataclasses import FrozenInstanceError, fields
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import connection
from django.test import TransactionTestCase, override_settings
from django.utils import timezone
from django.views.debug import SafeExceptionReporterFilter

from growthtwin.modules.workspaces.models import Workspace
from scripts import rehearse_inspection_once as once

from . import backend
from . import candidate_inspection_recovery as recovery
from . import candidate_inspection_storage as storage
from . import scoped_oauth_candidate as candidate
from .candidate_envelope import build_envelope
from .connector_identity import register_google_test_identity
from .models import CandidateInspectionPermit as Permit
from .models import ConnectorGeneration, ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


@override_settings(
    DEBUG=False,
    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
    GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED=True,
    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True,
    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
    GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED=True,
)
class InspectionOnceFixtureTests(TransactionTestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="gwt-inspection-once-fixture-"))
        self.parent = self.home.parent.resolve()
        self.home_resolved = self.home.resolve()
        self.appdata = self.home / "appdata"
        self.appdata.mkdir()
        self.addCleanup(self.clean_owned_directory)
        self.owner = get_user_model().objects.create_user(
            username=once.FIXTURE_USERNAME, password=None
        )
        self.workspace = Workspace.objects.create(
            owner=self.owner, name=once.FIXTURE_WORKSPACE
        )
        identity = register_google_test_identity(
            owner=self.owner, workspace_id=self.workspace.pk, request_id=uuid4()
        )
        now = timezone.now()
        self.row = Attempt.objects.create(
            pk=uuid4(),
            connection_id=identity.connection_id,
            generation=identity.generation,
            expected_revision=identity.revision,
            session_key_hash=candidate._session_key("fabricated-original-session"),
            client_id_hash=once.FIXTURE_CLIENT_HASH,
            state=Attempt.State.CANDIDATE,
            created_at=now,
            expires_at=now + timedelta(minutes=5),
        )
        self.marker = self.home / (
            "inspection-once-"
            + hashlib.sha256(str(self.row.pk).encode()).hexdigest()
            + ".json"
        )
        self.envelope = build_envelope(
            owner_id=self.owner.pk,
            workspace_id=self.workspace.pk,
            receipt=self.row,
            refresh_token="fabricated-refresh-only",
        )
        self.client = {
            "project_id": "growthtwin-ads-test",
            "type": "web",
            "client_id": once.FIXTURE_CLIENT_ID,
            "client_secret": "fabricated-client-secret-only",
        }
        self.before = self.history()
        self.decoder_calls = []
        for guard in (
            override_settings(
                GOOGLE_ADS_LOCAL_OWNER_ID=str(self.owner.pk),
                GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(self.workspace.pk),
            ),
            patch.dict(os.environ, {"LOCALAPPDATA": str(self.appdata)}),
            patch.object(
                once,
                "_CONTEXT",
                once.Context(self.home, self.appdata, connection.settings_dict["NAME"]),
            ),
            patch.object(backend, "_enabled", return_value=None),
            patch.object(backend, "_powershell", side_effect=self.decode),
            patch.object(storage, "_legacy_present", return_value=False),
        ):
            guard.start() if hasattr(guard, "start") else guard.enable()
            self.addCleanup(guard.stop if hasattr(guard, "stop") else guard.disable)

    def clean_owned_directory(self):
        self.assertEqual(self.home.resolve(), self.home_resolved)
        self.assertEqual(self.home.parent.resolve(), self.parent)
        self.assertEqual(self.appdata.parent, self.home)
        # Remove only the predetermined exclusive marker; never recurse.
        if self.marker.exists():
            self.assertEqual(self.marker.parent.resolve(), self.home_resolved)
            self.assertTrue(self.marker.is_file())
            self.assertFalse(self.marker.is_symlink())
            self.marker.unlink()
        self.appdata.rmdir()
        self.home.rmdir()

    def history(self):
        return tuple(
            list(model.objects.order_by("pk").values())
            for model in (
                get_user_model(),
                Workspace,
                ConnectorIdentity,
                ConnectorGeneration,
                Attempt,
            )
        )

    def decode(self, script, values):
        self.assertEqual(script, storage._BOUNDED_READ_SCRIPT)
        self.assertEqual(set(values), {"path"})
        path = Path(values["path"])
        self.assertEqual(path.parent, self.appdata / "GrowthTwinsecrets")
        self.decoder_calls.append(path.name)
        if path.name == "google-ads-oauth-client.dpapi":
            return json.dumps(self.client)
        self.assertEqual(path, candidate._candidate_path(self.row))
        self.assertEqual(Permit.objects.get().state, Permit.State.CONSUMED)
        return json.dumps(self.envelope)

    def assert_preserved(self):
        self.assertEqual(self.history(), self.before)
        self.assertFalse(Session.objects.exists())

    def test_closed_entrypoint_has_no_caller_paths_callbacks_or_arguments(self):
        self.assertEqual(
            list(inspect.signature(once.exercise_fixture_once).parameters), []
        )

    def test_direct_decoder_guard_failure_masks_session_in_exception_reporter(self):
        session_key = "fabricated-guard-report-session-only"
        report_filter = SafeExceptionReporterFilter()
        with patch.object(
            storage, "_locations", side_effect=ValueError("Fabricated mapping failure")
        ):
            try:
                with once._decoder_guard(
                    owner=self.owner,
                    workspace=self.workspace,
                    row=self.row,
                    session_key=session_key,
                    counters={"client": 0, "candidate": 0, "forbidden": 0},
                ):
                    self.fail("Fabricated mapping failure must refuse entry")
            except ValueError as error:
                found = False
                traceback = error.__traceback__
                while traceback is not None:
                    frame = traceback.tb_frame
                    if (
                        frame.f_globals.get("__name__") == once.__name__
                        and frame.f_code.co_name == "__enter__"
                    ):
                        self.assertEqual(frame.f_locals["session_key"], session_key)
                        filtered = dict(
                            report_filter.get_traceback_frame_variables(None, frame)
                        )
                        self.assertEqual(
                            filtered["session_key"], report_filter.cleansed_substitute
                        )
                        self.assertEqual(
                            filtered["self"], report_filter.cleansed_substitute
                        )
                        self.assertNotIn(session_key, repr(filtered))
                        found = True
                    traceback = traceback.tb_next
                self.assertTrue(found, "The real guard entry frame must be inspected")
            else:
                self.fail("The fabricated failure must reach the exception reporter")
        self.assertFalse(self.marker.exists())
        self.assertFalse(Permit.objects.exists())
        self.assertEqual(self.decoder_calls, [])
        self.assert_preserved()

    def test_real_session_claim_and_codec_match_once_without_changing_history(self):
        outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.disposition, "matches_candidate")
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assertTrue(outcome.history_preserved)
        self.assertFalse(outcome.cleanup_review)
        self.assertEqual(outcome.boundary_attempts, 0)
        self.assertEqual((outcome.client_reads, outcome.candidate_reads), (2, 1))
        self.assertEqual(len(self.decoder_calls), 3)
        self.assertEqual(Permit.objects.count(), 1)
        self.assertIsNotNone(Permit.objects.get().consumed_at)
        self.assert_preserved()
        self.assertEqual(
            {field.name for field in fields(outcome)},
            {
                "stage",
                "disposition",
                "permit_state",
                "history_preserved",
                "cleanup_review",
                "boundary_attempts",
                "client_reads",
                "candidate_reads",
            },
        )
        with self.assertRaises(FrozenInstanceError):
            outcome.disposition = "changed"
        permit = list(Permit.objects.values())
        with self.assertRaises(ValueError):
            once.exercise_fixture_once()
        self.assertEqual(list(Permit.objects.values()), permit)
        self.assertEqual(len(self.decoder_calls), 3)
        self.assert_preserved()

    def test_changed_client_consumes_permission_without_candidate_decode(self):
        self.client["client_id"] = (
            "fabricated-different-client.apps.googleusercontent.com"
        )
        outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.disposition, "client_changed")
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assertEqual((outcome.client_reads, outcome.candidate_reads), (2, 0))
        self.assertEqual(len(self.decoder_calls), 2)
        self.assert_preserved()

    def test_invalid_envelope_is_terminal_after_real_permission_claim(self):
        self.envelope["owner_id"] = "fabricated-wrong-owner"
        outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.disposition, "invalid_envelope")
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assertEqual(outcome.candidate_reads, 1)
        with self.assertRaises(ValueError):
            once.exercise_fixture_once()
        self.assertEqual(len(self.decoder_calls), 3)
        self.assert_preserved()

    def test_candidate_codec_rejects_duplicate_json_keys_and_never_decodes_again(self):
        original = self.decode

        def duplicate(script, values):
            value = original(script, values)
            if Path(values["path"]).name.startswith("google-candidate-"):
                return '{"refresh_token":"fabricated","refresh_token":"duplicate"}'
            return value

        with patch.object(backend, "_powershell", side_effect=duplicate):
            outcome = once.exercise_fixture_once()
            with self.assertRaises(ValueError):
                once.exercise_fixture_once()
        self.assertEqual(outcome.disposition, "unreadable")
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assertEqual(outcome.candidate_reads, 1)
        self.assertEqual(len(self.decoder_calls), 3)
        self.assert_preserved()

    def test_preclaim_failure_retains_marker_and_never_automatically_retries(self):
        with patch.object(recovery, "issue_inspection_permit", side_effect=ValueError):
            first = once.exercise_fixture_once()
        self.assertTrue(self.marker.exists())
        with self.assertRaises(FileExistsError):
            once.exercise_fixture_once()
        self.assertNotEqual(first.disposition, "matches_candidate")
        self.assertFalse(Permit.objects.exists())
        self.assertEqual(self.decoder_calls, [])
        self.assert_preserved()

    def test_issue_commit_then_failure_leaves_issued_terminal_without_decoder(self):
        original_issue = recovery.issue_inspection_permit

        def committed_then_failed(**values):
            original_issue(**values)
            self.assertEqual(Permit.objects.get().state, Permit.State.ISSUED)
            raise ValueError("Fabricated post-commit issuance failure")

        with patch.object(
            recovery, "issue_inspection_permit", side_effect=committed_then_failed
        ):
            outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.stage, "issue")
        self.assertEqual(outcome.permit_state, Permit.State.ISSUED)
        self.assertIsNone(Permit.objects.get().consumed_at)
        self.assertTrue(self.marker.exists())
        marker = self.marker.read_bytes()
        permit = list(Permit.objects.values())
        with self.assertRaises(ValueError):
            once.exercise_fixture_once()
        self.assertEqual(self.marker.read_bytes(), marker)
        self.assertEqual(list(Permit.objects.values()), permit)
        self.assertEqual(self.decoder_calls, [])
        self.assert_preserved()

    def test_postconsume_session_drift_retains_changed_session_for_cleanup_review(self):
        original_decode = self.decode
        client_reads = 0

        def drift_after_final_observation(script, values):
            nonlocal client_reads
            value = original_decode(script, values)
            if Path(values["path"]).name == "google-ads-oauth-client.dpapi":
                client_reads += 1
                if client_reads == 2:
                    self.assertEqual(Permit.objects.get().state, Permit.State.CONSUMED)
                    minted = Session.objects.get()
                    minted.expire_date += timedelta(seconds=1)
                    minted.save(update_fields=["expire_date"])
            return value

        with patch.object(
            backend, "_powershell", side_effect=drift_after_final_observation
        ):
            outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.stage, "review_required")
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assertTrue(outcome.cleanup_review)
        self.assertTrue(outcome.history_preserved)
        self.assertEqual(self.history(), self.before)
        self.assertEqual(Session.objects.count(), 1)
        self.assertTrue(self.marker.exists())
        session = list(Session.objects.values())
        permit = list(Permit.objects.values())
        with self.assertRaises(ValueError):
            once.exercise_fixture_once()
        self.assertEqual(list(Session.objects.values()), session)
        self.assertEqual(list(Permit.objects.values()), permit)
        self.assertEqual(len(self.decoder_calls), 3)

    def test_missing_owned_context_refuses_before_claim_or_decoder(self):
        with patch.object(once, "_CONTEXT", None):
            with self.assertRaises(ValueError):
                once.exercise_fixture_once()
        self.assertFalse(Permit.objects.exists())
        self.assertEqual(self.decoder_calls, [])
        self.assert_preserved()

    def test_postclaim_decoder_failure_consumes_and_does_not_retry(self):
        original = self.decode

        def failed(script, values):
            value = original(script, values)
            if Path(values["path"]).name.startswith("google-candidate-"):
                raise OSError("fabricated decoder failure")
            return value

        with patch.object(backend, "_powershell", side_effect=failed):
            outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.disposition, "unreadable")
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assertEqual((outcome.client_reads, outcome.candidate_reads), (2, 1))
        with self.assertRaises(ValueError):
            once.exercise_fixture_once()
        self.assertEqual(len(self.decoder_calls), 3)
        self.assert_preserved()

    def test_swallowed_provider_and_socket_attempts_still_require_review(self):
        original = self.decode

        def forbidden(script, values):
            value = original(script, values)
            if Path(values["path"]).name.startswith("google-candidate-"):
                for operation in (
                    lambda: backend._post("fabricated", {}),
                    lambda: socket.create_connection(("fabricated.invalid", 443)),
                ):
                    try:
                        operation()
                    except AssertionError:
                        pass
            return value

        with patch.object(backend, "_powershell", side_effect=forbidden):
            outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.stage, "review_required")
        self.assertEqual(outcome.boundary_attempts, 2)
        self.assertEqual(outcome.permit_state, Permit.State.CONSUMED)
        self.assert_preserved()

    def test_swallowed_second_candidate_decoder_attempt_never_reaches_decoder(self):
        original = self.decode

        def repeated(script, values):
            value = original(script, values)
            if Path(values["path"]).name.startswith("google-candidate-"):
                try:
                    backend._powershell(script, values)
                except ValueError:
                    pass
            return value

        with patch.object(backend, "_powershell", side_effect=repeated):
            outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.stage, "review_required")
        self.assertEqual(outcome.boundary_attempts, 1)
        self.assertEqual(outcome.candidate_reads, 2)
        self.assertEqual(len(self.decoder_calls), 3)
        self.assert_preserved()

    def test_wrong_database_context_refuses_before_marker_or_session(self):
        with (
            patch.object(
                once, "_CONTEXT", once.Context(self.home, self.appdata, "unowned-db")
            ),
            self.assertRaises(ValueError),
        ):
            once.exercise_fixture_once()
        self.assertFalse(self.marker.exists())
        self.assertFalse(Permit.objects.exists())
        self.assertEqual(self.decoder_calls, [])
        self.assert_preserved()

    def test_unrecognized_client_receipt_refuses_without_touching_decoder(self):
        Attempt.objects.filter(pk=self.row.pk).update(client_id_hash="0" * 64)
        expected = self.history()
        with self.assertRaises(ValueError):
            once.exercise_fixture_once()
        self.assertFalse(self.marker.exists())
        self.assertFalse(Permit.objects.exists())
        self.assertFalse(Session.objects.exists())
        self.assertEqual(self.decoder_calls, [])
        self.assertEqual(self.history(), expected)

    def test_environment_mismatch_refuses_before_marker_or_session(self):
        with patch.dict(os.environ, {"LOCALAPPDATA": str(self.home)}):
            with self.assertRaises(ValueError):
                once.exercise_fixture_once()
        self.assertFalse(self.marker.exists())
        self.assertFalse(Permit.objects.exists())
        self.assertEqual(self.decoder_calls, [])
        self.assert_preserved()

    def test_decoder_guard_refuses_changed_script_or_unbound_path(self):
        original = self.decode

        def wrong_inputs(script, values):
            value = original(script, values)
            if Path(values["path"]).name.startswith("google-candidate-"):
                for changed_script, changed_payload in (
                    ("fabricated-unapproved-script", values),
                    (script, {"path": str(self.home / "unbound.dpapi")}),
                ):
                    try:
                        backend._powershell(changed_script, changed_payload)
                    except ValueError:
                        pass
            return value

        with patch.object(backend, "_powershell", side_effect=wrong_inputs):
            outcome = once.exercise_fixture_once()
        self.assertEqual(outcome.stage, "review_required")
        self.assertEqual(outcome.boundary_attempts, 2)
        self.assertEqual((outcome.client_reads, outcome.candidate_reads), (2, 1))
        self.assertEqual(len(self.decoder_calls), 3)
        self.assert_preserved()
