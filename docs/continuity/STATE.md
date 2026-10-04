# GrowthTwin — current handoff

Last verified: 2026-10-04 19:09 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local synthetic product development. No real advertiser data, live ad
accounts, publication, media spend, or production AI use.

## Repository and CI state

- Current `main`: `94c9d2c` (PR #258, sanitized image-evaluation failure
  diagnostics).
- PR #256 required CI `37214462925` and post-merge CI `37214622803` passed.
  PR #257 required CI `37214916337` and post-merge CI `37215065615` passed.
  PR #258 required CI `37215352318` and post-merge CI `37215534053` passed.
- This snapshot is being updated on
  `docs/final-image-eval-handoff-20261004`; use a PR and merge only after
  required CI succeeds. Never push directly to `main`.

## AI/provider status

- Synthetic text comparisons: GPT-6 Luna remains an offline review candidate
  with generic drafts; Gemini did not pass the comparative quality gate. No
  production provider is selected and no model is connected to product routes.
- The owner authorized one synthetic image request using the pinned
  `google/gemini-3.1-flash-lite-image` / `google-vertex/global` path after PR
  #256 and main CI passed. The call did not produce verifiable output. Its
  local record confirms only call start; no safe error category, image, or
  provider-cost result was saved. The cause and charge are unknown. Its USD
  0.10 local reservation remains held. PR #258 now records only sanitized
  failure categories and HTTP status for future calls; no body or secret is
  recorded. No second provider request is authorized without renewed explicit
  approval.
- Previous confirmed shared evaluation ledger snapshot: USD 0.06024185 spent
  and USD 0.00078075 reserved for an earlier unresolved GPT call. No current
  post-image ledger total is verified. These are local ledger amounts, not the
  provider balance.
- The owner checks the OpenRouter account balance; it was not inspected. No
  top-up, auto-recharge, privacy-setting change, or real-data use occurred.
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

Wait for renewed explicit authorization before any second billable synthetic
image call. If authorized, run exactly once through the pinned ZDR-eligible
route with the existing cap; inspect only the local sanitized result, preserve
the unresolved USD 0.10 reservation, and never inspect the account balance.
Continue non-billable local work independently; keep AI disconnected from
product routes and do not attempt video through OpenRouter.
