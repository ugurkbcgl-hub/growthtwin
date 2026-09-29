# GrowthTwin — current handoff

Last verified: 2026-09-29 19:42 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` baseline is `9bce329eff5943658adbda566ffa95480b54970d` after PR #139 merged. PR #139 required CI `36598732604` and post-merge CI `36598998445` passed. PR #138 and its post-merge CI also passed.
- PR #140, `feat/report-metric-ui-contract`, is open. Required CI `36599563170` was in progress at last check. Local branch includes report UI integration and this handoff update.
- For PR #140, 38 campaign tests and 3 authenticated browser E2E tests passed with local SQLite test settings. Django system and migration checks, Ruff lint/format, and whitespace checks passed. The browser flow verifies unavailable metrics, six reporting periods when configured, and no mobile horizontal overflow.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added an authenticated report shell; PR #138 added an immutable, provider-neutral metric contract. PR #140 connects six typed unavailable metrics to the shell and shows a configured campaign reporting window. The UI still has no verified source, observed timestamp, or numeric result. Missing flight dates do not generate an invented reporting period.
- The authenticated workspace uses synthetic campaign examples. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Do not invent report values or forecasts.
- Keep Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Report category definitions, attribution, trusted source provenance, freshness thresholds, ingestion, and durable audit must be specified before real reporting.

## Next action

After verifying PR #140's CI and merge state, define provider-neutral meanings for the six report categories, including attribution boundaries, reporting windows, and unknown/stale-data handling. Keep examples synthetic and do not connect a platform.
