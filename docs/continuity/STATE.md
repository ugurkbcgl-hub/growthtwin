# GrowthTwin — current handoff

Last verified: 2026-09-28 10:11 (Europe/Istanbul). PR #23 merged to `main` as `a27fa25cae37c3dbccac0c67ab0c2b96b9daf346`; post-merge CI `36390088871` passed. Original PR #25 was auto-closed when its base branch was deleted; replacement PR #28 is open with the same feature head `ed04010f5af3ccf08d95f13c9d24cb28c9f953fb`. PR #27 remains open on `feature/GT-024-session-campaign-drafts` at `da6a863c2b026ce34b9aa55c4bbe0087edfaa9b4`. PR #28 currently needs fresh CI after reconciling its branch with the merged `main`; PR #27's last CI `36388737286` passed before that update.

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
- PR #23 is merged; post-merge CI passed on `main` at `a27fa25`.
- PR #25 was closed automatically after its base branch was deleted when #23 merged. Its feature branch is retained and is now tracked by replacement PR #28: https://github.com/ugurkbcgl-hub/growthtwin/pull/28. It must be reconciled with `main` and pass fresh CI before merge.
- PR #27: https://github.com/ugurkbcgl-hub/growthtwin/pull/27 — open, stacked on the retained campaign-draft feature branch. Its current head's previous CI passed, but it must be rechecked after integrating latest `main`.
- The owner authorizes merging reviewed PRs without asking again when required CI passes. Never push directly to `main`.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- Phase 1's website prototype is on `main`: synthetic brief → preview → simulated pause → sample report. PR #28/#27 extend Phase 2 with persisted synthetic drafts and a same-session return flow; no AI generation, account connection, publication, ad spend, or real metrics is added.
- Drafts use UUID identifiers and belong to anonymous Django sessions. The owner session can list, resume, edit, and discard drafts. Other or expired sessions cannot access them; empty visits do not create sessions. Django cleanup cascades drafts when it removes sessions. The UI labels data synthetic.
- Local verification on the feature code: 22 Django tests passed with SQLite test settings; Ruff format/lint, JavaScript syntax, and `git diff --check` passed. Original PR CI passed before the base change; fresh CI is required.
- No AI provider, publishing destination, paid service, live account, advertiser spend, or deployment was added.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Drafts contain only synthetic data for now. A hosted schedule for clearing expired Django sessions remains unverified; establish retention/deletion operations before accepting real advertiser data.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before beta/production, not blockers for local synthetic UX work.

## Next action

Resolve the `main`/campaign-draft branch history divergence, verify fresh CI on PR #28, and then integrate the same base into PR #27. Merge only after review and successful required CI; retain dependency branches until their child PR is merged.
