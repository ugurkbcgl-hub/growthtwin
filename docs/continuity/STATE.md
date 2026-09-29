# GrowthTwin — current handoff

Last verified: 2026-09-29 22:30 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `c059c1e` after PR #151. PR #149 required/post-merge CI `36617325319`/`36617630617` passed. PR #150 required/post-merge CI `36618254042`/`36618532218` passed. PR #151 required CI `36619100149` and post-merge CI `36619387519` passed at 2026-09-29 22:30 Europe/Istanbul.
- Current branch: `docs/report-source-freshness-evidence`, based on merged `main`; updates the Google Search evidence mapping and records the cautious timestamp finding. PR not yet opened.
- PR #151 changed documentation only; `git diff --check` and required PR CI passed. PR #150 local validation and required/post-merge CI passed.

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

Finish and review the source freshness evidence note, open its documentation PR, and wait for required CI. Preserve the evidence-gap qualification and do not add a live adapter or treat an SLO as a guarantee.
