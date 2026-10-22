# Recovered inspection — isolated exercise preparation

Verified on 2026-10-22, Europe/Istanbul. This is preparation evidence, not a
completed actual candidate inspection or permission to activate a grant.

## Windows decoder rehearsal

`apps/web/scripts/rehearse_inspection_storage.py` runs in a fresh process on Windows
using config.test_settings, an ephemeral secret and no saved database configuration.
Before Django setup, DB connections and Python network-connect APIs are guarded; legacy
client/read/transport/path operations are also forbidden during fixture work.
Only a fresh private temporary directory is used. Existing protected credentials
are not fixture inputs. The existing writer secures that directory to the current
user before the helper creates further fixed fabricated files.
These application guards are not an operating-system network sandbox.

Actual execution returned passed=true, checks_passed=12, cleanup_complete=true,
forbidden_boundary_attempts=0. Both valid cases round-tripped, including Turkish
JSON content and a 30000-character payload. Duplicate-key, malformed JSON,
non-object JSON, NaN, empty file, invalid UTF-8, invalid ciphertext, encrypted-size
overflow, missing file and oversized text were rejected. Cleanup removed only
the exact fixture manifest and empty directory; no recursive deletion.

The oversized-text ciphertext exceeded the encrypted-size cap first:
plaintext_limit_independently_exercised=false. This does not independently prove
the later 32768-character guard. Limits were not changed to force that result.
The successful rehearsal proves the tested Windows DPAPI paths/error cases on
this machine/user, not cross-user access, atomic no-follow, production vault,
remote account permission or a protected candidate match.

## Existing candidate metadata and ACL audit - before schema preparation

A separately source-reviewed, one-shot private helper performed immutable,
read-only SQLite queries on the SAME prepared database. It refused WAL/SHM/journal
companions, disabled extension loading, permitted only fixed reads/count/substr,
checked table types and compared DB hash/size/mtime afterward. Preparation metadata
was bounded and treated as typed scope data; no arbitrary path was followed.
Credential paths and ancestors were checked for reparse points. Get-Acl inspected
only the exact protected root, fixed client and receipt-derived candidate.

Verified booleans:

- Database bytes/size/mtime unchanged during the audit; no writes or migration.
- Owned inactive identity and old-retired -> current-candidate generation chain
  coherent; preparation attempt IDs match. Exactly two retained attempts.
- Synthetic owner password remains unusable; zero sessions.
- Candidate and fixed client files are regular/nonempty; root/files have
  current-user-only allow rules and the root DACL is protected.
- Legacy path for THIS owned identity is absent. Other legacy identities were
  not enumerated, opened or changed.
- At that audit, migration 0007 was NOT applied and the permit table did NOT exist.
- No encrypted contents were read/decrypted; current client-hash match and token/
  account access remain unverified.

