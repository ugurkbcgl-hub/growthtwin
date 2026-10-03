# GrowthTwin — current handoff

Last verified: 2026-10-03 23:52 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Product runtime and AI quality must not depend on the owner's
local PC/GPU. Continue synthetic development; no real advertiser data, live
ad accounts, publication, media spend, or production AI use.

## Repository and PR state

- `main` remains clean at `9b503b3118f93632a6311259e964914a603e4124`.
  Main CI `37150797067` passed. No other open PRs were returned.
- Current feature branch `feature/openrouter-synthetic-evaluation` is at
  `38858ed`. PR #234 is open; required CI run `37153088546` was in progress at
  the last check. Review CI before merging under the owner's standing
  authorization.

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
  PowerShell wrapper that asks the operator to verify a no-reset USD 4.50 key
  limit, sufficient existing credits, and disabled auto-recharge before calls.
  Four focused no-network Django tests passed; Ruff and formatting passed;
  estimate mode reserved at most USD 0.005834 for nine calls. No key was
  present, no hosted request was sent, and no spend occurred. PR CI remains
  pending.
- A shared local SQLite ledger reserves call cost before dispatch and caps the
  local allocation at USD 4.50, leaving USD 0.50 headroom inside the owner's
  approved USD 5 total. Never automatically replenish or reset the ledger.
  The operator-confirmation environment flag does not prove account settings.
- One synthetic run is estimated to reserve at most USD 0.005425. Estimate
  mode, Ruff checks, `git diff --check`, and 30 focused AI gateway tests passed.
  PR and post-merge CI passed. No hosted API request was made and no AI cost was
  incurred; `OPENAI_API_KEY` was absent.
- OpenRouter requires a USD 5 minimum credit purchase and currently charges a
  Standard account purchase fee with a USD 0.80 minimum, so a new credit buy
  exceeds the USD 5 total approval before tax. Do not top up or enable
  auto-recharge. Evaluation requires sufficient existing credits and a
  dedicated no-reset USD 4.50 API-key cap; account balance and key settings are
  unverified.
- OpenRouter `zdr=true` and `data_collection=deny` constrain eligible upstream
  providers but do not establish local/Türkiye processing or KVKK compliance.
  Use synthetic data only and fail closed if no endpoint satisfies the request.

## Risks and gates

- Recheck official provider prices, model availability, terms and data controls
  immediately before each hosted evaluation. This is not a KVKK assessment or
  Türkiye-only processing guarantee.
- The user's USD 5 approval does not authorize real customer data, routes,
  publication, advertiser media spend, automatic replenishment, or a production
  provider. Reassess before using the reserved USD 0.50 or adding another
  paid candidate.
- Image/video APIs, customer-file intake, live account connection, production
  publishing and media spend remain out of scope.

## Next action

After PR #234 passes required CI and is merged, ask the owner only to create a
dedicated OpenRouter key capped at USD 4.50 with no reset, confirm sufficient
existing credits and auto-recharge off, then securely store it with
`apps/web/scripts/setup_openrouter_key.ps1`. Run
`apps/web/scripts/run_openrouter_synthetic.ps1`; stop at the shared local USD
4.50 allocation and review results before considering any further spend.
