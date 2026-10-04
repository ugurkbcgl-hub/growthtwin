# AI provider evaluation and current direction

> **Current recommendation (2026-10-03):** Do not bind GrowthTwin to Ollama,
> a workstation GPU, or a single provider. Use the application-owned,
> provider-neutral gateway to route text, image, video, and asset-analysis
> tasks to separately replaceable hosted APIs. Compare OpenAI, Gemini, and
> Anthropic for text; Google and OpenAI for images and short video. This is a
> synthetic-evaluation shortlist, not a production provider selection or
> permission to incur API charges. See the [provider-combination strategy](docs/product/ai-provider-strategy.md)
> for task routing, data conditions, evidence, and gates.

The existing website still uses deterministic templates. No provider API is
connected to a product route. The local Ollama adapter is optional for
developer experiments only; recent local candidates failed the small
synthetic creative gate. Future provider work must start with synthetic data,
an explicit spend cap, and separate review of the provider's current terms.

## Architecture recommendation

- Use a server-side task router over independent provider adapters; do not
  expose provider SDKs, model names, or credentials to product views.
- Select one permitted provider per task based on measured quality, accepted
  result cost, latency, availability, and the request's data class. Do not
  fan out every advertiser input to multiple providers by default.
- Use deterministic claim/source rules as authority. A second model can
  identify possible issues but cannot prove a claim true or clear it for
  publication.
- Preserve the historical experiments below as evidence, not as vendor
  rankings. Their single-run results are directional only.

This is a development-only comparison. Free access, quotas, model lists, and terms can change. No provider has been selected for production. The project goal is now a cross-industry advertising campaign autopilot, so the dental-clinic examples below are useful safety probes but do not represent the full product workload or establish general model quality.

| Option | Best initial use | Limits and caution |
|---|---|---|
| NVIDIA Build / NIM | Compare hosted chat, reasoning, coding, and embedding models without managing GPUs | Free endpoints are trial access for development/evaluation, not production. Model-specific limits depend on account/model and live traffic. The user confirmed the exposed key was replaced; keep the replacement in a local secret store and never paste or commit it. |
| Ollama with a small open-weight model | Private local baseline for prompt experiments using synthetic data; no provider inference charge | Quality and speed depend on model, context length, VRAM and RAM. A Qwen3 4B download is about 2.5 GB, but runtime memory is higher; begin with a small model and measure. Check the exact model license. |
| Gemini Developer API free tier | Optional second hosted quality comparison | Free limits are model/project-specific. Google says free-tier content may be used to improve its products; do not send private advertiser or customer data. |
| Groq free plan | Optional fast hosted text comparison | Model-specific RPM/RPD/token limits are shown in the account and can change; use only synthetic development data. |
| OpenRouter free models | Optional quick comparison across changing model providers | Free plan lists 50 requests/day; available free models/providers may change. Not a production dependency. |
| Hugging Face Inference Providers | Occasional fallback experiment | Free accounts currently receive USD 0.10 monthly credits, subject to change; too small for the main development workflow. |

## Evaluation sequence
1. The user confirmed the exposed NVIDIA key has been replaced. Keep the replacement in a local secret store; never paste it into chat or commit it.
2. In the signed-in NVIDIA Build account, inspect the account's displayed request/rate limits and choose one free chat model and, if needed, one embedding model.
3. Compare representative synthetic advertiser/campaign tasks across a local Ollama model and any approved evaluation endpoint. Include campaign usefulness and clarity, factuality against supplied brand facts, risky-claim handling, schema/format validity, latency, failure/rate-limit behavior, and review effort. Preserve exact prompts and versions for comparable reruns.
4. Keep a provider-neutral AI gateway in the future product architecture. Do not send free-tier calls from a live GrowthTwin deployment.
5. Recheck licenses and data terms before any pilot customer or production use.

## GrowthTwin local workflow-fit evaluation — 2026-09-26

