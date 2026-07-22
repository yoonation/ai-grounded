<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.no-flaky-sleep fixed-time sleeps for synchronization

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: pytest with hopeful sleep

```python
import time

def test_background_job_completes(queue, worker):
    worker.start()
    queue.enqueue({"task": "process", "id": 42})
    time.sleep(2)  # "should be enough"
    assert result_store.get(42).status == "completed"
```

The `time.sleep(2)` was tuned to pass on the author's laptop. On
a slow CI runner under load, the worker has not yet processed
the task when the assertion runs; the test fails intermittently.
Raising the sleep to 5 seconds makes the failure rarer at the
cost of making every test slower.

## Anti-pattern B: Jest with setTimeout-based synchronization

```javascript
test("background job completes", (done) => {
  worker.start();
  queue.enqueue({ task: "process", id: 42 });

  setTimeout(() => {
    expect(resultStore.get(42).status).toBe("completed");
    done();
  }, 1000);
});

test("polls with sleep-await pattern", async () => {
  queue.enqueue({ task: "process", id: 42 });
  await new Promise((r) => setTimeout(r, 1000));
  expect(resultStore.get(42).status).toBe("completed");
});
```

Both forms wait for a fixed interval. The first is the
substrate-rejected callback-with-setTimeout pattern; the second
is the async-await variant. Both are flaky on slow runners and
slow on fast runners.

## Anti-pattern C: Java Thread.sleep in JUnit

```java
@Test
void backgroundJobCompletes() throws InterruptedException {
    worker.start();
    queue.enqueue(new Task("process", 42));

    Thread.sleep(2000);  // wait "long enough"

    assertThat(resultStore.get(42).status()).isEqualTo("completed");
}
```

`Thread.sleep(2000)` is the substrate-rejected Java form. The
substrate-acceptable replacement is Awaitility (Pattern C in the
companion good example).

## Anti-pattern D: Go time.Sleep in test

```go
func TestBackgroundJobCompletes(t *testing.T) {
    worker := NewWorker()
    worker.Start()
    defer worker.Stop()

    queue.Enqueue(Task{Op: "process", ID: 42})
    time.Sleep(2 * time.Second)  // hopeful wait

    if got := resultStore.Get(42).Status; got != "completed" {
        t.Errorf("status = %q; want %q", got, "completed")
    }
}
```

The substrate-rejected form uses `time.Sleep` for synchronization
rather than channel-based coordination. The replacement (Pattern
D in the companion good example) uses an explicit done channel.

## Anti-pattern E: testing real elapsed time

```python
def test_rate_limiter_resets_after_interval():
    limiter = RateLimiter(max_per_minute=10)
    for _ in range(10):
        assert limiter.allow("user-1") is True
    assert limiter.allow("user-1") is False

    time.sleep(61)  # wait for real reset
    assert limiter.allow("user-1") is True
```

The test takes a real 61 seconds to run. Beyond the obvious slow-
suite cost, the test is now flaky if the rate limiter's window
implementation uses a slightly different interval boundary
calculation. The substrate-preferred form (Pattern E in the
companion good example) uses `freezegun` to advance simulated
time.

## Anti-pattern F: nested sleeps with retry

```python
def test_eventually_consistent_read():
    publish_event("user-created", {"id": "u-42"})

    for _ in range(10):
        time.sleep(0.5)
        user = read_replica.fetch("u-42")
        if user is not None:
            break
    else:
        pytest.fail("user never appeared on read replica")

    assert user.name == "Test User"
```

The retry loop with fixed sleep is a substrate-rejected pattern
even though it has a timeout (5 seconds total). It looks like
explicit synchronization but actually waits for fixed time
intervals between polls; the substrate-acceptable form uses a
poll-with-condition helper that surfaces the failure as
"timed out waiting for: user-42 on replica" rather than a
generic "fail" message.

## Why these forms accumulate

Sleeps are the path of least resistance when a test depends on
asynchronous behavior. The author runs the test once locally,
it passes, the PR merges. The flakes appear later in CI, in
unrelated PRs, and are dismissed as "flaky CI" rather than
addressed at the root.
