"""Deterministic local fixtures. No Google/network/credential integration."""

from .lifecycle_decision import RemoteStop


def stop_result(example):
    """The selected fixed example is not evidence supplied by an advertiser."""
    outcomes = {
        "durdurma": RemoteStop.CONFIRMED,
        "belirsiz": RemoteStop.UNCERTAIN,
    }
    if example not in outcomes:
        raise ValueError("Unknown synthetic example.")
    return outcomes[example]


def new_work_result(kind):
    """No payload or remote side effect: simulate only three fixed work kinds."""
    if kind not in {"create", "refresh", "callback_save"}:
        raise ValueError("Unknown synthetic work kind.")
    return kind
