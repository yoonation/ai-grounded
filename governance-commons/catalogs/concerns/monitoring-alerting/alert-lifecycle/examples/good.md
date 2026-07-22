<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.alert-lifecycle alert lifecycle (good pattern)

Substrate-original illustration.

```yaml
# Alerts auto-resolve when the condition clears and signal resolution.
groups:
  - name: checkout
    rules:
      - alert: CheckoutErrorRateHigh
        expr: job:checkout_errors:ratio5m > 0.02
        for: 5m                # fires after sustained breach
        # Alertmanager sends a resolved notification when expr is false again,
        # to the same receiver, with send_resolved enabled on the receiver.
receivers:
  - name: oncall-primary
    pagerduty_configs:
      - { service_key_file: /etc/keys/pd, send_resolved: true }
```

## Why this satisfies the rule

The alert fires on a sustained breach, auto-resolves when the error rate falls
back, and sends a resolved notification to the same receiver (send_resolved is
on). The responder is never left staring at a stale firing alert. Silences for
this alert must carry an expiry (monitoring-alerting.silence-carries-expiry), and deduplication keeps a single
root cause from fragmenting into many lifecycles (observability.alerting-discipline).
