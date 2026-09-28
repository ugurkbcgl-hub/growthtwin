# GrowthTwin — current handoff

Last verified: 2026-09-28 09:50 (Europe/Istanbul). PR #23 is open at `68c1a2bc02f6e13070f4af90cedb6c3de22e0e82`; required CI `36346656517` passed. PR #25 is open at `ed04010f5af3ccf08d95f13c9d24cb28c9f953fb`; required CI `36386658561` passed. PR #27 is open at `772fcb7519176de55a98aa8117506d4d4c1ca535`; required CI `36388528960` passed. This state refresh will trigger another check; verify it on the new PR #27 head.

## Goal and working rules

- Target market: Türkiye; GrowthTwin serves people and organizations that want to advertise. Dental clinics are one example, not the product boundary.
- Omneky is a long-term capability benchmark for advertiser/brand intake, multi-format creative, connected campaign launch, unified reporting, and bounded optimization—not a first-release parity commitment.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. The initial workflow, platform, and review/autonomy defaults remain open.
- Routine work should not require a GrowthTwin employee. Advertisers authorize accounts and set enforceable spend, schedule, and content limits; pause on uncertainty.
- Use synthetic data in local, CI, and staging. Keep secrets and private advertiser data out of chat, source, logs, issues, and handoff files.
- Only approved paid infrastructure is the existing Heroku Basic dyno plus Essential-0 PostgreSQL at about USD 12/month before tax. Do not add paid services, live publishing, or advertiser spend without authorization.
- Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, and this file in order; then recheck Git, PR, and CI state.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin. Worktree: `C:\Users\Public\Desktop\GrowthTwin`; feature branches and PRs only, no direct `main` pushes.
- PR #23: https://github.com/ugurkbcgl-hub/growthtwin/pull/23 — open, base `main`, head `68c1a2bc02f6e13070f4af90cedb6c3de22e0e82`, required CI `36346656517` passed.
- Issue #24 / PR #25: https://github.com/ugurkbcgl-hub/growthtwin/pull/25 — open, head `ed04010f5af3ccf08d95f13c9d24cb28c9f953fb`, base `feature/GT-022-turkey-advertising-roadmap`, required CI `36386658561` passed. #25 is stacked on #23.
- Issue #26 / PR #27: https://github.com/ugurkbcgl-hub/growthtwin/pull/27 — open, head `772fcb7519176de55a98aa8117506d4d4c1ca535`, base `feature/GT-024-session-campaign-drafts`, required CI `36388528960` passed. #27 is stacked on #25.
- No PR was merged and no deployment was performed.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- Phase 1's website prototype is on `main`: synthetic brief → preview → simulated pause → sample report. PRs #25/#27 extend Phase 2 with persisted synthetic drafts and a same-session return flow; no AI generation, account connection, publication, ad spend, or real metrics is added.
- Drafts use UUID identifiers and belong to anonymous Django sessions. The owning active session can list, resume, edit, and discard them. Other or expired sessions cannot read or change drafts; empty visits do not create sessions. Django cleanup cascades drafts when it removes sessions. The UI labels the data as synthetic.
- Local verification on feature code: all 22 Django tests passed with SQLite test settings; Ruff format/lint, JavaScript syntax, and `git diff --check` passed. Required CI passed on code head `a3c9730` and state-only head `772fcb7`.
- No AI provider, publishing destination, paid service, live account, advertiser spend, or deployment was added.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Drafts contain only synthetic data for now. A hosted schedule for clearing expired Django sessions remains unverified; establish retention/deletion operations before accepting real advertiser data.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before beta/production, not blockers for local synthetic UX work.

## Next action

Verify CI triggered by this state refresh. Keep all PRs open: after #23 merges, retarget #25 to `main`; after #25 merges, retarget #27 to `main`. Verify required CI at each new head. Do not merge without an explicit owner request.
