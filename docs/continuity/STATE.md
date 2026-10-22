# GrowthTwin — current handoff

Verified: 2026-10-22 19:36 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinics are examples. Normal
journey should not need staff. Local synthetic development authorized; real data,
production accounts/publication/spend remain behind release gates. Reviewed green
PRs may squash merge under standing owner authorization; no force, main push,
auto-merge or checks bypass. No paid resources/deployment in this slice.

## Repository and CI

Verified base main6f120ca: PR315 merged. Required CI39811645737 and post-merge
main CI39812128522 successful:586 PostgreSQL tests +11 browser E2E. No open PR at
slice start. Current branch feat/inspection-recovery-permits, before its own PR/CI;
verify latest head/checks. Attachment100-item limit known; remove no unrelated items.

## Current slice — metadata-only inspection recovery permits

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
  No actual file/grant/DB/provider/Heroku/browser operation. CI pending at snapshot.
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

Finish this PR's independent review/required PostgreSQL CI, squash only if green,
and verify main CI. Then implement a separately reviewed MOCKED inspection executor
that consumes this permit directly before bounded I/O and rechecks immutable scope,
time, configured-client/legacy-file conditions after read. No real encrypted-file
operation, session-hash rewrite, activation, refresh, adoption or publishing. Normal
flags remain off; reconciliation/renewal and production gates remain unresolved.