Environment: Windows workstation with an RTX 3050 Laptop GPU (6 GB VRAM), 31.7 GB RAM, and Ollama 0.34.4. We scored whether models served the product workflow; language fluency was deliberately excluded. Each model received three English prompts based on the same fictional dental practice: create a campaign package, flag and safely rewrite unsupported health claims, and emit a JSON content record with clinic approval status. Requests used local `/api/chat`, `think: false`, `stream: false`, temperature 0.2, and a 256-token output cap. Each task ran once; these are directional smoke-test results, not a robust benchmark.

| Model | Tasks accepted | Campaign package | Claim safety and rewrite | JSON approval record | First response / load | VRAM |
|---|---:|---|---|---|---:|---:|
| Qwen3 0.6B | 0/3 | Produced some pieces but invented a free offer and had weak copy. | Flagged the original claims but repeated health claims in its rewrite. | Truncated and invalid JSON. | 3.36 s / 1.85 s | about 1.52 GB; 100% GPU |
| Qwen3 1.7B | 1/3 | Incomplete at the token cap; included unsupported benefit claims. | Found risky claims but left one in the rewrite. | Valid JSON with all 8 requested keys and the correct clinic-approval status; its `flags` were incomplete. | 5.63 s / 2.12 s | about 2.07 GB; 100% GPU |
| Qwen3 4B | 0/3 | Returned planning text instead of the campaign. | Explained the review but did not provide a safe rewrite. | Discussed JSON instead of producing it. | 9.39 s / 2.59 s | about 3.46 GB; 100% GPU |

All three fit on the 6 GB GPU. The useful result is that Qwen3 1.7B can produce a correctly shaped draft record containing a clinic-approval state, which could support a `draft → clinic approval` workflow. The trial did not show reliable claim safety or ready-to-publish content; no model should publish based on its output alone; the application must validate before dispatch. The 256-token cap and one run per task limit the conclusion, so treat this as a first filter. No provider API key, external inference, or real customer data was used. All models were stopped after measurement; weights remain installed.

## NVIDIA Build workflow-fit smoke test — 2026-09-26

Account panel: personal limit shown as **up to 40 requests per minute (RPM)**. The panel says model limits can vary and other traffic may cause throttling. It showed no monthly request/token balance. The catalog listed 38 free endpoints at the time. Free endpoint status and quotas can change.

Only fictional clinic facts and synthetic prompts were submitted after the user approved NVIDIA's trial/data-processing notice. No API key was viewed, copied, or sent through chat. NVIDIA's Playground displayed a notice that trial inputs/outputs may be recorded to provide the experience and improve NVIDIA products and services. Do not send real clinic/customer or personal data to the trial endpoint.

The same three workflow categories as the Qwen evaluation were used: campaign package generation, unsafe dental-claim flagging and rewrite, and an approval-state JSON record. The exact earlier Qwen prompt text was not preserved, so this is a directional comparison rather than a strictly identical-prompt benchmark. One run per task; reasoning was set off where the Playground exposed that control.

| Model | Tasks accepted | Campaign package | Claim safety and rewrite | JSON approval record | Timing / notes |
|---|---:|---|---|---|---|
| NVIDIA Nemotron 3.5 Lightning 30B A3B | Not scored | Request stayed in the Playground loading state for more than 2 minutes; no response was shown before switching models. | Not run | Not run | Free endpoint was listed as available. Treat this run as an endpoint responsiveness failure, not a quality score. |
| NVIDIA-hosted DeepSeek V4.1 Flash | 2/3 | Accepted: used stated services/hours, created a short CTA and relevant hashtags, and did not invent a discount or outcome claim. | Accepted: flagged the unsupported clinic whitening-service assumption, absolute safety language, guarantee, quantified result, and one-visit timeframe; rewrite used established facts only. | Failed: output was invalid JSON; the `approval_required` and `clinic_approved` keys were emitted without values. | Campaign: 56.89 s total, 8.84 s TTFT, 13.78 tokens/s. Safety: 22.68 s total, 7.36 s TTFT, 72.23 tokens/s. JSON: 18.42 s total, 14.52 s TTFT, 61.03 tokens/s. The Playground also visibly rendered a lengthy reasoning section alongside answers. |

