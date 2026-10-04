# GrowthTwin — current handoff

Last verified: 2026-10-04 14:33 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Continue local synthetic development. No real advertiser data,
live ad accounts, publication, media spend, or production AI use.

## Repository and CI state

- PR #239 (`feature/local-jsonl-evaluation-capture`) merged to `main` as
  `e8740e58e24e876ee43b948bd7dbeb19852e01a4`; required CI `37197149607` and
  post-merge `main` CI `37197326006` passed. PR #240 refreshed this handoff
  and merged as `15cec7ae1099255a9deb814b624101e50e90c60b`; its required CI
  `37197561977` and post-merge `main` CI `37197710180` passed, including
  Django tests and browser E2E. PR #241 corrected the verified repository
  snapshot and merged as `3142c4c6e6b34473a08c2d49f0fbff155e7cc9a9`; its
  required CI `37197887034` and post-merge CI `37198017987` passed. PR #242
  refreshed the OpenRouter evaluation status and merged as
  `cd1b3aee795045cee167a987eb9fc2a7c6a0072e`; its required CI `37198866107`
  and post-merge CI `37199002685` passed. At 2026-10-04 14:33 +0300, the
  working copy was clean `main` at `cd1b3ae` and no open PRs were returned.
  Recheck live Git/PR/CI state before acting.

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
- Merged PR #239 adds per-run local JSONL capture under
  `%LOCALAPPDATA%\GrowthTwin\evaluations`, before any next hosted run. Records
  omit the brief/request body and API key; result rows include generated
  synthetic variants and manual-review slots. No API request was made for this
  change.
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

After the owner confirms account-side readiness (dedicated key limit, existing
balance, and auto-recharge setting), make one bounded synthetic run with the
merged JSONL capture and manually score usefulness, source grounding,
diversity, brand fit, and correction effort. The assistant must not inspect
OpenRouter balance/auto-recharge settings. Recheck live branch, worktree, latest
commit, open PRs, and CI status before acting.
