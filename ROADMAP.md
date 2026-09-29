# GrowthTwin roadmap

## Direction reset — 2026-09-27

The owner clarified that Türkiye is the target market and GrowthTwin should serve anyone who wants to advertise. Dental clinics, creators, and small businesses are examples, not product boundaries. Omneky is a long-term capability benchmark for ad creation, campaign launch, unified reporting, and bounded optimization. See [PROJECT.md](PROJECT.md), [ARCHITECTURE.md](ARCHITECTURE.md), accepted [ADR-0004](docs/adr/0004-self-service-advertising-autopilot.md), and [ADR-0005](docs/adr/0005-turkey-first-advertising-platform.md).

The product should remove routine GrowthTwin-operator work after an advertiser explains a goal, authorizes an account, and sets explicit limits. Routine work may run within those boundaries; the system must pause and notify the advertiser when it cannot safely proceed. Omneky-style multi-channel breadth is a long-term target, not the first-release scope. Current work prioritizes the local website and synthetic-data development; it does not authorize production publishing, real ad spend, or additional paid infrastructure.

## Existing foundation — in place for local product work

- Public GitHub repository, protected `main`, pull-request workflow, and CI are active. Use pull requests for repository changes and verify live branch/PR status before acting.
- Django 5.2 LTS + PostgreSQL 18 is the accepted local stack and is already scaffolded under `apps/web`.
- CI checks Django configuration, formatting, linting, dependency vulnerabilities, package builds, migrations, and focused tests. A synthetic profile edit E2E exists locally and in CI.
- Local browser E2E and GitHub-hosted CI provide the initial feedback loop. Keep local UI work on synthetic data.
- Heroku staging has an approved Basic web dyno, Essential-0 PostgreSQL, and Standard Free Scheduler. On 2026-09-29, the Scheduler page recorded the daily synthetic session-cleanup job at 00:00 UTC as last run, and Heroku logs showed its one-off process exited with status 0. Actual one-off dyno cost remains unverified. The deployed app is for synthetic staging only.

## Phase 1 — Product experience prototype

**Goal:** demonstrate a clear, low-effort paid-advertising journey for a user in Türkiye without waiting for external APIs, paid infrastructure, or a production model.

