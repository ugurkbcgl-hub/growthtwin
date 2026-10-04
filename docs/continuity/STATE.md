# GrowthTwin — current handoff

Last verified: 2026-10-04 18:03 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local synthetic product development. No real advertiser data, live ad
accounts, publication, media spend, or production AI use.

## Repository and CI state

- PR #250 merged as `2ab4ea4`; required CI `37210497789` and post-merge CI
  `37210643009` passed.
- PR #251 merged as `d61e344`; required CI `37211134452` and post-merge CI
  `37211271343` passed.
- Current docs-only update is being prepared from a feature branch. Verify its
  open PR and CI, then check final `main` state. Do not push directly to `main`.

## AI/provider status

- The fixed Gemini 3.8 Flash evaluation completed 9/9 calls across three
  synthetic briefs. Average latency was 6.741 seconds, maximum 8.993 seconds;
  actual call costs totaled USD 0.03401925.
- All results were structurally accepted, review-required, and non-publishable.
  The exact configured forbidden-phrase screen found no matches, but manual
  assistant review found unsupported details and repeated angles. Provisional
  scores: usefulness 3/5, grounding 3/5, diversity 2/5, brand fit 3/5,
  correction effort 2/5. Gemini does not pass the candidate gate.
- GPT-6 Luna's earlier assistant-side heuristic review scored usefulness 3/5,
  fixture-relative grounding 5/5, diversity 3/5, brand fit 3/5, and correction
  effort 2/5. Side-by-side review using the same rubric remains to be done.
- Shared local ledger: USD 0.05826245 spent; USD 0.00078075 reserved for an
  unresolved earlier GPT call. These are not live account credits. The owner
  verified the approved USD 16 key cap with no reset. Balance was not checked.
- Website routes remain deterministic; no production provider is selected.

## Risks and boundaries

Use only fixed synthetic cases. Exact phrase screens do not establish semantic
truth/safety. `zdr=true` and `data_collection=deny` do not establish Türkiye/EU
processing or KVKK compliance. No credit top-up or auto-recharge, private data,
live ad-account connection, publication, media spend, or AI product-route use.
Keep account and local-ledger safeguards intact. Never store credentials or
provider output in Git.

## Next action

Review PR #252 (docs-only) and required CI if it is open; merge only after CI
passes under the owner's standing authorization. Then compare captured local
Gemini and GPT variants side by side under one rubric and reviewer, focusing
on claims, usefulness, diversity, brand fit, and correction effort. Do not
make another provider call until that review identifies a decision-changing
question. Preserve the unrelated USD 0.00078075 GPT reservation until its own
OpenRouter generation log is reconciled.
