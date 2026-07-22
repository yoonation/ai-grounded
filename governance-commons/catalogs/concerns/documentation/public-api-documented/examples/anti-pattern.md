<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.public-api-documented public API documented (anti-patterns)

Substrate-original anti-pattern examples for documentation.public-api-documented. An exported symbol
carries no doc comment, forcing consumers to read the implementation.

## Python: an undocumented public function

```python
def settle_invoice(invoice_id: str, amount_cents: int) -> SettlementResult:
    # no docstring: callers must read the body to learn it raises on mismatch
    ...
```

## Go: an undocumented exported identifier

```go
func SettleInvoice(id string, amountCents int64) (SettlementResult, error) {
    // no doc comment on an exported function
    ...
}
```

The public contract gives a consumer nothing to read, so they reverse-
engineer behavior from internals and couple to details they should not.
Add a doc comment stating purpose and contract.
