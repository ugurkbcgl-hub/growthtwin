# GrowthTwin — current handoff

Last verified: 2026-10-03 01:31 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository state

- `main` is at `2e521632c74f321be9d78cb729fddfd7d17d0066`; the worktree was clean
  and tracked `origin/main` at verification. PR #202 is merged; its required CI
  `37072537258` and post-merge `main` CI `37072744834` passed. No open PRs
  were listed after the merge.
- PR #202 clarifies that the local prototype does not yet support ad-account
  connection or platform report retrieval, so real campaign results cannot be
  shown. It adds a direct return link to the campaign plan. The change adds no
  account access, live data, estimates, spend, or publishing. CI passed; no
  local tests or authenticated browser visual review were performed.
- PR #201 refreshed this continuity snapshot; required CI `37072125194` and
  post-merge `main` CI `37072338290` both passed.
- PR #200 clarified that the example budget is media budget only, separate from
  GrowthTwin fees, which the prototype does not calculate. Required CI
  `37071209396` and post-merge `main` CI `37071471148` passed. The local public
  page at `http://127.0.0.1:8002/` was visually checked for the note and no
  visible horizontal overflow.
- The report is an owner-scoped, provider-free shell. Metrics remain unavailable
  without a verified source; the shell does not show simulated results or
  connect accounts.

## Open risks and limits

- Older anonymous session drafts from earlier versions may remain stored while
  hidden. Session expiry and `clearsessions` are best-effort, not a verified
  real-data retention guarantee; do not use real data.
- Heroku release v14 (`69476a62`) and `/health/` revision `unknown` were last
  recorded on 2026-10-01 and have not been rechecked in this session. Do not
  infer current staging state.
- Configured-database recovery and controlled staging rollback remain
  unverified. A temporary isolated PostgreSQL rehearsal folder remains from
  prior work; do not use alternate deletion paths. Staging charges and the
  Scheduler one-off cost remain unverified.
- No implementation work is currently in progress.

## Next action

Audit the six authenticated report metric labels and unavailable explanations
for plain-language clarity without erasing channel-specific meaning. Keep the
provider disconnected and values unavailable; make one small local synthetic
UX change only if the source review substantiates it.
