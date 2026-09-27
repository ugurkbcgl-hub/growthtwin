# ADR-0005: Türkiye-first advertising platform for all advertiser types

- Status: Accepted
- Date: 2026-09-27
- Decision owner: Project owner

## Context

The initial project material used dental clinics as the first product audience and focused on Instagram content. The owner has clarified that Türkiye is the target market and the product should serve anyone who wants to advertise. Dental clinics are an example customer, not a product boundary. The owner also selected Omneky as a capability benchmark for a complete advertising workflow.

The current local prototype is a synthetic brief, preview, simulated pause, and sample-report experience. It does not connect an advertiser account, generate real assets, publish an ad, spend money, or report live metrics. No destination platform or production AI provider has been selected.

## Decision drivers

- Serve the Türkiye market without making the product clinic-specific or tied to one industry or business size.
- Reduce advertiser effort from describing a goal through producing, launching, and measuring a campaign.
- Use brand-consistent multi-format ad generation, connected campaign launch, unified performance insights, and bounded optimization as the long-term capability target.
- Validate a narrow workflow and destination before committing to broad channel coverage.
- Preserve explicit advertiser authorization, spend limits, traceable actions, and safe stopping behavior.

## Options considered

1. Keep the product clinic-only and centered on organic Instagram content. This follows the original project document but conflicts with the owner's clarified market and advertising-platform goal.
2. Serve all Türkiye advertisers with an Omneky-inspired, self-service advertising platform, built in validated stages. This matches the clarified product goal while keeping the first release bounded.
3. Attempt feature and channel parity with Omneky in the first release. This would assume API access, market availability, cost, and user needs before they have been validated.

## Decision

Adopt option 2.

GrowthTwin targets people and organizations in Türkiye that want to advertise. Individuals, creators, small businesses, larger businesses, and clinics are examples; the product model must not hard-code one segment.

The long-term capability benchmark is an integrated workflow that learns the advertiser's brand and offer, builds a campaign plan from a plain-language goal, generates platform-ready copy/image/video creatives and variants, launches campaigns through authorized ad accounts, reports performance across channels, and recommends or performs bounded improvements.

Omneky is a reference for this capability breadth, not a promise to copy every feature or support every channel. Current public Omneky product pages are claims from the vendor, not proof of GrowthTwin API eligibility, platform availability in Türkiye, or technical parity. Relevant public references checked on 2026-09-27: [Omneky](https://www.omneky.com/) and [Campaign Launcher](https://www.omneky.com/campaign-launcher).

The first release must validate one advertiser workflow and one destination before adding broad multi-channel support. The first campaign type and platform remain open pending user discovery and Türkiye-specific API, policy, and reporting research.

Routine campaigns should not require a GrowthTwin employee. Advertisers must explicitly authorize account access and set enforceable spend, schedule, and content boundaries. The product may automate within those permissions; it pauses and explains when information, authorization, policy confidence, platform access, or a configured limit is missing or uncertain. The default per-campaign review mode remains open for product validation.

This decision does not authorize live publishing, advertiser spend, production AI use, a new provider, or additional paid infrastructure. Continue local work with synthetic data and the existing stack.

## Consequences

- `PROJECT.md` and `ROADMAP.md` describe a Türkiye-wide advertiser market and Omneky-inspired long-term capability scope.
- Clinics remain a possible pilot cohort rather than the defining product segment.
- The MVP must remain narrower than the capability benchmark; first campaign type, first destination, and approval defaults need evidence and review.
- Platform integrations must be selected only after checking access and policy requirements in Türkiye.
- Reporting and optimization require measurable, authorized inputs; AI cannot bypass deterministic account, spend, and action controls.
- Existing Django/PostgreSQL and local synthetic-data development decisions remain unchanged.

## Follow-up

- Validate a first campaign workflow with prospective advertisers from more than one category in Türkiye.
- Compare candidate ad networks' Turkish account/API eligibility, app approval, campaign formats, reporting, and maintenance costs.
- Decide the initial user review/autonomy controls before any live account integration.
- Stage Omneky-inspired features in the roadmap: multi-format creatives, channel launch, unified insights, and guarded optimization.
- Evaluate AI output on representative synthetic briefs before selecting a production provider.
