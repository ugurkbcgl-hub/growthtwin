# ADR-0031: Default-off scoped Google TEST candidate boundary

Status: Accepted for mocked adapter validation only; not rollout
Date: 2026-10-22

Follow-up: ADR0036 adds separate closed scoped endpoints and a distinct fixed
callback URI, validated only with mocks. Earlier no-endpoint statements describe
this original slice; normal flags remain off and no actual rollout is claimed.

## Source review and adoption plan

Legacy `views.start/callback` enforce exact owner/workspace/loopback and CSRF
on start. Their LocalAuthorizationStore binds a process-local five-minute
state/PKCE attempt to owner/workspace/session. `backend.exchange_and_store`
loads the fixed TEST client, exchanges a consumed code and writes the existing
owner/workspace DPAPI file. That file and campaign ledgers have no durable
connector-generation mapping. Do not guess such mapping, reset records or copy
synthetic acceptance into an actual grant. Stop/reconcile stay on their existing
path until a separately reviewed migration exists.

This slice adds a NEW, unwired adapter; legacy views/store/backend are unchanged.
GOOGLE_ADS_SCOPED_CANDIDATE_ENABLED remains False with no environment toggle,
URL, admin action or runtime reader. Normal backend platform/DEBUG/enabled gates
also apply. Tools invoked no adapter with actual transport or credentials.

## Boundary

1. A server caller must supply authenticated owner/workspace/session and typed
   connector/generation/revision/attempt UUIDs. Under workspace then connection
   locks, validate current active ownership and quarantined metadata. The
   legacy grant's presence blocks before loading a client. Never overwrite it.
2. Freeze session HMAC, client-ID hash, generation/revision and five-minute
   timestamps in a new token-free receipt. One attempt per connection/generation;
   unresolved reserved/exchanging/candidate/uncertain history blocks new attempts
   across generations. Begin replay can replace its process-local nonce but
   cannot extend the durable deadline. Restart loses pending handshake data.
3. A SEPARATE LocalAuthorizationStore derives its binding from those immutable
   fields, validates state/PKCE/code, and consumes once. Recheck current client,
   scope, expiry and legacy-file absence, then commit EXCHANGING before outbound
   transport. Reject caller transactions. No DB locks are held across transport.
4. After response shape/scope validation, reacquire scope/attempt locks, compare
   immutable binding and current generation/state/switch/lifetime, and check
   legacy-file absence again. Only then call existing encrypted CreateNew write
   into a DIFFERENT `google-candidate-*` basename and `google-test-candidate-v1`
   envelope (owner/workspace/connection/generation/attempt/client hash/scope and
   refresh material; no access token or client secret persisted). Recheck time
   after the bounded local write. Identity remains quarantined.

Candidate is NOT an active grant, not a verified Ads TEST account and not proof
that a file/database commit is independently trustworthy. Current readers cannot
consume it. SyntheticAuthorizationAttempt is never accepted by this adapter.
No raw code/query/state/verifier/token/path goes into SQL receipt or public DTO;
start URLs and sensitive locals are excluded from repr/debug reporting.

## Rollback and uncertainty

Encrypted filesystem write and SQL commit are not one transaction. A crash or
DB failure after a possible file write may leave an inert orphan; no candidate
activation existed in this slice; ADR0032 adds advisory inspection only. Leave exchanging/uncertain evidence and require explicit
reconciliation. Do not auto-resend, auto-adopt, unlink unknown files or revoke
remote credentials. Revocation/cleanup effects have not been verified for this
candidate/account and must not endanger the preserved grant. Disabling/reverting
the feature leaves additive receipts and candidate files inert; do not drop
history or migrate/reset the old DPAPI file. Losing ownership during finalization
may leave EXCHANGING; that also cannot resume automatically.

## Evidence and remaining gates

20 new local tests plus legacy backend/OAuth/store/view tests give51 local passes
and2 PostgreSQL race skips. Mocked transport runs outside transaction; duplicate
callback and concurrent block races require CI. Simulated post-write DB failure,
legacy-file appearance, expiry/rotation/block/client/session/state changes and
secret suppression are tested. Migration0005 applied only to ephemeral test DBs;
no actual candidate/grant/client/provider/preserved DB/UI/Heroku operation.

PR306 required CI39722697389 and main CI39722996360 passed487 PostgreSQL tests
and10 browser E2E tests. ADR0032 now adds strict versioned candidate-envelope
validation/advisory readback with matching receipt, current owner/scope and
explicit reconciliation dispositions using mocks. No activation or actual file access while preparing it. Before any
live hook: endpoint/session/CSRF wiring, configured TEST target evidence, pending
handshake recovery, credential-vault/readback and orphan reconciliation, explicit
legacy adoption/rollback, scoped refresh and separately permitted stop/reconcile
must pass review. Production privacy/access/recovery/financial gates remain open.
