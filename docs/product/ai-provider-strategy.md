# AI provider combinations and selection plan

**Status:** Recommended architecture and evaluation shortlist; no provider or
model is approved for production. Reviewed against official vendor material on
2026-10-03. Prices, model IDs, terms, regions, and availability change and must
be checked again before use.

## Decision in brief

GrowthTwin should not depend on Ollama, a workstation GPU, or one AI vendor.
Keep the Django AI gateway as the application-owned control point and route
separate tasks to replaceable hosted provider adapters. Select the provider
per task from measured synthetic evaluations. A provider outage may use only a
pre-approved alternative that passes the same data-class, safety, and cost
rules; otherwise pause with a clear status. Local inference can remain an
optional developer experiment, never a runtime requirement.

The recommended **evaluation combination** is:

1. **Campaign reasoning and copy:** compare current production API models from
   OpenAI, Google Gemini, and Anthropic on the same synthetic briefs. Test a
   strong quality candidate and a lower-cost candidate from each vendor where
   the API supports both. No vendor wins by reputation or a generic benchmark.
2. **Image generation and editing:** compare Google's current Gemini image
   endpoint with OpenAI's current image endpoint. Evaluate brand fidelity,
   exact dimensions, editability, legibility, unwanted text, and cost per
   accepted asset. Keep layout/text overlays deterministic in GrowthTwin where
   possible.
3. **Short video generation:** compare Google's current Veo API with OpenAI's
   current video API using synthetic scenes and no supplied customer assets.
   A video endpoint with incompatible retention controls is not eligible for
   confidential customer material unless separately approved for that data.
4. **Document and existing-asset understanding:** initially extract and
   classify using isolated, deterministic parsers where feasible; send only
   the minimum necessary synthetic sample to multimodal providers during
   evaluation. Real document intake remains closed under ADR-0009 until
   storage, permissions, deletion, processing location, and provider terms are
   approved.
5. **Quality review:** use application rules and source-linked claim checks as
   the authority. A second model may flag issues or rank candidates, but its
   agreement is not proof of truth, legal compliance, copyright clearance, or
   platform-policy approval.

This is a shortlist and architecture recommendation, not an API integration,
vendor contract, production selection, or authorization to spend. Existing
approved Heroku staging resources are unaffected. No provider account, key,
paid quota, or recurring AI service is being activated here.

## Candidate matrix

| Task | Candidates to evaluate | Starting recommendation | Required rule |
|---|---|---|---|
| Brief interpretation, campaign plan, copy variants | OpenAI Responses API; Google Gemini API or Vertex AI; Anthropic Messages API | Run all three against one task suite; route by task score and allowed data class | Structured output is schema-checked; factual statements must map to approved source facts; model output stays a draft |
| Image creation/editing | Google Gemini image API / Vertex AI media models; OpenAI image API | Evaluate both on the same brand-safe synthetic prompts and edits | No source asset is sent without explicit task/provider permission; record model, prompt version, source asset version, and rights declaration |
| Short video and variations | Google Veo through an eligible API; OpenAI video API | Compare a small synthetic set only after confirming endpoint status and retention | Per-generation spend cap, bounded retries, duration/resolution cap, rights and likeness checks; never silently fall back across data classes |
| Document/image analysis | Deterministic extraction first; then a separately evaluated multimodal API | Keep provider calls off until asset-intake readiness is approved | Quarantine, malware scanning, parser isolation, data minimization, deletion, owner authorization, and provider-specific consent |
| Claims, legal, and platform checks | Deterministic rules and source evidence; optional model suggestions | Application checks are authoritative; model is advisory | No model verdict alone may clear a claim, ad, destination, or publication |

For the first future production pilot, prefer at least two independently
operated inference vendors across the enabled tasks, but do not duplicate every
request. The router should select one permitted provider per task; an
independent critic is invoked only when evaluation shows a measurable benefit
and its extra cost/data transfer is permitted. This avoids unnecessary latency
and sending the same content to multiple companies by default.

## Gateway requirements

The existing `ai_gateway` is the application boundary. Extend it with task
types and provider adapters without binding product modules to vendor SDKs.
Each request needs an explicit data classification, permitted-provider set,
synthetic/real phase, model/profile, output schema, token/image/video bounds,
timeout, and spend ceiling. Each result records provider/model identifier,
version or snapshot when available, prompt/template version, usage/cost,
latency, outcome, and source fingerprint; logs must not contain full source
documents or secrets.

Routing must fail closed when consent, provider eligibility, data region,
spend cap, or safety state is unknown. Retry only transient failures, with
bounded attempts and idempotency. A fallback cannot change a data class,
increase a user budget, publish, approve a claim, or loosen policy. Provider
SDKs and credentials stay server-side. Keep publishing/ad-account tools out of
the model tool set; the application performs independently authorized actions.

## Synthetic evaluation gate

Before any provider integration reaches a user route, compare candidates with
the same versioned test suite across multiple advertiser types and paid-ad
formats. Include prompt injection, contradictory/expired facts, wrong-entity
facts, forbidden or regulated claims, unsupported offers, image text/brand
errors, video artifact/likeness problems, rate limits, timeouts, malformed
responses, and provider unavailability.

