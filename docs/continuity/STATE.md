# GrowthTwin — current handoff

Verified: 2026-10-19, Europe/Istanbul. Low-usage handoff: primary remaining 2%.

## Objective

Türkiye self-service advertising across industries. Current step prepares a
version-bound workspace draft for later Google PAUSED TEST dispatch. Live
advertiser data, production serving/spend remain gated.

## Repository

Base main 9403ca7 (PR #285 merged after required CI). Current branch
feat/workspace-google-draft-approval, PR #286. Head abd31c6 passed required CI 39205814580. This snapshot adds a documentation-only commit; recheck its CI and merge status. Owner standing authorization permits merging reviewed green PRs.
Recheck Git/CI before continuing. 62 focused local connection/mapper tests,
Ruff and browser review/approval passed. No Google requests in this new review.

## Verified milestones

- Encrypted Google OAuth, targeted test-account read and fixed synthetic test
  campaign/adgroup/keyword/RSA create/read/pause were previously verified through
  the app. Durable intent prevented duplicate create; Google remains PAUSED.
- Current preferred workspace creative now maps to canonical immutable JSON:
  exact source/version/selection, Google text assets, destination, budget,
  currency, dates/city and visible shortening/normalization metadata.
- Local draft review link, signed ten-minute review, CSRF explicit approval,
  owner/workspace and target/grant binding. Changed inputs invalidate current
  approval. Repeated approval stores one snapshot; old snapshots are preserved.
- Browser displayed and approved the fixed synthetic workspace package. This
  tests the owner UI flow; it is not a real advertiser's policy or financial consent.
- Migration 0007 applied only to the preserved isolated synthetic review DB;
  existing legacy/Heroku databases not touched. Preserve current DB identity,
  encrypted grant and Google operation ledger; do not recreate/reuse IDs.

## Limits

Local-only Windows process, DEBUG off, loopback, explicit owner/target, opt-in.
Review/approval does not send to Google. The existing fixed test campaign remains
separate. The sample destination example.invalid is preserved, not silently
replaced or verified. Review JSON is not a complete Google API operation; city,
budget/dates, keywords and destination need explicit test-dispatch semantics.
See ADR-0023 and current Google integration readiness. Production release,
privacy/legal, recovery and real participant usability gates remain unresolved.

## Next action

Connect the approved immutable workspace snapshot to a separate durable PAUSED
TEST dispatch operation, rejecting stale source/target/approval. Explicitly
resolve the synthetic destination and Google budget/date/targeting mapping in
review before any Google write; do not reuse/reset the fixed-test ledger.


## Local review environment and handoff

The existing synthetic review DB is under LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3. The reviewed local bootstrap is LocalAppData/Temp/growthtwin_oauth_preserved.py; do not run the older fresh-database bootstrap or recreate the owner/workspace IDs. It uses a generated disposable local password, not recorded here. The live review page is /connections/google/draft-review/?draft=1. Browser showed the current synthetic version approved. Helper/server availability is ephemeral and must be rechecked; never ask for Google reauthorization if the protected stored grant can be reused. No subagent remains running; mapper work was reviewed and integrated. No further implementation was started after low usage was confirmed.
