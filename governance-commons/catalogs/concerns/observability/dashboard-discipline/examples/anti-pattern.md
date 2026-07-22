<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.dashboard-discipline dashboard discipline (anti-patterns)

Substrate-original anti-pattern examples for observability.dashboard-discipline.

## Anti-pattern A: No declared methodology

```
Dashboard: payments-api overview
Tags: (none)

Panels (in order of authoring):
  1. Request rate
  2. Database query time
  3. Total revenue (last 24h)
  4. p99 latency
  5. Customer support tickets opened
  6. Kafka lag
  7. Error count
  8. JVM heap usage
  9. ... (continues for 30 more panels)
```

Why this violates observability.dashboard-discipline: no methodology is declared.
Operators reverse-engineer the layout per dashboard. Panels
mix request-driven signals (rate, latency, errors), resource-
constrained signals (heap, queue lag), business metrics
(revenue, tickets), and operational metrics (database query
time) without organization. Under incident pressure, the
operator scrolls through 38 panels trying to find the
relevant one.

Remediation: choose a methodology appropriate to the service
(RED for the request-driven view, USE for the resource view,
or both as composite); split the dashboard into methodology-
organized dashboards plus a separate business-metrics
dashboard.

## Anti-pattern B: RED dashboard missing duration

```
Dashboard: payments-api RED
Methodology: RED

Panels:
  - Request rate
  - Error rate
  - Request count by status
  - Request count by tenant
  - Error count by endpoint
```

Why this violates observability.dashboard-discipline: methodology declared as RED
but the duration signal is missing entirely. RED is rate +
errors + duration; without duration, the dashboard cannot
answer latency questions. The discipline violation may go
undetected because the dashboard looks busy and
methodology-tagged.

Remediation: add duration panels (p50/p95/p99 latency, by
endpoint where useful). The observability.dashboard-discipline test template
Scenario 2 catches this in CI.

## Anti-pattern C: SLI panels mixed with operational panels

```
Dashboard: payments-api everything
Tags: (none)

Row 1 - SLI
  Panel: SLO compliance (28-day rolling)
  Panel: Error budget remaining

Row 2 - RED
  Panel: Rate / Errors / Duration

Row 3 - Database
  Panel: Connection pool / Query latency

Row 4 - Infrastructure
  Panel: CPU / Memory / Disk

Row 5 - Business
  Panel: Revenue / Refund rate
```

Why this violates observability.dashboard-discipline: SLI panels are mixed with
operational and business panels on a single dashboard. The
executive looking for "are we meeting our SLO?" must scroll
through engineering and business panels. The on-call
responder looking for engineering signals must scroll
through SLI and business panels. Both audiences are degraded
by the mixing.

Remediation: extract SLI panels to a separate pinned SLI
dashboard (good-pattern Pattern C); keep operational
panels on methodology-organized dashboards; cross-link from
the operational dashboard to the SLI dashboard.

## Anti-pattern D: Panel count exceeds visual scan ceiling

```
Dashboard: payments-api production
Panels: 47

Layout:
  Row 1: 12 panels (CPU per replica, one per replica name)
  Row 2: 8 panels (memory per replica)
  Row 3: 8 panels (disk per replica)
  Row 4: 6 panels (errors per endpoint)
  Row 5: 6 panels (latency per endpoint)
  Row 6: 7 panels (database query time per query type)
```

Why this violates observability.dashboard-discipline: 47 panels exceeds the
substrate-recommended ceiling of roughly 20. The
per-replica panels are operationally wrong: dashboards
should aggregate across replicas (a single CPU panel with
per-replica series), not show one panel per replica.

Remediation: aggregate per-replica into single panels
showing all replicas as series on one panel; reduce per-
endpoint expansion using a single panel with a topk
function; if the consumer genuinely needs deep per-replica
breakdown, that lives on a subsidiary diagnostic dashboard
cross-linked from the parent.

## Anti-pattern E: Per-panel time range overrides creating confusion

```
Dashboard time range: last 1 hour
  Panel 1 (Rate): overridden to last 24 hours
  Panel 2 (Errors): default (last 1 hour)
  Panel 3 (Duration): overridden to last 7 days
  Panel 4 (DB): overridden to last 5 minutes
```

Why this violates observability.dashboard-discipline: each panel shows a different
time window without a documented reason. The operator
comparing rate (24h) against errors (1h) gets a misleading
view; "current spike" interpretations depend on which panel
the operator is looking at.

Remediation: use a single dashboard-level time range;
panel-level overrides exist only for specific comparative
purposes (a "weekly comparison" panel deliberately showing
last 7 days alongside last 1 hour) and are labeled to
communicate the override.

## Anti-pattern F: Cross-references that break on dashboard rename

```
Alert annotation:
  dashboard_url: "https://grafana.internal.example/d/abc123/payments-api"
```

The dashboard was renamed last quarter; the slug "payments-
api" became "payments-api-v2"; the alert URL now redirects
to a generic dashboard list page.

Why this violates observability.dashboard-discipline: cross-references rot when
dashboards are renamed without a stable identifier. The
substrate-recommended pattern is to reference by stable
dashboard UID (abc123 portion) so renames preserve the link.

Remediation: link by UID; periodic CI check verifies all
alert dashboard_url annotations resolve to live dashboards.

## Anti-pattern G: Refresh rate misconfigured for analytical dashboards

A long-running analytical dashboard (intended for periodic
review of weekly trends) is set to refresh every 5 seconds.
Each refresh issues 30 queries against the backend; the
dashboard generates substantial backend load for no
operational benefit.

Why this violates observability.dashboard-discipline sub-discipline: refresh rate
should match the dashboard's use case. Live refresh is for
incident-response dashboards where seconds matter;
analytical dashboards need refresh rates measured in
minutes or hours.

Remediation: set refresh rate by dashboard type. The
substrate-recommended starting cadence: 30s for incident-
response dashboards, 5m for operational status dashboards,
manual refresh for analytical dashboards.

## Cross-reference

- Substrate rule: observability.dashboard-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Good-pattern examples: examples/observability/dashboard-discipline-good.md
