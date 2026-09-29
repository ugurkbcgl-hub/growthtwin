# GrowthTwin — current handoff

Last verified: 2026-09-29 23:27 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `main` is `f055225` after PR #155. PR #155 merged at 2026-09-29 20:03 UTC; its required Django system check `36623355195` and post-merge CI `36623646892` passed. No PR is currently open. Latest verified local branch is `docs/report-visual-review-status`; this handoff correction is in progress and its PR/CI state must be checked again.
- PR #154 required CI `36622723566` and post-merge CI `36622985685` passed. PR #155 refreshed continuity after #154. The authenticated report remains disconnected and synthetic; no local tests were run for the manual visual review.
- Manual visual review was completed only at the available narrow browser width (about 596 px). Planned dates, no observed period, unknown freshness, and all six unavailable metrics were legible; no horizontal overflow was visible. The browser interface did not expose a viewport resize control, so desktop-width visual review remains incomplete. CSS source review confirmed a single-column report summary below 650 px and auto-fitting metric cards; this is not a substitute for the missing desktop screenshot.
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

First determine whether the two still-stored synthetic drafts can be restored through a supported, safe path without handling session-cookie values. Then finish visual review of the authenticated report at a true desktop viewport and a narrow mobile viewport, confirming planned period, no observed period, unknown freshness, and no horizontal overflow. Keep all data synthetic; do not add a live adapter.
