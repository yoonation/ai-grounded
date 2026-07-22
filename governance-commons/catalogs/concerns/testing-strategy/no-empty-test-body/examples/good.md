<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: testing-strategy.no-empty-test-body tests with substantive assertions

Substrate-original good patterns. Adapt to your stack.

## Pattern A: pytest with direct assertions

```python
import pytest
from app.calculator import compute_total

def test_compute_total_with_tax():
    result = compute_total(subtotal=100, tax_rate=0.08)
    assert result == 108

def test_compute_total_rejects_negative_subtotal():
    with pytest.raises(ValueError, match="subtotal must be non-negative"):
        compute_total(subtotal=-1, tax_rate=0.08)

def test_compute_total_clamps_tax_rate_to_unity():
    result = compute_total(subtotal=100, tax_rate=1.5)
    assert result == 200  # rate clamped to 1.0
```

Each test function exercises a specific behavior and asserts the
specific outcome. The `pytest.raises` context manager is itself
an assertion (the test fails if the call does not raise).

## Pattern B: Jest with expect matchers

```javascript
import { processOrder } from "../src/orders";

describe("processOrder", () => {
  it("applies the discount before tax", () => {
    const result = processOrder({ subtotal: 100, discount: 10, taxRate: 0.08 });
    expect(result.total).toBe(97.2);
  });

  it("rejects orders with no line items", () => {
    expect(() => processOrder({ lineItems: [] })).toThrow("no line items");
  });

  it("returns idempotent results for the same input", () => {
    const input = { subtotal: 50, discount: 5, taxRate: 0.10 };
    expect(processOrder(input)).toEqual(processOrder(input));
  });
});
```

Each `it` block contains at least one `expect` invocation. The
substrate-acceptable form uses framework matchers
(`toBe`, `toEqual`, `toThrow`); custom helpers that ultimately
invoke `expect` are also acceptable when configured in the
linter's assertion-name list.

## Pattern C: JUnit 5 with AssertJ

```java
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class OrderServiceTest {

    @Test
    void shouldComputeTotalIncludingTaxAndDiscount() {
        Order order = new Order(100, BigDecimal.valueOf(10), 0.08);
        OrderTotal total = service.computeTotal(order);
        assertThat(total.amount()).isEqualByComparingTo("97.20");
    }

    @Test
    void shouldRejectOrderWithNegativeSubtotal() {
        assertThatThrownBy(() -> service.computeTotal(new Order(-1, ZERO, 0)))
            .isInstanceOf(IllegalArgumentException.class)
            .hasMessageContaining("subtotal");
    }
}
```

Each `@Test` method invokes `assertThat` (or `assertThatThrownBy`,
which is itself an assertion).

## Pattern D: Go with substantive t.Errorf

```go
func TestComputeTotalWithTax(t *testing.T) {
    got := ComputeTotal(100, 0.08)
    want := 108
    if got != want {
        t.Errorf("ComputeTotal(100, 0.08) = %d; want %d", got, want)
    }
}

func TestComputeTotalRejectsNegativeSubtotal(t *testing.T) {
    _, err := ComputeTotalSafe(-1, 0.08)
    if err == nil {
        t.Fatal("expected error for negative subtotal; got nil")
    }
    if !strings.Contains(err.Error(), "non-negative") {
        t.Errorf("error = %q; want substring 'non-negative'", err)
    }
}
```

Each Test* function invokes at least one of `t.Error`,
`t.Errorf`, or `t.Fatal`. The substrate-acceptable form documents
both the expected behavior and the diagnostic for failure.
