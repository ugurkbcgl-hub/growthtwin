# GrowthTwin — current handoff

Last verified: 2026-10-04 18:25 +0300 (Europe/Istanbul). Repository:
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
- PR #254 merged as `03d1f49`; required CI `37212660663` passed. Post-merge CI
  `37212801135` is running; verify it before treating the integration as fully
  green.
- PR #255 contains the image/video research documentation on
  `docs/image-video-provider-research`. Its required CI is running; review and
  merge only after it passes. Never push directly to `main`.

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

Complete the current docs-only image/video research PR after CI; verify its
post-merge CI. Then design one synthetic visual storyboard and inspect the
existing local evaluation tooling for a secret-safe image/video path. Before
any paid request, verify model-specific terms and processing, prepare an exact
offline cost estimate with bounded variants/retries, and ensure the evaluation
fits the previously approved cap. Do not check OpenRouter balance or account
settings. Keep any trial output local, review-only, and outside product routes.
Preserve USD 0.00078075 until the earlier GPT request's generation log is
matched.
