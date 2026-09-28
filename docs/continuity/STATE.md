# GrowthTwin — current handoff

Last verified: 2026-09-28 10:20 (Europe/Istanbul). `main` is at `2ebc5c2b74d734d2ec96dbf4c2789772df31459d`; post-merge CI `36390932652` passed. PR #23 (product direction), replacement PR #28 (session-scoped synthetic draft persistence; original #25 was auto-closed when its base branch was deleted), and PR #27 (session draft library) are merged. No open PRs or uncommitted changes were present at this verification. No deployment or live campaign action was performed.

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
- `main` head: `2ebc5c2`; post-merge CI run `36390932652` passed.
- PR #23 merged at `a27fa25`; post-merge CI passed at run `36390088871`.
- The original PR #25 was auto-closed when its base branch was deleted. Replacement PR #28 merged at `c20cc6c`; required CI passed on its reconciled head `42cba79` (run `36390382434`), and post-merge CI passed (run `36390668094`).
- PR #27 merged at `2ebc5c2`; required CI passed on final head `bae0bcd` (run `36390786447`), and post-merge CI passed (run `36390932652`).
- No PR is currently open. The owner authorizes merging reviewed PRs without asking again when required CI passes. Never push directly to `main`.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- Phase 1's website prototype is on `main`: synthetic brief → preview → simulated pause → sample report.
- The local Phase 2 slice persists validated campaign briefs, daily caps, and durations as UUID drafts owned by an anonymous Django session. Users can resume, edit, list, and discard their own drafts. Empty visits do not create sessions; other and expired sessions cannot list, read, update, or delete drafts. Session cleanup cascades draft records.
- All 22 Django tests passed locally with SQLite test settings; Ruff format/lint, JavaScript syntax, and `git diff --check` passed. Required CI and post-merge CI passed on the merged revisions.
- No AI provider, publishing destination, paid service, live account, advertiser spend, or deployment was added.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Drafts currently contain synthetic data only. A hosted schedule for clearing expired Django sessions remains unverified; establish retention/deletion operations before accepting real advertiser data.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before beta/production, not blockers for local synthetic UX work.

## Next action

Review the remaining Phase 2 roadmap items and select the next small, locally testable advertiser workflow slice. Keep it synthetic and ensure it cannot connect accounts, publish ads, or incur spend.
