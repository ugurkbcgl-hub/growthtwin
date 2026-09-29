# GrowthTwin — current handoff

Last verified: 2026-09-29 23:45 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`.

## Verified repository state

- `origin/main` is `11aecd3` after PR #157 (`docs/report-visual-review-completion`), merged at 2026-09-29 20:43 UTC. Its required CI `36628090078` passed. Post-merge CI `36628363795` is in progress as of 2026-09-29 20:45 UTC. Current local branch: `research/google-ads-search-turkiye`, created from that main commit.
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

Review and submit the official-source Google Ads Search feasibility note for Türkiye, then begin the next roadmap slice on Türkiye advertising, consumer, privacy, and sector policy requirements. Keep the work research-only; no real account, advertiser data, lead flow, or campaign action. The two earlier synthetic drafts remain stored under an active server-side session but are not visible in the current browser session; do not expose or copy session-cookie values, and do not claim the drafts are restored.
