# Security baseline

- Never commit secrets. Local environment files and private-key formats are excluded by .gitignore.
- The NVIDIA Build API key shown in the supplied screenshot is exposed. Revoke it and issue a replacement in NVIDIA Build; the replacement belongs only in a local/deployment secret store.
- Do not send patient, clinic, lead, Instagram account, or other customer data to free/trial model endpoints.
- Treat free/trial APIs as unstable evaluation services and check provider terms, model licenses, data retention, rate limits, and commercial-use permissions before use.
- Separate development, staging, and production credentials and databases.
- Do not modify production systems manually. Production changes require a pipeline, a backup, a health check, and a tested rollback path.
- Log identifiers and request metadata, not secrets or sensitive content.
