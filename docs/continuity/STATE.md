# GrowthTwin — current handoff

Last verified: 2026-09-29 22:10 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `55cd410` after PR #148. Required CI `36615926887` and post-merge CI `36616229613` passed. No open PRs were reported at 2026-09-29 22:09 Europe/Istanbul.
- Current branch: `feat/report-freshness-evaluation`, based on `main`; source freshness evaluator, synthetic tests, ADR-0019, and status-document updates are ready for review. PR not yet opened.
- Local checks for this slice: 50 campaign Django tests passed; Django system check and migration consistency passed; Ruff lint/format and `git diff --check` passed. Browser E2E not run locally; required PR CI is pending.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; #138 established a provider-neutral typed metric contract; #140 connected typed unavailable metrics and labeled dates as the planned campaign period; #141 defined provider-neutral metric semantics; #142 mapped official Google Ads API v25 fields; #143 added typed unavailable reasons; #145 documented source-specific zero-row and freshness behavior; #147 refreshed the handoff.
- Current feature adds source- and metric-family-bound `MetricFreshnessRule` and a pure evaluator using source data time, evaluation time, and an explicit positive maximum age. Missing/future source timestamps yield `unknown`; exact-threshold age is `current`; older age is `stale`. Retrieval time is not used to classify freshness. Synthetic examples are application policy only, not a provider SLO or guarantee. No live source, adapter, or account is verified.
- The authenticated report remains disconnected and contains no observed values. Search mapping leaves reach unavailable; text-ad interactions are not added again to clicks; attributed conversions do not prove delivered leads.
- Keep the Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Google Ads API access/eligibility and production freshness thresholds remain unverified; provider-specific adapters, source verification, ingestion, and durable audit are not implemented.

## Next action

Open a PR for the synthetic freshness evaluator and updated reporting contract, review its diff, then merge only after required CI succeeds. Keep production thresholds unselected until reviewed against current source guidance; do not add a live adapter.
