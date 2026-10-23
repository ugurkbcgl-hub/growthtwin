"""Fixture-only single-attempt coordinator; no protected-candidate entry point.

No callback, path, envelope, session or receipt snapshot is accepted from callers.
_CONTEXT defaults to None; only isolated tests currently supply fabricated scope.
There is no CLI, fixture creator, Windows DPAPI execution proof or real-data mode.
"""

import hashlib
import json
import os
import socket
import stat
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid5

from django.views.decorators.debug import sensitive_variables

FIXTURE_USERNAME = "inspection-once-fixture-owner"
FIXTURE_WORKSPACE = "Inspection once fabricated workspace"
FIXTURE_CLIENT_ID = "inspection-once-fixture.apps.googleusercontent.com"
FIXTURE_CLIENT_HASH = hashlib.sha256(FIXTURE_CLIENT_ID.encode()).hexdigest()
_ORIGINAL_APPDATA = os.environ.get("LOCALAPPDATA")


@dataclass(frozen=True, repr=False)
class Context:
    home: Path
    appdata: Path
    database_name: object


@dataclass(frozen=True)
class Outcome:
    stage: str
    disposition: str
    permit_state: str
    history_preserved: bool
    cleanup_review: bool
    boundary_attempts: int
    client_reads: int
    candidate_reads: int


_CONTEXT = None


def _no_reparse(path):
    for item in (path, *path.parents):
        info = item.stat(follow_symlinks=False)
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
        ):
            raise ValueError("Fixture path refused.")


def _fixture_scope():
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.contrib.sessions.models import Session
    from django.db import connection, transaction

    from growthtwin.modules.connections import candidate_inspection_recovery as recovery
    from growthtwin.modules.connections.candidate_retirement import (
        receipt_binding_digest,
    )
    from growthtwin.modules.connections.models import (
        CandidateInspectionPermit as Permit,
    )
    from growthtwin.modules.connections.models import ConnectorIdentity
    from growthtwin.modules.connections.models import (
        ScopedOAuthCandidateAttempt as Attempt,
    )
    from growthtwin.modules.workspaces.models import Workspace

    context = _CONTEXT
    if (
        type(context) is not Context
        or connection.in_atomic_block
        or settings.GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED is not True
        or connection.settings_dict["NAME"] != context.database_name
        or not context.home.is_absolute()
        or not context.home.name.startswith("gwt-inspection-once-fixture-")
        or context.appdata != context.home / "appdata"
        or os.environ.get("LOCALAPPDATA") != str(context.appdata)
        or (_ORIGINAL_APPDATA and context.appdata == Path(_ORIGINAL_APPDATA))
    ):
        raise ValueError("Only a separately created fabricated fixture is eligible.")
    for path in (context.home, context.appdata):
        _no_reparse(path)
        if not path.is_dir():
            raise ValueError("Fixture directory unavailable.")
    owner = get_user_model().objects.get(username=FIXTURE_USERNAME, is_active=True)
    workspace = Workspace.objects.get(owner=owner, name=FIXTURE_WORKSPACE)
    if (
        owner.has_usable_password()
        or (str(owner.pk), str(workspace.pk))
        != (
            str(settings.GOOGLE_ADS_LOCAL_OWNER_ID),
            str(settings.GOOGLE_ADS_LOCAL_WORKSPACE_ID),
        )
        or Session.objects.exists()
    ):
        raise ValueError("Fixture owner or session changed.")
    identity = ConnectorIdentity.objects.get(
        workspace=workspace, provider="google_ads_test"
    )
    row = Attempt.objects.get(connection=identity, state=Attempt.State.CANDIDATE)
    with transaction.atomic():
        connector, current, row = recovery._scope(
            owner, workspace.pk, identity.pk, row.pk
        )
        if row.client_id_hash != FIXTURE_CLIENT_HASH:
            raise ValueError("Protected or unknown client is never a fixture.")
        digest = receipt_binding_digest(row)
    if Permit.objects.filter(attempt=row).exists():
        raise ValueError("Fixture permission already exists; never retry.")
    return context, owner, workspace, connector, current, row, digest


def _history():
    from django.contrib.auth import get_user_model

    from growthtwin.modules.connections.models import (
        ConnectorGeneration,
        ConnectorIdentity,
        ScopedOAuthCandidateAttempt,
    )
    from growthtwin.modules.workspaces.models import Workspace

    value = [
        list(model.objects.order_by("pk").values())
        for model in (
            get_user_model(),
            Workspace,
            ConnectorIdentity,
            ConnectorGeneration,
            ScopedOAuthCandidateAttempt,
        )
    ]
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode()
    ).digest()


