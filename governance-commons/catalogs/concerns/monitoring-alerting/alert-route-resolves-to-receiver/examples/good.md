<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.alert-route-resolves-to-receiver alert route resolves to a receiver (good pattern)

Substrate-original illustration.

```yaml
# Alertmanager config: every route resolves to a defined, non-empty receiver.
route:
  receiver: default-pager        # root route has a real receiver
  routes:
    - matchers: [severity="critical"]
      receiver: oncall-pager
    - matchers: [severity="warning"]
      receiver: ticket-queue
receivers:
  - name: default-pager
    pagerduty_configs: [{ service_key_file: /etc/keys/pd }]
  - name: oncall-pager
    pagerduty_configs: [{ service_key_file: /etc/keys/pd }]
  - name: ticket-queue
    webhook_configs: [{ url_file: /etc/hooks/tickets }]
```

## Why this satisfies the rule

Every route, including the root, names a receiver that is defined in the
receivers list and carries a real notification integration. When any alert
fires it terminates at a destination that delivers, so nothing is silently
dropped. This is the delivery floor beneath the alert-rule hygiene observability.alerting-discipline
owns; whether the integration is reachable at runtime is the monitoring-alerting.pipeline-liveness-and-runbook-reachability test.
