"""Owner-scoped SYNTHETIC persistence; the UI supplies only fixed fixture facts.

Snapshots are fixture assertions, never verified provider evidence. No real
connection registry, credential access, provider calls, erasure or executor.
The stored barrier does not block existing Google routes. No arbitrary save,
reset, delete, reopen or generation-rotation API is exposed here.
"""

from uuid import NAMESPACE_URL, uuid5

from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.utils import timezone

from growthtwin.modules.workspaces.models import Workspace

from .lifecycle_codec import (
    InvalidClosureState,
    decode_record,
    encode_record,
    encode_snapshot,
)
from .lifecycle_decision import ClosureSnapshot, RequestFacts
from .lifecycle_observation import (
    ClosureIdentity,
    ClosureRecord,
    Disposition,
    Observation,
    reduce_observation,
)
from .lifecycle_ticket import (
    IssuanceDisposition,
    TicketRequest,
    issue_ticket,
)
from .models import SyntheticClosureOperation, SyntheticClosureRequest


class ClosureConflict(ValueError):
    """No write committed; reload and review, never automatically resend."""


def _workspace(owner, workspace_id):
    if not getattr(owner, "is_authenticated", False) or not getattr(
        owner, "is_active", False
    ):
        raise PermissionDenied("An active workspace owner is required.")
    return Workspace.objects.get(pk=workspace_id, owner=owner, owner__is_active=True)


def _identity(row):
    # Stable synthetic mapping of the existing integer tenant PK, NOT anonymity.
    return ClosureIdentity(
        uuid5(NAMESPACE_URL, f"growthtwin:synthetic-workspace:{row.workspace_id}"),
        row.connection_id,
        row.pk,
        row.generation,
    )


def _load(owner, workspace_id, request_id):
    workspace = _workspace(owner, workspace_id)
    row = SyntheticClosureRequest.objects.select_for_update().get(
        pk=request_id, workspace=workspace
    )
    record = decode_record(_identity(row), row.state)
    if row.revision != record.revision:
        raise InvalidClosureState("Stored synthetic revision is inconsistent.")
    tickets = [ticket for ticket in (record.pending, record.priority_pending) if ticket]
    tickets.extend(event.ticket for event in record.seen_events)
    receipts = {
        receipt.pk: receipt
        for receipt in SyntheticClosureOperation.objects.filter(request=row)
    }
    operation_ids = {ticket.operation_id for ticket in tickets}
    if len(tickets) != len(operation_ids) or operation_ids != set(receipts):
        raise InvalidClosureState("Synthetic operation receipts are inconsistent.")
    for ticket in tickets:
        receipt = receipts.get(ticket.operation_id)
        if receipt is None or (
            receipt.source_step != ticket.source_step
            or receipt.outcome != ticket.outcome
            or receipt.issued_revision != ticket.issued_revision
        ):
            raise InvalidClosureState("Synthetic operation receipt does not match.")
    return row, record


def _cas(owner, row, updated):
    if updated.revision != row.revision + 1 or updated.identity != _identity(row):
        raise InvalidClosureState("Invalid synthetic revision transition.")
    changed = SyntheticClosureRequest.objects.filter(
        pk=row.pk,
        workspace_id=row.workspace_id,
        workspace__owner=owner,
        workspace__owner__is_active=True,
        revision=row.revision,
    ).update(
        revision=updated.revision,
        state=encode_record(updated),
        updated_at=timezone.now(),
    )
    if changed != 1:
        raise ClosureConflict("Synthetic closure changed; reload before review.")


def create_synthetic_closure(
    *,
    owner,
    workspace_id,
    connection_id,
    generation,
    request_id,
    snapshot=ClosureSnapshot(),
):
    """Reserve one synthetic request per workspace/connection, with exact replay.

    The connection UUID is a fixture identifier, not an actual Google account.
    A different generation/request cannot replace this experiment's barrier.
    """
    workspace = _workspace(owner, workspace_id)
    row = SyntheticClosureRequest(
        pk=request_id,
        workspace=workspace,
        connection_id=connection_id,
        generation=generation,
        initial_snapshot=encode_snapshot(snapshot),
    )
    record = ClosureRecord(_identity(row), 0, snapshot)
    row.state = encode_record(record)
    try:
        with transaction.atomic():
            row.save(force_insert=True)
        return record
    except IntegrityError:
        # A transaction/unique constraint, not a read-then-insert assumption,
        # decides creation races. Do not expose another tenant's conflicting ID.
        with transaction.atomic():
            try:
                existing, current = _load(owner, workspace_id, request_id)
            except SyntheticClosureRequest.DoesNotExist:
                raise ClosureConflict("Synthetic request identity conflicts.") from None
            if (
                current.identity != record.identity
                or existing.initial_snapshot != row.initial_snapshot
            ):
                raise ClosureConflict("Synthetic request identity conflicts.") from None
            return current


@transaction.atomic
def get_synthetic_closure(*, owner, workspace_id, request_id):
    """Reload a frozen value and its receipts, not a mutable ORM instance."""
    return _load(owner, workspace_id, request_id)[1]


def issue_synthetic_ticket(*, owner, workspace_id, request):
    """Atomically persist ticket + receipt; this never queues or executes work."""
    if type(request) is not TicketRequest:
        raise ValueError("A typed synthetic ticket request is required.")
    try:
        with transaction.atomic():
            row, record = _load(owner, workspace_id, request.identity.request_id)
            result = issue_ticket(RequestFacts(True, True, True, True), record, request)
            if result.disposition is IssuanceDisposition.ISSUED:
                _cas(owner, row, result.record)
                ticket = next(
                    ticket
                    for ticket in (
                        result.record.pending,
                        result.record.priority_pending,
                    )
                    if ticket and ticket.operation_id == request.operation_id
                )
                SyntheticClosureOperation.objects.create(
                    pk=ticket.operation_id,
                    request=row,
                    source_step=ticket.source_step,
                    outcome=ticket.outcome,
                    issued_revision=ticket.issued_revision,
                )
            return result
    except IntegrityError:
        raise ClosureConflict(
            "Synthetic operation identity conflicts; no write."
        ) from None


@transaction.atomic
def observe_synthetic_closure(*, owner, workspace_id, event):
    """Persist a typed fixture observation, not proof of any real-world result."""
    if type(event) is not Observation:
        raise ValueError("A typed synthetic observation is required.")
    row, record = _load(owner, workspace_id, event.identity.request_id)
    result = reduce_observation(RequestFacts(True, True, True, True), record, event)
    if result.disposition is Disposition.APPLIED:
        _cas(owner, row, result.record)
    return result
