<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.index-alignment index alignment (good pattern)

Substrate-original illustration. The composite index orders its columns to
match the query's equality predicate, then its range and sort, so the
planner uses the whole index.

```sql
-- Hot query: equality on customer_id, range + sort on created_at.
-- SELECT id, total FROM orders WHERE customer_id = $1
--   AND created_at >= $2 ORDER BY created_at DESC LIMIT 50;

CREATE INDEX CONCURRENTLY idx_orders_customer_created
    ON orders (customer_id, created_at);
```

Why this satisfies the rule: equality column first, then the range/sort
column, lets the planner seek to the customer's rows and walk them in
`created_at` order, serving the LIMIT without a sort step. EXPLAIN shows an
index scan, confirmed by the performance-database.index-alignment test template.
