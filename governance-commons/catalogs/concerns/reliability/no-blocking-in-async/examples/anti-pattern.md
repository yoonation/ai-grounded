<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.no-blocking-in-async no blocking in async (anti-pattern)

Substrate-original illustration. Synchronous blocking calls sit directly
on the async path, so a single slow call stalls every other concurrent
task on the loop. The native async-lint rules flag these.

```python
import time, requests

async def fetch_rate(symbol: str) -> Rate:
    # Blocking HTTP call inside a coroutine: the whole event loop is
    # frozen until this returns (Ruff ASYNC210).
    resp = requests.get(f"/rate/{symbol}")
    time.sleep(0.2)                      # blocking sleep (ASYNC251)
    return Rate.parse(resp.json())
```

```javascript
// Synchronous filesystem read blocks the event loop for every
// concurrent request (ESLint no-sync).
const data = fs.readFileSync(path, "utf8");
```

Why this fails the rule: each blocking call halts the single event loop,
so the latency of one request is paid by all of them. Under concurrency
the service's throughput collapses to serial. The fix is the async
equivalent for I/O and an executor for CPU-bound work.
