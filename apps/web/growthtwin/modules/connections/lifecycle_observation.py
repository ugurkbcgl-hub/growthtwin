"""Pure synthetic observation reducer, not storage or a provider callback handler.

Pending tickets assert prior authorization by a future coordinator. This module
does not issue tickets, verify provider evidence, or implement atomic persistence.
It cannot update barrier/recovery flags, grants, generation or closed status.
"""

from dataclasses import dataclass, replace
from enum import StrEnum
from uuid import UUID

from .lifecycle_decision import (
    ClosureSnapshot,
    ExternalErasure,
    LocalErasure,
    LocalSecret,
    RemoteStop,
    RequestFacts,
    Revocation,
    Step,
    evaluate_closure,
)


class Outcome(StrEnum):
    REMOTE_STOP = "remote_stop"
    REVOCATION = "revocation"
    LOCAL_SECRET = "local_secret"
    LOCAL_ERASURE = "local_erasure"
    RECIPIENT_ERASURE = "recipient_erasure"
    BACKUP_ERASURE = "backup_erasure"


_TYPES = {
    Outcome.REMOTE_STOP: RemoteStop,
    Outcome.REVOCATION: Revocation,
    Outcome.LOCAL_SECRET: LocalSecret,
    Outcome.LOCAL_ERASURE: LocalErasure,
    Outcome.RECIPIENT_ERASURE: ExternalErasure,
    Outcome.BACKUP_ERASURE: ExternalErasure,
}


def _uuid(value):
    if type(value) is not UUID or value.int == 0:
        raise ValueError("A nonzero synthetic UUID is required.")


def _revision(value):
    if type(value) is not int or value < 0:
        raise ValueError("A nonnegative integer revision is required.")


@dataclass(frozen=True)
class ClosureIdentity:
    workspace_id: UUID
    connection_id: UUID
    request_id: UUID
    generation: UUID

    def __post_init__(self):
        for name in self.__dataclass_fields__:
            _uuid(getattr(self, name))


@dataclass(frozen=True)
class PendingObservation:
    operation_id: UUID
    outcome: Outcome

    def __post_init__(self):
        _uuid(self.operation_id)
        if type(self.outcome) is not Outcome:
            raise ValueError("A typed outcome is required.")


@dataclass(frozen=True)
class Observation:
    identity: ClosureIdentity
    expected_revision: int
    event_id: UUID
    ticket: PendingObservation
    value: RemoteStop | Revocation | LocalSecret | LocalErasure | ExternalErasure

    def __post_init__(self):
        if type(self.identity) is not ClosureIdentity:
            raise ValueError("A typed closure identity is required.")
        _revision(self.expected_revision)
        _uuid(self.event_id)
        if type(self.ticket) is not PendingObservation:
            raise ValueError("A typed observation ticket is required.")
        if type(self.value) is not _TYPES[self.ticket.outcome]:
            raise ValueError("Evidence does not match the declared outcome.")


@dataclass(frozen=True)
class ClosureRecord:
    identity: ClosureIdentity
    revision: int
    snapshot: ClosureSnapshot
    pending: PendingObservation | None = None
    closed: bool = False
    seen_events: tuple[Observation, ...] = ()

    def __post_init__(self):
        if type(self.identity) is not ClosureIdentity:
            raise ValueError("A typed closure identity is required.")
        _revision(self.revision)
        if type(self.snapshot) is not ClosureSnapshot or type(self.closed) is not bool:
            raise ValueError("Typed closure state is required.")
        if self.pending is not None and type(self.pending) is not PendingObservation:
            raise ValueError("A typed observation ticket is required.")
        if type(self.seen_events) is not tuple or any(
            type(event) is not Observation or event.identity != self.identity
            for event in self.seen_events
        ):
            raise ValueError("Immutable same-scope evidence is required.")
        if len({event.event_id for event in self.seen_events}) != len(self.seen_events):
            raise ValueError("Duplicate evidence identities are invalid.")


class Disposition(StrEnum):
    APPLIED = "applied"
    DUPLICATE = "duplicate"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Reduction:
    record: ClosureRecord
    disposition: Disposition
    reason: str


def _transition_allowed(snapshot, outcome, value):
    current = getattr(snapshot, outcome.value)
    if current is value:
        return True
    if outcome is Outcome.REMOTE_STOP:
        return (
            current in {RemoteStop.PENDING, RemoteStop.UNCERTAIN}
            and value in {RemoteStop.CONFIRMED, RemoteStop.UNCERTAIN}
            and not (value is RemoteStop.CONFIRMED and snapshot.in_flight)
        )
    if outcome is Outcome.REVOCATION:
        return current is not Revocation.CONFIRMED and value in {
            Revocation.CONFIRMED,
            Revocation.UNVERIFIED,
        }
    if outcome is Outcome.LOCAL_SECRET:
        return current is not LocalSecret.ABSENT and value in {
            LocalSecret.ABSENT,
            LocalSecret.ERROR,
        }
    if outcome is Outcome.LOCAL_ERASURE:
        if current in {LocalErasure.BLOCKED, LocalErasure.COMPLETED}:
            return False
        if value is LocalErasure.COMPLETED:
            facts = RequestFacts(True, True, True, True)
            return Step.ERASE_LOCAL in evaluate_closure(facts, snapshot).next_steps
        return value in {LocalErasure.PARTIAL, LocalErasure.BLOCKED}
    return current in {
        ExternalErasure.PENDING,
        ExternalErasure.UNVERIFIED,
    } and value in {ExternalErasure.CONFIRMED, ExternalErasure.UNVERIFIED}


def reduce_observation(facts, record, event):
    """Return a replacement record; never reopen, authorize or execute an action.

    Revision is a compare-and-swap precondition only. A future storage adapter
    must enforce it atomically; two independent Python results are not a lock.
    Same event ID with different content is a conflict, not an idempotent replay.
    """
    if (
        type(facts) is not RequestFacts
        or type(record) is not ClosureRecord
        or type(event) is not Observation
    ):
        raise ValueError("Typed observation inputs are required.")

    def reject(reason):
        return Reduction(record, Disposition.REJECTED, reason)

    if not all(getattr(facts, name) for name in facts.__dataclass_fields__):
        return reject("request_unverified")
    if record.identity != event.identity:
        return reject("identity_mismatch")
    for seen in record.seen_events:
        if seen.event_id == event.event_id:
            if seen == event:
                return Reduction(record, Disposition.DUPLICATE, "exact_replay")
            return reject("event_identity_conflict")
    if record.closed:
        return reject("request_closed")
    if event.expected_revision != record.revision:
        return reject("revision_mismatch")
    if record.pending != event.ticket:
        return reject("ticket_mismatch")
    if not record.snapshot.recovery_verified or not record.snapshot.barrier_confirmed:
        return reject("closure_evidence_unverified")
    if not _transition_allowed(record.snapshot, event.ticket.outcome, event.value):
        return reject("transition_not_allowed")
    updated = replace(
        record,
        revision=record.revision + 1,
        pending=None,
        snapshot=replace(record.snapshot, **{event.ticket.outcome.value: event.value}),
        seen_events=(*record.seen_events, event),
    )
    return Reduction(updated, Disposition.APPLIED, "observation_applied")
