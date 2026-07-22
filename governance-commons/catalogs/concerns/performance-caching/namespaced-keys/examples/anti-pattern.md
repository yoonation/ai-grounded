<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-caching.namespaced-keys namespaced keys (anti-pattern)

Substrate-original illustration.

```python
# A bare key with no namespace, no version, and a missing result-varying input.
def cache_profile(cache, user_id, locale, profile):
    cache.set(str(user_id), serialize(profile), ex=300)  # key is just the id
```

## Why this violates the rule

The key is a bare user id. It has no namespace, so another data type keyed on
the same id (an order, a session) collides with it and one overwrites the
other. It has no version, so a deploy that changes the serialized shape keeps
serving the old shape. And it omits the locale, a result-varying input, so a
profile rendered for one locale is served for another. A namespaced,
versioned key built through a helper that includes the locale fixes all
three.
