"""No-network tests for the bounded synthetic OpenAI evaluation path."""

import json
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationRequest,
)
from growthtwin.modules.ai_gateway.evaluation_budget import (
    get_evaluation_budget_state,
    reserve_evaluation_cost,
    settle_evaluation_cost,
)
from growthtwin.modules.ai_gateway.openai import (
    MAX_OUTPUT_TOKENS,
    MAX_REQUEST_BYTES,
    OpenAICreativeGenerator,
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


class OpenAIEvaluationBoundaryTests(SimpleTestCase):
    def test_request_is_stateless_structured_and_bounded(self):
        generator = OpenAICreativeGenerator(api_key="synthetic-test-key")

        body = generator.request_body(synthetic_request())
        payload = json.loads(body)

        self.assertLessEqual(len(body), MAX_REQUEST_BYTES)
        self.assertEqual(payload["max_output_tokens"], MAX_OUTPUT_TOKENS)
        self.assertIs(payload["store"], False)
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertNotIn("synthetic-test-key", body.decode("utf-8"))
        self.assertLessEqual(generator.maximum_reserved_cost(body), 0.00128)

    @mock.patch("growthtwin.modules.ai_gateway.openai.HTTPSConnection")
    def test_non_synthetic_request_fails_before_network(self, connection):
        generator = OpenAICreativeGenerator(api_key="synthetic-test-key")

        with self.assertRaises(CreativeGenerationRejected):
            generator.generate(synthetic_request(synthetic_only=False))

        connection.assert_not_called()

    @mock.patch("growthtwin.modules.ai_gateway.openai.HTTPSConnection")
    def test_response_is_validated_and_never_publishable(self, connection_type):
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
                        "status": "completed",
                        "model": "gpt-6-luna",
                        "usage": {"input_tokens": 100, "output_tokens": 50},
                        "output": [
                            {
                                "type": "message",
                                "content": [
                                    {
                                        "type": "output_text",
                                        "text": json.dumps(output),
                                    }
                                ],
                            }
                        ],
                    }
                ).encode(),
            ),
        )
        connection = connection_type.return_value
        connection.getresponse.return_value = response
        generator = OpenAICreativeGenerator(api_key="synthetic-test-key")

        result = generator.generate(synthetic_request())

        connection.request.assert_called_once()
        self.assertEqual(
            connection.request.call_args.args[:2], ("POST", "/v1/responses")
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
        self.assertEqual(generator.last_model, "gpt-6-luna")

    def test_budget_requires_external_hard_limit_confirmation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(
                os.environ,
                {"LOCALAPPDATA": temp_dir},
                clear=True,
            ):
                with self.assertRaisesRegex(RuntimeError, "hard spend limit"):
                    reserve_evaluation_cost(0.001)
                self.assertFalse(
                    (
                        Path(temp_dir) / "GrowthTwin" / "ai-evaluation-budget.sqlite3"
                    ).exists()
                )

    def test_budget_reserves_then_settles_provider_usage(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(
                os.environ,
                {
                    "LOCALAPPDATA": temp_dir,
                    "GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED": "1",
                },
                clear=True,
            ):
                path = reserve_evaluation_cost(0.001)
                settle_evaluation_cost(path, 0.001, 0.00025)
                state = get_evaluation_budget_state(path)

            with closing(sqlite3.connect(path)) as connection:
                with connection as db:
                    row = db.execute(
                        "SELECT cap_usd, spent_usd, reserved_usd FROM budget"
                    ).fetchone()

        self.assertEqual(row, (4.5, 0.00025, 0.0))
        self.assertEqual(state, (4.5, 0.00025, 0.0))
