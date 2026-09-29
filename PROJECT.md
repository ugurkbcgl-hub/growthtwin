# GrowthTwin project brief

## Current status

- Product direction was clarified on 2026-09-27 at the owner's request: Türkiye is the target market, and the product is for people and organizations that want to advertise. Dental clinics are one example, not the product boundary.
- Local product development is authorized. The existing Django/PostgreSQL foundation and CI remain in use.
- The previous clinic-only Phase 0 demo is a foundation check, not the product itself. Staging browser E2E, backup/restore, and rollback remain unverified release-readiness tasks; they do not block local synthetic-data UX work.
- The first public website slice is merged to `main`: responsive campaign brief, preview, simulated pause control, and sample report. Synthetic drafts are persisted to PostgreSQL and can be listed, resumed, edited, or deleted from their owning anonymous session. Expired sessions cannot access drafts; `clearsessions` removes expired session records and their drafts. The scheduled cleanup job has run once, but it is best-effort and does not establish a real-data retention guarantee; keep data synthetic. The content module exposes persistence-free `CampaignBrief` and `CampaignPlan` values; the session-owned ORM adapter remains in `site` under [ADR-0006](docs/adr/0006-campaign-brief-boundary.md). There is no AI call, platform connection, publication, or real metrics.
- Phase 1 acceptance was verified on 2026-09-29 through source/E2E review and manual desktop browser review. PR #100 removed desktop horizontal overflow, improved the temporary-data notice, and keeps the sample report visible after navigation; required PR and post-merge CI passed. Mobile remains covered by browser E2E. This is still a synthetic local prototype, not a launch-ready product.
- Phase 2 now has an authenticated workspace campaign list and local Google Search text preview (PR #113), owner-scoped changes to whitelisted synthetic budget/duration options and confirmed draft removal (PR #114), browser E2E for the owner flow and tenant boundary (PR #115), and a Turkish accessible sign-in journey with public registration closed (PR #116). PR #117 adds an equal-allocation daily planning average based on the synthetic media cap and dates; PR and post-merge CI passed. ADR-0009 defines the future asset intake boundary; PR #120 adds pure state-transition contracts only, with no file or provider operations, and PR #121 tests those transitions. Both PRs and post-merge CI passed. PR #122 adds a pure synthetic campaign action-policy check. PR #125 corrects the handoff scope so local synthetic development stays allowed while Phase 0 checks remain release gates. The current feature branch adds allowlisted synthetic evidence-source and observation-time metadata only; it remains caller-supplied, unverified, and disconnected from publishing. The campaign flow still creates only a fixed synthetic example. Free-text advertiser inputs remain withheld until the real-data readiness gate; no account connection, publishing, spend, or live forecast is available. Real advertiser data remains out of scope.
- Heroku staging has the previously approved Basic web dyno and Essential-0 PostgreSQL plus the Standard Free Heroku Scheduler add-on. A daily `python manage.py clearsessions` job is scheduled for 00:00 UTC (03:00 Europe/Istanbul) on the existing Basic dyno. On 2026-09-29, Scheduler showed Last Run at 2026-09-29 00:00 UTC and Next Due at 2026-09-30 00:00 UTC; Heroku logs showed the one-off process exited with status 0. Actual one-off dyno cost remains unverified. Scheduler is best-effort, so this is synthetic-staging cleanup only, not a real-data retention guarantee; see [ADR-0006](docs/adr/0006-campaign-brief-boundary.md).
- Current implementation stack: Django 5.2 LTS + PostgreSQL in one modular monolith (accepted in ADR-0002). No new stack, paid service, or production AI provider is selected. Main is `0fc8143d36ec9a60d36aaa8ac0a68b71d018adb3`; required CI for PR #125 (`36581766793`) and post-merge CI (`36582051706`) passed on 2026-09-29.

## Product goal

Build a polished, low-effort, self-service advertising platform for the Türkiye market. It should be useful to anyone who wants to advertise: individuals, creators, small and large businesses, and organizations across industries. Dental clinics are one possible customer example, not a special product boundary.

GrowthTwin's long-term capability benchmark is an integrated, AI-assisted advertising workflow: understand the advertiser's brand and offer; turn a plain-language goal into a campaign plan; generate and refine platform-ready copy, image, and video ads; launch approved campaigns through connected ad accounts; report results across channels; and recommend or perform bounded improvements based on measured performance. Omneky is a product capability reference for this breadth, not a commitment to copy every feature or channel in the first release. Public vendor feature claims do not establish GrowthTwin's access to those platforms, API eligibility in Türkiye, or feature parity.

The normal path should not require a GrowthTwin employee or agency operator. The advertiser supplies essential facts, authorizes each selected destination, and sets explicit content, schedule, and spend boundaries. Routine work may proceed autonomously only within those permissions and enforceable limits. When facts, authorization, policy confidence, provider state, or a limit is missing or uncertain, the campaign pauses and the user receives a clear explanation. The exact default review mode and first-release autonomy settings remain open decisions.

The capability direction and owner requirements are clear; a first service blueprint draft is in [docs/product/growthtwin-service-blueprint.md](docs/product/growthtwin-service-blueprint.md). It includes customer-owned document/content analysis and improvement, separate production credits and ad fees/media spend, pre-purchase channel estimates, beginner and professional paths, campaign-level and combined reports, creative testing, a Türkiye channel/legal research matrix, and a readiness gate. [ADR-0008](docs/adr/0008-first-mvp-google-search-leads.md) selects a narrow synthetic workflow: a city service quote/contact campaign, with Google Search as first channel candidate and the advertiser's existing site as destination. [ADR-0009](docs/adr/0009-asset-intake-processing-boundary.md) sets a contract-first safety boundary for future files. Neither decision establishes Google access, customer demand, data-processing terms, pricing, AI credit costs, lead CRM delivery, performance guarantees, API approval or legal readiness. Phase 1.5 remains open for those evidence and launch decisions.

For this project, "advertising" means paid digital advertising campaigns and their creative, launch, measurement, and bounded optimization. Organic social-post scheduling is outside the initial product scope unless later evidence justifies it.

## Users and first market

- Target market: Türkiye. The product is for people and organizations in Türkiye that want to run paid digital advertising, across industries and advertiser sizes.
- Do not hard-code GrowthTwin to dental clinics, creators, e-commerce, or a single vertical. Shared campaign, brand, and account workflows should support different advertiser types.
- Dental clinics, creators, and small businesses are examples of potential users. None is currently selected as the exclusive first segment.
- Keep the first usable release narrow: validate one campaign workflow and one publishing destination before broad channel coverage. The initial campaign type, pilot cohort, and destination remain open until user discovery and platform/API feasibility are checked.

## User experience principles

- Start with the user's goal in their own words. Ask only for information required to produce a safe, useful campaign; use progressive disclosure for channel, audience, timing, and budget details.
- Show what GrowthTwin is doing, what it needs, and the current campaign state without making the user manage internal workflow steps.
- Make the generated campaign easy to inspect and revise. Keep budget caps, connected destinations, automation status, and a prominent pause/stop control easy to find.
- Design for mobile and desktop, with Turkish-first copy and room for additional languages.
- Use accessible, consistent components and realistic synthetic data in local prototypes. Do not disguise mock output as a real publication or result.

## Campaign lifecycle

1. Learn the advertiser's brand, offer, assets, audience, and goal from a short guided intake.
2. Turn the goal into a structured campaign plan with objective, audience, channel, placements, timing, and spend boundaries.
3. Generate and refine platform-ready copy, image, video, and variants; validate claims, brand rules, destination formats, and platform policies.
4. Launch or schedule only through an explicitly authorized ad-account connection and within user-defined spend and schedule limits.
5. Collect and explain performance by campaign, channel, and creative; recommend or make follow-up changes only within the advertiser's configured autonomy and caps.
6. Pause with an understandable message when information, confidence, permissions, platform access, or budget is insufficient. Record external actions so they are traceable.

AI may propose and transform campaign material; deterministic application rules enforce authorization, budget caps, valid states, idempotency, and external-action boundaries. Never let a model call a publishing API or increase spend outside these controls.

## Existing resources and intended use

- **This shared Windows checkout:** the single source of truth at `C:\Users\Public\Desktop\GrowthTwin`; build and review changes here through feature branches and pull requests.
- **Django 5.2 + PostgreSQL 18.6:** keep the accepted one-application modular-monolith stack for the first website and product workflows. Reconsider the stack only if a working interface demonstrates a concrete limit.
- **GitHub repository and Actions CI:** use pull requests and the existing checks for every change. Keep browser E2E coverage focused on the critical advertiser journey as it is built.
- **Local workstation:** Windows 11, Python 3.13.15, PostgreSQL 18.6, 31.7 GB RAM, RTX 3050 Laptop GPU with 6 GB VRAM, and Ollama 0.34.4. Use it for local development and synthetic AI experiments without new infrastructure.
- **Local Qwen3 models:** 0.6B, 1.7B, and 4B are installed and fit the GPU. The one-run evaluation in `AI_PROVIDERS.md` found substantial workflow, safety, and structured-output weaknesses. They are prototyping candidates, not a production/autopublish decision.
- **NVIDIA Build/NIM:** evaluation only, with synthetic inputs. The earlier trial was useful for draft and claim-review experiments but had latency and invalid-JSON failures. Do not use trial endpoints to serve end users or send real advertiser data.
- **Heroku staging:** the owner approved and provisioned one Basic web dyno plus one Essential-0 PostgreSQL database at an observed estimate near USD 12/month before tax. Keep it for synthetic staging/release-readiness checks only; it is not production or an AI serving tier. Add no paid resource without a new decision. Its latest observed deployed code revision was `ac2f627d`, while current `main` is newer; recheck before any deployment.
- **Secrets:** use the existing local protected secret store or the provider's secret store. Never put secret values in chat, source, Git, logs, screenshots, or handoff files.

## Architecture and AI direction

- Keep the accepted Django/PostgreSQL modular monolith (ADR-0001 and ADR-0002): workspaces/advertisers, brand facts, campaign briefs, content/creative versions, budget and consent policy, publishing adapters, reporting, and background work remain explicit modules.
- Keep provider and publishing integrations behind replaceable server-side adapters. The browser must never receive platform secrets.
- Do not add a separate worker, queue, vector database, object store, frontend runtime, or AI service until a working product slice shows a need and cost is reviewed.
- No production AI model/provider has been selected. Compare candidates using representative synthetic ad briefs, schema checks, claim safety, quality, latency, cost, and failure behavior. Do not infer production suitability from the existing one-run clinic examples.

## Budget and security constraints

- The project reference sets a Phase 0 working limit of USD 100/month, a warning near USD 80/month, and owner approval for a single spend above USD 20. The separate Heroku approval covers only one Basic dyno and one Essential-0 database at about USD 12/month before taxes.
- Advertiser media spend is different from GrowthTwin infrastructure or subscription spend. Before any campaign can spend money, the advertiser must connect the account and set explicit, enforceable per-campaign and aggregate caps. The application must fail closed on missing or unreadable budget state.
- Use synthetic data in local development, CI, and staging. Never use trial/free AI endpoints with private advertiser data.
- Production use requires verified privacy/data terms, model licensing, platform app/API approval, account token protection and revocation, tenant isolation, audit logs, operational alerts, backups, and a tested stop/rollback path.
- Do not publish from staging, connect real advertiser accounts, deploy production, or provision new paid infrastructure as part of local website prototyping.

## Open decisions to resolve before real publishing

1. The synthetic first workflow and objective are recorded in ADR-0008; validate the city-service quote/contact hypothesis with actual user/problem research before selecting a pilot cohort or accepting real data.
2. Google Search is the first technical channel candidate in ADR-0008. Verify GrowthTwin developer-token access, OAuth/app review and production-account use, the eligible account/currency, campaign-total budget and stop behavior before any live publishing. Meta remains second and TikTok third in the research sequence; neither is integrated.
3. Specify what GrowthTwin sells in the first release: included work, creative formats, automation limits, exclusions, service packages, and pricing.
4. Distinguish advertiser requests to GrowthTwin from leads generated by ads. For generated leads, decide what is collected, who receives it, which destinations are supported, consent and access controls, delivery/retry behavior, retention, and deletion.
5. Map AI tasks separately for text, image, and video; evaluate tools/models, licensing, data terms, quality, safeguards, cost, latency, and failure behavior on representative synthetic inputs. No production provider is selected.
6. Define default review mode, opt-in autonomy, account consent, enforceable spend caps, stop conditions, and escalation to the advertiser before enabling live publication or spend.
7. Decide data categories, purposes, recipients, deletion/export, retention, and backup behavior before any real advertiser, customer, or lead data is accepted.
8. Estimate production hosting/inference costs after the first end-to-end pilot workflow is understood, and seek approval before adding recurring services.
9. A narrow synthetic first service, workflow and objective are selected in [ADR-0008](docs/adr/0008-first-mvp-google-search-leads.md); pilot hypothesis and user experience still need validation. Keep the rest on the staged expansion plan.
10. Research channel availability separately from GrowthTwin's API access; complete a scorecard with Turkish account registration/billing, permissions, forecasts, formats, reports, policies and maintenance.
11. Cost the proposed credit packages, free introductory credits and separate campaign fees; define TRY/tax/payment/refund terms. Do not promise a target-result refund until its metric, attribution, exclusions, cap, reserve, evidence and legal treatment are defined.
12. Decide supported customer document formats, rights/provenance, AI-provider transfer controls, and initial creative tasks for text/image/video using synthetic quality, safety, latency and cost evaluation.

## Omneky capability reference

The owner selected Omneky as a long-term capability benchmark for ad creation, connected campaign launch, cross-channel performance reporting, and bounded optimization. Its current public product pages are a reference, not independent verification or a GrowthTwin feature commitment. Recheck current capabilities and Türkiye-specific platform/API access when selecting an implementation target. Sources: [Omneky](https://www.omneky.com/) and [Campaign Launcher](https://www.omneky.com/campaign-launcher), checked 2026-09-27.
