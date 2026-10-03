# GrowthTwin — current handoff

Last verified: 2026-10-03 13:22 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, or add paid infrastructure. Change
staging only for approved synthetic verification. Phase 0 recovery, privacy,
provider, and platform checks remain release gates before external beta or
production use.

## Verified repository and staging state

- `main` is `ebc53cd09694c4f54b8f9badc3c89fa54c60df5c` after PR #214; post-merge CI `37115454629` passed, including Django checks, tests, and browser E2E. At 13:22 +0300, feature branch `docs/record-staging-rollback-v18` was clean before this documentation change. No PRs were open.
- PR #206 updated `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four focused tests, Ruff, PR CI `37105816655`, and post-merge `main` CI `37106314635` passed. It is deployed to staging.
- Heroku release v18 is current, created by rolling back to v16 (`8e29944e024554098bd1c0a90e4b7b799362370a`). A staging `/health/` GET returned HTTP 200 and that exact full commit. v17 rolled back to v15 (`c13ba96ae610778ad9a924919a7bfabb71f0b12a`); health and profile-edit E2E passed there too. Both release commands applied no migrations. Git confirms v15/v16 differ only in docs, so the rollback test covered same application code only.
- Both `runtime-dyno-metadata` and `runtime-dyno-build-metadata` were enabled before v16. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) describes the base Lab and additional build-metadata Lab. No conflicting metadata config-var names existed before enablement. Config-var values were never displayed. No resource was added.
- The authenticated synthetic report was visually checked at narrow and desktop widths using a temporary local-only account and fixed synthetic campaign; no visible layout issue was found. No real data, account connection, publication, or spend was used. The local server is not guaranteed to remain running after this session.

## Open risks and limits

- The profile-edit E2E passed on v15, v16 before rollback, v15 after rollback, and v16 after restoration. The disposable account password was reset and is not recorded. Configured-database recovery and rollback across app-code or schema changes remain unverified.
- Older anonymous session drafts from earlier versions may remain stored while hidden. Session expiry and `clearsessions` are best-effort, not a verified real-data retention guarantee; do not use real data.
- Heroku billing displayed $0.00 current usage and a $1.37 September invoice marked Pending; this is not a finalized total. Tax and one-off Scheduler cost remain unverified.
- A stopped synthetic PostgreSQL rehearsal folder remains in `%TEMP%`; recursive cleanup was blocked by tool policy after checking its exact path and stopped process. It was left untouched and no alternate deletion method was attempted. The configured local `growthtwin` data composition is also unverified.

## Next action

Read-only inventory the configured local `growthtwin` database to establish whether its contents are synthetic without printing personal values. Only if synthetic content is demonstrable, plan a full dump/restore into a newly named isolated target; otherwise leave the source untouched. Do not try alternate tools to delete the blocked temporary rehearsal folder, expose config-var values, or use real data.
