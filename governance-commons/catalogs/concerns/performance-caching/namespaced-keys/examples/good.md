<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.namespaced-keys namespaced keys (good pattern)

Substrate-original illustration.

```python
# A key-building helper prepends a stable namespace and a schema version,
# and includes every input that varies the value.
CACHE_SCHEMA_VERSION = "v2"

def profile_key(user_id, locale):
    return f"user-profile:{CACHE_SCHEMA_VERSION}:{user_id}:{locale}"

def cache_profile(cache, user_id, locale, profile):
    cache.set(profile_key(user_id, locale), serialize(profile), ex=300)
```

## Why this satisfies the rule

The key carries a data-type namespace (`user-profile`), a schema version
(`v2`) so a deploy that changes the serialized shape does not serve an old
shape, and every result-varying input (the user id and the locale). It
cannot collide with another data type keyed on the same user id, and a
locale-specific value is never served for the wrong locale.
