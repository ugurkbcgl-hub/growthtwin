# GrowthTwin — current handoff

Last verified: 2026-10-04 00:09 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Product runtime and AI quality must not depend on the owner's
local PC/GPU. Continue synthetic development; no real advertiser data, live
ad accounts, publication, media spend, or production AI use.

## Repository and PR state

- PR #234 merged. `main` is clean at `fb9d71e7d13c7c14f8cc0fe098f88ca26273ade`.
  Required PR CI `37153197815` and post-merge main CI `37153354644` passed.
  No open PRs were returned before this budget-update branch was created.
- Current feature branch: `feature/track-openrouter-prepaid-usage`. Its PR and
  required CI status should be verified live before merge.

## AI and product status

- The website remains deterministic. No AI provider is connected to a user
  route and no production provider is selected. Ollama is an optional local
  experiment; its recent synthetic candidates failed the small creative gate.
- PR #231 added an opt-in OpenAI GPT-6 Luna text adapter. PR #234 adds a
  separate OpenRouter adapter and fixed synthetic runner for the same model:
  three briefs × three calls, up to 512 output tokens, a 4,096-byte request
  cap, no tools/retries, structured output, `zdr=true`,
  `data_collection=deny`, and provider token-price caps. Both adapters remain
  disconnected from routes and return non-publishable drafts requiring human
  review.
- PR #234 adds Windows current-user DPAPI storage for the OpenRouter key and a
  PowerShell wrapper. Its PR and post-merge CI passed. Four focused no-network
  tests passed; Ruff and formatting passed; estimate mode reserved at most USD
  0.005834 for nine calls. No key was present, no hosted request was sent, and
  no spend occurred.
- On 2026-10-04, the owner confirmed USD 16 of existing OpenRouter credits and
  replaced the earlier USD 5 evaluation cap with cumulative tracking against
  the current balance. The current feature branch increases the shared local
  SQLite ledger to USD 16 and sets the dedicated key cap to USD 16 with no
  reset; no top-up or auto-recharge is authorized. The ledger reserves each
  call before dispatch and retains reservations after ambiguous failures.
  The operator-confirmation flag does not prove account settings.
- One synthetic run is estimated to reserve at most USD 0.005425. Estimate
  mode, Ruff checks, `git diff --check`, and 30 focused AI gateway tests passed.
  PR and post-merge CI passed. No hosted API request was made and no AI cost was
  incurred; `OPENAI_API_KEY` was absent.
- Owner-reported OpenRouter balance is USD 16; live balance and auto-recharge
  status remain unverified. Do not top up. A dedicated no-reset USD 16 key cap
  and the shared local ledger bound this evaluation to the reported prepaid
  balance.
- OpenRouter `zdr=true` and `data_collection=deny` constrain eligible upstream
  providers but do not establish local/Türkiye processing or KVKK compliance.
  Use synthetic data only and fail closed if no endpoint satisfies the request.

## Risks and gates

- Recheck official provider prices, model availability, terms and data controls
  immediately before each hosted evaluation. This is not a KVKK assessment or
  Türkiye-only processing guarantee.
- The owner's balance confirmation does not authorize real customer data,
  routes, publication, advertiser media spend, automatic replenishment, new
  credit purchases, or a production provider. Stop at the existing balance and
  reassess before any new funding or another paid candidate.
- Image/video APIs, customer-file intake, live account connection, production
  publishing and media spend remain out of scope.

## Next action

After the current budget-update PR passes required CI and is merged, have the
owner create a dedicated OpenRouter key capped at USD 16 with no reset, confirm
the available credit balance and auto-recharge is off, then securely store the
key with `apps/web/scripts/setup_openrouter_key.ps1`. Run
`apps/web/scripts/run_openrouter_synthetic.ps1`; review cumulative usage and
stop before exceeding the existing credit balance.
