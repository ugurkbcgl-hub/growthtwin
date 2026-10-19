# GrowthTwin — current handoff

Verified: 2026-10-19 13:30 Europe/Istanbul (+03:00).

## Objective

Türkiye self-service advertising across industries. Local synthetic Google
workspace draft → approval → PAUSED TEST create/read/stop now works. Live
advertiser data, production serving and media spend remain gated.

## Repository

Base main 0266140 (PR #286 merged). Current branch
feat/workspace-google-test-dispatch; working changes prepare the next PR.
Recheck branch/head/open PR and CI live; this snapshot precedes its own commit.
Owner standing authorization permits merging reviewed green PRs.

## Verified result

- Existing encrypted OAuth grant reused; no new authorization or secrets entered.
- A second signed, explicit TEST consent shows original versus example.com URL,
  inclusive daily TRY budget (floor to kuruş), Türkiye-account date-times,
  Ankara/PRESENCE and fixed synthetic EXACT keyword. Original approval unchanged.
- Exact non-manager test child, TRY, Türkiye time zone and one active Ankara/TR
  city constant verified. Google v25 requires startDateTime/endDateTime; initial
  validation rejected old fields without creating anything. Corrected validation
  passed, then browser create/read/stop confirmed selected text and PAUSED.
- New GoogleDraftDispatch ledger is one per draft, separate from the fixed test
  ledger. Intent committed before create; uncertain/repeated requests never
  resend. Source/approval/target checked again before the write.
- Independent owner-only status page supports read/stop after source edits.
  Remote drift may remain uncertain after pause; changed identity requires review.
- 71 focused local connection/mapper tests passed, plus Ruff and migration
  consistency checks. Reviewer found no remaining blocker for this local scope.
  Required CI and final merge state must be checked after pushing the PR.
- Migration 0008 applied only to the preserved isolated synthetic DB. Legacy and
  Heroku databases untouched. No production or live campaign/spend enabled.

## Next action

Assess first live Google Search readiness against the existing launch gates:
identify exact remaining advertiser-account authorization, real destination,
platform-enforced spend/schedule limits, policy/privacy and recovery evidence.
Produce one concrete bounded implementation slice; do not enable live serving
or spend until its required inputs and explicit financial authorization exist.

## Local environment

Preserve LocalAppData/Temp/gwt-oauth-isolated-wq0dp50j/synthetic.sqlite3,
owner/workspace identity, encrypted grant and both durable ledgers. Helper:
LocalAppData/Temp/growthtwin_oauth_preserved.py. Never run the older fresh-DB
bootstrap or reset existing intent. Generated local login is not recorded.
The browser /connections/google/draft-dispatch/ displayed stopped / PAUSED.
Status controls: /connections/google/draft-status/?draft=1. Server/helper
availability is ephemeral; verify before use. Grant stored with user-scoped
Windows DPAPI outside Git; reuse it rather than unnecessary reauthorization.
Read-only reviewer completed; no agent work remains running.