The private helper is `%TEMP%\gwt_inspection_metadata_audit.py`; the prepared DB
and scope metadata remain under `%TEMP%\gwt-scoped-preparation-_jafwrsl\` as
documented in STATE. Temporary resources can vanish; verify and source-review
before reuse. The audit is not a reusable product endpoint or trusted capability.

## Preparation sequence - schema steps completed below

1. Reconfirm the exact same database/scope/history and absence of live sessions,
   unresolved competing work and any existing permit. Never create a fresh identity
   or clear history to make an exercise pass.
2. Create a private, verified backup of that database, with matching bytes and a
   recorded metadata snapshot. No token copy/export is needed. Do not automatically
   restore over a consumed claim or discard permanent receipt history.
3. Compute the actual migration plan before any schema write. It must contain ONLY
   forward `connections.0007_candidate_inspection_permit`; otherwise stop and review.
   Apply that additive migration only after backup and independent plan review.
   Recheck old identity/attempt/generation metadata unchanged and zero permits.
4. Separately review a one-shot local launcher: exact owner/workspace/connection/
   candidate/generation/revision/digest, short-lived fresh server-session binding,
   explicit scope confirmation, process-only flags and no external HTTP endpoint.
   Verify the bounded configured-client hash without exposing its contents, then
   issue/consume at most one permit and return only the advisory disposition.
5. Define failure handling BEFORE claiming. A consumed/expired permit is terminal;
   no rerun, new request, reset, backup restore or fabricated session-hash rewrite
   may bypass it. Preserve uncertainty for explicit reconciliation. Retain the same
   candidate/history; no OAuth, refresh, adoption, activation, revoke or publishing.

The earlier rehearsal slice did not back up/migrate the prepared database, issue a permit or run
the actual reader on protected data. Normal source flags stay False. A local
envelope match, if later obtained, still would not prove provider/account access.

## Two-phase helper preparation and usage handoff — 2026-10-22

A private, fixed-scope helper was prepared at
`%TEMP%\gwt_prepare_inspection_schema.py`, outside the repository. It has separate
PREPARE and APPLY phases; neither phase was executed at the PR320 handoff. There
was no actual backup or computed actual migration plan at that point. Source preparation is not
migration evidence. The prepared DB file still exists and the preparation pointer
was absent at the handoff check; full metadata admission must be repeated.

Independent source review identified and prompted these changes: verify the
reviewed audit's bounded source bytes against a pinned SHA before executing those
same bytes; forbid subprocesses throughout Django startup/plan/migration; reject
reparse paths before leaf hashing/ACL checks; verify the fresh backup root's private
ACL before copying; bound the manifest before writing its pointer; require typed
manifest versions. PREPARE uses immutable read-only SQLite; APPLY uses mode=rw to
refuse creation of a missing database. Direct MigrationExecutor avoids management
command post_migrate writes to existing permission/content-type tables.

The proposed preservation comparison covers preexisting application schema/data
and migration history, allowing only the added 0007 recorder row and the new empty
permit table/indexes. SQLite internal sqlite_sequence is excluded; a recorder
sequence increment is expected and must not be called byte-identical preservation.
No backup restoration, permit claim, protected credential read, provider call or
activation is included. Source checks are not an operating-system sandbox or an
exclusive cross-process lock.

Ruff with apps/web/pyproject.toml and Python compilation passed for the private
helper. The five-hour usage window reported100% consumed with additional credits
enabled; AGENTS' low-usage handoff rule stopped execution before PREPARE/APPLY.
At that handoff, independent source review found no remaining PREPARE blocker;
it had not approved APPLY or verified any execution result. It requested moving
success reporting after the outer network counters, renewed source review,
admission/PREPARE and separate actual-plan review before APPLY. These requests
were subsequently completed as documented below.
Historical PR320 helper SHA256 (code only, not credential data):
4668e9bb711fc25b3bf6eb69d68fb1087607e261cd30b99ed7e42269855db409.
The current executed helper has the different reviewed hash recorded below.
Temporary helpers can disappear. Do not recreate the database/identity to bypass
missing resources or history; do not interpret this handoff as execution approval
for an unchecked helper.

## Verified same-database backup and schema preparation - after PR320

On2026-10-22 23:49 Europe/Istanbul, the owner requested completion after the usage
handoff; with additional credits enabled, the bounded operation resumed under that
current instruction. The success-reporting refinement now captures phase output
until the outer network guards pass. Independently reviewed final helper SHA256:
d5742e54d168e7e31d64e8ff2ecb68083f7747be0d7c25192d68efabbc69acee.

Three PREPARE attempts stopped before any database copy: the first fresh directory
retained other explicit ACL entries; Set-Acl alternatives required unavailable
privileges. All three failed-attempt directories remained empty, without backup or
manifest. A focused empty-owned-directory check verified native icacls /reset then
/inheritance:r /grant:r for the current SID. The final helper requires a fresh empty
owned directory, checks both native exit codes and verifies strict private ACLs
BEFORE any database bytes are copied. No original-resource ACL or owner was changed.
The empty failed-attempt directories were retained; no recursive cleanup occurred.

Successful PREPARE then verified:

- SAME preserved candidate DB; exact identity/history, disabled login/session0,
  no8002 listener and no SQLite companion journals admitted again.
- Backup bytes and integrity/data snapshot equal to the unchanged original.
- Backup root, backup and manifest current-user-only ACLs; protected root DACL.
- Actual immutable read-only migration plan: ONLY forward
  connections.0007_candidate_inspection_permit, one CreateModel operation.

Independent review read the actual private manifest, checked source/preparation/
migration/DB/backup hashes and ACLs and found no APPLY blocker. APPLY reran admission
and the exact plan, then used MigrationExecutor once against mode=rw on that SAME
existing file. Successful postconditions: only0007 added to migration history;
preexisting application schema and table-data fingerprints unchanged; new permit
table/indexes only; permit_count=0; backup hash unchanged. Internal SQLite tables
remain excluded from that preservation comparison. No management-command
post_migrate permission/content-type writes, restore or APPLY retry occurred.

A separate post-operation read-only audit also passed: current inactive identity,
retained attempt/generation chain and preparation IDs coherent; session0; migration
and permit table present; exact protected client/candidate regular and private;
legacy absent for this identity. Its database_unchanged=true means unchanged DURING
that later audit, not byte-identical across the intentional schema migration.

Exact backup location is in the bounded private pointer
%TEMP%\gwt-scoped-preparation-_jafwrsl\inspection-schema-preparation.json.
Resolve that pointer with the existing no-reparse/typed/path checks, not by choosing
an arbitrary matching directory. Backup and manifest remain outside Git. Temporary
resources may disappear; never reset/recreate identity/history or restore over a
future consumed claim. PREPARE/APPLY are now completed, not reusable resume steps.

No permit was issued/consumed. No protected credential content was read/decrypted;
no OAuth, refresh, provider, adoption, activation, advertising or deployment occurred.
Default source flags stay False. Ruff/compilation and focused actual operational
checks passed; no new local Django suite was run for this private helper/docs slice.
Next is a separately reviewed one-shot inspection launcher and failure plan as in
sequence steps4-5, before any permit claim or protected-file read.
