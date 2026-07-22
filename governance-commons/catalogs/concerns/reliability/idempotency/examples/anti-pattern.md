<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.idempotency idempotency (anti-pattern)

Substrate-original illustration. The operation has a retry around it (per
error-handling.retry-and-circuit-breaker) but is not idempotent, so a timeout after the effect already
applied produces a duplicate charge.

```python
@retry(attempts=3, on=TimeoutError)      # error-handling.retry-and-circuit-breaker retry wrapper
async def charge(amount: Money, user_id: str) -> ChargeResult:
    # No idempotency key. If the processor succeeds but the response
    # times out, the retry charges the user a second time.
    result = await _capture_with_processor(user_id, amount)
    await db.execute(
        "INSERT INTO charges (user_id, amount) VALUES ($1, $2)",
        user_id, amount,
    )
    return ChargeResult(result.id, captured=True)
```

Why this fails the rule: the retry that error-handling correctly mandates
is precisely what makes the missing idempotency dangerous. A network
timeout on a request that already succeeded triggers a second attempt,
and with no idempotency key the second attempt charges again and inserts
a duplicate row. The fix is a client-supplied idempotency key with an
atomic dedup, as in the good example.
