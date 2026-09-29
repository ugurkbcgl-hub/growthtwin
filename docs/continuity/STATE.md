# GrowthTwin — current handoff

Last verified: 2026-09-29 15:51 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `afdfb82cef22e4fe21700b5169998dcc1ddd0a29`; PR #116 is merged. Its required CI `36570343105` and post-merge main CI `36570612418` passed. The main checkout was clean when the next feature branch was created.
- Current branch: `feat/synthetic-budget-pacing`, based on the merged main. It adds an equal-allocation daily planning average to the synthetic Search plan, explicitly distinct from platform spend limits and performance forecasts. The change is not yet committed or submitted as a PR.
- PRs #113–#116 and their relevant post-merge CI passed. Earlier campaign/workspace milestones remain detailed in `PROJECT.md` and `ROADMAP.md`.

## Product and safety context

- GrowthTwin is for people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local product development is authorized, but real advertiser/customer/lead data must wait until the readiness gate and a separate owner decision. Keep local, CI, and staging data synthetic; do not connect real accounts, publish, charge or spend.
- The current authenticated campaign workspace creates only a fixed synthetic example. No public registration, uploads, AI provider calls, account connections, live forecasts, publication, or payment exist.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and advertiser-owned website destination. It does not prove demand, API eligibility, forecast availability, final prices, legal readiness or permission to publish.
- Keep the current Django/PostgreSQL monolith and approved Heroku staging footprint. Do not add paid resources. Staging E2E, backup/restore, and rollback remain release-readiness gates; actual Scheduler one-off cost remains unverified.
- Use feature branches and PRs, never push directly to `main`. The owner has authorized merging successful PRs after local review and required CI pass.

## Recent verified work

- PR #113 adds the authenticated fixed-sample campaign list and preview; #114 adds owner-scoped bounded synthetic settings and confirmed deletion; #115 adds browser E2E for mobile owner flow and tenant isolation.
- PR #116 adds Turkish accessible sign-in, preserves the intended return path, keeps public registration closed, and makes account entry visible on mobile. Its PR CI and post-merge CI passed.
- On the current branch, the plan displays a calculated equal-allocation daily average from the total synthetic media cap and flight duration. It does not infer reach, clicks, cost performance, or a platform-enforced daily limit. Local tests have not been run for this current change.

## Open risks and decisions

- Real-data readiness: secure file ingestion, privacy/retention, data recipients, production provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.

## Next action

Review the daily pacing calculation and localized display, open a PR, and merge only after review and required CI pass. Fix any CI failures before merging. Keep forecasts unavailable and all real-data/external-action gates closed.
