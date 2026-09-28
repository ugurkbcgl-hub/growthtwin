# Domain module boundaries

Keep the first application as one Django deployment while keeping domain
responsibilities separate. Local product implementation is authorized. The
`content` module currently contains a provider-neutral, non-persistent campaign
plan value object; session-scoped prototype persistence remains in `site`.
Provider clients and cross-module persistence contracts are not defined yet.

- `workspaces`: advertiser identity, membership, roles, and tenant context.
- `content`: brand facts, campaign briefs, creative drafts, versions, and asset metadata.
- `approvals`: optional records for exact-version or exceptional review requirements; not a required staff gate for routine campaigns.
- `publishing`: advertiser-authorized dispatch contracts and platform adapters.
- `analytics`: normalized campaign performance from selected ad platforms.
- `ai_gateway`: provider-neutral AI contracts and replaceable adapters.
- `persistence`: shared persistence contracts and transaction ownership.

Modules should depend on explicit contracts rather than another module's
internal models. Add an explicit campaign policy/budget boundary as product
rules emerge, and keep channel credentials outside model and browser access.
