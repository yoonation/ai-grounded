<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.pipeline-liveness-and-runbook-reachability pipeline liveness and runbook reachability (anti-pattern)

Substrate-original illustration.

```yaml
# No heartbeat, and runbook links point at deleted pages.
groups:
  - name: checkout
    rules:
      - alert: CheckoutErrorRateHigh
        expr: job:checkout_errors:ratio5m > 0.02
        annotations:
          runbook_url: "https://wiki.example.com/old/deleted-page"  # 404
# no heartbeat / dead-man's-switch anywhere
```

## Why this violates the rule

There is no heartbeat, so when the alerting pipeline dies every alert goes
silent and the quiet dashboard reads as health. The one runbook link present
points at a deleted page that 404s, so even when an alert does fire the
responder has no usable response. Meta-monitoring is the backstop whose absence
turns a five-minute blind spot into a five-hour one.
