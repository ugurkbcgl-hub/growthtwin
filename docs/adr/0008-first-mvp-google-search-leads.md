# ADR-0008: First synthetic campaign workflow and channel candidate

- Status: Accepted for local synthetic product development only
- Date: 2026-09-29
- Decision owner: Project owner (delegated implementation decisions)

## Context

GrowthTwin is intended for all Türkiye advertisers, but the first usable flow
must be narrow enough to validate end to end. The current product is an
anonymous session prototype; a single-user-owned `Workspace` model exists but
campaign data is not connected to it. Real advertiser, lead, payment and
platform data remain blocked by [ADR-0007](0007-workspace-ownership-and-retention.md)
and the product blueprint readiness gate.

Official Google Ads documentation currently describes Search campaign creation,
location targeting, keyword forecast metrics and finite campaign total budgets.
The API requires a developer token and OAuth; production-account access needs
an approved access level. Test accounts cannot serve ads and have no live serving
metrics. Google average daily budgets can spend up to twice the average amount
on a day, so a daily average must not be presented as a strict daily ceiling.
Meta is a strong later creative/reach candidate, but using Marketing API for
other advertisers' accounts and retrieving form leads depends on additional
access and permissions. TikTok is a later short-video/creative-testing
candidate; GrowthTwin-specific API and lead-delivery eligibility have not been
verified for Türkiye.

## Decision

1. **First synthetic scenario:** a non-regulated, city-based service provider
   seeks quote/contact requests. Use a synthetic Ankara home-maintenance
   business in examples. The wider product remains sector-neutral and open to
   all advertiser types.
2. **First channel candidate:** Google Ads Search, with the advertiser's own
   website as the destination. The first local slice prepares a campaign plan
   and editable search-ad text/keyword groups. It does not connect a Google
   account or call a production API.
3. **Lead boundary:** the first slice does not collect raw lead details or
   deliver them to a CRM, email, SMS or webhook. The advertiser's website owns
   the lead interaction. GrowthTwin may show aggregate conversion counts only
   when a valid conversion action and authorized platform report provide them;
   otherwise it must state that leads cannot be calculated.
4. **Forecast boundary:** use Google Keyword Planner forecasts only after
   the applicable API access and account conditions are verified. Show
   impressions, clicks and cost with source, retrieval time, location,
   language, date range, keywords and assumptions. Do not invent an expected
   conversion rate or combine unique reach across channels.
5. **Budget boundary:** model a user-selected finite total media cap and flight
   dates separately from GrowthTwin fees/credits. A future Google Search
   campaign may use a campaign total budget only after validating platform and
   account eligibility and that no concurrent campaigns or account-level spend
   undermine the user's aggregate ceiling. A synthetic draft cannot authorize
   an external action.
6. **Channel sequence:** Google Search is the first technical candidate; Meta
   is second; TikTok follows if creative testing/short video remains a leading
   product advantage. This ranks research and prototype effort; it does not
   assert API approval or integrations.
7. **Deferred from this first technical slice:** upload/analysis of customer
   files, AI provider calls, image/video generation, payment/credits,
   performance guarantees, direct lead capture, automatic publication and
   automatic budget increases. They require separate contracts and evidence.
8. **User experience:** prepare and explain a complete campaign draft; any
   eventual live publication requires explicit account authorization and
   confirmation, hard enforceable campaign and aggregate caps, stop/revoke,
   platform-policy checks and the separate readiness gate. No staff operator is
   required for routine flow once those safeguards and approvals exist.

## Consequences

- The initial domain can support a sector-neutral objective and brand brief,
  while the first sample uses a local service lead scenario.
- First implementation should persist a synthetic campaign draft under its
  owning workspace through an owner-scoped application service. Keep
  `site.CampaignDraft` and all existing anonymous drafts untouched; never
  auto-backfill them.
- No GrowthTwin-specific Google, Meta or TikTok API access was checked using
  private credentials or an advertiser account. Test access and production
  approval remain to be requested/verified when authorized.
- Forecast, click, conversion and budget statements in the prototype must be
  clearly labeled `synthetic`, `estimate`, `observed`, or `unavailable` as
  applicable. Do not use synthetic data as market demand evidence.
- The selection does not establish user demand, final launch cohort, legal
  approval, final pricing, provider selection, or eligibility of regulated
  sectors.

## Evidence

- [Google Search campaigns](https://developers.google.com/google-ads/api/docs/campaigns/search-campaigns/getting-started)
- [Google Ads location targeting](https://developers.google.com/google-ads/api/docs/targeting/location-targeting)
- [Google Keyword Planner forecast metrics](https://developers.google.com/google-ads/api/docs/keyword-planning/generate-forecast-metrics)
- [Google Ads campaign total budgets](https://developers.google.com/google-ads/api/docs/campaigns/budgets/overview)
- [Google Ads API access levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels)
- [Google Ads test accounts](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts)
- [Google Ads average daily budget and overdelivery](https://support.google.com/google-ads/answer/1704424?hl=en)
- [Meta Marketing API official collection](https://www.postman.com/meta/facebook-marketing-api/documentation/0zr4mes/facebook-marketing-api-mapi)
- [Meta permissions reference](https://developers.facebook.com/docs/permissions/reference/)
