# GrowthTwin — current handoff

Last verified: 2026-10-03 23:11 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Product runtime and AI quality must not depend on the owner's
local PC/GPU. Continue synthetic development; no real advertiser data, live
ad accounts, publication, media spend, or production AI use.

## Repository and PR state

- `main` is clean at `bd6eb4c9dbe0931093887c6bd06d662858c457da`.
- PR #231 merged. Required PR CI `37149972884` and post-merge main CI
  `37150107533` passed, including Django tests and browser E2E. No open PRs
  were returned at the latest check. PR #232 refreshed this handoff; its
  required CI `37150316060` and post-merge main CI `37150467156` also passed.

## AI and product status

- The website remains deterministic. No AI provider is connected to a user
  route and no production provider is selected. Ollama is an optional local
  experiment; its recent synthetic candidates failed the small creative gate.
- PR #231 added an opt-in OpenAI GPT-6 Luna text adapter and fixed synthetic
  runner: three briefs × three calls, up to 512 output tokens, fixed request
  size, no tools/retries, and `store: false`. It remains disconnected from
  routes. It reports only non-publishable drafts and requires human review.
- A shared local SQLite ledger reserves call cost before dispatch and caps the
  local allocation at USD 4.50, leaving USD 0.50 headroom inside the owner's
  approved USD 5 total. Never automatically replenish or reset the ledger.
  The operator-confirmation environment flag does not prove account settings.
- One synthetic run is estimated to reserve at most USD 0.005425. Estimate
  mode, Ruff checks, `git diff --check`, and 30 focused AI gateway tests passed.
  PR and post-merge CI passed. No hosted API request was made and no AI cost was
  incurred; `OPENAI_API_KEY` was absent.
- Before any API call, set up an isolated OpenAI API project with a verified
  USD 5 monthly hard spend limit, no other traffic or existing project usage,
  and securely provide its key as `OPENAI_API_KEY`. OpenAI states that hard
  limit enforcement can lag and spend can slightly exceed the configured
  amount; the local USD 4.50 ledger is a separate safeguard, not an absolute
  bill guarantee. GPT-6 Luna's free tier is listed as unsupported.
- OpenAI's default abuse-monitoring may retain prompts/responses up to 30 days.
  `store: false` does not change that. Keep all evaluation inputs synthetic.

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

After the owner establishes and verifies the isolated OpenAI project hard cap
and securely configures its API key, run the fixed synthetic text evaluation
with `apps/web/scripts/evaluate_openai_synthetic.py`; stop at the local USD
4.50 allocation and review quality and cumulative provider usage before any
further paid candidate.
