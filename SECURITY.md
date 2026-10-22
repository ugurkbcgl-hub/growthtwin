# Security baseline

## Repository and credentials

- This is a public repository. Never commit API keys, passwords, tokens, OAuth client secrets, private keys, `.env` files, or real advertiser data.
- Keep `.env.example` limited to variable names and safe placeholders. Rotate any credential suspected of exposure and remove it from the provider account.
- Separate development, staging, and production credentials and data stores.
- Store local credentials only in the approved user-protected secret store; use the deployment provider's secret store for that environment. Never print secret values.

## Advertiser and tenant boundaries

- Scope every advertiser-owned record, campaign, asset, platform connection, and report to its workspace/account.
- Enforce membership and role authorization on the server for every read and write; do not trust advertiser or tenant IDs supplied by the browser.
- Keep an auditable record of account changes, consent, automation settings, campaign state transitions, and external actions without recording credentials or unnecessary creative content in logs.
- Store social/ad platform tokens encrypted at rest, limit them to necessary scopes, keep them out of browser and AI access, and support revocation and deletion.

## User-authorized automation and spend

- Automation may act only inside the advertiser's explicit destination/account connection, content boundaries, schedule, and hard spend caps. Record what the advertiser authorized, when, and how it can be revoked.
- Never infer consent to connect an account, publish an ad, or spend money from a prompt alone. Require the appropriate platform OAuth flow and explicit advertiser setup for those capabilities.
- Enforce per-campaign and aggregate ceilings in application code and verify the current state immediately before every external spend-affecting action. Fail closed if a limit, permission, destination response, or currency conversion cannot be verified.
- AI output is untrusted input. It cannot set limits, bypass validators, mark its own output safe, access tokens, or call external APIs.
- Pause and notify the advertiser when required facts are missing, output or policy checks fail, platform behavior is ambiguous, or a configured limit is reached. Provide a prominent stop/revoke path.
- Routine campaigns should not require a GrowthTwin employee to approve each step. This does not remove advertiser consent, platform review, or the need to pause exceptional cases.

## AI and data handling

- Use synthetic data with hosted free/trial endpoints. Do not send private advertiser, lead, customer, or account data to them.
- NVIDIA Build/NIM hosted trial endpoints are for evaluation and development only; they must not serve GrowthTwin end users.
- Check provider terms, model licenses, retention, rate limits, and commercial-use permission before enabling an AI provider. Keep providers behind the server-side AI gateway.
- Validate every AI result against a strict schema and deterministic content/policy checks before storing or passing it to another step.

## Operations

- Synthetic authorization pages (ADR0033) remain double default-off, owner/session
  bound, signed and CSRF protected. They use fixed examples only and cannot call
  the real candidate adapter. Status URLs are origin-session scoped; loss of a
  session is not evidence to retry, recover or activate a grant automatically.

- Scoped TEST candidate inspection is default-off, unwired and advisory only
  (ADR0032). Exact owned receipt/envelope binding and current quarantine checks
  never authorize provider work. Uncertain/orphaned attempts require explicit
  reconciliation; no automatic promotion, retry, revocation or cleanup occurs.

- Keep development, staging, and production configurations, permissions, and credentials separate. Do not copy production data into development or staging.
- Do not modify production systems manually. Production changes require a reviewed deployment, recoverable backup, health check, monitoring, and tested rollback/stop path.
- Log request IDs and operational metadata, not secrets, access tokens, private customer information, or unnecessary ad content.
- Track data retention, advertiser export/deletion, platform-token revocation, incident response, and account disconnection before inviting external beta users.
- Follow [ADR-0027](docs/adr/0027-data-lifecycle-and-no-resend-boundary.md) for the planned data lifecycle: stop, revoke, local erasure and recipient/backup erasure have separate evidence. A durable action barrier must survive restore without retaining creative snapshots indefinitely. This production mechanism is not implemented; existing TEST ledgers must not be reset or cascaded away.

- ADR0034 synthetic recovery rebinds only fixed-example session metadata after separate signed/CSRF confirmation. It does not recover a Google/candidate grant or authorize retries. Assessment preserves uncertainty across session/scope/time changes; legacy stop/reconcile access remains unchanged.
