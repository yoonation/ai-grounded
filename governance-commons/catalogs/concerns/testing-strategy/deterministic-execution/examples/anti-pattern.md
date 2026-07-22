<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.deterministic-execution non-deterministic test execution

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: shared mutable state across tests

```python
# tests/conftest.py
USER_COUNT = 0  # module-level mutable state

@pytest.fixture
def shared_user(db):
    global USER_COUNT
    USER_COUNT += 1
    user = User(email=f"test-{USER_COUNT}@example.com")
    db.add(user)
    db.commit()
    return user
```

The `USER_COUNT` is shared across tests. In parallel execution,
multiple workers increment it concurrently; the email value is
non-deterministic. In randomized order, the same email value
may be generated for different tests on different runs. The
test passes sometimes and fails sometimes.

## Anti-pattern B: wall-clock time in assertions

```python
def test_user_creation_records_timestamp():
    user = create_user(email="alice@example.com")
    expected = datetime.utcnow()  # wall clock
    assert abs((user.created_at - expected).total_seconds()) < 1
```

The test passes when `create_user` returns within 1 second of
`datetime.utcnow()` and fails when CI is under load and the call
takes longer. The substrate-aligned form uses frozen time
(Pattern D in the companion good example).

```javascript
test("token expires after 1 hour", () => {
  const token = issueToken({ ttlMinutes: 60 });
  setTimeout(() => {
    expect(verifyToken(token).valid).toBe(false);
  }, 3600 * 1000);  // wait one hour in real time
});
```

The test takes one hour to run in real time. Beyond the slow
suite, the test is also Jest-default-timeout dependent and will
fail under most configurations.

## Anti-pattern C: shared database state without per-test cleanup

```python
@pytest.fixture(scope="session")  # session-scoped!
def db():
    """Database is created once per session and reused."""
    engine = create_engine("postgresql://...")
    Base.metadata.create_all(engine)
    yield Session(engine)

def test_create_order(db):
    order = Order(amount=100)
    db.add(order)
    db.commit()
    # no cleanup; order persists for the rest of the session

def test_orders_initially_empty(db):
    # this test passes when run in isolation, fails when run after test_create_order
    assert db.query(Order).count() == 0
```

The session-scoped fixture means database state accumulates
across tests. Order-dependent tests pass in one ordering and
fail in another. The substrate-aligned form uses function-
scoped fixtures with per-test isolation.

## Anti-pattern D: parallel-unsafe global singletons

```javascript
// src/orderProcessor.js
let currentOrder = null;  // module-level singleton

export function startOrder(id) {
  currentOrder = { id, items: [] };
}

export function addItem(item) {
  currentOrder.items.push(item);
}

export function finalize() {
  const result = process(currentOrder);
  currentOrder = null;
  return result;
}
```

```javascript
// tests/orderProcessor.test.js
test("can start and finalize", () => {
  startOrder("order-1");
  addItem({ name: "widget" });
  expect(finalize().id).toBe("order-1");
});

test("can process multiple items", () => {
  startOrder("order-2");
  addItem({ name: "gadget" });
  addItem({ name: "gizmo" });
  expect(finalize().items).toHaveLength(2);
});
```

When tests run in parallel, both workers manipulate the same
`currentOrder` singleton. Test 1 may see test 2's items added
to its order; finalize may return a result for the wrong order.
The test failures are intermittent and depend on scheduler
timing.

## Anti-pattern E: real network in tests

```python
def test_external_api_integration():
    response = requests.get("https://real-api.example.com/users/42")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"
```

The test depends on `real-api.example.com` being available,
returning a user named "Test User", and not having been changed
since the test was written. The test fails when the API is
down, the user is deleted, the API renames the field, or
network latency exceeds the request timeout. The substrate-
aligned form mocks the external API or uses a hermetic test
container.

## Anti-pattern F: retry-until-green policy

```yaml
# .github/workflows/test.yml
- name: run tests with retry
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 5      # retry up to 5 times on failure
    command: pytest tests/
```

The retry-on-failure CI configuration masks flakiness. A test
that fails 3 times out of 5 still passes the build. Real
regressions hide among the flake noise; the team loses signal
from the test suite. The substrate-rejected pattern.

## Anti-pattern G: flake quarantine with no sunset

```python
@pytest.mark.flaky
def test_payment_callback_under_concurrent_load():
    # quarantined "for now"; no sunset; no tracking issue
    ...
```

The quarantine is permanent. The test stays in the non-blocking
tier indefinitely; no one is responsible for fixing or deleting
it; the quarantine tier grows over time as more tests are
moved in. The substrate-aligned form has a sunset date in the
comment, a tracking issue, and a quarterly review of
quarantined tests.

## Anti-pattern H: no observability into flake rate

The team has no dashboard, no CI metric, no team-channel
notification about flake rate. Flakes happen; PRs are
re-run; merges proceed; the cost is invisible. Six months later,
the suite's flake rate is 12% and the team has normalized
"sometimes you have to re-run it twice."

The substrate-aligned remediation: publish flake rate as a
team-visible metric; threshold above 1% triggers team review;
trends over time inform the test-strategy ADR.

## Why these forms accumulate

Determinism failures are not localized; they emerge from the
interaction of fixtures, parallelism, ordering, time, and shared
state. A single PR may not introduce flakiness; an unrelated
PR's change to an unrelated fixture exposes a latent race
condition. Without infrastructure (randomization in CI, parallel
execution as default, mock time, per-test isolation, flake
metrics), determinism erodes silently.
