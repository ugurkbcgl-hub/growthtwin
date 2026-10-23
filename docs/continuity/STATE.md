# GrowthTwin — current handoff

Verified: 2026-10-23 06:53 Europe/Istanbul (+03:00).

## Objective and authorization

Türkiye self-service advertising across industries; clinics are examples. Normal
journey should not need staff. Local synthetic development authorized; real data,
production accounts/publication/spend remain behind release gates. Reviewed green
PRs may squash merge under standing owner authorization; no force, main push,
auto-merge or checks bypass. No paid resources/deployment in this slice.

## Repository and CI

Verified base mainff32417434e7722f770486d5f2a2c1774573a696: PR323 merged;
required CI39856678034 and main CI39857094533 passed722 PostgreSQL+11 browser
E2E. No open PR at slice start. Current branch fix/inspection-session-expiry,
before its source-review/PR/required CI. Verify final PR/closure comment.
Attachment100-item limit known. Work queue issue322.

## Scheduler incident and current authorization

Owner extended work to2026-10-23 18:00 Europe/Istanbul; stop new work17:40.
At06:47 automation was ACTIVE but last_run_at=null and zero run records; no Git/PR
progress after PR323 at00:25. Cause unverified; do not claim configured timer is
working. Observed next trigger06:59 must be checked against actual run evidence.
Direct work resumed on owner's complaint; no additional authorization required.
No auth/production/spending/privacy gate is overridden by the schedule.

## Current slice - session expiry acceptance and preservation

- Captures original expire_date before insertion; verifies exact expiry at reload
  and cleanup. Changed expiry retained for explicit review, never silently deleted.
- validate() checks original encoded row, owner/workspace and original wall-clock/
  300s monotonic window. Rechecks BOTH clocks after all DB queries to refuse late
  success. No hard cancellation of arbitrary blocked queries is claimed.
- 20 focused fabricated local tests passed (prior14+6 new), including scope drift,
  expiry/clock drift and delayed final query; Ruff from apps/web and whitespace pass.
- No real preserved session/permit/decode/provider use. Source remains plan-only;
  full single-attempt execution/failure integration is still the next bounded task.

## Previous milestone - read-only preparation and synthetic bootstrap

PR323 added a fixed Windows read-only plan using pinned helper/audit and exact
private backup/post0007 history/schema/data admission; actual read-only plan passed
with permit0/session0, no protected credential contents read, no current-client
proof or execute capability. Its separate synthetic operator-session primitive
was tested only with fabricated DB rows, not the preserved candidate. Password
unchanged; explicit local operator authority is not password/public authentication.

## Previous milestone - same-DB backup and only forward0007 completed

- Owner requested completing next steps after usage handoff; additional credits
  enabled, bounded work resumed under current instruction. No change to standing
  low-usage rule or production permissions.
- Private helper reporting now waits for outer network checks. Three PREPARE ACL
  failures stopped BEFORE copying DB data; fresh failed directories remain empty.
  Independently reviewed native ACL handling on fresh empty owned directory fixed
  this; strict private ACL checked before copying. No original ACL/owner changed.
- PREPARE passed: same DB admission/history/session0, private backup byte/snapshot
  equivalence, unchanged source DB and actual ONLY-forward connections.0007 plan.
  Independent review checked actual manifest/hash/ACL/migration source before APPLY.
- Exactly one APPLY passed: original application schema/table-data/history preserved
  except added0007 recorder row; new permit table/indexes only; permit_count0;
  backup unchanged. SQLite internals excluded; no restore/APPLY retry/post_migrate.
- Later separate RO audit passed: coherent current owned inactive candidate/history,
  preparation IDs, disabled login/session0, migration0007 and permit table present,
  exact client/candidate regular/private and identity legacy absent. DB unchanged
  DURING later audit; schema migration intentionally changed original DB bytes.
- Ruff/compilation passed. No new local Django suite. No permit claim, protected
  credential content read/decryption, provider, activation, publishing or deployment.
- Full evidence/helper hash: docs/product/recovered-inspection-exercise-preparation.md.

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
Separate recovery adapter exists. Backup/schema preparation is now complete;
reviewed launcher/scope/session/permit/failure plan still required before actual
inspection. No bypass, activation or provider use.

Private backup pointer: same prepared root's inspection-schema-preparation.json;
read only that exact pointer with typed/path/no-reparse checks. It identifies the
private backup/manifest outside Git. Completed PREPARE/APPLY must not be rerun.
Private helper %TEMP%\gwt_prepare_inspection_schema.py final reviewed SHA256:
d5742e54d168e7e31d64e8ff2ecb68083f7747be0d7c25192d68efabbc69acee.

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

Close this expiry PR after independent review/green required CI and verify
main CI. Then integrate and rehearse ONE bounded single-attempt local inspection
launcher using the reviewed synthetic-owner session primitive and the SAME candidate.
Complete terminal failure/cleanup behavior, exact scope/source/receipt pins,
process-only flags and fixed decoder boundary; independently review before any
real session bootstrap, permit claim or protected content read. Existing bounded
reader proves client binding only AFTER consumption; no pre-claim decode bypass.
No retry/renewal/reset/restore/new identity/session-hash rewrite. PREPARE/APPLY are
complete; preserve history/backup. No provider/refresh/adoption/activation/publishing.
By17:40 stop new implementation and finish/preserve work; final report by18:00
Europe/Istanbul2026-10-23 and pause heartbeat. Authentication blockers skip to
independent safe roadmap work; no gates weakened to fill the overnight window.
