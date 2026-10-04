"""Credential-free harness for synthetic, provider-neutral text benchmarks.

This module accepts generator objects from its caller but does not construct
providers, read credentials, persist results, or authorize product use.
"""

import re
import unicodedata
from dataclasses import dataclass
from time import perf_counter
from typing import Iterable

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
    CreativeGenerator,
    ProviderResponseUnverified,
    generate_creative_draft,
)
from growthtwin.modules.ai_gateway.profiles import TextTaskProfile
from growthtwin.modules.content.planning import CampaignBrief

MAX_CANDIDATES = 5
MAX_CASES = 20
MAX_REPETITIONS = 3
MAX_TOTAL_RUNS = 60
MAX_BRIEF_CHARS = 8_000


@dataclass(frozen=True)
class SyntheticTextCase:
    """A synthetic brief and case-specific phrase screens, never proof of safety."""

    case_id: str
    request: CreativeGenerationRequest
    allowed_facts: tuple[str, ...]
    forbidden_claims: tuple[str, ...]


@dataclass(frozen=True)
class TextBenchmarkRecord:
    """One candidate/case/repetition observation for later human review."""

    profile_id: str
    task_id: str
    output_contract_id: str
    minimum_repetitions_per_case: int
    repetitions_requested: int
    candidate_id: str
    case_id: str
    repetition: int
    latency_ms: int
    outcome: str
    failure_kind: str | None
    allowed_facts: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    detected_forbidden_claims: tuple[str, ...]
    manual_review: tuple[tuple[str, int | None], ...]
    variants: tuple[dict[str, str], ...]

    def as_record(self) -> dict[str, object]:
        """Return a JSON-serializable, provider-neutral observation."""

        return {
            "profile_id": self.profile_id,
            "task_id": self.task_id,
            "output_contract_id": self.output_contract_id,
            "minimum_repetitions_per_case": self.minimum_repetitions_per_case,
            "repetitions_requested": self.repetitions_requested,
            "candidate_id": self.candidate_id,
            "case_id": self.case_id,
            "repetition": self.repetition,
            "latency_ms": self.latency_ms,
            "outcome": self.outcome,
            "failure_kind": self.failure_kind,
            "allowed_facts": list(self.allowed_facts),
            "forbidden_claims": list(self.forbidden_claims),
            "detected_forbidden_claims": list(self.detected_forbidden_claims),
            "manual_review": dict(self.manual_review),
            "publishable": False,
            "variants": list(self.variants),
        }


def _normalized_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _detected_forbidden_claims(
    case: SyntheticTextCase,
    variants: tuple[dict[str, str], ...],
) -> tuple[str, ...]:
    generated = " ".join(value for variant in variants for value in variant.values())
    normalized_output = _normalized_text(generated)
    return tuple(
        phrase
        for phrase in case.forbidden_claims
        if _normalized_text(phrase) in normalized_output
    )


def _candidate_id_is_valid(candidate_id: str) -> bool:
    return (
        isinstance(candidate_id, str)
        and re.fullmatch(r"[a-z0-9][a-z0-9._-]{0,79}", candidate_id) is not None
    )


