# GrowthTwin architecture

Status: the product objective is a user-authorized advertising autopilot. The accepted modular-monolith and Django/PostgreSQL decisions remain in [ADR-0001](docs/adr/0001-modular-monolith.md) and [ADR-0002](docs/adr/0002-application-stack-and-local-environment.md). No production AI provider or publishing platform is selected.

## Product boundary

GrowthTwin receives a plain-language campaign request from an individual, creator, or business, produces and validates campaign assets, publishes and measures them through an authorized destination, and reports results. The ordinary journey should not need a GrowthTwin staff operator. The advertiser initiates the work, connects the destination, and configures the permitted channels, schedule, content boundaries, and spend caps. Application rules enforce those limits; incomplete or unsafe cases pause and explain what is needed.

The website should reduce user effort by asking only for missing essential facts, showing progress in plain language, and keeping preview, limits, and stop controls visible. Dental-clinic examples are a potential pilot dataset, not a domain boundary.

Local UX and campaign prototypes may proceed with synthetic data before Phase 0 staging/recovery checks are complete. Staging E2E, backup/restore, rollback, and production readiness remain gates before real account connections, an external beta, or production activity.

## Proposed shape

Start with one modular Django application and PostgreSQL. Add a separate worker or service only when the local product slice demonstrates a need and the cost and operations are reviewed.

```mermaid
flowchart LR
  Advertiser[Advertiser] --> Web[GrowthTwin web experience]
  Web --> App[Campaign application boundary]
  App --> Identity[Advertiser and workspace]
  App --> Brand[Brand facts, documents, and asset versions]
  App --> Brief[Campaign brief and media plan]
  App --> Creative[Creative generation and versions]
  App --> Pricing[Credits and service-fee ledger]
  App --> Policy[Consent, budget, and safety policy]
  App --> AI[AI gateway]
  App --> Publish[Publishing adapters]
  App --> Report[Performance reporting]
  App --> Leads[Lead delivery]
  App --> Experiments[Creative experiments]
  App --> Jobs[Background work boundary]
  Identity --> Store[(PostgreSQL)]
  Brand --> Store
  Brief --> Store
  Creative --> Store
  Pricing --> Store
  Policy --> Store
  Publish --> Store
  Report --> Store
  Leads --> Store
  Experiments --> Store
  AI --> Providers[Local or replaceable model providers]
  Jobs --> Publish
  Jobs --> Report
```

The diagram is a logical view, not a deployment topology. It does not require a separate worker, new database, or third-party AI provider.

## Module responsibilities

- **Web experience:** low-friction, responsive campaign intake, previews, progress, reports, and pause/stop controls.
- **Advertiser and workspace:** accounts, memberships, tenant context, and connected destinations. Enforce authorization on the server for every read and write.
- **Brand facts, documents, and assets:** advertiser-supplied facts, references, source documents, permitted claims, and reusable creative inputs. Preserve original uploads and record rights/source/version metadata. Isolate parsing and text extraction.
- **Campaign brief and media plan:** validated objective, audience/geography, budget ceiling and currency, schedule, channel/placement, status, and required facts. Forecasts carry source, timestamp, assumptions and confidence; missing forecast data must not be filled with invented values.
- **Creative generation and versions:** customer-owned material and GrowthTwin-created copy/image/video are distinct paths; record immutable source versions, derivatives, destination formatting, rights and traceability to briefs. Regeneration creates a new version instead of overwriting edits.
- **Pricing and credit ledger:** keep purchased/granted/bonus credits, holds, consumption, releases/refunds and adjustments auditable and idempotent. Separate creative credits, GrowthTwin service fees, platform media spend, tax and currency. Prices remain a product decision.
- **Consent, budget, and safety policy:** accepted account scopes, per-campaign and aggregate spend ceilings, allowed schedules and content, stop conditions, and auditable decisions. Fail closed when state is missing or stale.
- **AI gateway:** server-side contract and replaceable providers for generation and checking. Outputs are untrusted suggestions and must pass deterministic schema and policy validation.
- **Publishing adapters:** provider-neutral external-action contract. Adapters own OAuth/token details, platform payloads, idempotency keys, failure mapping, and reconciliation. Only the application policy layer may authorize dispatch.
- **Performance reporting:** imports and normalizes platform results, marks missing or delayed data clearly, and presents understandable summaries.
- **Lead delivery:** distinguish advertiser requests from campaign-generated leads; route only to an authorized destination with purpose/consent, access, retries, audit and deletion behavior.
- **Experimentation:** store hypothesis, tested variable, success/guard metrics, budget and duration bounds, result sufficiency, and the user's authorization for any follow-up budget increase.
- **Background work:** asynchronous generation, scheduling, publishing, and reporting with bounded retries and visible state. Select a queue or workflow product only after need and cost are established.
- **Persistence and operations:** transaction ownership, tenant-scoped records, health/readiness, revision visibility, audit metadata, backups, and recovery controls.

