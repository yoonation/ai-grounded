<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.cardinality-discipline cardinality discipline (good patterns)

Substrate-original good-pattern examples for observability.cardinality-discipline.

## Pattern A: Bounded vocabulary documented at registration (Python)

```python
from prometheus_client import Counter

# Bounded vocabularies (documented at registration):
#   tenant_id: up to 1000 tenants (business roadmap ceiling 2027)
#   region: 5 values (us-east-1, us-west-2, eu-west-1, eu-central-1, ap-southeast-2)
#   endpoint: ~80 route templates (current API surface)
#   status: 5 HTTP status classes (2xx, 3xx, 4xx, 5xx, timeout)
# Cartesian product ceiling: 1000 * 5 * 80 * 5 = 2,000,000 series
# Tracked in cardinality-budget.md; reviewed monthly.

api_requests_total = Counter(
    "api_requests_total",
    "API request count.",
    ["tenant_id", "region", "endpoint", "status"],
)
```

Why this satisfies observability.cardinality-discipline: each label has a documented
bounded vocabulary; the cartesian-product ceiling is computed
and tracked; the source-of-truth for the bounds (business
roadmap, deployment topology) is referenced. The monthly
review cadence catches drift.

## Pattern B: Per-aggregate metric instead of per-identity (Go)

```go
// SUBSTRATE-RECOMMENDED PATTERN:
// Metric answers "how many requests per tenant per endpoint?"
// at the aggregate level. Per-user questions are answered
// through traces (per-request span attributes) where retention
// bounds the cost rather than continuously growing.

var apiRequestsTotal = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "api_requests_total",
    },
    []string{"tenant_id", "endpoint"},
)
```

Why this satisfies observability.cardinality-discipline: the comment explicitly
documents the substrate-recommended pattern of lifting
per-identity questions to traces. Operators investigating a
per-user issue follow the trace context through the trace
backend rather than querying a per-user-labeled metric.

## Pattern C: Endpoint template, not substituted URL (Node.js)

```javascript
import { Counter } from 'prom-client';

const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'HTTP requests. Label endpoint is the route template, not the substituted URL.',
  labelNames: ['endpoint', 'method', 'status'],
});

app.use((req, res, next) => {
  res.on('finish', () => {
    // req.route.path is the templated pattern (e.g., '/users/:id')
    // req.path would be the substituted URL (e.g., '/users/12345')
    const endpoint = req.route?.path ?? 'unknown';
    httpRequestsTotal.labels(endpoint, req.method, String(res.statusCode)).inc();
  });
  next();
});
```

Why this satisfies observability.cardinality-discipline: the label uses the route
template (bounded by API surface ~80 values) rather than the
substituted URL (unbounded by user input). The helper
comment documents the discipline at the registration site
for future maintainers.

## Pattern D: Cardinality budget tracking (cardinality-budget.md)

```markdown
# Cardinality Budget

## Service: payments-api

| Metric                              | Labels                                       | Bound      | Actual (last audit) |
|-------------------------------------|----------------------------------------------|------------|---------------------|
| api_requests_total                  | tenant_id, region, endpoint, status          | 2,000,000  | 142,318             |
| api_request_duration_seconds        | tenant_id, region, endpoint                  | 400,000    | 31,254              |
| payment_attempts_total              | tenant_id, payment_method, outcome           | 24,000     | 6,108               |
| queue_depth_messages                | queue_name                                   | 12         | 12                  |

Bound = cartesian product of documented vocabularies.
Actual = backend-reported active series count.
Source of truth: tenant count from business roadmap; endpoints
from openapi.yaml route count.
Last audit: 2026-05-15.
Next audit: 2026-06-15.
```

Why this satisfies observability.cardinality-discipline: the budget is documented,
bounds are mathematically defensible, actuals are tracked
against bounds, the audit cadence is explicit. The document
lives in the service's repo and is part of code review
when metric registrations change.

## Pattern E: Pipeline-level cardinality drop with documented backlog (Prometheus configuration)

```yaml
# Drop high-cardinality labels from third-party metrics at ingestion.
# These drops are stabilization for source-side fixes tracked in
# backlog tickets; each drop has a corresponding remediation issue.
metric_relabel_configs:
  # Drop user_id label from springframework metric (ticket OPS-2371).
  # Source fix: switch to Micrometer instrument with tenant_id label.
  # Target removal date: 2026-07-15.
  - source_labels: [__name__]
    regex: 'spring_security_authentication_seconds.*'
    target_label: user_id
    replacement: ''
    action: replace
```

Why this satisfies observability.cardinality-discipline: pipeline drops are used
sparingly, documented per-rule with backlog ticket and
target removal date, and treated as stabilization rather
than the permanent solution.

## Pattern F: SLI-driving metric with verified stability

```yaml
# slo-instrumentation.md (excerpt)

## Availability SLI for payments-api

SLI query:
  sum(rate(api_requests_total{service="payments",status!~"5.."}[5m]))
  /
  sum(rate(api_requests_total{service="payments"}[5m]))

SLI metric:        api_requests_total
SLI labels used:   service, status
Cardinality:       bounded (service ~10 values, status 5 classes)
Query stability:   verified under load test at 1000 RPS sustained
SLO reference:     /docs/decisions/ADR-014-payments-slo-policy.md
```

Why this satisfies observability.cardinality-discipline and observability.slo-policy together: the
SLI computation uses a bounded-label metric; the query
stability is verified empirically; the SLO documentation
references the specific metric and labels. The SLI is
computable and stable across the cardinality bound.

## Cross-reference

- Substrate rule: observability.cardinality-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Anti-pattern examples: examples/observability/cardinality-discipline-anti-pattern.md
- Related: observability.metric-naming-convention (naming convention forbids identifier embedding); observability.slo-policy (SLO depends on stable SLI metric)
