# Deployment and environment policy

Status: Phase 0 policy. No hosting provider, staging service, or recurring spend has been selected or enabled.

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
- NVIDIA Build/NIM trial endpoints are limited to development/evaluation under their terms and are not a production deployment option.
- No cloud, database, queue, object storage, or paid AI provider is selected by this policy.

## Phase 0 rollout

M2 resolves the bootstrap host and cost limits. M3 establishes stack-appropriate CI. M4 may deploy only the synthetic demo after a staging provider and budget are accepted. M5 verifies health, backup/restore, rollback, and records the results. Production deployment remains out of scope.