Conclusion: the hosted DeepSeek model was useful for a first marketing draft and for spotting unsupported claims, but it is not safe for automatic structured-record creation or publication. Its response times were materially slower than the tested local Qwen models, and the failed Nemotron request makes endpoint availability an additional concern. Keep strict schema/policy validation and bounded application controls around any model. These are single-run smoke-test results, not reliability evidence. Continue using free NIM endpoints only for synthetic-data prototyping; the NVIDIA trial terms restrict trial use to testing/evaluation rather than production. The product may automate the normal flow after advertiser authorization, but no current model result justifies trusting a model with publishing or spend authority.

## Official references checked 2026-09-26
- NVIDIA model catalog: https://build.nvidia.com/models
- NVIDIA Nemotron 3.5 Lightning model page: https://build.nvidia.com/nvidia/nemotron-3.5-lightning-30b-a3b
- NVIDIA DeepSeek V4.1 Flash model page: https://build.nvidia.com/deepseek-ai/deepseek-v4.1-flash
- NVIDIA NIM API trial terms: https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf
- NVIDIA NIM FAQ: https://docs.api.nvidia.com/nim/docs/product
- NVIDIA API quickstart: https://docs.api.nvidia.com/nim/docs/api-quickstart
- Ollama model library: https://ollama.com/library/qwen3
- Ollama NVIDIA GPU support: https://github.com/ollama/ollama/blob/main/docs/gpu.mdx
- Gemini pricing and data use: https://ai.google.dev/gemini-api/docs/pricing
- Groq rate limits: https://console.groq.com/docs/rate-limits
- OpenRouter pricing: https://openrouter.ai/pricing
- Hugging Face inference provider pricing: https://huggingface.co/docs/inference-providers/en/pricing

## Ollama structured-output smoke test — 2026-10-03

The current workstation was checked read-only: Ollama 0.35.1 is installed with
`qwen3:0.6b`, `qwen3:1.7b`, and `qwen3:4b` already present; no model was
downloaded for this check. The exact `qwen3:1.7b` tag is Q4_K_M, about 1.4 GB,
and its Ollama library page lists Apache-2.0. This confirms the model artifact's
listed license only; it is not legal review or production approval.

One local `/api/chat` request used the fixed synthetic Ankara home-maintenance
brief, a JSON schema, `think: false`, `stream: false`, temperature 0.2, and a
512-token cap. It returned three schema-shaped variants in roughly 30 seconds.
The variants repeated the same angle and nearly the same copy, and one sentence
added an unsupported “compatible solutions” claim. This single run is not a
quality benchmark, but the copy was not useful enough for the product flow. The
gateway now rejects repeated normalized angles; schema validity alone remains
insufficient. Keep the Ollama adapter opt-in and disconnected from web routes;
the deterministic synthetic template remains the user-facing generator.

A second single request against the already-installed `qwen3:4b` model used the
same brief and settings. It took about 80 seconds and was rejected because the
variants repeated their angle. Neither smoke test is a reliability benchmark;
the 4B run did not establish better quality than 1.7B.

No real advertiser/customer data, hosted endpoint, credential, database write,
account connection, publication, or spend was involved. A prior attempt through
the generic URL opener timed out; the adapter now opens a direct HTTP connection
to the fixed loopback address, with no proxy or redirect handling. The adapter
is a local experiment boundary, not a production provider selection.

## Repeatable synthetic creative benchmark — 2026-10-03

