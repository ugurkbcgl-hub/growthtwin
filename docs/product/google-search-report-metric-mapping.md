# Google Ads Search reporting metric mapping (research only)

**Verified:** 2026-09-29 (Europe/Istanbul), against Google Ads API v25 official documentation.
**Scope:** map the currently selected synthetic Search workflow to possible source fields. This is a documentation exercise, not confirmation of GrowthTwin API access, account eligibility, or permission to connect an account.

## Candidate mapping

| GrowthTwin report category | Google Ads API v25 candidate | Search workflow disposition | Important limitation |
| --- | --- | --- | --- |
| Reach | `metrics.unique_users` | **Unavailable for the first Search slice.** | Google's field reference lists unique users for Display, Video, Discovery, and App campaigns, not Search. It also says the metric cannot be aggregated and only supports ranges up to 92 days. Never derive reach from impressions. |
| Impressions | `metrics.impressions` | Candidate source field | Google defines this as how often the ad appeared on a search results page or a Google Network website. Keep it distinct from unique people. |
| Clicks | `metrics.clicks` | Candidate source field | Treat as provider-reported ad clicks. It does not establish a website session, contact request, or qualified lead. Review available click types before presenting a more specific label. |
| Other interactions | `metrics.interactions`, `metrics.interaction_event_types` | **No separate “other interactions” total for Search by default.** | Google defines an interaction as the main action for an ad format; clicks are the action for text ads. Showing both clicks and interactions as separate Search totals could double-count. Preserve event types if a later format has distinct interactions. |
| Contact requests | `metrics.conversions` / `metrics.all_conversions` are attributed conversion candidates | **Unavailable as delivered contact requests without independent delivery evidence.** | Conversion actions are configured by the account. An attributed conversion is not proof that GrowthTwin or the advertiser received a lead record, nor that it was qualified. Keep “conversion” separate from “contact request” unless a delivery record and deduplication rule exist. |
| Media spend | `metrics.cost_micros` with `customer.currency_code` | Candidate source field | Treat as provider-reported campaign media cost in the ad account's currency. Convert micros exactly; keep separate from budget, GrowthTwin fees, tax, and FX. Never combine different currencies without a disclosed, evidenced conversion. |

## Period, attribution, and missing data

- Read the reporting timezone from `customer.time_zone`. Google describes it as the customer's local timezone ID. Do not replace it with the browser's timezone. The report's planned campaign period remains distinct from an observed reporting period.
- Google Ads conversion reporting can be delayed. Its reporting guide states that conversion data is not available instantly and reports may omit rows when all selected metrics are zero. Therefore, an absent row is not evidence of a zero. A future adapter needs source-confirmed completeness before it may record a real zero.
- Preserve conversion-action identity and the account's attribution settings/window with any conversion result. Do not silently equate different actions, models, or windows, or call a conversion a delivered contact request.
- These docs do not establish a universal freshness threshold. Verify source-specific update behavior before setting one. Missing, partial, delayed, unsupported, and stale data must not be rendered as zero.

## Findings for the first Search report

1. Impressions, clicks, and media cost have plausible campaign-level source fields, subject to API field compatibility and account access.
2. Reach is not currently supported for Search by the documented `unique_users` campaign-type restrictions.
3. `interactions` is not an independent “other interactions” count for text Search ads; don't show it alongside clicks as if it were additive.
4. Conversion metrics need an explicit, reviewed conversion action and attribution metadata. They do not independently verify lead delivery or lead quality.
5. Keep unsupported and not-yet-connected categories distinguishable in the product's future status model. The current two-state metric contract does not yet encode all reasons a value is unavailable.

No API request or account access was made. No customer data, credentials, campaign performance, or forecast was used. This mapping does not verify API developer-token level, production approval, Türkiye account eligibility, or account consent. Recheck the versioned official field references before implementing an adapter.

## Official sources

- [Google Ads API v25 metrics fields](https://developers.google.com/google-ads/api/fields/v25/metrics) — field availability and resource compatibility, including `unique_users`, `interactions`, and campaign metrics.
- [Google Ads API v25 campaign fields](https://developers.google.com/google-ads/api/fields/v25/campaign) — campaign-level selectable fields and metrics.
- [Google Ads API v25 customer fields](https://developers.google.com/google-ads/api/fields/v25/customer) — account currency and timezone attributes.
- [Google Ads API conversion reporting](https://developers.google.com/google-ads/api/docs/conversions/reporting) — conversion-action reporting, delayed data, and zero-only rows.
- [Google Ads API conversion setup](https://developers.google.com/google-ads/api/docs/conversions/getting-started) — conversion tracking prerequisites and action-specific configuration.
- [Google Ads API v25 Metrics reference](https://developers.google.com/google-ads/api/reference/rpc/v25/Metrics) — canonical v25 metric descriptions and restrictions.
