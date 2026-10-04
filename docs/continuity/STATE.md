# GrowthTwin — current handoff

Last verified: 2026-10-04 19:00 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local synthetic product development. No real advertiser data, live ad
accounts, publication, media spend, or production AI use.

## Repository and CI state

- Current `main`: `4bb188d` (PR #256, bounded synthetic image evaluator).
- PR #256 required CI `37214462925` passed; post-merge CI `37214622803`
  passed. No open PRs were found before this documentation update.
- Current work is on `docs/image-eval-outcome-20261004`; prepare a documentation
  PR, review it locally, and merge only after required CI succeeds. Never push
  directly to `main`.

## Completed and current AI/provider status

- Synthetic text comparisons: GPT-6 Luna remains an offline review candidate
  with generic drafts; Gemini did not pass the comparative quality gate. No
  production provider is selected and no model is connected to product routes.
- The owner authorized one synthetic image request using the pinned
  `google/gemini-3.1-flash-lite-image` / `google-vertex/global` path after PR
  #256 and main CI passed. The call did not produce verifiable output. A local
  record confirms only call start; there is no image or provider-cost result.
  Charge is unknown; its USD 0.10 local reservation remains held. The previous confirmed shared ledger snapshot also had USD 0.06024185 spent and USD 0.00078075 reserved for an earlier unresolved GPT call; no post-image ledger total is verified. No retry is
  authorized without renewed user approval.
- The owner checks the OpenRouter account balance; it was not inspected. No
  top-up, auto-recharge, privacy-setting change, or real-data use occurred.
- OpenRouter video remains excluded because its async video API is not
  ZDR-eligible.

## Risks and boundaries

Use synthetic cases only. Exact phrase screens and assistant ratings do not
establish general semantic safety, legal compliance, copyright clearance, or
production quality. `zdr=true` and `data_collection=deny` do not establish
Türkiye/EU processing or KVKK compliance. Do not store credentials or provider
output in Git. Do not inspect provider balance, retry billable calls, buy
credits, or change privacy settings without applicable authorization.

## Next action

Submit the documentation update describing the unresolved image-call outcome.
Then inspect the local runner implementation and sanitized operational state to
identify why it failed without revealing credentials, reading account balance,
or making another provider request. Keep the USD 0.10 reservation held. Ask
for renewed authorization before any further billable attempt.
