<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: data-classification.no-classified-data-in-logs no classified data in logs (anti-pattern)

Substrate-original illustration.

```python
# A confidential field interpolated directly into a log line.
def process_order(logger, order):
    logger.info(f"processing order for {order.email}, card {order.card_number}")
    charge_card(order)
```

## Why this violates the rule

The log line interpolates the customer email and the card number, both
classified, directly into the message. Those values are now copied to the log
aggregation system, retained on the log retention schedule rather than the
data's, and readable by everyone with log access and by any observability
vendor the logs are shipped to. A single line like this can be the largest
exposure in an otherwise well-classified system. Logging the order identifier
instead is the fix.
