# GrowthTwin — current handoff

Last verified: 2026-10-04 13:28 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Continue local synthetic development. No real advertiser data,
live ad accounts, publication, media spend, or production AI use.

## Repository and CI state

- The verified base was clean `main` at `9f68dad3c33284c24243ad3d510cbf3eb4f0241e`
  (PR #237). PRs #235–237 and their required/post-merge CI checks passed:
  `37154223644`, `37154378786`, `37192777132`, `37192892848`,
  `37193067113`, and `37193177093`. No open PRs were returned before this
  evaluation-result documentation branch was created. Verify live Git/PR/CI
  state before acting.

## AI and product status

- The website still uses deterministic templates. No AI provider is connected
  to a product route; no production provider is selected.
- PR #231/#234 provide opt-in OpenAI/OpenRouter text adapters. OpenRouter's
  fixed runner uses three synthetic briefs × three calls, up to 512 output
  tokens, a 4,096-byte request cap, no tools/retries, structured output,
  `zdr=true`, `data_collection=deny`, and per-token price caps. Results remain
  non-publishable and require review.
- PR #234 added Windows current-user DPAPI key setup. The key is now stored in
  the current Windows user's DPAPI-protected local secret folder; its value is
  never to be read into chat, logs, or Git.
- On 2026-10-04, the owner reported USD 16 of existing OpenRouter credits and
  directed usage tracking against that balance. PR #235 sets a shared local
  cumulative USD 16 ledger and calls for a dedicated USD 16 no-reset key cap.
  No top-up or auto-recharge is authorized.
- The owner keeps OpenRouter account balance and auto-recharge checks in their
  hands and signaled readiness before the first run. The assistant did not
  access the account; do not claim its live balance/settings were verified.
- On 2026-10-04, the fixed nine-call synthetic GPT-6 Luna run completed.
  OpenRouter-reported costs and the shared ledger show USD 0.0014665 spent,
  zero reserved, and USD 15.9985335 remaining under the local USD 16 cap.
  Outputs are review-required/non-publishable; manual quality scores are
  pending. The run output was not persisted, and no second run was made.
- The preflight estimate was at most USD 0.005834 for nine calls. Four focused
  OpenRouter tests and broader focused gateway tests passed in recorded runs;
  PR and post-merge CI also passed. No real data or production route was used.
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

Before another hosted run, make the synthetic runner preserve JSONL results
outside the repository so usefulness, source grounding, diversity, brand fit,
and correction effort can be reviewed after execution. Keep the OpenRouter
account check owner-controlled; recheck the live account only if the owner
explicitly asks. No more calls until the saved outputs can be reviewed and the
owner confirms any needed account-side readiness. Before acting, recheck live
branch, worktree, latest commit, open PRs, and CI status.
