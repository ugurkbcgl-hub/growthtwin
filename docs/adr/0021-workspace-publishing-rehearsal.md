# ADR-0021: Owner-scoped synthetic publishing rehearsal

- Status: Accepted for local synthetic development only
- Date: 2026-10-15
- Decision owner: Project owner (delegated implementation decisions)

## Context

The workspace can prepare, edit, select and download a synthetic campaign
draft. It needs an observable start, failure, retry and stop journey before a
channel integration can be developed. No live account or provider is connected.

## Decision

1. Store a rehearsal separately from the draft, with a current state and
   revision, operation identifier, input fingerprint and synthetic receipt.
   Record accepted transitions as related events; show the latest 20 in the UI.
   Campaign deletion cascades to the rehearsal and events. These are prototype
   records, not a production audit trail or new real-data retention policy.
2. Use only the hard-coded fake adapter. It performs no network, credential,
   publishing, billing or reporting operation. A running state means that the
   fake start step succeeded, not that a worker or ad is running.
3. Require a current preferred creative and complete local plan before start.
   Bind the submitted form to the campaign's input fingerprint and rehearsal
   revision. Serialize actions under the owning draft's database lock. Reject
   stale/duplicate revisions without another action or event.
4. A deliberately failed start can retry the same operation identifier. A
   changed creative, selection, destination, budget or schedule prevents retry
   of that old snapshot. The owner can always stop a running/failed rehearsal
   from its current revision, even when campaign inputs changed. A stopped
   operation is terminal; a later explicit start creates a new operation.
5. Require authentication, owner-scoped lookup, POST and CSRF for every action.
   Do not accept provider choices, live flags, receipts or states from forms.
6. Keep the synthetic/no-publication/no-spend boundary visible in every state.
   Do not invent performance metrics or treat the review preference as consent.
7. The action-policy evaluator in ADR-0010 stays disconnected. Do not fabricate
   account authorization, legal eligibility or spend evidence to make it pass.
   The rehearsal verifies local workflow transitions only. A future live
   adapter needs an independently designed authorization, budget reservation,
   reconciliation, revocation and stop propagation boundary.

## Consequences

The local journey can demonstrate recovery and duplicate-submit protection
without an external account. PostgreSQL locking protects the application action
boundary; SQLite tests cannot establish production concurrency behavior.
There is no asynchronous job or distributed retry mechanism in this slice.
It does not establish Google Ads API eligibility, safe live publishing,
provider availability, real-data readiness or customer beta acceptance.
