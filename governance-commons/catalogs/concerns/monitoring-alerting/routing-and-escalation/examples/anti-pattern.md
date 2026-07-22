<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.routing-and-escalation routing and escalation (anti-pattern)

Substrate-original illustration.

```yaml
# A critical alert routes to a shared email with no paging and no escalation.
route:
  receiver: team-email
  routes:
    - matchers: [severity="critical"]
      receiver: team-email     # critical lands in a mailbox, no paging
receivers:
  - name: team-email
    email_configs: [{ to: "team@example.com" }]
# no escalation policy
```

## Why this violates the rule

The critical alert routes to a shared mailbox that no one is paged on, so it
sits unread until business hours, and there is no escalation to recover a missed
notification. The incident is detected and unhandled, the same outcome as not
detecting it. Severity should drive a paging path with a backstop, which is the
operations layer observability defers to this concern.
