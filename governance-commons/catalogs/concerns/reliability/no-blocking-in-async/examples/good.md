<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.no-blocking-in-async no blocking in async (good pattern)

Substrate-original illustration. Blocking work is either replaced with an
async equivalent or offloaded to an executor, so it does not stall the
shared event loop.

```python
import asyncio

async def fetch_rate(symbol: str) -> Rate:
    # Async HTTP client: yields the loop while waiting on the network,
    # so other coroutines keep running.
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"/rate/{symbol}")
        return Rate.parse(resp.json())

async def hash_password(pw: str) -> str:
    # CPU-bound work offloaded to a thread pool so it does not
    # monopolize the event loop.
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _bcrypt_hash, pw)
```

```javascript
// Async filesystem API, not the *Sync variant.
const data = await fs.promises.readFile(path, "utf8");
```

Why this satisfies the rule: no synchronous blocking call sits on the
async path. Network I/O uses the async client; CPU-bound work is
offloaded. One slow operation cannot serialize every concurrent request
sharing the loop.