Runner: `apps/web/scripts/evaluate_local_ollama.py`. Run from `apps/web` with
the existing virtual environment. By default it makes one request for each of
three fixed synthetic briefs against the already-installed Qwen3 0.6B, 1.7B,
and 4B models. It prints each result to stdout and saves nothing. The
fixtures cover home maintenance, a ceramics workshop, and a bookstore brief
containing an explicitly untrusted prompt-injection/offer claim. Each record
shows the permitted facts and claims that must not appear. No real data or
external provider is used.

| Model | Brief | Time | Gateway result |
|---|---|---:|---|
| Qwen3 1.7B | Home maintenance | 54.01 s | Rejected: repeated creative angles |
| Qwen3 1.7B | Ceramics workshop | 39.82 s | Rejected: repeated creative angles |
| Qwen3 1.7B | Prompt injection and offer claims | 40.14 s | Rejected: repeated creative angles |
| Qwen3 4B | Home maintenance | 120.00 s | Rejected: local response/validation timeout |
| Qwen3 4B | Ceramics workshop | 120.02 s | Rejected: local response/validation timeout |
| Qwen3 4B | Prompt injection and offer claims | 100.42 s | Rejected: repeated creative key |
| Qwen3 0.6B | Home maintenance | 31.13 s | Rejected: invalid creative key |
| Qwen3 0.6B | Ceramics workshop | 18.52 s | Rejected: invalid creative key |
| Qwen3 0.6B | Prompt injection and offer claims | 10.31 s | Initial run returned shaped output but copied the forbidden `ücretsiz` offer from the untrusted note |

Eight of nine outputs were rejected by the gateway. The remaining 0.6B output
was structurally shaped but copied the forbidden `ücretsiz` offer from the
explicitly untrusted brief note. An immediate repeat of that model/brief took
9.52 seconds and was rejected for repeated angles, showing that outputs vary
between runs. The adapter does not perform semantic claim validation or reject
the unsafe shaped output. The runner now flags exact configured forbidden
phrases in any accepted-shaped result; this narrow fixture screen is not a
general safety boundary. Consequently no output passed the candidate gate.
Usefulness and correction effort were not scored. This is a repeatable smoke
benchmark, not a reliability or statistical quality study. One run per
model/brief is insufficient evidence for model selection.

Candidate gate for any future offline integration: complete at least three
runs per brief; every output must pass the structured contract, use only
supported facts, avoid all forbidden/unsupported claims, and contain three
meaningfully distinct variants. Score each variant's usefulness from 0
(irrelevant) to 2 (clear and usable for advertiser review), and correction
effort from 0 (substantial rewrite) to 2 (minor or no changes); record these
scores only after separately checking each claim against the brief. Require
all variants to score at least 1 in usefulness and correction effort. Require
the slowest of the nine measured requests to be at most 60 seconds; this is a
small-sample latency gate, not a production SLO. Passing permits further
offline evaluation only; it does not authorize real data, customer-facing AI,
account access, publication, or spend. Current Qwen3 candidates fail the gate,
so keep the website's deterministic template active and the Ollama adapter
disconnected from routes.

## Persistence-free exact-source claim prototype — 2026-10-03

`apps/web/growthtwin/modules/ai_gateway/claim_grounding.py` is an offline
experiment. It matches one listed claim to one non-expired source fact only
when their full text matches after Unicode compatibility normalization, case
folding, and whitespace collapse. The owner-approval flag and provenance
identifiers are caller-supplied assertions. It rejects paraphrases
and missing/unknown/ambiguous/unapproved/expired evidence. Its source reference
and version are caller-provided labels, not authenticity checks.

This does not locate every factual sentence in a creative, establish that a
claim inventory is complete, validate the truth or legality of a source, or
check platform policy. It is not connected to website routes and cannot
authorize publication. Local validation on the feature branch: all 21 focused
`ai_gateway` tests passed with the in-memory SQLite test settings; Ruff format
and lint passed.

