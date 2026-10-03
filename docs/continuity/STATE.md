# GrowthTwin — current handoff

Last verified: 2026-10-03 11:43 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository and staging state

- Verified at 11:43 +0300: `main` is `550062526b24db0ea05ee68d37b0eede34081f09` after PR #210, with a clean tree and no open PRs at that time. PR #210 required CI `37110361879` and post-merge CI `37110487277` passed. The previous five `main` runs also passed.
- PR #206 updated `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four focused tests, Ruff, PR CI `37105816655`, and post-merge `main` CI `37106314635` passed. The change has not been deployed to staging.
- The authenticated Heroku Activity page was checked read-only on 2026-10-03: latest release remains v14, deployed 2026-09-30 from `69476a62`. Staging is behind current `main`. A direct GET to staging `/health/` returned HTTP 200 with `{"status":"ok","version":"unknown"}` at 11:01 +0300.
- At 11:32 +0300 an authenticated, read-only Heroku CLI query confirmed `runtime-dyno-build-metadata` is disabled on the staging app. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) says `HEROKU_BUILD_COMMIT` requires that feature and becomes available on the next deploy. No Labs setting, release, config-var value, or secret was changed or revealed. The CLI was run from a temporary local extraction, not installed globally.
- The authenticated synthetic report was visually checked at narrow and desktop widths using a temporary local-only account and fixed synthetic campaign; no visible layout issue was found. No real data, account connection, publication, or spend was used. The local server is not guaranteed to remain running after this session.

## Open risks and limits

- The 2026-09-30 staging profile-edit E2E passed against release v14, but has not been rerun since. Configured-database recovery and controlled staging rollback remain unverified.
- Older anonymous session drafts from earlier versions may remain stored while hidden. Session expiry and `clearsessions` are best-effort, not a verified real-data retention guarantee; do not use real data.
- A temporary synthetic PostgreSQL rehearsal folder remains from prior work; clean only the exact verified path via an allowed local operation. Staging charges and Scheduler one-off cost remain unverified.

## Next action

Review the staging change sequence for enabling `runtime-dyno-build-metadata` and deploying the reviewed `main` revision; only proceed with that separate staging change after its scope is explicitly authorized. Then verify the Heroku release and `/health/` revision. Do not reveal config-var values.
