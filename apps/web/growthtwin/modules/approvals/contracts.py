"""Fail-closed, side-effect-free policy checks for synthetic campaign actions."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PolicyReason(StrEnum):
    """Stable reason codes for a blocked synthetic action review."""

    LIVE_ENVIRONMENT = "live_environment_not_supported"
    AUTHORIZATION_MISSING = "advertiser_authorization_missing"
    DESTINATION_MISSING = "destination_authorization_missing"
    CHANNEL_NOT_ALLOWED = "channel_not_allowed_or_unknown"
    CONTENT_NOT_APPROVED = "content_not_approved_or_unknown"
    POLICY_STALE = "policy_state_stale_or_unknown"
    STOP_REQUESTED = "stop_requested_or_unknown"
    BUDGET_MISSING = "budget_state_missing_or_invalid"
    CAMPAIGN_CAP_EXCEEDED = "campaign_cap_exceeded"
    ACCOUNT_CAP_EXCEEDED = "account_cap_exceeded"
    CURRENCY_INVALID = "currency_invalid"
    SCHEDULE_MISSING = "schedule_missing_or_invalid"
    OUTSIDE_SCHEDULE = "action_outside_schedule"


@dataclass(frozen=True)
class SyntheticActionEvidence:
    """Caller-supplied facts for a local review; never a live authorization."""

    advertiser_authorized: bool | None = None
    destination_authorized: bool | None = None
    channel_allowed: bool | None = None
    content_approved: bool | None = None
    policy_current: bool | None = None
    stop_requested: bool | None = None
    campaign_cap_minor: int | None = None
    account_cap_minor: int | None = None
    account_committed_minor: int | None = None
    requested_minor: int | None = None
    currency: str | None = None
    action_at: datetime | None = None
    campaign_starts_at: datetime | None = None
    campaign_ends_at: datetime | None = None
    synthetic_environment: bool = True


@dataclass(frozen=True)
class SyntheticPolicyDecision:
    """Precondition result for a synthetic preview, not permission to dispatch."""

    eligible_for_synthetic_review: bool
    reasons: tuple[PolicyReason, ...]
    live_dispatch_authorized: bool = False


def evaluate_synthetic_action(
    evidence: SyntheticActionEvidence,
) -> SyntheticPolicyDecision:
    """Check supplied synthetic evidence and fail closed on missing or unsafe facts."""

    reasons: list[PolicyReason] = []
    if not evidence.synthetic_environment:
        reasons.append(PolicyReason.LIVE_ENVIRONMENT)

    required_booleans = (
        (evidence.advertiser_authorized, PolicyReason.AUTHORIZATION_MISSING),
        (evidence.destination_authorized, PolicyReason.DESTINATION_MISSING),
        (evidence.channel_allowed, PolicyReason.CHANNEL_NOT_ALLOWED),
        (evidence.content_approved, PolicyReason.CONTENT_NOT_APPROVED),
        (evidence.policy_current, PolicyReason.POLICY_STALE),
    )
    for value, reason in required_booleans:
        if value is not True:
            reasons.append(reason)
    if evidence.stop_requested is not False:
        reasons.append(PolicyReason.STOP_REQUESTED)

    amounts = (
        evidence.campaign_cap_minor,
        evidence.account_cap_minor,
        evidence.account_committed_minor,
        evidence.requested_minor,
    )
    if any(value is None or value < 0 for value in amounts) or (
        evidence.requested_minor is not None and evidence.requested_minor == 0
    ):
        reasons.append(PolicyReason.BUDGET_MISSING)
    else:
        assert evidence.campaign_cap_minor is not None
        assert evidence.account_cap_minor is not None
        assert evidence.account_committed_minor is not None
        assert evidence.requested_minor is not None
        if evidence.requested_minor > evidence.campaign_cap_minor:
            reasons.append(PolicyReason.CAMPAIGN_CAP_EXCEEDED)
        if (
            evidence.account_committed_minor + evidence.requested_minor
            > evidence.account_cap_minor
        ):
            reasons.append(PolicyReason.ACCOUNT_CAP_EXCEEDED)

    if (
        evidence.currency is None
        or len(evidence.currency) != 3
        or not evidence.currency.isascii()
        or not evidence.currency.isalpha()
        or evidence.currency != evidence.currency.upper()
    ):
        reasons.append(PolicyReason.CURRENCY_INVALID)

    schedule = (
        evidence.action_at,
        evidence.campaign_starts_at,
        evidence.campaign_ends_at,
    )
    if any(value is None or value.utcoffset() is None for value in schedule):
        reasons.append(PolicyReason.SCHEDULE_MISSING)
    else:
        assert evidence.action_at is not None
        assert evidence.campaign_starts_at is not None
        assert evidence.campaign_ends_at is not None
        if (
            evidence.campaign_ends_at < evidence.campaign_starts_at
            or evidence.action_at < evidence.campaign_starts_at
            or evidence.action_at > evidence.campaign_ends_at
        ):
            reasons.append(PolicyReason.OUTSIDE_SCHEDULE)

    unique_reasons = tuple(dict.fromkeys(reasons))
    return SyntheticPolicyDecision(
        eligible_for_synthetic_review=not unique_reasons,
        reasons=unique_reasons,
    )
