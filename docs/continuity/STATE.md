# GrowthTwin — current handoff

Last verified: 2026-09-29 15:58 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `d65acc2f4614f5b1004b90cfb8a8f503f28289ae`; PR #117 is merged. Required PR CI `36571112986` and post-merge main CI `36571373689` passed. No open implementation PR is known.
- The main checkout was clean when this documentation branch `docs/asset-ingestion-next-step` was created. This branch only refreshes project/roadmap/gap-analysis continuity after PR #117. It has not yet been committed or opened as a PR.
- PR #116 localized and improved the login journey. PR #117 added an equal-allocation daily planning average to the fixed synthetic Search campaign. Details and prior milestones are in `PROJECT.md` and `ROADMAP.md`.

## Product and safety context

- GrowthTwin is for people and organizations in Türkiye who want to advertise; clinics are one possible sector. Omneky is a long-term capability benchmark, not a first-release scope promise.
- Local product development is authorized, but real advertiser/customer/lead data must wait until the readiness gate and a separate owner decision. Keep local, CI, and staging data synthetic; do not connect real accounts, publish, charge or spend.
- The authenticated campaign workspace creates only a fixed synthetic example. No public registration, uploads, AI provider calls, account connections, live forecasts, publication, or payment exist.
- ADR-0008 selects a synthetic city-service quote/contact flow, Google Search as a technical candidate, and advertiser-owned website destination. It does not prove demand, API eligibility, forecast availability, final prices, legal readiness or permission to publish.
- Keep the Django/PostgreSQL monolith and approved Heroku staging footprint. Do not add paid resources. Staging E2E, backup/restore, and rollback remain release-readiness gates; actual Scheduler one-off cost remains unverified.
- Use feature branches and PRs, never push directly to `main`. The owner has authorized merging successful PRs after local review and required CI pass.

## Recent verified work

- PR #113 adds the authenticated fixed-sample campaign list and preview; #114 adds owner-scoped bounded synthetic settings and confirmed deletion; #115 adds browser E2E for mobile owner flow and tenant isolation.
- PR #116 adds Turkish accessible sign-in, preserves the intended return path, keeps public registration closed, and makes account entry visible on mobile. Its PR and post-merge CI passed.
- PR #117 displays total synthetic media budget, dates, and the equal-allocation daily average. It labels this as arithmetic planning, not a platform daily limit or performance forecast. Its PR and post-merge CI passed.

## Open risks and decisions

- Real-data readiness: secure file ingestion, privacy/retention, data recipients, production provider terms, platform/API approvals, token controls, audit/stop/revoke, backup/restore and rollback remain incomplete.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees and production AI/provider remain undecided or unverified.
- Google forecasts and keyword ideas remain unavailable until eligible authorized sources are connected and verified.

## Next action

Define the storage/provider-independent asset intake and processing contract using synthetic-only examples: ownership, rights and AI consent, quarantine, scanning, extraction, provenance, failure, and deletion states. Keep file upload and persistence closed until privacy, retention, parser isolation, malware scanning, deletion, and tenant isolation are demonstrably ready and the owner separately opens the real-data gate.
