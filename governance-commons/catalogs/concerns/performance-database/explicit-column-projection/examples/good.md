<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.explicit-column-projection explicit column projection (good pattern)

Substrate-original illustration. The query selects only the columns the
response needs, which can be served by a covering index without touching the
wide row.

```sql
-- The list view needs three fields. Select exactly those.
SELECT id, title, created_at
FROM articles
WHERE author_id = $1
ORDER BY created_at DESC
LIMIT 50;
```

Why this satisfies the rule: a narrow projection reads less off disk and
over the wire, and lets an index on `(author_id, created_at)` that includes
`title` answer the query as an index-only scan. It pairs with performance-database.index-alignment,
which provides that covering index.
