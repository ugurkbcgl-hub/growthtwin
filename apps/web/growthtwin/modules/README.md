# Domain module boundaries

These packages are placeholders only. Keep the first application as one Django
deployment while keeping domain responsibilities separate as implementation is
authorized. No models, persistence behavior, provider clients, or cross-module
imports are defined yet.

- `workspaces`: workspace identity, membership, roles, and tenant context.
- `content`: drafts, versions, and asset metadata.
- `approvals`: approval records tied to an exact content version.
- `publishing`: provider-neutral publication contracts and platform adapters.
- `analytics`: normalized results from social platforms.
- `ai_gateway`: provider-neutral AI contracts and replaceable adapters.
- `persistence`: shared persistence contracts and transaction ownership.

Modules should depend on explicit contracts rather than another module's
internal models. Product workflows remain out of scope for this Phase 0 shell.
