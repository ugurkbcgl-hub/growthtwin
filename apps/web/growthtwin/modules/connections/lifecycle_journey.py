"""Server-owned fixed synthetic fixture; no browser-supplied facts or outcomes."""

from uuid import NAMESPACE_URL, uuid5

from django.db import transaction

from .lifecycle_decision import ClosureSnapshot, LocalSecret, RemoteStop, Step
from .lifecycle_store import (
    ClosureConflict,
    create_synthetic_closure,
    issue_synthetic_ticket,
)
from .lifecycle_ticket import IssuanceDisposition, TicketRequest

EXAMPLES = (
    ("durdurma", "Durdurma doğrulandı örneği"),
    ("belirsiz", "Durdurma doğrulanamadı örneği"),
)


def example_id(workspace_id, kind, example="durdurma"):
    # Stable per-workspace v1 fixture IDs. No IDs from actual accounts/grants.
    if example not in dict(EXAMPLES):
        raise ValueError("Unknown synthetic example.")
    suffix = kind if example == "durdurma" else f"{example}:{kind}"
    return uuid5(
        NAMESPACE_URL, f"growthtwin:closure-journey:v1:{workspace_id}:{suffix}"
    )


def example_snapshot():
    return ClosureSnapshot(
        barrier_confirmed=True,
        recovery_verified=True,
        in_flight=False,
        local_secret=LocalSecret.PRESENT,
        remote_stop=RemoteStop.PENDING,
        stop_authorized=True,
        project_impact_confirmed=True,
    )


@transaction.atomic
def start_example(*, owner, workspace_id, example="durdurma"):
    """One synthetic request and one STOP receipt; duplicate POST resumes it.

    Initial creation and ticket commit together. No evidence/result is invented
    after issuance, and no provider job is queued. There is no reset/retry API.
    """
    record = create_synthetic_closure(
        owner=owner,
        workspace_id=workspace_id,
        connection_id=example_id(workspace_id, "connection", example),
        generation=example_id(workspace_id, "generation", example),
        request_id=example_id(workspace_id, "request", example),
        snapshot=example_snapshot(),
    )
    if record.revision == 0:
        issued = issue_synthetic_ticket(
            owner=owner,
            workspace_id=workspace_id,
            request=TicketRequest(
                record.identity,
                0,
                example_id(workspace_id, "operation", example),
                Step.STOP,
            ),
        )
        if issued.disposition is not IssuanceDisposition.ISSUED:
            raise ClosureConflict("Synthetic example cannot be started safely.")
        record = issued.record
    return record
