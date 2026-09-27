# Session continuity

This folder carries GrowthTwin's current working context between Codex chats, models, and people.

## Source of truth

- `STATE.md` is the compact, current handoff snapshot. Replace outdated snapshot details; do not turn it into a transcript.
- `PROJECT.md`, `ROADMAP.md`, and accepted ADRs remain the canonical project record. Update those when a decision or durable project status changes.
- The current user request and the repository's `AGENTS.md` instructions take precedence over this handoff note. Verify facts that may have changed, especially Git/PR state, provider quotas, and environment status.

## At the start of a session

1. Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, this file, and `STATE.md`.
2. Check the current branch, working-tree changes, latest commit, and linked pull request before editing.
3. Confirm the next action still matches the user's current request and the Phase 0 gates.

## At a milestone or handoff

Update `STATE.md` with only verified current facts: objective, completed work, branch/PR, checks actually run, remaining decisions/blockers, and one recommended next action. Update canonical docs when appropriate. Mark unverified information as unverified and include the date/time and timezone.

Never record API keys, passwords, access tokens, secret values, or private customer data here. If relevant, record only that a credential is stored in an approved secret store and whether it needs rotation. Do not copy credentials into another chat or model.

## Copyable handoff prompt

> Continue the GrowthTwin project from its repository. First read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md`, and `docs/continuity/STATE.md`; then verify the current branch, working-tree state, and PR. Treat the current user request as authoritative, preserve the Phase 0 gates, keep credentials out of chat and Git, and update the continuity snapshot after meaningful progress. Start with the single next action in `STATE.md` and report progress in clear Turkish.

If the next model cannot access the repository, provide it the current `STATE.md` text and the user's new request. The repository remains the durable source of truth; never include secrets in the pasted context.
