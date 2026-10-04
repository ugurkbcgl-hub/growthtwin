# GrowthTwin — current handoff

Last verified: 2026-10-04 17:46 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for the Türkiye market across
industries. Continue local synthetic product development. No real advertiser
data, live ad accounts, publication, media spend, or production AI use.

## Repository and CI state

- Starting point verified on 2026-10-04: clean `main` at `fb68bb6`; PRs #246–249
  are merged and their required/post-merge CI passed. No open PRs were returned.
- A feature branch now gives Gemini a model-specific 1,024 output-token bound;
  GPT-6 Luna remains at 512. Focused no-network tests (5), estimate, and Ruff
  passed locally. The nine-call Gemini estimate is USD 0.061142; no network
  calls were made by these checks.
- The Gemini change has not yet been reviewed or merged. Verify this branch's
  PR and required CI before any provider call.

## AI/provider status

- Deterministic website templates remain active; no provider is connected to
  product routes and no production model is selected.
- OpenRouter's read-only account-key/API inspection after the owner's update
  confirmed the approved USD 16 cap with no reset. No account balance or usage
  amount is recorded here.
- OpenRouter's generation log matched both Gemini calls to Google Vertex at
  their local timestamps. They returned 496 and 497 output tokens,
  `finish_reason=length`, at USD 0.00221 each. No response text was opened.
  The two local reservations were reconciled to this dashboard evidence.
- Shared evaluation ledger: USD 0.0102197 spent and USD 0.00078075 reserved.
  The remaining reservation belongs to an earlier GPT call and remains held
  pending separate reconciliation. These local ledger amounts are not live
  account credits.
- Earlier Gemini attempts did not produce usable validated outputs. The
  token-bound fix is intended to address truncation only; candidate quality is
  still unproven.

## Risks and boundaries

Use only fixed synthetic cases; `zdr=true` and `data_collection=deny` do not
establish Türkiye/EU processing or KVKK compliance. Do not top up or enable
auto-recharge, send private data, connect live ad accounts, publish, spend
media budget, or connect AI to product routes. Keep the account cap and local
ledger safeguards intact. Never store secrets or generated private content in
Git.

## Next action

Review and merge the Gemini-specific 1,024-token cap only after required CI
passes, then run the one fixed nine-call synthetic evaluation once. Stop at the
first truncation or unverified response/accounting result. If it completes,
review the captured synthetic variants manually for claims, usefulness,
diversity, and correction effort; do not select a production provider from a
single run. Preserve the unrelated USD 0.00078075 reservation until its own
OpenRouter generation log can be matched.
