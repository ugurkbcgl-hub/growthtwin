# GrowthTwin — current handoff

Last verified: 2026-10-03 01:39 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective and scope

Build a polished, low-effort, self-service paid-advertising platform for
advertisers in Türkiye across sectors. Local product development remains
synthetic-only. Do not enter real advertiser/customer/patient data, connect live
accounts, publish ads, spend media budget, add paid infrastructure, or change
staging. Phase 0 recovery, privacy, provider, and platform checks remain release
gates before external beta or production use.

## Verified repository state

- `main` is at `5112a7fe6ba9427b3faf317184ae809a461b5b6c`; the worktree was clean
  and tracked `origin/main` at verification. PR #204 is merged; required CI
  `37073305109` passed. Post-merge `main` CI `37073534626` was still running
  at 2026-10-03 01:39 +0300. No open PRs were listed then.
- PR #204 adds plain-language explanations for reach, impressions, destination
  clicks, other channel-defined interactions, delivered contact requests, and
  source-reported media spend. The text follows ADR-0017 and keeps unavailable
  values distinct from actual results. No source, live data, estimates, spend,
  or publication was added. CI passed; no local tests were run.
- PR #202 clarifies that the prototype cannot connect ad accounts or retrieve
  platform report data and offers a return link to the campaign plan. Required
  CI `37072537258` and post-merge `main` CI `37072744834` passed.
- PR #203 refreshed the continuity note after #202; required CI `37072964625`
  and post-merge `main` CI `37073158303` passed.
- The authenticated report page was not visually inspected. Opening its local
  workspace route redirected to login; no credentials were entered. The public
  prototype remains accessible at `http://127.0.0.1:8002/`.

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

## Next action

When the local synthetic workspace session is available, visually inspect the
authenticated report cards at desktop and narrow widths. Only adjust spacing or
copy if the actual page reveals a problem; keep the report source disconnected
and use no real data.
