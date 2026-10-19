# ADR-0023: Version-bound workspace Google test review

- Status: Accepted for local synthetic review only
- Date: 2026-10-19
- Decision owner: Project owner (delegated implementation decisions)

## Decision

Map the current owner-selected creative and campaign plan into a canonical,
immutable JSON review package. Include all selected source text, preferred
version/key, mapper version, source fingerprint, plan budget/currency/dates/city
and exact original destination. Derive distinct Google text assets within local
30/90 character limits; show original/mapped values and shortening metadata.
Do not silently replace destination or treat local length checks as Google policy
approval. The current example.invalid destination remains unverified/unreachable.

The local review page does not contact Google. A CSRF-protected explicit test
approval uses a ten-minute signed review token bound to owner, workspace, draft,
package fingerprint and local target/credential configuration fingerprint. On
submission lock the owned draft, rebuild and compare; stale input/target is rejected.
Store an append-only approval snapshot with a unique draft/package/target key.
Repeating the same approval reuses it. Protected draft deletion preserves history.

This is preparation for later PAUSED TEST dispatch, not production consent,
policy clearance, financial authority, or an external campaign action. The live
fixed test from ADR-0022 stays separate. Later dispatch must recheck current
source/approval and verified target, explicitly handle destination readiness,
translate budget/date/targeting semantics, and reserve a durable operation before
network writes. Never dispatch the review JSON directly as an API operation.

## Verification

Six mapper checks and four DB/HTTP approval checks cover immutable source,
shortening, target/source change, owner isolation, CSRF and repeat approval.
Browser reviewed and approved a synthetic package without a Google request.
Migration 0007 applied only to the preserved isolated synthetic review database.
