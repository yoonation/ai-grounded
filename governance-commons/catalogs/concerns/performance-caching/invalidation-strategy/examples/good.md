<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.invalidation-strategy invalidation strategy (good pattern)

Substrate-original illustration.

```python
# A write invalidates the entity key AND the derived list keys it affects.
def publish_article(cache, db, article):
    db.save(article)
    # entity key
    cache.delete(f"article:v1:{article.id}")
    # derived keys that included this article
    cache.delete(f"article-list:v1:author:{article.author_id}")
    cache.delete("article-list:v1:recent")
    cache.delete(f"article-count:v1:author:{article.author_id}")
```

## Why this satisfies the rule

The write enumerates every key the value is cached under, not only the
primary entity key: the author's article list, the global recent list, and
the author's article count are all invalidated. The common partial-
invalidation failure (forgetting the derived list and count) is avoided
because the invalidation set was derived from where the value is actually
cached.
