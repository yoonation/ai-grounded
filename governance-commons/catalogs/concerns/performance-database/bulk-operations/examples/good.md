<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.bulk-operations bulk operations (good pattern)

Substrate-original illustration. The import uses a batched multi-row insert,
so statement count is bounded by batch rather than by row, and each batch
commits to keep transactions short.

```python
BATCH = 1000
def import_rows(rows):
    for chunk in batched(rows, BATCH):
        with db.begin():                 # one short transaction per batch
            db.execute(insert_many, chunk)   # one multi-row INSERT per batch
```

Why this satisfies the rule: 50,000 rows become 50 statements rather than
50,000, capturing most of the round-trip savings, and the per-batch commit
keeps any single transaction short so it does not hold locks too long
(performance-database.transaction-scope). The performance-database.bulk-operations test template asserts statement count
does not scale with row count.
