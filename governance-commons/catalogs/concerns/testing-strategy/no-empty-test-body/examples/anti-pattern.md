<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: testing-strategy.no-empty-test-body empty or assertion-free test bodies

Substrate-original anti-patterns. Do not adopt these forms.

## Anti-pattern A: pytest placeholder bodies

```python
def test_compute_total_with_tax():
    pass  # TODO: implement

def test_user_signup_sends_welcome_email():
    # written during planning; assertions never added
    user = create_user(email="test@example.com")
    send_welcome_email(user)

def test_password_reset_flow():
    user = create_user(email="test@example.com")
    request_password_reset(user.email)
    # never asserted that the reset email was sent or the token was issued
```

Each of these tests reports green when run; none verifies the
behavior the function name claims. The first is an explicit
placeholder; the second and third exercise the code but make no
assertion about the outcome.

## Anti-pattern B: Jest assertion-free tests

```javascript
describe("processOrder", () => {
  it("applies the discount before tax", () => {
    processOrder({ subtotal: 100, discount: 10, taxRate: 0.08 });
    // no expect() invocation; test always passes
  });

  it("handles edge case with zero subtotal", async () => {
    const result = await processOrder({ subtotal: 0 });
    console.log(result);  // logged but never asserted
  });
});
```

Calling the system under test without verifying the result
produces no signal. The `console.log` form is particularly
insidious because it looks intentional but provides no
verification.

## Anti-pattern C: JUnit method with only system-under-test invocation

```java
@Test
void shouldComputeTotalIncludingTaxAndDiscount() {
    Order order = new Order(100, BigDecimal.valueOf(10), 0.08);
    service.computeTotal(order);
    // no assertion against the returned total
}

@Test
void shouldHandleEmptyOrder() {
    Order order = new Order();
    OrderTotal total = service.computeTotal(order);
    System.out.println("Got: " + total);  // visible but not asserted
}
```

The first test does not assert against the return value; the
second logs but does not assert. Both pass regardless of system
behavior.

## Anti-pattern D: Go Test* function without t.Error or t.Fatal

```go
func TestComputeTotalWithTax(t *testing.T) {
    got := ComputeTotal(100, 0.08)
    _ = got  // result discarded
}

func TestComputeTotalEdgeCases(t *testing.T) {
    ComputeTotal(0, 0)
    ComputeTotal(100, 1.0)
    ComputeTotal(1000, 0.5)
    // calls made, no checks performed
}
```

Discarding the result and not calling t.Error / t.Fatal / t.Errorf
means the test cannot fail. Coverage tools report these lines as
covered; the suite reports green; the function is effectively
untested.

## Anti-pattern E: degenerate assertions

```python
def test_user_creation():
    user = create_user(email="test@example.com")
    assert True  # always passes
    assert user  # passes for any truthy value

def test_password_validation():
    result = validate_password("hunter2")
    assert result is not None  # passes when validate returns False
```

`assert True` is always true; `assert user` passes for any non-
None object; `assert result is not None` does not distinguish
True from False. These forms pass the L1 mechanical check (an
assertion is present) but should fail the L2 review for
triviality.

## Why these forms appear

The pattern arises from "I'll fill in the assertions later"
placeholders that never get filled in, copy-paste scaffolding
that does not get the body written, and refactoring that removes
the assertion but leaves the test in place. The L1 mechanical
check catches the first and second cases at PR time; the L2
review catches the third when the assertion was removed but the
test file remained.
