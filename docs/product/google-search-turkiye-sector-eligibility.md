# Google Search Türkiye sector eligibility matrix

**Reviewed:** 2026-09-30 (Europe/Istanbul)
**Channel:** Google Ads Search; this is not a cross-channel decision.  
**Purpose:** product-planning and synthetic prototype gate. This is not legal advice, legal clearance, an account/API approval, or permission to publish.

## Decision language

The product must evaluate the advertiser's sector, advertised product/service, destination, target location, evidence, and the current channel rule together. The output is one of:

| State | Product behavior |
|---|---|
| `eligible` | All required facts and evidence are present and the current rule permits this specific campaign. This is still not platform account authorization or a publish command. |
| `restricted` | A documented rule permits a narrower format, product, audience, geography, or verified advertiser. Enforce every condition before allowing the workflow to proceed. |
| `not_supported` | The selected product/channel/location combination is disallowed or outside an approved list. Stop campaign preparation for that combination and explain why. |
| `needs_review` | The category or evidence is unassessed, ambiguous, stale, or missing. Pause; do not infer permission from a broad sector label. |

Missing category, product, destination, target geography, or required proof always resolves to `needs_review`. A channel permission does not establish Turkish legal permission; legal permission does not establish Google acceptance; neither establishes GrowthTwin's API access or account authority.

## Initial matrix