class _DecoderGuard:
    @sensitive_variables()
    def __init__(self, *, owner, workspace, row, session_key, counters):
        self.owner, self.workspace, self.row = owner, workspace, row
        self.session_key, self.counters = session_key, counters
        self.stack = ExitStack()

    @sensitive_variables()
    def __enter__(self):
        from growthtwin.modules.connections import backend
        from growthtwin.modules.connections import (
            candidate_inspection_storage as storage,
        )

        owner, workspace, row = self.owner, self.workspace, self.row
        session_key, counters = self.session_key, self.counters
        locations = storage._locations(
            owner_id=owner.pk,
            workspace_id=workspace.pk,
            session_key=session_key,
            receipt=row,
        )
        root = _CONTEXT.appdata / "GrowthTwinsecrets"
        if locations.root != root or any(
            path.parent != root
            for path in (locations.client, locations.candidate, locations.legacy)
        ):
            raise ValueError("Fixture storage mapping changed.")
        original_reader = backend._powershell
        original_path = backend._token_path

        @sensitive_variables()
        def token_path(binding):
            if binding != (str(owner.pk), str(workspace.pk), session_key):
                counters["forbidden"] += 1
                raise ValueError("Unexpected fixture mapping.")
            result = original_path(binding)
            if result != locations.legacy:
                counters["forbidden"] += 1
                raise ValueError("Fixture mapping drifted.")
            return result

        @sensitive_variables()
        def bounded(script, payload):
            if (
                script != storage._BOUNDED_READ_SCRIPT
                or type(payload) is not dict
                or set(payload) != {"path"}
                or type(payload["path"]) is not str
            ):
                counters["forbidden"] += 1
                raise ValueError("Only the fixed bounded decoder is permitted.")
            kind = (
                "client"
                if payload["path"] == str(locations.client)
                else "candidate"
                if payload["path"] == str(locations.candidate)
                else None
            )
            if kind is None:
                counters["forbidden"] += 1
                raise ValueError("Unexpected fixture decoder path.")
            counters[kind] += 1  # Failed attempts also consume the fixed quota.
            if counters[kind] > (2 if kind == "client" else 1):
                counters["forbidden"] += 1
                raise ValueError("Fixture decoder budget exhausted.")
            return original_reader(script, payload)

        try:
            self.stack.enter_context(patch.object(backend, "_powershell", bounded))
            self.stack.enter_context(patch.object(backend, "_token_path", token_path))
        except BaseException:
            self.stack.close()
            raise
        return self

    @sensitive_variables()
    def __exit__(self, exc_type, exc, traceback):
        return self.stack.__exit__(exc_type, exc, traceback)


_decoder_guard = _DecoderGuard


@sensitive_variables()
def exercise_fixture_once():
    from django.contrib.sessions.models import Session

    from growthtwin.modules.connections import backend
    from growthtwin.modules.connections import candidate_inspection_recovery as recovery
    from growthtwin.modules.connections import candidate_recovered_readback as reader
    from growthtwin.modules.connections.models import (
        CandidateInspectionPermit as Permit,
    )
    from scripts.prepare_recovered_inspection import _owned_synthetic_session

    context, owner, workspace, connector, current, row, digest = _fixture_scope()
    before = _history()
    marker = context.home / (
        "inspection-once-" + hashlib.sha256(str(row.pk).encode()).hexdigest() + ".json"
    )
    request_id = uuid5(
        NAMESPACE_URL, "growthtwin:inspection-once-fixture:" + str(row.pk)
    )
    with marker.open("x", encoding="utf-8") as output:
        json.dump(
            {"version": 1, "request_id": str(request_id), "receipt": digest}, output
        )

    stage, disposition = "started", "none"
    counters = {"client": 0, "candidate": 0, "forbidden": 0}
    guards = []
    try:
        with ExitStack() as stack:
            for target, names in (
                (backend, ("_client", "_read", "_write", "_post")),
                (socket, ("create_connection",)),
                (socket.socket, ("connect",)),
            ):
                for name in names:
                    guards.append(
                        stack.enter_context(
                            patch.object(
                                target,
                                name,
                                side_effect=AssertionError(
                                    "Fixture boundary forbidden"
                                ),
                            )
                        )
                    )
            stage = "bootstrap"
            binding = _owned_synthetic_session(owner=owner, workspace_id=workspace.pk)
            with binding as (authenticated, key):
                with _decoder_guard(
                    owner=authenticated,
                    workspace=workspace,
                    row=row,
                    session_key=key,
                    counters=counters,
                ):
                    binding.validate()
                    stage = "issue"
                    recovery.issue_inspection_permit(
                        owner=authenticated,
                        workspace_id=workspace.pk,
                        connection_id=connector.pk,
                        attempt_id=row.pk,
                        request_id=request_id,
                        expected_generation=current.generation,
                        expected_revision=current.revision,
                        expected_receipt_key=digest,
                        session_key=key,
                        recovery_confirmation=True,
                    )
                    binding.validate()
                    stage = "reader"
                    result = reader.inspect_recovered_candidate(
                        owner=authenticated,
                        workspace_id=workspace.pk,
                        connection_id=connector.pk,
                        attempt_id=row.pk,
                        request_id=request_id,
                        session_key=key,
                    )
                    binding.validate()
                    if (
                        type(result) is not reader.RecoveredInspection
                        or result.request_id != request_id
                        or result.attempt_id != row.pk
                        or result.disposition
                        not in {
                            "matches_candidate",
                            "invalid_envelope",
                            "legacy_exists",
                            "client_changed",
                            "unreadable",
                        }
                    ):
                        raise ValueError("Unknown fixture result.")
                    disposition = result.disposition
                    stage = "validated"
            if counters["forbidden"] or any(guard.call_count for guard in guards):
                raise ValueError("Forbidden fixture boundary attempted.")
        stage = "completed"
    except Exception:
        # No exception text, traceback, raw binding or decoded dictionary escapes.
        pass
    boundary_count = counters["forbidden"] + sum(g.call_count for g in guards)
    permit_state, cleanup_review, preserved = "unknown", True, False
    try:
        permits = list(Permit.objects.filter(attempt=row).values_list("id", "state"))
        if permits == []:
            permit_state = "absent"
        elif len(permits) == 1 and permits[0][0] == request_id:
            permit_state = permits[0][1]
        cleanup_review = Session.objects.exists()
        preserved = _history() == before
        if not preserved or cleanup_review or boundary_count:
            stage = "review_required"
        if stage == "completed" and permit_state != Permit.State.CONSUMED:
            stage = "review_required"
    except Exception:
        stage = "review_required"
    return Outcome(
        stage,
        disposition,
        permit_state,
        preserved,
        cleanup_review,
        boundary_count,
        counters["client"],
        counters["candidate"],
    )
