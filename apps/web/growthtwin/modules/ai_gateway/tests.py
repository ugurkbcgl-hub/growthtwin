"""Focused checks for the provider-neutral synthetic generation boundary."""

from dataclasses import replace

from django.test import SimpleTestCase

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationResult,
    generate_creative_draft,
)
from growthtwin.modules.ai_gateway.synthetic import (
    SYNTHETIC_CREATIVE_REQUEST,
    SyntheticTemplateGenerator,
)


class FixedGenerator:
    generator_id = "fixture"

    def __init__(self, result):
        self.result = result

    def generate(self, request):
        return self.result


class CreativeGenerationBoundaryTests(SimpleTestCase):
    def test_synthetic_fixture_generates_bounded_unreviewed_drafts(self):
        result = generate_creative_draft(
            SYNTHETIC_CREATIVE_REQUEST,
            SyntheticTemplateGenerator(),
        )

        self.assertEqual(result.generator_id, "synthetic-template-v1")
        self.assertEqual(len(result.variants), 3)
        self.assertTrue(result.review_required)
        self.assertFalse(result.publishable)

    def test_non_synthetic_request_is_rejected_before_generator_call(self):
        class MustNotRun:
            called = False

            def generate(self, request):
                self.called = True
                raise AssertionError("Generator must not receive non-synthetic input")

        generator = MustNotRun()
        request = replace(SYNTHETIC_CREATIVE_REQUEST, synthetic_only=False)

        with self.assertRaises(CreativeGenerationRejected):
            generate_creative_draft(request, generator)

        self.assertFalse(generator.called)

    def test_stale_source_result_is_rejected(self):
        request = SYNTHETIC_CREATIVE_REQUEST
        result = SyntheticTemplateGenerator().generate(request)
        stale = replace(result, source_hash="0" * 64)

        with self.assertRaises(CreativeGenerationRejected):
            generate_creative_draft(request, FixedGenerator(stale))

    def test_duplicate_variant_keys_are_rejected(self):
        request = SYNTHETIC_CREATIVE_REQUEST
        variants = SyntheticTemplateGenerator().generate(request).variants
        duplicate = replace(variants[1], key=variants[0].key)
        result = CreativeGenerationResult(
            generator_id="fixture",
            source_hash=request.source_hash,
            variants=(variants[0], duplicate),
        )

        with self.assertRaises(CreativeGenerationRejected):
            generate_creative_draft(request, FixedGenerator(result))

    def test_overlong_copy_is_rejected(self):
        request = SYNTHETIC_CREATIVE_REQUEST
        result = SyntheticTemplateGenerator().generate(request)
        overlong = replace(result.variants[0], headline="x" * 81)
        malformed = replace(result, variants=(overlong,))

        with self.assertRaises(CreativeGenerationRejected):
            generate_creative_draft(request, FixedGenerator(malformed))

    def test_unexpected_variant_type_is_rejected(self):
        request = SYNTHETIC_CREATIVE_REQUEST
        result = CreativeGenerationResult(
            generator_id="fixture",
            source_hash=request.source_hash,
            variants=("untrusted output",),
        )

        with self.assertRaises(CreativeGenerationRejected):
            generate_creative_draft(request, FixedGenerator(result))
