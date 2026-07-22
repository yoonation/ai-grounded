<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.idempotency idempotency (good pattern)

Substrate-original illustration. A retryable mutating operation carries an
idempotency key and deduplicates atomically, so a redelivery or a retry
after a timeout applies the effect exactly once.

```python
async def charge(payment_id: str, amount: Money) -> ChargeResult:
    # payment_id is the client-supplied idempotency key. The insert and
    # the dedup check are one atomic statement: a duplicate key is a
    # no-op that returns the original outcome.
    row = await db.execute(
        """
        INSERT INTO charges (payment_id, amount, status)
        VALUES ($1, $2, 'captured')
        ON CONFLICT (payment_id) DO NOTHING
        RETURNING id
        """,
        payment_id, amount,
    )
    if row is None:
        # Key already processed: return the prior result, do not re-charge.
        return await _load_existing(payment_id)
    await _capture_with_processor(payment_id, amount)
    return ChargeResult(payment_id, captured=True)
```

Why this satisfies the rule: the operation is safe to run twice. The
unique idempotency key plus the atomic conflict-handling guarantee that a
retry after a timeout, or a duplicate message delivery, produces one
charge. This is the deliberate complement to the bounded retry that
error-handling.retry-and-circuit-breaker wraps around the call.
