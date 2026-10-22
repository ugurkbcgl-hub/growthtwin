# ADR-0032: Scoped candidate envelope and advisory reconciliation inspection

Status: Accepted for mocked validation only; not runtime rollout
Date: 2026-10-22

## Decision

Extend ADR0031 with a shared strict version-one codec and an unwired, default-off
inspection service. The writer uses the same codec. Only the exact nine keys are
accepted; schema, owner/workspace, connector/generation/attempt UUID strings,
client-ID hash and scope must equal the owned receipt binding. Refresh material
must be nonempty bounded printable ASCII (maximum8192 characters). Extra keys,
legacy unversioned payloads, unknown versions and mismatches fail validation.
The codec validates an already decoded dictionary; it is not a signature,
duplicate-JSON-key detector, file fingerprint or remote token validity proof.

The public inspection DTO contains receipt metadata and an allowlisted advisory
disposition only, never credential material or paths. Normal adapter, platform,
DEBUG, owner/session and caller-transaction gates apply. Under owned workspace
then connector locks, verify receipt consistency and current quarantined scope.
Only CANDIDATE can read its derived candidate-only path. RESERVED is pending;
EXCHANGING/UNCERTAIN require reconciliation; REJECTED stays rejected. Old or
blocked generations return scope_changed without reading. A possible orphan
cannot promote a receipt. No metadata/file mutation, retry, revoke, unlink,
activation, network call, URL or current-runtime integration is added.

Release DB locks for bounded encrypted read/client inspection; keep the existing
process lock. Preserve legacy contents and deny on legacy presence. Reacquire
owned locks and compare all immutable receipt fields/state/reason and current
scope after I/O. Recheck client binding and legacy absence before reporting
matches_candidate. Missing/decrypt/configuration failures are unreadable, never
proof of absence; mismatched contents are invalid_envelope. Client changes and
legacy presence have explicit dispositions. Ownership loss/inconsistent metadata
raise scoped denial. A match is advisory at inspection time, never permission
to refresh/create/activate or independent filesystem/SQL recovery proof.

The five-minute lifetime remains the handshake/write deadline. It does not expire
a committed inactive candidate; inspection still verifies timestamp consistency,
current generation/revision/quarantine and configured client. It does not prove
that the remote refresh material remains valid. Any later consumer must validate
scope again at its own operation boundary and pass separate rollout gates.

## Evidence and remaining work

All client, legacy path, transport, encrypted reads/writes use fabricated mocks.
Focused candidate readback/adapter/backend tests:55 local passes,3 PostgreSQL-only
race skips. New readback coverage includes21 local tests and1 PostgreSQL race
that permits a concurrent block to commit while a mocked read waits. No migration
or actual credential/provider/preserved DB/fixture/browser/Heroku operation.
Required PostgreSQL CI and independent review are recorded in the PR/STATE.

Next: design and rehearse owner/session/CSRF endpoint wiring using explicit
fixtures, keeping the real adapter off. Actual hook rollout still requires
configured TEST target proof, pending/orphan recovery handling, explicit legacy
adoption/rollback, scoped refresh and separately permitted stop/reconcile.
Production privacy/access/recovery/financial gates remain open.
