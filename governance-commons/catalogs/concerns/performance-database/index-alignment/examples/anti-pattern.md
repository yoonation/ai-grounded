<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.index-alignment index alignment (anti-pattern)

Substrate-original illustration. A hot filtered query has no supporting
index and does a sequential scan, while three unused indexes tax every
write.

```sql
-- Hot query does a sequential scan: no index leads with customer_id.
-- SELECT id, total FROM orders WHERE customer_id = $1 ...

-- Meanwhile these exist and the planner never chooses them:
--   idx_orders_status        (low selectivity, never selected)
--   idx_orders_updated_at    (no query filters on updated_at)
--   idx_orders_created_status (redundant prefix of another index)
```

Why this violates the rule: the symmetric failure. The hot query scans the
whole table because no index matches its access pattern, while the three
speculative indexes maintained on every insert and update buy nothing. The
fix is to add the composite index the query needs and drop the unused ones,
using the index-usage statistics as evidence.
