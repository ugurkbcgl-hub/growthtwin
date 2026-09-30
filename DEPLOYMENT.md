# Deployment and environment policy

Status: the owner approved one Heroku staging app for the Phase 0 synthetic demo, at an observed estimate of about USD 12/month before tax. There is no production deployment. Local product UX work is the current focus.

## Environments

- **Local development:** synthetic data, current Windows checkout, local Django/PostgreSQL, and locally protected secrets. This is the primary place to build the website and validate campaign UX.
- **Staging:** isolated config and synthetic/demo data only. The approved Heroku app is for release-readiness checks; do not connect real advertiser accounts, run live campaigns, or serve end users from it.
- **Production:** separate credentials, data, permissions, observability, and a reviewed pipeline. No production service is selected or authorized.

Do not copy production data into development or staging. Promotion must never carry credentials across environment boundaries.

## Deployment controls

- Build versioned artifacts from reviewed source and deploy through a controlled pipeline; do not edit production files or databases manually.
- Keep environment configuration in the relevant secret store. Grant the smallest required permissions and make connection revocation possible.
- Expose health/readiness and deployed revision. Log operational metadata without secrets or unnecessary advertiser content.
- Before external beta or production, verify a recoverable backup, health check, monitoring, emergency stop, and practical rollback. Record schema-change recovery order.
- Publishing and spend-affecting actions must pass the current advertiser authorization and limit checks in application code. A staging deployment must never be treated as permission to spend.

## Cost and provider controls

- The project reference sets a working cap of USD 100/month, a warning near USD 80/month, and user approval for a single spend above USD 20.
- Estimate recurring and one-time charges before enabling a service; record an owner, expected cost, and shutdown path.
- The Phase 0 approval covers one Heroku Basic web dyno and one Essential-0 PostgreSQL database, observed near USD 12/month before tax. It does not authorize add-ons, more dynos, production hosting, or paid AI. Delete the app and database when staging is no longer needed.
- No production AI provider, cloud host, queue, object storage, or paid integration is selected. Do not add paid resources without a new owner decision.
- NVIDIA Build/NIM trial endpoints are only for synthetic development/evaluation and cannot serve GrowthTwin end users.

## Heroku Phase 0 staging snapshot

- App: `growthtwin-stage-270927` at `https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com/`.
- Last dashboard observation recorded at 2026-09-27 20:06 Europe/Istanbul: one Basic web dyno (~USD 0.010/hour) and one Essential-0 PostgreSQL add-on (~USD 0.007/hour); dashboard estimate about USD 12/month.
- At that observation the latest deployed code revision was `ac2f627d`; later releases were configuration changes. Current `main` at `6aba41e` was not deployed. Recheck the dashboard before deploying because it can change.
- A direct request to `/health/?check=20260927-followup-01` returned HTTP 200 and `{"status":"ok","version":"unknown"}`. Database readiness responded, but the app did not identify its revision. An in-app browser request was blocked by the client, so that browser path remains unverified.
- The synthetic profile-edit E2E passes locally and in CI but has not run against this staging deployment. No disposable staging account has been provisioned. Backup/restore and rollback are also unverified.
- Keep only synthetic values in the staging app and its database. Do not expose or copy config-var secrets. No extra paid dyno or service is approved for account provisioning.

## Current readiness review (2026-09-30)

- A read-only GET to the staging health endpoint returned HTTP 200 with database-ready status, but `version` was `unknown`; the deployed revision is not verified.
- The pinned staging profile-edit E2E runner is ready, but no run against staging is recorded and a disposable test account is not verified. CI E2E is not a substitute for this check.
- Heroku CLI is not installed in the reviewed workspace. Current app releases, resource configuration, and billing/Scheduler charges were not rechecked; the snapshot above is historical.
- Backup/restore and rollback remain unverified. Do not restore over the only database or add a separate resource as part of this review.
- See the [Phase 0 staging verification sequence](docs/phase-0-staging-verification.md) for prerequisites, safe stop points, and pass evidence.

## Rollout gates

- Local website prototype: no deployment required; use synthetic examples and local verification.
- External beta: complete staging E2E, backup/restore, rollback, CI merge-gate check, security/privacy review, and selected platform integration tests first.
- Production: requires separate owner approval for provider, recurring costs, advertiser-spend authority, monitoring, support, and data-retention arrangements.
