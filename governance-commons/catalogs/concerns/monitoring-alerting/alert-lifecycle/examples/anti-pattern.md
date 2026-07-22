<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.alert-lifecycle alert lifecycle (anti-pattern)

Substrate-original illustration.

```yaml
# The alert never resolves; the responder cannot tell it is stale.
groups:
  - name: checkout
    rules:
      - alert: CheckoutErrorRateHigh
        expr: job:checkout_errors:ratio5m > 0.02
receivers:
  - name: oncall-primary
    pagerduty_configs:
      - { service_key_file: /etc/keys/pd, send_resolved: false }  # no resolve
```

## Why this violates the rule

The receiver has send_resolved false, so when the error rate recovers the alert
keeps showing as firing and no resolution notification is sent. The responder
cannot tell whether the condition is still active or cleared an hour ago. Stale
firing alerts teach a team to ignore alerting, the slow erosion of trust the
lifecycle exists to prevent.
