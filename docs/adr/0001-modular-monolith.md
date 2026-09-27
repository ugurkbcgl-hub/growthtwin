# ADR-0001: Modular monolith boundaries

- Status: Accepted
- Date: 2026-09-27
- Decision owner: Project owner

## Context

GrowthTwin needs clear boundaries for content, approval, AI-provider access, publishing, analytics, and workspace access. The project remains in Phase 0. The initial application stack is recorded separately in [ADR-0002](0002-application-stack-and-local-environment.md); hosting and several supporting technologies remain open.

## Decision drivers

- Keep the first implementation understandable and affordable for a small team.
- Preserve the ability to replace AI and social-platform providers.
- Make approval, tenant isolation, and external side effects explicit.
- Avoid operating services before a measured need exists.

## Options considered

1. **Modular monolith:** one product boundary with explicit modules and provider interfaces; can split a component later if justified.
2. **Microservices from the start:** independent deployments, but adds networking, deployment, and operational cost before scale or team needs are known.

## Decision

Adopt a modular monolith as the initial logical architecture. Define workspace/access, content/versioning, approval, publishing, analytics, AI gateway, background jobs, persistence, and operations as boundaries. The initial application stack is decided in ADR-0002. Keep authentication extensions, job system, storage, cloud provider, and production AI provider undecided until a concrete need is reviewed.

This decision accepts the architecture boundaries; it does not authorize product implementation. Phase 0 restrictions remain in force.

## Consequences

- Modules can be built and reviewed without committing to a network of services.
- Provider adapters reduce coupling to trial AI and social APIs.
- Module boundaries need review to prevent cross-module data access and import cycles.
- A later split into workers or services will require evidence, cost review, and a new decision.

## Follow-up

- Review module boundaries before adding implementation.
- ADR-0002 records the initial application stack. Record hosting and supporting technology choices in separate ADRs before implementation depends on them.
