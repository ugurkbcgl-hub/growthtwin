# GrowthTwin — current handoff

Last verified: 2026-09-27 22:59 (Europe/Istanbul), while PR #23's required CI check was running.

## Goal and working rules

- Target market: Türkiye; GrowthTwin serves people and organizations who want to advertise. Dental clinics are an example, not the product boundary.
- Long-term capability benchmark: an Omneky-inspired advertising workflow for brand/brief intake, multi-format creative, connected campaign launch, unified reporting, and bounded optimization. This is a north star, not a first-release parity commitment.
- Validate one advertiser workflow and one publishing destination before broad channel coverage. First workflow, platform, and review/autonomy defaults remain open.
- Routine work should not require a GrowthTwin employee. Advertisers authorize their accounts and set enforceable spend, schedule, and content limits; pause on uncertainty.
- Use synthetic data in local, CI, and staging. Keep secrets and private advertiser data out of chat, source, logs, and handoff files.
- Only approved paid infrastructure is the existing Heroku Basic dyno plus Essential-0 PostgreSQL at about USD 12/month before tax. Do not add paid services, live publishing, or advertiser spend without authorization.
- Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, and this file in order; then recheck Git, PR, and CI state live.

## Repository and review

- Repository: https://github.com/ugurkbcgl-hub/growthtwin; use feature branches and PRs; do not push directly to `main`.
- `main` at the start of this documentation update: `d79082de9de02b9f18cb973451abf6edee44cc32`. PR #21 was merged at that commit; required CI run `36339595216` passed.
- Issue #22 tracks this product-plan clarification.
- Current branch: `feature/GT-022-turkey-advertising-roadmap`. Product documentation commit: `33a6cd8`.
- PR #23: https://github.com/ugurkbcgl-hub/growthtwin/pull/23. At this snapshot, required Django system check run `36346325849` was pending. This STATE update will create another PR commit, so recheck required CI on the latest PR head before taking the next action.
- No merge has been performed for PR #23.

## Product and implementation status

- The direction is recorded in `PROJECT.md`, `ROADMAP.md`, and accepted ADR-0005: Türkiye-wide advertiser market, clinics as one example, and Omneky as a long-term functional benchmark.
- Roadmap phases now separate the local synthetic prototype, local persisted/generation slice, one verified publisher/reporting integration, limited beta readiness, and later cross-channel expansion.
- The website prototype is merged to `main`: synthetic brief → preview → simulated pause → sample report. It does not persist campaigns, call AI, connect ad accounts, publish ads, spend money, or use real metrics.
- The application stack remains Django 5.2 LTS + PostgreSQL in one modular monolith. No provider, publishing destination, production host, or new paid service was selected.
- `git diff --check` passed before the documentation PR. No application test suite was run for this documentation-only change; CI is the required check.

## Open decisions and risks

- Select the first advertiser workflow/pilot cohort and first ad destination after user discovery and checking API eligibility, approval, policy, and reporting in Türkiye.
- Define campaign review/autonomy defaults, account consent, spend caps, and stop conditions before live publishing or spend.
- Select production AI/data-processing providers and pricing only after synthetic evaluation and privacy review.
- Staging browser E2E, backup/restore, and controlled rollback remain unverified gates before external beta/production; they do not block local synthetic-data UX work.
- Omneky's public product claims do not verify GrowthTwin's platform access or feature parity.

## Next action

Recheck PR #23's required CI on its latest head, review the documentation diff, and leave the PR open unless the owner explicitly asks to merge it.
