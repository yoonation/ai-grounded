<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.non-blocking-migrations non-blocking migrations (good pattern)

Substrate-original illustration. The index is built concurrently, outside a
transaction, so writes to the table are not blocked during the build.

```sql
-- Run outside a transaction block (the migration tool is told not to wrap it).
CREATE INDEX CONCURRENTLY idx_orders_customer_created
    ON orders (customer_id, created_at);
```

Why this satisfies the rule: `CONCURRENTLY` builds the index without taking
the lock that blocks writes, so a routine deploy does not become a partial
outage on a hot table. squawk's `require-concurrent-index-creation` rule
(referenced in the performance-database.non-blocking-migrations binding) confirms this form.
