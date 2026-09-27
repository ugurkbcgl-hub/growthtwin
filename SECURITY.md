# Security baseline

## Repository and credentials
- This is a public repository. Never commit API keys, passwords, tokens, OAuth client secrets, private keys, `.env` files, or real customer data.
- The NVIDIA Build key shown in the supplied screenshot was replaced by the user. Keep the replacement in a local environment variable or deployment secret store; never paste or print it.
- Keep `.env.example` limited to variable names and safe placeholders. Rotate any credential suspected of exposure and remove it from the provider account.
- Separate development, staging, and production credentials and data stores.

## Tenant and account boundaries
- Every clinic-owned record and file must be scoped to a workspace/tenant.
- Enforce tenant membership and role authorization on the server for every read and write; do not trust tenant IDs supplied by the browser.
- Keep an auditable record of important account, approval, and publishing actions without recording credentials or sensitive content in logs.
- Store social-platform tokens as secrets, encrypt them at rest, limit their scope, and support revocation. Do not expose them to the browser or AI providers.

## AI and data handling
- Use synthetic data with hosted free/trial endpoints. Do not send patient, clinic, lead, Instagram account, unpublished campaign, or other customer data to them.
- NVIDIA Build/NIM hosted trial endpoints are for evaluation and development only; they must not serve GrowthTwin end users.
- Check provider terms, model licenses, data retention, rate limits, and commercial-use permissions before enabling a provider. Keep providers behind the application AI gateway.
- Treat generated text and media as untrusted drafts. Require an authorized human approval before publishing or taking an external action.

## Operations
- Use separate development, staging, and production configurations and permissions.
- Do not modify production systems manually. Production changes require an approved pipeline, a verified backup, health checks, and a tested rollback path.
- Log request IDs and operational metadata, not secrets, access tokens, patient data, or unnecessary content.
