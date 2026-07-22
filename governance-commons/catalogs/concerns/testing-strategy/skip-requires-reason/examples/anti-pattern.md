<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.skip-requires-reason skip without rationale

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: bare pytest skip

```python
import pytest

@pytest.mark.skip
def test_payment_authorization_with_retry():
    ...

@pytest.mark.skip()
def test_user_signup_with_email_verification():
    ...
```

Bare `@pytest.mark.skip` without a `reason` argument is the
substrate-rejected form. Six months from now no one remembers
why the skip was added; the skip persists indefinitely as dead
test code that no longer protects the behavior it once verified.

## Anti-pattern B: Jest skip with no comment

```javascript
describe.skip("PaymentService", () => {
  it("processes payment with valid card", async () => {
    ...
  });
});

xit("retries on transient network failure", async () => {
  ...
});
```

The `describe.skip` and the `xit` form have no associated
rationale. The L2 review will reject them; the L1 mechanical
check flags them at PR time. Contributors do not know whether
the test was skipped because it was flaky, because the feature
was deprecated, or because someone forgot to remove the skip
after debugging.

## Anti-pattern C: JUnit @Disabled with no argument

```java
@Disabled
@Test
void shouldReconcileAccountBalanceWithLedger() {
    ...
}

@Ignore
public void testLegacyAccountMigration() {
    ...
}
```

`@Disabled` without an argument and `@Ignore` without value both
suppress the test silently. The substrate-required form includes
an issue identifier and rationale.

## Anti-pattern D: Go t.SkipNow without context

```go
func TestKafkaConsumerRebalance(t *testing.T) {
    t.SkipNow()
    // ... test body
}

func TestSlowIntegration(t *testing.T) {
    if shouldSkip() {
        t.Skip()
    }
    // ...
}
```

`t.SkipNow()` with no message and `t.Skip()` with no argument
produce a skip with no diagnostic information. The substrate-
required form passes a string with the rationale.

## Anti-pattern E: RSpec xit with empty description

```ruby
RSpec.describe PaymentProcessor do
  xit "handles 3DS challenge flow" do
    # body that may or may not still match the description
  end

  it "processes refund" do
    skip  # no reason
    expect(processor.refund(order)).to be_success
  end
end
```

`xit` and `skip` without a description are bare skips that
accumulate as silent test debt. The description string is the
substrate-acceptable rationale carrier.

## Why these forms accumulate

Bare skips are easy to add (one keyword, one line); the cost
of leaving them is invisible at PR time but compounds as the
test suite ages. The substrate's L1 rule catches the missing-
rationale case at the syntactic layer; the L2 review (when the
checklist is followed) catches the missing-reason-quality case
where the rationale is "todo" or "wip" rather than an actionable
issue reference.
