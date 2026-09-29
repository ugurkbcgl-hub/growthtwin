# Domain module boundaries

Keep the first application as one Django deployment while keeping domain
responsibilities separate. Local product implementation is authorized. The
`content` contains provider-neutral, persistence-free `CampaignBrief` and
`CampaignPlan` values. Session-scoped synthetic prototype persistence remains
in `site`; see [ADR-0006](../../../../docs/adr/0006-campaign-brief-boundary.md)
for the ownership boundary and conditions required before adding a content ORM
entity. Provider clients and cross-module persistence contracts are not defined
yet.

- `workspaces`: advertiser identity, membership, roles, and tenant context.
- `campaigns`: workspace-owned campaign plans, user-selected spend limits, state history, and channel-neutral application rules. Initial synthetic persistence uses a narrow Google Search lead-generation draft; platform writes remain outside this module.
- `content`: brand facts, campaign briefs, creative drafts, versions, and asset metadata.
- `approvals`: optional records for exact-version or exceptional review requirements; not a required staff gate for routine campaigns.
- `publishing`: advertiser-authorized dispatch contracts and platform adapters.
- `analytics`: normalized campaign performance from selected ad platforms.
- `ai_gateway`: provider-neutral AI contracts and replaceable adapters.
- `persistence`: shared persistence contracts and transaction ownership.

Modules should depend on explicit contracts rather than another module's
internal models. The initial `campaigns` record has a direct foreign key to the
workspace tenant boundary; all application-level workspace lookup must pass
through the owner-scoped service. Add an explicit campaign policy/budget
boundary as product rules emerge, and keep channel credentials outside model
and browser access.
