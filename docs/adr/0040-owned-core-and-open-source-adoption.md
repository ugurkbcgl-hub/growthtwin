# ADR-0040: Yaparo-owned core and staged open-source adoption

- Status: Accepted strategy and delivery priorities; individual new packages/providers remain evaluation candidates
- Date: 2026-10-23
- Decision owner: Project owner, explicit request for an adaptable, self-operated, open-source-based product and delegated technical planning

## Context

The owner requests a sustainable product assembled from current maintained projects, with in-product editing and replaceable AI providers. The present system is a tested local synthetic prototype with narrow Google PAUSED TEST evidence; it is not a complete commercial advertising service. Prior work overemphasized connection recovery relative to the unfinished customer creative journey.

## Decision

1. Retain the Django/PostgreSQL modular monolith. Own users/workspaces, brand facts, assets, editable creative documents, campaigns, permissions, money and report semantics.
2. Prefer maintained packages behind thin application interfaces. Whole-product forks require a demonstrated customer benefit, usable license/edition, upgrade path and lower total implementation/operation cost. None is selected now.
3. Define independence as self-operated core/editor, portable data and replaceable services. Advertising networks/payment processors and selected hosted models remain external dependencies.
4. Prioritize a synthetic brand/asset/editor/export slice. Compare Fabric with one complete MIT editor using the same task before adoption; Uppy/Pillow are intake/processing candidates. Provider access is not required for basic editing.
5. Keep application-owned AI task/capability profiles and versioned request/result/provenance. Compare PydanticAI with existing direct adapters; defer additional orchestration/gateway frameworks until needed. Quality, cost and data-policy eligibility govern model upgrades/fallbacks.
6. Add worker/storage/frontend build components only when the slice demonstrates need and operating cost is reviewed. No production host, paid service, production model or unrestricted real-data path is selected by this ADR.
7. Keep exact Google TEST histories, private backup and closed candidate boundaries; no resetting, identity substitution or repeated preparation. The protected candidate recovery task becomes a separate integration workstream, not a prerequisite for synthetic creative-studio development.
8. Use the [master plan](../product/yaparo-open-source-master-plan.md), [research register](../product/open-source-candidate-research.md) and [Y01–Y32 delivery sequence](../product/yaparo-delivery-plan.md). All unimplemented capabilities stay explicitly pending.

## Relationship to earlier decisions

Reaffirms ADR-0001/0002 architecture while their original clinic/Phase0 context remains historical. Reorders the 21 October delivery sequence in ROADMAP: content/editing advances before further broad connector-recovery work. Retains ADR-0008's first Google Search technical channel and advertiser-site lead destination. Extends ADR-0009 from contract-only planning toward gated synthetic implementation; real asset intake still requires its security/data conditions. Does not supersede authorization, tenant, no-resend, consent, budget or launch protections in later ADRs.

## Alternatives and consequences

- Full Postiz/Mixpost replacement: useful social-posting products but insufficient paid-ad/commerce scope and material stack/edition/license differences.
- Dify/n8n as product core: usage/edition conditions and ownership boundaries require case-specific review; no automatic commercial adoption.
- Entirely bespoke features: maximizes code ownership but repeats standard editor/auth/worker work and increases maintenance.
- Selected approach: fewer custom standard components, more integration/upgrade responsibility. Code license, model/font/media rights and provider terms are tracked separately. A recent push or popularity is not a compatibility/security proof.

## Acceptance and review

First slice must save/reopen an editable synthetic design, preserve Turkish text/layers and export without provider calls. Before production: customer isolation, cost/credit consistency, explicit financial consent, stop/reconciliation, actual reporting, current staging/restore/rollback, privacy/legal and applicable platform approvals. Customer demand is validated through observed tasks and pilots, not market-size figures.

Monthly reviewed dependency upgrades and quarterly exit/restore checks are proposed operating cadence, not newly enabled automations. No application code, schema, credentials, API permissions, deployments or paid resources change in this planning milestone.
