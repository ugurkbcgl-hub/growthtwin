# GrowthTwin — current handoff

Last verified: 2026-09-29 15:10 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main is `d242a892d5aef6502cb64c02edd1a50eaee33e78`; PR #110, #111 and #112 are merged. PR #112 required CI `36564841865` and post-merge main CI `36565059126` passed. No open PR was present when checked.
- Current branch is `feat/workspace-campaign-preview`, based on PR #112. Its uncommitted changes add authenticated owner-scoped list/preview launched only from a fixed synthetic example, Turkish TRY formatting, navigation, tests and documentation; free-text advertiser inputs are withheld until readiness gates are met. No PR is open yet.
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
- Current branch checks: 14 campaign tests passed locally, including an assertion that submitted free text cannot replace fixed sample content; Django system check, migration check, Ruff lint/format, `collectstatic` and `git diff --check` passed. Tests use synthetic fixtures and do not call providers.

## Next action

Review, commit and open a PR for `feat/workspace-campaign-preview`; wait for required CI and merge only if the diff and checks remain clean. The branch's authenticated workspace list/preview persists only a fixed synthetic sample and remains separate from the anonymous prototype. After merge, implement owner-scoped revision/removal using synthetic inputs. Keep real data, uploads, AI provider calls, account connections, publishing, payments and spend blocked.
