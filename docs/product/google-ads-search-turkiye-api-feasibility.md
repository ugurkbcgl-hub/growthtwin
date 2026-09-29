# Google Ads Search in Türkiye: API feasibility

**Reviewed:** 2026-09-29 (Europe/Istanbul)  
**Scope:** official-source desk research for the synthetic Google Search campaign candidate. This is not legal advice, an account eligibility decision, API approval, a forecast, or authorization to connect or publish.

## Assessment

Google Ads Search is a reasonable **first technical channel candidate** for a Türkiye-focused prototype. Google's current location-targeting guide supports country, region, city, and proximity criteria, and its country-code list maps Turkey to `TR`. The current country-restrictions help page lists several embargoed territories and does not list Türkiye. Those facts support technical targeting and indicate no listed country restriction in that particular policy; they do **not** prove that every Turkish advertiser/account can sign up, pay, or serve every category of ad, nor that GrowthTwin is approved to use the API.

**Production status: unverified and blocked.** GrowthTwin has no verified developer token, access level, permissible-use approval, external-client approval, advertiser OAuth/account flow, or tested customer-account entitlement. No live account or API request was used for this assessment.

## Findings

### Türkiye targeting and advertiser billing

- Google Ads API supports country, region, city, and proximity targeting. `GeoTargetConstantService.SuggestGeoTargetConstants` can look up current target criteria; the country-code reference identifies Turkey as `TR`. Resolve IDs dynamically from Google's source at implementation time and check target status instead of hard-coding stale IDs.
- The current country-restrictions page lists Crimea, Cuba, DNR, Iran, LNR, and North Korea. Türkiye is not listed there. This only addresses that specific restriction list; it is not a full country-onboarding, advertiser eligibility, sector policy, or legal clearance.
- Google says available payment methods depend on the Ads account's billing country and currency. Payment settings also depend on billing address country and currency. Therefore, the existence of a payment method in one account cannot establish all Turkish users' available methods or a supported GrowthTwin billing model. The advertiser-owned Ads account should remain the direct media-billing boundary in the prototype design.

### Developer access and SaaS use

- A Google Ads API developer token is required. The documented setup involves a Google Ads manager account, a developer token, a Google Cloud project and OAuth credentials, a target customer account ID, and granting the calling identity appropriate account access. Credential format and account authorization need a security design before implementation; do not put tokens or key files in the repository.
- Google's access-level page currently describes Test, Explorer, Basic, and Standard. Test can reach only test accounts. Explorer can reach production accounts but has a 2,880-operation rolling 24-hour production limit and excludes listed planning functions such as keyword planning and reach planning. Basic supports 15,000 operations per rolling 24 hours and requires Google Cloud brand verification before application. Standard is intended for higher-volume tools and entails a detailed manual audit; Google's page says external-user tools should provide demo sign-in access. Service-specific quotas and rate limits still apply.
- Under the current access-level page, **permissible use is allocated for Standard access**. It distinguishes ad creation/management, reporting-only, and keyword research/recommendations; an application to update permissible use is required if clients will use the tool. GrowthTwin's desired campaign creation plus reporting plus planning is not evidenced as covered until Google's approval for the actual product and user model is obtained. Treat access levels and quotas as changeable; re-check before application and production use.
- Google states the API itself has no usage charge at Explorer, Basic, or Standard. This is separate from advertiser media spend and from potential non-compliance fees. Standard-access Required Minimum Functionality (RMF) review can impose fees for non-compliance, so budget exposure is not conclusively zero.

### Reports, estimates, and test-account limits

- Google Ads reporting uses GAQL through `GoogleAdsService.Search` or `SearchStream`; the reporting references describe campaign, ad group, keyword and other resource reporting. The existing [Search metric mapping](google-search-report-metric-mapping.md) remains the contract for what GrowthTwin may display: reach and a delivered contact request are not established by Search metrics; attributed conversions must not be labeled as delivered leads.
- Explorer excludes KeywordPlan and ReachPlan services. This constrains any in-product keyword ideas, reach forecasts, or planning estimates at that level. The reviewed sources do not validate a Turkish-market forecast, model its accuracy, or promise a reliable number of people reached before purchase. Treat pre-purchase estimates as unavailable until the precise current endpoint, access level, inputs, geographic coverage, and terms are verified.
- Test accounts do not serve ads, have no billing, cannot interact with production accounts, and return no serving metrics such as impressions, conversions, or cost. They are suitable for request/configuration behavior, not verifying live delivery, spend, conversion performance, or reporting freshness. A later integration plan needs a separate gate for safe production-account validation; this research does not authorize that gate.

## Recommendation and gates

Keep Google Search as the **synthetic prototype's first channel candidate**, not a production commitment. Continue with local synthetic fixtures and the existing provider-neutral report contract. Before any real connection or live adapter:

1. Obtain and record GrowthTwin's own Google Ads developer-token access level and approved use, including explicit permission for external clients and the intended campaign-management/reporting/planning functions.
2. Verify the supported advertiser authorization flow, least-privilege access, token storage/revocation, manager-account relationship, and independent account ownership with Google's current OAuth/API guidance.
3. Verify a Turkish advertiser account's country/currency/payment onboarding and current product/sector eligibility from current account-specific Google sources; do not infer this from the country-restrictions list or an expired terms table.
4. Map each forecast/plan estimate to an actually approved API feature, disclose uncertainty and unavailable values, and keep it separate from delivery guarantees.
5. Complete separate Türkiye legal/policy research (including advertising, consumer, personal-data, and sector-specific obligations) with qualified review before real data, lead handling, or campaigns.

This document closes only the initial technical-candidate desk research. It does not close any production-readiness, legal, privacy, account, or commercial gate.

## Official sources checked on 2026-09-29

- [Google Ads API: access levels and permissible use](https://developers.google.com/google-ads/api/docs/api-policy/access-levels)
- [Google Ads API: access levels and Required Minimum Functionality](https://developers.google.com/google-ads/api/docs/productionize/access-levels)
- [Google Ads API: developer token](https://developers.google.com/google-ads/api/docs/api-policy/developer-token)
- [Google Ads API: quick start](https://developers.google.com/google-ads/api/docs/get-started/make-first-call)
- [Google Ads API: location targeting](https://developers.google.com/google-ads/api/docs/targeting/location-targeting)
- [Google Ads API: country codes](https://developers.google.com/google-ads/api/data/codes-formats)
- [Google Ads Help: country restrictions](https://support.google.com/google-ads/answer/6163740?hl=en)
- [Google Ads Help: payment methods](https://support.google.com/google-ads/answer/2393032?hl=tr)
- [Google Ads API: reporting overview](https://developers.google.com/google-ads/api/docs/reporting/overview)
- [Google Ads API: conversion reporting](https://developers.google.com/google-ads/api/docs/conversions/reporting)
- [Google Ads API: test accounts](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts)
