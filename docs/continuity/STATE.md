# GrowthTwin — current handoff

Last verified: 2026-10-03 13:05 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository and staging state

- At 13:05 +0300, PR #214 (`docs/verify-staging-e2e-v16`, commit `e6c5dd6`) is open against `main` `5c70fa2db5e16e6fb5f3f69e3d083da2dc4e892d`. Required CI `37115205743` passed, including Django checks, tests, and browser E2E. The main worktree was clean before this documentation change. Latest main CI `37112420329` succeeded.
- PR #206 updated `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four focused tests, Ruff, PR CI `37105816655`, and post-merge `main` CI `37106314635` passed. It is deployed to staging.
- The authenticated Heroku CLI shows release v16 deployed from `8e29944e024554098bd1c0a90e4b7b799362370a` with succeeded status. A GET to staging `/health/` at 12:08 +0300 returned HTTP 200 and the same full commit. The release command reported no migrations to apply.
- Both `runtime-dyno-metadata` and `runtime-dyno-build-metadata` were enabled before v16. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) describes the base Lab and additional build-metadata Lab. No conflicting metadata config-var names existed before enablement. Config-var values were never displayed. No resource was added.
- The authenticated synthetic report was visually checked at narrow and desktop widths using a temporary local-only account and fixed synthetic campaign; no visible layout issue was found. No real data, account connection, publication, or spend was used. The local server is not guaranteed to remain running after this session.

## Open risks and limits

- The staging profile-edit E2E passed against v16 on 2026-10-03. The disposable account password was reset for the run and is not recorded. Configured-database recovery and controlled staging rollback remain unverified.
- Older anonymous session drafts from earlier versions may remain stored while hidden. Session expiry and `clearsessions` are best-effort, not a verified real-data retention guarantee; do not use real data.
- A temporary synthetic PostgreSQL rehearsal folder remains from prior work; clean only the exact verified path via an allowed local operation. Staging charges and Scheduler one-off cost remain unverified.

## Next action

Merge PR #214 under the owner's standing authorization. Then clean the stopped temporary PostgreSQL rehearsal directory only after checking its exact resolved path and stopped server; keep configured-database backup/restore and controlled rollback as separate Phase 0 gates. Do not expose config-var values or use real data.
