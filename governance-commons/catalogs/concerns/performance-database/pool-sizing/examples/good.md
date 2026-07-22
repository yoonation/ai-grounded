<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.pool-sizing pool sizing (good pattern)

Substrate-original illustration. Pool size is derived from the instance
count and the database ceiling, with an acquire timeout and a max lifetime.

```python
# DB ceiling 100, reserve 20 for admin/replica, 40 app instances:
#   (100 - 20) / 40 = 2 connections per instance is too tight for this
#   workload, so the fleet runs an external pooler and apps use small pools.
engine = create_engine(
    DATABASE_URL,
    pool_size=5, max_overflow=0,   # bounded; sums safely behind PgBouncer
    pool_timeout=2,                # acquire timeout: fail fast, not hang
    pool_recycle=1800,             # max lifetime: rebalance after failover
)
```

Why this satisfies the rule: the aggregate stays within the ceiling because
the external pooler multiplexes, each instance has enough for its
concurrency, and the acquire timeout turns starvation into a fast visible
error rather than a hang.
