"""Pure, caller-supplied sector/channel eligibility checks for synthetic drafts."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from urllib.parse import urlsplit


class EligibilityOutcome(StrEnum):
    """Category and channel state; none of these values authorizes dispatch."""

    ELIGIBLE = "eligible"
    RESTRICTED = "restricted"
    NOT_SUPPORTED = "not_supported"
    NEEDS_REVIEW = "needs_review"


class EligibilityReason(StrEnum):
    """Stable reason codes for an unresolved or blocked eligibility result."""

    RULES_MISSING = "eligibility_rules_missing"
    RULE_METADATA_INVALID = "eligibility_rule_metadata_missing_or_invalid"
    EVALUATION_DATE_INVALID = "eligibility_evaluation_date_invalid"
    RULE_REVIEW_DATE_IN_FUTURE = "eligibility_rule_review_date_in_future"
    RULE_STALE = "eligibility_rule_review_expired"
    OUTCOME_UNKNOWN = "eligibility_outcome_unknown"
    RULE_REQUIRES_REVIEW = "eligibility_rule_requires_review"
    OFFER_NOT_SUPPORTED = "eligibility_offer_not_supported"
    CONDITIONS_UNKNOWN = "eligibility_conditions_unknown"
    CONDITIONS_NOT_MET = "eligibility_conditions_not_met"


SYNTHETIC_ELIGIBILITY_VERSION = "synthetic-sector-eligibility.v1"


@dataclass(frozen=True)
class SyntheticEligibilityRule:
    """A claimed, dated rule assessment supplied by the local synthetic caller.

    This value is not evidence authentication: callers can claim a source,
    review date, outcome, and condition result. It has no network or clock access.
    """

    jurisdiction: str | None = None
    channel: str | None = None
    category: str | None = None
    outcome: EligibilityOutcome | None = None
    source_url: str | None = None
    rule_version: str | None = None
    reviewed_on: date | None = None
    review_due_on: date | None = None
    conditions_satisfied: bool | None = None


@dataclass(frozen=True)
class SyntheticEligibilityDecision:
    """Combined policy state for local review, never a publish permission."""

    outcome: EligibilityOutcome
    reasons: tuple[EligibilityReason, ...]
    policy_version: str = SYNTHETIC_ELIGIBILITY_VERSION
    evaluated_rules: tuple[SyntheticEligibilityRule, ...] = ()
    live_dispatch_authorized: bool = False


def _metadata_is_valid(rule: SyntheticEligibilityRule) -> bool:
    if not all(
        isinstance(value, str) and value.strip()
        for value in (
            rule.jurisdiction,
            rule.channel,
            rule.category,
            rule.rule_version,
        )
    ):
        return False
    if not isinstance(rule.source_url, str):
        return False
    try:
        parsed_url = urlsplit(rule.source_url)
    except ValueError:
        return False
    if (
        parsed_url.scheme != "https"
        or not parsed_url.hostname
        or parsed_url.username is not None
        or parsed_url.password is not None
    ):
        return False
    if type(rule.reviewed_on) is not date or type(rule.review_due_on) is not date:
        return False
    return rule.review_due_on >= rule.reviewed_on


def _assess_rule(
    rule: SyntheticEligibilityRule, *, evaluated_on: date
) -> tuple[EligibilityOutcome, tuple[EligibilityReason, ...]]:
    reasons: list[EligibilityReason] = []
    if not _metadata_is_valid(rule):
        return (
            EligibilityOutcome.NEEDS_REVIEW,
            (EligibilityReason.RULE_METADATA_INVALID,),
        )
    if evaluated_on > rule.review_due_on:
        reasons.append(EligibilityReason.RULE_STALE)
    if rule.reviewed_on > evaluated_on:
        reasons.append(EligibilityReason.RULE_REVIEW_DATE_IN_FUTURE)
    if not isinstance(rule.outcome, EligibilityOutcome):
        reasons.append(EligibilityReason.OUTCOME_UNKNOWN)
    if reasons:
        return (EligibilityOutcome.NEEDS_REVIEW, tuple(reasons))
    if rule.outcome is EligibilityOutcome.NOT_SUPPORTED:
        return (
            EligibilityOutcome.NOT_SUPPORTED,
            (EligibilityReason.OFFER_NOT_SUPPORTED,),
        )
    if rule.outcome is EligibilityOutcome.NEEDS_REVIEW:
        return (
            EligibilityOutcome.NEEDS_REVIEW,
            (EligibilityReason.RULE_REQUIRES_REVIEW,),
        )
    if rule.conditions_satisfied is not True:
        reason = (
            EligibilityReason.CONDITIONS_UNKNOWN
            if rule.conditions_satisfied is not False
            else EligibilityReason.CONDITIONS_NOT_MET
        )
        return (EligibilityOutcome.NEEDS_REVIEW, (reason,))
    return (rule.outcome, ())


def evaluate_synthetic_eligibility(
    rules: tuple[SyntheticEligibilityRule, ...], *, evaluated_on: date | None
) -> SyntheticEligibilityDecision:
    """Combine independent law/platform rule claims using fail-closed precedence.

    Callers must supply the evaluation date. Any unsupported rule stops; absent,
    stale, or unmet/unknown conditions pause; a restriction remains visible even
    when its conditions are satisfied. Eligible means category eligibility only.
    """

    if type(evaluated_on) is not date:
        return SyntheticEligibilityDecision(
            outcome=EligibilityOutcome.NEEDS_REVIEW,
            reasons=(EligibilityReason.EVALUATION_DATE_INVALID,),
        )
    if not isinstance(rules, tuple) or any(
        not isinstance(rule, SyntheticEligibilityRule) for rule in rules
    ):
        return SyntheticEligibilityDecision(
            outcome=EligibilityOutcome.NEEDS_REVIEW,
            reasons=(EligibilityReason.RULE_METADATA_INVALID,),
        )
    if not rules:
        return SyntheticEligibilityDecision(
            outcome=EligibilityOutcome.NEEDS_REVIEW,
            reasons=(EligibilityReason.RULES_MISSING,),
        )

    assessments = tuple(_assess_rule(rule, evaluated_on=evaluated_on) for rule in rules)
    outcomes = tuple(outcome for outcome, _reasons in assessments)
    if EligibilityOutcome.NOT_SUPPORTED in outcomes:
        combined = EligibilityOutcome.NOT_SUPPORTED
    elif EligibilityOutcome.NEEDS_REVIEW in outcomes:
        combined = EligibilityOutcome.NEEDS_REVIEW
    elif EligibilityOutcome.RESTRICTED in outcomes:
        combined = EligibilityOutcome.RESTRICTED
    else:
        combined = EligibilityOutcome.ELIGIBLE

    reasons = tuple(
        dict.fromkeys(reason for _outcome, items in assessments for reason in items)
    )
    return SyntheticEligibilityDecision(
        outcome=combined,
        reasons=reasons,
        evaluated_rules=rules,
    )
