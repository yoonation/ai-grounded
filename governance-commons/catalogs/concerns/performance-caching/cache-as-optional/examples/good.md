<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.cache-as-optional cache as optional (good pattern)

Substrate-original illustration.

```python
# The cache is optional to correctness: a miss, an error, or a timeout all
# fall back to the source of record. Cache calls carry a bounded timeout.
def get_settings(cache, db, account_id):
    key = f"settings:v1:{account_id}"
    try:
        raw = cache.get(key)              # client configured with a short timeout
        if raw is not None:
            return deserialize(raw)
    except CacheError:
        pass  # treat any cache failure as a miss; do not propagate
    # source of record is always present and exercised
    settings = db.load_settings(account_id)
    try:
        cache.set(key, serialize(settings), ex=300)
    except CacheError:
        pass  # a failed cache write must not fail the read
    return settings
```

## Why this satisfies the rule

A cache miss, a cache error, and a cache timeout all reach the source of
record, so a cache outage degrades to slightly slower reads rather than to
failed requests. The cache write is best-effort. No authoritative data lives
only in the cache. The source path runs on every miss, so it cannot rot
unnoticed.
