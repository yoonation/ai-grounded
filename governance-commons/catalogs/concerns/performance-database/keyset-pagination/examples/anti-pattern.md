<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.keyset-pagination keyset pagination (anti-pattern)

Substrate-original illustration. LIMIT with a large OFFSET scans and
discards every preceding row on each deep page.

```sql
-- Page 1000 of a long list: the database computes and throws away the
-- first 49,950 rows just to return 50. Cost grows with depth, and a
-- crawler walking to a high offset issues cheap requests that are
-- expensive to serve.
SELECT id, title, created_at
FROM articles
ORDER BY created_at DESC
LIMIT 50 OFFSET 49950;
```

Why this violates the rule: OFFSET does work proportional to how far into
the list the page is, so deep pages are progressively slower and exploitable
by automated traversal. The fix is keyset pagination with a cursor on an
indexed sort key.
