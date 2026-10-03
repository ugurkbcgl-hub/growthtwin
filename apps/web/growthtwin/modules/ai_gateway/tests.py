"""Focused checks for the provider-neutral synthetic generation boundary."""

import json
from dataclasses import replace
from unittest.mock import patch

from django.test import SimpleTestCase

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationResult,
    generate_creative_draft,
)
from growthtwin.modules.ai_gateway.ollama import (
    MAX_RESPONSE_BYTES,
    OLLAMA_HOST,
    OLLAMA_PATH,
    OLLAMA_PORT,
    OllamaCreativeGenerator,
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


class StubHTTPResponse:
    def __init__(self, payload):
        self.payload = payload
        self.status = 200

    def read(self, limit=-1):
        body = json.dumps(self.payload).encode("utf-8")
        return body if limit < 0 else body[:limit]


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

    def test_duplicate_variant_angles_are_rejected(self):
        request = SYNTHETIC_CREATIVE_REQUEST
        variants = SyntheticTemplateGenerator().generate(request).variants
        duplicate = replace(
            variants[1],
            angle=f"  {variants[0].angle.lower()}  ",
        )
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

    @patch("growthtwin.modules.ai_gateway.ollama.HTTPConnection")
    def test_ollama_uses_local_structured_request_and_validates_result(
        self, http_connection
    ):
        request = SYNTHETIC_CREATIVE_REQUEST
        result = SyntheticTemplateGenerator().generate(request)
        content = json.dumps(
            {"variants": [variant.as_record() for variant in result.variants]},
            ensure_ascii=False,
        )
        http_connection.return_value.getresponse.return_value = StubHTTPResponse(
            {"message": {"content": content}}
        )

        generated = generate_creative_draft(
            request,
            OllamaCreativeGenerator(model="qwen3:1.7b"),
        )

        self.assertEqual(generated.generator_id, "ollama-qwen3:1.7b")
        self.assertEqual(generated.variants, result.variants)
        http_connection.assert_called_once_with(
            OLLAMA_HOST,
            OLLAMA_PORT,
            timeout=60,
        )
        request_arguments = http_connection.return_value.request.call_args
        self.assertEqual(request_arguments.args[:2], ("POST", OLLAMA_PATH))
        payload = json.loads(request_arguments.kwargs["body"])
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["format"]["required"], ["variants"])
        http_connection.return_value.close.assert_called_once()

    @patch("growthtwin.modules.ai_gateway.ollama.HTTPConnection")
    def test_ollama_never_receives_non_synthetic_requests(self, http_connection):
        request = replace(SYNTHETIC_CREATIVE_REQUEST, synthetic_only=False)

        with self.assertRaises(CreativeGenerationRejected):
            OllamaCreativeGenerator(model="qwen3:1.7b").generate(request)

        http_connection.assert_not_called()

    @patch("growthtwin.modules.ai_gateway.ollama.HTTPConnection")
    def test_ollama_rejects_oversized_brief_before_network_request(
        self, http_connection
    ):
        too_long = replace(
            SYNTHETIC_CREATIVE_REQUEST.brief,
            text="x" * 2001,
        )
        request = replace(SYNTHETIC_CREATIVE_REQUEST, brief=too_long)

        with self.assertRaises(CreativeGenerationRejected):
            OllamaCreativeGenerator(model="qwen3:1.7b").generate(request)

        http_connection.assert_not_called()

    @patch("growthtwin.modules.ai_gateway.ollama.HTTPConnection")
    def test_ollama_malformed_response_fails_closed_without_details(
        self, http_connection
    ):
        http_connection.return_value.getresponse.return_value = StubHTTPResponse(
            {"message": {"content": "not json"}}
        )

        with self.assertRaisesRegex(
            CreativeGenerationRejected, "yanıtı alınamadı veya doğrulanamadı"
        ):
            OllamaCreativeGenerator(model="qwen3:1.7b").generate(
                SYNTHETIC_CREATIVE_REQUEST
            )

    @patch("growthtwin.modules.ai_gateway.ollama.HTTPConnection")
    def test_ollama_oversized_response_fails_closed(self, http_connection):
        response = http_connection.return_value.getresponse.return_value
        response.status = 200
        response.read.return_value = b"x" * (MAX_RESPONSE_BYTES + 1)

        with self.assertRaises(CreativeGenerationRejected):
            OllamaCreativeGenerator(model="qwen3:1.7b").generate(
                SYNTHETIC_CREATIVE_REQUEST
            )

        response.read.assert_called_once_with(MAX_RESPONSE_BYTES + 1)
        http_connection.return_value.close.assert_called_once()

    def test_ollama_rejects_unvalidated_model_name_and_timeout(self):
        with self.assertRaises(ValueError):
            OllamaCreativeGenerator(model="https://example.invalid")
        with self.assertRaises(ValueError):
            OllamaCreativeGenerator(model="qwen3:1.7b", timeout_seconds=0)
