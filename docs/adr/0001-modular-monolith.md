# ADR-0001: Modular monolith boundaries

- Status: Proposed
- Date: 2026-09-26
- Decision owner: Project owner

## Context

GrowthTwin needs clear boundaries for content, approval, AI-provider access, publishing, analytics, and workspace access. The reference architecture lists several candidate services and technologies, but the project is still in Phase 0 and has not selected an implementation stack or hosting environment.

## Decision drivers

- Keep the first implementation understandable and affordable for a small team.
- Preserve the ability to replace AI and social-platform providers.
- Make approval, tenant isolation, and external side effects explicit.
- Avoid operating services before a measured need exists.

## Options considered

1. **Modular monolith:** one product boundary with explicit modules and provider interfaces; can split a component later if justified.
2. **Microservices from the start:** independent deployments, but adds networking, deployment, and operational cost before scale or team needs are known.

## Decision

Propose a modular monolith as the initial logical architecture. Define workspace/access, content/versioning, approval, publishing, analytics, AI gateway, background jobs, persistence, and operations as boundaries. Keep the language, framework, database, authentication, job system, storage, cloud provider, and production AI provider undecided.

This is a proposal for review, not authorization to begin product implementation. Phase 0 restrictions remain in force.

## Consequences

- Modules can be built and reviewed without committing to a network of services.
- Provider adapters reduce coupling to trial AI and social APIs.
- Module boundaries need review to prevent cross-module data access and import cycles.
- A later split into workers or services will require evidence, cost review, and a new decision.

## Follow-up

- Review this proposal with the project owner.
- Record stack and hosting choices in separate ADRs only when needed for Phase 0 implementation.
