<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.on-call-rotation-coverage on-call rotation coverage (good pattern)

Substrate-original illustration.

```text
On-call rotation: Checkout service (documented in the team handbook)
  Coverage:  every hour, every day, including weekends and holidays
  Schedule:  primary + secondary, weekly rotation, Monday 10:00 handoff
  Handoff:   outgoing responder briefs incoming on open incidents at handoff;
             overlap window of 30 minutes so coverage never lapses
  Holidays:  a holiday sub-schedule names an owner for every covered date
  Escalation targets (monitoring-alerting.routing-and-escalation) reference the current rotation, not names
```

## Why this satisfies the rule

The rotation covers every hour with no unowned window, defines a handoff with an
overlap so coverage does not lapse at the boundary, names a holiday owner, and
its escalation targets reference the live rotation. A page fired at any time
reaches a responsible human. This is review-only because a rotation is an
organizational artifact no application-source test settles.
