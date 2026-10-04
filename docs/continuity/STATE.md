# GrowthTwin — current handoff

Last verified: 2026-10-04 18:47 +0300 (Europe/Istanbul). Repository:
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
- PR #252 merged as `e7b7ef2`; required CI `37211772281` and post-merge CI
  `37211905675` passed.
- PR #253 merged as `dd0c0af`; required CI `37212140811` and post-merge CI
  `37212274710` passed.
- PR #254 merged as `03d1f49`; required CI `37212660663` and post-merge CI
  `37212801135` passed.
- PR #255 merged as `7ed51ee`; required CI `37213371584` and post-merge CI
  `37213592296` passed.
- PR #256 adds one bounded synthetic image-evaluation path on
  `eval/openrouter-image-synthetic`. Required CI `37214309287` is running;
  review and merge only after it passes. Never push directly to `main`.

## AI/provider status

- The full fixed Gemini synthetic evaluation completed 9/9; it had generic,
  repetitive drafts and some unsupported operational details. Do not select it.
- PR #253 tightened the shared offline prompt for grounded facts and distinct
  angles. The follow-up fixed GPT-6 Luna suite completed 9/9 after required and
  post-merge CI passed. No configured forbidden phrases or unsupported factual
  details were found in manual review. The outputs were concise but generic;
  heuristic ratings remained usefulness 3/5, grounding 5/5, diversity 3/5,
  brand fit 3/5, correction effort 2/5. GPT is the preferred current text
  candidate for further offline synthetic review only; no production selection.
- Shared local evaluation ledger: USD 0.06024185 spent, USD 0.00078075 reserved
  for an unresolved earlier GPT call. These are not live account credits. The
  owner handles checking the OpenRouter balance; it was not checked.
- Official image catalog review found a single-output, 1K 9:16 Google Gemini
  3.1 Flash Lite Image route pinned to the ZDR-eligible `google-vertex/global`
  endpoint. A local-only runner estimates USD 0.0336 list cost and reserves at
  most USD 0.10 for one call. It has not made a provider request. OpenRouter's
  asynchronous video API is not ZDR-eligible and is excluded; account privacy
  settings were not changed.
- Website routes remain deterministic; no provider is connected to product
  routes.

## Risks and boundaries

Use only synthetic cases. Exact phrase screens and assistant ratings do not
establish general semantic safety, legal compliance, or production quality.
`zdr=true` and `data_collection=deny` do not establish Türkiye/EU processing or
KVKK compliance. No credit top-up or auto-recharge, private data, live ad
account connection, publication, media spend, or AI product-route use. Never
store credentials or provider output in Git.

## Next action

After PR #256 and its post-merge CI pass, make exactly one synthetic 1K image
request through the pinned ZDR-eligible provider, using its USD 0.10 local
reservation and the existing approved shared budget. Inspect the saved asset
locally, record the result and cost, then decide whether any further visual
evaluation is justified. Do not attempt video through OpenRouter, inspect its
balance or change privacy settings, or connect outputs to product routes.
Preserve USD 0.00078075 until the earlier GPT request's generation log is
matched.
