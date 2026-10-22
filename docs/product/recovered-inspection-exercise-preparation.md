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

## Existing candidate metadata and ACL audit

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
- Migration 0007 is NOT applied and the inspection permit table does NOT exist.
- No encrypted contents were read/decrypted; current client-hash match and token/
  account access remain unverified.

The private helper is `%TEMP%\gwt_inspection_metadata_audit.py`; the prepared DB
and scope metadata remain under `%TEMP%\gwt-scoped-preparation-_jafwrsl\` as
documented in STATE. Temporary resources can vanish; verify and source-review
before reuse. The audit is not a reusable product endpoint or trusted capability.

## Next bounded preparation step

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

This slice did not back up/migrate the prepared database, issue a permit or run
the actual reader on protected data. Normal source flags stay False. A local
envelope match, if later obtained, still would not prove provider/account access.
