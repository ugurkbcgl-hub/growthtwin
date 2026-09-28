# GrowthTwin — current handoff

Last verified: 2026-09-28 09:23 (Europe/Istanbul). PR #23 is open at `68c1a2bc02f6e13070f4af90cedb6c3de22e0e82`; required CI run `36346656517` passed. PR #25 is open at `9767d6e2313c3483cb1e6fc44c9a6349fd118be9`; required CI run `36386168800` is running. Verify its result on the latest head.

## Goal and working rules

- Target market: Türkiye; GrowthTwin serves people and organizations that want to advertise. Dental clinics are one example, not the product boundary.
- Omneky is a long-term capability benchmark for advertiser/brand intake, multi-format creative, connected campaign launch, unified reporting, and bounded optimization—not a first-release parity commitment.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. The initial workflow, platform, and review/autonomy defaults remain open.
- Routine work should not require a GrowthTwin employee. Advertisers authorize accounts and set enforceable spend, schedule, and content limits; pause on uncertainty.
- Use synthetic data in local, CI, and staging. Keep secrets and private advertiser data out of chat, source, logs, issues, and handoff files.
- Only approved paid infrastructure is the existing Heroku Basic dyno plus Essential-0 PostgreSQL at about USD 12/month before tax. Do not add paid services, live publishing, or advertiser spend without authorization.
- Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, and this file in order; then recheck Git, PR, and CI state.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin. Use feature branches and PRs; do not push directly to `main`.
- PR #23: https://github.com/ugurkbcgl-hub/growthtwin/pull/23 — open, base `main`, head `68c1a2bc02f6e13070f4af90cedb6c3de22e0e82`, required CI run `36346656517` passed.
- Issue #24 tracks session-scoped synthetic campaign drafts, UUID identifiers, in-session edits, deletion, isolation, and cleanup.
- PR #25: https://github.com/ugurkbcgl-hub/growthtwin/pull/25 — open, head `9767d6e2313c3483cb1e6fc44c9a6349fd118be9`, base `feature/GT-022-turkey-advertising-roadmap`; required CI run `36386168800` is running. It is stacked on PR #23; retarget it to `main` after #23 merges.
- No PR has been merged or deployed as part of this work.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- Phase 1's website prototype is merged to `main`: synthetic brief → preview → simulated pause → sample report. PR #25 adds the first Phase 2 persistence slice; it adds no AI generation, account connection, publication, ad spend, or real metrics.
- PR #25 stores only the brief, daily cap, and duration in a UUID-keyed draft linked to the anonymous Django session. The owner session can restore and edit the same draft, discard it with a CSRF-protected POST, and cannot act on drafts owned by another session. GET does not delete. Django session cleanup deletes linked drafts. The UI warns to use synthetic input only.
- Local verification on the latest code head: all 17 Django tests passed with SQLite test settings; `makemigrations --check --dry-run` reported no changes; Ruff format/lint, `node --check`, and `git diff --check` passed. Latest required PR CI is pending.
- No AI provider, ad destination, live account connection, publishing, advertiser spend, new paid service, or deployment was added.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of current Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- The prototype stores briefs in the PostgreSQL-backed session-linked draft table. Use synthetic data only; a hosted cleanup schedule for expired sessions has not been verified. Define retention and deletion operations before real advertiser data is accepted.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before external beta/production, not blockers for local synthetic UX work.

## Next action

Verify CI run `36386168800` on the latest PR #25 head. Keep #25 open while #23 is open; after #23 merges, retarget #25 to `main` and verify its required CI again. Do not merge without an explicit owner request.
