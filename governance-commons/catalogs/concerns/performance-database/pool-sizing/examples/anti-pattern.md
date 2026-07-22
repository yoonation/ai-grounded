<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.pool-sizing pool sizing (anti-pattern)

Substrate-original illustration. A large per-instance pool across many
instances sums past the database connection limit.

```python
# DB max_connections = 100. This pool is 50, and autoscaling runs up to
# 40 instances: 50 * 40 = 2000 attempted connections against a ceiling
# of 100. Under scale-out, the database refuses connections fleet-wide.
engine = create_engine(DATABASE_URL, pool_size=50, max_overflow=50)
# No pool_timeout: a starved pool hangs instead of failing fast.
```

Why this violates the rule: the per-instance pool looks fine in isolation
but the aggregate breaches the database ceiling under autoscaling, causing
the same correlated outage as per-request connections. The missing acquire
timeout compounds it by hanging rather than erroring. The fix is small pools
behind an external pooler with a bounded acquire timeout.
