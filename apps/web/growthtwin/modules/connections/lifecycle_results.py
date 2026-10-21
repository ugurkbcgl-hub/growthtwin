"""Bounded synthetic STOP observations, never an external action executor."""

from dataclasses import replace

from django.db import transaction

from . import lifecycle_fake
from .lifecycle_decision import RemoteStop, Step
from .lifecycle_journey import EXAMPLES, example_id, example_snapshot
from .lifecycle_observation import Disposition, Observation, Outcome, PendingObservation
from .lifecycle_store import (
    ClosureConflict,
    get_synthetic_closure,
    observe_synthetic_closure,
)


def example_for_record(workspace_id, record):
    for example, _ in EXAMPLES:
        if (
            record.identity.request_id == example_id(workspace_id, "request", example)
            and record.identity.connection_id
            == example_id(workspace_id, "connection", example)
            and record.identity.generation
            == example_id(workspace_id, "generation", example)
        ):
            return example
    return None


def example_ticket(workspace_id, example):
    return PendingObservation(
        example_id(workspace_id, "operation", example),
        Outcome.REMOTE_STOP,
        Step.STOP,
        1,
    )


def result_available(workspace_id, record):
    example = example_for_record(workspace_id, record)
    return (
        example is not None
        and not record.closed
        and record.revision == 1
        and record.pending == example_ticket(workspace_id, example)
        and record.priority_pending is None
        and not record.seen_events
        and record.snapshot == example_snapshot()
    )


@transaction.atomic
def complete_example(
    *, owner, workspace_id, request_id, operation_id, expected_revision
):
    """Commit one fixed fixture result; exact replay never invokes the fake twice.

    No arbitrary record/outcome/proof argument. Ownership is loaded inside the
    transaction and PostgreSQL locks survive through observation commit.
    """
    record = get_synthetic_closure(
        owner=owner, workspace_id=workspace_id, request_id=request_id
    )
    example = example_for_record(workspace_id, record)
    if example is None:
        raise ClosureConflict("Record is not a supported synthetic fixture.")
    ticket = example_ticket(workspace_id, example)
    if (
        operation_id != ticket.operation_id
        or type(expected_revision) is not int
        or expected_revision != 1
        or record.closed
        or not record.snapshot.barrier_confirmed
        or not record.snapshot.recovery_verified
    ):
        raise ClosureConflict("Synthetic operation/revision does not match.")
    expected_value = (
        RemoteStop.CONFIRMED if example == "durdurma" else RemoteStop.UNCERTAIN
    )
    event = Observation(
        record.identity,
        expected_revision,
        example_id(workspace_id, "observation", example),
        ticket,
        expected_value,
    )
    if event in record.seen_events:
        # Recognition comes before adapter invocation, including process reloads.
        if (
            record.revision != 2
            or record.pending is not None
            or record.priority_pending is not None
            or record.seen_events != (event,)
            or record.snapshot
            != replace(example_snapshot(), remote_stop=expected_value)
        ):
            raise ClosureConflict("Synthetic replay state does not match.")
        return record
    if not result_available(workspace_id, record):
        raise ClosureConflict("Synthetic result is stale or no longer eligible.")
    value = lifecycle_fake.stop_result(example)
    if value is not expected_value:
        raise ClosureConflict("Synthetic adapter returned an unexpected result.")
    result = observe_synthetic_closure(
        owner=owner, workspace_id=workspace_id, event=event
    )
    if result.disposition is not Disposition.APPLIED:
        raise ClosureConflict("Synthetic observation could not be recorded.")
    return result.record
