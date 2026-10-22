# ADR-0028: Read-only owner campaign stage overview

Status: Accepted for local synthetic development only
Date: 2026-10-21

## Decision

Provide one owner-scoped six-stage overview linking existing campaign creation/
editing, current creative preference, plan/budget review, explicit TEST consent,
stored TEST dispatch and report screens. The next step is advisory navigation;
no completion percentage or authorization is inferred from visiting a page.

The projection reads local owned draft metadata, approval existence and only
allowlisted dispatch state/observed_status/updated_at. It never reads immutable
payloads, grants, credentials or verification configuration, contacts a provider,
or writes. GET/HEAD are safe, mutation methods rejected; private/no-store,
noindex and referrer boundaries apply to errors too.

Creative preference must match current source and version and never implies
consent. Approval existence alone cannot establish current source/target consent.
Stored TEST state is explicitly unrefreshed and may refer to an older source;
unknown/inconsistent states require verification. Existing dispatch takes next-
action priority even after source changes, preserving no-resend expectations.
Only exact existing local owner/workspace/host/remote/no-forwarded/DEBUG-off
settings expose TEST links; review also requires current creative and a complete
local plan, status requires a dispatch record. These are link visibility rules,
not replacements for endpoint authorization, CSRF or immutable ledger checks.
Reports remain truthfully unavailable without verified platform observations.

## Consequences and evidence

No new schema, provider integration, scope, real data, live publishing or spend.
Existing creation redirects, creative actions and TEST endpoint behavior remain.
Sixteen new tests plus 47 existing focused tests passed. Independent review,
ruff/migration drift and desktop/mobile/Enter-navigation checks passed in the
isolated credential-free fixture. Required CI is tracked in PR/continuity state.
Actual Google guard mapping and production readiness gates stay open.

Next narrow slice: add consistent campaign overview navigation to protected
TEST review/status pages while retaining existing fixed TEST consent and action
boundaries. Do not infer real publishing permission from this UX.


## Protected TEST presentation follow-up — 2026-10-22

The existing guarded review/status, operation result and validateOnly result
share the campaign shell, noindex metadata and no scripts. Owned409 recoverable
errors return to stages; unresolved/foreign drafts must not gain navigation.
Shared status labels allowlist only known stored metadata; status GET reads no
payload/grant/configuration and performs no remote request or write. Explicit
POST operation results limit fresh observation claims to that operation, while
uncertain or unrecognized states never imply verified publication. A local
record timestamp includes timezone offset, not provider freshness.
No intent means no status read/stop form. Existing guarded POST actions, fixed
consent, CSRF/signatures, immutable snapshots, no-resend and stop behavior remain.
Fourteen new tests plus existing focused coverage (55 tests) passed, as did
independent source review, ruff/migration drift and isolated browser layout/
keyboard checks. The stubbed browser fixture is not actual Google evidence.
