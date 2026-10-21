"""Serialized fixture-only new-work/callback gate. Not a Google runtime guard.

Only positively registered fixed synthetic scopes may run the deterministic
local fake. No arbitrary executor, payload, token, provider or grant writes.
Workspace locks order fake work versus closure intake; already-sent network
effects and independently trustworthy restore evidence are not implemented.
"""

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from django.db import transaction

from . import lifecycle_fake
from .lifecycle_journey import EXAMPLES, example_id
from .lifecycle_observation import _revision, _uuid
from .lifecycle_store import ClosureConflict, _workspace
from .models import SyntheticClosureRequest, SyntheticConnectionScope


class WorkKind(StrEnum):
    CREATE = "create"
    REFRESH = "refresh"
    CALLBACK_SAVE = "callback_save"


@dataclass(frozen=True)
class FakeWorkRequest:
    connection_id: UUID
    generation: UUID
    expected_revision: int
    kind: WorkKind

    def __post_init__(self):
        _uuid(self.connection_id)
        _uuid(self.generation)
        _revision(self.expected_revision)
        if type(self.kind) is not WorkKind:
            raise ValueError("A typed synthetic work kind is required.")


@dataclass(frozen=True)
class ScopeSnapshot:
    connection_id: UUID
    generation: UUID
    state: str
    revision: int
    fake_work_count: int


def _snapshot(scope):
    return ScopeSnapshot(
        scope.pk, scope.generation, scope.state, scope.revision, scope.fake_work_count
    )


def _known_example(workspace_id, connection_id):
    return next(
        (
            key
            for key, _ in EXAMPLES
            if connection_id == example_id(workspace_id, "connection", key)
        ),
        None,
    )


@transaction.atomic
def register_fixture_scope(*, owner, workspace_id, example="durdurma"):
    """Explicitly prepare a fixed fake scope; never reset/reopen on replay.

    These registration assertions apply only to fresh local fixtures. They are
    not provider authorization or production recovery verification.
    """
    workspace = _workspace(owner, workspace_id, lock=True)
    connection_id = example_id(workspace_id, "connection", example)
    closed = SyntheticClosureRequest.objects.filter(
        workspace=workspace, connection_id=connection_id
    ).exists()
    scope, _ = SyntheticConnectionScope.objects.get_or_create(
        pk=connection_id,
        workspace=workspace,
        defaults={
            "generation": example_id(workspace_id, "generation", example),
            "state": (
                SyntheticConnectionScope.State.BLOCKED
                if closed
                else SyntheticConnectionScope.State.OPEN
            ),
        },
    )
    return _snapshot(scope)


@dataclass(frozen=True)
class GuardResult:
    performed: bool
    reason: str
    scope: ScopeSnapshot | None


@transaction.atomic
def perform_fake_work(*, owner, workspace_id, request):
    """Check and run only a local fake under the same lock as closure intake."""
    if type(request) is not FakeWorkRequest:
        raise ValueError("A typed synthetic work request is required.")
    workspace = _workspace(owner, workspace_id, lock=True)
    example = _known_example(workspace_id, request.connection_id)
    if example is None:
        return GuardResult(False, "unknown_fixture_scope", None)
    scope = (
        SyntheticConnectionScope.objects.select_for_update()
        .filter(workspace=workspace, pk=request.connection_id)
        .first()
    )
    if scope is None:
        return GuardResult(False, "unregistered_scope", None)
    snapshot = _snapshot(scope)
    if (
        scope.generation != example_id(workspace_id, "generation", example)
        or request.generation != scope.generation
    ):
        return GuardResult(False, "generation_mismatch", snapshot)
    # Any closure for this connection blocks work, regardless of request or
    # generation. Do not trust a successful STOP as permission to start again.
    if (
        scope.state == SyntheticConnectionScope.State.BLOCKED
        or SyntheticClosureRequest.objects.filter(
            workspace=workspace, connection_id=scope.pk
        ).exists()
    ):
        return GuardResult(False, "closure_blocks_new_work", snapshot)
    if scope.state != SyntheticConnectionScope.State.OPEN:
        return GuardResult(False, "scope_not_verified", snapshot)
    if (
        type(scope.revision) is not int
        or type(scope.fake_work_count) is not int
        or not 0 <= scope.fake_work_count <= scope.revision
    ):
        return GuardResult(False, "invalid_scope_metadata", snapshot)
    if request.expected_revision != scope.revision:
        return GuardResult(False, "revision_mismatch", snapshot)
    output = lifecycle_fake.new_work_result(request.kind.value)
    if output != request.kind.value:
        raise ClosureConflict("Unexpected synthetic work result.")
    changed = SyntheticConnectionScope.objects.filter(
        pk=scope.pk,
        workspace=workspace,
        generation=scope.generation,
        state=SyntheticConnectionScope.State.OPEN,
        revision=scope.revision,
    ).update(revision=scope.revision + 1, fake_work_count=scope.fake_work_count + 1)
    if changed != 1:
        raise ClosureConflict("Synthetic scope changed; no fake result committed.")
    scope.revision += 1
    scope.fake_work_count += 1
    return GuardResult(True, "fake_work_recorded", _snapshot(scope))
