<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: monitoring-alerting.alerting-strategy alerting strategy (good pattern)

Substrate-original illustration.

```text
ADR-014: Alerting strategy for the Checkout service
  Coverage philosophy:   symptom-based + SLO-burn (SLOs from ADR-009 / observability.slo-policy)
  Severity-to-routing:   critical -> pager; warning -> ticket; info -> log sink
  Escalation + on-call:  primary + secondary; unacked critical escalates at 5m;
                         weekly rotation, every-hour coverage (see rotation doc)
  Alert lifecycle:       ack supported; silences require expiry; auto-resolve on
  Meta-monitoring:       external dead-man's-switch heartbeat
  Feedback loop:         post-incident review asks "was it alerted?" and "was it
                         noise?"; gaps and noise feed back into the rules
  Owner / review:        SRE lead; reviewed quarterly and after any incident
```

## Why this satisfies the rule

The ADR records each sub-decision the L1 and L2 rules conform to: the coverage
philosophy (anchoring monitoring-alerting.detection-coverage), the routing matrix (monitoring-alerting.routing-and-escalation), the
escalation and on-call model (monitoring-alerting.routing-and-escalation, monitoring-alerting.on-call-rotation-coverage), the lifecycle
(monitoring-alerting.alert-lifecycle), the meta-monitoring approach (monitoring-alerting.pipeline-liveness-and-runbook-reachability), and the feedback loop.
It references the SLOs observability.slo-policy owns and the hygiene observability.alerting-discipline owns rather
than restating them, so the parts cohere into one operable strategy.
