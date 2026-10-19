"""Pure synthetic ticket issuance; no runtime permission, storage or execution.

Only steps with a typed observation outcome are supported. A future adapter
must persist revision and ticket atomically and recheck auth/provider evidence.
An exact issuance replay is a no-op, never an instruction to execute again.
"""

from dataclasses import dataclass, replace
from enum import StrEnum
from uuid import UUID

from .lifecycle_decision import RequestFacts, Step, evaluate_closure
from .lifecycle_observation import (
    _ISSUABLE_OUTCOMES,
    ClosureIdentity,
    ClosureRecord,
    Outcome,
    PendingObservation,
    _revision,
    _uuid,
)


@dataclass(frozen=True)
class TicketRequest:
    identity: ClosureIdentity
    expected_revision: int
    operation_id: UUID
    step: Step

    def __post_init__(self):
        if type(self.identity) is not ClosureIdentity or type(self.step) is not Step:
            raise ValueError("Typed ticket identity and step are required.")
        _revision(self.expected_revision)
        _uuid(self.operation_id)


class IssuanceDisposition(StrEnum):
    ISSUED = "issued"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Issuance:
    record: ClosureRecord
    disposition: IssuanceDisposition
    reason: str


def issue_ticket(facts, record, request):
    """Reserve one eligible synthetic step; outcome evidence stays unchanged.

    Recovery/barrier checks precede replay recognition. Rejected and duplicate
    results retain the exact input object. Tickets for manual review, barrier/
    recovery checks and unresolved-create reconciliation are not supported here.
    """
    if (
        type(facts) is not RequestFacts
        or type(record) is not ClosureRecord
        or type(request) is not TicketRequest
    ):
        raise ValueError("Typed issuance inputs are required.")

    def reject(reason):
        return Issuance(record, IssuanceDisposition.REJECTED, reason)

    if not all(getattr(facts, name) for name in facts.__dataclass_fields__):
        return reject("request_unverified")
    if request.identity != record.identity:
        return reject("identity_mismatch")
    if record.closed:
        return reject("request_closed")
    if not record.snapshot.recovery_verified or not record.snapshot.barrier_confirmed:
        return reject("closure_evidence_unverified")
    if request.step not in _ISSUABLE_OUTCOMES:
        return reject("unsupported_step")

    candidate = PendingObservation(
        operation_id=request.operation_id,
        outcome=_ISSUABLE_OUTCOMES[request.step],
        source_step=request.step,
        issued_revision=request.expected_revision + 1,
    )
    active = tuple(
        ticket for ticket in (record.pending, record.priority_pending) if ticket
    )
    for ticket in active:
        if ticket.operation_id == request.operation_id:
            if ticket == candidate:
                return Issuance(record, IssuanceDisposition.DUPLICATE, "exact_replay")
            return reject("operation_identity_conflict")
    if request.expected_revision != record.revision:
        return reject("revision_mismatch")
    if any(
        event.ticket.operation_id == request.operation_id
        for event in record.seen_events
    ):
        return reject("operation_already_observed")
    if request.step not in evaluate_closure(facts, record.snapshot).next_steps:
        return reject("step_not_eligible")
    if active:
        # Immediate revocation must not wait for stop/reconciliation. Preserve
        # the old operation and reserve a separate, bounded priority lane.
        urgent = (
            request.step is Step.REVOKE
            and record.snapshot.immediate_revoke
            and record.priority_pending is None
            and not any(
                ticket.source_step is Step.REVOKE
                or (ticket.source_step is None and ticket.outcome is Outcome.REVOCATION)
                for ticket in active
            )
        )
        if not urgent:
            return reject("operation_unresolved")
        updated = replace(
            record, revision=record.revision + 1, priority_pending=candidate
        )
    else:
        updated = replace(record, revision=record.revision + 1, pending=candidate)
    return Issuance(updated, IssuanceDisposition.ISSUED, "ticket_issued")
