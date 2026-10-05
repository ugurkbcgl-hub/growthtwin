# GrowthTwin — current handoff

Last verified: 2026-10-05 18:13 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Current handoff scope: do not begin product features until Phase 0 is complete.
Use synthetic data only. No real advertiser data, live ad accounts,
publication, media spend, or production AI use.

## Repository and CI state

- Verified `origin/main`: `5cf013134107eb399048946b016d2853cad5228d` (PR #267).
- PR #267 (`docs: refresh low-usage GrowthTwin handoff`) merged at
  2026-10-05 01:03 +0300. Required CI `37238412605` and post-merge CI
  `37238542795` passed, including Django tests and browser E2E. At this
  verification, no PRs were open. The current handoff branch
  `docs/low-usage-handoff-20261005-1508` was created from this `main` commit;
  the working tree was clean before this documentation update. PR #268 carries
  this snapshot and was open when checked; verify its current state and CI
  before acting.
- PR #266 merged as `986aab894cdb728744026292e661d0d0d3908f8d`; required CI
  `37237129966` and post-merge CI `37237255078` passed.
- PR #256 required CI `37214462925` and post-merge CI `37214622803` passed.
  PR #257 required CI `37214916337` and post-merge CI `37215065615` passed.
  PR #258 required CI `37215352318` and post-merge CI `37215534053` passed.
  PR #259 required CI `37215728911` and post-merge CI `37215872411` passed.
  PR #260 required CI `37230669981` and post-merge CI `37230830736` passed.
  PR #261 required CI `37231049330` and post-merge CI `37231211050` passed.
- PR #263 merged as `1f17927`; required CI `37234341834` and post-merge CI
  `37234496365` passed. PR #264 refreshed this state; required CI
  `37234728688` and post-merge CI `37234918113` passed, including Django
  tests and browser E2E.
- PR #265 (`fix/openrouter-image-media-type`) merged as `183df04`; required CI
  `37236726475` and post-merge CI `37236885525` passed, including Django tests
  and browser E2E. Local Ruff lint/format and `git diff --check` passed. Never
  push directly to `main`.
- PR #266 merged as `986aab894cdb728744026292e661d0d0d3908f8d`; required CI
  `37237129966` and post-merge CI `37237255078` passed. At verification, the
  working tree was clean and no PRs were open. This handoff is being prepared
  on `docs/low-usage-handoff-20261005`; do not push directly to `main`.

## AI/provider status

- Synthetic text comparisons: GPT-6 Luna remains an offline review candidate
  with generic drafts; Gemini did not pass the comparative quality gate. No
  production provider is selected and no model is connected to product routes.
- The owner separately authorized two one-call synthetic image attempts using
  the pinned `google/gemini-3.1-flash-lite-image` /
  `google-vertex/global` route. Matching OpenRouter Logs entries show both
  completed and were charged USD 0.0336 each; the local runner saved neither
  image. Their exact MIME type and precise historical rejection point remain
  unavailable. PR #265 removes the PNG-only assumption: the runner validates
  PNG, JPEG, and WebP signatures against optional `media_type` and saves the
  matching extension. No retry or new provider request was made. PR #258
  ensures failures save only safe category/status, without response body or
  secret.
- Reconciled the two image reservations against the matching visible provider
  costs. Local ledger now records USD 0.12744185 spent and USD 0.00078075
  reserved for the unresolved earlier GPT call. These are local ledger
  amounts, not the provider account balance.
- The owner checks the OpenRouter account balance; it was not inspected. No
  top-up, auto-recharge, privacy-setting change, or real-data use occurred.
- PR #263 separates safe response failure categories, including missing usage
  cost, malformed JSON/shape, missing image data and HTTP errors. PR #265
  removes the PNG-only assumption based on the Image API's documented
  `media_type` and PNG/JPEG/WebP outputs. It has not been tested against a new
  provider request.
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

Resolve the Phase 0 data-safety blocker before any new product-feature work:
obtain privacy-preserving, owner-approved evidence that the unclassified
legacy drafts and workspace creative values in the configured local database
are synthetic. Until then, leave that database untouched and do not inspect or
dump those values. Preserve the unresolved USD 0.00078075 GPT reservation;
do not inspect the OpenRouter account balance or make another billable call
without renewed explicit authorization. Keep AI disconnected from product
routes and do not use OpenRouter video.
