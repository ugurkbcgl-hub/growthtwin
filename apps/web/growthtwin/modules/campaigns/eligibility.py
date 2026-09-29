"""Synthetic Google Search category state shown in the campaign preview."""

from datetime import date

from growthtwin.modules.approvals.eligibility import (
    EligibilityOutcome,
    SyntheticEligibilityDecision,
    SyntheticEligibilityRule,
    evaluate_synthetic_eligibility,
)

MATRIX_SOURCE = (
    "https://github.com/ugurkbcgl-hub/growthtwin/blob/main/"
    "docs/product/google-search-turkiye-sector-eligibility.md"
)
SYNTHETIC_HOME_MAINTENANCE_RULE = SyntheticEligibilityRule(
    jurisdiction="TR",
    channel="google_ads.search",
    category="local_service.home_maintenance",
    outcome=EligibilityOutcome.ELIGIBLE,
    source_url=MATRIX_SOURCE,
    rule_version="matrix-2026-09-29",
    reviewed_on=date(2026, 9, 29),
    review_due_on=date(2026, 10, 29),
    conditions_satisfied=True,
)


def synthetic_campaign_eligibility_preview(
    *, evaluated_on: date
) -> SyntheticEligibilityDecision:
    """Return only the dated local home-maintenance scenario assessment."""

    return evaluate_synthetic_eligibility(
        (SYNTHETIC_HOME_MAINTENANCE_RULE,),
        evaluated_on=evaluated_on,
    )
