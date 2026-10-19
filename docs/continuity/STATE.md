# GrowthTwin — current handoff

Verified: 2026-10-19 14:04 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
workspace approval and DAILY/total-budget PAUSED TEST lifecycle work. Real
advertiser data, production serving and media spend remain gated.

## Repository

Base main 8ba9ea3 (PR #288 merged); its required CI 39239847336 and main CI
39240223862 passed. Current branch feat/google-total-budget-dispatch; PR #289, implementation
head f8a04de. This documentation follow-up records the PR; recheck latest
Git/head/checks/merge state live.
Reviewed green PRs may merge under standing owner authorization.

## Verified result

- New stored v2 profile binds exact total TRY/period/date-times into signed test
  consent. Uses CUSTOM_PERIOD/totalAmountMicros, no daily amount/fallback.
- Existing v1 DAILY ledger remains immutable; read/stop use its stored version.
  Create/convert through v2 is blocked. Unknown versions or mismatched period,
  amount or nonzero alternate amount cannot report a verified result.
- Browser created NEW synthetic draft 2 through the app, selected text/approved,
  then created Google TEST PAUSED with 5,000 TRY total, October 20–November 3.
  Exact budget/date/creative readback passed, repeat create reconciled same
  record, and stop confirmed stopped/PAUSED. Original draft 1 DAILY at 333.33 TRY
  November 1–15 still read/stopped successfully; no reset/conversion occurred.
- 82 focused local connection/mapper tests, Ruff and system check passed.
  Read-only reviewer found no blocker; required/post-merge CI for this new change
  must be checked after publishing. No migration, production deployment or spend.
- TEST evidence does not prove live budget exhaustion/aggregate account caps,
  advertiser financial consent, real destination, privacy, recovery or launch.
  See docs/product/google-search-live-readiness.md and ADR-0026.

## Next action

Read-only inspect current Google Cloud Ads API access level and OAuth application
publishing/review state; identify concrete production-access application gaps.
Do not submit an upgrade/grant new permissions, connect a real advertiser account
or enable spend. Prepare any later action for explicit review while retaining
privacy/recovery/financial launch gates. Reuse encrypted TEST grant for TEST work.

## Local environment

Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
owner/workspace identity, encrypted grant and both durable ledgers. Helper:
LocalAppData/Temp/growthtwin_oauth_preserved.py. Never run the older fresh-DB
bootstrap or reset existing intent. Generated local login is not recorded.
Latest browser draft-dispatch result for draft 2: stopped / PAUSED, 5,000 TRY CUSTOM_PERIOD. Original draft 1 remains stopped / PAUSED, 333.33 TRY DAILY. Preserve both ledgers and all draft IDs.
Status controls: /connections/google/draft-status/?draft=1. Server/helper
availability is ephemeral; verify before use. Grant stored with user-scoped
Windows DPAPI outside Git; reuse it rather than unnecessary reauthorization.
Read-only reviewer completed; no agent work remains running.
