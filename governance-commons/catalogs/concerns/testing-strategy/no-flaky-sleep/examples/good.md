<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.no-flaky-sleep explicit synchronization

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python with poll-and-timeout helper

```python
import time

def wait_for(predicate, timeout=5.0, interval=0.05, what=""):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(interval)  # bounded poll, not test synchronization
    raise TimeoutError(f"timed out waiting for: {what}")

def test_background_job_completes(queue, worker):
    worker.start()
    queue.enqueue({"task": "process", "id": 42})
    wait_for(
        lambda: queue.is_empty() and result_store.has_result(42),
        timeout=5.0,
        what="job-42 to complete",
    )
    assert result_store.get(42).status == "completed"
```

The helper polls the condition with a bounded timeout; the
`time.sleep(interval)` is inside the helper rather than in the
test, and it is a backoff between polls rather than a fixed
synchronization wait. The condition expression captures what
the test is actually waiting for.

## Pattern B: JavaScript Jest with waitFor

```javascript
import { waitFor } from "@testing-library/dom";

test("background job completes", async () => {
  worker.start();
  queue.enqueue({ task: "process", id: 42 });

  await waitFor(
    () => {
      expect(queue.isEmpty()).toBe(true);
      expect(resultStore.has(42)).toBe(true);
    },
    { timeout: 5000, interval: 50 }
  );

  expect(resultStore.get(42).status).toBe("completed");
});
```

`waitFor` polls the assertion until it passes or the timeout
expires. The framework's helper is substrate-recommended over
custom polling because it integrates with the test reporter and
produces a substrate-acceptable failure message.

## Pattern C: Java with Awaitility

```java
import static org.awaitility.Awaitility.await;
import java.time.Duration;

@Test
void backgroundJobCompletes() {
    worker.start();
    queue.enqueue(new Task("process", 42));

    await()
        .atMost(Duration.ofSeconds(5))
        .pollInterval(Duration.ofMillis(50))
        .until(() -> queue.isEmpty() && resultStore.has(42));

    assertThat(resultStore.get(42).status()).isEqualTo("completed");
}
```

Awaitility's fluent API expresses the wait condition declaratively.
The substrate-acceptable form bounds the wait with a timeout and
specifies the poll interval explicitly.

## Pattern D: Go with channel-based coordination

```go
func TestBackgroundJobCompletes(t *testing.T) {
    done := make(chan struct{})
    worker := NewWorker(WithCompletionSignal(done))
    worker.Start()
    defer worker.Stop()

    queue.Enqueue(Task{Op: "process", ID: 42})

    select {
    case <-done:
        // proceed
    case <-time.After(5 * time.Second):
        t.Fatal("timed out waiting for job-42")
    }

    if got := resultStore.Get(42).Status; got != "completed" {
        t.Errorf("status = %q; want %q", got, "completed")
    }
}
```

The channel-based coordination is the idiomatic Go form. The
`time.After` in the `select` is a bounded timeout, not a
synchronization wait; the test waits for the explicit completion
signal rather than for elapsed time.

## Pattern E: time-controlled rate limiter tests

```python
from freezegun import freeze_time

def test_rate_limiter_resets_after_interval():
    with freeze_time("2026-05-25 12:00:00") as frozen:
        limiter = RateLimiter(max_per_minute=10)
        for _ in range(10):
            assert limiter.allow("user-1") is True
        assert limiter.allow("user-1") is False

        frozen.tick(delta=timedelta(seconds=61))
        assert limiter.allow("user-1") is True
```

For tests of time-dependent behavior, the substrate-preferred
form uses a fake clock (`freezegun`, `sinon.useFakeTimers`,
Awaitility's fake clock) to advance simulated time
deterministically. Real elapsed time is not required and is
substrate-discouraged because of flakiness.
