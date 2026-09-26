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
1. Revoke the exposed NVIDIA key and create a replacement directly in NVIDIA Build. Keep its value in a local secret store; never paste it into chat or commit it.
2. In the signed-in NVIDIA Build account, inspect the account's displayed request/rate limits and choose one free chat model and, if needed, one embedding model.
3. Use identical synthetic Turkish dental-clinic prompts across NVIDIA and a small local Ollama model. Record quality, latency, failure/rate-limit behavior, and operator effort.
4. Keep a provider-neutral AI gateway in the future product architecture. Do not send free-tier calls from a live GrowthTwin deployment.
5. Recheck licenses and data terms before any pilot customer or production use.

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
