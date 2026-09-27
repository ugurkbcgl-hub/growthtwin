# ADR-0004: Self-service advertising autopilot

- Status: Accepted
- Date: 2026-09-27
- Decision owner: Project owner

## Context

The earlier project brief focused on AI-assisted social content for dental clinics, and the roadmap prioritized completing every staging/recovery task before building product workflows. The owner has redirected the project toward the actual website: a polished experience that accepts an advertising request and carries it through campaign production, publishing, and reporting with minimal user effort and no routine GrowthTwin staff involvement.

The current checkout already has a Django/PostgreSQL modular-monolith foundation, CI, a synthetic profile demo, a local Ollama installation, exploratory NVIDIA NIM results, and an approved Heroku staging app. The local model and trial service measurements are not sufficient to authorize production advertising or trusted autonomous decisions.

## Decision drivers

- Make the user's end-to-end advertising result the center of product and engineering work.
- Make brief intake simple and keep users informed without making them operate an internal workflow.
- Support different advertiser types instead of hard-coding dental clinics.
- Automate routine work after the advertiser explicitly connects destinations and sets boundaries.
- Prevent model output, missing data, provider errors, or retries from bypassing spend or publishing limits.
- Use existing local and CI resources before adding infrastructure or recurring costs.

## Options considered

1. Continue with a dental-clinic content approval tool and complete all Phase 0 staging/recovery tasks before product development. This preserves the earlier narrow scope but does not address the owner's updated product goal.
2. Build a broad, self-service digital advertising autopilot. Routine campaigns proceed within advertiser-authorized account, content, schedule, and spend limits; exceptional or uncertain cases pause for the advertiser. Develop the website locally with synthetic data first.
3. Start with a full cross-platform advertising agency service and human-managed campaigns. This could hide product uncertainty behind staff effort and would contradict the desired low-effort, automated service.

## Decision

This decision supersedes ADR-0002's earlier restriction that product implementation was not authorized. ADR-0002's accepted Django/PostgreSQL stack and local-environment decisions remain in force.

Adopt option 2 as the product direction. GrowthTwin is a self-service advertising website for individuals, creators, and businesses; the first practical users may be Turkish small businesses and creators. Dental clinics may serve as an early pilot cohort, but are not the only supported industry.

The normal journey is: a plain-language request; a short guided clarification for essential facts; structured campaign plan and creative drafts; deterministic checks; authorized scheduling/publication; understandable performance reporting; and bounded follow-up optimization. A GrowthTwin staff reviewer is not required for each routine step. The advertiser must authorize each destination, set explicit schedule and content boundaries, and choose enforceable campaign and aggregate spend caps. The product must pause rather than guess when required information, authorization, policy confidence, or a cap is missing or uncertain.

The owner authorized local product website development before the older staging/recovery checklist is complete. The existing local checkout, Django/PostgreSQL stack, CI, and synthetic data are the implementation path. Staging E2E, backup/restore, rollback, privacy/security review, and real platform integration remain gates before an external beta or production. This decision does not authorize production deployment, live ad spend, a production model, a new provider, or additional paid services.

## Consequences

- Product architecture and UI must be advertiser- and campaign-oriented, not clinic-oriented.
- The first product slice may use clearly labeled simulated publishing and metrics; the real platform can be selected after API feasibility is checked.
- Budget caps, OAuth consent, deterministic validators, idempotent actions, logs, and a stop/revoke path become core safety requirements.
- The user experience and creative quality matter alongside correctness because the website must reduce effort while producing useful campaign assets.
- Broad market and multi-platform support remain a vision; the first MVP must stay narrow enough to validate one user journey.
- No current AI evaluation supports letting a model hold credentials, publish directly, or control spend.

## Follow-up

- Build a responsive local campaign-intake and campaign-status prototype with synthetic examples.
- Select the initial user segment and campaign type through that prototype and pilot feedback.
- Compare destination-platform API access, permissions, reviews, publishing formats, and reporting before selecting the first real adapter.
- Expand synthetic model evaluation before choosing any production inference provider.
- Update `PROJECT.md`, `ROADMAP.md`, `ARCHITECTURE.md`, `SECURITY.md`, `TESTING.md`, and `AGENTS.md` to follow this decision.
