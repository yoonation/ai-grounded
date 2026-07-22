<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.no-classified-data-in-logs no classified data in logs (good pattern)

Substrate-original illustration.

```python
# Log a non-sensitive identifier, never the confidential field itself.
def process_order(logger, order):
    logger.info("processing order", extra={"order_id": order.id})
    charge_card(order)
    logger.info("order charged", extra={"order_id": order.id})
```

## Why this satisfies the rule

The log lines record the order identifier, a non-sensitive reference, rather
than the confidential customer or payment fields. An operator reading the
aggregated logs can trace the order without ever seeing classified data,
which keeps that data inside the per-class controls the rest of the system
enforces.