Score separately: task usefulness, source-grounding false accepts and false
rejects, variant diversity, Turkish and other supported-language quality,
accessibility, brand adherence, correction effort, latency, availability, and
actual per-accepted-result cost. Preserve prompts, model/API identifiers, and
evaluation date. Do not average a safety failure away with a high quality
score. A small synthetic pass permits only the next stage of evaluation; it
does not establish production safety or authorize real data, publication, or
spend. Current Qwen3/Ollama results fail the existing small creative gate, so
local inference is not the default and remains disconnected from web routes.

## Data, terms, and pricing review

The official material checked on 2026-10-03 supports these distinctions:

- OpenAI says API content is not used to train its models by default, but
  standard abuse-monitoring logs can retain content for up to 30 days. Zero
  Data Retention requires eligibility/approval, and the current Video API is
  not compatible with those controls. Check endpoint-specific state and region
  requirements before sending any non-synthetic material.
- Google distinguishes unpaid Gemini API use, where submitted content may be
  used to improve products and human reviewers may process it, from paid
  services, which do not use prompts/responses for product improvement but
  may retain them temporarily for safety and legal purposes. A billing-linked
  project changes the terms category; confirm the exact project and API path.
- Vertex AI separately documents training restrictions for managed models.
  This is not equivalent to zero retention or a promise that all processing
  stays in Türkiye; check product-specific data handling and region controls.
- Anthropic API documentation and pricing/model lifecycle pages must be
  rechecked at provider selection time. Model retirement is expected over
  time, so aliases/snapshots and a migration test are required.
- Image and especially video cost depends on resolution, duration, modality,
  retries, and accepted-output rate. Measure the complete workflow cost rather
  than comparing token price alone. Place a hard provider-side or application
  spend cap before any future API evaluation involving billable usage.

These vendor statements are not Turkish legal advice or a completed KVKK
assessment. Before any real advertiser material, confirm controller/processor
roles, lawful basis and notices, transfer mechanism and region, retention and
deletion, sub-processors, intellectual-property/likeness rights, and the
provider's current commercial/API terms. Do not send real data to free trials.

## Official references checked 2026-10-03

- [OpenAI API models and pricing](https://platform.openai.com/docs/models),
  [image generation](https://platform.openai.com/docs/guides/image-generation),
  [video API](https://platform.openai.com/docs/api-reference/videos), and
  [API data controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint).
- [Gemini API models](https://ai.google.dev/gemini-api/docs/models),
  [image generation](https://ai.google.dev/gemini-api/docs/image-generation),
  [video generation](https://ai.google.dev/gemini-api/docs/video),
  [pricing](https://ai.google.dev/gemini-api/docs/pricing), and
  [additional terms/data use](https://ai.google.dev/gemini-api/terms).
- [Vertex AI generative media pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing),
  [data governance](https://cloud.google.com/vertex-ai/generative-ai/docs/data-governance),
  and [zero data retention](https://cloud.google.com/vertex-ai/generative-ai/docs/vertex-ai-zero-data-retention).
- [Anthropic active model lifecycle](https://docs.anthropic.com/en/docs/about-claude/model-deprecations),
  [pricing](https://docs.anthropic.com/en/docs/about-claude/pricing), and
  [prompt injection mitigations](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks).
- [Existing GrowthTwin claim-grounding design](ai-claim-grounding-contract.md)
  and [asset-intake ADR](../adr/0009-asset-intake-processing-boundary.md).

## Next work

1. Keep the current deterministic template active and all provider calls out of
   web routes.
2. **Completed 2026-10-03:** add the first versioned creative-copy task profile
   and repeatable synthetic benchmark harness. The harness accepts a caller-
   supplied adapter, makes no provider calls itself, and records results in
   memory/JSON-serializable form only.
3. Score the text candidates first using the existing multi-industry claim and
   creative fixtures; add image/video suites separately when their workflows
   and budget limits are defined.
4. **Text evaluation completed; first image evaluation prepared:** on
   2026-10-04 the owner verified a dedicated USD 16 no-reset key cap and
   authorized synthetic-only provider evaluation against existing credits,
   with no top-up or auto-recharge. The owner handles checking account balance;
   do not inspect or persist it. The shared local ledger is separate from the
   provider account. GPT-6 Luna's text comparisons and prompt iteration are
   recorded in `AI_PROVIDERS.md`; results remain generic review drafts and do
   not select a production provider. Gemini did not pass the comparative
   quality gate. Current official image/video research and cost controls are
   also recorded there. A feature branch adds one fixed synthetic 1K image
   call, pinned to the OpenRouter Google Vertex ZDR endpoint, with a USD 0.10
   local reservation and local-only output. Complete required CI before the
   single image call. OpenRouter's video endpoint is not ZDR-eligible, so do
   not make a video request through it. Never send advertiser/customer/patient
   data or use free-tier endpoints with private data.
5. Revisit provider choice and model versions before an externally accessible
   pilot; no result in this document selects a production vendor.
