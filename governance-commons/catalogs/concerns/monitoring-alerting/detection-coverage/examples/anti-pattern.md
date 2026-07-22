<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.detection-coverage detection coverage (anti-pattern)

Substrate-original illustration.

```yaml
# Alerts exist only for causes, none for the user-facing symptom.
groups:
  - name: checkout-coverage
    rules:
      - alert: NodeCPUHigh           # cause-level only
        expr: instance:cpu:ratio5m > 0.9
      - alert: DiskSpaceLow          # cause-level only
        expr: instance:disk_free:ratio < 0.1
      # no alert on checkout error rate, latency, or SLO burn
```

## Why this violates the rule

The service alerts on CPU and disk but has no alert on the user-facing error
rate, latency, or SLO burn. When checkout starts failing, no alert fires; the
outage is reported by a customer before it is seen internally. Cause-level
alerts catch some problems early but cannot substitute for symptom coverage,
and their noise is what drives alert fatigue.
