"""Owned metadata assessment only. Never resumes, reads or mutates a grant."""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from . import scoped_oauth_candidate as candidate
from .connector_identity import _uuid
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


@dataclass(frozen=True)
class RecoveryAssessment:
    snapshot: candidate.CandidateSnapshot
    disposition: str
    current_scope: bool
    session_matches: bool
    can_retry_exchange: bool = False
    can_activate: bool = False


@transaction.atomic
def assess_candidate(
    *, owner, workspace_id, connection_id, attempt_id, session_key=None
):
    _uuid(connection_id)
    _uuid(attempt_id)
    connector, current = candidate._locked(owner, workspace_id, connection_id)
    row = Attempt.objects.select_for_update().get(pk=attempt_id, connection=connector)
    snapshot = candidate._metadata(row)
    same_session = (
        session_key is not None
        and candidate._session_key(session_key) == row.session_key_hash
    )
    current_scope = (
        current.state == ConnectorIdentity.State.QUARANTINED
        and current.generation == row.generation
        and current.revision == row.expected_revision
    )
    # Uncertainty never disappears because a scope/session changed or time elapsed.
    disposition = {
        Attempt.State.EXCHANGING: "reconciliation_required",
        Attempt.State.UNCERTAIN: "reconciliation_required",
        Attempt.State.CANDIDATE: "inactive_candidate_review",
        Attempt.State.REJECTED: "rejected_history",
    }.get(row.state)
    if row.state == Attempt.State.RESERVED:
        disposition = (
            "callback_wait"
            if current_scope
            and same_session
            and row.created_at <= timezone.now() < row.expires_at
            else "restart_review"
        )
    return RecoveryAssessment(snapshot, disposition, current_scope, same_session)
