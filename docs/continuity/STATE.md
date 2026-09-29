# GrowthTwin — current handoff

Last verified: 2026-09-29 23:00 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `48be3d3` after PR #154. PR #150 required/post-merge CI `36618254042`/`36618532218` and PR #151 required/post-merge CI `36619100149`/`36619387519` passed. PR #152 required/post-merge CI `36619787628`/`36620109320` and PR #153 CI `36621068238` passed; PR #153 post-merge CI `36621329777` passed. PR #154 required CI `36622723566` and post-merge CI `36622985685` both passed at 2026-09-29 23:00 Europe/Istanbul.
- Current branch: `docs/report-status-handoff`, based on merged `main`; records the completed report observation-status UI and CI results, with visual inspection as the next action.
- PR #152 documents the source timestamp evidence gap; PR #153 refreshed continuity. Both required and post-merge CI passed. PR #154 keeps report data disconnected and synthetic; local test suite was not run. Required PR and post-merge CI (including Django and browser E2E) passed.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and labeled dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields; #143 added typed unavailable reasons; #145 documented source-specific zero-row and freshness behavior; #147 refreshed the handoff.
- PR #150 adds `freshness_unknown` as a valueless report reason for a complete observation without trustworthy freshness evidence; it remains distinct from partial coverage and stale data. The underlying freshness evaluator is synthetic and no live source, adapter, or account is verified.
- The authenticated report remains disconnected and contains no observed values. Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility and production freshness thresholds remain unverified; provider-specific adapters, source verification, ingestion, and durable audit are not implemented.

## Next action

Manually inspect the authenticated report empty state at desktop and mobile widths, confirming planned period, no observed period, unknown freshness, and no horizontal overflow. Use only synthetic/local data; do not add a live adapter.
