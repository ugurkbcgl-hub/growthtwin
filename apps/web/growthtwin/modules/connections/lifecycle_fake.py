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
