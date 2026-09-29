# GrowthTwin — current handoff

Last repository verification: 2026-09-29 08:56 (Europe/Istanbul). Repository: `https://github.com/ugurkbcgl-hub/growthtwin`. PR #82 (`849467f`) is merged; its required CI and post-merge CI both passed. Current documentation branch: `docs/validation-accessibility-handoff`; changes are pending review. The working tree was clean on `main` and there were no open PRs before this docs update.

## Goal and working rules

- Türkiye is the target market. GrowthTwin serves people and organizations that want to advertise; clinics are one example. Omneky is a long-term breadth benchmark, not a first-release parity promise.
- Local synthetic-data product development is authorized. Keep using the existing Django/PostgreSQL app and CI; use branches and PRs, never push directly to `main`.
- Advertisers must authorize connected accounts and define enforceable spend, schedule, and content limits before live actions. Pause when information or permission is unclear.
- Keep local, CI, and staging examples synthetic. Do not expose secrets or private advertiser data.
- Do not add paid services or enable live publishing/spend without authorization. The owner explicitly requested a read-only Heroku Scheduler check on 2026-09-29; no run was triggered and no settings were changed.

## Current product state

- Local prototype demonstrates synthetic brief → preview → simulated pause → sample report. Drafts remain session-scoped and synthetic.
- PR #51 (`15fda3a`) corrected stale README and roadmap status. Required CI `36422821769` and post-merge CI `36423011388` passed.
- PR #52 (`a3e1d22`) added three deterministic, editable copy starting points from the saved brief, brand/product context, and optional audience. No AI, account integration, publishing, or spend. Required CI `36424389194` and post-merge CI `36424605181` passed.
- PR #54 (`a9be467`) improved the information-focused fallback when brand context is absent. Required CI `36472843404` and post-merge CI `36473065414` passed.
- Manual local browser review with synthetic campaign data verified layout, editing, save feedback, regeneration feedback, and saved-value persistence. A missing local migration was applied during that review; local Ruff was unavailable, while CI formatting/lint passed.
- PR #56 (`f799426`) stopped the audience-focused variant from appending “Detayları incele” to the brief when no audience is given; the CTA remains separate. Three focused local tests passed, and the browser confirmed the no-brand/no-audience brief stays unchanged in the audience- and information-focused bodies. Required CI `36474994196` and post-merge CI `36475232546` passed.
- PR #58 (`a978014`) clarified that these are synthetic, editable starting points; when brand or audience context is missing, the brief may be shown unchanged and should be edited and checked before publication. The note is more readable. Four focused local tests and browser review passed. A database-backed local test was unavailable because the local PostgreSQL role cannot create test databases; the focused UI test uses no database, and CI ran the full Django suite. Required CI `36478847264` and post-merge CI `36479049872` passed.
- Comparing five synthetic inputs found that the audience- and information-focused variants could omit the offer when both brand and audience were supplied. PR #60 (`52e93e3`) keeps the brief content in those bodies, includes a shortened audience in the audience-focused body, and keeps the brand in the headline. Five focused local tests and the full CI suite passed; required CI `36483491236` and post-merge CI `36483681415` passed.
- Long synthetic briefs exposed that simple end truncation could remove an offer or audience detail placed near the end. PR #62 (`af83c57`) keeps beginning and ending context in bounded headline/body fields; seven focused local tests and browser inspection at 390px confirmed offer, audience, and brand-tail details remain in bounded fields. PR CI `36484889021` and post-merge CI `36485086542` passed.
- PR #65 (`b0a4d80`) fixed a 7px horizontal overflow caused by decorative studio glow at 390px and a 3px overflow at 1024px. A Chromium sweep at 320, 360, 390, 430, 600, 768, 820, 1024, 1030, and 1280px found no remaining horizontal overflow; manual 390px review covered brief, preview, and sample report. PR CI `36486720468` and post-merge CI `36486952363` passed.
- PR #66 (`eb4d686`) added a mobile Chromium regression check for the brief → preview → sample report flow and made the E2E suite run explicitly in CI. The focused browser test passed locally; PR CI `36487628405` and post-merge CI `36487818391` passed.
- Mobile browser review at 390px confirmed that an empty brief is stopped by the required field, the optional brand/audience disclosure opens with the keyboard, and budget limits accept 100 and 100,000 while rejecting 99 and 100,001. No further field-validation issue was observed; no code change was needed.
- At 390px, all six campaign form controls have unique accessible labels, the brief exposes its required state, and the flow status is announced through a polite live region. No naming or status issue was observed in the brief step.
- The preview editor exposes labeled text fields and named save/regenerate actions; the report is a named region with a heading and readable metric labels and values. PR #70 (`bdc4ca1`) fixed the pause/resume button's conflicting action name and `aria-pressed` state, and added a browser check for its changing accessible name and polite pause announcement. Focused local browser E2E, PR CI `36490407579`, and post-merge CI `36490586669` passed.
- PR #72 (`e5c8dea`) extended the mobile browser E2E to open a creative variant with the keyboard, verify its labeled field, save synthetic copy and check the status message and persisted value, then regenerate and check its status message. The focused local E2E passed; PR CI `36492742189` and post-merge CI `36492925328` passed. No accessibility behavior gap was found, so this change adds regression coverage only.
- PR #73 (`35c56e0`) refreshed this handoff with PR #72's verified results and set the next action to review invalid creative-copy validation accessibility. PR CI `36493159093` and post-merge CI `36493316954` passed.
- PR #75 (`577de64`) opened creative variants containing validation errors, connected each invalid field to its error text, and focused the first invalid field after the server response. Its mobile E2E covers the closed-variant invalid-submission case using synthetic content. Local focused E2E, PR CI `36495232468`, and post-merge CI `36495382212` passed.
- PR #77 (`d282277`) associates campaign brief form errors with fields, marks invalid controls, focuses the first invalid visible field, and opens the optional brand/audience disclosure when it contains errors. The mobile E2E covers synthetic invalid brief and overlong optional brand submissions; focused local E2E, PR CI `36496415009`, and post-merge CI `36496565902` passed.
- PR #79 (`0735aa5`) extends the mobile E2E with keyboard-only correction after invalid submissions: Tab navigation, Space to open optional details, returning focus to the invalid field, and Enter to reach preview. A load-event focus fallback was needed for consistent Chromium behavior. Focused local E2E, PR CI `36498106247`, and post-merge CI `36498250268` passed.
- Budget and duration server-side validation review used synthetic out-of-range budgets (99 and 100001) and an unsupported duration (21 days). Each error was connected to its field and focus moved to that invalid field; no product behavior fix was needed. PR #82 (`849467f`) adds a mobile E2E regression check. The focused local browser test passed using in-memory SQLite. Local Ruff was unavailable; PR CI `36528220737` and post-merge CI `36528406419` passed, including formatting, lint, Django tests, and browser E2E.
- Copy remains deterministic and provider-free. It is an editable starting point, not an AI-generated or publish-ready ad.

## Open decisions and gates

- Select the first advertiser workflow and publishing destination only after validating user need and Türkiye-specific platform eligibility, approval, policy, and reporting.
- Define advertiser consent, spend caps, review/autonomy defaults, and stop conditions before live publishing or spend.
- Session drafts are synthetic. Verify retention/deletion before accepting real advertiser data; staging E2E, backup/restore, and rollback remain external-beta/production gates.
- Heroku Scheduler's first run is verified: dashboard Last Run was 2026-09-29 00:00 UTC, Next Due was 2026-09-30 00:00 UTC, and application logs showed `python manage.py clearsessions` exited with status 0 at 00:00:11 UTC. Actual billed one-off dyno usage remains unverified. Keep staging data synthetic; this best-effort run is not a real-data retention guarantee.
- AI/provider selection and production data-processing terms remain undecided. Recheck provider terms before using an external provider.

## Next action

Review the brief-to-preview experience against the product goal: check whether daily and total budget boundaries, selected duration, and the simulated nature of preview/results are clear without extra explanation; fix only demonstrated comprehension or accessibility gaps using synthetic examples.
