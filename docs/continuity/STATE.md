# GrowthTwin — current handoff

Last verified: 2026-09-29 13:41 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main is `60f39717fe3102fe764670e29023554368e6b2e3`; latest main CI run `36552662332` passed. PR #105 and subsequent documentation PRs are merged. No open PR was present at audit start.
- Current working branch is `docs/current-system-foundation-audit`, based on that main commit. It contains documentation changes for the implementation gap inventory, architecture coverage, and roadmap sequencing; these are not yet committed or submitted as a PR. Recheck live PR and CI status before repository actions.
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

## Recent verified work

- PR #105 adds the detailed service blueprint, Türkiye platform availability/API distinction, official source notes for consumer advertising/KVKK/IYS and platform experiments, calculator/reporting requirements, price math, guarantee decision framework, readiness gate and phased plan. It updates `PROJECT.md` and `ROADMAP.md` so the plan is the canonical next-phase reference.
- Initial source review found TikTok and X self-serve ad-account country eligibility includes Türkiye, but that does not prove GrowthTwin API authorization or availability of every objective/placement. LinkedIn Marketing API access is vetted. Google YouTube reach planning API is allowlisted. Meta application access needs validation. Snapchat, Pinterest, Microsoft Ads, Yandex and local inventory need research before being described as supported. Details and links are in the blueprint.
- Official Commerce Ministry information reviewed includes advertising rule changes effective 2026-08-01 concerning targeted ads, AI-generated ad characters/digital likeness, minors, influencers and substantiation. KVKK cross-border data transfer and IYS commercial message obligations are identified for counsel-led workflow analysis. This is a planning scan, not legal advice or approval.
- Documentation-only `git diff --check` passed on PR #105. Application CI passed on GitHub. No local application tests were run for the documentation change.
- This branch adds a source-reviewed code-to-plan gap assessment, clarifies the logical target versus implemented coverage in `ARCHITECTURE.md`, and links the assessment and sequencing in `ROADMAP.md`. Findings are based on main `60f3971`; no application code or external service was changed. Local app tests have not been run.

## Next action

Finish reviewing this documentation branch, run `git diff --check`, commit and open a PR, then review the rendered changes and wait for required CI. Merge only if review and CI pass. After that, continue Phase 1.5: compare Google/Meta (and TikTok if relevant) for one synthetic city service-lead scenario, disclose evidence/cost/access uncertainty, and present the first-release workflow for owner selection. Only after that selection should the smallest synthetic-only workspace-authorization and campaign-persistence contracts begin. Keep real data, account connections, publishing, and spend blocked.
