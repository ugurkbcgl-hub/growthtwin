# GrowthTwin — current handoff

Last verified: 2026-10-15 18:36 +0300 (Europe/Istanbul). Repository:
`https://github.com/ugurkbcgl-hub/growthtwin`.

## Objective

Build a self-service paid-advertising platform for Türkiye across industries.
Continue local product development with synthetic data; Phase 0 operational
checks remain pre-beta/production gates, not blockers for local UX work. No real
advertiser data, live ad accounts, publication, media spend, or production AI
use.

## Repository and CI state

- Current work is on `feat/progressive-campaign-detail-r10`, based on verified
  local `main`/`origin/main` commit `33fbac0186fa2d3eff515b79b21e453dc74d19e5`
  (PR #272). The pre-change main worktree was clean.
- PR #273, [progressive campaign review details](https://github.com/ugurkbcgl-hub/growthtwin/pull/273),
  is open from this branch. At 2026-10-15 18:36 +0300, required CI
  `Django system check` run `38761752773` was in progress; no merge decision has
  been made. The feature commit before this handoff update is `14c16e0`.
- This slice defines measurable synthetic usability criteria for R-10 and
  progressively discloses creative source/character metadata and deeper
  readiness/search details while leaving safety, eligibility, budget and
  unavailable-result facts visible. Source review and `git diff --check`
  passed; no tests ran. The local browser server on `127.0.0.1:8002` was
  unreachable, so no manual visual review or participant usability test was
  performed. No forms were submitted or database/provider/external account
  data touched.
- Verified `origin/main`: `33fbac0186fa2d3eff515b79b21e453dc74d19e5` (PR #272).
- PR #272 (`docs: refresh GrowthTwin current handoff`) merged at
  2026-10-15 18:14 +0300; its post-merge CI `38759064122` passed.
- PR #271 (`docs: refresh GrowthTwin data provenance handoff`) merged at
  2026-10-15 18:12 +0300. Required CI `38757852740` and post-merge CI
  `38758208720` passed, including Django tests and browser E2E.
- Earlier verification recorded `origin/main` as
  `7b939dab5ffb12ba968b922e8342fd5022a4cb47` (PR #271).
- PR #271 (`docs: refresh GrowthTwin data provenance handoff`) merged at
  2026-10-15 18:12 +0300. Required CI `38757852740` and post-merge CI
  `38758208720` passed, including Django tests and browser E2E. No PRs were
  open at this verification.
- PR #270 merged at 2026-10-07 19:51 +0300. Required CI `37654996009` and
  post-merge CI `37655317683` passed, including Django tests and browser E2E.
  The previous `docs/low-usage-handoff-20261013-1827` snapshot was clean
  before its handoff edits; recheck delivery state before acting.
- PR #269 merged at 2026-10-07 06:52 +0300. Required CI run `37568618655`
  and post-merge CI `37568776587` passed, including Django tests and browser
  E2E.
- PR #268 merged at 2026-10-05 19:09 +0300. Required CI runs
  `37331142933` and `37331246980`, and post-merge CI `37338587867` passed,
  including Django tests and browser E2E.
- PR #267 (`docs: refresh low-usage GrowthTwin handoff`) merged at
  2026-10-05 01:03 +0300. Required CI `37238412605` and post-merge CI
  `37238542795` passed, including Django tests and browser E2E.
- PR #256 required CI `37214462925` and post-merge CI `37214622803` passed.
  PR #257 required CI `37214916337` and post-merge CI `37215065615` passed.
  PR #258 required CI `37215352318` and post-merge CI `37215534053` passed.
  PR #259 required CI `37215728911` and post-merge CI `37215872411` passed.
  PR #260 required CI `37230669981` and post-merge CI `37230830736` passed.
  PR #261 required CI `37231049330` and post-merge CI `37231211050` passed.
- PR #263 merged as `1f17927`; required CI `37234341834` and post-merge CI
  `37234496365` passed. PR #264 refreshed this state; required CI
  `37234728688` and post-merge CI `37234918113` passed, including Django
  tests and browser E2E.
- PR #265 (`fix/openrouter-image-media-type`) merged as `183df04`; required CI
  `37236726475` and post-merge CI `37236885525` passed, including Django tests
  and browser E2E. Local Ruff lint/format and `git diff --check` passed. Never
  push directly to `main`.
- PR #266 merged as `986aab894cdb728744026292e661d0d0d3908f8d`; required CI
  `37237129966` and post-merge CI `37237255078` passed. At the earlier
  verification, the working tree was clean and no PRs were open.
- On 2026-10-15, `origin/main` still resolved to
  `9ff9664764fcd3457aa156bc96a76ae9672850a`; GitHub reported no open PRs.
  Latest main CI run `37655317683` succeeded. Main branch protection remains
  enabled, strict, and requires `Django system check`.

## AI/provider status

- Synthetic text comparisons: GPT-6 Luna remains an offline review candidate
  with generic drafts; Gemini did not pass the comparative quality gate. No
  production provider is selected and no model is connected to product routes.
- The owner separately authorized two one-call synthetic image attempts using
  the pinned `google/gemini-3.1-flash-lite-image` /
  `google-vertex/global` route. Matching OpenRouter Logs entries show both
  completed and were charged USD 0.0336 each; the local runner saved neither
  image. Their exact MIME type and precise historical rejection point remain
  unavailable. PR #265 removes the PNG-only assumption: the runner validates
  PNG, JPEG, and WebP signatures against optional `media_type` and saves the
  matching extension. No retry or new provider request was made. PR #258
  ensures failures save only safe category/status, without response body or
  secret.
- Reconciled the two image reservations against the matching visible provider
  costs. Local ledger now records USD 0.12744185 spent and USD 0.00078075
  reserved for the unresolved earlier GPT call. These are local ledger
  amounts, not the provider account balance.
- The owner checks the OpenRouter account balance; it was not inspected. No
  top-up, auto-recharge, privacy-setting change, or real-data use occurred.
- PR #263 separates safe response failure categories, including missing usage
  cost, malformed JSON/shape, missing image data and HTTP errors. PR #265
  removes the PNG-only assumption based on the Image API's documented
  `media_type` and PNG/JPEG/WebP outputs. It has not been tested against a new
  provider request.
- OpenRouter video remains excluded because its async video API is not
  ZDR-eligible.

## Risks and boundaries

Use synthetic cases only. Small evaluations do not establish general safety,
legal compliance, rights clearance, or production quality. `zdr=true` and
`data_collection=deny` do not establish Türkiye/EU processing or KVKK
compliance. Do not store credentials or provider output in Git. Do not inspect
provider balance, retry billable calls, buy credits, change privacy settings,
or use real data without applicable authorization.

## Next action

Check PR #273's required CI. If it passes, complete review and merge under the
owner's standing authorization; if it fails, fix only the blocking issue. Then
reopen the local synthetic campaign screen for visual review and prepare the
R-10 beginner/pro task script for participant usability observation. Do not
add real-data intake, live forecast, fee calculation, platform connection, or
publication. Keep configured-database recovery deferred: the
2026-10-15 authorized read-only inventory still could not establish provenance
for 8 legacy anonymous drafts, 1 workspace draft, or its creative version.
Do not edit, export, back up, or restore that database. No OpenRouter call or
balance check was needed; the owner remains responsible for balance checks,
and any billable evaluation must stay synthetic and within previously approved
limits. Do not connect AI to product routes or use OpenRouter video.
