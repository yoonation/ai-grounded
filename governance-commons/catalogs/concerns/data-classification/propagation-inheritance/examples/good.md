<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.propagation-inheritance propagation inheritance (good pattern)

Substrate-original illustration.

```python
# An export inherits the source class; a tier that cannot meet the class is
# refused the data.
def export_records(records, destination):
    cls = most_restrictive(r.data_classification for r in records)
    artifact = Export(rows=records, data_classification=cls)  # inherits class
    if not destination.can_handle(cls):
        raise ClassificationError(f"{destination} cannot hold {cls} data")
    destination.write(artifact)

def cache_value(cache_tier, key, value, cls):
    # restricted data is not cached in a shared or edge tier
    if cls == "restricted" and cache_tier.is_shared:
        return  # do not cache; serve from source of record
    cache_tier.set(key, value, cls=cls)
```

## Why this satisfies the rule

The export carries the most restrictive class of its source records, and a
destination that cannot meet that class is refused the data. The cache helper
declines to place restricted data in a shared tier that cannot protect it,
honoring the what-may-be-cached-where boundary this rule owns while leaving
the caching mechanics to the performance-caching concern.
