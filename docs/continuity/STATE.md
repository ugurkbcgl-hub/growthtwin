# GrowthTwin — current handoff

Last verified: 2026-09-28 10:36 (Europe/Istanbul). `main` is at `e310fe3a874e72b6aee18cb447694271699b9e7e`; post-merge CI `36391321451` passed. Current branch is `feature/GT-030-brand-context`; PR #31 is open against `main` at code commit `2f93f7f`; its required CI is running. Worktree was clean before this handoff update.

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
- PRs #23, #28, #27, and #29 are merged; no deployment or live campaign action occurred.
- Issue #30 tracks optional brand/product context. PR #31: https://github.com/ugurkbcgl-hub/growthtwin/pull/31 — open, based on `main`, CI running on the feature commit.
- The owner authorizes merging reviewed PRs without asking again when required CI passes. Never push directly to `main`.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- The local prototype has a synthetic brief → preview → simulated pause → sample report flow. Session-scoped UUID drafts persist brief, daily limit, and duration; the owner can list, resume, edit, and discard. Other and expired sessions cannot access drafts.
- PR #31 adds a bounded optional brand/product context field to a draft, restores it for editing, and displays it as plain text in the synthetic preview. No AI generation, external account, publication, real metric, or spend is involved.
- Full local Django suite passed (23 tests) using SQLite test settings. Migration check, Ruff format/lint, JavaScript syntax, and `git diff --check` passed before the continuity-only commit; required PR CI remains the merge gate.
- Issues #24 and #26 are closed as completed. Issue #2 (record NVIDIA NIM model quotas) remains open and unrelated to this local UI slice; verify current provider terms before any NIM use.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Drafts currently contain synthetic data only. A hosted schedule for clearing expired Django sessions remains unverified; establish retention/deletion operations before accepting real advertiser data.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before beta/production, not blockers for local synthetic UX work.

## Next action

Verify required CI on the latest PR #31 head, review the final diff, and merge only if CI passes and no issue is found. Then select the next small Phase 2 slice from `ROADMAP.md`.
