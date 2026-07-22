<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.detection-coverage detection coverage (good pattern)

Substrate-original illustration.

```yaml
# Alerts exist for the user-facing symptoms and the SLO burn, not just causes.
groups:
  - name: checkout-coverage
    rules:
      - alert: CheckoutErrorRateHigh        # symptom: users see failures
        expr: job:checkout_errors:ratio5m > 0.02
      - alert: CheckoutLatencyHigh          # symptom: users wait too long
        expr: job:checkout_latency:p99_5m > 0.8
      - alert: CheckoutSLOErrorBudgetBurn    # SLO burn (SLO from observability.slo-policy)
        expr: checkout:slo_burn_rate_1h > 14.4
```

## Why this satisfies the rule

The critical user-facing failure modes (error rate, latency) and the SLO-burn
condition each have an alert, so a real checkout outage is detected internally.
The SLO itself is observability.slo-policy's decision, referenced here not redefined, and the
per-rule hygiene (severity, runbook, summary) is observability.alerting-discipline. This rule owns the
presence question: the alert for the thing that breaks exists.
