<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.pooled-connections pooled connections (good pattern)

Substrate-original illustration. A process-level pool is created once at
startup; each request checks out and returns a connection.

```python
# module scope, created once at process start
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=0,
                        pool_timeout=2, pool_recycle=1800)

def handle_request(req):
    with engine.connect() as conn:   # checkout from pool, return on exit
        return conn.execute(query, req.params).fetchall()
```

Why this satisfies the rule: connection establishment cost is paid once and
amortized across requests, and the pool bounds the connections the process
can hold. Sizing, the acquire timeout, and the max lifetime here are the
performance-database.pool-sizing review's subject; this example shows only that a pool is used.
