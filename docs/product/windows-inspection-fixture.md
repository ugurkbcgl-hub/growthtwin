# Fresh Windows fabricated inspection fixture

Verified: 2026-10-23 07:52 Europe/Istanbul (+03:00).

## Scope and acceptance

This is a disposable fabricated integration exercise for the closed recovered
inspection services. It is not the preserved-candidate launcher, Google access
proof, grant recovery, publishing permission or a production vault.

The CLI accepts exactly one fixed scenario and no path, credential, account,
receipt, callback or session inputs. Run from apps/web with the project Python:

```
python scripts/rehearse_inspection_fixture.py match
python scripts/rehearse_inspection_fixture.py client-changed
python scripts/rehearse_inspection_fixture.py invalid-envelope
python scripts/rehearse_inspection_fixture.py unreadable
```

Every invocation creates a NEW fabricated fixture. Do not use these commands to
retry any preserved candidate or replace a terminal permit. No .env file, saved
application SECRET_KEY, existing DB or protected OAuth files are loaded.

## Isolation and operations

- Reject invalid CLI/non-Windows/already configured Django before any fixture work.
- Force process-only test settings, random SECRET_KEY, DEBUG=False and memory
  startup settings. Deny all Django DB access during setup. Startup network
  attempts, including swallowed exceptions, prevent fixture creation.
- Create a fresh directory under original LOCALAPPDATA/Temp. Track original
  root/child identities and reject ancestor reparse points, UNC/nonlocal shapes
  and changed directory identities. This is best effort, not atomic no-follow.
- Secure the EMPTY owned directory using native icacls reset then protected
  current-user-only inheritable FullControl; independently check owner, rules
  and protected directory DACL BEFORE writing any DB/credential bytes. Existing
  directories are not accepted for ACL mutation. Child directories are checked too.
- Create/migrate only a fresh private SQLite file. DB access pins exact alias,
  engine and filename; path checks repeat on access and native ACL checks repeat
  at stage boundaries. No preserved helper, backup or schema preparation is used.
- Seed one fixed fabricated active owner with unusable password, owned workspace,
  quarantined TEST identity and current candidate receipt. All model/service flags
  are process-local overrides; source defaults stay off.
- Encrypt fixed fake client/envelope JSON with real Windows DPAPI and CreateNew;
  refuse existing output. No backend credential writer is enabled. Unreadable case
  deliberately leaves the exact derived candidate absent.
- Use the existing one-shot coordinator: original synthetic operator-session
  primitive, deterministic exclusive marker, one permit issue and the reader's
  own consumption BEFORE client/candidate observations. Fixed decoder quotas count
  attempts, including failures. A local match is advisory only.
- Deny/count provider, backend read/write and Python socket boundaries, including
  swallowed calls. This is not an OS network sandbox and does not constrain
  unrelated processes. Fixed reviewed native scripts contain no network calls.
- Verify expected disposition, CONSUMED, exact quotas, no sessions, preserved
  identity/history and terminal replay refusal. Recheck all written-file ACLs.
- Close DB connections; restore process context/env/DB settings. Delete only the
  inventoried regular private files under the pinned owned root and remove empty
  directories nonrecursively. Unexpected SQLite sidecars/files, identity or ACL
  drift stop cleanup; no recursive delete, restore, ownership change or glob.

The marker is removed only as part of disposal of the WHOLE fresh fabricated DB
fixture; the same DB is never retained with its terminal history erased. An ACL
failure before create_home returns can leave an empty owned root. A process kill
can skip cleanup. Such cases are failures, not claims of successful cleanup.

## Actual Windows evidence

All four commands above ran as separate fresh processes on Windows. Every one
returned passed=true, stage=complete, permit_state=consumed, session_count=0,
history_preserved=true, private_storage_verified=true, replay_refused=true,
cleanup_complete=true and boundary_attempts=0.

| Fresh scenario | Disposition | Fixed client decodes | Candidate decode attempts |
| --- | --- | ---: | ---: |
| match | matches_candidate | 2 | 1 |
| client-changed | client_changed | 2 | 0 |
| invalid-envelope | invalid_envelope | 2 | 1 |
| unreadable (exact file absent) | unreadable | 2 | 1 |

These prove the reviewed fabricated full flow using actual bounded DPAPI. They do
not establish actual preserved-candidate/current-client binding, token validity,
Google TEST target permission, remote token preservation, activation or advertising.
No protected-candidate database/helper/backup/credential contents were accessed.

## Targeted source checks

17 file-helper tests and13 creator admission/report tests passed; together with
17 coordinator and20 preparation/session tests,67 focused local SQLite checks
passed. Native operations are mocked in the unit tests; the Windows evidence above
is separate. Tests include private-before-write ordering, root/child identity,
existing output, sidecar retention, exact cleanup, scalar output allowlist, existing
Django refusal, raw error suppression and swallowed startup DB/network attempts.
Independent source review completed before actual Windows execution and repeated
on final fixes; Ruff and whitespace checks passed. Verify PR and CI status live.

## Next gate

Separately design/review a fixed-scope protected-candidate launcher using the SAME
preserved DB/receipt/history and existing private backup admission. Pin source,
scope, client and decoder boundary and exact one-shot terminal cleanup plan before
any actual session/permit/content read. Completed PREPARE/APPLY must not repeat.
No retry, renewal, reset, restore-over-claim, identity substitution, session-hash
rewrite, provider refresh/adoption/activation/revoke or publication is authorized
by this fabricated exercise.
