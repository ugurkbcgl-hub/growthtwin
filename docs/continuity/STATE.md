# GrowthTwin — current handoff

Last verified: 2026-10-05 00:05 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local synthetic product development. No real advertiser data, live ad
accounts, publication, media spend, or production AI use.

## Repository and CI state

- Verified base `main`: `1f17927` (PR #263, improved sanitized image-response diagnostics).
- PR #256 required CI `37214462925` and post-merge CI `37214622803` passed.
  PR #257 required CI `37214916337` and post-merge CI `37215065615` passed.
  PR #258 required CI `37215352318` and post-merge CI `37215534053` passed.
  PR #259 required CI `37215728911` and post-merge CI `37215872411` passed.
  PR #260 required CI `37230669981` and post-merge CI `37230830736` passed.
  PR #261 required CI `37231049330` and post-merge CI `37231211050` passed.
- PR #263 (`fix/classify-image-eval-response-failures`) merged as `1f17927`.
  Required CI `37234341834` and post-merge CI `37234496365` passed, including
  Django tests and browser E2E. Local review and `git diff --check` passed.
  Never push directly to `main`.

## AI/provider status

- Synthetic text comparisons: GPT-6 Luna remains an offline review candidate
  with generic drafts; Gemini did not pass the comparative quality gate. No
  production provider is selected and no model is connected to product routes.
- The owner separately authorized two one-call synthetic image attempts using
  the pinned `google/gemini-3.1-flash-lite-image` /
  `google-vertex/global` route. Both lacked verifiable image and provider-cost
  output. The first record confirms only call start; the second safely records
`invalid_or_unverifiable_response` with no HTTP status. The failure cause and
provider charges remain unknown. Both USD 0.10 local reservations remain held.
PR #258 ensures future failures save only safe category/status, no response
  body or secret.
- Read-only local ledger verification: USD 0.06024185 spent and USD
  0.20078075 reserved; reservations comprise USD 0.00078075 for the unresolved
  earlier GPT call and USD 0.20 for the two image attempts. These are local
  ledger amounts, not provider billing or the provider balance.
- The owner checks the OpenRouter account balance; it was not inspected. No
  top-up, auto-recharge, privacy-setting change, or real-data use occurred.
- PR #263 separates safe response failure categories, including missing usage
  cost, malformed JSON/shape, missing image data and HTTP errors. Official
  Image API documentation says `usage.cost` is included when available. This
  may explain the second attempt's generic failure, but its stored record does
  not prove that; both attempt causes and provider charges remain unknown. No
  further provider request was made.
- OpenRouter video remains excluded because its async video API is not
  ZDR-eligible.

## Risks and boundaries

Use synthetic cases only. Small evaluations do not establish general safety,
legal compliance, rights clearance, or production quality. `zdr=true` and
`data_collection=deny` do not establish Türkiye/EU processing or KVKK
compliance. Do not store credentials or provider output in Git. Do not inspect
provider balance, retry billable calls, buy credits, change privacy settings,
or use real data without applicable authorization.

## Next action

Continue non-billable local work from the roadmap. Preserve both unresolved
image reservations and never inspect the OpenRouter account balance. Any
further billable synthetic image call requires renewed explicit authorization;
if received, run exactly once through the pinned ZDR-eligible route and inspect
only its local sanitized result. Keep AI disconnected from product routes and
do not attempt video through OpenRouter.
