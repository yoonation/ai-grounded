<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.keyset-pagination keyset pagination (good pattern)

Substrate-original illustration. The cursor encodes the last seen sort key,
and the next page seeks to it via an indexed predicate, so every page costs
the same.

```sql
-- Next page: seek past the last (created_at, id) the client saw.
SELECT id, title, created_at
FROM articles
WHERE (created_at, id) < ($1, $2)   -- last seen cursor, total stable order
ORDER BY created_at DESC, id DESC
LIMIT 50;
-- Backed by an index on (created_at, id), so this is an indexed seek.
```

Why this satisfies the rule: the indexed seek to the cursor boundary makes
page 1000 cost the same as page 1, and the `(created_at, id)` total order
with the primary-key tiebreaker keeps pages stable under concurrent inserts.
