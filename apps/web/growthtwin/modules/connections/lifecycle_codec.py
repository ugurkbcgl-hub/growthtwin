"""Versioned, allowlisted synthetic state encoding; no arbitrary text payloads."""

from dataclasses import fields
from uuid import UUID

from .lifecycle_decision import (
    ClosureSnapshot,
    ExternalErasure,
    LocalErasure,
    LocalSecret,
    RemoteStop,
    Revocation,
    Step,
)
from .lifecycle_observation import (
    ClosureRecord,
    Observation,
    Outcome,
    PendingObservation,
)

_OUTCOME_TYPES = {
    "remote_stop": RemoteStop,
    "revocation": Revocation,
    "local_secret": LocalSecret,
    "local_erasure": LocalErasure,
    "recipient_erasure": ExternalErasure,
    "backup_erasure": ExternalErasure,
}


class InvalidClosureState(ValueError):
    """Stored metadata is unsupported or inconsistent; do not guess or repair."""


def _keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise InvalidClosureState("Unsupported synthetic closure metadata.")


def encode_snapshot(snapshot):
    if type(snapshot) is not ClosureSnapshot:
        raise ValueError("A typed synthetic snapshot is required.")
    return {
        field.name: (
            getattr(snapshot, field.name).value
            if field.name in _OUTCOME_TYPES
            else getattr(snapshot, field.name)
        )
        for field in fields(snapshot)
    }


def _snapshot(data):
    _keys(data, (field.name for field in fields(ClosureSnapshot)))
    # Enums must arrive as strings; bool/int coercion is deliberately forbidden.
    if any(type(data[name]) is not str for name in _OUTCOME_TYPES):
        raise InvalidClosureState("Unsupported synthetic outcome metadata.")
    return ClosureSnapshot(
        **{
            name: _OUTCOME_TYPES[name](value) if name in _OUTCOME_TYPES else value
            for name, value in data.items()
        }
    )


def _encode_ticket(ticket):
    if ticket is None:
        return None
    if ticket.source_step is None or ticket.issued_revision is None:
        raise InvalidClosureState("Unissued synthetic tickets cannot be stored.")
    return {
        "operation_id": str(ticket.operation_id),
        "outcome": ticket.outcome.value,
        "source_step": ticket.source_step.value,
        "issued_revision": ticket.issued_revision,
    }


def _ticket(data):
    if data is None:
        return None
    _keys(data, ("operation_id", "outcome", "source_step", "issued_revision"))
    return PendingObservation(
        UUID(data["operation_id"]),
        Outcome(data["outcome"]),
        Step(data["source_step"]),
        data["issued_revision"],
    )


def encode_record(record):
    if type(record) is not ClosureRecord:
        raise ValueError("A typed synthetic record is required.")
    return {
        "version": 1,
        "revision": record.revision,
        "snapshot": encode_snapshot(record.snapshot),
        "pending": _encode_ticket(record.pending),
        "priority_pending": _encode_ticket(record.priority_pending),
        "closed": record.closed,
        "seen_events": [
            {
                "expected_revision": event.expected_revision,
                "event_id": str(event.event_id),
                "ticket": _encode_ticket(event.ticket),
                "value": event.value.value,
            }
            for event in record.seen_events
        ],
    }


def decode_record(identity, data):
    """Rebuild only typed state; identity comes from scoped database columns."""
    try:
        _keys(
            data,
            (
                "version",
                "revision",
                "snapshot",
                "pending",
                "priority_pending",
                "closed",
                "seen_events",
            ),
        )
        if type(data["version"]) is not int or data["version"] != 1:
            raise InvalidClosureState("Unsupported synthetic state version.")
        if type(data["seen_events"]) is not list:
            raise InvalidClosureState("Invalid synthetic observation collection.")
        events = []
        for item in data["seen_events"]:
            _keys(item, ("expected_revision", "event_id", "ticket", "value"))
            ticket = _ticket(item["ticket"])
            if ticket is None:
                raise InvalidClosureState("Observation requires an issued ticket.")
            events.append(
                Observation(
                    identity,
                    item["expected_revision"],
                    UUID(item["event_id"]),
                    ticket,
                    _OUTCOME_TYPES[ticket.outcome.value](item["value"]),
                )
            )
        return ClosureRecord(
            identity=identity,
            revision=data["revision"],
            snapshot=_snapshot(data["snapshot"]),
            pending=_ticket(data["pending"]),
            priority_pending=_ticket(data["priority_pending"]),
            closed=data["closed"],
            seen_events=tuple(events),
        )
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise InvalidClosureState(
            "Invalid synthetic closure state; no update."
        ) from exc
