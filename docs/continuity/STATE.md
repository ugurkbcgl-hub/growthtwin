# GrowthTwin — current handoff

Last verified: 2026-10-03 13:37 +0300 (Europe/Istanbul). Repository:
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

- `main` is `c4df72be050afbf06f09413cd84e21e4fe7d0c2e` after PR #215; post-merge CI `37116535983` passed, including Django checks, tests, and browser E2E. At 13:37 +0300, feature branch `docs/record-local-db-inventory` was created from clean `main`. No PRs were open before this documentation change.
- PR #206 updated `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four focused tests, Ruff, PR CI `37105816655`, and post-merge `main` CI `37106314635` passed. It is deployed to staging.
- Heroku release v18 is current, created by rolling back to v16 (`8e29944e024554098bd1c0a90e4b7b799362370a`). A staging `/health/` GET returned HTTP 200 and that exact full commit. v17 rolled back to v15 (`c13ba96ae610778ad9a924919a7bfabb71f0b12a`); health and profile-edit E2E passed there too. Both release commands applied no migrations. Git confirms v15/v16 differ only in docs, so the rollback test covered same application code only.
- Both `runtime-dyno-metadata` and `runtime-dyno-build-metadata` were enabled before v16. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) describes the base Lab and additional build-metadata Lab. No conflicting metadata config-var names existed before enablement. Config-var values were never displayed. No resource was added.
- The authenticated synthetic report was visually checked at narrow and desktop widths using a temporary local-only account and fixed synthetic campaign; no visible layout issue was found. No real data, account connection, publication, or spend was used. The local server is not guaranteed to remain running after this session.

## Open risks and limits

- The profile-edit E2E passed on v15, v16 before rollback, v15 after rollback, and v16 after restoration. The disposable account password was reset and is not recorded. Configured-database recovery and rollback across app-code or schema changes remain unverified.
- Older anonymous session drafts from earlier versions may remain stored while hidden. Session expiry and `clearsessions` are best-effort, not a verified real-data retention guarantee; do not use real data.
- Heroku billing displayed $0.00 current usage and a $1.37 September invoice marked Pending; this is not a finalized total. Tax and one-off Scheduler cost remain unverified.
- A stopped synthetic PostgreSQL rehearsal folder remains in `%TEMP%`; recursive cleanup was blocked by tool policy after checking its exact path and stopped process. It was left untouched and no alternate deletion method was attempted. The configured local `growthtwin` data composition is also unverified.
- A read-only inventory of configured local `growthtwin` (through the local `dev.ps1`, with no `DATABASE_URL` override) found 1 account with a test-marked username, whose email is blank or in a reserved example domain; 0 demo profiles; 8 anonymous campaign drafts that do not match the current fixed synthetic sample; 9 sessions; and 1 workspace campaign with the fixed synthetic base but stored creative versions. No usernames, emails, or content values were output. Those older drafts and creative versions remain unclassified; no full data-bearing dump or restore was attempted.

## Next action

Continue Phase 2 locally with a provider-neutral content-generation boundary and synthetic fixture data. Before implementation, read `AI_PROVIDERS.md` and relevant accepted ADRs; keep real providers, accounts, and customer content out. Leave the configured local database untouched while its legacy drafts remain unclassified. Do not try alternate tools to delete the blocked temporary rehearsal folder or expose private values.