def run_text_benchmark(
    profile: TextTaskProfile,
    cases: Iterable[SyntheticTextCase],
    candidates: Iterable[tuple[str, CreativeGenerator]],
    *,
    repetitions: int = 1,
) -> tuple[TextBenchmarkRecord, ...]:
    """Run bounded synthetic cases through caller-supplied candidate adapters.

    Candidate identifiers are labels only; this function does not know which
    provider they refer to. Output is held in memory and contains no source
    brief text. Exact phrase screens are fixture-specific and not semantic
    claim or policy validation.
    """

    if not isinstance(profile, TextTaskProfile):
        raise ValueError("A supported text task profile is required.")
    cases = tuple(cases)
    candidates = tuple(candidates)
    if not cases or len(cases) > MAX_CASES:
        raise ValueError(f"Provide between 1 and {MAX_CASES} benchmark cases.")
    if not candidates or len(candidates) > MAX_CANDIDATES:
        raise ValueError(f"Provide between 1 and {MAX_CANDIDATES} candidates.")
    if type(repetitions) is not int or not 1 <= repetitions <= MAX_REPETITIONS:
        raise ValueError(f"Repetitions must be from 1 to {MAX_REPETITIONS}.")
    if len(cases) * len(candidates) * repetitions > MAX_TOTAL_RUNS:
        raise ValueError(f"A run may not exceed {MAX_TOTAL_RUNS} candidate calls.")
    if any(not isinstance(case, SyntheticTextCase) for case in cases):
        raise ValueError("Every benchmark case must be a synthetic text case.")
    for case in cases:
        brief = (
            case.request.brief
            if isinstance(case.request, CreativeGenerationRequest)
            else None
        )
        brief_values = (
            (
                brief.text,
                brief.objective,
                brief.objective_label,
                brief.target_audience,
                brief.brand_context,
            )
            if isinstance(brief, CampaignBrief)
            else ()
        )
        if (
            not isinstance(case.case_id, str)
            or re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", case.case_id) is None
            or not brief_values
            or any(not isinstance(value, str) for value in brief_values)
            or any(
                not isinstance(value, str)
                for value in case.allowed_facts + case.forbidden_claims
            )
        ):
            raise ValueError("A benchmark case has invalid synthetic fixture data.")
        if sum(len(value) for value in brief_values) > MAX_BRIEF_CHARS:
            raise ValueError(
                f"Benchmark briefs must be at most {MAX_BRIEF_CHARS} chars."
            )
        if case.request.synthetic_only is not True:
            raise ValueError("Only explicitly synthetic requests can be benchmarked.")

    candidate_ids = [candidate_id for candidate_id, _ in candidates]
    if any(not _candidate_id_is_valid(candidate_id) for candidate_id in candidate_ids):
        raise ValueError("Candidate identifiers must be bounded, non-secret labels.")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("Candidate identifiers must be unique within one run.")

    records = []
    for candidate_id, generator in candidates:
        for case in cases:
            for repetition in range(1, repetitions + 1):
                started = perf_counter()
                try:
                    result = generate_creative_draft(case.request, generator)
                except ProviderResponseUnverified:
                    records.append(
                        TextBenchmarkRecord(
                            profile_id=profile.profile_id,
                            task_id=profile.task_id,
                            output_contract_id=profile.output_contract_id,
                            minimum_repetitions_per_case=profile.minimum_repetitions_per_case,
                            repetitions_requested=repetitions,
                            candidate_id=candidate_id,
                            case_id=case.case_id,
                            repetition=repetition,
                            latency_ms=round((perf_counter() - started) * 1000),
                            outcome="candidate_error",
                            failure_kind="provider_response_unverified",
                            allowed_facts=case.allowed_facts,
                            forbidden_claims=case.forbidden_claims,
                            detected_forbidden_claims=(),
                            manual_review=tuple(
                                (dimension, None)
                                for dimension in profile.manual_review_dimensions
                            ),
                            variants=(),
                        )
                    )
                except CreativeGenerationRejected:
                    records.append(
                        TextBenchmarkRecord(
                            profile_id=profile.profile_id,
                            task_id=profile.task_id,
                            output_contract_id=profile.output_contract_id,
                            minimum_repetitions_per_case=profile.minimum_repetitions_per_case,
                            repetitions_requested=repetitions,
                            candidate_id=candidate_id,
                            case_id=case.case_id,
                            repetition=repetition,
                            latency_ms=round((perf_counter() - started) * 1000),
                            outcome="contract_rejected",
                            failure_kind="generation_contract",
                            allowed_facts=case.allowed_facts,
                            forbidden_claims=case.forbidden_claims,
                            detected_forbidden_claims=(),
                            manual_review=tuple(
                                (dimension, None)
                                for dimension in profile.manual_review_dimensions
                            ),
                            variants=(),
                        )
                    )
                    continue
                except Exception as error:
                    records.append(
                        TextBenchmarkRecord(
                            profile_id=profile.profile_id,
                            task_id=profile.task_id,
                            output_contract_id=profile.output_contract_id,
                            minimum_repetitions_per_case=profile.minimum_repetitions_per_case,
                            repetitions_requested=repetitions,
                            candidate_id=candidate_id,
                            case_id=case.case_id,
                            repetition=repetition,
                            latency_ms=round((perf_counter() - started) * 1000),
                            outcome="candidate_error",
                            failure_kind=type(error).__name__,
                            allowed_facts=case.allowed_facts,
                            forbidden_claims=case.forbidden_claims,
                            detected_forbidden_claims=(),
                            manual_review=tuple(
                                (dimension, None)
                                for dimension in profile.manual_review_dimensions
                            ),
                            variants=(),
                        )
                    )
                    continue

                variants = tuple(variant.as_record() for variant in result.variants)
                records.append(
                    TextBenchmarkRecord(
                        profile_id=profile.profile_id,
                        task_id=profile.task_id,
                        output_contract_id=profile.output_contract_id,
                        minimum_repetitions_per_case=profile.minimum_repetitions_per_case,
                        repetitions_requested=repetitions,
                        candidate_id=candidate_id,
                        case_id=case.case_id,
                        repetition=repetition,
                        latency_ms=round((perf_counter() - started) * 1000),
                        outcome="structured_draft_review_required",
                        failure_kind=None,
                        allowed_facts=case.allowed_facts,
                        forbidden_claims=case.forbidden_claims,
                        detected_forbidden_claims=_detected_forbidden_claims(
                            case, variants
                        ),
                        manual_review=tuple(
                            (dimension, None)
                            for dimension in profile.manual_review_dimensions
                        ),
                        variants=variants,
                    )
                )

    return tuple(records)
