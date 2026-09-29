# GrowthTwin — current handoff

Last verified: 2026-09-29 23:35 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `f055225` after PR #155. PR #155 merged at 2026-09-29 20:03 UTC; its required Django system check `36623355195` and post-merge CI `36623646892` passed. PR #156 (`docs/report-visual-review-status`) has passed required CI `36626690808`; recheck its merge state before acting. Latest verified local branch is `docs/report-visual-review-status`.
- PR #154 required CI `36622723566` and post-merge CI `36622985685` passed. PR #155 refreshed continuity after #154. The authenticated report remains disconnected and synthetic; no local tests were run during manual visual inspection.
- Manual visual review is complete using a narrow ~596 px view and a ~1265 px desktop view on an isolated `localhost` fixture. Planned dates, no observed period, unknown freshness, and all six unavailable metrics were legible at both sizes; no horizontal overflow was visible. On desktop the metric cards form three columns; on the narrow view the summary stacks and cards adapt to available width. No product code changed.
- The earlier browser session showed two synthetic drafts. Their active server-side session and two associated records remain in the local PostgreSQL database, but the browser's current session no longer lists them after the isolated review login changed the `127.0.0.1` session cookie. No project-database draft deletion was performed. Do not expose or manually copy session-cookie values; determine whether there is a supported, safe recovery path before claiming the drafts are accessible again.

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

Research Google Ads Search's current Türkiye suitability and SaaS/API access requirements from official primary sources; record verified account/API approval constraints, reporting coverage, and unresolved evidence gaps. Keep the work research-only: no account connection, live adapter, advertiser data, or campaign action. The two earlier synthetic drafts remain stored under an active server-side session but are not visible in the current browser session; do not expose or copy session-cookie values, and do not claim the drafts are restored.
