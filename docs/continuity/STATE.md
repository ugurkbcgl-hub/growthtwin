# GrowthTwin — current handoff

Last verified: 2026-09-29 19:47 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- Main baseline is `fb18fc5744b158448e7a41d24a40ff39fcc4881c` after PR #140. Required CI `36599719349` and post-merge CI `36599967255` passed.
- PR #141 is being prepared on `docs/report-metric-semantics` with ADR-0017, current-system-gap-analysis, and a small report-label correction. It has not yet been opened; verify the live Git state before assuming its PR number/status.
- PR #140's code passed 38 campaign tests and 3 authenticated browser E2E tests on local SQLite settings; Django system and migration checks, Ruff lint/format, and diff whitespace checks passed. Its browser check covers the six unavailable categories, planned-period labels, and no mobile horizontal overflow.

## Product and safety context

- GrowthTwin serves people and organizations in Türkiye who want to advertise; clinics are one example. Omneky is a long-term capability reference, not first-release scope.
- Local synthetic-data product development is authorized. Staging E2E, backup/restore, rollback, and other release-readiness gates remain before external beta or production.
- PR #135 added the authenticated report shell; PR #138 defined the provider-neutral typed metric contract; PR #140 connected six typed unavailable metrics to the report. The UI shows the **planned campaign period** only when dates exist. It remains disconnected from verified sources and has no observed values, source timestamp, platform account, or persistence.
- ADR-0017 defines provider-neutral semantics for reach, impressions, destination clicks, other interactions, delivered contact requests, media spend, reporting windows, attribution, and unavailable/stale values. It does not verify any platform mapping. Platform-specific API definitions require current primary-source research before an adapter is implemented.
- The authenticated workspace uses synthetic campaign examples. Real advertiser/customer/lead data, uploads, production AI, platform account connections, publication, advertiser spend, and payments remain out of scope. Do not invent report values or forecasts.
- Keep Django/PostgreSQL modular monolith and previously approved Heroku staging only. No additional paid service. Never push directly to `main`; successful PRs may be merged after review and required CI under the owner's standing authorization.

## Open risks

- Real-data readiness and release gates remain: secure file handling, privacy/retention, data recipients, provider terms, Türkiye-specific platform/API approvals, token protection/revocation, audit/stop behavior, backup/restore, rollback, and staging browser E2E.
- Credit costs, TRY/tax/payment pricing, ad service fees, lead delivery, performance guarantees, and production AI/provider remain undecided or unverified.
- Provider metric field mappings, source provenance, freshness/completeness thresholds, attribution settings, ingestion, and durable audit remain unimplemented.

## Next action

Research current official Google Ads reporting definitions and map available source fields to ADR-0017's metrics without accessing an account. Mark unsupported, partial, or attribution-dependent fields explicitly; do not connect or import platform data.
