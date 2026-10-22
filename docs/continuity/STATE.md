# GrowthTwin — current handoff

Verified: 2026-10-22 22:20 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinics are examples. Normal
journey should not need staff. Local synthetic development authorized; real data,
production accounts/publication/spend remain behind release gates. Reviewed green
PRs may squash merge under standing owner authorization; no force, main push,
auto-merge or checks bypass. No paid resources/deployment in this slice.

## Repository and CI

Verified base main3022af4: PR317 merged. Required CI39836461900 and post-merge
main CI39837030362 successful:650 PostgreSQL tests +11 browser E2E. No open PR at
slice start. Current branch feat/recovered-inspection-storage, before its own PR/CI;
verify latest head/checks. Attachment100-item limit known; remove no unrelated items.

## Current slice — closed recovered reader, mocked storage validation

- New defaultFalse GOOGLE_ADS_RECOVERED_INSPECTION_ENABLED, plus strictlyTrue
  recovery/scoped/local-OAuth switches and existing Windows/no-DEBUG runtime guard.
  No HTTP route or env toggle. Existing origin reader and fixture rehearsal unchanged.
- Five-second process lock wait before claim. Pure configured owner/workspace and
  captured root/client/legacy/candidate derivation precedes committed direct consume.
  All file/client observations outside DB locks. Strict scope/session/digest/exact
  consumed snapshot/time rechecks plus final configuration check;60s monotonic
  acceptance budget rechecked after DB locks. Not hard cancellation of all I/O.
- Separate bounded decoder for BOTH client and candidate:131072 encrypted bytes,
  32768 plaintext characters,15s subprocess limit, held read-only stream, strictUTF8,
  duplicate-JSON rejection, BSTR cleanup, sanitized errors. Legacy contents unread.
  Reparse checks best effort; no production no-follow/crossprocess guarantee.
- Only safe advisory metadata returned; match is NOT token/account/activation proof.
  Consumption terminal even on failure/crash, no retry/renewal/result persistence.
- New54 tests:52 passed,2 PostgreSQL skips. Combined with permit/readback/retirement:
  119 total,112 passed,7 skipped. Ruff format/lint, migration drift and whitespace
  checks passed. Independent review found two gaps (late DB wait and final client
  configuration drift); corrected and regression-tested, no remaining source blocker.
- All storage/stat/PowerShell mocked; no actual file/client/credential/provider/
  protected DB/migration/Heroku/UI operation. ADR0039 records actual exercise gates.
  Required PostgreSQL CI pending at pre-PR snapshot; final closure in PR comment.

## Previous milestone — fixed-fixture inspection recovery rehearsal

- Separate defaultFalse GOOGLE_ADS_INSPECTION_REHEARSAL_ENABLED plus existing
  recovery flag. Service-only, no route/env toggle/actual reader/backend adapter.
  Admission requires fixed fabricated client hash; actual client receipt ineligible.
- Executor consumes permit directly, commits before internal in-memory probe,
  accepts no caller reader/path/envelope/snapshot. Reloads owned current quarantine,
  original digest/new-sessionHMAC/exact consumed snapshot/initial deadline after
  claim, before read and after completion. Time must remain within consume/deadline;
  no monotonic clock guarantee. Fixture client/legacy probes run outside DB locks.
- Five fixed scenarios; successful result explicitly synthetic_match. Only frozen
  request/attempt/disposition returned, no real proof or stored inspection result.
  Failure/crash does not reopen/renew permit. No actual file/path/client/provider/
  legacy operation, migration, browser, preserved Google DB or Heroku change.
- ADR0038 records fixture limits and future actual-reader gates. The current backend
  derives durable legacy location from configured owner/workspace, not session;
  future actual adapter must verify that exact mapping and current client.
- New37 tests:35 local passes,2 PostgreSQL-only skips. Combined with permit/readback/
  retirement:102 total,95 passed,7 PostgreSQL-only skips. Ruff format/lint, migration
  drift and whitespace checks passed; independent source review found no blockers.
  PR317/main CI verified above, including both executor races.

## Previous milestone — metadata-only inspection recovery permits

- DefaultFalse GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED, no env toggle,
  routes or actual reader. Short-lived new-session permit requires authenticated
  owner/workspace/current quarantined CANDIDATE and expected immutable scope.
- Additive model binds request/owner/workspace/connection/attempt/generation/revision/
  receipt digest/new sessionHMAC; original attempt/sessionhash/history unchanged.
  One permit per candidate; exact replay preserves current state and deadline;
  expired/consumed cannot renew or replace. Session/SECRET_KEY loss fails closed.
