# Türkiye advertising, consumer, and privacy readiness map

**Reviewed:** 2026-09-29 (Europe/Istanbul)
**Scope:** initial product-planning map from current official Turkish sources. This is not legal advice or a complete sector-by-sector compliance opinion. It identifies product gates that need qualified legal review before checkout, real data, lead handling, or campaign publication.

## Executive assessment

GrowthTwin can keep developing its local synthetic prototype. It should not yet accept real advertiser or lead data, sell credit packages to the public, promise advertising outcomes, or publish campaigns. The main gap is not one generic consent checkbox: the product needs separate controls for ad-claim evidence, user type and checkout, the purpose and ownership of personal-data processing, third-party transfers, commercial follow-up messages, and regulated-sector eligibility.

The long-term product remains open to advertisers across many sectors. A sector-neutral onboarding therefore needs a policy and eligibility check that can allow a category, apply channel-specific restrictions, stop unsupported claims, or pause for qualified review. It must not assume a clinic is an ordinary local service. The current first synthetic example is an unregulated local-service quote/contact flow and stays synthetic.

## Findings and product consequences

### 1. Advertising claims and outcome guarantees

The Ministry of Trade describes commercial ads as needing to follow the Advertising Board's principles and be honest and accurate. The Commercial Advertising and Unfair Commercial Practices Regulation puts the burden on advertisers to prove the accuracy of ad claims and requires verifiable facts to be supported by scientifically valid information and documents. Specially regulated products and services may also have additional rules.

**Product consequence:** every factual claim generated from an advertiser brief or supplied material needs source/provenance, an evidence status, and a check that the user is entitled to use it. The AI must not invent prices, awards, performance statistics, professional titles, product efficacy, scarcity, or guarantees. The advertiser must be able to review and correct claims before publication. GrowthTwin's “refund if the result misses the target” idea remains a commercial and legal decision: define the measurable outcome, attribution, exclusions, platform outages, the refund source/amount, and customer remedies, then obtain qualified review before advertising it as a guarantee.

### 2. Credit packs, fees, and online consumer purchases

The Ministry's current consumer guide describes internet purchases as potential distance contracts and says consumers must receive clear pre-contract information before payment, including service characteristics, seller/provider identity and contact details, total price including taxes, extra charges, withdrawal rights, and dispute routes. It also describes records, complaint handling, and certain platform responsibilities where an intermediary brings a seller and consumer together. The precise scope depends on the contracting parties, user status, service and checkout model.

**Product consequence:** before enabling the proposed 100/1,000-credit packages, credit expiry, creative fees, campaign fees, or outcome-refund promise, determine whether each buyer is a consumer or business, who is seller/provider/merchant of record, whether GrowthTwin sells its own SaaS or intermediates another contract, and what the credits legally represent. Do not label unused credits, generated content, or instant digital services “non-refundable” by assumption. The actual credit wallet and refund/cancellation rules need Turkish counsel review before a payment interface is built.

### 3. Personal data, ad leads, and onward messaging

KVKK guidance says the data controller is the party determining the purposes and means of processing; the label in a contract does not settle the role. Its current guidance says people must be informed before processing, and the 18 February 2026 Board announcement emphasizes that the information notice and explicit-consent request are distinct: notice is required regardless of the legal basis; explicit consent should only be requested when that is the selected legal basis, separately and specifically. A recent official KVKK page also sets out the post-2024 staged rules for transfers abroad: adequacy decision, appropriate safeguards (including standard contracts with notification in relevant cases), or limited incidental grounds. The page reviewed says no adequate-country decision has yet been made.

**Product consequence:** map roles and data flows separately for GrowthTwin account/profile data, source files, platform account/report data, web conversion measurement, and each lead handoff. Decide who determines each purpose and means, the lawful basis, notice, recipients, access, retention/deletion, and rights workflow before collection. Avoid raw lead custody in the first usable service; direct campaigns to the advertiser's site and use only synthetic conversion fixtures. If a future flow forwards a lead, define the recipient and exact disclosure before collection and avoid transferring sensitive data into ad prompts or analytics by default. Inventory every cloud, analytics, and AI recipient and transfer country; do not assume that user consent alone or a Türkiye-hosted app resolves the transfer requirements.

### 4. Email, SMS, and telephone follow-up

The Ministry's current information on the Commercial Communication and Commercial Electronic Messages Regulation covers SMS, email, and telephone marketing. It says prior permission is generally collected by the service provider that will send the messages; a trader or tradesperson exception exists for messages to those business recipients but ends if they exercise the rejection right. The Ministry also says an intermediary service provider cannot obtain commercial-message permission on another party's behalf, and identifies IYS as the permission/rejection record system.

**Product consequence:** a campaign “contact request” must not silently enroll a lead in ongoing marketing. Separate a request to be contacted about the stated service from consent for future promotional email/SMS/calls. If GrowthTwin later adds follow-up automation, resolve whether it is the sender/service provider or an intermediary in that flow; do not design GrowthTwin as collecting another advertiser's IYS permission without a legal basis for that exact role. Store evidence of the correct permission/rejection state only after the process is validated.

### 5. Regulated sectors and channel policy

The current Health Ministry regulation, published 12 November 2025, covers health professionals, private health facilities, and international health-tourism intermediaries. It prohibits explicit and implicit advertising in health service provision. It restricts health-facility and professional information to specified identifying, specialty, schedule, qualification, and health-protective information; it also says sponsored/featured search-engine and social-platform listings are not permitted. A category-specific service check is therefore necessary even when the advertiser wants only “a simple Search ad.”

