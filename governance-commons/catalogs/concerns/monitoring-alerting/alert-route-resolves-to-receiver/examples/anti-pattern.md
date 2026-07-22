<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.alert-route-resolves-to-receiver alert route resolves to a receiver (anti-pattern)

Substrate-original illustration.

```yaml
# Alertmanager config: a route points at a receiver that does not exist.
route:
  receiver: default          # root receiver is never defined below
  routes:
    - matchers: [severity="critical"]
      receiver: oncall-pager  # typo or renamed; not in receivers list
receivers:
  - name: oncall_pager       # name mismatch: underscore vs hyphen
    pagerduty_configs: [{ service_key_file: /etc/keys/pd }]
```

## Why this violates the rule

The root route names "default" and the critical route names "oncall-pager", but
neither is defined in the receivers list (the only receiver is "oncall_pager",
a name mismatch). A critical alert fires, finds no matching receiver, and is
silently dropped: the condition is detected, the config looks populated, and
nobody is paged. The gap is invisible until an incident exposes it.
