<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.bulk-operations bulk operations (anti-pattern)

Substrate-original illustration. An import loop issues one INSERT per row for
tens of thousands of rows.

```python
def import_rows(rows):
    for row in rows:
        # One statement and one round trip per row. The fixed per-statement
        # overhead, paid 50,000 times, dominates the actual data work.
        db.execute(insert_one, row)
```

Why this violates the rule: row-at-a-time processing pays the per-round-trip
overhead on every row, the write-side form of N+1. The fix is a batched
multi-row insert. Note the opposite extreme (one unbatched statement over
all 50,000 rows) trades this for a long lock-holding transaction, which is
why the good pattern batches.