**Product consequence:** make sector, advertised object/service, advertiser authorization, target territory, and channel first-class eligibility inputs. A generic copy generator cannot make a regulated ad acceptable. Maintain a dated rule record per category/channel, cite the governing source, distinguish permitted informational content from promotional claims, and fail closed when the rule or advertiser evidence is missing. The health rule is one concrete example; it is not a full inventory. Finance, medicines/devices, food/supplements, alcohol/tobacco, gambling, political ads, employment/housing, and other regulated areas still need separate research against both Turkish law and each ad platform's current policy.

## Readiness decisions for product planning

1. Keep the current local product slice synthetic and outside payment, lead custody, account connection, and publishing.
2. Add an advertiser/category/channel eligibility gate to the product architecture before expanding the campaign flow. The output should be `eligible`, `restricted`, `not_supported`, or `needs_review`, with a plain-language reason and cited rule version. Missing facts must pause the flow.
3. Require evidence for objective advertiser claims and retain which source supports each generated claim; unsupported claims cannot enter a publishable draft.
4. Define consumer/business checkout, seller/provider roles, taxes, credit accounting and expiry, cancellation/refund, and the exact performance-guarantee promise before designing payment UI.
5. Keep conversion measurement separate from receiving a lead. Keep a service-contact request separate from future marketing permission. Do not store or forward lead details until roles, notice, purpose, recipient, retention, and transfer path have been reviewed.
6. Review platform policy independently from Turkish law. Legal permission to advertise does not establish Google Ads acceptance or GrowthTwin API approval.

## Open questions for qualified review

- GrowthTwin's legal role in each advertiser agreement, self-service ad flow, platform account authorization, and consumer checkout.
- Whether the product's account/profile, analytics, and campaign services trigger any separate electronic-commerce information/registration duties in the intended business model.
- Consumer classification and distance-contract treatment of one-time credit packages, generated content, unused balance, immediate service, expiry, refunds, and a performance-based remedy.
- KVKK role allocation and lawful bases across GrowthTwin, each advertiser, Google, landing-page/conversion providers, cloud, and AI vendors; transfer safeguards for each recipient.
- A reliable method for proving ad claims and advertiser rights to uploaded documents, images, testimonials, marks, and generated derivatives.
- The outcome/lead definition and commercial conditions needed before making an enforceable or advertised performance/refund guarantee.
- Sector-by-sector allow/restrict/decline decisions and current Google Ads policies, including how a non-lawyer product team handles ambiguous cases.

## Official sources checked on 2026-09-29

- [Ministry of Trade: Commercial advertising principles](https://ticaret.gov.tr/tuketici/ticari-reklamlar)
- [Ministry of Trade: 6502 consumer-law legislation, including current secondary regulations](https://ticaret.gov.tr/tuketici/mevzuat/6502-sayili-tuketicinin-korunmasi-mevzuati)
- [Ministry of Trade: Distance contracts consumer guide (17 August 2026)](https://tuketici.ticaret.gov.tr/yayinlar/tuketici-bilgi-rehberi/mesafeli-sozlesmeler-hakkinda-bilgilendirme)
- [Ministry of Trade: current electronic-commerce laws and regulations](https://ticaret.gov.tr/ic-ticaret/mevzuat/elektronik-ticaret)
- [Ministry of Trade: commercial electronic message rules](https://www.ticaret.gov.tr/ic-ticaret/ticari-elektronik-iletiler/genel-bilgiler)
- [Ministry of Trade: IYS overview](https://www.ticaret.gov.tr/ic-ticaret/ticari-elektronik-iletiler/ileti-yonetim-sistemi-iys)
- [KVKK: information duty](https://www.kvkk.gov.tr/Icerik/2033/Aydinlatma-Yukumlulugu-)
- [KVKK: Board principle on separating information notices and explicit consent (18 February 2026)](https://www.kvkk.gov.tr/Icerik/8710/veri-sorumlulari-tarafindan-acik-riza-ve-aydinlatma-metinlerinin-ayri-ayri-duzenlenmesi-gerektigi-hakkinda-kisisel-verileri-koruma-kurulunun-18-02-2026-tarihli-ve-2026-347-sayili-ilke-kararina-iliskin-kamuoyu-duyurusu)
- [KVKK: international transfers](https://www.kvkk.gov.tr/Icerik/2053/Yurtdisina-Aktarim)
- [Health Ministry: Health Services Promotion and Information Regulation, published 12 November 2025](https://www.resmigazete.gov.tr/eskiler/2025/11/20251112-2.htm)
- [Health Ministry: notice that the 2025 health promotion regulation entered into force](https://shgmdenetimdb.saglik.gov.tr/TR-111587/saglik-hizmetlerinde-tanitim-ve-bilgilendirme-faaliyetleri-hakkinda-yonetmelik-yayimlanmistir.html)
- [Ministry of Trade: Commercial Advertising and Unfair Commercial Practices Regulation (official publication)](https://tuketici.ticaret.gov.tr/data/5e819a8e13b876a1b04c7a4a/T%C4%B0CAR%C4%B0%20REKLAM%20VE%20HAKSIZ%20T%C4%B0CAR%C4%B0%20UYGULAMALAR%20Y%C3%96NETMEL%C4%B0%C4%9E%C4%B0.pdf)
