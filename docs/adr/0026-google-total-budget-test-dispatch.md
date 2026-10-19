# ADR-0026: Immutable total-budget PAUSED TEST dispatch

- Status: Accepted for isolated local synthetic TEST use
- Date: 2026-10-19
- Decision owner: Project owner, delegated sequencing

## Decision

New workspace dispatch uses profile workspace-paused-test-v2-total. Exact TRY
minor units become totalAmountMicros (multiply by 10000); period CUSTOM_PERIOD,
non-shared budget, explicit account-local start/end date-times. Do not submit
amountMicros or fall back to a daily budget. Preserve the reviewed TEST-only
example.com override, Ankara/PRESENCE, synthetic keyword and selected text.

The signed review key includes the whole v2 profile. Existing per-draft durable
intent, committed-before-create reservation, current approval/source/target
rechecks, atomic PAUSED resources, no-resend and uncertain-state rules remain.
Create/read/stop still verify the exact configured non-manager TEST child.

Interpret old ledgers exclusively by their stored v1 version. They retain DAILY
and the old amount, with read/stop available. Reject attempts to create/convert
v1 through the new profile; show the recorded daily type/amount and disable its
create button. Use a genuinely new synthetic draft for a new total-budget test.
No migration/reset of prior ledger identity, operation UUID or payload occurs.
Unknown stored budget versions fail closed.

Readback verifies period, exact corresponding amount, zero/absent alternate
amount field, non-sharing, budget/campaign linkage and date-times in addition
to existing creative/geo/status checks. Remote drift prevents a verified result;
stop can still pause a resource whose target/name/identity match. A type/amount
drift after pause can leave reconciliation uncertain and never permits recreate.

## Verified evidence

82 focused local connection/mapper tests passed, including backward v1 read/stop,
blocked conversion, exact total fields, total/period drift and unknown version.
Existing timeout/no-resend, source/target/CSRF and validation-only tests also pass.

Browser created a NEW synthetic draft (id 2 in the preserved isolated DB),
selected and approved its current text, and created Google resources PAUSED with
5,000 TRY CUSTOM_PERIOD for October 20–November 3. Exact budget/date/creative
readback passed. Repeated create reconciled the same recorded resource. Stop
returned stopped/PAUSED. The original draft 1 DAILY test also stopped/read back
successfully at 333.33 TRY, with its old November 1–15 schedule intact.

Google TEST accounts do not serve ads. This proves request/configuration and
stop behavior, not actual budget exhaustion, live financial consent, account
aggregate limits or production concurrency/recovery. No production account,
advertiser data, migration, deployment, new service or spend was enabled.

Official budget schema checked 2026-10-19:
https://developers.google.com/google-ads/api/docs/campaigns/budgets/create-budgets
