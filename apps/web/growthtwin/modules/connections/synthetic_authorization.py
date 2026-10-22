"""Default-off, generation-bound fixed-example coordination, not OAuth.

No URL, actual token/code/PKCE/session, provider call or credential write.
Accepted means only a local fake example; identity remains quarantined.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, connection, transaction
from django.utils import timezone

from .connector_identity import (
    IdentityConflict,
    _revision,
    _snapshot,
    _uuid,
    _workspace,
)
from .models import ConnectorGeneration, ConnectorIdentity
from .models import SyntheticAuthorizationAttempt as Attempt

LIFETIME = timedelta(minutes=10)
ACTIVE = (Attempt.State.PENDING, Attempt.State.RUNNING)
REJECTION_REASONS = {
    "scope_changed",
    "disabled",
    "clock_changed",
    "example_denied",
    "fake_failed",
}


class FakeAuthorizationScenario(StrEnum):
    ALLOW = "allow_example"
    DENY = "deny_example"


@dataclass(frozen=True)
class AttemptSnapshot:
    attempt_id: UUID
    connection_id: UUID
    generation: UUID
    expected_revision: int
    scenario: FakeAuthorizationScenario
    state: str
    reason: str
    expires_at: datetime


def _enabled():
    return getattr(settings, "SYNTHETIC_CONNECTOR_AUTHORIZATION_ENABLED", False) is True


def _require_enabled():
    if not _enabled():
        raise PermissionDenied("Synthetic authorization rehearsal is disabled.")


def _attempt_snapshot(row):
    try:
        _uuid(row.pk)
        _uuid(row.generation)
        _revision(row.expected_revision)
        scenario = FakeAuthorizationScenario(row.scenario)
        if not ConnectorGeneration.objects.filter(
            pk=row.generation,
            connection_id=row.connection_id,
            ordinal=row.expected_revision + 1,
        ).exists():
            raise ValueError
        if (
            row.mode != "synthetic"
            or row.state not in Attempt.State.values
            or timezone.is_naive(row.created_at)
            or timezone.is_naive(row.expires_at)
            or row.expires_at - row.created_at != LIFETIME
        ):
            raise ValueError
        if row.state in ACTIVE or row.state == Attempt.State.ACCEPTED:
            if row.reason:
                raise ValueError
        elif row.state == Attempt.State.EXPIRED:
            if row.reason != "expired":
                raise ValueError
        elif row.reason not in REJECTION_REASONS:
            raise ValueError
        if (row.completed_at is None) != (row.state in ACTIVE):
            raise ValueError
        if row.completed_at is not None and timezone.is_naive(row.completed_at):
            raise ValueError
        if row.state == Attempt.State.ACCEPTED and (
            scenario is not FakeAuthorizationScenario.ALLOW
            or not row.created_at <= row.completed_at < row.expires_at
        ):
            raise ValueError
    except (ValueError, TypeError, AttributeError):
        raise IdentityConflict("Synthetic attempt metadata is inconsistent.") from None
    return AttemptSnapshot(
        row.pk,
        row.connection_id,
        row.generation,
        row.expected_revision,
        scenario,
        row.state,
        row.reason,
        row.expires_at,
    )


def _locked_connection(owner, workspace_id, connection_id):
    workspace = _workspace(owner, workspace_id, lock=True)
    row = ConnectorIdentity.objects.select_for_update().get(
        pk=connection_id, workspace=workspace
    )
    return row, _snapshot(row)


def _reason(current, row, now):
    if not _enabled():
        return "disabled"
    if (
        current.state != ConnectorIdentity.State.QUARANTINED
        or current.generation != row.generation
        or current.revision != row.expected_revision
    ):
        return "scope_changed"
    if now < row.created_at:
        return "clock_changed"
    if now >= row.expires_at:
        return "expired"
    return ""


def _complete(row, reason, now):
    state = (
        Attempt.State.EXPIRED
        if reason == "expired"
        else Attempt.State.REJECTED
        if reason
        else Attempt.State.ACCEPTED
    )
    changed = Attempt.objects.filter(pk=row.pk, state=row.state).update(
        state=state, reason=reason, completed_at=now
    )
    if changed != 1:
        raise IdentityConflict("Synthetic attempt changed.")
    row.refresh_from_db()
    return _attempt_snapshot(row)


@transaction.atomic
def begin_example(
    *,
    owner,
    workspace_id,
    connection_id,
    attempt_id,
    expected_generation,
    expected_revision,
    scenario,
    synthetic_confirmation=False,
):
    _require_enabled()
    if (
        synthetic_confirmation is not True
        or type(scenario) is not FakeAuthorizationScenario
    ):
        raise ValueError("Explicit typed synthetic confirmation/scenario required.")
    for value in (connection_id, attempt_id, expected_generation):
        _uuid(value)
    _revision(expected_revision)
    connector, current = _locked_connection(owner, workspace_id, connection_id)
    if (
        current.state != ConnectorIdentity.State.QUARANTINED
        or current.generation != expected_generation
        or current.revision != expected_revision
    ):
        raise IdentityConflict("Connector changed or is blocked.")
    existing = Attempt.objects.select_for_update().filter(pk=attempt_id).first()
    now = timezone.now()
    if existing:
        _attempt_snapshot(existing)
        if (
            existing.connection_id != connector.pk
            or existing.generation != expected_generation
            or existing.expected_revision != expected_revision
            or existing.scenario != scenario
            or _reason(current, existing, now)
        ):
            raise IdentityConflict("Attempt does not match current scope.")
        return _attempt_snapshot(existing)
    active = (
        Attempt.objects.select_for_update()
        .filter(connection=connector, state__in=ACTIVE)
        .first()
    )
    if active:
        _attempt_snapshot(active)
        reason = _reason(current, active, now)
        if not reason:
            raise IdentityConflict("A synthetic attempt is already pending.")
        _complete(active, reason, now)
    try:
        with transaction.atomic():
            row = Attempt.objects.create(
                id=attempt_id,
                connection=connector,
                generation=expected_generation,
                expected_revision=expected_revision,
                scenario=scenario,
                created_at=now,
                expires_at=now + LIFETIME,
            )
    except IntegrityError:
        raise IdentityConflict("Synthetic attempt identity conflicts.") from None
    return _attempt_snapshot(row)


@transaction.atomic
def get_example(*, owner, workspace_id, connection_id, attempt_id):
    _uuid(connection_id)
    _uuid(attempt_id)
    connector, _ = _locked_connection(owner, workspace_id, connection_id)
    row = Attempt.objects.select_for_update().get(pk=attempt_id, connection=connector)
    # Historical metadata only, never a credential or current authorization.
    return _attempt_snapshot(row)


def _fixed_result(scenario):
    """Deterministic local fake. No arbitrary executor or submitted evidence."""
    return scenario is FakeAuthorizationScenario.ALLOW


def perform_example(*, owner, workspace_id, connection_id, attempt_id):
    _require_enabled()
    _uuid(connection_id)
    _uuid(attempt_id)
    if connection.in_atomic_block:
        raise IdentityConflict("Run the fake outside any caller transaction.")
    with transaction.atomic():
        connector, current = _locked_connection(owner, workspace_id, connection_id)
        row = Attempt.objects.select_for_update().get(
            pk=attempt_id, connection=connector
        )
        snapshot = _attempt_snapshot(row)
        if row.state not in ACTIVE:
            return snapshot
        now = timezone.now()
        reason = _reason(current, row, now)
        if reason:
            return _complete(row, reason, now)
        if row.state == Attempt.State.RUNNING:
            # Never replay an in-flight fake or infer that its result succeeded.
            return snapshot
        row.state = Attempt.State.RUNNING
        row.save(update_fields=["state"])
        scenario = snapshot.scenario
        expected = snapshot
    try:
        result = _fixed_result(scenario)
        fake_reason = (
            ""
            if result is True and scenario is FakeAuthorizationScenario.ALLOW
            else "example_denied"
            if result is False and scenario is FakeAuthorizationScenario.DENY
            else "fake_failed"
        )
    except Exception:
        fake_reason = "fake_failed"
    with transaction.atomic():
        connector, current = _locked_connection(owner, workspace_id, connection_id)
        row = Attempt.objects.select_for_update().get(
            pk=attempt_id, connection=connector
        )
        snapshot = _attempt_snapshot(row)
        if row.state != Attempt.State.RUNNING:
            return snapshot
        now = timezone.now()
        # Recheck immutable attempt binding too, not just the connector version.
        if (
            snapshot.generation != expected.generation
            or snapshot.expected_revision != expected.expected_revision
            or snapshot.scenario != expected.scenario
            or snapshot.expires_at != expected.expires_at
        ):
            return _complete(row, "scope_changed", now)
        reason = _reason(current, row, now) or fake_reason
        return _complete(row, reason, now)
