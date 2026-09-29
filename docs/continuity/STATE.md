# GrowthTwin — current handoff

Last verified: 2026-09-29 19:33 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is at `c9f5823e1a06bff260adba17d5d8bfce1de7a7b0` after PR #138 merged. Its required CI run `36598277954` passed. Post-merge CI `36598564211` was in progress at last check.
- PR #138 is merged. No other open PR was listed before it was created. Local campaign metric-contract tests (6), all campaign tests (37), Django system check, migration check, Ruff lint/format, and diff whitespace check passed. CI also passed migration, Django test, and browser E2E stages.
- Checkout is `main`, fast-forwarded to the merge commit. No unrelated working changes were present before the continuity update.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added an authenticated report shell with six unavailable metric categories and explicit source/update state. PR #138 adds an immutable, provider-neutral metric contract with explicit available/unavailable status, reporting window, unit/currency, source, and timezone-aware observation time. An available zero is valid; unavailable metrics cannot carry a numeric value. This contract is not yet connected to the report UI or any storage/provider.
- The authenticated workspace uses synthetic campaign examples. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Do not invent report values or forecasts.
- Keep Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Report metric semantics, attribution, trusted source provenance, freshness thresholds, ingestion, and durable audit must be specified before real reporting.

## Next action

Connect `CampaignReportMetric` to the authenticated report shell with typed unavailable values and current no-source explanatory copy. Keep it persistence-free and provider-free, show no synthetic result numbers in the authenticated report, and add focused unit/view coverage.
