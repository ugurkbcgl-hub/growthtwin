# GrowthTwin — current handoff

Last verified: 2026-10-03 22:32 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Product runtime and AI quality must not depend on the owner's
local PC/GPU. Develop with synthetic data; no real advertiser data, live ad
accounts, publication, media spend, or unapproved paid infrastructure.

## Repository and PR state

- `main` was verified clean at
  `fb2fa9a3faed12de3a02945e1ca0af68e85e599b`. PR #229 merged; required PR CI
  `37147927261` and post-merge main CI `37148068356` passed, including Django
  tests and browser E2E. No open PRs were returned at the last check.
- The current documentation-only state refresh is on
  `docs/refresh-ai-benchmark-handoff`, created from that verified main commit.
  Recheck its live PR/CI status before continuing.

## AI and product status

- Website generation remains deterministic. The provider-neutral gateway has
  a text creative contract; Ollama is optional and disconnected from routes.
  Recent Qwen3 evaluations failed the small creative gate. No production
  provider is selected.
- PRs #227/#228 documented a task-routed hosted shortlist: OpenAI,
  Gemini/Vertex AI, and Anthropic for text; Google and OpenAI for image/video.
  This is not permission to activate accounts, credentials, paid API calls, or
  process real data.
- PR #229 added `creative-copy-v1`, a bounded provider-neutral benchmark
  interface, and refactored the local Ollama runner to use it. It accepts
  caller-supplied adapters; the harness itself does not create providers, read
  credentials, call the network, persist results, or connect to routes. It
  caps a run at 60 calls and records structured status, latency, exact fixture
  phrase screens, manual score fields, and non-publishable draft output.
- Local Ruff lint/format and `git diff --check` passed. No model benchmark or
  application tests were run locally; required PR and post-merge CI passed.
  The harness's exact phrase check is not semantic claim or policy validation.
- Heroku's approximately USD 12 approval does not cover provider charges. No
  AI provider cost has been approved or incurred.

## Risks and gates

- Provider/model IDs, prices, terms, retention, availability, and processing
  regions change. Recheck official vendor materials before use. Existing
  research is not a KVKK assessment or Türkiye-only processing guarantee.
- Hosted evaluation must use synthetic cases and a hard approved spend limit.
  Do not connect provider calls to user routes or send real advertiser assets
  before the applicable privacy/data gates are met.
- Image/video integrations, customer-file intake, live account connection,
  publication, media spend, and production deployment remain out of scope.

## Next action

Prepare a provider-by-provider cost estimate for the fixed synthetic text
benchmark and propose a hard evaluation cap. Recheck current official prices,
model availability, and data terms; do not make billable calls until that
bounded budget is approved. Keep image/video and real-data paths deferred.
