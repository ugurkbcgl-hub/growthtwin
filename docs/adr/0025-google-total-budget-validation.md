# ADR-0025: TEST-only total-budget candidate validation

- Status: Accepted for local synthetic validation only
- Date: 2026-10-19
- Decision owner: Project owner, delegated sequencing

## Decision

Daily budget is not an enforceable flight total. Before extending dispatch,
prepare a separate candidate from the current immutable draft approval with
CUSTOM_PERIOD, non-shared budget and exact totalAmountMicros. Remove amountMicros;
preserve reviewed TEST text, URL override, dates, timezone and targeting.

Expose a local owner-only CSRF POST with a distinct ten-minute signed budget
review, bound to owner/workspace/source/target. Verify the exact non-manager TEST
account and existing TRY/timezone/city constraints. Recheck source/grant before
and after the request. The only mutation-shaped request sets validateOnly=true
and partialFailure=false. No model is saved and no existing ledger is reset.
No create fallback, daily-budget fallback or ENABLED operation exists.

Success is transient request validation, not a persisted production capability,
cap application, campaign approval, advertiser consent or live readiness. UI
must say the existing daily-budget test remains unchanged. Timeout/malformed
response returns sanitized failure. Production gates remain closed.

## Verification and next boundary

Browser validation of the 5,000 TRY synthetic candidate succeeded against Google
v25 without creating resources. 79 focused connection/mapper tests passed.
Source/key/CSRF, test-target failures, preserved ledger, exact units/no daily
field, no fallback and sanitized network/shape failures are covered.

Next verify a NEW durable PAUSED TEST total-budget resource's creation/read/stop
under a separate reviewed profile; never migrate the old daily resource's type.
See [live readiness](../product/google-search-live-readiness.md) for remaining gates.
