# ADR-0037: New-session inspection recovery permit metadata

Status: Accepted for synthetic protocol validation only; actual readback unwired
Date: 2026-10-22

## Problem and scope

The isolated inactive candidate exists, but its original session and process-only
SECRET_KEY were lost at logout/shutdown. Existing inspect_candidate correctly
requires the original session HMAC. Do not change its receipt/hash, reconstruct a
fictional session, copy fixture proof into an actual grant or weaken that reader.

This slice adds a separate metadata-only issue/consume protocol. It has no HTTP
route, credential/path/envelope/transport operations, reader callback or result
finalization. GOOGLE_ADS_CANDIDATE_INSPECTION_RECOVERY_ENABLED is False without an
environment toggle. No production activation or actual encrypted file operation.

## Recorded scope and admission

CandidateInspectionPermit records a request UUID, authenticated owner, workspace,
connector UUID, candidate attempt, generation/revision, immutable receipt digest,
NEW session HMAC and exact five-minute lifetime. Digest preserves the original
session hash, client hash, timestamps and scope; the original attempt is untouched.
No raw session, OAuth code/state/verifier, token, client secret or file path is
stored or returned. Public snapshots are metadata, not proof of inspection.

Admission locks workspace -> connector -> attempt -> permit and checks live
active workspace ownership, consistent generation history and current quarantined
CANDIDATE only. RESERVED/EXCHANGING/UNCERTAIN/rejected, rotated/blocked scope or
other unresolved candidate history denies. User confirmation must be exactly True,
with the expected generation/revision/receipt digest. New-session HMAC binds the
permission without replacing or interpreting the old session HMAC.

One permit per candidate is deliberate in this slice. Exact request replay returns
that permit's CURRENT state and ORIGINAL deadline, only within its unchanged scope
and new-session binding. Another request, another session, expired/consumed permit
or mismatched request reuse cannot renew, replace or reset it. Renewal/abandonment
and reconciliation remain separate design work; no automatic recovery by new IDs.

## Irreversible claim, not an inspection result

Both operations reject caller transactions. Consume revalidates ownership, scope,
receipt, session and time, then atomically changes ISSUED to CONSUMED exactly once.
It commits before returning its metadata snapshot, so caller rollback cannot reopen
the claim. Duplicate/expired consumption denies. CONSUMED means only the metadata
claim was consumed; it does NOT mean any file was read, matched, activated or used.
Failure/crash after claim cannot justify another permit or automatic I/O retry.

Model constraints require positive lifetime, valid issue/consume timestamp state
including explicit non-null consumed time, and a unique candidate relationship.
Application checks also require exact duration, bounded typed UUID/revision and
digest/session binding. PostgreSQL concurrency evidence comes from CI; local
SQLite cannot prove row-lock behavior.

## Unfinished integration gates

No current configured client or legacy path is read. Receipt client-hash consistency
is NOT proof of current client configuration. No actual envelope readback, target
proof, provider permission, refresh, adoption, activation, revoke or publishing.

A future separately reviewed executor must consume directly, never trust a caller-
fabricated snapshot, and only derive the exact candidate path from the bound owned
receipt. It must release DB locks for bounded I/O, check current client and legacy
presence, and recheck time/owner/generation/revision/immutable receipt and current
quarantine after I/O before returning any advisory result. Legacy contents must
remain unread. Post-read scope validation and uncertainty/reconciliation are NOT
implemented by this metadata slice.

Future HTTP wiring also needs authenticated server-derived session identity,
CSRF and explicit signed scope/action confirmation; a supplied session string is
not authentication. New permits still depend on the current Django SECRET_KEY;
restart/rotation or session loss fails closed and does not solve production vault
or recovery guarantees. Never migrate the preserved candidate DB for this slice.

## Validation

Focused synthetic service/constraint/race checks and independent source review
cover admission, scope drift, no-I/O, replay, expiry, caller rollback and single
consumption. Exact executed counts and required/post-merge CI are recorded in the
PR and continuity snapshot. Migration0007 is additive and applied only in ephemeral
test databases; no actual provider, credential or preserved database operation.
