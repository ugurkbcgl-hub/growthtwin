# GrowthTwin — current handoff

Last verified: 2026-09-29 22:18 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `75b1c6c` after PR #149. Required CI `36617325319` and post-merge CI `36617630617` passed at 2026-09-29 22:15 Europe/Istanbul.
- Current branch: `feat/unknown-report-freshness`, based on merged `main`; adds the typed `freshness_unknown` reason for complete observations whose freshness is unknown. Implementation, tests, ADR, roadmap, and handoff updates are ready for PR review; PR not yet opened.
- Current-slice local validation: 50 campaign Django tests passed; Django system check and migration consistency passed; Ruff lint/format and `git diff --check` passed. Browser E2E not run locally; PR CI pending.
- PR #149 local checks: 50 campaign Django tests passed; Django system check and migration consistency passed; Ruff lint/format and `git diff --check` passed. Browser E2E was not run locally; required PR CI passed.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and labeled dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields; #143 added typed unavailable reasons; #145 documented source-specific zero-row and freshness behavior; #147 refreshed the handoff.
- Current feature adds `freshness_unknown` as a valueless report reason for a complete observation without trustworthy freshness evidence; it remains distinct from partial coverage and stale data. The underlying freshness evaluator is synthetic and no live source, adapter, or account is verified.
- The authenticated report remains disconnected and contains no observed values. Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility and production freshness thresholds remain unverified; provider-specific adapters, source verification, ingestion, and durable audit are not implemented.

## Next action

Finish the focused tests and local checks for `freshness_unknown`, open its PR, then merge only after review and required CI succeed. Keep production thresholds unselected until reviewed against current source guidance; do not add a live adapter.
