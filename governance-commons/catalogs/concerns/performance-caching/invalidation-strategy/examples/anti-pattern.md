<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.invalidation-strategy invalidation strategy (anti-pattern)

Substrate-original illustration.

```python
# Partial invalidation: the entity key is cleared, the derived keys are not.
def publish_article(cache, db, article):
    db.save(article)
    cache.delete(f"article:v1:{article.id}")   # only the entity key
    # the author's article list, the recent list, and the count are NOT
    # invalidated and continue to serve the pre-publish view
```

## Why this violates the rule

The write invalidates the single article it obviously changed but leaves the
derived keys that also cached the value: the author's article list, the
global recent list, and the author's article count all continue to serve
their stale, pre-publish contents until an unrelated time-to-live happens to
expire. This is the dominant invalidation failure. The fix is to invalidate
every key the value is cached under, derived from where it is actually
cached.
