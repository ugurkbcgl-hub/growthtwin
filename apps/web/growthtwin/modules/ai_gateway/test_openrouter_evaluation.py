"""No-network tests for the bounded synthetic OpenRouter evaluation path."""

import json
from unittest import mock

from django.test import SimpleTestCase

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
)
from growthtwin.modules.ai_gateway.openrouter import (
    GEMINI_EVALUATION_MODEL,
    GEMINI_MAX_OUTPUT_TOKENS,
    MAX_OUTPUT_TOKENS,
    MAX_REQUEST_BYTES,
    OPENROUTER_MODEL,
    OpenRouterCreativeGenerator,
)
from growthtwin.modules.content.planning import CampaignBrief


def synthetic_request(*, synthetic_only: bool = True) -> CreativeGenerationRequest:
    return CreativeGenerationRequest(
        brief=CampaignBrief(
            text="Ankara'da sentetik ev bakım hizmeti için teklif talepleri alın.",
            objective="lead_generation",
            objective_label="Teklif talebi",
            target_audience="Ankara'da ev bakımı arayan kişiler",
            brand_context="Başkent Ev Bakım (Sentetik)",
        ),
        synthetic_only=synthetic_only,
    )


class OpenRouterEvaluationBoundaryTests(SimpleTestCase):
    def test_request_is_private_structured_and_bounded(self):
        generator = OpenRouterCreativeGenerator(api_key="synthetic-test-key")

        body = generator.request_body(synthetic_request())
        payload = json.loads(body)

        self.assertLessEqual(len(body), MAX_REQUEST_BYTES)
        self.assertEqual(payload["model"], OPENROUTER_MODEL)
        self.assertEqual(payload["max_tokens"], MAX_OUTPUT_TOKENS)
        self.assertEqual(payload["stream"], False)
        self.assertEqual(payload["response_format"]["type"], "json_schema")
        self.assertTrue(payload["provider"]["zdr"])
        self.assertEqual(payload["provider"]["data_collection"], "deny")
        self.assertTrue(payload["provider"]["require_parameters"])
        self.assertNotIn("synthetic-test-key", body.decode("utf-8"))

    def test_gemini_uses_a_larger_but_per_call_bounded_output_cap(self):
        generator = OpenRouterCreativeGenerator(
            api_key="synthetic-test-key", model=GEMINI_EVALUATION_MODEL
        )
        body = generator.request_body(synthetic_request())
        payload = json.loads(body)

        self.assertEqual(generator.max_output_tokens, GEMINI_MAX_OUTPUT_TOKENS)
        self.assertEqual(payload["max_tokens"], GEMINI_MAX_OUTPUT_TOKENS)
        self.assertLessEqual(generator.maximum_reserved_cost(body), 0.01)

    @mock.patch("growthtwin.modules.ai_gateway.openrouter.HTTPSConnection")
    def test_non_synthetic_request_fails_before_network(self, connection):
        generator = OpenRouterCreativeGenerator(api_key="synthetic-test-key")

        with self.assertRaises(CreativeGenerationRejected):
            generator.generate(synthetic_request(synthetic_only=False))

        connection.assert_not_called()

    @mock.patch("growthtwin.modules.ai_gateway.openrouter.HTTPSConnection")
    def test_response_cost_and_content_are_validated(self, connection_type):
        output = {
            "variants": [
                {
                    "key": "local-service",
                    "angle": "Local expertise",
                    "headline": "Ev bakım desteği",
                    "body": "Ankara'da ev bakım hizmeti için bilgi alın.",
                    "call_to_action": "Bilgi alın",
                }
            ]
        }
        response = mock.Mock(
            status=200,
            read=mock.Mock(
                return_value=json.dumps(
                    {
                        "model": OPENROUTER_MODEL,
                        "provider": "OpenAI",
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {"content": json.dumps(output)},
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 100,
                            "completion_tokens": 50,
                            "cost": 0.000035,
                        },
                    }
                ).encode(),
            ),
        )
        connection = connection_type.return_value
        connection.getresponse.return_value = response
        generator = OpenRouterCreativeGenerator(api_key="synthetic-test-key")

        result = generator.generate(synthetic_request())

        connection.request.assert_called_once()
        self.assertEqual(
            connection.request.call_args.args[:2],
            ("POST", "/api/v1/chat/completions"),
        )
        self.assertEqual(
            connection.request.call_args.kwargs["headers"]["Authorization"],
            "Bearer synthetic-test-key",
        )
        self.assertTrue(result.review_required)
        self.assertFalse(result.publishable)
        self.assertEqual(
            generator.last_usage, {"input_tokens": 100, "output_tokens": 50}
        )
        self.assertEqual(generator.last_cost_usd, 0.000035)
        self.assertEqual(generator.last_model, OPENROUTER_MODEL)
        self.assertEqual(generator.last_provider, "OpenAI")

    @mock.patch("growthtwin.modules.ai_gateway.openrouter.HTTPSConnection")
    def test_cost_over_reservation_is_rejected(self, connection_type):
        response = mock.Mock(
            status=200,
            read=mock.Mock(
                return_value=json.dumps(
                    {
                        "model": OPENROUTER_MODEL,
                        "choices": [
                            {
                                "finish_reason": "stop",
                                "message": {"content": json.dumps({"variants": []})},
                            }
                        ],
                        "usage": {
                            "prompt_tokens": 100,
                            "completion_tokens": 50,
                            "cost": 0.01,
                        },
                    }
                ).encode(),
            ),
        )
        connection = connection_type.return_value
        connection.getresponse.return_value = response
        generator = OpenRouterCreativeGenerator(api_key="synthetic-test-key")

        with self.assertRaises(CreativeGenerationRejected):
            generator.generate(synthetic_request())
