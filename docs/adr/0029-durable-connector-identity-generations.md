# ADR-0029: Durable connector identity and generation foundation

Status: Accepted for isolated local synthetic validation only
Date: 2026-10-22

## Context

Existing Google TEST credentials use owner/workspace storage without durable
connection identity/generation. SyntheticConnectionScope identifies fixed
examples only and cannot represent those grants. We need a separate durable
metadata identity before binding real OAuth starts/callbacks/refreshes/results.
No existing grant can be assigned a fixture identity or migrated implicitly.

## Decision

Introduce ConnectorIdentity and ConnectorGeneration with no tokens, account IDs,
paths, content or provider payloads. There is one google_ads_test slot per owned
workspace in this narrow foundation. UUIDs for connection/generation are generated
server-side; internal operation request UUIDs are typed, nonzero and globally
unique receipts. Each generation preserves its ordinal and prior generation/
revision. Register replay returns CURRENT metadata, never resets a connection.
A different registration for an existing slot conflicts. A replayed rotation
returns current metadata even after later rotation/block, and never reactivates
its historical generation; mismatched request arguments conflict.

Only quarantined and blocked states are supported and enforced by DB constraints.
Neither grants provider work. Block is permanent through this service; current
revision replay is a no-op and stale block conflicts. Rotation is permitted only
within quarantined metadata, preserves connection identity and retires the prior
generation. This is metadata rotation, not credential refresh or reauthorization.
No activation/reopen/deletion API, URL, admin action or real account mapping.

Every service path verifies current active workspace ownership, locks workspace
then connection in a transaction, and verifies the full metadata receipt chain.
Generation/revision conditional updates and atomic receipts prevent partial
writes; uniqueness resolves cross-workspace request races with generic conflict.
Corrupt or missing history denies reads and transitions. ORM/database access can
still bypass service semantics; these are not tamper-proof receipts or independent
restore/recovery evidence. Preserve history; no cleanup/drop policy is authorized.

## Scope and evidence

Migration0003 creates only new metadata tables/constraints, no data migration.
It ran only in ephemeral test DBs. Existing Google routes, DPAPI files, grants,
immutable campaign ledgers, fixed fixture guard and closure store are untouched.
There is no runtime protection for their requests from this metadata alone.
Stop/reconcile must remain separately authorized in future real integration.

15 new local tests and14 existing work-guard tests passed;4 PostgreSQL races
(two new) require CI. Ruff/format/migration drift and independent source review
passed. No UI/browser test was needed for this service-only slice.

Next: a generation-bound authorization-attempt receipt and result acceptance
coordinator with a closed default and deterministic local fake outcomes. Later
actual OAuth integration needs separately reviewed pre/post exchange/refresh/
result gates, explicit grant mapping and recovery/secret-vault readiness. Do not
read, migrate, reactivate or reset the preserved grant in the next fake slice.
