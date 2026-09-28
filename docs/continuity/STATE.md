# GrowthTwin — current handoff

Last verified: 2026-09-28 10:16 (Europe/Istanbul). PR #23 merged to `main` as `a27fa25cae37c3dbccac0c67ab0c2b96b9daf346`; its post-merge CI passed (`36390088871`). Replacement PR #28 (the original #25 was auto-closed when its base branch was deleted) merged to `main` as `c20cc6cdd955966ff62fe27b0e9561658fba7dbb`; CI passed on head `42cba7902d5e969a60ea8e944f220ea3ced0fd6c` (`36390382434`). PR #27 is open and now targets `main`. Its prior head `a4309ba9012d33dfaec9793f3905d8c1c229bdc3` passed CI (`36390474453`); this history reconciliation needs fresh CI before merge.

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
- PR #23 merged; post-merge CI passed on `main` at `a27fa25`.
- PR #25 was auto-closed when its base branch was deleted. Replacement PR #28 merged to `main` at `c20cc6c`; its fresh required CI passed.
- PR #27: https://github.com/ugurkbcgl-hub/growthtwin/pull/27 — open, retargeted to `main`; current merge reconciliation awaits fresh CI.
- The owner authorizes merging reviewed PRs without asking again when required CI passes. Never push directly to `main`.

## Product and implementation status

- Product direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, Omneky as a long-term benchmark.
- Phase 1's website prototype is on `main`: synthetic brief → preview → simulated pause → sample report. PR #28 added session-scoped synthetic campaign draft persistence; PR #27 adds listing/reopening and stricter expired-session access checks. No AI generation, account connection, publication, ad spend, or real metrics is included.
- Drafts use UUID identifiers and belong to anonymous Django sessions. The owner session can list, resume, edit, and discard drafts. Other or expired sessions cannot access them; empty visits do not create sessions. Django cleanup cascades drafts when it removes sessions. The UI labels data synthetic.
- Local verification on feature code: 22 Django tests passed with SQLite test settings; Ruff format/lint, JavaScript syntax, and `git diff --check` passed. CI passed for PR #28 and for PR #27's preceding head; fresh CI is required after this history reconciliation.
- No AI provider, publishing destination, paid service, live account, advertiser spend, or deployment was added.

## Open decisions and risks

- Choose the first advertiser workflow/pilot cohort and ad destination only after discovery and review of Türkiye API eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Drafts contain only synthetic data for now. A hosted schedule for clearing expired Django sessions remains unverified; establish retention/deletion operations before accepting real advertiser data.
- Production AI/data-processing providers and pricing remain undecided. Staging E2E, backup/restore, and controlled rollback remain unverified gates before beta/production, not blockers for local synthetic UX work.

## Next action

Verify fresh required CI on PR #27's current head. If it passes and the final diff remains clean, merge it to `main` and verify post-merge CI.
