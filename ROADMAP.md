# GrowthTwin roadmap

## Direction reset — 2026-09-27

The owner clarified that Türkiye is the target market and GrowthTwin should serve anyone who wants to advertise. Dental clinics, creators, and small businesses are examples, not product boundaries. Omneky is a long-term capability benchmark for ad creation, campaign launch, unified reporting, and bounded optimization. See [PROJECT.md](PROJECT.md), [ARCHITECTURE.md](ARCHITECTURE.md), accepted [ADR-0004](docs/adr/0004-self-service-advertising-autopilot.md), and [ADR-0005](docs/adr/0005-turkey-first-advertising-platform.md).

The product should remove routine GrowthTwin-operator work after an advertiser explains a goal, authorizes an account, and sets explicit limits. Routine work may run within those boundaries; the system must pause and notify the advertiser when it cannot safely proceed. Omneky-style multi-channel breadth is a long-term target, not the first-release scope. Current work prioritizes the local website and synthetic-data development; it does not authorize production publishing, real ad spend, or additional paid infrastructure.

## Existing foundation — in place for local product work

- Public GitHub repository, protected `main`, pull-request workflow, and CI are active. Verified `main` is `d79082d`; no open PRs at the start of issue #22; CI run `36339595216` passed.
- Django 5.2 LTS + PostgreSQL 18 is the accepted local stack and is already scaffolded under `apps/web`.
- CI checks Django configuration, formatting, linting, dependency vulnerabilities, package builds, migrations, and focused tests. A synthetic profile edit E2E exists locally and in CI.
- Local browser E2E and GitHub-hosted CI provide the initial feedback loop. Keep local UI work on synthetic data.
- Heroku staging has one approved Basic web dyno and one Essential-0 PostgreSQL database (about USD 12/month before tax); the deployed app is still the synthetic demo. Current `main` is not yet deployed.

## Phase 1 — Product experience prototype

**Goal:** demonstrate a clear, low-effort paid-advertising journey for a user in Türkiye without waiting for external APIs, paid infrastructure, or a production model.

Status: the initial product-experience slice is complete and merged to `main` at `d79082d`; PR #21 and its required CI completed successfully. It is a synthetic brief → preview → simulated pause → sample-report flow, not a connected ad platform. The bullets below record its validated scope; Phase 2 is the next implementation phase.

- Build the public product entry and a mobile-friendly campaign workspace in the existing Django application.
- Let any advertiser in the Türkiye target market describe a goal with a short plain-language brief, then ask only for essential missing details such as audience, destination, timing, and maximum spend.
- Demonstrate brand/offer intake, a campaign plan, and on-brand ad concepts in a simple experience.
- Show a believable lifecycle with synthetic output: request received, plan prepared, creative preview, destination/schedule, simulated publication, and performance summary. Label mock publishing and metrics clearly.
- Keep editing, current status, spend boundary, and pause/stop visible. Do not hard-code clinic fields.
- **Acceptance:** a new visitor can understand the offer; a synthetic advertiser can move through brief → campaign preview → mock result without staff help; the layout works on mobile and desktop; no external account, AI provider, or publishing API is called.

## Phase 2 — Local campaign vertical slice

**Goal:** connect the website to deterministic campaign records and evaluate draft generation without creating external side effects.

- Model advertiser/workspace, brand facts and assets, campaign brief, versioned multi-format ad creatives, destinations, user-defined caps, and status history.
- Add a server-side AI gateway with validated structured output and provider adapters. Begin with local Ollama plus synthetic data; use NIM only for synthetic evaluation.
- Add quality checks for missing/unsupported claims, format constraints, and budget/schedule completeness. A rejected or ambiguous output stays paused.
- Verify tenant isolation, schema validation, retry/idempotency behavior, and the campaign user journey.
- **Acceptance:** the local end-to-end path saves a campaign, produces or safely rejects structured ad drafts, explains its state, and cannot publish or incur ad spend.

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
Heroku Scheduler. The first execution and actual one-off dyno cost remain
unverified. Scheduler is best-effort; do not infer a real-data retention
guarantee from session expiry or this schedule.
