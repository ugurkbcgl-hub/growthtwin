# GrowthTwin — current handoff

Last verified: 2026-09-29 15:31 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main is `2f4fd6a21cd1c2ca4d624772d30c73380c2eb4f1`; PRs #110–#114 are merged. PR #114 CI `36567921819` and post-merge main CI `36568151300` passed. No open PR existed when checked for the new branch.
- Current branch is `feat/workspace-campaign-e2e`, based on PR #114. It adds authenticated browser E2E tests for the fixed-synthetic campaign create/edit/delete flow and tenant access boundary, plus documentation updates. No PR is open yet.
- PR #104 blueprint gate and prior Phase 1 prototype/workspace milestones remain as recorded in `PROJECT.md` and `ROADMAP.md`.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability reference, not a promise to ship all capabilities/channels at once.
- The detailed service/product blueprint is [docs/product/growthtwin-service-blueprint.md](../product/growthtwin-service-blueprint.md). It includes GrowthTwin-created and customer-owned creative paths, credit and separate ad fee/media spend concepts, a pre-purchase channel calculator, beginner/pro experience, campaign and aggregate reports, creative experiments, Türkiye channel/legal research, a phased delivery map and open decisions.
- Phase 1.5 remains open: user-demand validation, first platform/API access, exact credit costs/TRY prices, service fees, lead routing and outcome/refund terms are unresolved. The blueprint is a draft, not an authorization or legal conclusion.
- User price anchors to validate: 100 credits = USD 10; USD 100 for 1,000 purchased credits plus 20% bonus = 1,200 usable credits; offer free introductory creation credits. Do not invent per-output credit costs or a final TRY/tax/payment rate card.
- The user explicitly said real data should wait until the system is fully ready. Keep local/CI/staging work synthetic; do not connect real advertiser accounts, accept customer/lead data, publish, charge or spend. Separate readiness gates and owner decision are required.
- Any performance guarantee remains a hypothesis to assess, not an unconditional promise. Define controllable metrics, attribution, exclusions, caps, reserves, evidence, economics and current Turkish-law review first.
- Use feature branches and PRs; never push directly to `main`. Successful PRs may be merged under the owner's standing authorization after review and required CI passes. No new paid service or production provider is approved.
- Heroku staging/Scheduler observations and outstanding backup/restore, rollback and staging E2E gates are recorded in `PROJECT.md` and `ROADMAP.md`; staging remains synthetic-only.
- Current implementation inventory: [docs/product/current-system-gap-analysis.md](../product/current-system-gap-analysis.md). Workspace-owned drafts, tenant tests and provider-free Search text planning are merged. No customer document pipeline, credit/fee ledger, enforceable live publish policy, real provider integration, lead routing or real analytics exists.
- ADR-0008 selects a local synthetic workflow: city-based, non-regulated service quote/contact campaign; Google Search as a technical candidate; advertiser-owned website; no raw lead custody in GrowthTwin. It does not establish customer demand, API approval, real-data/legal readiness, final prices, production model or live-publishing permission.

## Recent verified work

- PR #105 adds the detailed service blueprint and initial official-source Türkiye platform/legal research; open decisions and gates remain documented.
- PR #108 adds a source-reviewed code-to-plan gap assessment and clarifies logical architecture versus implemented coverage.
- PR #110 adds the workspace-owned campaign draft, constraints, owner-scoped services and ADR-0008; anonymous `site.CampaignDraft` remains separate.
- PR #111 adds tenant-isolation and validation tests.
- PR #112 adds provider-free, source-traceable Google Search text assets with RSA character limits and explicit unavailable forecast/keyword states. Required PR and post-merge CI passed.
- PR #113 adds login-protected workspace list and fixed-sample campaign creation/preview. It withholds free-text advertiser inputs until readiness gates; 14 targeted campaign tests and PR/main CI passed.
- PR #114 adds whitelisted budget/duration edits and confirmed owner-scoped deletion. Its 22 focused campaign tests, PR CI and post-merge main CI passed.
- Current branch's 3 browser E2E tests pass locally, including the mobile owner flow, confirmed deletion, foreign-draft 404 and horizontal overflow checks. Ruff lint/format and `git diff --check` pass. No provider call is made.

## Next action

Review and open a PR for `feat/workspace-campaign-e2e`; wait for required CI and merge only if the diff and checks remain clean. It verifies mobile create/edit, confirmed delete and that another user receives not found. Keep real data, uploads, AI provider calls, account connections, publishing, payments and spend blocked.
