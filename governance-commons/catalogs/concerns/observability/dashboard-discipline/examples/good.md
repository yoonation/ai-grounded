<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.dashboard-discipline dashboard discipline (good patterns)

Substrate-original good-pattern examples for observability.dashboard-discipline.

## Pattern A: RED-organized dashboard structure (Grafana)

```
Dashboard: payments-api RED
Methodology declared: RED (rate, errors, duration)
Tags: methodology:red, service:payments-api

Row 1 - Rate
  Panel: Request rate (req/s) by endpoint
    Query: sum by (endpoint) (rate(api_requests_total{service="payments-api"}[5m]))
  Panel: Request rate by status class (2xx, 4xx, 5xx)
    Query: sum by (status) (rate(api_requests_total{service="payments-api"}[5m]))

Row 2 - Errors
  Panel: Error rate (5xx ratio)
    Query: rate(api_requests_total{service="payments-api",status=~"5.."}[5m])
           / rate(api_requests_total{service="payments-api"}[5m])
  Panel: Error rate by endpoint
    Query: sum by (endpoint) (rate(api_requests_total{service="payments-api",status=~"5.."}[5m]))
           / sum by (endpoint) (rate(api_requests_total{service="payments-api"}[5m]))

Row 3 - Duration
  Panel: p50/p95/p99 latency
  Panel: p99 latency by endpoint
  Panel: Latency heatmap

Cross-links (bottom):
  - SLI dashboard: https://grafana.internal.example/d/payments-sli
  - Alert rules: alerts/payments-api.yml
  - SLO ADR: /docs/decisions/ADR-014-payments-slo-policy.md

Refresh: 30s; Time range: last 1h (dashboard-level)
```

Why this satisfies observability.dashboard-discipline: methodology declared in
title and tags; rate, errors, duration each have a labeled
row; panel count ~7 fits a typical screen; cross-links to
SLI dashboard, alert rules, and SLO ADR are explicit;
dashboard-level time range and refresh keep panels
consistent.

## Pattern B: USE-organized dashboard for resource-constrained component

```
Dashboard: payments-database USE
Methodology declared: USE (utilization, saturation, errors)
Tags: methodology:use, service:payments-database

Section 1 - Utilization
  Panel: CPU utilization (per replica)
  Panel: Memory utilization
  Panel: Disk I/O utilization
  Panel: Connection pool utilization (active / max)

Section 2 - Saturation
  Panel: CPU run-queue length
  Panel: Query queue depth
  Panel: Connection pool waiting (clients waiting on connection)
  Panel: Disk I/O queue length

Section 3 - Errors
  Panel: Query errors per minute (categorized)
  Panel: Connection errors per minute
  Panel: Replication lag (per replica)

Refresh: 30s; Time range: last 1h
```

Why this satisfies observability.dashboard-discipline: USE methodology declared and
appropriate to the resource-constrained component; all three
required signal categories (utilization, saturation, errors)
present with labeled sections; each tracked resource (CPU,
memory, disk, connections) appears under each applicable
signal.

## Pattern C: SLI dashboard, separate and pinned

```
Dashboard: payments-api SLI (pinned at top of navigation)
Tags: methodology:sli, service:payments-api

Top panel (large): Current SLO compliance
  - Target: 99.9% availability (from ADR-014)
  - Current 28-day rolling: 99.94%
  - Budget remaining: 38% (of monthly budget)

Panel: Burn rate (1h window) with alert threshold overlay
Panel: Burn rate (6h window) with alert threshold overlay
Panel: Error budget consumption over 28-day window
Panel: SLI ratio over 28-day window

Single big-number panel: Budget remaining (with color band)
  - Green: > 50%
  - Yellow: 20% to 50%
  - Red: < 20%

Cross-link (top): SLO ADR /docs/decisions/ADR-014-payments-slo-policy.md
Cross-link (top): Operational RED dashboard https://grafana.internal.example/d/payments-red

Refresh: 1m; Time range: last 28d (dashboard-level)
```

Why this satisfies observability.dashboard-discipline and observability.slo-policy together: the
SLI dashboard is separate from operational dashboards
(no operational panels mixed in); it is pinned to the top
of navigation per the substrate-recommended discoverability
pattern; the SLI computation cross-references the ADR; the
dashboard answers the executive question (is the service
meeting its commitment?) without mixing in the engineering
question.

## Pattern D: Cross-reference convention

```
Standard cross-link footer on every operational dashboard:

| Reference          | Link                                           |
|--------------------|------------------------------------------------|
| SLI dashboard      | https://grafana.internal.example/d/{service}-sli |
| Alert rules        | alerts/{service}.yml (in service repo)        |
| SLO ADR            | /docs/decisions/ADR-XXX-{service}-slo-policy.md |
| Service catalog    | https://catalog.internal.example/{service}    |
| On-call runbooks   | https://runbooks.internal.example/{service}   |
```

Why this satisfies observability.dashboard-discipline: a consistent cross-link
template across the consumer's dashboard catalog; operators
expect the same five references on every operational
dashboard; the substrate-recommended dashboard-as-code
templating produces this footer automatically rather than
relying on per-dashboard authoring.

## Pattern E: Quarterly dashboard sweep document

```markdown
# Quarterly Dashboard Sweep: payments-api (2026-05-15)

| Dashboard                     | Action                | Rationale                              |
|-------------------------------|------------------------|----------------------------------------|
| payments-api RED              | Keep                  | Reflects current service architecture  |
| payments-api SLI              | Keep                  | SLO ADR-014 unchanged                  |
| payments-api troubleshooting  | Restructure           | Drifted to 35 panels; split into two   |
| payments-database USE         | Keep                  | Resource set unchanged                 |
| payments-archive (deprecated) | Retire                | Service archived 2026-03; remove links |

Sweep performed by: myoung
Next sweep: 2026-08-15
```

Why this satisfies observability.dashboard-discipline: the sweep cadence is
documented; each dashboard's status is reviewed; dashboards
that have drifted from their methodology are restructured;
dashboards for retired services are removed.

## Cross-reference

- Substrate rule: observability.dashboard-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Anti-pattern examples: examples/observability/dashboard-discipline-anti-pattern.md
- Related: observability.slo-policy (SLI dashboard content); observability.alerting-discipline (alert-to-dashboard cross-references)
