# GrowthTwin — current handoff

Last verified: 2026-10-03 11:56 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository and staging state

- Verified at 11:56 +0300: `main` is `c13ba96ae610778ad9a924919a7bfabb71f0b12a` after PR #211, the main worktree was clean, and no PRs were open at that time. PR #210 required CI `37110361879` and post-merge CI `37110487277` passed; PR #211 required CI `37110674347` and post-merge CI `37110805928` passed. Current docs follow-up is on branch `docs/record-heroku-dyno-metadata-dependencies`.
- PR #206 updated `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four focused tests, Ruff, PR CI `37105816655`, and post-merge `main` CI `37106314635` passed. It is now deployed to staging in release v15.
- The authenticated Heroku CLI shows release v15 deployed from `c13ba96` with succeeded status. A GET to staging `/health/` at 11:54 +0300 returned HTTP 200 with `{"status":"ok","version":"unknown"}`. The deploy's release command reported no migrations to apply.
- At 11:53 +0300, both `runtime-dyno-build-metadata` and `runtime-dyno-metadata` were enabled on the staging app. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) requires the base Lab for environment metadata and the additional build-metadata Lab for `HEROKU_BUILD_COMMIT`; metadata becomes available on the next deploy. The base Lab was enabled after v15, so the revision remains unverified. Conflicting metadata config-var names were absent before enablement. Config-var values were never displayed. No resource was added.
- The authenticated synthetic report was visually checked at narrow and desktop widths using a temporary local-only account and fixed synthetic campaign; no visible layout issue was found. No real data, account connection, publication, or spend was used. The local server is not guaranteed to remain running after this session.

## Open risks and limits

- The 2026-09-30 staging profile-edit E2E passed against release v14, but has not been rerun since. Configured-database recovery and controlled staging rollback remain unverified.
- Older anonymous session drafts from earlier versions may remain stored while hidden. Session expiry and `clearsessions` are best-effort, not a verified real-data retention guarantee; do not use real data.
- A temporary synthetic PostgreSQL rehearsal folder remains from prior work; clean only the exact verified path via an allowed local operation. Staging charges and Scheduler one-off cost remain unverified.

## Next action

Merge the docs follow-up after required CI passes, then deploy the reviewed `main` commit to the existing staging app and verify release status plus `/health/` commit alignment. Do not reveal config-var values or add infrastructure.
