<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.deterministic-execution deterministic test execution

Substrate-original good patterns. Adapt to your stack.

## Pattern A: pytest with randomization and parallelism by default

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
  "-ra",
  "--strict-markers",
  "--strict-config",
  "-p", "pytest_randomly",          # order randomization
  "-n", "auto",                     # pytest-xdist parallelism
]
```

```python
# conftest.py - fixture for per-test database isolation
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def db():
    """Each test gets a fresh schema; no inter-test state leak."""
    engine = create_engine("postgresql://test:test@localhost/test")
    schema = f"test_{uuid4().hex[:8]}"
    engine.execute(f"CREATE SCHEMA {schema}")
    Session = sessionmaker(bind=engine.connect().execution_options(
        schema_translate_map={None: schema}))
    yield Session()
    engine.execute(f"DROP SCHEMA {schema} CASCADE")
```

The configuration enables order randomization and parallelism
by default. The per-test schema isolation lets tests run in
parallel without interfering with each other's database state.

## Pattern B: Jest with random sequencer and worker isolation

```javascript
// jest.config.js
export default {
  testSequencer: "<rootDir>/test-config/random-sequencer.js",
  maxWorkers: "50%",                  // parallel by default
  setupFilesAfterEach: ["./test-config/reset-state.ts"],
  testEnvironment: "node",
  globalSetup: "./test-config/setup-ephemeral-db.ts",
  globalTeardown: "./test-config/teardown-ephemeral-db.ts",
};
```

```javascript
// test-config/reset-state.ts
afterEach(() => {
  // Reset any singletons or caches between tests
  resetCache();
  resetEventEmitters();
});
```

The custom random sequencer shuffles test execution per run; the
50% workers run tests in parallel; the per-test reset prevents
inter-test state leak.

## Pattern C: Awaitility for asynchronous condition waits

```java
@Test
void backgroundJobCompletes() {
    Order order = orderFixture.create();
    queueService.enqueue("process", order.getId());

    Awaitility.await()
        .atMost(Duration.ofSeconds(5))
        .pollInterval(Duration.ofMillis(50))
        .untilAsserted(() ->
            assertThat(orderRepo.findById(order.getId()).getStatus())
                .isEqualTo("processed"));
}
```

The condition is the test's actual requirement; the framework
polls with a bounded timeout; no fixed sleep is used.

## Pattern D: frozen time for time-dependent tests

```python
from freezegun import freeze_time
from datetime import datetime, timedelta

@freeze_time("2026-05-25 12:00:00")
def test_token_expires_after_one_hour():
    token = auth.issue_token(user_id="u-1", ttl_minutes=60)

    assert auth.verify(token).valid is True

    with freeze_time("2026-05-25 13:01:00"):
        assert auth.verify(token).valid is False
        assert auth.verify(token).reason == "expired"
```

The test asserts behavior at specific simulated times; no real
wall-clock elapses; the test is deterministic regardless of when
it runs.

## Pattern E: flake quarantine with sunset

```python
# tests/conftest.py
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "quarantine" in item.keywords:
            item.add_marker(pytest.mark.flaky)
```

```python
# tests/integration/test_payment_processor.py
@pytest.mark.quarantine
def test_payment_callback_under_concurrent_load():
    """
    issue-456: intermittent failure when external sandbox is rate-
    limited. Quarantined 2026-04-15. Sunset 2026-06-15 (delete
    if not fixed).
    """
    ...
```

```yaml
# .github/workflows/test.yml
- name: run quarantined separately
  run: pytest tests/ -m "quarantine" --no-cov || true  # do not gate build
  continue-on-error: true
```

Quarantined tests run in their own non-blocking CI step. The
sunset date is in a comment so the team knows when to delete
the test if not fixed.

## Pattern F: flake observability dashboard

```python
# ci/publish_flake_metrics.py
def publish_flake_report():
    """Run nightly; computes per-test flake rate over last 30 days."""
    for test_id, history in get_test_history(days=30).items():
        if has_alternating_outcomes(history):
            metrics_backend.gauge(
                f"test.flake_rate.{test_id}",
                compute_flake_rate(history),
            )

    flake_rate_global = aggregate_global_flake_rate()
    if flake_rate_global > 0.01:
        post_to_team_channel(
            f"Flake rate above threshold: {flake_rate_global:.2%}. "
            f"Top offenders: {top_n_flakiest(5)}"
        )
```

The dashboard makes flake rate visible. When it crosses the
substrate-recommended 1% threshold, the team is notified for
review.

## Pattern G: CI verification of determinism scenarios

```yaml
# .github/workflows/nightly-determinism.yml
name: nightly determinism check
on:
  schedule:
    - cron: "0 4 * * *"

jobs:
  repeated-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: run suite 10 times, compare outcomes
        run: |
          for i in $(seq 1 10); do
            pytest tests/ --no-cov -q > "run-$i.txt"
          done
          python ci/check_determinism.py run-*.txt
```

The scheduled job verifies that the suite produces identical
outcomes across 10 consecutive runs. Per-test flake events
trigger investigation tickets.
