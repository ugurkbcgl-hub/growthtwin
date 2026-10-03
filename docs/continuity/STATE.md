# GrowthTwin — current handoff

Last verified: 2026-10-03 22:23 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a polished, self-service paid-advertising platform for Türkiye across
industries. Product runtime and AI quality must not depend on the owner's
local PC/GPU. Develop with synthetic data; no real advertiser data, live ad
accounts, publication, media spend, or unapproved paid infrastructure.

## Repository and PR state

- `main` was verified clean at
  `45ce42a1c576463d8d743a9f88dd32cde3035991`. PRs #227 and #228 merged; PR
  checks and post-merge CI passed (`37146525709`, `37146671062`,
  `37146841173`, `37146984437`). No open PRs at the last check.
- Current work is on `feat/credential-free-ai-benchmarks`, created from that
  verified `main`. Branch changes and PR/CI are not yet submitted at this
  snapshot.

## AI and product status

- Website generation remains deterministic. The provider-neutral gateway has
  a text creative contract; Ollama is optional and disconnected from routes.
  Recent Qwen3 evaluations failed the small creative gate. No production
  provider is selected.
- PRs #227/#228 documented a hosted, task-routed candidate strategy: OpenAI,
  Gemini/Vertex AI, and Anthropic for text; Google and OpenAI for image/video.
  This shortlist does not authorize provider accounts, credentials, paid API
  calls, or processing real data.
- Current branch adds a versioned text task profile and bounded synthetic
  benchmark harness accepting caller-supplied `CreativeGenerator` adapters.
  It does not create adapters, read credentials, call the network, persist
  output, or connect to web routes. The optional Ollama CLI is refactored to
  use the same interface. Ruff lint/format and `git diff --check` passed;
  application tests were not run locally.
- The benchmark checks only output-contract failures and exact fixture phrases;
  manual source-grounding, usefulness, diversity, brand-fit, and correction
  review remain necessary. No candidate was evaluated in this refactor.
- Existing approximately USD 12 Heroku approval does not cover AI provider
  charges. A separate bounded budget is required before billable comparison.

## Risks and gates

- Provider/model IDs, availability, prices, terms, retention, and processing
  regions change. Recheck current official terms before use. Prior source review
  is not a KVKK assessment or Türkiye-only processing guarantee.
- Do not connect provider calls to user routes or process real advertiser
  assets before data and privacy readiness. A model or second-model critique
  does not authorize claims, policy clearance, publication, or spend.
- Image/video integrations, customer-file intake, account connection,
  publication, and production deployment remain outside this work.

## Next action

Review and merge this benchmark PR after required CI passes. Then prepare a
provider-by-provider cost estimate for the fixed synthetic text suite and a
hard spend cap; ask for budget approval before any billable API comparison.
Keep the website on deterministic templates and image/video work deferred.
