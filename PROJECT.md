# GrowthTwin project brief

## Current status

- Product direction was reset on 2026-09-27 at the owner's request: focus on the user-facing advertising website and its automated campaign journey.
- Local product development is authorized. The existing Django/PostgreSQL foundation and CI remain in use.
- The previous clinic-only Phase 0 demo is a foundation check, not the product itself. Staging browser E2E, backup/restore, and rollback remain unverified release-readiness tasks; they do not block local synthetic-data UX work.
- Product code beyond the small synthetic profile demo has not yet been implemented.
- Current implementation stack: Django 5.2 LTS + PostgreSQL in one modular monolith (accepted in ADR-0002). No new stack, paid service, or production AI provider is selected.

## Product goal

Build a polished, low-effort, self-service website that lets an individual, creator, or business request a digital advertising campaign in plain language and have GrowthTwin carry the routine work from brief intake through creative production, safe checks, publishing, performance reporting, and permitted follow-up optimization.

The normal campaign path should not require a GrowthTwin employee or agency operator. The advertiser starts the request, connects the selected account, and defines the allowed channel, schedule, content boundaries, and spend ceiling. After that setup, routine work can run automatically inside those limits. If the request is missing essential facts, the destination rejects it, a safety check fails, or a configured limit is reached, the system pauses that campaign and explains the next step to the advertiser.

For this project, "advertising" means digital campaign assets and their destination-platform launch and measurement. An organic-post calendar is a possible adjacent feature; it must not dilute the campaign-first MVP.

## Users and first market

- Product vision: do not hard-code GrowthTwin to dental clinics or a single industry. The campaign and brand model should work for different kinds of advertisers.
- Practical first audience: independent creators and Turkish small businesses, where a small business can reuse the account, brand, and campaign tools.
- The founders' existing dental-clinic contacts remain useful as an optional first pilot cohort, not as the product's only supported customer type.
- Keep the first usable release narrow: one validated advertiser workflow and one publishing destination can prove the end-to-end value. The first destination and exact pilot segment remain open until API feasibility and user feedback are checked.

## User experience principles

- Start with the user's goal in their own words. Ask only for information required to produce a safe, useful campaign; use progressive disclosure for channel, audience, timing, and budget details.
- Show what GrowthTwin is doing, what it needs, and the current campaign state without making the user manage internal workflow steps.
- Make the generated campaign easy to inspect and revise. Keep budget caps, connected destinations, automation status, and a prominent pause/stop control easy to find.
- Design for mobile and desktop, with Turkish-first copy and room for additional languages.
- Use accessible, consistent components and realistic synthetic data in local prototypes. Do not disguise mock output as a real publication or result.

## Campaign lifecycle

1. Capture a short goal/offer brief and the advertiser's brand facts and assets.
2. Turn the brief into a structured campaign plan with audience, objective, destination format, timing, and a cost boundary.
3. Generate copy and creative drafts; validate required fields, brand constraints, destination formats, factual claims, and platform rules.
4. Publish or schedule through an authorized platform connection only when the account, permissions, content checks, and user-defined budget/schedule limits allow it.
5. Collect results, explain them in plain language, and make follow-up changes only inside the advertiser's configured autonomy and spend limits.
6. Pause with an understandable message when confidence, policy, platform access, or budget is insufficient. Log all external actions and make them traceable.

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

1. Choose and validate the first advertiser segment and campaign type through the product prototype and pilot feedback.
2. Compare platform API access, review/approval requirements, supported formats, reporting coverage, and ongoing maintenance before selecting the first publishing destination.
3. Define the exact user-controlled autonomy settings, account consent, budget caps, and stop conditions before enabling automatic spend or publication.
4. Select production AI/data-processing terms and cost only after representative evaluations and a privacy review.
5. Decide pricing and any recurring production infrastructure after the first end-to-end pilot workflow is understood.