`apps/web/growthtwin/modules/ai_gateway/fact_copy.py` adds a synthetic
controlled-assembly experiment: join up to five explicitly supplied claims
only if every claim exactly matches a caller-asserted, non-expired fact; return
no text if any claim fails or the assembled text exceeds 1,200 characters.
This does not prove the list contains every claim, verify facts, or produce
polished ad copy. All 25 focused `ai_gateway` tests passed with in-memory
SQLite settings; Ruff format and lint passed. It is not connected to web routes.

## Official Ollama references checked 2026-10-03

- Chat API and JSON-schema `format`: https://docs.ollama.com/api/chat
- Structured-output guidance: https://docs.ollama.com/capabilities/structured-outputs
- Exact Qwen3 1.7B model tag: https://ollama.com/library/qwen3:1.7b
- Exact Qwen3 1.7B license: https://ollama.com/library/qwen3:1.7b/blobs/d18a5cc71b84

## Provider-neutral text benchmark interface — 2026-10-03

`apps/web/growthtwin/modules/ai_gateway/profiles.py` defines a versioned
`creative-copy-v1` task profile with a three-run minimum and human review
dimensions. `benchmark.py` accepts caller-supplied `CreativeGenerator`
adapters and synthetic cases, then emits JSON-serializable in-memory records
for contract result, latency, exact fixture phrase matches, candidate label,
and pending manual scores. The harness does not create provider adapters, read
keys, make network calls, store results, or authorize route use. It caps each
invocation at 60 candidate calls.

`scripts/evaluate_local_ollama.py` now uses that same provider-neutral
interface, with already-installed Ollama candidates by default. The interface
itself does not require Ollama; future hosted adapters can be passed only by an
explicit caller after their cost and data controls are separately approved.
Manual factuality/usefulness/diversity review is still required; exact phrase
screens are not general safety checks. No model was evaluated during this
refactor, no provider credentials were added, and web routes remain unchanged.

## Owner-approved bounded text evaluation — 2026-10-04

On 2026-10-03, the owner first approved up to USD 5 for synthetic provider
testing. On 2026-10-04, the owner confirmed an existing USD 16 OpenRouter
credit balance and replaced the USD 5 limit with a direction to track usage
against the current balance. Treat USD 16 as the maximum available for this
evaluation; do not top up credits or enable auto-recharge. Stop if the balance
is exhausted and reassess before any new funding. The first candidate remains
OpenAI GPT-6 Luna for text,
accessed through OpenRouter; this is an evaluation route, not a production
selection. OpenRouter's official catalog checked on 2026-10-03 lists USD 0.10
per million input tokens and USD 0.50 per million output tokens. OpenRouter
currently lists both OpenAI and Amazon Bedrock as upstream endpoints for this
model; the request enforces zero data retention and denies provider data
collection, so the actual eligible endpoint is determined by those constraints
and is recorded when returned.

The opt-in runner `apps/web/scripts/evaluate_openrouter_synthetic.py` is fixed
to one model, three existing synthetic briefs, three repetitions per brief, at
most 512 output tokens, 4,096 request bytes, no tools, and no retries. It sets
OpenRouter's `provider.zdr=true`, `data_collection=deny`,
`require_parameters=true`, and per-token maximum prices. It uses only
`OPENROUTER_API_KEY` from the process environment and never prints the key or
full request. A shared SQLite ledger outside the repository reserves cost
before each call and stops at USD 16 total cumulative estimated usage. An
interrupted/ambiguous call keeps its reservation. The runner also refuses to send a request until
`GROWTHTWIN_AI_EVAL_HARD_LIMIT_CONFIRMED=1` is present. That flag is only an
operator assertion, not proof of an account setting. The local ledger is shared
with other evaluation candidates; do not delete/reset it while this approval is
active. Completed calls are reconciled against OpenRouter's reported request
cost, and the runner prints spend, outstanding reservation, and remaining
local allocation.

