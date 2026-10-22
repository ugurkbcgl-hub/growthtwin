# ADR-0033: Synthetic owner/session/CSRF authorization journey

Status: Accepted for isolated fixed-example rehearsal only
Date: 2026-10-22

## Decision

Rehearse endpoint security before connecting the ADR0031/0032 candidate adapter.
New `/workspace/connection-rehearsal/<workspace>/` routes call ONLY ADR0030's
fixed synthetic coordinator. They never call Google, candidate exchange/readback,
credential storage, refresh or account verification. Both synthetic service/UI
flags default False, with no new environment toggle. Existing Google endpoints,
legacy grant, candidate adapter flag and quarantined connector remain unchanged.
An already registered owned metadata identity is required; GET never registers,
rotates or creates anything. No production/customer navigation link is added.

The authenticated active owner opens a GET with two explicit fixed examples.
Server-issued ten-minute signed POST tickets bind owner/workspace, session HMAC,
connection/generation/revision, server-generated attempt UUID, scenario and action.
Only exact scalar fields and a checked synthetic confirmation are accepted; reject
extra/duplicate fields, files, wrong action/session, tampering and expired forms.
Django CSRF applies to BOTH POST steps. Start reserves metadata and redirects;
only a separate confirmed perform POST can run the deterministic local fake.
UUID/generation/scope and outcome are never accepted as unsigned form evidence.

Only metadata is saved in the initiating Django session. Status/result access
must match that session's marker and the durable receipt; another login/session
cannot use the form or status URL. GET/HEAD show stored results without running
work. Current scope is inspected for controls; stale/blocked/expired examples
have no run button. The service rechecks current scope before/after fake work,
and in-flight/terminal replay never reruns it. A stored accepted example is not
current permission; neither accepted nor rejected activates a connector/grant.
UI labels explicitly disclose the synthetic boundary and historical result.

All responses on the new prefix, including framework/CSRF errors and default-off
404s, receive no-store/private, same-origin referrer and noindex headers through
the common middleware. No raw exception/payload is reflected in error content.

## Limits and recovery

The session keeps only the LAST successfully started example across these pages.
Starting another example replaces that marker, without deleting history. Logout,
session loss/rotation, or session-store failure after metadata reservation can
leave a pending receipt that this UI cannot recover. This is an explicit fixture
rehearsal limitation, not a production recovery mechanism. Exact still-valid start
replay may restore the same marker; it cannot create another receipt or extend
the original attempt deadline. Do not automatically run/retry an orphan, reset
the DB, infer success, or use synthetic acceptance as candidate/grant evidence.
No OAuth callback, code/PKCE, candidate-file inspection or adoption is wired here.

## Evidence and next action

Seventeen new endpoint tests plus the coordinator tests:40 local passes and2
PostgreSQL race skips. New isolated browser test covers desktop/mobile, keyboard,
two fixed outcomes, refresh/no duplicate and unchanged quarantine. All real
backend/candidate/readback boundaries are forbidden in endpoint tests; browser
backend calls are also forbidden. No new migration or actual provider/credential/
preserved database/Heroku operation. Screenshots are outside Git in the temporary
authorization rehearsal artifacts folder. Local browser test uses static finders
to load source CSS, rather than a previously collected manifest.

Independent review identified missing framework-error header coverage; prefix
and three header regressions were added. Required CI/final review live in the PR.

Next: design and test recovery dispositions for lost sessions and pending/uncertain
candidate receipts, including explicit preservation of legacy grants and separate
stop/reconcile access. Keep actual adapter off until endpoint/callback recovery,
configured TEST target proof and reviewed adoption/rollback gates are met.
