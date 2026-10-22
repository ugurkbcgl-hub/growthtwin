# ADR-0034: Recovery assessment and synthetic session reopening

Status: Accepted for metadata assessment and isolated synthetic rehearsal only
Date: 2026-10-22

## Candidate assessment

An unwired metadata-only service verifies active ownership, durable identity and
receipt consistency under workspace/connector/receipt locks. It returns a public
snapshot, disposition and separate current-quarantine-scope/session-match flags.
It never loads a client, checks a credential path, decrypts files, exchanges,
refreshes, revokes, writes metadata or changes the existing runtime.

| Receipt | Advisory disposition |
| --- | --- |
| RESERVED, same session/current scope, within five-minute window | callback_wait |
| Other RESERVED, including lost session or elapsed window | restart_review |
| EXCHANGING or UNCERTAIN | reconciliation_required |
| CANDIDATE | inactive_candidate_review |
| REJECTED | rejected_history |

Uncertainty survives expiry, block, generation rotation and session loss. Candidate
remains inactive after its handshake deadline. None proves that an outbound request
failed, a file is absent or revocation occurred. can_retry_exchange/can_activate
are always False. Adapter-off assessment is permitted like historical metadata
reads; callback_wait is metadata, not permission. No actual candidate recovery UI,
secret reading, adoption or cancellation is added. Legacy grants and separately
permitted stop/reconcile paths remain unchanged.

## Synthetic session reopening

ADR0033's double-default-off pages list20 recent OWNED fixed synthetic receipts.
GET neither runs work nor changes the session marker. A separate CSRF, signed
ten-minute confirmed recover POST binds current owner/workspace/session plus
original connector/generation/revision/attempt/scenario AND receipt expiry.
Reload metadata and compare exactly before changing only the last-example session
marker. Wrong action/session, tampering, expiry and changed deadline fail closed.
Recover calls neither begin_example nor perform_example and creates no receipt.

A lost/new session may explicitly view an existing fixed example, including
historical/running/terminal state. Status still hides run controls for stale,
blocked, expired, running or terminal receipts. A current pending fake requires
the existing SEPARATE confirmed perform POST and DB reservation/scope/time checks.
Reopening never extends its deadline or reruns a fake. No code/PKCE/provider
handshake or candidate receipt is rebound by this synthetic mechanism.

Only the last opened/started example is session-accessible. Session-save failure
may require another explicit reopen; no automatic recovery exists. The20-row list
is not an audit export; older history remains untouched. These fixtures establish
neither production reauthentication nor grant-recovery policy.

## Evidence and next action

18 new tests (8 candidate assessment,10 synthetic recovery) and17 prior journey
tests:35 local passes. Extended isolated browser test passed new-session404,
explicit SAME pending-receipt reopen, separate execution and both outcomes,
desktop/mobile/keyboard and preserved quarantine. Recovery mobile screenshot
reviewed outside Git. Actual client/transport/path/read/write boundaries mocked
or forbidden. No migration, actual credential/provider/preserved DB/Heroku use.
Independent review requested stronger expired/stale/terminal tests; added/passed.
Final review and required CI results belong to the PR/continuity record.

Next: explicit RESERVED-only retirement with generation fencing and mocked tests;
never retire/retry EXCHANGING/UNCERTAIN or touch legacy grants. Actual callback
wiring, configured TEST target proof, orphan reconciliation, adoption/rollback,
scoped refresh and production gates remain open.
