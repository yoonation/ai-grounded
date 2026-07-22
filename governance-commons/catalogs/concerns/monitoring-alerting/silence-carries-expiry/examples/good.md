<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.silence-carries-expiry silence carries an expiry (good pattern)

Substrate-original illustration.

```yaml
# A silence carries a bounded expiry after which the condition is re-evaluated.
silences:
  - matchers: [alertname="HighLatencyCheckoutFlow"]
    startsAt: "2026-06-03T02:00:00Z"
    endsAt:   "2026-06-03T06:00:00Z"   # bounded; lapses in four hours
    comment:  "Muting during the known maintenance window; reopens after."
```

## Why this satisfies the rule

The silence carries an explicit endsAt, so it lapses after the maintenance
window and the alert is live again. Suppression is used as the temporary
operational tool it is meant to be. Whether the silence should exist at all is
the monitoring-alerting.alert-lifecycle lifecycle review; this floor only requires that it expires.
