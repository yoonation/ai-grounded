<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.public-api-documented public API documented (good patterns)

Substrate-original good-pattern examples for documentation.public-api-documented. Every exported
symbol carries a doc comment that states its purpose and contract.

## Python: a documented public function

```python
def settle_invoice(invoice_id: str, amount_cents: int) -> SettlementResult:
    """Settle an open invoice and return the settlement outcome.

    Raises InvoiceNotFound if the invoice does not exist, and
    AmountMismatch if amount_cents does not equal the invoice balance.
    """
    ...
```

## Go: a documented exported identifier

```go
// SettleInvoice settles an open invoice and returns the settlement
// outcome. It returns ErrInvoiceNotFound when the invoice is unknown.
func SettleInvoice(id string, amountCents int64) (SettlementResult, error) {
    ...
}
```

Each public contract is self-describing at the point of definition, so a
consumer reads the doc comment rather than the implementation.
