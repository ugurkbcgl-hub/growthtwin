# AI provider evaluation

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

## Official Ollama references checked 2026-10-03

- Chat API and JSON-schema `format`: https://docs.ollama.com/api/chat
- Structured-output guidance: https://docs.ollama.com/capabilities/structured-outputs
- Exact Qwen3 1.7B model tag: https://ollama.com/library/qwen3:1.7b
- Exact Qwen3 1.7B license: https://ollama.com/library/qwen3:1.7b/blobs/d18a5cc71b84
