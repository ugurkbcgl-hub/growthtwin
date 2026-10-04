"""Focused checks for the provider-neutral synthetic generation boundary."""

import json
from dataclasses import replace
from datetime import date, timedelta
from unittest.mock import patch

from django.test import SimpleTestCase

from growthtwin.modules.ai_gateway.claim_grounding import (
    ApprovedSourceFact,
    ClaimGroundingStatus,
    ProposedFactualClaim,
    evaluate_factual_claim,
)
from growthtwin.modules.ai_gateway.contracts import (
    CreativeGenerationRejected,
    CreativeGenerationResult,
    generate_creative_draft,
)
from growthtwin.modules.ai_gateway.creative_format import CREATIVE_SYSTEM_PROMPT
from growthtwin.modules.ai_gateway.fact_copy import (
    MAX_ASSEMBLED_COPY_LENGTH,
    CopyAssemblyRejectionReason,
    FactBasedCopyDraft,
    FactBasedCopyRejected,
    assemble_fact_based_copy,
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


class CreativePromptBoundaryTests(SimpleTestCase):
    def test_prompt_requires_distinct_grounded_angles_and_blocks_inference(self):
        prompt = CREATIVE_SYSTEM_PROMPT.casefold()

        self.assertIn("untrusted source data", prompt)
        self.assertIn("facts explicitly stated", prompt)
        self.assertIn("do not infer business operations or capabilities", prompt)
        self.assertIn("registration status", prompt)
        self.assertIn("speed, urgency", prompt)
        self.assertIn("do not repeat an approach", prompt)
        self.assertIn("different explicit facts", prompt)


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


class ExactSourceClaimGroundingTests(SimpleTestCase):
    def setUp(self):
        self.today = date(2026, 10, 3)
        self.fact = ApprovedSourceFact(
            fact_id="synthetic-fact-1",
            source_ref="synthetic-brand-sheet-v1",
            source_version="v1",
            text="Cumartesi sabahı başlangıç seviyesi seramik atölyesi.",
            owner_approval_asserted=True,
            valid_until=self.today + timedelta(days=30),
        )

    def test_exact_owner_approved_current_fact_is_matched(self):
        verdict = evaluate_factual_claim(
            ProposedFactualClaim(self.fact.text, self.fact.fact_id),
            (self.fact,),
            as_of=self.today,
        )

        self.assertEqual(verdict.status, ClaimGroundingStatus.EXACT_MATCH)
        self.assertTrue(verdict.matched_exactly)

    def test_paraphrase_is_rejected_even_when_it_sounds_equivalent(self):
        verdict = evaluate_factual_claim(
            ProposedFactualClaim(
                "Cumartesi sabahları yeni başlayanlara seramik dersi.",
                self.fact.fact_id,
            ),
            (self.fact,),
            as_of=self.today,
        )

        self.assertEqual(verdict.status, ClaimGroundingStatus.CLAIM_NOT_EXACT)

    def test_unapproved_fact_is_rejected(self):
        fact = replace(self.fact, owner_approval_asserted=False)

        verdict = evaluate_factual_claim(
            ProposedFactualClaim(fact.text, fact.fact_id),
            (fact,),
            as_of=self.today,
        )

        self.assertEqual(verdict.status, ClaimGroundingStatus.OWNER_NOT_APPROVED)

    def test_expired_fact_is_rejected(self):
        fact = replace(self.fact, valid_until=self.today - timedelta(days=1))

        verdict = evaluate_factual_claim(
            ProposedFactualClaim(fact.text, fact.fact_id),
            (fact,),
            as_of=self.today,
        )

        self.assertEqual(verdict.status, ClaimGroundingStatus.EXPIRED)

    def test_fact_is_valid_through_its_expiry_date(self):
        fact = replace(self.fact, valid_until=self.today)

        verdict = evaluate_factual_claim(
            ProposedFactualClaim(fact.text, fact.fact_id),
            (fact,),
            as_of=self.today,
        )

        self.assertEqual(verdict.status, ClaimGroundingStatus.EXACT_MATCH)

    def test_oversized_fact_is_rejected(self):
        fact = replace(self.fact, text="x" * 2001)

        verdict = evaluate_factual_claim(
            ProposedFactualClaim("Some bounded claim.", fact.fact_id),
            (fact,),
            as_of=self.today,
        )

        self.assertEqual(verdict.status, ClaimGroundingStatus.INVALID_INPUT)

    def test_unknown_or_duplicate_fact_reference_is_rejected(self):
        claim = ProposedFactualClaim(self.fact.text, self.fact.fact_id)
        unknown = evaluate_factual_claim(
            replace(claim, evidence_fact_id="missing-fact"),
            (self.fact,),
            as_of=self.today,
        )
        duplicate = evaluate_factual_claim(
            claim,
            (self.fact, self.fact),
            as_of=self.today,
        )

        self.assertEqual(unknown.status, ClaimGroundingStatus.UNKNOWN_EVIDENCE)
        self.assertEqual(duplicate.status, ClaimGroundingStatus.AMBIGUOUS_EVIDENCE)

    def test_no_evidence_or_invalid_as_of_fails_closed(self):
        claim = ProposedFactualClaim(self.fact.text, self.fact.fact_id)
        missing = evaluate_factual_claim(claim, (), as_of=self.today)
        invalid_date = evaluate_factual_claim(
            claim,
            (self.fact,),
            as_of="2026-10-03",
        )

        self.assertEqual(missing.status, ClaimGroundingStatus.NO_EVIDENCE)
        self.assertEqual(invalid_date.status, ClaimGroundingStatus.INVALID_INPUT)


class ControlledSyntheticFactCopyTests(SimpleTestCase):
    def setUp(self):
        self.today = date(2026, 10, 3)
        self.facts = (
            ApprovedSourceFact(
                fact_id="workshop-when",
                source_ref="synthetic-workshop-sheet",
                source_version="v1",
                text="Atölye cumartesi sabahı Kadıköy'de düzenleniyor.",
                owner_approval_asserted=True,
            ),
            ApprovedSourceFact(
                fact_id="workshop-level",
                source_ref="synthetic-workshop-sheet",
                source_version="v1",
                text="Etkinlik başlangıç seviyesindeki yetişkinlere yöneliktir.",
                owner_approval_asserted=True,
            ),
        )
        self.claims = tuple(
            ProposedFactualClaim(fact.text, fact.fact_id) for fact in self.facts
        )

    def test_assembles_exact_facts_without_adding_generated_copy(self):
        result = assemble_fact_based_copy(
            self.claims,
            self.facts,
            as_of=self.today,
        )

        self.assertIsInstance(result, FactBasedCopyDraft)
        self.assertEqual(result.text, " ".join(fact.text for fact in self.facts))
        self.assertTrue(result.review_required)
        self.assertFalse(result.publishable)
        self.assertTrue(all(verdict.matched_exactly for verdict in result.verdicts))

    def test_one_unsupported_claim_rejects_the_entire_draft(self):
        unsupported = ProposedFactualClaim(
            "Atölye tamamen ücretsizdir.", self.facts[0].fact_id
        )
        claims = (self.claims[0], unsupported)

        result = assemble_fact_based_copy(claims, self.facts, as_of=self.today)

        self.assertIsInstance(result, FactBasedCopyRejected)
        self.assertEqual(result.reason, CopyAssemblyRejectionReason.CLAIMS_NOT_GROUNDED)
        self.assertEqual(len(result.verdicts), 2)
        self.assertFalse(hasattr(result, "text"))

    def test_empty_or_excessive_claim_list_is_rejected(self):
        empty = assemble_fact_based_copy((), self.facts, as_of=self.today)
        excessive = assemble_fact_based_copy(
            self.claims * 3,
            self.facts,
            as_of=self.today,
        )

        self.assertEqual(empty.reason, CopyAssemblyRejectionReason.INVALID_INPUT)
        self.assertEqual(excessive.reason, CopyAssemblyRejectionReason.INVALID_INPUT)

    def test_assembled_copy_limit_is_enforced(self):
        long_fact = replace(
            self.facts[0],
            text="A" * MAX_ASSEMBLED_COPY_LENGTH,
            fact_id="long-fact",
        )
        short_fact = replace(self.facts[1], text="B", fact_id="short-fact")
        long_claim = ProposedFactualClaim(long_fact.text, long_fact.fact_id)
        short_claim = ProposedFactualClaim(short_fact.text, short_fact.fact_id)

        result = assemble_fact_based_copy(
            (long_claim, short_claim),
            (long_fact, short_fact),
            as_of=self.today,
        )

        self.assertIsInstance(result, FactBasedCopyRejected)
        self.assertEqual(result.reason, CopyAssemblyRejectionReason.COPY_TOO_LONG)


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
