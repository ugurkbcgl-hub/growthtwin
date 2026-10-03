# GrowthTwin — current handoff

Last verified: 2026-10-03 12:09 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository and staging state

- Verified at 12:09 +0300: `main` is `8e29944e024554098bd1c0a90e4b7b799362370a` after PR #212, the main worktree was clean, and no PRs were open at that time. PR #212 required CI `37111641208` and post-merge CI `37111781360` passed. The final documentation refresh is on branch `docs/record-heroku-v16-deployment`.
- PR #206 updated `/health/` to prefer `HEROKU_BUILD_COMMIT`, fall back to `HEROKU_SLUG_COMMIT`, and report `unknown` when neither is available. Four focused tests, Ruff, PR CI `37105816655`, and post-merge `main` CI `37106314635` passed. It is deployed to staging.
- The authenticated Heroku CLI shows release v16 deployed from `8e29944e024554098bd1c0a90e4b7b799362370a` with succeeded status. A GET to staging `/health/` at 12:08 +0300 returned HTTP 200 and the same full commit. The release command reported no migrations to apply.
- Both `runtime-dyno-metadata` and `runtime-dyno-build-metadata` were enabled before v16. Heroku's official [Dyno Metadata documentation](https://devcenter.heroku.com/articles/dyno-metadata) describes the base Lab and additional build-metadata Lab. No conflicting metadata config-var names existed before enablement. Config-var values were never displayed. No resource was added.
- The authenticated synthetic report was visually checked at narrow and desktop widths using a temporary local-only account and fixed synthetic campaign; no visible layout issue was found. No real data, account connection, publication, or spend was used. The local server is not guaranteed to remain running after this session.

## Open risks and limits

- The 2026-09-30 staging profile-edit E2E passed against release v14, but has not been rerun since. Configured-database recovery and controlled staging rollback remain unverified.
- Older anonymous session drafts from earlier versions may remain stored while hidden. Session expiry and `clearsessions` are best-effort, not a verified real-data retention guarantee; do not use real data.
- A temporary synthetic PostgreSQL rehearsal folder remains from prior work; clean only the exact verified path via an allowed local operation. Staging charges and Scheduler one-off cost remain unverified.

## Next action

Rerun the pinned profile-edit E2E against v16 with the existing disposable synthetic account. Enter its password only at the hidden local terminal prompt; never record it. Then keep backup/restore and rollback as separate Phase 0 gates. Do not expose config-var values or use real data.