- Issue/consume reject caller atomic transactions. Workspace->connector->attempt->
  permit locks; consume commits once before returning metadata. CONSUMED is NOT
  inspection result or current-reader I/O permission. No path/client/legacy-file/
  envelope/provider operation, activation or grant adoption. Actual postread scope
  checks/reconciliation and configured-client proof remain future gates.
- New27 tests plus readback/retirement:60 local passes,5 PostgreSQL-only skips.
  Ruff format/lint, migration drift/whitespace and independent source review passed.
  Migration0007 only in ephemeral test DBs; protected actual Google DB not migrated.
  No actual file/grant/DB/provider/Heroku/browser operation. PR316 required
  CI39815782725 and main CI39816401402 passed613 PostgreSQL tests +11 browser E2E.
- ADR0037 describes limits, including no renewal and no future consumer trusting
  caller-fabricated snapshots. Future UI requires server-session/CSRF/signed consent.

## Verified milestone — inactive scoped candidate

- User completed Google general account verification and then application-specific
  device verification. No Google credential created or security setting weakened.
- Bounded preflight repeated18:57: one legacy refresh +one fixed Ads identity
  SELECT proved non-manager TEST child and registered client. Encrypted client/
  grant hashes and preserved DB stat unchanged DURING PREFLIGHT; no writes.
  This is old-grant evidence, not candidate target proof or post-consent remote
  token preservation guarantee.
- Exact expired RESERVED retired with existing locked service, stable request/
  immutable digest, atomic generation rotation. Old REJECTED/retired_before_exchange
  history retained. No provider/credential I/O in retirement, no reset/new DB.
- Reviewed wrapper requires exact old retirement proof/current generation/history,
  one start/exchange/exact-envelope write. Same synthetic owner/workspace; only
  isolated process flags enabled. Callback produced CANDIDATE and clean status URL,
  no query/fragment. No candidate refresh/Ads/adoption/activation/revoke/advertising.
- Independent read-only NEW-DB metadata/file-existence check: quarantine/revision1,
  generation chain, old rejected receipt and current candidate all consistent;
  exact candidate file exists and nonempty. Contents NOT read/decrypted. Token
  validity and candidate account access unverified. No active grant.
- Logout/process stop completed; explicit exact-DB cleanup after interrupt proved
  unusable synthetic password, session0, two retained history rows. No8002 listener.
  Normal source flags remain False. Forced stop does not guarantee finally.

## Continuation resources and limits

Same private temp DB: %TEMP%\gwt-scoped-preparation-_jafwrsl\synthetic.sqlite3.
preparation.json has exact owner/workspace/connection/generation/attempt metadata;
retirement-intent.json preserves stable old request/digest. target-preflight.json,
candidate-runtime.json and inactive-candidate-success.png are in the same directory.
No passwords/code/state/verifier/token in these notes. Temporary files may vanish.

Git-external helpers were source-reviewed. Original preparation helper creates NEW
DB and is not resume. Old one-candidate launcher requires zero history; replacement
%TEMP%\growthtwin_after_retirement_candidate_runtime.py requires exactly one old
retired row and now also cannot rerun (two rows). Never relax these guards or use
new DB/identity to bypass history. Candidate encrypted material remains inert.

Origin session and random process-only Django SECRET_KEY were lost at logout/stop.
Existing inspect_candidate requires original session HMAC; cannot recreate by a
new session/secret or mutate stored hash. Guarded actual readback not performed.
Design recovery first; no bypass, activation or provider consumption.

## Existing evidence and open gates

Local prior Google DAILY/total-budget PAUSED TEST create/read/repeat/stop verified;
drafts1/2 remain historical stopped examples, no serving/spend/cap-exhaustion proof.
ADR0027 lifecycle decisions, synthetic persistence/owner journey and fake result
examples exist; not actual grant closure/revocation/erasure integration. Existing
legacy stop/reconcile must remain separately usable; fixture UUIDs are not grant
mapping. Cloud earlier October22: API Test, OAuth External/Testing, one test user,
Branding URLs/domains incomplete; no production upgrade or scope/publish change.
Fresh deployment/campaign stagingE2E, configured recovery/schema rollback, privacy/
retention/legal/domain/contact, production vault/tenant identity, real metrics and
commercial/payment/refund/enforceable financial consent gates remain open.

## Next action

Finish this reader PR's independent review/required PostgreSQL CI, squash only if
green, and verify main CI. Then review one-shot isolated exercise preparation on
the SAME preserved candidate DB/history: private backup/schema plan (0007 not yet
applied there), ACL/location/current-client metadata, owner session/permit lifetime
and failure disposition. Do not create a new identity or reset a consumed permit.
No actual encrypted-file operation, session-hash rewrite, activation, refresh,
adoption or publishing in this slice. Normal flags remain off; actual Windows
decode, reconciliation/renewal and production launch gates remain unresolved.
