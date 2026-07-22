<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.non-blocking-migrations non-blocking migrations (anti-pattern)

Substrate-original illustration. A bare index build inside the migration
transaction takes a lock that blocks writes for the whole build.

```sql
-- Inside the default migration transaction, on a large table.
CREATE INDEX idx_orders_customer_created
    ON orders (customer_id, created_at);
```

Why this violates the rule: a non-concurrent `CREATE INDEX` on a populated
table holds a lock that blocks writes until the build finishes, turning the
deploy into a self-inflicted stall on every request touching `orders`. The
fix is `CREATE INDEX CONCURRENTLY` run outside the transaction; squawk
flags the bare form.
