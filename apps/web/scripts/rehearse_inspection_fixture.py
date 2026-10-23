"""Fresh Windows fabricated fixture only; never a preserved-candidate launcher.

Run with exactly one fixed scenario: match, client-changed, invalid-envelope,
or unreadable. No paths, credentials, account identifiers or callbacks accepted.
"""

import hashlib
import io
import json
import os
import secrets
import socket
import sys
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

SCENARIOS = {"match", "client-changed", "invalid-envelope", "unreadable"}
_STAGES = {
    "admission",
    "setup",
    "storage",
    "database",
    "seed",
    "exercise",
    "cleanup",
    "complete",
}
_DISPOSITIONS = {
    "none",
    "matches_candidate",
    "client_changed",
    "invalid_envelope",
    "unreadable",
    "legacy_exists",
}


def _parse_scenario(argv):
    if type(argv) is not list or len(argv) != 1 or type(argv[0]) is not str:
        raise ValueError("A single fixed fixture scenario is required.")
    if argv[0] not in SCENARIOS:
        raise ValueError("A single fixed fixture scenario is required.")
    return argv[0]


def _empty_report(scenario="none"):
    return {
        "passed": False,
        "scenario": scenario,
        "stage": "admission",
        "disposition": "none",
        "permit_state": "unknown",
        "history_preserved": False,
        "cleanup_complete": False,
        "private_storage_verified": False,
        "session_count": -1,
        "boundary_attempts": 0,
        "client_reads": 0,
        "candidate_reads": 0,
        "replay_refused": False,
    }


def _emit(report):
    expected = _empty_report()
    if type(report) is not dict or set(report) != set(expected):
        raise ValueError("Fixture report refused.")
    for key, default in expected.items():
        if type(report[key]) is not type(default):
            raise ValueError("Fixture report refused.")
    if (
        report["scenario"] not in SCENARIOS | {"none"}
        or report["stage"] not in _STAGES
        or report["disposition"] not in _DISPOSITIONS
        or report["permit_state"] not in {"unknown", "absent", "issued", "consumed"}
        or not -1 <= report["session_count"] <= 10000
        or any(
            not 0 <= report[key] <= 10000
            for key in ("boundary_attempts", "client_reads", "candidate_reads")
        )
    ):
        raise ValueError("Fixture report refused.")
    print(json.dumps(report, sort_keys=True))


