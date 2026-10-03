"""Provider-neutral, synthetic-only creative generation contracts.

This boundary deliberately has no persistence, HTTP, credential, or publication
behavior. A structurally valid result is still an unreviewed draft.
"""

import re
from dataclasses import dataclass
from typing import Protocol

from growthtwin.modules.content.creative import (
    CREATIVE_BODY_MAX_LENGTH,
    CREATIVE_CTA_MAX_LENGTH,
    CREATIVE_HEADLINE_MAX_LENGTH,
    CreativeVariant,
    source_fingerprint,
)
from growthtwin.modules.content.planning import CampaignBrief

MAX_CREATIVE_VARIANTS = 5
GENERATOR_ID_MAX_LENGTH = 80


@dataclass(frozen=True)
class CreativeGenerationRequest:
    """A brief the caller explicitly classifies as synthetic in this phase.

    This marker is a caller assertion, not a real-data permission check. Keep
    non-synthetic briefs out of this boundary until a separate readiness gate.
    """

    brief: CampaignBrief
    synthetic_only: bool

    @property
    def source_hash(self) -> str:
        """Fingerprint the source without retaining or logging its text."""

        return source_fingerprint(self.brief)


@dataclass(frozen=True)
class CreativeGenerationResult:
    """Validated-shaped copy plus minimal, non-secret generator provenance."""

    generator_id: str
    source_hash: str
    variants: tuple[CreativeVariant, ...]

    @property
    def review_required(self) -> bool:
        """Generation never represents approval or factual/policy review."""

        return True

    @property
    def publishable(self) -> bool:
        """This contract cannot authorize publishing."""

        return False


class CreativeGenerationRejected(ValueError):
    """Raised when a request or provider result does not meet the boundary."""


class CreativeGenerator(Protocol):
    """One replaceable implementation of the bounded creative-generation port."""

    generator_id: str

    def generate(self, request: CreativeGenerationRequest) -> CreativeGenerationResult:
        """Return candidate variants without approving or publishing them."""


def validate_generation_result(
    request: CreativeGenerationRequest,
    result: CreativeGenerationResult,
) -> CreativeGenerationResult:
    """Reject malformed, stale, or unbounded output before a caller can use it."""

    if not isinstance(request, CreativeGenerationRequest):
        raise CreativeGenerationRejected("Üretim isteği geçersiz.")
    if request.synthetic_only is not True:
        raise CreativeGenerationRejected("Yalnızca sentetik istekler kullanılabilir.")
    if not isinstance(result, CreativeGenerationResult):
        raise CreativeGenerationRejected("Üretici yanıt biçimi geçersiz.")
    if not isinstance(result.generator_id, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._:-]{0,79}", result.generator_id
    ):
        raise CreativeGenerationRejected("Üretici kimliği geçersiz.")
    if result.source_hash != request.source_hash:
        raise CreativeGenerationRejected("Üretici yanıtı güncel brief ile eşleşmiyor.")
    if not isinstance(result.variants, tuple) or not (
        1 <= len(result.variants) <= MAX_CREATIVE_VARIANTS
    ):
        raise CreativeGenerationRejected("Reklam metni seçenek sayısı geçersiz.")

    seen_keys: set[str] = set()
    seen_angles: set[str] = set()
    bounds = {
        "key": GENERATOR_ID_MAX_LENGTH,
        "angle": GENERATOR_ID_MAX_LENGTH,
        "headline": CREATIVE_HEADLINE_MAX_LENGTH,
        "body": CREATIVE_BODY_MAX_LENGTH,
        "call_to_action": CREATIVE_CTA_MAX_LENGTH,
    }
    for variant in result.variants:
        if not isinstance(variant, CreativeVariant):
            raise CreativeGenerationRejected("Reklam metni seçeneği geçersiz.")
        for field, maximum in bounds.items():
            value = getattr(variant, field)
            if not isinstance(value, str) or not value.strip() or len(value) > maximum:
                raise CreativeGenerationRejected(
                    f"Reklam metni alanı geçersiz: {field}."
                )
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", variant.key):
            raise CreativeGenerationRejected("Reklam metni anahtarı geçersiz.")
        if variant.key in seen_keys:
            raise CreativeGenerationRejected("Reklam metni anahtarı tekrarlanıyor.")
        seen_keys.add(variant.key)
        normalized_angle = " ".join(variant.angle.split()).casefold()
        if normalized_angle in seen_angles:
            raise CreativeGenerationRejected("Reklam metni açıları tekrarlanıyor.")
        seen_angles.add(normalized_angle)

    return result


def generate_creative_draft(
    request: CreativeGenerationRequest,
    generator: CreativeGenerator,
) -> CreativeGenerationResult:
    """Check the phase boundary before dispatch, then validate provider output."""

    if not isinstance(request, CreativeGenerationRequest):
        raise CreativeGenerationRejected("Üretim isteği geçersiz.")
    if request.synthetic_only is not True:
        raise CreativeGenerationRejected("Yalnızca sentetik istekler kullanılabilir.")
    return validate_generation_result(request, generator.generate(request))
