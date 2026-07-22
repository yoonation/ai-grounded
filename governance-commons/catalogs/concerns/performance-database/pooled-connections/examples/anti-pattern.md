<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: performance-database.pooled-connections pooled connections (anti-pattern)

Substrate-original illustration. A fresh connection is opened inside the
request handler on every call.

```python
def handle_request(req):
    # New TCP + TLS + auth handshake every request, and a new slot against
    # the database's connection ceiling. A traffic burst exhausts it.
    conn = psycopg.connect(DATABASE_URL)
    try:
        return conn.execute(query, req.params).fetchall()
    finally:
        conn.close()
```

Why this violates the rule: per-request connections pay full establishment
cost on every call and can exhaust the database's hard connection limit
under load, locking out the whole application. The fix is a process-level
pool created at startup.
