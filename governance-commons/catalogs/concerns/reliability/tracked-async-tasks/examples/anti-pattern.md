<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.tracked-async-tasks tracked async tasks (anti-pattern)

Substrate-original illustration. Tasks are started fire-and-forget, so
exceptions vanish and (in CPython) the task can be garbage-collected
before it completes. The native lint rules flag both shapes.

```python
import asyncio

def start_background(coro):
    # No reference kept. The event loop holds only a weak reference,
    # so this task may be GC'd before it runs. Exceptions are lost.
    asyncio.create_task(coro)   # RUF006 finding
```

```typescript
async function handler(req: Request): Promise<Response> {
  recordMetrics(req);   // floating promise: rejection becomes an
                        // unhandled rejection, completion unobserved
                        // (@typescript-eslint/no-floating-promises)
  return serve(req);
}
```

Why this fails the rule: the work is started but not tracked. Its failure
is silent, its completion is unobservable, and in Python it may not run
to completion at all. The fix is to hold a reference and observe the
result, or to await the promise.
