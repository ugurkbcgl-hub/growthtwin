# GrowthTwin — current handoff

Verified: 2026-10-22 23:11 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinics are examples. Normal
journey should not need staff. Local synthetic development authorized; real data,
production accounts/publication/spend remain behind release gates. Reviewed green
PRs may squash merge under standing owner authorization; no force, main push,
auto-merge or checks bypass. No paid resources/deployment in this slice.

## Repository and CI

Verified base mainf6aa75d: PR318 merged. Required CI39843136730 and main
CI39843726808 passed708 PostgreSQL tests +11 browser E2E. Bounded official-mirror
dependency installation passed both; old cancelled runs are not the proof.
No open PR at slice start. Current branch chore/windows-inspection-rehearsal,
before its own PR/CI. Verify latest head/checks and final closure comment.
Attachment100-item limit known; remove no unrelated items.

## Current slice — actual Windows synthetic rehearsal and RO preparation audit

- New reviewed harness scripts/rehearse_inspection_storage.py ran actual DPAPI
  on fresh disposable fabricated files only:12 checks passed, cleanup complete,
  forbidden boundary attempts0. DB/network guards before Django setup; legacy
  client/read/transport/path forbidden. No saved secret/DB or protected-file input.
- Turkish JSON and30000-character payload round-tripped. Error/size/missing cases
  rejected. Oversized text hit ciphertext cap first; later plaintext cap NOT
  independently exercised. No limit changes. Exact nonrecursive cleanup succeeded.
- Separate source-reviewed RO immutable SQLite + exact-file metadata/ACL audit
  verified SAME preserved DB unchanged (hash/size/mtime), coherent two-attempt chain,
  unusable owner password/session0, regular nonempty candidate/client and private
  root/files ACLs; legacy path absent for this identity. No encrypted content read.
- Actual DB still lacks migration0007 and permit table. No backup/schema write,
  permit, actual recovered readback, provider, activation or Heroku operation.
- New preparation evidence/plan in docs/product/recovered-inspection-exercise-preparation.md.
  Private reviewed audit helper: %TEMP%\gwt_inspection_metadata_audit.py (temporary,
  verify/source-review before reuse). No raw metadata/secret values in public output.
- Ruff format/lint/whitespace passed. No new local Django suite for harness/docs;
  actual12-case rehearsal and RO audit are the focused validation. Required CI
  pending at this snapshot; independent source review passed before operations.

## Previous milestone — closed recovered reader, mocked storage validation

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
- New58 tests:56 passed,2 PostgreSQL skips. Combined with permit/readback/retirement:
  123 total,116 passed,7 skipped. Four real Django reporter-filter checks verify
  direct session-bearing helpers; entry already protects its nested frames.
  Ruff format/lint, migration drift and whitespace
  checks passed. Independent review found two gaps (late DB wait and final client
  configuration drift); corrected and regression-tested, no remaining source blocker.
- All storage/stat/PowerShell mocked; no actual file/client/credential/provider/
  protected DB/migration/Heroku/UI operation. ADR0039 records actual exercise gates.
  PR318/main CI verified above. Actual protected-file readback remains unperformed.

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
Separate recovery adapter now exists; it requires the backup/schema/permit steps
in Next action before an actual exercise. No bypass, activation or provider use.

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

Finish this harness/docs PR's review/required CI, squash only if green, verify main
CI. Then create a private verified backup of the SAME preserved candidate DB and
review its exact migration plan: ONLY forward connections.0007_candidate_inspection_permit.
Apply that additive migration only after backup/independent plan review; recheck
old history unchanged/zero permits. Actual one-shot client-bound inspection remains
a subsequent reviewed operation with explicit scope/session/expiry/failure handling.
Never reset a consumed permit, restore over a claim, rewrite session hashes, or
create another identity to bypass refusal. Normal flags off; no provider/refresh/
adoption/activation/publishing. Reconciliation/renewal and launch gates stay open.
