<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.no-query-in-loop no query in loop (anti-pattern)

Substrate-original illustration. A query is issued inside the loop, so the
work scales with the data: 50 authors becomes 51 round trips, 50,000 becomes
50,001.

```python
authors = Author.objects.filter(active=True)[:50]
for author in authors:
    # One query PER author. The lazy relationship access hides it: there is
    # no visible query call, just an attribute read that triggers a fetch.
    books = author.books.all()
    render(author.name, [b.title for b in books])
```

Why this violates the rule: each `author.books.all()` is a separate round
trip. The pattern is invisible against a few seed rows and gets worse
exactly as the table grows. The fix is `prefetch_related("books")` on the
parent query.
