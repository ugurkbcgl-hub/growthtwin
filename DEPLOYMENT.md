# Deployment and environment policy

Status: Phase 0. Heroku has been selected for staging, with the owner's approval for about USD 12/month before taxes. The app and database are not provisioned yet.

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
- For Phase 0 staging only, the owner approved one Heroku Basic web dyno ($7/month) and one Essential-0 PostgreSQL database ($5/month), about USD 12/month before taxes. Use PostgreSQL 18, add no paid add-ons or additional dynos, and delete the app and database after M4 acceptance. This does not authorize production hosting or additional recurring services.
- NVIDIA Build/NIM trial endpoints are limited to development/evaluation under their terms and are not a production deployment option.
- No cloud, queue, object storage, or paid AI provider is selected by this policy; Heroku is the sole approved Phase 0 staging exception.

## Heroku Phase 0 staging

- Deploy only the synthetic demo. Keep `DJANGO_SECRET_KEY` in Heroku config vars; the attached database supplies `DATABASE_URL`.
- Pin Python to 3.13, serve Django with Gunicorn and WhiteNoise, and run migrations in the Heroku release phase.
- Set `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to the selected `*.herokuapp.com` hostname. Enable secure cookies and HTTPS redirection behind Heroku's proxy, with one-hour HSTS (`DJANGO_SECURE_HSTS_SECONDS=3600`). Keep HSTS limited to this hostname; do not enable `includeSubDomains` or preload for the staging app.
- Expose `/health/` for readiness and deployed revision. Verify the endpoint, profile-edit path, backups, and rollback before M4 acceptance.
- Use the Heroku dashboard or CLI only after the owner account is authenticated. Do not copy or log credential values.

## Phase 0 rollout

M2 resolves the bootstrap host and cost limits. M3 establishes stack-appropriate CI. M4 may deploy only the synthetic demo after a staging provider and budget are accepted. M5 verifies health, backup/restore, rollback, and records the results. Production deployment remains out of scope.
