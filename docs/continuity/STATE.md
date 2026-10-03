# GrowthTwin — current handoff

Last verified: 2026-10-03 10:27 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository state

- `main` is at `a4cc44744ad512640ad13325c83e2bac094c88fe`; the worktree was clean
  after merge. PR #206 was merged at 2026-10-03 10:25 +0300. Required PR CI
  `37105816655` and post-merge `main` CI `37106314635` both passed. No open PRs
  were listed at 10:27 +0300.
- PR #206 updates `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to
  `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four
  focused endpoint tests passed locally; Ruff and `git diff --check` passed.
  This code has not been deployed to staging.
- The authenticated synthetic report was visually inspected on 2026-10-03 at
  narrow and desktop widths using a temporary local-only account and the fixed
  synthetic campaign. The metric cards, source/disconnected state, dates, and
  navigation rendered without a visible layout issue; no changes were needed.
  No real data, ad account, publication, or spend was used. Local migrations
  were applied and the local web server is available at
  `http://127.0.0.1:8002/`.
- A read-only staging `/health/` request on 2026-10-03 returned HTTP 200 and
  `version: unknown`. The saved dashboard release observations conflict, and
  the Heroku CLI is unavailable; current staging release and whether
  `runtime-dyno-build-metadata` is enabled remain unverified. Do not assume
  staging matches `main` or alter staging configuration as part of the code PR.

## Open risks and limits

- Older anonymous session drafts from earlier versions may remain stored while
  hidden. Session expiry and `clearsessions` are best-effort, not a verified
  real-data retention guarantee; do not use real data.
- Staging revision alignment, configured-database recovery, and controlled
  staging rollback remain unverified. A temporary isolated PostgreSQL rehearsal
  folder remains from prior work; do not use alternate deletion paths. Staging
  charges and the Scheduler one-off cost remain unverified.

## Next action

Read-only inspect the authenticated Heroku staging release and dyno build
metadata setting, then compare the observed release SHA with `main` and
`/health/`. Do not deploy or change staging settings until the observed state
and required metadata configuration are clear; never expose config secrets.
