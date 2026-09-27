# Deployment and environment policy

Status: Heroku has been provisioned for staging with the owner's approval for about USD 12/month before taxes. Production hosting is out of scope.

## Environments

- **Local development:** synthetic data; local-only secrets; convenient iteration.
- **Staging:** isolated configuration and synthetic/demo data; verifies deployment and integration behavior. Do not connect real clinic accounts or use trial AI endpoints with customer data.
- **Production:** separate secrets, data, permissions, and deployment pipeline. No production service is part of the current phase.

Do not copy production data into development or staging. Promotion between environments must not carry credentials across environment boundaries.

## Deployment controls

- Build a versioned artifact from reviewed source and deploy through CI/CD; do not change production files or databases manually.
- Keep environment configuration external to source. Grant the smallest required permissions and rotate credentials through the provider's secret store.
- Expose health/readiness checks and the deployed revision. Collect logs and operational metrics without secrets or sensitive user content.
- Before a production release, verify a recoverable backup, a health check, and a practical rollback path. Record schema changes and recovery order.
- Use staged rollout and explicit approval for production changes once production exists.

## Cost and provider controls

- The project reference sets a working ceiling of USD 100/month, a warning near USD 80/month, and user approval for a single spend above USD 20. Confirm the current cap before provisioning.
- Estimate recurring and one-time charges before enabling a service. Keep an owner, expected monthly cost, and shutdown path for each resource.
- For Phase 0 staging only, the owner approved one Heroku Basic web dyno and one Essential-0 PostgreSQL database, about USD 12/month before taxes. Use PostgreSQL 18, add no paid add-ons or additional dynos, and delete the app and database after M4 acceptance. This does not authorize production hosting or additional recurring services.
- NVIDIA Build/NIM trial endpoints are limited to development/evaluation under their terms and are not a production deployment option.
- No cloud, queue, object storage, or paid AI provider is selected by this policy; Heroku is the sole approved Phase 0 staging exception.

## Heroku Phase 0 staging

- On 2026-09-27, Heroku app `growthtwin-stage-270927` was deployed from connected repository `ugurkbcgl-hub/growthtwin`, branch `main`, revision `ac2f627`. PR #17 later advanced `main` to `f2973b6`; whether Heroku has deployed that newer commit has not been checked. App URL: https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com/.
- Resources showed one Basic web dyno and one Essential-0 PostgreSQL database; estimated monthly cost was about USD 12 before taxes. No additional paid resource was shown.
- Heroku reported a successful deployment and release phase; the release command applies migrations. A direct PowerShell `GET /health/?check=20260927-followup-01` returned HTTP 200 with `{"status": "ok", "version": "unknown"}`. This confirms database readiness, but the revision signal is missing. The earlier browser tab retained a `400` page after blocked navigation; browser-visible behavior has not been rechecked.
- Deploy only the synthetic demo. Keep `DJANGO_SECRET_KEY` in Heroku config vars; the attached database supplies `DATABASE_URL`. Never copy either secret value into source, documentation, chat, or logs.
- Pin Python to 3.13, serve Django with Gunicorn and WhiteNoise, and run migrations in the Heroku release phase.
- Set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to the selected `*.herokuapp.com` hostname. Enable secure cookies and HTTPS redirection behind Heroku's proxy, with one-hour HSTS (`DJANGO_SECURE_HSTS_SECONDS=3600`). Keep HSTS limited to this hostname; do not enable `includeSubDomains` or preload for the staging app.
- Expose `/health/` for readiness and deployed revision. Verify the endpoint, profile-edit path, backups, and rollback before M4 acceptance.
- PR #17 merged as `f2973b6`; its Playwright path passes locally and in CI, but has not run against staging. The app has no public signup or Django admin route, so no disposable staging account exists yet. Use synthetic values only and do not log or commit credentials.
- Backup/restore and rollback remain unverified. Do not provision an additional paid dyno or service beyond the approved Basic dyno and Essential-0 database without a new approval.

## Phase 0 rollout

M2 resolves the bootstrap host and cost limits. M3 establishes stack-appropriate CI. M4 deploys only the synthetic demo after a staging provider and budget are accepted; its E2E and recovery checks are still pending. M5 verifies CI failure blocking, rollback, and records the results. Production deployment remains out of scope.
