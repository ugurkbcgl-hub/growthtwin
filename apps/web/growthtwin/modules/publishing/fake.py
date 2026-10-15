"""Deterministic in-process publishing rehearsal; no transport or real metrics."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SyntheticReceipt:
    state: str
    receipt: str


def start_rehearsal(operation_id: UUID, *, fail: bool = False) -> SyntheticReceipt:
    state = "failed" if fail else "running"
    return SyntheticReceipt(state, f"synthetic:{operation_id}:{state}")


def stop_rehearsal(operation_id: UUID) -> SyntheticReceipt:
    return SyntheticReceipt("stopped", f"synthetic:{operation_id}:stopped")
