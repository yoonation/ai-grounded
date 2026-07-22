<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.no-query-in-loop no query in loop (good pattern)

Substrate-original illustration. Related rows are fetched up front with one
eager-loaded query, so rendering N parent rows issues one or two queries
instead of N+1.

```python
# One query for authors, one for all their books, joined in memory by the ORM.
authors = (
    Author.objects
    .filter(active=True)
    .prefetch_related("books")[:50]
)
for author in authors:
    render(author.name, [b.title for b in author.books.all()])
```

Why this satisfies the rule: `prefetch_related` collapses what would be one
query per author's books into a single additional query over all the
collected author IDs. The cost is constant in the number of authors rather
than linear, and the resulting set-based query is the one performance-database.index-alignment
ensures is indexed.