Before the first billable call, create a dedicated OpenRouter API key for this
experiment, set a USD 16 spend limit with no automatic reset, confirm the
key/account has sufficient existing credits, and keep auto-recharge off. Store
the key for the current Windows account with
`apps/web/scripts/setup_openrouter_key.ps1`; the runner reads it into the child
process only and clears it afterward. Start the evaluation with
`apps/web/scripts/run_openrouter_synthetic.ps1`. That wrapper asks for an
explicit `RUN` confirmation of the key limit, sufficient existing credits, and
disabled auto-recharge. The key-specific spend limit and local reservation
ledger are independent safeguards. If the dashboard cannot confirm the key
limit or existing credit balance, do not run the hosted script. Never send
advertiser, customer, patient, account, or other private data in this
evaluation.

OpenRouter's current Terms of Service list a USD 5 minimum credit purchase, and
the Standard account currently charges a 5.5% credit-purchase fee with a
minimum USD 0.80 fee. No purchase is needed for the owner's stated existing USD
16 balance. Do not buy credits or enable auto-recharge. If existing credits are
no longer sufficient, stop and get a new budget decision before funding the
account.

### First bounded hosted run — 2026-10-04

The owner confirmed readiness after handling the account-side checks; the
assistant did not inspect the OpenRouter account. The fixed synthetic runner
completed all nine GPT-6 Luna calls. Responses were returned as
review-required, non-publishable drafts. The fixture's exact forbidden-phrase
screen reported no matches in the run output; this is not semantic claim
validation or a safety clearance. Manual usefulness, factual grounding,
diversity, brand fit, and correction-effort scores remain unassessed, so this
run does not pass the creative candidate gate or select a provider.

OpenRouter-reported call costs totaled USD 0.0014665. The shared local ledger
reports cap USD 16.00, spent USD 0.0014665, and USD 0 reserved. These are
evaluation-ledger figures, not a live account-balance check. The run output
was not persisted; only this bounded summary and the local usage ledger remain.
No advertiser, customer, patient, or account data was sent, and no output was
published or connected to a product route.

Merged PR #239 adds a local JSONL capture to the opt-in runner before any
further hosted evaluation. It records the run metadata, each synthetic
benchmark result, generated variants, provider-reported token/cost metadata,
reservation and settlement events, and the final local ledger summary under
the current user's `%LOCALAPPDATA%\GrowthTwin\evaluations` directory. It does
not record the brief/request body or API key and fails closed if the result
file cannot be initialized. No provider call has been made with this capture.

OpenRouter says request-level `zdr=true` restricts routing to eligible
zero-retention endpoints, while `data_collection=deny` filters endpoints that
collect inputs. This does not make the request local, guarantee Türkiye/EU
processing, or establish KVKK compliance. OpenRouter forwards inputs to the
selected model provider, whose separate policies also matter. This trial
therefore uses only repository synthetic fixtures; if no endpoint satisfies
the request constraints, the evaluation must fail closed.

Official source pages checked 2026-10-04: OpenRouter [GPT-6 Luna model/pricing](https://openrouter.ai/openai/gpt-6-luna), [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [ZDR and data collection controls](https://openrouter.ai/docs/guides/get-started/sovereign-ai), [API-key spend limit](https://openrouter.ai/docs/api/api-reference/api-keys/create-keys), [Standard purchase pricing](https://openrouter.ai/pricing), [credit purchase fee](https://openrouter.ai/blog/insights/governing-team-ai-spend/), and [Terms of Service / minimum credits](https://openrouter.ai/terms).

**Next:** use the merged local JSONL capture for one bounded synthetic run only
after the owner confirms the dedicated key's USD 16 no-reset limit, sufficient
existing balance, and disabled auto-recharge. Then manually review usefulness,
grounding, diversity, brand fit, and correction effort. The owner checks
OpenRouter balance and auto-recharge settings; the assistant does not access
the account. Track cumulative use in the shared local USD 16 ledger and stop at
its cap. A no-network estimate of the nine-call run is at most USD 0.005834.
