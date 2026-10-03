"""Controlled synthetic copy assembly from explicitly listed source facts.

This helper emits no creative text of its own: it joins exact-matched source
statements. It cannot discover factual claims omitted from the caller's list.
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from growthtwin.modules.ai_gateway.claim_grounding import (
    ApprovedSourceFact,
    ClaimGroundingVerdict,
    ProposedFactualClaim,
    evaluate_factual_claim,
)

MAX_ASSEMBLED_CLAIMS = 5
MAX_ASSEMBLED_COPY_LENGTH = 1200


class CopyAssemblyRejectionReason(StrEnum):
    """Safe, caller-facing reasons why no composed text was returned."""

    INVALID_INPUT = "invalid_input"
    CLAIMS_NOT_GROUNDED = "claims_not_grounded"
    COPY_TOO_LONG = "copy_too_long"


@dataclass(frozen=True)
class FactBasedCopyDraft:
    """Unreviewed text made only from the supplied exact-matched statements."""

    text: str
    verdicts: tuple[ClaimGroundingVerdict, ...]
    review_required: bool = True
    publishable: bool = False


@dataclass(frozen=True)
class FactBasedCopyRejected:
    """No text is returned if any supplied claim fails its evidence check."""

    verdicts: tuple[ClaimGroundingVerdict, ...]
    reason: CopyAssemblyRejectionReason


def assemble_fact_based_copy(
    claims: tuple[ProposedFactualClaim, ...],
    source_facts: tuple[ApprovedSourceFact, ...],
    *,
    as_of: date,
) -> FactBasedCopyDraft | FactBasedCopyRejected:
    """Join all explicit claims only if each has a valid exact source match.

    The supplied claim list is treated as exhaustive, but the function has no
    way to verify that assertion. This remains a synthetic/offline experiment.
    """

    if (
        not isinstance(claims, tuple)
        or not 1 <= len(claims) <= MAX_ASSEMBLED_CLAIMS
        or not isinstance(source_facts, tuple)
        or type(as_of) is not date
    ):
        return FactBasedCopyRejected(
            verdicts=(), reason=CopyAssemblyRejectionReason.INVALID_INPUT
        )

    verdicts = tuple(
        evaluate_factual_claim(claim, source_facts, as_of=as_of) for claim in claims
    )
    if any(not verdict.matched_exactly for verdict in verdicts):
        return FactBasedCopyRejected(
            verdicts=verdicts,
            reason=CopyAssemblyRejectionReason.CLAIMS_NOT_GROUNDED,
        )

    text = " ".join(claim.text.strip() for claim in claims)
    if len(text) > MAX_ASSEMBLED_COPY_LENGTH:
        return FactBasedCopyRejected(
            verdicts=verdicts,
            reason=CopyAssemblyRejectionReason.COPY_TOO_LONG,
        )

    return FactBasedCopyDraft(text=text, verdicts=verdicts)
