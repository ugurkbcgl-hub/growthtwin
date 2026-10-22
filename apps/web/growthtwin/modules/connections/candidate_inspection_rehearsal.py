"""Closed in-memory inspection rehearsal; no file, backend or provider adapter.

Only the fixed fabricated client receipt is eligible. Results are synthetic and
never inspection evidence for a real candidate. A failed claim is not renewable.
"""

import hashlib
import secrets
from dataclasses import dataclass
from uuid import UUID

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables

from . import candidate_inspection_recovery as recovery
from .candidate_envelope import build_envelope, validate_envelope
from .candidate_retirement import receipt_binding_digest
from .connector_identity import IdentityConflict, _uuid
from .models import CandidateInspectionPermit as Permit

FIXTURE_CLIENT_HASH = hashlib.sha256(
    b"fabricated-inspection-client.apps.googleusercontent.com"
).hexdigest()
SCENARIOS = frozenset(
    {"match", "legacy_exists", "client_changed", "invalid_envelope", "unreadable"}
)


@dataclass(frozen=True)
class RehearsalResult:
    request_id: UUID
    attempt_id: UUID
    disposition: str


@dataclass(frozen=True)
class _Address:
    owner_id: str
    workspace_id: str
    connection_id: UUID
    attempt_id: UUID
    generation: UUID


class _FixtureProbe:
    """Fixed in-memory behavior only; callers cannot supply a reader or path."""

    def __init__(self, scenario, address, row):
        self.scenario = scenario
        self.address = address
        self.envelope = build_envelope(
            owner_id=address.owner_id,
            workspace_id=address.workspace_id,
            receipt=row,
            refresh_token="fabricated-inspection-only",
        )

    def legacy_present(self):
        return self.scenario == "legacy_exists"

    def client_hash(self):
        return "0" * 64 if self.scenario == "client_changed" else FIXTURE_CLIENT_HASH

    def read(self, address):
        if address != self.address or self.scenario == "unreadable":
            raise ValueError("Synthetic read unavailable.")
        if self.scenario == "invalid_envelope":
            return self.envelope | {"scope": "fabricated-invalid"}
        return self.envelope.copy()


def _enabled():
    recovery._enabled()
    if getattr(settings, "GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED", False) is not True:
        raise PermissionDenied("Inspection rehearsal is disabled.")


def _gate():
    _enabled()
    recovery._gate()


def _checked(
    *,
    owner,
    workspace_id,
    connection_id,
    attempt_id,
    request_id,
    session_key,
    issued=None,
    claimed=None,
    digest=None,
):
    _enabled()
    with transaction.atomic():
        connector, _, row = recovery._scope(
            owner, workspace_id, connection_id, attempt_id
        )
        permit = Permit.objects.select_for_update().get(pk=request_id)
        recovery._bound(
            permit, owner, workspace_id, connector, row, recovery._session(session_key)
        )
        # This cannot consume or simulate success for an actual configured client.
        if row.client_id_hash != FIXTURE_CLIENT_HASH:
            raise IdentityConflict("Only the fixed fabricated client is eligible.")
        now = timezone.now()
        if not permit.created_at <= now < permit.expires_at:
            raise IdentityConflict("Rehearsal permission is outside its time window.")
        snapshot = recovery._snapshot(permit)
        current_digest = receipt_binding_digest(row)
        if claimed is None:
            if permit.state != Permit.State.ISSUED:
                raise IdentityConflict("Rehearsal permission was already consumed.")
        elif (
            snapshot != claimed
            or not permit.consumed_at <= now
            or permit.created_at != issued.created_at
            or permit.expires_at != issued.expires_at
            or not secrets.compare_digest(current_digest, digest)
        ):
            raise IdentityConflict("Rehearsal scope changed after its claim.")
        _enabled()
        return snapshot, current_digest, row


def _storage_disposition(probe):
    legacy = probe.legacy_present()
    if type(legacy) is not bool:
        return "unreadable"
    if legacy:
        return "legacy_exists"
    client_hash = probe.client_hash()
    if not recovery._hex(client_hash):
        return "unreadable"
    return "" if client_hash == FIXTURE_CLIENT_HASH else "client_changed"


@sensitive_variables()
def rehearse_inspection(
    *,
    owner,
    workspace_id,
    connection_id,
    attempt_id,
    request_id,
    session_key,
    scenario="match",
):
    _gate()
    for value in (connection_id, attempt_id, request_id):
        _uuid(value)
    if type(scenario) is not str or scenario not in SCENARIOS:
        raise ValueError("A fixed synthetic scenario is required.")
    values = dict(
        owner=owner,
        workspace_id=workspace_id,
        connection_id=connection_id,
        attempt_id=attempt_id,
        request_id=request_id,
        session_key=session_key,
    )
    issued, digest, _ = _checked(**values)
    # Never accept caller-supplied snapshots. Claim commits before any probe call.
    claimed = recovery.consume_inspection_permit(**values)
    checks = values | dict(issued=issued, claimed=claimed, digest=digest)
    _, _, row = _checked(**checks)
    address = _Address(
        str(owner.pk), str(workspace_id), connection_id, attempt_id, row.generation
    )
    probe = _FixtureProbe(scenario, address, row)
    disposition = "unreadable"
    try:
        disposition = _storage_disposition(probe)
        if not disposition:
            _checked(**checks)
            value = probe.read(address)
            disposition = (
                "synthetic_match"
                if validate_envelope(
                    value, owner_id=owner.pk, workspace_id=workspace_id, receipt=row
                )
                else "invalid_envelope"
            )
    except Exception:
        # No exception text or fabricated envelope may escape to the result.
        disposition = "unreadable"
    # Check client/legacy again even for negative or failed reads, outside DB locks.
    try:
        changed = _storage_disposition(probe)
        if changed:
            disposition = changed
    except Exception:
        disposition = "unreadable"
    _checked(**checks)
    return RehearsalResult(request_id, attempt_id, disposition)
