# GrowthTwin — current handoff

Updated: 2026-10-18, Europe/Istanbul.

## Objective

Self-service advertising for Türkiye across industries. Current slice is an
isolated Google authorization flow, not live publishing or a beta launch.

## Repository

Base main `6dfabe1` (PR #281 merged; post-merge CI success verified).
Current branch `feat/local-google-oauth-connection`; this snapshot precedes its
commit/PR, so recheck live Git and CI. No existing database was modified.

## Completed locally

- Status/start/callback/disconnect routes, disabled by default; explicit owner
  and workspace, loopback-only, DEBUG off, CSRF on POST actions.
- Existing state/PKCE boundary now connects to fixed Google token endpoints;
  token storage uses Windows user-scoped DPAPI outside Git. Disconnect revokes
  before deleting locally. No Ads API or publishing transport exists.
- Real stored client could be decrypted/validated without revealing values.
  Separate fabricated Windows encryption/write/read round-trip passed.
- 31 focused synthetic tests and Ruff checks passed locally. Unit-test network
  and storage were mocked. No real OAuth exchange/revocation was attempted.
- Final delegated follow-ups were interrupted by agent credit errors; primary
  agent reviewed the files and reran focused verification.

## Google setup

October 17: test manager/child, Cloud Test API access, OAuth External/Testing
web client and one owner test user verified. Redirect URI remains unregistered;
no Google grant or refresh token verified. Developer tokens are no longer a
prerequisite under current Google guidance. See
[test connection readiness](../product/google-ads-test-account-readiness.md).

## Risks

Single isolated Windows process only. No staging/proxy/multiworker activation.
OAuth scope is broad; do not confuse stored authorization with verified test
account routing. Credential IDs must not be reused for another synthetic
owner/database. Proxy logging and production secret storage are not implemented.
Legacy database provenance/recovery and real participant usability remain open.
Real advertiser data, live campaigns and media spend remain behind release gates.

## Next action

Prepare an isolated synthetic local instance, review the new connection screen,
then register its exact callback in Google and obtain an explicit account grant.
Verify encrypted save before making a separately scoped test-account API read.
