# GrowthTwin — current handoff

Last verified: 2026-09-29 14:37 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main at session start was `ceb0989ba6b44d56d5df91a81a4d9796ba8cca9b`; PR #109 (handoff sync) and #108 (system gap analysis) are merged. Main CI runs `36557534411` and `36557842942` passed. No open PR was present at session start.
- Current branch is `feat/first-search-campaign-foundation`, based on that main. It has uncommitted ADR, blueprint/project/roadmap updates and a workspace-owned synthetic campaign-draft model/migration plus owner-scoped application services. Changes are not yet committed or submitted; verify PR/CI after opening.
- PR #104 blueprint gate and prior Phase 1 prototype/workspace milestones remain as recorded in `PROJECT.md` and `ROADMAP.md`.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability reference, not a promise to ship all capabilities/channels at once.
- The detailed service/product blueprint is [docs/product/growthtwin-service-blueprint.md](../product/growthtwin-service-blueprint.md). It includes GrowthTwin-created and customer-owned creative paths, credit and separate ad fee/media spend concepts, a pre-purchase channel calculator, beginner/pro experience, campaign and aggregate reporting, creative experiments, initial official-source channel/legal findings, a phased delivery map, and a decision register.
- Phase 1.5 remains open: the first advertiser workflow/objective/cohort, first platform/API access, first lead destination, first text/image/video tasks, exact credit costs/TRY prices, service fees, and outcome/refund terms have not been finalized. The blueprint is a draft; its proposals are not silently accepted business/legal decisions.
- User-provided price anchors to validate: 100 credits = USD 10; USD 100 for 1,000 purchased credits plus 20% bonus = 1,200 usable credits; offer free introductory creation credits. Do not invent per-output credit costs or a final TRY/tax/payment rate card.
- The user explicitly said real data should wait until the system is fully ready. Keep all local/CI/staging work synthetic; do not connect real advertiser accounts, accept personal/customer/lead data, publish, charge or spend. The readiness gate and separate owner decision are required.
- Separate advertiser service requests from ad-generated leads. User's interest in refunding when an engagement target is missed remains a goal to explore, not an unconditional promise. Define controllable metrics, attribution, exclusions, caps, reserves, evidence, economics and current Turkish-law review before any performance guarantee.
- Use feature branches and PRs; never push directly to `main`. Successful PRs may be merged under the owner's standing authorization after local review and required CI passes. No new paid service or production provider is approved by this planning work.
- Existing Heroku staging and Scheduler observations, outstanding backup/restore, rollback and staging E2E gates are recorded in `PROJECT.md` and `ROADMAP.md`; staging remains synthetic-only.
- Current implementation inventory: [docs/product/current-system-gap-analysis.md](../product/current-system-gap-analysis.md). Local synthetic prototype and PR CI are ready for development, but there is no user-to-workspace campaign ownership, customer document/assets pipeline, credit/fee ledger, enforceable campaign policy, provider integration, lead routing, or real analytics. Do not represent the logical architecture as implemented.
- ADR-0008 selects a local synthetic first workflow: city-based, non-regulated service quote/contact campaign; Google Search candidate; advertiser-owned website; no raw lead custody in GrowthTwin. It does not establish customer demand, API approval, real-data/legal readiness, final prices, production model or live-publishing permission.

## Recent verified work

- PR #105 adds the detailed service blueprint, Türkiye platform availability/API distinction, official source notes for consumer advertising/KVKK/IYS and platform experiments, calculator/reporting requirements, price math, guarantee decision framework, readiness gate and phased plan. It updates `PROJECT.md` and `ROADMAP.md` so the plan is the canonical next-phase reference.
- Initial source review found TikTok and X self-serve ad-account country eligibility includes Türkiye, but that does not prove GrowthTwin API authorization or availability of every objective/placement. LinkedIn Marketing API access is vetted. Google YouTube reach planning API is allowlisted. Meta application access needs validation. Snapchat, Pinterest, Microsoft Ads, Yandex and local inventory need research before being described as supported. Details and links are in the blueprint.
- Official Commerce Ministry information reviewed includes advertising rule changes effective 2026-08-01 concerning targeted ads, AI-generated ad characters/digital likeness, minors, influencers and substantiation. KVKK cross-border data transfer and IYS commercial message obligations are identified for counsel-led workflow analysis. This is a planning scan, not legal advice or approval.
- Documentation-only `git diff --check` passed on PR #105. Application CI passed on GitHub. No local application tests were run for the documentation change.
- PR #108 merged the source-reviewed code-to-plan gap assessment, clarified logical architecture versus implemented coverage in `ARCHITECTURE.md`, and linked the assessment and sequencing in `ROADMAP.md`. Findings were based on main `60f3971`; no application code or external service was changed. Required PR CI passed; no local app tests were run.
- Current branch records platform source findings and the first synthetic workflow in ADR-0008 and the service blueprint; it adds a separate Workspace-owned campaign draft with owner-scoped services. The anonymous `site.CampaignDraft` remains unchanged; there is no UI/API endpoint or external provider call. Local `git diff --check`, Ruff formatting/lint, Django system check, and `makemigrations --check --dry-run` passed. Application tests have not been run locally.

## Next action

Review this branch diff, run `git diff --check`, commit and open a PR; review the actual changed files and wait for required CI. Merge only if review and CI pass. Then continue the synthetic-only campaign vertical slice, adding focused owner-isolation coverage before any campaign UI. Keep real data, customer uploads, AI provider calls, account connections, publishing, payments and spend blocked.
