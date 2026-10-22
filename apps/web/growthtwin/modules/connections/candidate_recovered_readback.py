"""Closed recovered readback adapter, validated with mocked storage only.

An advisory envelope match is not token validity, account access or activation.
No routes, refresh, provider or result persistence; consumed permits never retry.
"""

import secrets
from dataclasses import dataclass
from time import monotonic
from uuid import UUID

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables

from . import backend
from . import candidate_inspection_recovery as recovery
from . import candidate_inspection_storage as storage
from .candidate_envelope import validate_envelope
from .candidate_retirement import receipt_binding_digest
from .connector_identity import IdentityConflict, _uuid
from .models import CandidateInspectionPermit as Permit

LOCK_WAIT_SECONDS = 5
OBSERVATION_SECONDS = 60


@dataclass(frozen=True)
class RecoveredInspection:
    request_id: UUID
    attempt_id: UUID
    disposition: str


def _enabled():
    recovery._enabled()
    if any(
        getattr(settings, name, False) is not True
        for name in (
            "GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED",
            "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED",
            "GOOGLE_ADS_LOCAL_OAUTH_ENABLED",
        )
    ):
        raise PermissionDenied("Recovered inspection is disabled.")
    backend._enabled()


def _checked(values, *, issued=None, claimed=None, digest=None, deadline=None):
    _enabled()
    if deadline is not None and monotonic() >= deadline:
        raise IdentityConflict("Inspection observation exceeded its time budget.")
    with transaction.atomic():
        connector, _, row = recovery._scope(
            values["owner"],
            values["workspace_id"],
            values["connection_id"],
            values["attempt_id"],
        )
        permit = Permit.objects.select_for_update().get(pk=values["request_id"])
        recovery._bound(
            permit,
            values["owner"],
            values["workspace_id"],
            connector,
            row,
            recovery._session(values["session_key"]),
        )
        now = timezone.now()
        if not permit.created_at <= now < permit.expires_at:
            raise IdentityConflict("Inspection permission is outside its time window.")
        snapshot = recovery._snapshot(permit)
        current_digest = receipt_binding_digest(row)
        if claimed is None:
            if permit.state != Permit.State.ISSUED:
                raise IdentityConflict("Inspection permission was already consumed.")
        elif (
            snapshot != claimed
            or not permit.consumed_at <= now
            or permit.created_at != issued.created_at
            or permit.expires_at != issued.expires_at
            or not secrets.compare_digest(current_digest, digest)
        ):
            raise IdentityConflict("Inspection changed after its claim.")
        _enabled()
        if deadline is not None and monotonic() >= deadline:
            raise IdentityConflict("Inspection observation exceeded its time budget.")
        return snapshot, current_digest, row


def _locations(values, row):
    return storage._locations(
        owner_id=values["owner"].pk,
        workspace_id=values["workspace_id"],
        session_key=values["session_key"],
        receipt=row,
    )


def _unchanged_locations(values, row, locations):
    _enabled()
    if _locations(values, row) != locations:
        raise IdentityConflict("Inspection storage configuration changed.")


def _observe(locations, row):
    legacy = storage._legacy_present(locations)
    if type(legacy) is not bool:
        return "unreadable"
    if legacy:
        return "legacy_exists"
    client_key = storage._client_key(locations)
    if not recovery._hex(client_key):
        return "unreadable"
    return "" if client_key == row.client_id_hash else "client_changed"


@sensitive_variables()
def inspect_recovered_candidate(
    *, owner, workspace_id, connection_id, attempt_id, request_id, session_key
):
    _enabled()
    recovery._gate()
    for value in (connection_id, attempt_id, request_id):
        _uuid(value)
    values = dict(
        owner=owner,
        workspace_id=workspace_id,
        connection_id=connection_id,
        attempt_id=attempt_id,
        request_id=request_id,
        session_key=session_key,
    )
    # Bound same-process lock wait before claiming; no DB locks while waiting.
    if not backend._LOCK.acquire(timeout=LOCK_WAIT_SECONDS):
        raise IdentityConflict("Inspection storage is busy; permission not consumed.")
    try:
        _enabled()
        issued, digest, row = _checked(values)
        locations = _locations(values, row)  # Pure derivation/config checks only.
        claimed = recovery.consume_inspection_permit(**values)
        checks = dict(
            issued=issued,
            claimed=claimed,
            digest=digest,
            deadline=monotonic() + OBSERVATION_SECONDS,
        )
        _, _, row = _checked(values, **checks)
        disposition = "unreadable"
        try:
            _unchanged_locations(values, row, locations)
            disposition = _observe(locations, row)
            if not disposition:
                _checked(values, **checks)
                _unchanged_locations(values, row, locations)
                value = storage._read_bounded(locations.candidate)
                disposition = (
                    "matches_candidate"
                    if validate_envelope(
                        value, owner_id=owner.pk, workspace_id=workspace_id, receipt=row
                    )
                    else "invalid_envelope"
                )
                del value
        except Exception:
            disposition = "unreadable"
        # Never switch root or mapping for the final client/legacy observation.
        try:
            _unchanged_locations(values, row, locations)
            changed = _observe(locations, row)
            if changed:
                disposition = changed
        except Exception:
            disposition = "unreadable"
        _checked(values, **checks)
        _unchanged_locations(values, row, locations)
        if (
            monotonic() >= checks["deadline"]
            or not claimed.consumed_at <= timezone.now() < claimed.expires_at
        ):
            raise IdentityConflict("Inspection result is outside its time window.")
        return RecoveredInspection(request_id, attempt_id, disposition)
    finally:
        backend._LOCK.release()