Status: **Phase 1 acceptance verified on 2026-09-29.** The local product slice saves synthetic briefs as session-scoped drafts, derives a plan summary, and demonstrates preview, simulated pause, editable deterministic copy, and sample report. Visual review at a 1252 px desktop viewport found and fixed horizontal overflow, a hard-to-read data notice, and a report transition that could leave the report off-screen (PR #100). Mobile E2E and all PR/post-merge CI checks pass. There is no connected account, AI provider, publishing, or real metrics. Durable advertiser/workspace persistence remains deferred until ownership and lifecycle boundaries are specified; see ADR-0006 and ADR-0007.

- Build the public product entry and a mobile-friendly campaign workspace in the existing Django application.
- Let any advertiser in the Türkiye target market describe a goal with a short plain-language brief, then ask only for essential missing details such as audience, destination, timing, and maximum spend.
- Demonstrate brand/offer intake, a campaign plan, and on-brand ad concepts in a simple experience.
- Show a believable lifecycle with synthetic output: request received, plan prepared, creative preview, destination/schedule, simulated publication, and performance summary. Label mock publishing and metrics clearly.
- Keep editing, current status, spend boundary, and pause/stop visible. Do not hard-code clinic fields.
- **Acceptance:** a new visitor can understand the offer; a synthetic advertiser can move through brief → campaign preview → mock result without staff help; the layout works on mobile and desktop; no external account, AI provider, or publishing API is called.

## Phase 1.5 — Product and service blueprint

**Goal:** define what the first usable service does from advertiser request through campaign results, before building account/workspace flows that could invite real data.

This work is required before continuing the authenticated workspace UI or accepting real advertiser, customer, or lead data. The long-term direction and owner requirements are now expanded in [the product/service blueprint](docs/product/growthtwin-service-blueprint.md). A first research draft exists; Phase 1.5 remains **in progress** until its open decisions and narrow MVP are reviewed and selected. The blueprint records the full desired service while separating customer requirements, recommendations, findings, and undecided implementation/commercial/legal choices.

- Specify the two content paths: GrowthTwin-created content paid from credits, and customer-owned documents/assets that can be analyzed, edited, improved, adapted and versioned without overwriting the original.
- Map beginner and professional experiences across intake, strategy, content, pre-purchase plan/estimates, price breakdown, approval, publication, reporting, experimentation, pause, recovery, export and deletion.
- Treat owner-provided credit anchors (100 credits = USD 10; USD 100 for 1,000 purchased credits plus 20% bonus = 1,200 credits) and free initial credits as pricing requirements to cost and validate; distinguish creation credits, GrowthTwin campaign fees, platform media spend, tax and currency. The precise rate card and outcome/refund guarantee remain unresolved pending economics and legal review.
- Research Türkiye channel availability separately from GrowthTwin's API/SaaS approval. Score objective/format, OAuth and app review, forecast/report coverage, account/currency, lead sync, policies, maintenance and cost. Initial official-source findings and unknown channels are recorded in the blueprint; do not describe a candidate as integrated until access is verified.
- Define the pre-purchase calculator's channel-level budget, estimated reach/impressions/engagement ranges, assumptions, source and freshness, confidence, fees and platform spend. Never invent or present uncertain results as guarantees.
- Define AI evaluation by text, image, video and customer-document tasks, including copyright/likeness, data classes, provider terms, source traceability, claims and evaluation on synthetic data. No production provider is selected.
- Separate advertiser service requests from generated campaign leads; decide collection, purpose, destination, consent, account/role access, delivery/retry/audit, retention and deletion.
- Record Turkish advertising, KVKK/cross-border transfer, commercial electronic message, IP and sector-policy review as launch gates. Product policy checks are versioned and explainable; they do not replace counsel.
- Define spend/schedule/content boundaries, user authorization, tenant ownership, data recipients, category-specific retention/deletion/export, backup and restore. Keep all development and staging data synthetic.

**Current artifact:** `docs/product/growthtwin-service-blueprint.md` (draft, research timestamp 2026-09-29). It captures the service model, pricing arithmetic, channel evidence, calculator, strategy/testing, Türkiye legal review areas, launch readiness gate, phased delivery, source list and decision register.

The code-to-plan inventory is [the current system gap analysis](docs/product/current-system-gap-analysis.md). It confirms that the local synthetic prototype and CI are ready for local work, while authenticated ownership, customer assets, campaign/pricing/policy domain, provider ports, and live integrations are not. The analysis is an implementation dependency map, not approval to collect real data or to settle open product decisions.

**Acceptance:** owner-facing review selects one initial advertiser workflow/objective and cohort hypothesis, first platform candidate (or records an explicit API/access blocker), first service boundary, lead destination/consent approach, supported first creative tasks, credit/fee hypothesis, beginner/pro defaults and bounded autonomy. Open legal, partner, privacy and pricing items have named evidence and next steps. The blueprint does not itself authorize real accounts, data, payment, publishing, ad spend or paid infrastructure. Those remain blocked until the separate readiness gate and owner decision.

**Decision:** the project owner delegated product and sequencing decisions. ADR-0008 selects a synthetic Ankara city-service quote/contact workflow, Google Search as the first technical channel candidate, the advertiser's own site as destination, no raw lead custody in GrowthTwin, and a fake-only adapter boundary. This is a prototype scope decision; user-demand validation, API access approval, forecasts, real-data/legal review, fees and live spend remain open gates.

**Completed:** PR #110 adds the workspace-owned synthetic campaign draft and owner-scoped services; PR #111 adds focused tenant-isolation/input validation tests. The anonymous `site.CampaignDraft` path remains separate.

**Completed:** PR #112 adds provider-free, source-traceable Google Search text assets with current RSA character limits and explicit unavailable forecast/keyword states. Local planning tests pass; the plan cannot publish or spend.

**Completed:** PR #113 adds a login-protected workspace list and preview launched from a fixed synthetic example. It uses owner-scoped create/read, shows source fields and unavailable forecasts, and keeps session drafts/public prototype separate. Free-text advertiser inputs are withheld until the real-data readiness gate. PR and post-merge CI passed.

**Completed:** PR #114 lets the owner change only bounded synthetic budget/duration choices or remove their own saved draft. Tenant isolation and choice enforcement are tested. PR and post-merge CI passed.

**Completed:** PR #115 adds browser end-to-end coverage for the authenticated synthetic workspace path, including mobile layout, owner isolation and bounded draft changes. PR and post-merge CI passed.

**Completed:** PR #116 replaces the stale Phase 0 login screen with a Turkish, accessible sign-in page that explains the synthetic-only scope, preserves the requested return path, and keeps public registration closed. PR and post-merge CI passed.

**Completed:** PR #117 shows the campaign's equal-allocation daily planning average, clearly separated from a platform spend limit or performance forecast. PR and post-merge CI passed.

## Phase 2 — Local campaign vertical slice

**Goal:** connect the website to deterministic campaign records and evaluate draft generation without creating external side effects.

**First gate:** establish the workspace owner and campaign/brand data lifecycle before adding durable content records. See the [current system gap analysis](docs/product/current-system-gap-analysis.md) for the implementation inventory and dependencies. For this synthetic-only prototype, workspace ownership is tied to an authenticated user, anonymous session drafts are never backfilled automatically, and no real advertiser data is accepted. Do not invent a universal retention period; set purpose- and data-category-specific limits before real data. See [ADR-0007](docs/adr/0007-workspace-ownership-and-retention.md).

Status: the minimal user-owned `Workspace` model and owner-deletion/owner-scoping tests are merged in PR #102. ADR-0008 defines the first synthetic flow. PR #110 connects a new campaign draft model to Workspace, PR #111 verifies isolation, PR #112 adds the provider-free Search draft plan, PR #113 adds the authenticated fixed-sample list/preview, PR #114 adds owner-scoped bounded setting changes and removal, PR #115 adds browser E2E coverage, PR #116 improves sign-in, and PR #117 adds transparent arithmetic pacing. PRs #120–#121 define and test pure future-asset workflow states. PR #122 adds fail-closed synthetic action-policy contracts and focused tests. The anonymous public draft path remains separate. All campaign records remain synthetic-only.

- Model advertiser/workspace, brand facts and assets, campaign brief, versioned multi-format ad creatives, destinations, user-defined caps, and status history.
- Add a server-side AI gateway with validated structured output and provider adapters. Begin with local Ollama plus synthetic data; use NIM only for synthetic evaluation.
- Add quality checks for missing/unsupported claims, format constraints, and budget/schedule completeness. A rejected or ambiguous output stays paused.
- Verify tenant isolation, schema validation, retry/idempotency behavior, and the campaign user journey.
- **Acceptance:** the local end-to-end path saves a campaign, produces or safely rejects structured ad drafts, explains its state, and cannot publish or incur ad spend.

**Asset boundary decided:** [ADR-0009](docs/adr/0009-asset-intake-processing-boundary.md) defines contract-first handling of future customer files. It keeps ownership, rights declaration, task permission and AI-provider permission separate; requires quarantine, scanning, provenance, fail-closed states and complete deletion; and explicitly does not authorize upload, persistence, storage, parsing, or AI calls.

**Completed in PR #120:** pure, storage/provider-independent asset workflow types define declaration gates, clean/unsafe/error scan outcomes, extraction, provider permission, and deletion states. The code performs no file operations, persistence, or AI calls.

**Completed in PR #121:** focused synthetic tests cover declaration gates, scan outcomes, extraction, provider permission, invalid construction, and deletion. Local tests, required PR CI, and post-merge CI passed. User upload and real data remain closed.

**Completed in PR #122:** add a pure synthetic policy check for authorization, destination/channel/content state, campaign and aggregate budget caps, schedule, and stop conditions. It reports reasons, fails closed on unknown inputs, and never authorizes live dispatch. Its caller-supplied evidence remains untrusted.

**Completed in PR #126:** add allowlisted synthetic evidence-source labels and a timezone-aware observation time to the policy result. Unknown labels and missing/naive timestamps fail closed. The returned metadata remains caller-supplied and untrusted; it is not authentication, freshness proof, atomic spend reservation, or live authorization.

**Completed in PR #128:** add a stable synthetic policy version and identifiers for the deterministic checks reported with each decision. This metadata is informational and in memory; the version does not authenticate evidence. No persistence, live integration, spend reservation, or dispatch authorization is included.

**Completed in PR #131:** bring the provider-free creative-variant workflow into the authenticated workspace campaign path. Versions are owner-scoped; brief/brand/city changes hide stale copy, while budget/schedule changes leave it current. The anonymous demo remains separate and no external AI/provider call was added.

**Completed in PR #133:** let the campaign owner choose one current copy variant as the preferred draft. Store the selection against the current version, hide it when source inputs change, clear it when a new version is generated, and label it as an informational review preference. No approval or publication action is implied. See [ADR-0014](docs/adr/0014-workspace-creative-preference.md). The workflow remains synthetic and provider-free.

**Completed in PR #135:** give each authenticated workspace campaign a report page with reach, impressions, clicks, other interactions, contact requests, and media spend. Mark values unavailable until a verified channel source exists; show source and update status, with no fabricated metrics. Keep this distinct from the public prototype's simulated sample report. See [ADR-0015](docs/adr/0015-authenticated-campaign-report-empty-state.md).

**Completed in PR #138:** define a provider-neutral report metric contract that distinguishes unavailable data from a real zero and carries reporting window, unit/currency, source, and timezone-aware observation time. Focused tests use synthetic fixtures only. The contract is persistence-free and does not connect platforms or fabricate live results. See [ADR-0016](docs/adr/0016-campaign-report-metric-contract.md).

**Completed in PR #140:** connect typed unavailable metric values to the authenticated report shell. Show the planned campaign period only when its dates are defined; do not imply observed delivery. No source, value, persistence, or provider is added.

**Metric semantics (ADR-0017; documentation update pending PR #141):** define provider-neutral meanings for the six report categories, their attribution boundaries, reporting windows, currency, and unknown/stale-data handling. Do not flatten differing native platform definitions into comparable values. Keep this as a design contract; do not connect a platform or imply live reporting.

**Completed in PR #142 (research only):** map Google Ads API v25 official source fields to ADR-0017's metric definitions without an account or API request. The Search candidate mapping leaves reach unavailable, avoids double-counting interactions as clicks, and does not treat attributed conversions as delivered lead records.

**Completed in PR #143:** extend the provider-neutral report contract with explicit `not_connected`, `unsupported`, `partial`, and `stale` reasons, reason-specific provenance requirements, and metric-level user-facing explanations. A source-confirmed zero remains an available numeric zero. Required PR CI `36602784613` and post-merge CI `36603066285` passed. No provider, account, persistence, or real data was added. See [ADR-0018](docs/adr/0018-explicit-unavailable-report-metric-reasons.md).

**Completed in PR #145 (research only):** document source-specific zero-row completeness and freshness rules for the Google Search candidate. Official guidance confirms that segmented all-zero rows and dates with no metrics can be omitted, common metrics have different update guidance from conversions, and historical values can be adjusted later. Retrieval time must remain distinct from metric coverage/freshness; an absent row cannot become zero without independent completeness evidence. No adapter or account connection was implemented. Required PR CI `36604492004` and post-merge CI `36604748472` passed. See the [Google Search mapping](docs/product/google-search-report-metric-mapping.md).

**Completed in PR #149:** add a provider-neutral observation contract that separates requested and covered windows, source response completion, row presence, retrieval time, and freshness evidence. A pure evaluator classifies source-data time under an explicit source/metric-family rule; missing or future-dated source evidence is `unknown`, and retrieval time alone does not affect freshness. Available values require a complete exact-period row and evaluator-produced `current` status. Synthetic thresholds are policy examples only, not provider guarantees. No adapter, account, or real data is added. Required PR CI `36617325319` and post-merge CI `36617630617` passed. See [ADR-0019](docs/adr/0019-report-observation-coverage.md).

**Completed in PR #150:** distinguish a complete report observation with unknown freshness from stale and partial data, with a typed `freshness_unknown` unavailable reason. Keep it valueless and require the evaluator result to match; no live adapter was added. Required PR CI `36618254042` and post-merge CI `36618532218` passed.

**Current synthetic foundation slice (`docs/report-source-freshness-evidence`, PR pending):** document the Google Ads evidence limits for per-row source time, report-window coverage, retrieval time, and provider SLO guidance. The reviewed official guides do not define a row-level `source_data_as_of` contract; record this as an evidence gap, not proof that no endpoint or metadata exists. Keep freshness unknown when the source cannot support the claim; do not add a live adapter.

**Next synthetic foundation slice:** define how the report presents its observed period and freshness evidence separately, including the unknown state, without presenting an SLO as a delivery guarantee.

## Phase 3 — First publishing and reporting integration

**Goal:** prove one authorized destination before expanding channel coverage.

- Choose the first paid-ad platform only after checking access and eligibility in Türkiye, app review, supported campaign/creative formats, authorization requirements, reporting coverage, policy constraints, and maintenance cost.
- Build OAuth/account connection and revocation, narrow scopes, a test/sandbox path, immutable action records, safe retries, and a user-visible emergency stop.
- Require explicit advertiser authorization and a hard platform-enforced spend boundary. Never let a model modify a cap or directly invoke a publishing API.
- Import performance data and present plain-language results. Do not imply that automated optimization is supported until the API and safe bounds are verified.
- **Acceptance:** a controlled test account can publish, report, stop, and recover from a simulated provider failure without exceeding its configured limits.

## Phase 4 — Limited beta and production readiness

**Goal:** invite a small pilot group only after the real operational and data protections are ready.

- Finish staging E2E, backup/restore, rollback, deployment-revision health reporting, and a tested CI merge gate.
- Review platform approvals, privacy notice/consent, model/provider data terms, data deletion/export, retention, OAuth token handling, accessibility, monitoring, and incident procedures.
- Estimate production hosting and AI costs; ask the owner before any new recurring service or advertiser campaign-spend feature is enabled.
- Select a small pilot cohort from the Türkiye market after the first workflow is validated; clinics may be included but are not the exclusive target.
- **Acceptance:** a documented pilot run stays within the approved service budget and advertiser caps, can be stopped and recovered, and produces a useful report with no unreviewed safety failures.

## Phase 5 — Omnichannel capability expansion

**Goal:** expand toward the Omneky capability benchmark after one complete channel is validated and the product has evidence from real user workflows.

- Add channels one at a time after verifying Türkiye-specific API access, platform approval, formats, reporting, policy obligations, and operating costs.
- Expand ad production and editing across image, short-form video, and other supported formats; make creative variations and review tools easy to use.
- Add cross-channel and creative-level analytics, plain-language insights, and explainable recommendations.
- Add A/B testing and bounded optimization only where the platform supports reliable measurements and advertiser-defined guardrails.
- **Acceptance:** every supported channel and optimization action has tested authorization, spend/schedule limits, traceable state changes, idempotent retries, stop/revoke behavior, and understandable reporting. Unsupported or uncertain actions remain paused.

## Deferred until evidence supports them

- Broad simultaneous channel coverage, vertical-specific workflow depth, native mobile clients, organic-content calendars, long-form video generation, full CRM, vector search, microservices, a separate queue service, and automatic cross-channel budget allocation.
- Production AI/provider selection and production hosting.

## Existing Phase 0 tasks retained as gates

Staging browser E2E for the demo, backup/restore, controlled rollback, and final cost/CI recording remain incomplete. They are useful before an external beta or production release, but no longer block a local synthetic-data website prototype. Continue to use the existing approved Heroku resources only; do not add a paid dyno, database, add-on, AI service, or production environment without a new owner decision.

Session-scoped prototype drafts must remain synthetic. Heroku staging now has a
daily `python manage.py clearsessions` job scheduled at 00:00 UTC through
Heroku Scheduler. The 2026-09-29 00:00 UTC execution is verified in Heroku logs
with exit status 0. Actual one-off dyno cost remains unverified. Scheduler is
best-effort; do not infer a real-data retention guarantee from session expiry
or this schedule.
