# GrowthTwin roadmap

## Direction reset — 2026-09-27

The owner asked to refocus GrowthTwin on the actual self-service advertising website. The product vision is now an end-to-end campaign autopilot for individuals, creators, and businesses; the earlier dental-clinic-only content workflow is a possible pilot cohort, not the product boundary. See [PROJECT.md](PROJECT.md), [ARCHITECTURE.md](ARCHITECTURE.md), and accepted [ADR-0004](docs/adr/0004-self-service-advertising-autopilot.md).

The product should remove routine operator work after an advertiser gives a brief, connects an account, and sets explicit limits. The system must pause and notify the advertiser when it cannot safely proceed. Current work prioritizes the real website and local synthetic-data development; it does not authorize production publishing, real ad spend, or additional paid infrastructure.

## Existing foundation — in place for local product work

- Public GitHub repository, protected `main`, pull-request workflow, and CI are active. Latest verified `main` is `6aba41e`; no open PRs; CI run `36335898184` passed.
- Django 5.2 LTS + PostgreSQL 18 is the accepted local stack and is already scaffolded under `apps/web`.
- CI checks Django configuration, formatting, linting, dependency vulnerabilities, package builds, migrations, and focused tests. A synthetic profile edit E2E exists locally and in CI.
- Local browser E2E and GitHub-hosted CI provide the initial feedback loop. Keep local UI work on synthetic data.
- Heroku staging has one approved Basic web dyno and one Essential-0 PostgreSQL database (about USD 12/month before tax); the deployed app is still the synthetic demo. Current `main` is not yet deployed.

## Phase 1 — Product experience prototype (next)

**Goal:** demonstrate the simplest complete user experience without waiting for external APIs, paid infrastructure, or a production model.

- Build the public product entry and a mobile-friendly campaign workspace in the existing Django application.
- Let a user describe an advertising goal with a short plain-language brief, then progressively ask only for essential missing details such as destination, timing, and maximum spend.
- Show a believable campaign lifecycle with synthetic example output: request received, plan prepared, creative preview, destination/schedule, and performance summary. Label mock publishing and metrics clearly.
- Keep editing, current status, spend boundary, and pause/stop visible. Do not hard-code clinic fields.
- **Acceptance:** a new visitor can understand the offer; a synthetic advertiser can move through brief → campaign preview → mock result without staff help; the layout works on mobile and desktop; no external account, AI provider, or publishing API is called.

## Phase 2 — Local campaign vertical slice

**Goal:** connect the website to deterministic campaign records and evaluate draft generation without creating external side effects.

- Model advertiser/workspace, brand facts, campaign brief, versioned creatives, destinations, user-defined caps, and status history.
- Add a server-side AI gateway with validated structured output and provider adapters. Begin with local Ollama plus synthetic data; use NIM only for synthetic evaluation.
- Add quality checks for missing/unsupported claims, format constraints, and budget/schedule completeness. A rejected or ambiguous output stays paused.
- Verify tenant isolation, schema validation, retry/idempotency behavior, and the campaign user journey.
- **Acceptance:** the local end-to-end path saves a campaign, produces or safely rejects a structured draft, explains its state, and cannot publish or incur ad spend.

## Phase 3 — First publishing and reporting integration

**Goal:** prove one authorized destination before expanding channel coverage.

- Choose the first platform only after checking current API access, app review, supported campaign/creative formats, authorization requirements, reporting coverage, and maintenance cost.
- Build OAuth/account connection and revocation, narrow scopes, a test/sandbox path, immutable action records, safe retries, and a user-visible emergency stop.
- Require explicit advertiser authorization and a hard platform-enforced spend boundary. Never let a model modify a cap or directly invoke a publishing API.
- Import performance data and present plain-language results. Do not imply that automated optimization is supported until the API and safe bounds are verified.
- **Acceptance:** a controlled test account can publish, report, stop, and recover from a simulated provider failure without exceeding its configured limits.

## Phase 4 — Limited beta and production readiness

**Goal:** invite a small pilot group only after the real operational and data protections are ready.

- Finish staging E2E, backup/restore, rollback, deployment-revision health reporting, and a tested CI merge gate.
- Review platform approvals, privacy notice/consent, model/provider data terms, data deletion/export, retention, OAuth token handling, accessibility, monitoring, and incident procedures.
- Estimate production hosting and AI costs; ask the owner before any new recurring service or advertiser campaign-spend feature is enabled.
- Start with the owners' existing business contacts as an optional cohort; broaden only after observed usability and quality evidence.
- **Acceptance:** a documented pilot run stays within the approved service budget and advertiser caps, can be stopped and recovered, and produces a useful report with no unreviewed safety failures.

## Deferred until evidence supports them

- More ad platforms, multiple vertical-specific workflows, native mobile clients, organic-content calendars, long-form video generation, full CRM, vector search, microservices, a separate queue service, and automatic multi-channel budget optimization.
- Production AI/provider selection and production hosting.

## Existing Phase 0 tasks retained as gates

Staging browser E2E for the demo, backup/restore, controlled rollback, and final cost/CI recording remain incomplete. They are useful before an external beta or production release, but no longer block a local synthetic-data website prototype. Continue to use the existing approved Heroku resources only; do not add a paid dyno, database, add-on, AI service, or production environment without a new owner decision.
