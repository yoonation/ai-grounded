<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.alerting-discipline alerting discipline (good patterns)

Substrate-original good-pattern examples for observability.alerting-discipline.

## Pattern A: Complete alert rule with severity, runbook, summary (Prometheus)

```yaml
groups:
  - name: payments-api.rules
    interval: 30s
    rules:
      - alert: PaymentsApiHighErrorRate
        expr: |
          (
            sum(rate(api_requests_total{service="payments-api",status=~"5.."}[5m]))
            /
            sum(rate(api_requests_total{service="payments-api"}[5m]))
          ) > 0.01
        for: 5m
        labels:
          severity: warning
          service: payments-api
          team: payments
        annotations:
          summary: "payments-api error rate above 1 percent over 5 minutes"
          description: |
            5xx rate has exceeded 1 percent of total requests for 5 minutes.
            Investigate via the linked runbook; this is a customer-impacting
            condition.
          runbook_url: "https://runbooks.internal.example/payments-api/high-error-rate"
          dashboard_url: "https://grafana.internal.example/d/payments-red"
          source_of_truth: "alerts/payments-api.yml in payments-api repo"
```

Why this satisfies observability.alerting-discipline: severity label drawn from the
bounded vocabulary; runbook_url linking to a live document;
summary distinguishes this alert from related alerts;
description provides on-call context; dashboard_url cross-
links to the operational dashboard; source_of_truth points to
the authoring location.

## Pattern B: Burn-rate alerting against documented SLO (Prometheus)

```yaml
groups:
  - name: payments-api.slo.rules
    interval: 30s
    rules:
      - alert: PaymentsApiSloFastBurn
        expr: |
          (
            sum(rate(api_requests_total{service="payments-api",status=~"5.."}[1h]))
            /
            sum(rate(api_requests_total{service="payments-api"}[1h]))
          ) > (14.4 * 0.001)
        for: 2m
        labels:
          severity: critical
          slo: payments-api-availability
        annotations:
          summary: "payments-api SLO fast burn (1h window)"
          description: |
            Error rate over the 1-hour window indicates we will exhaust
            the monthly error budget in 2 days at current rate. Pause
            risky deployments and engage incident response.
          runbook_url: "https://runbooks.internal.example/slo-fast-burn"
          slo_adr: "/docs/decisions/ADR-014-payments-slo-policy.md"

      - alert: PaymentsApiSloSlowBurn
        expr: |
          (
            sum(rate(api_requests_total{service="payments-api",status=~"5.."}[6h]))
            /
            sum(rate(api_requests_total{service="payments-api"}[6h]))
          ) > (6 * 0.001)
        for: 15m
        labels:
          severity: warning
          slo: payments-api-availability
        annotations:
          summary: "payments-api SLO slow burn (6h window)"
          runbook_url: "https://runbooks.internal.example/slo-slow-burn"
          slo_adr: "/docs/decisions/ADR-014-payments-slo-policy.md"
```

Why this satisfies observability.alerting-discipline and observability.slo-policy together:
multi-window burn-rate alerting against a documented SLO
(0.001 error budget = 99.9 percent target). The fast-burn
alert (1h window, 14.4x rate) catches acute incidents; the
slow-burn alert (6h window, 6x rate) catches sustained
elevation. The slo_adr annotation links to the SLO policy
document; the alert is operationally meaningful only because
the SLO exists.

## Pattern C: Inhibition for cascade dedup (Alertmanager)

```yaml
inhibit_rules:
  # When the database is down, suppress dependent service error alerts
  # because those alerts are symptoms of the same root cause.
  - source_matchers:
      - alertname = "DatabaseDown"
    target_matchers:
      - alertname =~ "PaymentsApi.*HighErrorRate|OrdersApi.*HighErrorRate"
    equal: ['cluster']

  # When a service's SLO fast burn fires, suppress the related warning
  # alerts on the same service (the responder is already engaged).
  - source_matchers:
      - severity = "critical"
      - slo =~ ".+"
    target_matchers:
      - severity = "warning"
    equal: ['service']
```

Why this satisfies observability.alerting-discipline: cascading symptoms are
suppressed when the root cause is firing; the on-call
responder receives one notification per incident root cause
rather than ten notifications for cascading symptoms.

## Pattern D: Symptom-based detection (Prometheus)

```yaml
- alert: PaymentsApiUserVisibleLatency
  # The customer-facing p99 latency exceeds 2 seconds for 10 minutes.
  # Detection is on the customer-visible symptom; remediation may
  # involve various components (database, downstream APIs, internal
  # queue saturation). The alert fires regardless of underlying cause.
  expr: |
    histogram_quantile(0.99,
      sum by (le) (rate(api_request_duration_seconds_bucket{service="payments-api"}[5m]))
    ) > 2
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "payments-api p99 latency above 2 seconds for 10 minutes"
    runbook_url: "https://runbooks.internal.example/payments-api/high-latency"
```

Why this satisfies observability.alerting-discipline: the alert fires on a customer-
felt symptom (slow API responses), robust to different root
causes producing the same effect. Compare to a cause-based
alert ("database connection pool above 80 percent") that
catches one specific failure mode and misses others.

## Pattern E: Alert sweep finding documentation

```markdown
# Quarterly Alert Sweep: payments-api (2026-05-15)

| Alert                              | Action     | Rationale                                     |
|------------------------------------|------------|-----------------------------------------------|
| PaymentsApiHighErrorRate           | Keep       | Fired 3x last quarter, all acted on           |
| PaymentsApiQueueDepthHigh          | Retire     | Fired 47x, all silenced; queue depth alone is not actionable |
| PaymentsApiDbConnectionPoolHigh    | Convert to ticket | Symptom-based; raising as ticket not page  |
| PaymentsApiSloFastBurn             | Keep       | Anchors customer commitment per ADR-014       |

Sweep performed by: myoung
Next sweep: 2026-08-15
```

Why this satisfies observability.alerting-discipline: the sweep cadence is
documented; each alert's status is reviewed; chronically-
ignored alerts are retired rather than continuing to page.
The retire decision for PaymentsApiQueueDepthHigh follows
the substrate-recommended pattern: an alert no one acts on
is operational noise.

## Cross-reference

- Substrate rule: observability.alerting-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Anti-pattern examples: examples/observability/alerting-discipline-anti-pattern.md
- Related: observability.slo-policy (SLO anchors burn-rate alerting)
