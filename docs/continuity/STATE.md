# GrowthTwin — current handoff

Last verified: 2026-09-27 20:47 (Europe/Istanbul), while PR #20 CI was running.

## Goal and working rules

- Product direction: a polished self-service ad website that carries a user's request through campaign planning, creative generation, validation, authorized publishing, and reporting with minimal effort.
- Product is not restricted to dental clinics. Turkish small businesses and creators are recommended as an initial audience; the first pilot segment and publishing destination remain to validate.
- The owner authorized local product development now. Routine campaigns should not need a GrowthTwin employee; advertisers must explicitly connect accounts and set hard content, schedule, and spend limits. Pause when a safe/authorized action is uncertain.
- Use synthetic data in local/CI/staging; never store secrets or private user data in chat, Git, logs, or handoff files.
- Only approved paid infrastructure: one Heroku Basic dyno plus one Essential-0 PostgreSQL database, observed near USD 12/month before tax. No add-ons, extra dynos, production hosting, or paid AI without a new decision.
- Use `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, this file, then verify current Git/PR/CI facts before acting.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin; `main` is default and protected; changes go through PRs.
- At the start of this work, `main` was `6aba41e27ef6a6ea6974697d2aa2577321595180`, clean, with no open PRs. Latest main CI run `36335898184` passed.
- Current work branch: `product/autonomous-advertising-reorientation` at `9c07243`, based on that `main`.
- PR #20, `docs: refocus GrowthTwin on ad automation website`, is open: https://github.com/ugurkbcgl-hub/growthtwin/pull/20. Required check `Django system check` / CI run `36338252883` was in progress at this snapshot. Recheck before acting.
- The owner previously authorized routine merges after review and successful required CI. Do not push directly to `main`.

## Current product/workflow status

- Existing code remains a small synthetic profile-edit demo; no campaign product workflow has been implemented.
- Django 5.2 LTS + PostgreSQL 18 remains the accepted one-app modular-monolith stack. Local development in the single checkout at `C:\Users\Public\Desktop\GrowthTwin` is now the immediate focus.
- Workstation resources already available: Python 3.13.15, PostgreSQL 18.6, 31.7 GB RAM, RTX 3050 Laptop GPU with 6 GB VRAM, Ollama 0.34.4, and Qwen3 0.6B/1.7B/4B. Existing Qwen and NVIDIA tests are one-run synthetic dental examples; they show safety/JSON/latency weaknesses and do not select a production model.
- NVIDIA Build/NIM remains evaluation-only with synthetic data; do not send private advertiser data or use it for end users.
- Heroku app `growthtwin-stage-270927` is staging only. Last recorded dashboard observation showed one Basic web dyno and one Essential-0 database. Latest observed deployed revision was `ac2f627d`; current `main` was not deployed at that observation.

## Remaining release-readiness work

- Staging profile-edit E2E has not run; no disposable account is provisioned. A one-off dyno/account-provisioning action has not been approved.
- Backup/restore, controlled rollback, and browser-visible health response remain unverified. These are gates before external beta or production, but do not block local synthetic-data UX work.
- No real platform API destination, production AI provider, or production host has been selected.

## Next action

Review PR #20's required CI result and merge it if green under the standing authorization; then build the Phase 1 local campaign-intake and campaign-status prototype with clearly labeled synthetic data and no external publishing calls.
