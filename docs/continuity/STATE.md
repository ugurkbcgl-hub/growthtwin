# GrowthTwin — current handoff

Last verified: 2026-10-04 12:35 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Continue local synthetic development. No real advertiser data,
live ad accounts, publication, media spend, or production AI use.

## Repository and CI state

- `main` is clean at `aa99ec27ce333e05cfe6ec16daf4350c44c8afc0` (PR #235).
- PR #235, which set the cumulative OpenRouter evaluation ledger to USD 16,
  is merged. Required CI `37154223644` and post-merge `main` CI `37154378786`
  both passed. No other open PRs were returned before this documentation
  refresh branch was created.
- Current documentation branch: `docs/openrouter-balance-owner-check`, based
  on `aa99ec2`. It removes stale USD 5 evaluation-budget claims and records
  that the owner, not the assistant, checks OpenRouter balance/settings.
  Verify this branch's PR and CI live before treating it as merged.

## AI and product status

- The website still uses deterministic templates. No AI provider is connected
  to a product route; no production provider is selected.
- PR #231/#234 provide opt-in OpenAI/OpenRouter text adapters. OpenRouter's
  fixed runner uses three synthetic briefs × three calls, up to 512 output
  tokens, a 4,096-byte request cap, no tools/retries, structured output,
  `zdr=true`, `data_collection=deny`, and per-token price caps. Results remain
  non-publishable and require review.
- PR #234 added Windows current-user DPAPI key setup. The key has not been
  installed in this environment; no hosted request or spend has occurred.
- On 2026-10-04, the owner reported USD 16 of existing OpenRouter credits and
  directed usage tracking against that balance. PR #235 sets a shared local
  cumulative USD 16 ledger and calls for a dedicated USD 16 no-reset key cap.
  No top-up or auto-recharge is authorized.
- The owner explicitly keeps OpenRouter account balance and auto-recharge
  checks in their hands. Do not access the account or claim those settings are
  verified. The USD 16 remains owner-reported until the owner confirms.
- The no-network estimate for a fixed run is at most USD 0.005834 reserved for
  nine calls. Four focused OpenRouter tests and the broader focused gateway
  tests passed in their recorded runs; PR and post-merge CI also passed. The
  successful GitHub CI runs are `37154223644` and `37154378786`.
- Provider retention controls do not establish local/Türkiye processing or
  KVKK compliance. Use repository synthetic fixtures only.

## Risks and gates

- Before any billable run, the owner verifies the dedicated key's USD 16
  no-reset limit, sufficient existing balance, and disabled auto-recharge;
  the assistant does not inspect the OpenRouter dashboard.
- Never send keys, real advertiser/customer/patient data, or private account
  data to this evaluation. Do not top up, enable auto-recharge, publish ads,
  connect advertiser accounts, or use a production AI provider.
- The hosted run requires the key to be entered only in the hidden local
  prompt from `apps/web/scripts/setup_openrouter_key.ps1`, not in chat.

## Next action

Finish and merge the current documentation-only PR after required CI passes.
Then wait for the owner to verify the OpenRouter key/account limits and signal
readiness. Only then run the local hidden-key setup and, after its explicit
`RUN` confirmation, the bounded synthetic evaluation; review the cumulative
ledger and stop at its USD 16 cap.
