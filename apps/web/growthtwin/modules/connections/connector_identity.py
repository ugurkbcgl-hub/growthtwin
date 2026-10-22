"""Durable TEST connector metadata exercised only in isolated synthetic tests.

No activation, credentials, network, account mapping, closure executor or routes.
Neither supported state grants provider-work permission; real runtime is not wired here.
"""

from dataclasses import dataclass
from uuid import UUID, uuid4

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction

from growthtwin.modules.workspaces.models import Workspace

from .models import ConnectorGeneration, ConnectorIdentity


class IdentityConflict(ValueError):
    """Reload metadata; never infer permission or automatically retry work."""


@dataclass(frozen=True)
class IdentitySnapshot:
    connection_id: UUID
    generation: UUID
    ordinal: int
    revision: int
    state: str


def _uuid(value):
    if type(value) is not UUID or not value.int:
        raise ValueError("A nonzero typed UUID is required.")


def _revision(value):
    if type(value) is not int or value < 0 or value >= 2**63 - 1:
        raise ValueError("A bounded revision is required.")


def _workspace(owner, workspace_id, *, lock=False):
    if not getattr(owner, "is_authenticated", False) or not getattr(
        owner, "is_active", False
    ):
        raise PermissionDenied("An active workspace owner is required.")
    rows = Workspace.objects.select_for_update() if lock else Workspace.objects
    return rows.get(pk=workspace_id, owner=owner, owner__is_active=True)


def _snapshot(row):
    # Fail closed on inconsistent metadata or a missing/retired generation chain.
    receipts = list(
        ConnectorGeneration.objects.filter(connection=row).order_by("ordinal")
    )
    if (
        row.provider != "google_ads_test"
        or row.state not in ConnectorIdentity.State.values
        or len(receipts) != row.ordinal
        or not receipts
    ):
        raise IdentityConflict("Connector metadata is inconsistent.")
    try:
        _uuid(row.pk)
        _uuid(row.generation)
        for receipt in receipts:
            _uuid(receipt.pk)
            _uuid(receipt.request_id)
    except ValueError:
        raise IdentityConflict("Connector identity is invalid.") from None
    previous = None
    for ordinal, receipt in enumerate(receipts, 1):
        if (
            receipt.ordinal != ordinal
            or receipt.from_generation != previous
            or receipt.from_revision != max(0, ordinal - 2)
        ):
            raise IdentityConflict("Connector generation history is inconsistent.")
        previous = receipt.pk
    expected_revision = row.ordinal - 1 + (row.state == ConnectorIdentity.State.BLOCKED)
    if row.generation != previous or row.revision != expected_revision:
        raise IdentityConflict("Connector current generation is inconsistent.")
    return IdentitySnapshot(
        row.pk, row.generation, row.ordinal, row.revision, row.state
    )


@transaction.atomic
def get_identity(*, owner, workspace_id, connection_id):
    _uuid(connection_id)
    # All paths take the workspace first, then the connection, including reads.
    workspace = _workspace(owner, workspace_id, lock=True)
    row = ConnectorIdentity.objects.select_for_update().get(
        pk=connection_id, workspace=workspace
    )
    return _snapshot(row)


@transaction.atomic
def register_google_test_identity(*, owner, workspace_id, request_id):
    _uuid(request_id)
    workspace = _workspace(owner, workspace_id, lock=True)
    row = ConnectorIdentity.objects.filter(
        workspace=workspace, provider="google_ads_test"
    ).first()
    receipt = ConnectorGeneration.objects.filter(request_id=request_id).first()
    if row:
        snapshot = _snapshot(row)
        if receipt and receipt.connection_id == row.pk and receipt.ordinal == 1:
            return snapshot
        raise IdentityConflict("Connector registration already exists.")
    if receipt:
        raise IdentityConflict("Request identity was already used.")
    try:
        with transaction.atomic():
            row = ConnectorIdentity.objects.create(workspace=workspace)
            ConnectorGeneration.objects.create(
                id=row.generation,
                connection=row,
                request_id=request_id,
                ordinal=1,
                from_generation=None,
                from_revision=0,
            )
    except IntegrityError:
        raise IdentityConflict("Connector registration conflicts.") from None
    return _snapshot(row)


@transaction.atomic
def rotate_generation(
    *,
    owner,
    workspace_id,
    connection_id,
    request_id,
    expected_generation,
    expected_revision,
):
    for value in (connection_id, request_id, expected_generation):
        _uuid(value)
    _revision(expected_revision)
    workspace = _workspace(owner, workspace_id, lock=True)
    row = ConnectorIdentity.objects.select_for_update().get(
        pk=connection_id, workspace=workspace
    )
    current = _snapshot(row)
    receipt = ConnectorGeneration.objects.filter(request_id=request_id).first()
    if receipt:
        if (
            receipt.connection_id == row.pk
            and receipt.ordinal > 1
            and receipt.from_generation == expected_generation
            and receipt.from_revision == expected_revision
        ):
            # Return CURRENT metadata, including later rotations or a permanent block.
            return current
        raise IdentityConflict("Request does not match the original rotation.")
    if (
        row.state != ConnectorIdentity.State.QUARANTINED
        or row.generation != expected_generation
        or row.revision != expected_revision
    ):
        raise IdentityConflict("Connector changed or is blocked.")
    generation = uuid4()
    try:
        with transaction.atomic():
            ConnectorGeneration.objects.create(
                id=generation,
                connection=row,
                request_id=request_id,
                ordinal=row.ordinal + 1,
                from_generation=row.generation,
                from_revision=row.revision,
            )
    except IntegrityError:
        raise IdentityConflict("Generation request conflicts.") from None
    changed = ConnectorIdentity.objects.filter(
        pk=row.pk,
        state=ConnectorIdentity.State.QUARANTINED,
        generation=expected_generation,
        revision=expected_revision,
    ).update(generation=generation, ordinal=row.ordinal + 1, revision=row.revision + 1)
    if changed != 1:
        raise IdentityConflict("Connector changed.")
    row.refresh_from_db()
    return _snapshot(row)


@transaction.atomic
def block_identity(
    *, owner, workspace_id, connection_id, expected_generation, expected_revision
):
    _uuid(connection_id)
    _uuid(expected_generation)
    _revision(expected_revision)
    workspace = _workspace(owner, workspace_id, lock=True)
    row = ConnectorIdentity.objects.select_for_update().get(
        pk=connection_id, workspace=workspace
    )
    current = _snapshot(row)
    if row.generation != expected_generation or row.revision != expected_revision:
        raise IdentityConflict("Connector changed.")
    if row.state == ConnectorIdentity.State.BLOCKED:
        return current
    changed = ConnectorIdentity.objects.filter(
        pk=row.pk,
        generation=expected_generation,
        revision=expected_revision,
        state=ConnectorIdentity.State.QUARANTINED,
    ).update(state=ConnectorIdentity.State.BLOCKED, revision=row.revision + 1)
    if changed != 1:
        raise IdentityConflict("Connector changed.")
    row.refresh_from_db()
    return _snapshot(row)