## Campaign lifecycle

`brief -> planned -> generated -> validated -> scheduled/paused -> published -> measured -> optimized/paused`

The advertiser first authorizes the connected destination and chooses hard limits. The normal path can proceed without a per-campaign staff approval when the request, content, account, schedule, and spend all fit that authorization. Missing facts, invalid output, unsafe or restricted content, provider uncertainty, and limit violations pause the campaign. A revised creative is always revalidated before dispatch. A prominent advertiser stop action disables future dispatch immediately.

An AI model must never set or raise a spend cap, invent advertiser facts, decide that policy checks passed, access platform credentials, or call a publishing API. Application code validates permissions and current limits at dispatch time, records the exact version and idempotency key, and reconciles uncertain provider responses before retrying.

## Current implementation coverage

The implementation is intentionally earlier than the logical target above. The baseline audit at `60f3971` described a public session-owned synthetic `CampaignDraft`; subsequent PRs add a separate workspace-owned `WorkspaceCampaignDraft`, owner-scoped services, tenant tests, a provider-free Google Search text plan, an authenticated fixed-sample preview, bounded synthetic edits, and browser E2E. PR #120 defines pure asset workflow contracts and PR #121 tests their transitions; neither performs file operations. Free-text advertiser inputs remain withheld pending the real-data readiness gate. These flows do not change the public session-draft path or call Google Ads API. The current feature branch adds a pure synthetic action-policy evaluator in `approvals`; it has no view, persistence, provider, token, or publishing integration and cannot authorize live dispatch. `ai_gateway`, `publishing`, `analytics`, and `persistence` remain placeholders; there is no live spend/consent enforcement, asset ingestion, credit ledger, real campaign forecast, lead route, or experiment implementation. The sample report and pause control remain simulations.

Do not turn every box in the diagram into a database model before the first MVP workflow and data/tenant boundaries are selected. The field-by-field gap assessment and implementation dependencies are in [the current system gap analysis](docs/product/current-system-gap-analysis.md). No architectural cloud service is selected or required by that plan.

## Architecture rules

1. Domain modules own their rules and expose application contracts; avoid cross-module database access and import cycles.
2. Enforce workspace/advertiser scoping at application and persistence boundaries.
3. External AI and publishing providers are server-side adapters. Never expose provider credentials to the browser or model.
4. Hosted trial models receive synthetic evaluation examples only and never serve GrowthTwin end users.
5. Verify platform permissions, terms, and reporting coverage before selecting an adapter for real use.
6. Keep budget, consent, validation, pause, and idempotency rules deterministic and testable.
7. Keep early product work in the existing application. Add infrastructure only when measured workflow needs justify it.

## Open architecture decisions

The first stack remains Django 5.2 LTS + PostgreSQL. The first advertising destination, authentication extensions, async job system, object/media storage, production host, and production AI provider remain open. Local product UX does not depend on resolving these choices; resolve each before the feature requires it and record it in an ADR.
