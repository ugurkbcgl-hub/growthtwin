"""Deterministic adapter and fixture for the synthetic creative boundary."""

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
    CreativeGenerationResult,
    generate_creative_draft,
    validate_generation_result,
)
from growthtwin.modules.content.creative import draft_creative_variants
from growthtwin.modules.content.planning import CampaignBrief

SYNTHETIC_CREATIVE_REQUEST = CreativeGenerationRequest(
    brief=CampaignBrief(
        text="Ankara'da ev bakım ve onarım hizmeti için teklif talepleri alın.",
        objective="lead_generation",
        objective_label="Teklif talebi",
        target_audience="Ankara",
        brand_context="Başkent Ev Bakım (Sentetik)",
    ),
    synthetic_only=True,
)


class SyntheticTemplateGenerator:
    """Exercise the gateway with local deterministic copy, without AI calls."""

    generator_id = "synthetic-template-v1"

    def generate(self, request: CreativeGenerationRequest) -> CreativeGenerationResult:
        if request.synthetic_only is not True:
            raise CreativeGenerationRejected(
                "Sentetik şablon üreticisi yalnızca sentetik veri kabul eder."
            )
        result = CreativeGenerationResult(
            generator_id=self.generator_id,
            source_hash=request.source_hash,
            variants=draft_creative_variants(request.brief),
        )
        return validate_generation_result(request, result)


def generate_synthetic_creative_draft(brief: CampaignBrief) -> CreativeGenerationResult:
    """Run the local fixture through the same boundary a later provider uses."""

    request = CreativeGenerationRequest(brief=brief, synthetic_only=True)
    return generate_creative_draft(request, SyntheticTemplateGenerator())
