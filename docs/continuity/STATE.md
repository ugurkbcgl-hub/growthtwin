# GrowthTwin — current handoff

Last verified: 2026-10-04 17:22 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished self-service paid-advertising platform for Türkiye across
industries. Continue local synthetic development. No real advertiser data,
live ad accounts, publication, media spend, or production AI use.

## Repository and CI state

- PR #246 added bounded candidate selection for the synthetic OpenRouter
  benchmark, merged to `main` as `fcdc3e9`; required CI `37203552127` and
  post-merge CI `37208468991` passed.
- PR #247 fixed the unverified-response branch in the benchmark loop, merged to
  `main` as `000f014`; required CI `37208553129` passed. Post-merge CI
  `37208716235` was still running at last check.
- Current documentation PR #248 is on
  `docs/openrouter-cross-vendor-handoff` at `49472a8`, based on `000f014`;
  required CI was running at last check. Recheck its PR and CI status, branch,
  working tree, latest commit, and other open PRs before acting.

## AI and product status

- The website uses deterministic templates. No provider is connected to product
  routes and no production model is selected.
- GPT-6 Luna's captured synthetic baseline and prompt-iteration comparison were
  heuristically reviewed by the assistant, not independently by a person.
  Diversity moved from 2.33/5 to 3/5; usefulness 3/5, fixture-relative
  grounding 5/5, brand fit 3/5, and correction effort 2/5 were unchanged.
  Results remain generic review drafts, not production candidates.
- The full post-prompt GPT-6 Luna run completed 9/9 for USD 0.0017208, average
  latency 3.803 seconds; Azure was returned upstream in all calls. A separate
  attempt stopped after six calls on unverified response/accounting; USD
  0.00078075 remains reserved.
- PR #246 permits selecting Gemini 3.8 Flash for this synthetic evaluation
  only. Its first attempted call yielded no verifiable benchmark result; the
  remaining eight were not sent. PR #247 fixed the resulting local benchmark
  exception. USD 0.004761 remains reserved for the call with unknown provider
  cost.
- The shared local USD 16 ledger reports USD 0.0057997 spent and USD 0.00554175
  reserved; USD 15.98865855 remains inside that local allocation. This is not
  a live credit balance.
- A read-only current-key API check contradicted the owner's earlier
  confirmation: the returned limit/reset configuration did not match the
  approved USD 16 limit with no reset. No more hosted calls until corrected and
  reverified. Account usage/remaining-credit amounts are intentionally omitted
  from repository history.
- Use only repository synthetic cases. `zdr=true` and
  `data_collection=deny` do not guarantee Türkiye/EU processing or KVKK
  compliance.

## Risks and gates

- Never store credentials in chat, source, Git, logs, or handoff files. Do not
  top up, enable auto-recharge, use real advertiser/customer/patient data,
  connect live ad accounts, publish, spend media budget, or route AI through a
  product route.
- The first Gemini result has unknown cost; retain its USD 0.004761 reservation
  unless usage is reconciled. Do not reset the shared ledger.

## Next action

Correct the dedicated OpenRouter evaluation key to the authorized USD 16
no-reset limit and verify it with the read-only current-key endpoint; only then
diagnose the unverified Gemini response/accounting path and consider rerunning
the fixed suite. Keep the existing reservation held, use synthetic fixtures,
and manually review any valid outputs before drawing a candidate conclusion.
