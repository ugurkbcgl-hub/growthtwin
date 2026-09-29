# GrowthTwin — current handoff

Last verified: 2026-09-29 12:44 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main contains PR #105 at `ea5819d` (`docs: expand Türkiye-first service blueprint`); working tree was clean after fast-forwarding origin/main. PR #105 is merged. Its PR CI run `36550819556` and post-merge main CI run `36551064892` both passed, including Django checks/tests and browser E2E.
- No other open PR was present immediately after PR #105 merged. Recheck live status before the next repository action.
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

## Recent verified work

- PR #105 adds the detailed service blueprint, Türkiye platform availability/API distinction, official source notes for consumer advertising/KVKK/IYS and platform experiments, calculator/reporting requirements, price math, guarantee decision framework, readiness gate and phased plan. It updates `PROJECT.md` and `ROADMAP.md` so the plan is the canonical next-phase reference.
- Initial source review found TikTok and X self-serve ad-account country eligibility includes Türkiye, but that does not prove GrowthTwin API authorization or availability of every objective/placement. LinkedIn Marketing API access is vetted. Google YouTube reach planning API is allowlisted. Meta application access needs validation. Snapchat, Pinterest, Microsoft Ads, Yandex and local inventory need research before being described as supported. Details and links are in the blueprint.
- Official Commerce Ministry information reviewed includes advertising rule changes effective 2026-08-01 concerning targeted ads, AI-generated ad characters/digital likeness, minors, influencers and substantiation. KVKK cross-border data transfer and IYS commercial message obligations are identified for counsel-led workflow analysis. This is a planning scan, not legal advice or approval.
- Documentation-only `git diff --check` passed on PR #105. Application CI passed on GitHub. No local application tests were run for the documentation change.

## Next action

Complete one decision-ready MVP scenario in the blueprint: score Google/YouTube, Meta, TikTok, X and LinkedIn for one clearly specified advertiser goal in Türkiye; identify the required official API/app approvals and forecast/report capabilities; then draft example channel budget/estimate output and separate credit/service/media cost breakdown for the same scenario. Keep unknowns marked unknown and real data blocked. Use that concrete comparison to prepare—not assume—the first Phase 1.5 owner decisions before any authenticated workspace UI expansion.
