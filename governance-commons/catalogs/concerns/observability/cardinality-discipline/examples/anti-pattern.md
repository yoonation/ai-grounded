<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.cardinality-discipline cardinality discipline (anti-patterns)

Substrate-original anti-pattern examples for observability.cardinality-discipline.

## Anti-pattern A: user_id as label (Python)

```python
api_requests_total = Counter(
    "api_requests_total",
    "API request count.",
    ["user_id", "endpoint", "status"],
)


def handle_request(req):
    api_requests_total.labels(req.user_id, req.endpoint, req.status).inc()
```

Why this violates observability.cardinality-discipline: user_id is in the substrate-
recognized unbounded vocabulary list. In a service with
100,000 active users, this metric produces 100,000 series
per (endpoint, status) combination; with 80 endpoints and 5
status classes, the resulting series count is 40,000,000.
Prometheus tsdb storage grows linearly; vendor SaaS billing
escalates; query latency degrades.

Remediation: replace user_id with tenant_id (bounded by
business unit count). Per-user investigation goes through
traces (per-request span attributes) where retention bounds
the cost rather than continuous growth.

## Anti-pattern B: Session identifier as label (Go)

```go
var requestCounter = prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "api_requests_total"},
    []string{"session_id", "endpoint"},
)
```

Why this violates observability.cardinality-discipline: session_id is unbounded by
user input; every session creates a new series. The metric
becomes effectively a per-session log entry, with all the
cost of metric retention and none of the operational
benefit of structured logging.

Remediation: drop the session_id label. If per-session
investigation is operationally needed, capture session_id as
a span attribute (bounded by trace retention, not metric
retention) or as a structured log field (bounded by log
retention policy, governed by logging.retention-policy).

## Anti-pattern C: Substituted URL as label (Node.js)

```javascript
app.use((req, res, next) => {
  res.on('finish', () => {
    httpRequestsTotal.labels(req.path, req.method, String(res.statusCode)).inc();
  });
  next();
});
```

Why this violates observability.cardinality-discipline: req.path is the substituted
URL containing user-provided parameter values (e.g.,
`/users/12345`, `/orders/abc-def-123`). Every distinct URL
path produces a new series; the cardinality is bounded by
the number of distinct paths the service serves, which scales
with user activity rather than API surface.

Remediation: use the route template (req.route.path), which
is bounded by the API surface (~80 templates in a typical
service). The good-patterns example shows the Express
pattern.

## Anti-pattern D: Free-form error message as label (Python)

```python
errors_total = Counter(
    "errors_total",
    "Errors.",
    ["error_message"],
)


def handle_error(exc):
    errors_total.labels(str(exc)).inc()
```

Why this violates observability.cardinality-discipline: error_message takes values
from the exception's stringification, which is unbounded
(stack traces vary by call site; exception messages may
include user input or query parameters). Each distinct
stringified exception produces a new series.

Remediation: label by error class (a bounded vocabulary the
service defines, e.g., "validation_error", "downstream_5xx",
"timeout"). The full error message belongs in logs or in
span events; metrics carry the categorical signal.

## Anti-pattern E: Timestamp embedded as label (Go)

```go
var eventCounter = prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "events_total"},
    []string{"event_type", "event_timestamp"},
)


func recordEvent(eventType string) {
    timestamp := time.Now().Format(time.RFC3339)
    eventCounter.WithLabelValues(eventType, timestamp).Inc()
}
```

Why this violates observability.cardinality-discipline: every recorded event produces
a unique label value (the current timestamp). The metric
becomes a write-once log of events with cardinality growing
linearly with event rate, defeating the purpose of metrics
(aggregation over time).

Remediation: drop the event_timestamp label. Metric records
already carry a sample timestamp; recording the timestamp
again as a label is dimensionally wrong.

## Anti-pattern F: Cardinality exceeds documented bound silently

The service registered a metric with tenant_id as the only
label, documenting a bound of "up to 1000 tenants." Six
months later, the business added a feature that issues a
fresh tenant_id per customer trial signup. The bound is now
silently violated (10,000+ tenants); the metric backend's
cardinality cost has tripled; no one is reviewing the
cardinality budget.

Why this violates observability.cardinality-discipline: the documented bound exists
but is not actually maintained. The discipline broke not at
registration but at the absence of the substrate-recommended
monthly cardinality review.

Remediation: re-establish the monthly review cadence; either
update the bound documentation to reflect the new reality
(and accept the cost) or apply a pipeline-level drop while
source-side remediation is in flight.

## Anti-pattern G: Pipeline drop with no source-side fix

The Prometheus configuration has a metric_relabel_configs
entry dropping a high-cardinality label. The entry was added
18 months ago as a stabilization measure. The corresponding
backlog ticket is unresolved.

Why this violates observability.cardinality-discipline: pipeline drops are substrate-
acceptable as stabilization, not as the permanent solution.
A drop that lives indefinitely obscures the true source-of-
truth metric and adds operational complexity to the pipeline.

Remediation: prioritize the source-side fix. If the fix is
genuinely impossible (third-party library with no
configuration hook), upgrade the drop documentation to
permanent status with explicit rationale and remove the
backlog ticket.

## Cross-reference

- Substrate rule: observability.cardinality-discipline in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Good-pattern examples: examples/observability/cardinality-discipline-good.md
