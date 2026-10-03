"""Persistence-free exact-source matching for synthetic claim experiments.

An exact match proves only that text matches a caller-supplied source record
whose owner-approval flag is asserted.
It does not establish truth, completeness, legal compliance, or publication
eligibility. The caller must inventory every factual claim separately.
"""

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

FACT_ID_MAX_LENGTH = 80
SOURCE_REF_MAX_LENGTH = 240
SOURCE_VERSION_MAX_LENGTH = 80
SOURCE_FACT_TEXT_MAX_LENGTH = 2000


class ClaimGroundingStatus(StrEnum):
    """A deliberately small, fail-closed claim/source matching result."""

    EXACT_MATCH = "exact_match"
    INVALID_INPUT = "invalid_input"
    NO_EVIDENCE = "no_evidence"
    UNKNOWN_EVIDENCE = "unknown_evidence"
    AMBIGUOUS_EVIDENCE = "ambiguous_evidence"
    OWNER_NOT_APPROVED = "owner_not_approved"
    EXPIRED = "expired"
    CLAIM_NOT_EXACT = "claim_not_exact"


@dataclass(frozen=True)
class ApprovedSourceFact:
    """An in-memory fact record with a caller-asserted verbatim-copy permit."""

    fact_id: str
    source_ref: str
    source_version: str
    text: str
    owner_approval_asserted: bool
    valid_until: date | None = None


@dataclass(frozen=True)
class ProposedFactualClaim:
    """One claim and its untrusted reference to a single source fact."""

    text: str
    evidence_fact_id: str


@dataclass(frozen=True)
class ClaimGroundingVerdict:
    """Non-persistent result; it never means the claim is true or compliant."""

    status: ClaimGroundingStatus
    evidence_fact_id: str | None = None

    @property
    def matched_exactly(self) -> bool:
        """Only full-text equality to an approved, current fact is accepted."""

        return self.status is ClaimGroundingStatus.EXACT_MATCH


def _normalized_exact_text(value: str) -> str:
    """Normalize Unicode compatibility forms and whitespace, preserving words."""

    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def evaluate_factual_claim(
    claim: ProposedFactualClaim,
    source_facts: tuple[ApprovedSourceFact, ...],
    *,
    as_of: date,
) -> ClaimGroundingVerdict:
    """Check one listed claim against exactly one owner-approved source fact.

    This does not find claims in surrounding copy, verify the source's truth,
    or determine whether an approved fact is legal for an ad or channel.
    """

    if (
        not isinstance(claim, ProposedFactualClaim)
        or not isinstance(source_facts, tuple)
        or type(as_of) is not date
    ):
        return ClaimGroundingVerdict(ClaimGroundingStatus.INVALID_INPUT)
    if (
        not isinstance(claim.text, str)
        or not claim.text.strip()
        or len(claim.text) > SOURCE_FACT_TEXT_MAX_LENGTH
        or not isinstance(claim.evidence_fact_id, str)
        or not claim.evidence_fact_id.strip()
        or len(claim.evidence_fact_id) > FACT_ID_MAX_LENGTH
    ):
        return ClaimGroundingVerdict(ClaimGroundingStatus.INVALID_INPUT)
    if not source_facts:
        return ClaimGroundingVerdict(ClaimGroundingStatus.NO_EVIDENCE)
    if any(not isinstance(fact, ApprovedSourceFact) for fact in source_facts):
        return ClaimGroundingVerdict(ClaimGroundingStatus.INVALID_INPUT)

    matching = tuple(
        fact for fact in source_facts if fact.fact_id == claim.evidence_fact_id
    )
    if not matching:
        return ClaimGroundingVerdict(
            ClaimGroundingStatus.UNKNOWN_EVIDENCE,
            evidence_fact_id=claim.evidence_fact_id,
        )
    if len(matching) != 1:
        return ClaimGroundingVerdict(
            ClaimGroundingStatus.AMBIGUOUS_EVIDENCE,
            evidence_fact_id=claim.evidence_fact_id,
        )

    fact = matching[0]
    if (
        not re.fullmatch(
            rf"[A-Za-z0-9][A-Za-z0-9._:-]{{0,{FACT_ID_MAX_LENGTH - 1}}}",
            fact.fact_id,
        )
        or not isinstance(fact.source_ref, str)
        or not fact.source_ref.strip()
        or len(fact.source_ref) > SOURCE_REF_MAX_LENGTH
        or not isinstance(fact.source_version, str)
        or not fact.source_version.strip()
        or len(fact.source_version) > SOURCE_VERSION_MAX_LENGTH
        or not isinstance(fact.text, str)
        or not fact.text.strip()
        or len(fact.text) > SOURCE_FACT_TEXT_MAX_LENGTH
        or type(fact.owner_approval_asserted) is not bool
        or (fact.valid_until is not None and type(fact.valid_until) is not date)
    ):
        return ClaimGroundingVerdict(
            ClaimGroundingStatus.INVALID_INPUT,
            evidence_fact_id=fact.fact_id,
        )
    if not fact.owner_approval_asserted:
        return ClaimGroundingVerdict(
            ClaimGroundingStatus.OWNER_NOT_APPROVED,
            evidence_fact_id=fact.fact_id,
        )
    if fact.valid_until is not None and fact.valid_until < as_of:
        return ClaimGroundingVerdict(
            ClaimGroundingStatus.EXPIRED,
            evidence_fact_id=fact.fact_id,
        )
    if _normalized_exact_text(claim.text) != _normalized_exact_text(fact.text):
        return ClaimGroundingVerdict(
            ClaimGroundingStatus.CLAIM_NOT_EXACT,
            evidence_fact_id=fact.fact_id,
        )
    return ClaimGroundingVerdict(
        ClaimGroundingStatus.EXACT_MATCH,
        evidence_fact_id=fact.fact_id,
    )
