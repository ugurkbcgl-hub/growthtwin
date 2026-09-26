# AI provider evaluation

This is a development-only comparison. Free access, quotas, model lists, and terms can change. No provider has been selected for production.

| Option | Best initial use | Limits and caution |
|---|---|---|
| NVIDIA Build / NIM | Compare hosted chat, reasoning, coding, and embedding models without managing GPUs | Free endpoints are trial access for development/evaluation, not production. Model-specific limits depend on account/model and live traffic. The key in the shared screenshot must be rotated before use. |
| Ollama with a small open-weight model | Private local baseline for prompt experiments using synthetic data; no provider inference charge | Quality and speed depend on model, context length, VRAM and RAM. A Qwen3 4B download is about 2.5 GB, but runtime memory is higher; begin with a small model and measure. Check the exact model license. |
| Gemini Developer API free tier | Optional second hosted quality comparison | Free limits are model/project-specific. Google says free-tier content may be used to improve its products; do not send customer/clinic data. |
| Groq free plan | Optional fast hosted text comparison | Model-specific RPM/RPD/token limits are shown in the account and can change; use only synthetic development data. |
| OpenRouter free models | Optional quick comparison across changing model providers | Free plan lists 50 requests/day; available free models/providers may change. Not a production dependency. |
| Hugging Face Inference Providers | Occasional fallback experiment | Free accounts currently receive USD 0.10 monthly credits, subject to change; too small for the main development workflow. |

## Evaluation sequence
1. The user confirmed the exposed NVIDIA key has been replaced. Keep the replacement in a local secret store; never paste it into chat or commit it.
2. In the signed-in NVIDIA Build account, inspect the account's displayed request/rate limits and choose one free chat model and, if needed, one embedding model.
3. Use identical synthetic Turkish dental-clinic prompts across NVIDIA and a small local Ollama model. Record quality, latency, failure/rate-limit behavior, and operator effort.
4. Keep a provider-neutral AI gateway in the future product architecture. Do not send free-tier calls from a live GrowthTwin deployment.
5. Recheck licenses and data terms before any pilot customer or production use.

## GrowthTwin local workflow-fit evaluation — 2026-09-26

Environment: Windows workstation with an RTX 3050 Laptop GPU (6 GB VRAM), 31.7 GB RAM, and Ollama 0.34.4. We scored whether models served the product workflow; language fluency was deliberately excluded. Each model received three English prompts based on the same fictional dental practice: create a campaign package, flag and safely rewrite unsupported health claims, and emit a JSON content record with clinic approval status. Requests used local `/api/chat`, `think: false`, `stream: false`, temperature 0.2, and a 256-token output cap. Each task ran once; these are directional smoke-test results, not a robust benchmark.

| Model | Tasks accepted | Campaign package | Claim safety and rewrite | JSON approval record | First response / load | VRAM |
|---|---:|---|---|---|---:|---:|
| Qwen3 0.6B | 0/3 | Produced some pieces but invented a free offer and had weak copy. | Flagged the original claims but repeated health claims in its rewrite. | Truncated and invalid JSON. | 3.36 s / 1.85 s | about 1.52 GB; 100% GPU |
| Qwen3 1.7B | 1/3 | Incomplete at the token cap; included unsupported benefit claims. | Found risky claims but left one in the rewrite. | Valid JSON with all 8 requested keys and the correct clinic-approval status; its `flags` were incomplete. | 5.63 s / 2.12 s | about 2.07 GB; 100% GPU |
| Qwen3 4B | 0/3 | Returned planning text instead of the campaign. | Explained the review but did not provide a safe rewrite. | Discussed JSON instead of producing it. | 9.39 s / 2.59 s | about 3.46 GB; 100% GPU |

All three fit on the 6 GB GPU. The useful result is that Qwen3 1.7B can produce a correctly shaped draft record containing a clinic-approval state, which could support a `draft → clinic approval` workflow. The trial did not show reliable claim safety or ready-to-publish content; no model should publish without a review gate. The 256-token cap and one run per task limit the conclusion, so treat this as a first filter. No provider API key, external inference, or real customer data was used. All models were stopped after measurement; weights remain installed.

## Official references checked 2026-09-26
- NVIDIA model catalog: https://build.nvidia.com/models
- NVIDIA NIM API trial terms: https://assets.ngc.nvidia.com/products/api-catalog/legal/NVIDIA%20API%20Trial%20Terms%20of%20Service.pdf
- NVIDIA NIM FAQ: https://docs.api.nvidia.com/nim/docs/product
- NVIDIA API quickstart: https://docs.api.nvidia.com/nim/docs/api-quickstart
- Ollama model library: https://ollama.com/library/qwen3
- Ollama NVIDIA GPU support: https://github.com/ollama/ollama/blob/main/docs/gpu.mdx
- Gemini pricing and data use: https://ai.google.dev/gemini-api/docs/pricing
- Groq rate limits: https://console.groq.com/docs/rate-limits
- OpenRouter pricing: https://openrouter.ai/pricing
- Hugging Face inference provider pricing: https://huggingface.co/docs/inference-providers/en/pricing