| Sector or offer | Google Search / Türkiye finding checked 2026-09-29 | Initial product state | Required product behavior |
|---|---|---|---|
| City-based home-maintenance quote/contact service (ADR-0008 example) | No sector-specific Google certification requirement was identified in this initial review. General ad, destination, account and local-law requirements still apply. Certain trades may have their own authorization rules; the sample is not blanket approval for every repair service. | `eligible` for synthetic local planning only; `needs_review` before any live campaign | Keep current fixtures fictional. For live use, identify the exact service and advertiser, verify any trade authorization and claim evidence, inspect the landing page and account permissions, and re-check current platform policy. |
| Financial services, including credit, banking, insurance and investment | Google requires Türkiye-targeted financial-services advertisers to complete Google verification and demonstrate relevant Turkish regulator licensing or exemption. The verification rule also covers some categories that may not be regulated and non-financial advertisers targeting audiences seeking financial services. Approved third parties require an authorized advertiser to verify/vouch for domains and Ads account IDs. | `restricted` only after exact Google verification and evidence; otherwise `needs_review` | Do not prepare a liveable campaign until advertiser class, license/exemption and Google verification are evidenced. Treat financial-intent audience targeting as a trigger too. GrowthTwin's own multi-tenant/API eligibility remains unverified. |
| Online gambling | Google's Türkiye row lists online lotteries and sports betting, with the operator required to be a state-licensed entity. Google certification is also required. This is Google's policy description, not a complete opinion on Turkish gambling law. | `restricted` for the exact listed product/operator only; all other offers `not_supported` or `needs_review` | Exclude from the first release. Even an apparently listed offer stays stopped until qualified legal review, state-license evidence and Google certification are verified for that advertiser/account. |
| Offline gambling promotion | Google's policy says offline gambling promotion is not supported in locations where advertising it is illegal and lists Turkey among unsupported locations. | `not_supported` | Stop the campaign on this channel/location. Do not route around the policy with different copy or a different campaign label. |
| Alcohol brand/information advertising and online alcohol sale | Google's current approved-location lists for both alcohol information/branding and online sales do not include Türkiye; ads targeting locations outside each list are disapproved. | `not_supported` for Google Ads targeting Türkiye | Stop the campaign for Türkiye. This is a platform-specific result and does not purport to summarize Turkish alcohol law. |
| Healthcare providers/facilities and health-service promotion | Türkiye's 2025 Health Services Promotion and Information Regulation prohibits explicit and implicit advertising in health-service provision and restricts permitted information; it also bars sponsored/featured search-engine and social-platform listings. Google's separate health/medicine rules may require category-specific certification for certain products/services. | `not_supported` for promotional paid Search in the first release; `needs_review` for any narrowly informational proposal | Do not treat a Google certificate as overriding Turkish rules. Keep healthcare outside the first paid campaign workflow unless qualified Turkish counsel assesses the exact content, advertiser and format. |
| Medicines, medical devices, supplements and other health products | Not fully researched at product and subcategory level in this matrix. Google's healthcare/medicines policy applies location-specific restrictions and some categories need an application/certificate. Turkish rules vary by product and claim. | `needs_review` (fail closed) | No preparation for live publication until the exact product, claims, advertiser authorization, destination and both legal/platform rules are reviewed. |
| Tobacco, nicotine and vaping products; accessories or services facilitating consumption | Google disallows ads for tobacco-containing products, products that are part of tobacco products, services facilitating/promoting consumption (examples include hookah lounges), and products designed to simulate tobacco smoking (including e-cigarettes). This is a global Google Ads policy rule, independent of Turkish-law status. | `not_supported` for the covered offers on Google Search | Stop covered offers. Classify the advertised product/service and landing page, not only the advertiser's broad sector; separately review adjacent products that may fall outside these examples. |
| Cryptocurrency offers prohibited everywhere by Google | Google globally disallows promotion of ICOs, DeFi trading protocols, cryptocurrency buying/selling/trading and related products, unhosted software wallets, unregulated dApps, crypto trading signals/advice aggregators, among other listed examples. | `not_supported` for the prohibited offer | Stop these exact offers regardless of target country; do not relabel them as generic blockchain services. |
| Crypto exchanges, software wallets, hardware wallets and coin trusts subject to Google certification | These products require Google approval and can only target countries in the policy's approved-location list. The current list reviewed on 2026-09-30 does not include Türkiye/Turkey; Google says non-approved markets cannot advertise these products. | `not_supported` for Türkiye under the current reviewed list | Stop these offers for Türkiye. Recheck the live country list before any future policy update; Turkish licensing review is separate and cannot override Google's location list. |
| Other blockchain/crypto-adjacent services not dealing in buying, holding or exchanging cryptocurrency | Google says businesses outside buying, holding or exchanging crypto may advertise without the crypto-specific application if local law, industry standards and other Google policies are met. Examples include crypto-accepting businesses, mining hardware, qualifying tax/legal/security services and educational materials without investment advice. | `needs_review` for Türkiye | Do not treat the broad word “crypto” as sufficient for a stop or approval. Identify the exact offer and destination, then complete Turkish-law and other policy review. |
| Political and election-related advertising | Google requires compliance with applicable campaign/election laws and silence periods, with different region-specific restrictions and verification. The current political-content policy page reviewed on 2026-09-30 contains no Türkiye/Turkey-specific section; absence is not proof of permission. Political affiliation/content are sensitive categories for personalized-ad targeting. | `needs_review` | Keep paused until Turkish election-law and applicable Google requirements are assessed for the exact advertiser, message, dates, targeting and destination. Do not infer a Turkey-specific Google verification process from other countries' sections. |
| Housing and employment advertising | Google's personalized-ad policy labels its special “access to opportunities” targeting limits for housing and employment as US/Canada-only. That geographic scope does not establish Turkish legal permission or remove other Google restrictions. | `needs_review` | Do not apply the US/Canada-only demographic/ZIP restrictions as if they were Türkiye rules; also do not infer Turkish eligibility. Research Turkish law and the exact service, claims, audience and destination. |
| Adult services, food/supplements and other regulated/restricted offers | Not exhaustively researched at product and subcategory level. Google maintains separate category rules and Turkish requirements may depend on product, claim, advertiser and audience. | `needs_review` (fail closed) | Never infer eligibility from the absence of a row. Add a dated, sourced category assessment before enabling each workflow. |

“Eligible” in this first matrix is intentionally narrow: it only supports the fictional ADR-0008 local-service scenario in the local synthetic prototype. It does not mean a real advertiser may launch today.

## Fail-closed evaluation sequence