def _exercise(scenario, forbidden):
    """Called only after fresh-process startup, with all native operations real."""
    from datetime import timedelta

    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.contrib.sessions.models import Session
    from django.core.management import call_command
    from django.db import connection, connections
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.test import override_settings
    from django.utils import timezone

    from growthtwin.modules.connections import backend
    from growthtwin.modules.connections import scoped_oauth_candidate as candidate
    from growthtwin.modules.connections.candidate_envelope import build_envelope
    from growthtwin.modules.connections.connector_identity import (
        register_google_test_identity,
    )
    from growthtwin.modules.connections.models import (
        CandidateInspectionPermit as Permit,
    )
    from growthtwin.modules.connections.models import (
        ScopedOAuthCandidateAttempt as Attempt,
    )
    from growthtwin.modules.workspaces.models import Workspace
    from scripts import inspection_fixture_files as files
    from scripts import rehearse_inspection_once as once

    if scenario not in SCENARIOS:
        raise ValueError("Fixture scenario refused.")
    report = _empty_report(scenario)
    home = None
    owned_files, owned_directories = [], []
    database_denials = [0]
    original_database_name = connection.settings_dict["NAME"]
    original_ensure = BaseDatabaseWrapper.ensure_connection
    original_context = once._CONTEXT
    try:
        report["stage"] = "storage"
        # create_home captures original LOCALAPPDATA before the environment shift.
        home = files.create_home()
        appdata = home / "appdata"
        storage_root = appdata / "GrowthTwinsecrets"
        owned_directories.append(appdata)
        files.make_private_directory(appdata)
        owned_directories.append(storage_root)
        files.make_private_directory(storage_root)
        database = home / "fixture.sqlite3"
        owned_files.append(database)  # Inventory precedes every possible write.
        if (
            database.exists()
            or database.is_symlink()
            or connection.connection is not None
        ):
            raise ValueError("Fresh fixture database required.")
        connection.settings_dict["NAME"] = str(database)
        settings.DATABASES["default"]["NAME"] = str(database)

        def exact_database(wrapper):
            if (
                wrapper.alias != "default"
                or wrapper.vendor != "sqlite"
                or wrapper.settings_dict["NAME"] != str(database)
            ):
                database_denials[0] += 1
                raise ValueError("Only the new fabricated database is eligible.")
            # Recheck local path shape on every DB access. Native ACL is checked
            # before initial creation and at stage boundaries, not per SQL query.
            files.no_reparse(home)
            if database.exists():
                files.no_reparse(database)
                if not database.is_file():
                    raise ValueError("Fixture database object changed.")
            return original_ensure(wrapper)

        with ExitStack() as stack:
            stack.enter_context(patch.dict(os.environ, {"LOCALAPPDATA": str(appdata)}))
            stack.enter_context(
                patch.object(BaseDatabaseWrapper, "ensure_connection", exact_database)
            )
            for name in ("_client", "_read", "_write", "_post"):
                forbidden.append(
                    stack.enter_context(
                        patch.object(
                            backend,
                            name,
                            side_effect=AssertionError("Fixture boundary forbidden"),
                        )
                    )
                )
            report["stage"] = "database"
            call_command(
                "migrate",
                interactive=False,
                verbosity=0,
                stdout=io.StringIO(),
                stderr=io.StringIO(),
            )
            files.assert_private(database)
            report["stage"] = "seed"
            owner = get_user_model().objects.create_user(
                username=once.FIXTURE_USERNAME, password=None
            )
            workspace = Workspace.objects.create(
                owner=owner, name=once.FIXTURE_WORKSPACE
            )
            identity = register_google_test_identity(
                owner=owner, workspace_id=workspace.pk, request_id=uuid4()
            )
            now = timezone.now()
            row = Attempt.objects.create(
                id=uuid4(),
                connection_id=identity.connection_id,
                generation=identity.generation,
                expected_revision=identity.revision,
                session_key_hash=candidate._session_key("fabricated-original-session"),
                client_id_hash=once.FIXTURE_CLIENT_HASH,
                state=Attempt.State.CANDIDATE,
                created_at=now,
                expires_at=now + timedelta(minutes=5),
            )
            stack.enter_context(
                override_settings(
                    DEBUG=False,
                    GOOGLE_ADS_LOCAL_OWNER_ID=str(owner.pk),
                    GOOGLE_ADS_LOCAL_WORKSPACE_ID=str(workspace.pk),
                    GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED=True,
                    GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED=True,
                    GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED=True,
                    GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED=True,
                    GOOGLE_ADS_LOCAL_OAUTH_ENABLED=True,
                )
            )
            client = storage_root / "google-ads-oauth-client.dpapi"
            candidate_file = candidate._candidate_path(row)
            marker = home / (
                "inspection-once-"
                + hashlib.sha256(str(row.pk).encode()).hexdigest()
                + ".json"
            )
            owned_files.extend([client, candidate_file, marker])
            if candidate_file.parent != storage_root or len(set(owned_files)) != len(
                owned_files
            ):
                raise ValueError("Fixture mapping changed.")
            client_value = {
                "project_id": "growthtwin-ads-test",
                "type": "web",
                "client_id": once.FIXTURE_CLIENT_ID,
                "client_secret": "fabricated-client-secret-only",
            }
            if scenario == "client-changed":
                client_value["client_id"] = (
                    "fabricated-changed.apps.googleusercontent.com"
                )
            files.encrypt_new(client, client_value)
            if scenario != "unreadable":
                envelope = build_envelope(
                    owner_id=owner.pk,
                    workspace_id=workspace.pk,
                    receipt=row,
                    refresh_token="fabricated-refresh-only",
                )
                if scenario == "invalid-envelope":
                    envelope["owner_id"] = "fabricated-wrong-owner"
                files.encrypt_new(candidate_file, envelope)
            for item in (home, appdata, storage_root, database, client):
                files.assert_private(item)
            if scenario != "unreadable":
                files.assert_private(candidate_file)
            report["private_storage_verified"] = True
            report["stage"] = "exercise"
            once._CONTEXT = once.Context(home, appdata, str(database))
            outcome = once.exercise_fixture_once()
            report.update(
                disposition=outcome.disposition,
                permit_state=outcome.permit_state,
                history_preserved=outcome.history_preserved,
                client_reads=outcome.client_reads,
                candidate_reads=outcome.candidate_reads,
            )
            before_replay = list(Permit.objects.values())
            try:
                once.exercise_fixture_once()
            except ValueError:
                report["replay_refused"] = (
                    list(Permit.objects.values()) == before_replay
                )
            report["session_count"] = Session.objects.count()
            expected = {
                "match": ("matches_candidate", 1),
                "client-changed": ("client_changed", 0),
                "invalid-envelope": ("invalid_envelope", 1),
                "unreadable": ("unreadable", 1),
            }[scenario]
            report["passed"] = (
                outcome.stage == "completed"
                and not outcome.cleanup_review
                and (outcome.disposition, outcome.candidate_reads) == expected
                and outcome.client_reads == 2
                and outcome.boundary_attempts == 0
                and outcome.permit_state == Permit.State.CONSUMED
                and outcome.history_preserved
                and report["session_count"] == 0
                and report["replay_refused"]
                and marker.is_file()
            )
            for item in (home, appdata, storage_root, database, client, marker):
                files.assert_private(item)
            if candidate_file.exists():
                files.assert_private(candidate_file)
            report["boundary_attempts"] = outcome.boundary_attempts
    except Exception:
        report["passed"] = False
    finally:
        once._CONTEXT = original_context
        try:
            connections.close_all()
            connection.settings_dict["NAME"] = original_database_name
            settings.DATABASES["default"]["NAME"] = original_database_name
        except Exception:
            report["passed"] = False
        if home is not None:
            try:
                report["cleanup_complete"] = files.cleanup(
                    home, owned_files, owned_directories
                )
            except Exception:
                report["cleanup_complete"] = False
        report["boundary_attempts"] += database_denials[0] + sum(
            g.call_count for g in forbidden
        )
        report["passed"] = (
            report["passed"]
            and report["cleanup_complete"]
            and report["private_storage_verified"]
            and report["boundary_attempts"] == 0
        )
        if report["passed"]:
            report["stage"] = "complete"
    return report


