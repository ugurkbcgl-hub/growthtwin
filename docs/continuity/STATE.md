# GrowthTwin — current handoff

Last verified: 2026-10-17 14:43 +03:00 (Europe/Istanbul).
Repository: https://github.com/ugurkbcgl-hub/growthtwin

## Objective

Self-service paid advertising for Türkiye across industries: brief, creative,
plan, authorized publishing and reporting. Current work prepares Google test
account integration; live campaigns and real advertiser data remain gated.

## Repository and checks

- Base main: `1038a8e` (merged PR #280); post-merge CI `38956701478` passed.
- Working branch: `feat/google-oauth-safety-foundation`. This snapshot precedes
  its commit/PR; recheck live Git and CI before continuing.
- Offline OAuth foundation added: fixed loopback callback constant, PKCE S256,
  five-minute random state, owner/workspace/session binding and atomic one-time
  consumption in a bounded single-process store. No HTTP route or transport yet.
- Ten focused local synthetic tests passed; formatting/lint passed. Independent
  review caught slashless callback logging leakage; filter and regression case
  updated. Recheck final PR CI. No external API or existing database was touched.
- Prior PR #279 delivered owner-scoped synthetic start/fail/retry/stop rehearsal;
  this remains a fake adapter, not a live advertisement. Existing-database
  migration/recovery status has not been changed or reverified.

## Google setup observed October 17

Dedicated test manager/child and Cloud project exist; child had zero campaigns.
Google Ads API enabled, Cloud access Test. OAuth External/Testing, web client
created, one owner test user saved and visibly verified. Redirect URIs still
empty; no account grant or refresh token. Client credentials encrypted outside
Git with Windows DPAPI and verified by the writer process; subsequent folder
rename failed. Django credential access is unverified. Do not print secrets.

Google's current guide sunsets developer tokens; use Cloud project access,
not a new production manager/token application. See the updated
[test integration checklist](../product/google-ads-test-account-readiness.md).

## Risks and boundaries

No live account connection, publication, spend or real metrics. OAuth adwords
scope is broad; enforce test targets separately. The new memory store is not
multiworker-safe. Django log filtering does not cover upstream proxy logs or
DEBUG pages. Legacy database provenance/recovery and participant usability
observations remain unresolved. Do not inspect/modify legacy data without a
defined authorized recovery plan.

## Next action

Implement the test-only Django start/callback routes and encrypted credential
store boundary using the offline OAuth primitive, then verify locally before
registering its exact redirect URI in Google. Enforce authenticated ownership,
CSRF start, DEBUG off, sanitized callback responses/logs and no provider writes.