1. Identify what is actually promoted (including landing-page content), the advertiser's legal/business type, target location, campaign objective, and audience. If any are absent, return `needs_review`.
2. Match the offer to the most specific sector/product category, not just a broad business label. If no reviewed rule matches, return `needs_review`.
3. Evaluate current Turkish law and Google Ads policy independently. If either source is missing, expired, contradictory, or uncertain, return `needs_review` and pause.
4. Check all evidence required by the matching rule (license, exemption, platform certificate, authorized first party, age/location restrictions, claim substantiation and destination requirements). Missing/expired evidence means `needs_review` or `not_supported`, as specified by the rule.
5. Apply the narrowest result across all matched rules: any `not_supported` stops; a restricted result enforces its conditions; otherwise unresolved evidence pauses. Keep reasons and source/rule versions user-visible and auditable.
6. Re-evaluate before any future external action. Eligibility does not grant OAuth scope, API access, a connected account, a budget, or authorization to publish.

## Product/API implications

- Store dated rule records with jurisdiction, channel, category, product/subcategory, status, source URL, effective/review date, conditions, and a human-readable reason.
- Store an evaluation snapshot on a synthetic campaign draft so later policy updates do not silently rewrite an earlier decision. On a new rule version, invalidate or re-evaluate affected drafts.
- Keep category selection and evidence review deterministic. A language model may help extract candidate facts, but cannot override a stop, invent evidence, or turn an unknown state into eligible.
- Fail closed on stale policy records. This research should be rechecked before any real account, real advertiser data, or campaign is introduced.
- This matrix covers Google Search only. It does not assess Google Display/YouTube, Meta, TikTok, X, LinkedIn, messaging, or organic content.

## Official sources checked

- [Google Ads Financial Services Verification — Türkiye](https://support.google.com/adspolicy/answer/15332527?co=GENIE.CountryCode%3DTR&hl=en)
- [Google Ads Gambling and games policy](https://support.google.com/adspolicy/answer/15132179?hl=en)
- [Google Ads Alcohol information policy and approved locations](https://support.google.com/adspolicy/answer/16427711)
- [Google Ads Alcohol sale policy and approved locations](https://support.google.com/adspolicy/answer/16428720)
- [Google Ads applications for healthcare and other restricted industries](https://support.google.com/adspolicy/answer/16114090?hl=en)
- [Google Ads Cryptocurrencies and related products](https://support.google.com/adspolicy/answer/14009787?hl=en-GB)
- [Google Ads Tobacco policy](https://support.google.com/adspolicy/answer/16489929?hl=en-GB)
- [Google Ads Political content policy](https://support.google.com/adspolicy/answer/6014595?hl=en)
- [Google Ads restricted targeting in personalized advertising](https://support.google.com/adspolicy/answer/143465?hl=en)
- [Google Ads transparency — Türkiye](https://support.google.com/adspolicy/answer/13733850?co=GENIE.CountryCode%3DTR&hl=en)
- [Google Ads policies index](https://support.google.com/adspolicy/answer/6008942?hl=en)
- [Türkiye Official Gazette: Health Services Promotion and Information Regulation (12 November 2025)](https://www.resmigazete.gov.tr/eskiler/2025/11/20251112-2.htm)
- [Ministry of Health: publication notice for the 2025 health-services regulation](https://shgmdenetimdb.saglik.gov.tr/TR-111587/saglik-hizmetlerinde-tanitim-ve-bilgilendirme-faaliyetleri-hakkinda-yonetmelik-yayimlanmistir.html)
- [GrowthTwin ADR-0008: first synthetic Google Search workflow](../adr/0008-first-mvp-google-search-leads.md)
- [GrowthTwin Türkiye advertising/privacy readiness map](turkiye-advertising-privacy-readiness.md)

Google Ads policy help says its English version is the policy-enforcement language. The official pages can change; the review date above is part of the finding, not a guarantee that it remains current. This 2026-09-30 update is a Google-policy pass only; it did not complete Turkish statutory research for tobacco, crypto, political advertising, housing, employment, adult services or food/supplements. Those legal questions remain `needs_review` wherever the platform's global rule does not already stop the offer.
