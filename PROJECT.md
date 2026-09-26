# GrowthTwin project brief

## Status
- Current phase: Phase 0, development factory.
- Repository: public GitHub repository `https://github.com/ugurkbcgl-hub/growthtwin` is connected at the user's request; `main` is the default branch. Branch protection now requires PRs and blocks force-push/deletion. Required CI status checks remain to be configured after a workflow exists.
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
Build and demonstrate a repeatable development workflow before building the GrowthTwin product: the public repository selected by the user, persistent project docs, isolated development/staging/production configuration, CI, a small demo app, a staging deployment, E2E coverage, health checks, backup and a tested rollback path.

The project owner accepted Django 5.2 LTS + PostgreSQL as the initial application stack in ADR-0002. The reference also discussed Next.js, FastAPI, pgvector, Temporal, Redis, object storage, and an AI gateway; do not add separate services or extensions until a feature requires them and the cost/architecture is reviewed.

## AI provider direction
- NVIDIA Build/NIM's hosted free endpoints are a useful place to prototype and compare models. NVIDIA's trial terms restrict this access to evaluation/testing and exclude production use.
- The user confirmed the API key exposed in the screenshot has been replaced. Keep the replacement secret out of chat and the repository.
- Do not submit real clinic or patient data to free/trial endpoints. Use synthetic examples while evaluating.
- A small local model through Ollama is a candidate for private, no-per-call-cost experiments. Initial Qwen3 runtime and VRAM measurements on this workstation are recorded in AI_PROVIDERS.md; no production model has been selected.
- Do not select a production model or provider yet. Keep the integration behind an AI gateway so providers can change.

## Workstation and tool inventory (2026-09-27)
- Host: Acer Nitro ANV15-51, Windows, 13th Gen Intel Core i5-13420H, 31.7 GB RAM.
- NVIDIA GeForce RTX 3050 6 GB Laptop GPU is visible to Windows and WSL2.
- Ubuntu is installed as a WSL2 distribution; WSL package version 2.6.1.0 was observed, and the distribution was stopped when checked.
- Git is present. GitHub CLI was not found in the current PowerShell session; Git push to the configured remote works. Windows Node.js 24.11.1 and npm 11.6.2 are available. Python 3.13.15 is installed in the current user's Windows environment. Docker CLI and the `psql` command were not found in the current session.
- Ollama 0.34.4 is installed; Qwen3 0.6B, 1.7B, and 4B fit on the GPU. See AI_PROVIDERS.md for the initial quality/latency comparison. No additional model tests are planned for this setup step.
- The ChatGPT project mirror contains reference files but is not a Git repository. Its sources/ directory remains read-only.

## Budget and project constraints
The project reference sets a Phase 0 working hard limit of USD 100/month, with a warning around USD 80/month and user approval for a single spend above USD 20. Treat these as project constraints to confirm against the user's current budget before purchasing or provisioning anything. Prefer the NVIDIA trial and local models for experiments; free API quotas and terms can change.

## Open decisions
1. Which local PostgreSQL installation should be used for M4 while keeping the single Codex-managed checkout intact?
2. Which CI status check should be required on `main` after its workflow stabilizes?
3. What exact per-model NVIDIA Build limits and account quota are visible for future development evaluations? The key is already replaced; do not share the replacement key in chat or commit it. Recheck current limits before relying on them.
4. What deployment provider and recurring-cost ceiling will be used for a Phase 0 staging environment?
