<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.explicit-column-projection explicit column projection (anti-pattern)

Substrate-original illustration. A wildcard reads every column of a wide row
to feed a response that uses two of them, and defeats any covering index.

```sql
-- The view uses title and created_at, but this reads the full row,
-- including a large `body` TEXT column, on every list render.
SELECT *
FROM articles
WHERE author_id = $1
ORDER BY created_at DESC
LIMIT 50;
```

Why this violates the rule: the wildcard reads the large `body` column the
list never displays, inflating every read, and forces a heap fetch because
no index can cover every column. A schema change adding another large column
silently slows this query further. The fix is to name the three columns.
