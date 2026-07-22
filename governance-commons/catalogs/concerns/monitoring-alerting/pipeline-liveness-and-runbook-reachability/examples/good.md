<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.pipeline-liveness-and-runbook-reachability pipeline liveness and runbook reachability (good pattern)

Substrate-original illustration.

```yaml
# A dead-man's-switch heartbeat pages an external receiver if it stops.
groups:
  - name: meta-monitoring
    rules:
      - alert: AlertingPipelineHeartbeat
        expr: vector(1)            # always firing under normal operation
        labels: { severity: heartbeat }
        annotations:
          runbook_url: "https://runbooks.example.com/heartbeat"  # resolves
# The heartbeat is forwarded to an external dead-man's-switch provider that
# pages if the heartbeat stops arriving (delivery independent of this pipeline).
```

## Why this satisfies the rule

A constantly-firing heartbeat is forwarded to an external dead-man's-switch
that pages precisely when the heartbeat stops, so a dead scraper or crashed
rules engine becomes an alert rather than silence, and the alarm is delivered
by a path the failure cannot also take down. The runbook_url that observability.alerting-discipline
requires on paging alerts resolves to a live document, so the link pays off.
