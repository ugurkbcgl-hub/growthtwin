# GrowthTwin — current handoff

Verified: 2026-10-19, Europe/Istanbul.

## Objective

Self-service advertising for Türkiye across industries. Continue from verified
Google test integration toward immutable draft-to-platform dispatch; live
advertiser data, serving and spend remain separately gated.

## Repository and checks

Base main: 626cb8b, PR #284 merged after successful CI.
Current branch: feat/google-paused-test-campaign; this note precedes its own
commit/PR. Recheck Git/CI before continuing. 52 focused local tests, Ruff and
migration consistency passed. Live browser create/read/stop passed.

## Verified implementation

Google OAuth grant is encrypted outside Git with Windows DPAPI. Explicit local
test target read/verification works. The connection screen now supports a fixed
synthetic Search test campaign behind a separate opt-in flag. Budget, campaign,
ad group, exact keyword and responsive search ad are created atomically with
partial failure disabled; statuses PAUSED, virtual daily budget one account unit.

One durable workspace intent is committed before a real create. Uncertain
responses cannot trigger a second create, including after restart. Read reconciles
the exact operation and budget resource. The first real request succeeded but
budget naming differed from expectation; reader corrected and recovered the
same record. Stop and repeated-create readback confirmed the same PAUSED record.
No actual serving or media spend; user-authorized Google test objects remain.

Migration 0006 applied ONLY to the existing isolated synthetic review database.
Preserve that DB, owner/workspace, encrypted grant and ledger. No legacy/Heroku
DB migration or data inspection. The active local server uses the preserved
review bootstrap, not the older fresh-database bootstrap.

## Limits

Single isolated Windows process, DEBUG off, loopback, explicit identity/targets;
local OAuth and test mutation flags default off. No ENABLED mutation path.
The fixed test is separate from fake campaign rehearsal; arbitrary workspace
creative dispatch is not implemented. See ADR-0022 and the current Google test
integration checklist. Recovery, legal/privacy and production gates remain open.

## Next action

Bind a current owner-selected synthetic workspace draft to an immutable Google
Search payload and explicit test-dispatch consent, reusing the verified target,
durable idempotency and pause/readback protections. Do not enable real accounts,
live serving, advertiser data or media spend.
