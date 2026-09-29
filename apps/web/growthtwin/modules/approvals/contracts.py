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
    EVIDENCE_SOURCE_INVALID = "evidence_source_missing_or_unknown"
    EVIDENCE_TIME_MISSING = "evidence_observation_time_missing"
    EVIDENCE_TIME_INVALID = "evidence_observation_time_not_timezone_aware"


class SyntheticEvidenceSource(StrEnum):
    """Known labels for evidence origins used only by local synthetic flows."""

    FIXED_SAMPLE = "fixed_sample"
    TEST_FIXTURE = "test_fixture"


class SyntheticPolicyRule(StrEnum):
    """Stable identifiers for checks run by the synthetic policy evaluator."""

    ENVIRONMENT = "environment_is_synthetic"
    AUTHORIZATION = "required_authorizations_present"
    CHANNEL_AND_CONTENT = "channel_and_content_allowed"
    POLICY_AND_STOP = "policy_current_and_stop_clear"
    BUDGET = "campaign_and_account_caps_respected"
    CURRENCY = "currency_valid"
    EVIDENCE_METADATA = "evidence_source_and_observation_time_valid"
    SCHEDULE = "action_within_campaign_schedule"


SYNTHETIC_POLICY_VERSION = "synthetic-action-policy.v1"
SYNTHETIC_POLICY_RULES = tuple(SyntheticPolicyRule)


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
    evidence_source: SyntheticEvidenceSource | None = None
    evidence_observed_at: datetime | None = None
    synthetic_environment: bool = True


@dataclass(frozen=True)
class SyntheticPolicyDecision:
    """Synthetic check result and unverified metadata; never dispatch permission."""

    eligible_for_synthetic_review: bool
    reasons: tuple[PolicyReason, ...]
    policy_version: str = SYNTHETIC_POLICY_VERSION
    evaluated_rule_ids: tuple[SyntheticPolicyRule, ...] = SYNTHETIC_POLICY_RULES
    evidence_source: SyntheticEvidenceSource | None = None
    evidence_observed_at: datetime | None = None
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

    if not isinstance(evidence.evidence_source, SyntheticEvidenceSource):
        reasons.append(PolicyReason.EVIDENCE_SOURCE_INVALID)

    observed_at = evidence.evidence_observed_at
    if observed_at is None:
        reasons.append(PolicyReason.EVIDENCE_TIME_MISSING)
    elif not isinstance(observed_at, datetime) or observed_at.utcoffset() is None:
        reasons.append(PolicyReason.EVIDENCE_TIME_INVALID)

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
        evidence_source=(
            evidence.evidence_source
            if isinstance(evidence.evidence_source, SyntheticEvidenceSource)
            else None
        ),
        evidence_observed_at=(
            observed_at
            if isinstance(observed_at, datetime) and observed_at.utcoffset() is not None
            else None
        ),
    )
