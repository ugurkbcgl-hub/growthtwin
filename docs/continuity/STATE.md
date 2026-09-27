# GrowthTwin — current handoff

Last verified: 2026-09-27 (Europe/Istanbul)

## Goal and working rules

- Complete Phase 0: establish and demonstrate a repeatable, safe development workflow before implementing product features.
- Product direction: an AI-assisted content, review, publishing, and analytics workflow for dental clinics in Türkiye.
- The project owner wants the assistant to coordinate the work, track progress, and provide clear Turkish summaries; keep hands-on terminal work with the assistant where possible.
- Prefer fit-for-purpose AI over Turkish-language specialization. Keep model/provider choices replaceable and use synthetic inputs for hosted trials.
- No product features, staging deployment, paid services, or real clinic/patient data until the relevant Phase 0 gate and explicit user decision.

## Repository and review

- Repository: `https://github.com/ugurkbcgl-hub/growthtwin`
- Working branch: `docs/qwen3-local-evaluation` (verify before continuing).
- Pull request #3: [docs: record Qwen3 workflow-fit evaluation](https://github.com/ugurkbcgl-hub/growthtwin/pull/3), open against `main` at last check. Verify live status before acting.
- Use feature branches and PRs; never push directly to `main`. Do not merge unless the user requests it.
- Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, and the continuity protocol before work.

## Accepted decisions and verified setup

- Initial application stack: Django 5.2 LTS + PostgreSQL, modular monolith (`apps/web`); see ADR-0002.
- Windows workstation has Python 3.13.15 and PostgreSQL 18.6. The PostgreSQL service is `postgresql-x64-18` on port 5432; local database `growthtwin` and restricted role `growthtwin_app` were created.
- App and Django secrets are protected outside the repository with Windows DPAPI under `%LOCALAPPDATA%\GrowthTwin\secrets`. Never reveal, copy, or commit their values.
- Django framework migrations and `manage.py check` passed after local setup. This was a development shell only; no GrowthTwin product models or workflows exist.
- Ollama 0.34.4 is installed. Qwen3 0.6B, 1.7B, and 4B fit the 6 GB RTX 3050 Laptop GPU; initial quality/latency findings are in `AI_PROVIDERS.md`. No additional broad model sweep is planned.
- NVIDIA Build/NIM hosted models are evaluation-only. The previously exposed key was replaced; its replacement must remain secret. Account and per-model limits have not been recorded and need a fresh check before relying on the service. Use synthetic data only.
- CI checks/required branch status, NVIDIA quotas, and M4 staging provider/cost ceiling remain open. No paid infrastructure is enabled.

## Phase 0 status

- M2 local development setup: complete.
- M3 engineering guardrails: in progress; CI workflow/required checks remain.
- M4 demo and staging chain: pending and gated by the roadmap.
- M5 final acceptance: pending.
- No product feature implementation has been authorized or started.

## Next action

Verify PR #3 and the branch state, then continue Phase 0 by preparing a small CI workflow for the existing Django shell and documentation. Decide required branch-protection checks only after the workflow name and result are stable. Keep the scope limited to checks; do not start product features or incur service costs.

## Session start facts to recheck

At every new session, recheck the live PR, branch and working-tree state. PostgreSQL service status and provider quotas are time-sensitive; recheck them if the next task depends on them.
