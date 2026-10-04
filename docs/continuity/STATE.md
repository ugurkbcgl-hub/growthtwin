# GrowthTwin — current handoff

Last verified: 2026-10-04 19:01 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local synthetic product development. No real advertiser data, live ad
accounts, publication, media spend, or production AI use.

## Repository and CI state

- Current `main`: `a09d65f` (PR #257, image-call outcome documentation).
- PR #256 required CI `37214462925` and post-merge CI `37214622803` passed.
  PR #257 required CI `37214916337` and post-merge CI `37215065615` passed.
- Current work is on `fix/sanitized-image-eval-diagnostics`; review its code and
  docs, then use a PR and merge only after required CI succeeds. Never push
  directly to `main`.

## Completed and current AI/provider status

- Synthetic text comparisons: GPT-6 Luna remains an offline review candidate
  with generic drafts; Gemini did not pass the comparative quality gate. No
  production provider is selected and no model is connected to product routes.
- The owner authorized one synthetic image request using the pinned
  `google/gemini-3.1-flash-lite-image` / `google-vertex/global` path after PR
  #256 and main CI passed. The call did not produce verifiable output. A local
  record confirms only call start; the runner suppressed diagnostic details,
  so the cause cannot be determined. There is no image or provider-cost result.
  Charge is unknown; its USD 0.10 local reservation remains held. A code
  change will record only sanitized failure categories/status, not response
  bodies or secrets, for any future explicitly authorized call. The previous
  confirmed shared ledger snapshot had USD 0.06024185 spent and USD 0.00078075
  reserved for an earlier unresolved GPT call; no post-image ledger total is
  verified. No retry is authorized without renewed user approval.
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

Review PR for sanitized image-call failure diagnostics and merge only after
required CI passes. The prior call's root cause is unknown because its failure
category was not recorded. Keep the USD 0.10 reservation held. Do not make
another provider request without renewed authorization; do not inspect the
account balance.
