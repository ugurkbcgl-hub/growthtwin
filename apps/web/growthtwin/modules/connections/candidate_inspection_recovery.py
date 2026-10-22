"""Closed, metadata-only recovery permit protocol. No reader or provider hook.

CONSUMED records an irreversible claim, not an inspection result or I/O permission
for existing readers. Actual readback integration and post-read checks remain gated.
"""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, transaction
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.debug import sensitive_variables

from . import scoped_oauth_candidate as candidate
from .candidate_retirement import receipt_binding_digest
from .connector_identity import IdentityConflict, _revision, _uuid
from .models import CandidateInspectionPermit as Permit
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt

LIFETIME = timedelta(minutes=5)


@dataclass(frozen=True)
class PermitSnapshot:
    request_id: UUID
    connection_id: UUID
    attempt_id: UUID
    generation: UUID
    expected_revision: int
    state: str
    created_at: datetime
    expires_at: datetime
    consumed_at: datetime | None


def _enabled():
    if (
        getattr(settings, "GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED", False)
        is not True
    ):
        raise PermissionDenied("Inspection recovery is disabled.")


def _gate():
    _enabled()
    if connection.in_atomic_block:
        raise IdentityConflict("Recovery requires no caller transaction.")


@sensitive_variables()
def _session(session_key):
    if type(session_key) is not str or not session_key or len(session_key) > 256:
        raise ValueError("A current server session is required.")
    return salted_hmac(
        "growthtwin:inspection-recovery-session", session_key, algorithm="sha256"
    ).hexdigest()


def _scope(owner, workspace_id, connection_id, attempt_id):
    # Shared ordering: workspace -> connector -> attempt -> permit.
    connector, current = candidate._locked(owner, workspace_id, connection_id)
    row = Attempt.objects.select_for_update().get(pk=attempt_id, connection=connector)
    candidate._metadata(row)
    if (
        current.state != ConnectorIdentity.State.QUARANTINED
        or row.state != Attempt.State.CANDIDATE
        or current.generation != row.generation
        or current.revision != row.expected_revision
        or Attempt.objects.filter(connection=connector)
        .exclude(pk=row.pk)
        .exclude(state=Attempt.State.REJECTED)
        .exists()
    ):
        raise IdentityConflict("Only a current quarantined candidate is eligible.")
    return connector, current, row


def _hex(value):
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _bound(permit, owner, workspace_id, connector, row, session_hash):
    if (
        permit.owner_id != owner.pk
        or str(permit.workspace_id) != str(workspace_id)
        or permit.connection_id != connector.pk
        or permit.attempt_id != row.pk
        or permit.generation != row.generation
        or permit.expected_revision != row.expected_revision
        or not _hex(permit.session_key_hash)
        or not secrets.compare_digest(permit.session_key_hash, session_hash)
        or not _hex(permit.receipt_key)
        or not secrets.compare_digest(permit.receipt_key, receipt_binding_digest(row))
        or timezone.is_naive(permit.created_at)
        or timezone.is_naive(permit.expires_at)
        or permit.expires_at - permit.created_at != LIFETIME
        or permit.created_at > timezone.now()
        or permit.state not in Permit.State.values
        or (permit.state == Permit.State.ISSUED and permit.consumed_at is not None)
        or (
            permit.state == Permit.State.CONSUMED
            and (
                permit.consumed_at is None
                or timezone.is_naive(permit.consumed_at)
                or not permit.created_at <= permit.consumed_at < permit.expires_at
            )
        )
    ):
        raise IdentityConflict("Recovery permit binding is inconsistent.")


def _snapshot(permit):
    return PermitSnapshot(
        permit.pk,
        permit.connection_id,
        permit.attempt_id,
        permit.generation,
        permit.expected_revision,
        permit.state,
        permit.created_at,
        permit.expires_at,
        permit.consumed_at,
    )


@sensitive_variables()
def issue_inspection_permit(
    *,
    owner,
    workspace_id,
    connection_id,
    attempt_id,
    request_id,
    expected_generation,
    expected_revision,
    expected_receipt_key,
    session_key,
    recovery_confirmation=False,
):
    _gate()
    for value in (connection_id, attempt_id, request_id, expected_generation):
        _uuid(value)
    _revision(expected_revision)
    if recovery_confirmation is not True or not _hex(expected_receipt_key):
        raise ValueError("Explicit scope-bound recovery confirmation is required.")
    session_hash = _session(session_key)
    with transaction.atomic():
        connector, current, row = _scope(owner, workspace_id, connection_id, attempt_id)
        if (
            current.generation != expected_generation
            or current.revision != expected_revision
            or not secrets.compare_digest(
                expected_receipt_key, receipt_binding_digest(row)
            )
        ):
            raise IdentityConflict("Candidate changed before recovery permission.")
        permit = Permit.objects.select_for_update().filter(pk=request_id).first()
        if permit:
            _bound(permit, owner, workspace_id, connector, row, session_hash)
            return _snapshot(permit)
        if Permit.objects.filter(attempt=row).exists():
            raise IdentityConflict(
                "Existing permission requires review; never replace it."
            )
        _enabled()
        now = timezone.now()
        try:
            with transaction.atomic():
                permit = Permit.objects.create(
                    id=request_id,
                    owner=owner,
                    workspace_id=connector.workspace_id,
                    connection=connector,
                    attempt=row,
                    generation=current.generation,
                    expected_revision=current.revision,
                    receipt_key=expected_receipt_key,
                    session_key_hash=session_hash,
                    created_at=now,
                    expires_at=now + LIFETIME,
                )
        except IntegrityError:
            raise IdentityConflict("Recovery permission conflicts.") from None
        return _snapshot(permit)


@sensitive_variables()
def consume_inspection_permit(
    *, owner, workspace_id, connection_id, attempt_id, request_id, session_key
):
    _gate()
    for value in (connection_id, attempt_id, request_id):
        _uuid(value)
    session_hash = _session(session_key)
    with transaction.atomic():
        connector, _, row = _scope(owner, workspace_id, connection_id, attempt_id)
        permit = Permit.objects.select_for_update().get(pk=request_id)
        _bound(permit, owner, workspace_id, connector, row, session_hash)
        _enabled()
        now = timezone.now()
        if permit.state != Permit.State.ISSUED or now >= permit.expires_at:
            raise IdentityConflict("Permission expired or was already consumed.")
        changed = Permit.objects.filter(
            pk=request_id, state=Permit.State.ISSUED, expires_at__gt=now
        ).update(state=Permit.State.CONSUMED, consumed_at=now)
        if changed != 1:
            raise IdentityConflict("Permission changed; no automatic retry.")
        permit.refresh_from_db()
        return _snapshot(permit)