def main():
    report = _empty_report()
    try:
        scenario = _parse_scenario(sys.argv[1:])
    except ValueError:
        _emit(report)
        return 2
    report["scenario"] = scenario
    if os.name != "nt":
        _emit(report)
        return 2
    import django
    from django.apps import apps
    from django.conf import settings
    from django.db.backends.base.base import BaseDatabaseWrapper

    # Never reconfigure an existing app, test runner or operator DB connection.
    if settings.configured or apps.ready:
        _emit(report)
        return 2
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    with patch.dict(
        os.environ,
        {
            "DJANGO_SETTINGS_MODULE": "config.test_settings",
            "DJANGO_SECRET_KEY": secrets.token_urlsafe(48),
            "DATABASE_URL": "sqlite:///:memory:",
            "DJANGO_DEBUG": "false",
        },
    ):
        with ExitStack() as startup:
            forbidden = [
                startup.enter_context(
                    patch.object(
                        target,
                        name,
                        side_effect=AssertionError("Fixture network forbidden"),
                    )
                )
                for target, name in (
                    (socket, "create_connection"),
                    (socket.socket, "connect"),
                )
            ]
            report["stage"] = "setup"
            no_database = None
            try:
                with patch.object(
                    BaseDatabaseWrapper,
                    "ensure_connection",
                    side_effect=AssertionError("Startup database forbidden"),
                ) as no_database:
                    django.setup()
                if no_database.call_count or any(g.call_count for g in forbidden):
                    raise ValueError("Startup boundary attempted.")
                report = _exercise(scenario, forbidden)
            except Exception:
                report["passed"] = False
                report["boundary_attempts"] = sum(g.call_count for g in forbidden) + (
                    no_database.call_count if no_database is not None else 0
                )
    _emit(report)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
