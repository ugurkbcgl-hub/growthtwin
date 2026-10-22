"""Default-off Google TEST candidate boundary. NOT grant adoption.

Separate closed scoped endpoints call this adapter; validation uses mocked
transport/client/encrypted storage. Legacy routes and token path stay unchanged.
No candidate activation exists; readback is advisory. Uncertainty never auto-retries.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

from django.conf import settings
from django.db import IntegrityError, connection, transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.debug import sensitive_variables

from . import backend
from .candidate_envelope import build_envelope
from .connector_identity import (
    IdentityConflict,
    _revision,
    _snapshot,
    _uuid,
    _workspace,
)
from .google_oauth import (
    ADS_SCOPE,
    SCOPED_REDIRECT_URI,
    AuthorizationRejected,
    LocalAuthorizationStore,
)
from .models import ConnectorGeneration, ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt

LIFETIME = timedelta(minutes=5)
_store = LocalAuthorizationStore()
REASONS = {
    "",
    "scope_changed",
    "expired",
    "legacy_exists",
    "callback_invalid",
    "configuration",
    "exchange_uncertain",
    "storage_uncertain",
    "retired_before_exchange",
}


@dataclass(frozen=True)
class CandidateSnapshot:
    attempt_id: UUID
    connection_id: UUID
    generation: UUID
    state: str
    reason: str
    expires_at: datetime


@dataclass(frozen=True, repr=False)
class CandidateStart:
    snapshot: CandidateSnapshot
    authorization_url: str


def _gate():
    if getattr(settings, "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED", False) is not True:
        raise backend.ConnectionUnavailable("Scoped TEST candidates are disabled.")
    if connection.in_atomic_block:
        raise IdentityConflict("Candidate exchange requires no caller transaction.")
    backend._enabled()


def _session_key(session_key):
    if not isinstance(session_key, str) or not session_key or len(session_key) > 256:
        raise IdentityConflict("A server session binding is required.")
    return salted_hmac(
        "growthtwin:scoped-candidate-session", session_key, algorithm="sha256"
    ).hexdigest()


def _client_key(client_id):
    if (
        not isinstance(client_id, str)
        or not client_id.endswith(".apps.googleusercontent.com")
        or len(client_id) > 256
        or any(c.isspace() for c in client_id)
    ):
        raise backend.ConnectionUnavailable("Invalid TEST client configuration.")
    return hashlib.sha256(client_id.encode()).hexdigest()


def _locked(owner, workspace_id, connection_id):
    workspace = _workspace(owner, workspace_id, lock=True)
    row = ConnectorIdentity.objects.select_for_update().get(
        pk=connection_id, workspace=workspace
    )
    return row, _snapshot(row)


def _metadata(row):
    _uuid(row.pk)
    _uuid(row.generation)
    _revision(row.expected_revision)
    if (
        row.state not in Attempt.State.values
        or row.reason not in REASONS
        or timezone.is_naive(row.created_at)
        or timezone.is_naive(row.expires_at)
        or row.expires_at - row.created_at != LIFETIME
        or any(
            len(value) != 64 or any(c not in "0123456789abcdef" for c in value)
            for value in (row.session_key_hash, row.client_id_hash)
        )
    ):
        raise IdentityConflict("Candidate metadata is inconsistent.")
    if (
        row.state
        in (Attempt.State.RESERVED, Attempt.State.EXCHANGING, Attempt.State.CANDIDATE)
    ) != (row.reason == ""):
        raise IdentityConflict("Candidate outcome metadata is inconsistent.")
    if not ConnectorGeneration.objects.filter(
        pk=row.generation, connection=row.connection, ordinal=row.expected_revision + 1
    ).exists():
        raise IdentityConflict("Candidate generation is inconsistent.")
    if row.reason == "retired_before_exchange":
        _uuid(row.retirement_request_id)
        _uuid(row.retired_generation)
        if (
            row.state != Attempt.State.REJECTED
            or not ConnectorGeneration.objects.filter(
                pk=row.retired_generation,
                request_id=row.retirement_request_id,
                connection_id=row.connection_id,
                from_generation=row.generation,
                from_revision=row.expected_revision,
                ordinal=row.expected_revision + 2,
            ).exists()
        ):
            raise IdentityConflict("Candidate retirement receipt is inconsistent.")
    elif row.retirement_request_id is not None or row.retired_generation is not None:
        raise IdentityConflict("Unexpected retirement metadata.")
    return CandidateSnapshot(
        row.pk, row.connection_id, row.generation, row.state, row.reason, row.expires_at
    )


def _scope_reason(current, row):
    if (
        getattr(settings, "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED", False) is not True
        or current.state != ConnectorIdentity.State.QUARANTINED
        or current.generation != row.generation
        or current.revision != row.expected_revision
    ):
        return "scope_changed"
    now = timezone.now()
    if now < row.created_at or now >= row.expires_at:
        return "expired"
    return ""


def _oauth_binding(owner, workspace_id, row):
    key = salted_hmac(
        "growthtwin:scoped-candidate-handshake",
        str(row.pk)
        + ":"
        + str(row.connection_id)
        + ":"
        + str(row.generation)
        + ":"
        + str(row.expected_revision)
        + ":"
        + row.session_key_hash,
        algorithm="sha256",
    ).hexdigest()
    return (str(owner.pk), str(workspace_id), key)


def _legacy_binding(owner, workspace_id, session_key):
    return (str(owner.pk), str(workspace_id), session_key)


def _finish(row, state, reason):
    row.state, row.reason = state, reason
    row.save(update_fields=["state", "reason"])
    return _metadata(row)


@sensitive_variables()
def begin_candidate(
    *,
    owner,
    workspace_id,
    connection_id,
    attempt_id,
    expected_generation,
    expected_revision,
    session_key,
):
    _gate()
    for value in (connection_id, attempt_id, expected_generation):
        _uuid(value)
    _revision(expected_revision)
    session_hash = _session_key(session_key)
    with backend._LOCK, transaction.atomic():
        connector, current = _locked(owner, workspace_id, connection_id)
        if (
            current.state != ConnectorIdentity.State.QUARANTINED
            or current.generation != expected_generation
            or current.revision != expected_revision
        ):
            raise IdentityConflict("Connector scope changed.")
        row = Attempt.objects.select_for_update().filter(pk=attempt_id).first()
        if row:
            _metadata(row)
            if (
                row.connection_id != connector.pk
                or row.generation != expected_generation
                or row.expected_revision != expected_revision
                or row.session_key_hash != session_hash
                or row.state != Attempt.State.RESERVED
                or _scope_reason(current, row)
            ):
                raise IdentityConflict("Candidate start does not match.")
        elif (
            Attempt.objects.filter(connection=connector)
            .exclude(state=Attempt.State.REJECTED)
            .exists()
        ):
            raise IdentityConflict("Resolve the existing candidate attempt first.")
        if backend._token_path(
            _legacy_binding(owner, workspace_id, session_key)
        ).exists():
            raise backend.ConnectionUnavailable("Existing local grant is preserved.")
        client_id = backend.load_client_id()
        client_key = _client_key(client_id)
        if row and row.client_id_hash != client_key:
            raise IdentityConflict("TEST client changed.")
        if row is None:
            now = timezone.now()
            try:
                with transaction.atomic():
                    row = Attempt.objects.create(
                        id=attempt_id,
                        connection=connector,
                        generation=expected_generation,
                        expected_revision=expected_revision,
                        session_key_hash=session_hash,
                        client_id_hash=client_key,
                        created_at=now,
                        expires_at=now + LIFETIME,
                    )
            except IntegrityError:
                raise IdentityConflict("A candidate receipt already exists.") from None
        if _scope_reason(current, row):
            raise IdentityConflict("Candidate start expired.")
        # Separate process-local store; legacy routes' handshake is untouched.
        url = _store.begin(
            client_id=client_id,
            binding=_oauth_binding(owner, workspace_id, row),
            redirect_uri=SCOPED_REDIRECT_URI,
        )
        return CandidateStart(_metadata(row), url)


@transaction.atomic
def get_candidate(*, owner, workspace_id, connection_id, attempt_id, session_key):
    _uuid(connection_id)
    _uuid(attempt_id)
    connector, _ = _locked(owner, workspace_id, connection_id)
    row = Attempt.objects.select_for_update().get(pk=attempt_id, connection=connector)
    if row.session_key_hash != _session_key(session_key):
        raise IdentityConflict("Candidate session does not match.")
    return _metadata(row)


def _candidate_path(row):
    # Different basename and schema: existing backend readers never consume it.
    key = hashlib.sha256(
        (
            str(row.connection_id) + ":" + str(row.generation) + ":" + str(row.pk)
        ).encode()
    ).hexdigest()
    return (
        Path(os.environ["LOCALAPPDATA"])
        / "GrowthTwinsecrets"
        / ("google-candidate-" + key + ".dpapi")
    )


def _valid_token(token):
    return (
        isinstance(token, dict)
        and isinstance(token.get("token_type"), str)
        and token["token_type"].lower() == "bearer"
        and all(
            isinstance(token.get(key), str) and token[key]
            for key in ("access_token", "refresh_token")
        )
        and isinstance(token.get("scope"), str)
        and set(token["scope"].split()) == {ADS_SCOPE}
    )


@sensitive_variables()
def consume_candidate(
    *, owner, workspace_id, connection_id, attempt_id, session_key, query
):
    _gate()
    _uuid(connection_id)
    _uuid(attempt_id)
    session_hash = _session_key(session_key)
    with backend._LOCK:
        with transaction.atomic():
            connector, current = _locked(owner, workspace_id, connection_id)
            row = Attempt.objects.select_for_update().get(
                pk=attempt_id, connection=connector
            )
            expected = _metadata(row)
            if row.session_key_hash != session_hash:
                raise IdentityConflict("Candidate session does not match.")
            if row.state != Attempt.State.RESERVED:
                return expected
            reason = _scope_reason(current, row)
            if reason:
                return _finish(row, Attempt.State.REJECTED, reason)
            if backend._token_path(
                _legacy_binding(owner, workspace_id, session_key)
            ).exists():
                return _finish(row, Attempt.State.REJECTED, "legacy_exists")
            try:
                code = _store.consume(
                    binding=_oauth_binding(owner, workspace_id, row), query=query
                )
                client = backend._client()
                if _client_key(
                    client["client_id"]
                ) != row.client_id_hash or _scope_reason(current, row):
                    raise AuthorizationRejected("Candidate configuration changed.")
            except (
                AuthorizationRejected,
                backend.ConnectionUnavailable,
                KeyError,
                TypeError,
            ):
                return _finish(row, Attempt.State.REJECTED, "callback_invalid")
            row.state = Attempt.State.EXCHANGING
            row.save(update_fields=["state"])
            frozen = (
                row.generation,
                row.expected_revision,
                row.client_id_hash,
                row.session_key_hash,
                row.created_at,
                row.expires_at,
            )
        stage = "exchange_uncertain"
        try:
            token = json.loads(
                backend._post(
                    "https://oauth2.googleapis.com/token",
                    {
                        "client_id": client["client_id"],
                        "client_secret": client["client_secret"],
                        "code": code.code,
                        "code_verifier": code.verifier,
                        "redirect_uri": SCOPED_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    },
                )
            )
            if not _valid_token(token):
                raise ValueError("Invalid token shape")
            with transaction.atomic():
                connector, current = _locked(owner, workspace_id, connection_id)
                row = Attempt.objects.select_for_update().get(
                    pk=attempt_id, connection=connector
                )
                _metadata(row)
                if row.state != Attempt.State.EXCHANGING or frozen != (
                    row.generation,
                    row.expected_revision,
                    row.client_id_hash,
                    row.session_key_hash,
                    row.created_at,
                    row.expires_at,
                ):
                    raise IdentityConflict("Candidate changed during exchange.")
                reason = _scope_reason(current, row)
                if (
                    reason
                    or backend._token_path(
                        _legacy_binding(owner, workspace_id, session_key)
                    ).exists()
                ):
                    return _finish(
                        row, Attempt.State.UNCERTAIN, reason or "legacy_exists"
                    )
                stage = "storage_uncertain"
                backend._write(
                    _candidate_path(row),
                    build_envelope(
                        owner_id=owner.pk,
                        workspace_id=workspace_id,
                        receipt=row,
                        refresh_token=token["refresh_token"],
                    ),
                )
                reason = _scope_reason(current, row)
                return (
                    _finish(row, Attempt.State.UNCERTAIN, reason)
                    if reason
                    else _finish(row, Attempt.State.CANDIDATE, "")
                )
        except Exception:
            # Never automatically revoke: it could affect another grant for the
            # same Google client. Keep uncertainty for explicit reconciliation.
            try:
                with transaction.atomic():
                    connector, _ = _locked(owner, workspace_id, connection_id)
                    row = Attempt.objects.select_for_update().get(
                        pk=attempt_id, connection=connector
                    )
                    _metadata(row)
                    if row.state == Attempt.State.EXCHANGING:
                        return _finish(row, Attempt.State.UNCERTAIN, stage)
                    return _metadata(row)
            except Exception:
                raise backend.ConnectionUnavailable(
                    "Candidate outcome is unknown; do not retry exchange."
                ) from None
