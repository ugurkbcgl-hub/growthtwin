# Google Ads test integration prerequisites

Reviewed: 2026-10-16, Europe/Istanbul. Scope: setup evidence only; no account
creation, credentials issued, API call, publication or spend performed.

## Verified local status

PR #279 adds an in-process synthetic rehearsal, not a Google Ads adapter.
The inspected process has no `GOOGLE_ADS_*` or `GOOGLE_CLIENT_*` variables.
Neither repository-root `.env` nor `apps/web/.env` exists. This limited check
does not establish that credentials or accounts do not exist elsewhere.
No personal credential stores, remote configuration or advertiser data were read.

| Prerequisite | Evidence still needed |
| --- | --- |
| Dedicated test manager and child client | Account owner and test-account status verified in Google Ads; no production account substituted |
| Developer token | Approved storage location and access availability, without displaying the value |
| Google Cloud project and OAuth credentials | Project identity, API setup, authentication approach and access to the dedicated test account |
| Test customer and manager routing | Correct test client and manager selected; identifiers kept out of public handoff notes |
| Credential handling | Storage, restricted access, revocation and sanitized errors established before integration |

All account-specific prerequisites remain **unverified**, not confirmed absent.

## Ordered implementation gate

1. Inspect the signed-in Google Ads and Cloud setup with the owner; record only
   readiness status. If sign-in is needed, the owner enters credentials directly.
2. Establish a separate test manager/client hierarchy and authorized API identity.
   Verify the Google Ads test label before any account operation.
3. Design a dedicated test-only configuration that rejects production targets,
   defaults to disabled and never falls back to another customer or credential.
4. Make the first narrowly scoped read-only request only after authentication and
   the target are verified. Then separately review a paused synthetic campaign
   creation/stop rehearsal. Record results without tokens or customer payloads.

The current official guidance requires a separate test hierarchy and permits
the Cloud project's OAuth credentials for test accounts. Test accounts neither
serve ads nor incur media charges; their empty serving metrics cannot validate
delivery or business results. Test setup does not close production launch gates.

## Official references checked

- [Test accounts](https://developers.google.com/google-ads/api/docs/best-practices/test-accounts)
- [OAuth overview](https://developers.google.com/google-ads/api/docs/oauth/overview)

The earlier [Türkiye feasibility assessment](google-ads-search-turkiye-api-feasibility.md)
remains dated research; recheck access rules before applying for production use.
