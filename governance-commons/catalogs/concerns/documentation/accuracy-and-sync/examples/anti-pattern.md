<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.accuracy-and-sync accuracy and sync (anti-pattern)

Substrate-original anti-pattern example for documentation.accuracy-and-sync. The code changed and
the documentation was left describing the old behavior.

## Stale reference documentation (illustrative)

```markdown
## POST /invoices/{id}/settle

Body: { "amount": 1.50 }   <!-- documents a float in dollars -->
Returns 200 with the settlement record.
```

```python
# the code now requires integer cents and returns 202, not 200
def settle(invoice_id: str, amount_cents: int) -> Response:
    ...
    return Response(status=202, body=settlement)
```

The document still says dollars-as-float and 200; the code requires
integer cents and returns 202. A reader integrates against the document and
fails. Nothing verifies the example, so the drift is invisible until it
causes a misintegration. Update the doc within the change and execute the
example so drift fails a check.
