<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.skip-requires-reason skip requires reason

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python pytest with issue-tracked reason

```python
import pytest

@pytest.mark.skip(reason="issue-123: flaky in CI, fix in v2.4")
def test_payment_authorization_with_retry():
    ...

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="issue-456: posix-only fixture; Windows runner support tracked",
)
def test_unix_socket_consumer():
    ...
```

The reason argument is a required keyword for pytest's skip and
skipif decorators. The substrate-acceptable form references an
issue tracker identifier so contributors can grep the skip back
to its source. The reason argument appears in pytest's output
making the skip visible at every test run.

## Pattern B: JavaScript Jest with structured rationale

```javascript
describe.skip("PaymentService", () => {
  // SKIP: issue-789: contract-test failures pending API v2 release.
  // Re-enable after PR #1024 merges.

  it("processes payment with valid card", async () => {
    const result = await processPayment(validCard);
    expect(result.status).toBe("approved");
  });
});

it.todo("retries on transient network failure (issue-1011)");
```

The structured comment makes the skip discoverable; the
substrate-recommended alternative for not-yet-implemented tests
is `it.todo` which produces pending status rather than green.

## Pattern C: Java JUnit 5 with @Disabled argument

```java
@Disabled("issue-234: pending Spring Boot 3.2 upgrade; remove after PR #567")
@Test
void shouldReconcileAccountBalanceWithLedger() {
    BigDecimal expected = ledger.balanceFor(accountId);
    BigDecimal actual = accountingService.computeBalance(accountId);
    assertEquals(expected, actual);
}
```

JUnit 5's `@Disabled` argument is included in test reports; the
substrate-required form always passes a string referencing an
issue.

## Pattern D: Go testing with explicit Skip rationale

```go
func TestKafkaConsumerRebalance(t *testing.T) {
    if testing.Short() {
        t.Skip("issue-345: requires real Kafka; runs only in nightly suite")
    }
    // ... test body
}
```

The `t.Skip` argument is logged with the skip; the rationale
explains why the skip exists and points to the tracking issue.

## Pattern E: Ruby RSpec with documented pending

```ruby
RSpec.describe PaymentProcessor do
  it "handles 3DS challenge flow", pending: "issue-678: 3DS sandbox unavailable" do
    expect(processor.charge(card_3ds)).to be_a(ChallengeRequired)
  end
end
```

RSpec's pending status with description is the substrate-
acceptable form for tests that document expected-future
behavior.
