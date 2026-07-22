<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.silence-carries-expiry silence carries an expiry (anti-pattern)

Substrate-original illustration.

```yaml
# An open-ended silence permanently hides a real alert.
silences:
  - matchers: [alertname="HighLatencyCheckoutFlow"]
    startsAt: "2026-06-03T02:00:00Z"
    # no endsAt: the silence never lapses
    comment:  "Too noisy, muting for now."
```

## Why this violates the rule

The silence has no endsAt, so it never lapses. An operator muted a noisy alert
during an incident, the incident ended, and the mute outlived everyone's memory
of it. The next time checkout latency spikes, nothing fires. A genuinely
permanent suppression should instead be a disabled alert rule with a documented
rationale (the observability.alerting-discipline remediation), not an unbounded silence.
