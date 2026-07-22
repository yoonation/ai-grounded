<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.on-call-rotation-coverage on-call rotation coverage (anti-pattern)

Substrate-original illustration.

```text
On-call rotation: Checkout service
  Coverage:  Monday to Friday, 09:00 to 18:00 only
  Weekends:  "best effort" (no named owner)
  Handoff:   none documented
  Escalation targets (monitoring-alerting.routing-and-escalation): point at "Jess" who left the team in March
```

## Why this violates the rule

The rotation leaves nights and weekends unowned, so a Saturday page escalates
and reaches no one, and the escalation target names a departed engineer. The
routing and escalation chain monitoring-alerting.routing-and-escalation builds is decorative if no human is on
the other end. Coverage gaps and stale handoffs are the quiet failures this
review exists to catch.
