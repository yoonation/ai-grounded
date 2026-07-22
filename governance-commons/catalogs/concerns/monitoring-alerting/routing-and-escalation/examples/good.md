<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.routing-and-escalation routing and escalation (good pattern)

Substrate-original illustration.

```yaml
# Severity drives the route; an unacknowledged page escalates to a secondary.
route:
  receiver: ticket-queue
  routes:
    - matchers: [severity="critical"]
      receiver: oncall-primary
      # escalation handled by the pager policy below
receivers:
  - name: oncall-primary
    pagerduty_configs: [{ service_key_file: /etc/keys/pd }]
  - name: ticket-queue
    webhook_configs: [{ url_file: /etc/hooks/tickets }]
# Pager escalation policy (vendor): unacked critical escalates after 5m.
escalation_policy:
  - notify: primary-oncall
  - after_minutes: 5
    notify: secondary-oncall   # backstop if the primary does not ack
```

## Why this satisfies the rule

Critical-severity alerts route to a paging receiver that notifies the on-call
responder, and the escalation policy escalates an unacknowledged page to the
secondary after five minutes. A caught incident reaches a human, and an
unavailable primary does not leave it unhandled. The severity label is consumed
from observability.alerting-discipline and the routes resolve per monitoring-alerting.alert-route-resolves-to-receiver.
