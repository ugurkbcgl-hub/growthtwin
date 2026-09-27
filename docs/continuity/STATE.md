# GrowthTwin — current handoff

Last verified: 2026-09-27 21:05 (Europe/Istanbul), before the local prototype PR was opened.

## Goal and working rules

- Product direction (accepted ADR-0004): a polished self-service ad website that carries a user's request through campaign planning, creative generation, validation, authorized publishing, and reporting with minimal effort.
- The product must support different advertiser types; Turkish small businesses and creators are the recommended starting audience. The first pilot segment and publishing destination remain open.
- The owner authorized local product development. Routine work should not require a GrowthTwin employee; the advertiser must connect accounts and set hard content, schedule, and spend limits. Pause when a safe/authorized action is uncertain.
- Use synthetic data in local, CI, and staging; keep secrets/private data out of chat, Git, logs, and handoff files.
- Only approved paid infrastructure is one Heroku Basic dyno and one Essential-0 PostgreSQL database, observed near USD 12/month before tax. No add-ons, extra dynos, production hosting, or paid AI without a new owner decision.
- Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, and this file in order; then verify Git, PR, and CI state live.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin; `main` is protected; use feature branches and PRs.
- Product-direction documentation PR #20 was merged as `4c822626c4627e90c5240e09a224ceca34a6d9cc`. Its required check `36338295417` and post-merge main CI `36338406074` passed.
- Current branch: `product/campaign-experience-prototype` at `134817d`, based on that main commit. It contains the first local website prototype and roadmap status update. The PR was not yet open at this snapshot.
- The owner previously authorized routine merges after review and successful required CI. Never push directly to `main`.

## Product and implementation status

- The local site at `/` is a responsive Turkish landing/campaign workspace. It demonstrates a short brief, daily cap and duration, a creative preview, a simulated pause control, and a clearly synthetic sample report.
- Prototype values remain in the browser; no campaign is stored and no network integration, model call, account connection, publication, ad spend, or real metric is used.
- Django 5.2 LTS + PostgreSQL 18 remains the accepted one-app modular-monolith stack. The single shared checkout is `C:\Users\Public\Desktop\GrowthTwin`.
- Local browser screenshots were visually reviewed at desktop and mobile sizes and at preview/report states. `git diff --check` passed. No test suite was run manually; CI will run the required checks after the PR opens.
- Existing Qwen/NVIDIA evaluations are one-run synthetic dental examples with safety, schema, and latency weaknesses. NVIDIA Build/NIM remains evaluation-only; no production model is selected.

## Remaining release-readiness work

- Staging profile-edit E2E has not run; no disposable account is provisioned. A one-off dyno/account-provisioning action has not been approved.
- Backup/restore, controlled rollback, and browser-visible health response remain unverified. They gate external beta/production, not local synthetic-data UX.
- No real platform API, production AI provider, or production host is selected.

## Next action

Open the local prototype PR, verify its required CI, review and merge it under the standing authorization; then extend the local flow to save synthetic advertiser/campaign records without connecting a platform or spending money.
