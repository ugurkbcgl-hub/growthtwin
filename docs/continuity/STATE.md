# GrowthTwin — current handoff

Last verified: 2026-09-28 10:49 (Europe/Istanbul). `main` is at `72e3cbd34a0ae661a9c687f772be5176eb4dfb19`; post-merge CI `36393053256` passed. Current branch `feature/GT-033-campaign-objective` has PR #34 open against `main`; CI is running. Issue #33 tracks the objective slice. No deployment, external account connection, or live campaign action occurred.

## Goal and working rules

- Target market: Türkiye; GrowthTwin serves people and organizations that want to advertise. Dental clinics are one example, not the product boundary.
- Omneky is a long-term capability benchmark for advertiser/brand intake, multi-format creative, connected campaign launch, unified reporting, and bounded optimization—not a first-release parity commitment.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. The initial workflow, platform, and review/autonomy defaults remain open.
- Routine work should not require a GrowthTwin employee. Advertisers authorize accounts and set enforceable spend, schedule, and content limits; pause on uncertainty.
- Use synthetic data in local, CI, and staging. Keep secrets and private advertiser data out of chat, source, logs, and handoff files.
- Only approved paid infrastructure is the existing Heroku Basic dyno plus Essential-0 PostgreSQL at about USD 12/month before tax. Do not add paid services, live publishing, or advertiser spend without authorization.
- Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, and this file in order; then recheck Git, PR, and CI state.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin. Worktree: `C:\Users\Public\Desktop\GrowthTwin`; feature branches and PRs only, no direct `main` pushes.
- PRs #23, #28, #27, #29, #31, and #32 are merged. PR #34: https://github.com/ugurkbcgl-hub/growthtwin/pull/34 — open; required CI is running on code head `e54e29a` and will be rerun for this handoff commit.
- Issue #33 tracks the objective work; issue #2 (record NVIDIA NIM model quotas) remains open. Verify current provider terms before any NIM use.
- No deployment or live campaign action occurred. The owner authorizes merging reviewed PRs without asking again when required CI passes. Never push directly to `main`.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- Session-scoped UUID drafts persist the brief, optional brand/product context, daily limit, and duration. The owner can list, resume, edit, and discard drafts. Other and expired sessions cannot access them.
- PR #34 adds an optional generic campaign objective (awareness, site visits, leads, sales/bookings, local visits), stores it with the draft, restores it for edits, and displays it in the synthetic preview. Blank stays blank; no goal is inferred.
- Full local Django suite passed (24 tests) using SQLite test settings. Migration consistency, Ruff format/lint, JavaScript syntax, and `git diff --check` passed before this continuity-only commit. Required CI is the merge gate.
- No AI generation, provider, external account, publishing, real performance metric, new paid service, advertiser spend, or deployment was added.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Drafts currently contain synthetic data only. A hosted schedule for clearing expired Django sessions remains unverified; establish retention/deletion operations before accepting real advertiser data.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before beta/production, not blockers for local synthetic UX work.

## Next action

Verify required CI on the latest PR #34 head and review its final diff. Merge if all checks pass and no issue is found; then select the next small Phase 2 workflow slice.
