# GrowthTwin — current handoff

Last verified: 2026-10-04 12:42 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Continue local synthetic development. No real advertiser data,
live ad accounts, publication, media spend, or production AI use.

## Repository and CI state

- The verified base was clean `main` at
  `206fcf9ca` (PR #236). PR #235 set the cumulative OpenRouter evaluation
  ledger to USD 16; its required CI `37154223644` and post-merge `main` CI
  `37154378786` passed. PR #236 removed stale USD 5 evaluation-budget claims
  and recorded that the owner checks OpenRouter balance/settings. Its required
  CI `37192777132` and post-merge `main` CI `37192892848` passed. No other open
  PRs were returned after PR #236 merged. A documentation-only branch updates
  this snapshot; verify live Git/PR/CI state before acting.

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

Wait for the owner to verify the dedicated OpenRouter key's USD 16 no-reset
limit, current available balance, and disabled auto-recharge, and to signal
readiness. The assistant must not access the account. Then run the local
hidden-key setup and, after the owner's explicit `RUN` confirmation, the
bounded synthetic evaluation; review the cumulative ledger and stop at its
USD 16 cap. Before proceeding, recheck the live repository branch, working
tree, latest commit, open PRs, and CI status.
