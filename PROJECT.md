# GrowthTwin project brief

## Status
- Current phase: Phase 0, development factory.
- Repository: private GitHub repository `https://github.com/ugurkbcgl-hub/growthtwin` is connected; `main` is the default branch and the baseline is pushed. GitHub rejected branch protection for this private repository with HTTP 403 and requires Pro; repository visibility remains private.
- Product feature implementation: not started.
- Project name is a codename and may change.

## Product direction
GrowthTwin is intended to help dental clinics in Türkiye create, review, publish, and learn from social content. The first five customers are planned as free pilot customers from the founders' existing network.

The first product scope described in the project reference is:
- Instagram Reels and short video, image posts, captions/copy
- Clinic approval before publishing
- Publishing and analytics
- A web panel and email

Long video, Google Ads, full CRM, and production growth-graph functionality are later work.

## Phase 0 objective
Build and demonstrate a repeatable development workflow before building the GrowthTwin product: private repository, persistent project docs, isolated development/staging/production configuration, CI, a small demo app, a staging deployment, E2E coverage, health checks, backup and a tested rollback path.

The reference specification describes a modular monolith with workers and a target architecture including Next.js, FastAPI, PostgreSQL/pgvector, Temporal, Redis, object storage, and an AI gateway. These are candidate decisions until recorded and accepted; do not create unnecessary services during Phase 0.

## AI provider direction
- NVIDIA Build/NIM's hosted free endpoints are a useful place to prototype and compare models. NVIDIA's trial terms restrict this access to evaluation/testing and exclude production use.
- The shared screenshot exposed an API key. Treat that key as compromised: rotate it in NVIDIA Build before any further use. Do not store the old or replacement value here.
- Do not submit real clinic or patient data to free/trial endpoints. Use synthetic examples while evaluating.
- A small local model through Ollama is a candidate for private, no-per-call-cost experiments. This workstation has 32 GB RAM and an RTX 3050 Laptop GPU with 6 GB VRAM; runtime and context memory still need to be measured.
- Do not select a production model or provider yet. Keep the integration behind an AI gateway so providers can change.

## Workstation and tool inventory (2026-09-26)
- Host: Acer Nitro ANV15-51, Windows, 13th Gen Intel Core i5-13420H, 31.7 GB RAM.
- NVIDIA GeForce RTX 3050 6 GB Laptop GPU is visible to Windows and WSL2.
- Ubuntu on WSL2 is present.
- Git is present. GitHub CLI 2.101.0 is installed and authorized through the local credential store. Ollama 0.34.4 is installed; Qwen3 0.6B and 4B fit on the GPU. See AI_PROVIDERS.md for the initial quality/latency comparison.
- Docker CLI was not found during the initial inventory.
- The ChatGPT project mirror contains reference files but is not a Git repository. Its sources/ directory remains read-only.

## Budget and project constraints
The project reference sets a Phase 0 working hard limit of USD 100/month, with a warning around USD 80/month and user approval for a single spend above USD 20. Treat these as project constraints to confirm against the user's current budget before purchasing or provisioning anything. Prefer the NVIDIA trial and local models for experiments; free API quotas and terms can change.

## Open decisions
1. Should we accept the recurring GitHub Pro cost to enforce branch protection on this private repository, or keep manual branch/PR discipline for now? Do not make the repository public to avoid this cost.
2. Should initial development use the existing local WSL2 Ubuntu environment as a temporary bootstrap, or should we provision a separate Linux host immediately?
3. What exact account quota is visible in NVIDIA Build after the exposed key is revoked and replaced? No replacement key should be shared in chat or committed.
4. What deployment provider and recurring-cost ceiling will be used for a Phase 0 staging environment?
5. Which technical stack candidates from the reference should become accepted architecture decisions?
