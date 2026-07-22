<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.tracked-async-tasks tracked async tasks (good pattern)

Substrate-original illustration. Background tasks are kept in a live
reference set and their failures are observed, so a crash is visible and
the task is not garbage-collected mid-flight.

```python
import asyncio

_background: set[asyncio.Task] = set()

def start_background(coro) -> None:
    task = asyncio.create_task(coro)
    # Hold a strong reference so the loop cannot GC the task,
    # and observe completion so failures are not silent.
    _background.add(task)
    task.add_done_callback(_on_done)

def _on_done(task: asyncio.Task) -> None:
    _background.discard(task)
    if not task.cancelled() and task.exception() is not None:
        log.error("background task failed", exc_info=task.exception())
```

```typescript
// The promise is awaited (or explicitly handled), not left floating.
async function handler(req: Request): Promise<Response> {
  await recordMetrics(req);     // tracked
  return await serve(req);
}
```

Why this satisfies the rule: every concurrently-started unit of work is
either awaited or held in a live reference whose completion and failure
are observed. A crash surfaces in logs rather than vanishing, and the
task cannot be collected before it finishes.
