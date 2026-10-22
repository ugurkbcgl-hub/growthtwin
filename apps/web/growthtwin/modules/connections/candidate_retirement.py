"""Default-off reserved-only retirement. No I/O or provider action."""

import hashlib
import json
import secrets
from dataclasses import dataclass

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction

from . import scoped_oauth_candidate as candidate
from .connector_identity import (
    IdentityConflict,
    IdentitySnapshot,
    _revision,
    _uuid,
    rotate_generation,
)
from .models import ConnectorIdentity
from .models import ScopedOAuthCandidateAttempt as Attempt


@dataclass(frozen=True)
class Retirement:
    snapshot: candidate.CandidateSnapshot
    current_identity: IdentitySnapshot


def receipt_binding_digest(row):
    value = [
        str(row.pk),
        str(row.connection_id),
        str(row.generation),
        row.expected_revision,
        row.session_key_hash,
        row.client_id_hash,
        row.created_at.isoformat(),
        row.expires_at.isoformat(),
    ]
    return hashlib.sha256(json.dumps(value).encode()).hexdigest()


@transaction.atomic
def retire_reserved(
    *,
    owner,
    workspace_id,
    connection_id,
    attempt_id,
    request_id,
    expected_generation,
    expected_revision,
    retirement_confirmation=False,
    expected_receipt_key=None,
):
    if getattr(settings, "GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED", False) is not True:
        raise PermissionDenied("Scoped candidate retirement is disabled.")
    if retirement_confirmation is not True:
        raise ValueError("Explicit retirement confirmation is required.")
    for value in (connection_id, attempt_id, request_id, expected_generation):
        _uuid(value)
    _revision(expected_revision)
    connector, current = candidate._locked(owner, workspace_id, connection_id)
    row = Attempt.objects.select_for_update().get(pk=attempt_id, connection=connector)
    snapshot = candidate._metadata(row)
    if expected_receipt_key is not None and (
        type(expected_receipt_key) is not str
        or not secrets.compare_digest(expected_receipt_key, receipt_binding_digest(row))
    ):
        raise IdentityConflict("Retirement receipt binding changed.")
    if (
        row.generation != expected_generation
        or row.expected_revision != expected_revision
    ):
        raise IdentityConflict("Retirement scope does not match the receipt.")
    if row.reason == "retired_before_exchange":
        if row.retirement_request_id != request_id:
            raise IdentityConflict("Retirement request does not match.")
        # Historical exact replay returns CURRENT identity, never reopening it.
        return Retirement(snapshot, current)
    if (
        row.state != Attempt.State.RESERVED
        or current.state != ConnectorIdentity.State.QUARANTINED
        or current.generation != expected_generation
        or current.revision != expected_revision
        or Attempt.objects.filter(connection=connector)
        .exclude(pk=attempt_id)
        .exclude(state=Attempt.State.REJECTED)
        .exists()
    ):
        raise IdentityConflict("Only an unexchanged current reservation can retire.")
    replacement = rotate_generation(
        owner=owner,
        workspace_id=workspace_id,
        connection_id=connection_id,
        request_id=request_id,
        expected_generation=expected_generation,
        expected_revision=expected_revision,
    )
    changed = Attempt.objects.filter(
        pk=attempt_id,
        state=Attempt.State.RESERVED,
        reason="",
        generation=expected_generation,
        expected_revision=expected_revision,
        retirement_request_id__isnull=True,
        retired_generation__isnull=True,
    ).update(
        state=Attempt.State.REJECTED,
        reason="retired_before_exchange",
        retirement_request_id=request_id,
        retired_generation=replacement.generation,
    )
    if changed != 1:
        raise IdentityConflict("Candidate changed during retirement.")
    row.refresh_from_db()
    return Retirement(candidate._metadata(row), replacement)
