# ADR-0039: Closed recovered candidate readback adapter

Status: Accepted for mocked storage validation only; actual access not exercised
Date: 2026-10-22

## Decision

Implement a separate recovered candidate reader, retaining the original
origin-session reader and fixture rehearsal unchanged. The new service has no
HTTP route, environment switch or caller-supplied reader/path/snapshot. Recovery,
recovered-inspection, scoped-candidate and local-OAuth switches must each be
exactly True; the new switch is False by default. Existing local Windows/no-DEBUG
backend admission still applies. All validation in this slice mocks storage;
no actual client/candidate/legacy credential or preserved database is accessed.

## Claim and scope

The reader acquires the existing process storage lock with a five-second wait
before claiming; no database locks are held while waiting. It reloads the owned
current quarantined CANDIDATE, exact new-session permit and immutable receipt.
Pure location derivation requires the configured owner/workspace pair and absolute
local LOCALAPPDATA root. It derives the same durable legacy location as the
existing backend (owner/workspace, not session), the fixed client basename and
the exact receipt-derived candidate basename. All three paths must be distinct
direct children of the captured root. No path comes from a caller or envelope.

The service calls consume_inspection_permit directly and commits consumption
before any client/file observation. It never accepts an issued/consumed snapshot
as a capability. Post-claim, pre-read and final checks reload live ownership,
current generation/revision/quarantine, immutable digest, current-session HMAC,
exact consumed snapshot, original issue/deadline and consumption time. Expiry,
clock movement before consumption, switch or SECRET_KEY change, scope/history
drift and late observations fail closed. A sixty-second monotonic acceptance
budget additionally rejects results completed too late; it does not interrupt
arbitrary blocked filesystem metadata calls or replace the permit deadline.

## Storage observations

Outside database transactions, the adapter observes legacy presence without
reading its contents and checks the bounded fixed client against the receipt
hash. An existing/inaccessible/irregular legacy path or changed client cannot
yield a match. Only the exact captured candidate file is then decoded and checked
using the existing strict envelope codec. Root/settings/locations are rederived
before reads and before final observations; drift never redirects the operation
to a different root. Legacy/client observations are repeated, followed by the
final owned metadata checks. The process lock serializes cooperating local
writers only, not other processes.

The new private decoder is used for BOTH client and candidate files. The old
backend._read is unchanged and is not used here. A fixed PowerShell script reads
from a held read-only FileStream with FileShare.Read, checks its positive length,
reads at most 131073 bytes and rejects more than 131072. Strict UTF-8 decoding and
SecureString length <=32768 precede plaintext output; BSTR is zero-freed and
stream/SecureString disposed. The existing subprocess has a fifteen-second
timeout; errors and stderr stay suppressed. Python also caps decoded text, rejects
duplicate JSON keys/non-JSON constants/non-object values and sanitizes exceptions.
Client schema/project/ID/secret bounds are checked but secret material is not
returned. Reparse/ancestor checks in the script are best effort, not an atomic
no-follow guarantee. No writes, refresh, revoke or network request are performed.

## Result and failure

Only frozen request/attempt IDs and an advisory disposition are returned:
matches_candidate, invalid_envelope, legacy_exists, client_changed or unreadable.
A match is local envelope/binding evidence only; it proves neither token validity
nor account access, remote grant preservation, adoption or activation. No result
is stored. After a claim, any failure/crash leaves CONSUMED; no automatic retry,
renewal, replacement or reconciliation is implemented. Before-claim lock/config
failure leaves the original ISSUED permit unchanged.

## Actual exercise gates

Mocked Windows-script checks are not evidence of a successful real DPAPI decode,
ACL safety, reparse/race resistance, configured-target permission or recovery.
Before an actual isolated exercise, separately review the launcher, protected root
and ACL/location/regular-file metadata, unchanged receipt/history, current client
binding, precise one-shot permit/session lifetime, bounded logging and cleanup.
Preserve the same candidate database and history; do not create a new identity or
reset consumed metadata to bypass a refusal. Actual preserved-DB migration/access
is a separate reviewed step. A failed consumed claim needs an explicit disposition
and cannot be worked around by new IDs. No browser wiring, production rollout,
provider account proof, activation, grant adoption or advertising is enabled.

## Validation

Targeted tests replace every filesystem/PowerShell/client/provider boundary and
fabricate receipts in ephemeral databases. Source review and required PostgreSQL
CI cover claim/reader races and post-read drift; exact executed counts and final
PR/CI outcomes are in TESTING.md, STATE.md and the PR closure comment.
