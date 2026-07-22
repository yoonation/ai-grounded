<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.cache-as-optional cache as optional (anti-pattern)

Substrate-original illustration.

```python
# The cache is a hard dependency: if it is down, the read fails.
def get_settings(cache, db, account_id):
    key = f"settings:v1:{account_id}"
    raw = cache.get(key)        # no timeout; raises on a cache outage
    if raw is None:
        settings = db.load_settings(account_id)
        cache.set(key, serialize(settings))   # also raises if cache is down
        return settings
    return deserialize(raw)
```

## Why this violates the rule

The cache read has no surrounding error handling and no timeout, so a cache
outage raises straight out of the function and a cache slowdown hangs the
request. A cache failover or eviction storm becomes a user-visible outage,
even though the source of record is healthy and could serve the read. The fix
is to treat any cache error or timeout as a miss and fall back to the source,
with a bounded timeout on the cache call.
