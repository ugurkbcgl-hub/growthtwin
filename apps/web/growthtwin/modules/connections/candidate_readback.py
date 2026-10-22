"""Default-off, unwired advisory inspection; never an active grant reader.

Only a committed CANDIDATE receipt permits reading its exact derived file.
An orphan cannot promote EXCHANGING/UNCERTAIN. No provider calls or mutations.
"""

from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.views.decorators.debug import sensitive_variables

from . import backend
from . import scoped_oauth_candidate as candidate
from .candidate_envelope import validate_envelope
from .connector_identity import IdentityConflict, _uuid
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


@dataclass(frozen=True)
class Inspection:
    snapshot: candidate.CandidateSnapshot
    disposition: str


def _frozen(row):
    return (
        row.generation,
        row.expected_revision,
        row.client_id_hash,
        row.session_key_hash,
        row.created_at,
        row.expires_at,
        row.state,
        row.reason,
    )


def _disposition(current, row):
    if (
        getattr(settings, "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED", False) is not True
        or current.state != ConnectorIdentity.State.QUARANTINED
        or current.generation != row.generation
        or current.revision != row.expected_revision
    ):
        return "scope_changed"
    return {
        Attempt.State.RESERVED: "pending",
        Attempt.State.EXCHANGING: "reconciliation_required",
        Attempt.State.UNCERTAIN: "reconciliation_required",
        Attempt.State.REJECTED: "rejected",
        Attempt.State.CANDIDATE: "",
    }[row.state]


@sensitive_variables()
def inspect_candidate(*, owner, workspace_id, connection_id, attempt_id, session_key):
    candidate._gate()
    _uuid(connection_id)
    _uuid(attempt_id)
    session_hash = candidate._session_key(session_key)
    with backend._LOCK:
        with transaction.atomic():
            connector, current = candidate._locked(owner, workspace_id, connection_id)
            row = Attempt.objects.select_for_update().get(
                pk=attempt_id, connection=connector
            )
            snapshot = candidate._metadata(row)
            if row.session_key_hash != session_hash:
                raise IdentityConflict("Candidate session does not match.")
            disposition = _disposition(current, row)
            if disposition:
                return Inspection(snapshot, disposition)
            frozen = _frozen(row)
            path = candidate._candidate_path(row)
        # Bounded local I/O outside DB locks. Never inspect legacy contents.
        disposition = "unreadable"
        try:
            binding = candidate._legacy_binding(owner, workspace_id, session_key)
            if backend._token_path(binding).exists():
                disposition = "legacy_exists"
            elif candidate._client_key(backend.load_client_id()) != row.client_id_hash:
                disposition = "client_changed"
            else:
                value = backend._read(path)
                disposition = (
                    "matches_candidate"
                    if validate_envelope(
                        value, owner_id=owner.pk, workspace_id=workspace_id, receipt=row
                    )
                    else "invalid_envelope"
                )
        except Exception:
            # Missing, unreadable or malformed storage is never proof of absence.
            disposition = "unreadable"
        with transaction.atomic():
            connector, current = candidate._locked(owner, workspace_id, connection_id)
            latest = Attempt.objects.select_for_update().get(
                pk=attempt_id, connection=connector
            )
            snapshot = candidate._metadata(latest)
            if _frozen(latest) != frozen:
                raise IdentityConflict("Candidate changed during inspection.")
            changed = _disposition(current, latest)
            if changed:
                return Inspection(snapshot, changed)
            if disposition == "matches_candidate":
                try:
                    if backend._token_path(binding).exists():
                        disposition = "legacy_exists"
                    elif (
                        candidate._client_key(backend.load_client_id())
                        != latest.client_id_hash
                    ):
                        disposition = "client_changed"
                except Exception:
                    disposition = "unreadable"
            return Inspection(snapshot, disposition)
