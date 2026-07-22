<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.metric-naming-convention metric naming convention (good patterns)

Substrate-original good-pattern examples for observability.metric-naming-convention.

## Pattern A: Prometheus-convention metric names (Python)

```python
from prometheus_client import Counter, Histogram, Gauge

api_requests_total = Counter(
    "api_requests_total",
    "Total API requests. Labels: tenant_id (bounded by business unit count); "
    "endpoint (route template, bounded by API surface); status (HTTP status).",
    ["tenant_id", "endpoint", "status"],
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "API request duration. Labels: tenant_id, endpoint.",
    ["tenant_id", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)

queue_depth_messages = Gauge(
    "queue_depth_messages",
    "Current messages in queue. Labels: queue_name (bounded by topology).",
    ["queue_name"],
)
```

Why this satisfies observability.metric-naming-convention: every name is lowercase
snake_case; every name has a semantic suffix indicating unit
and aggregation kind (_total for monotonic counters, _seconds
for duration histograms, _messages for size measurements);
no identifier values appear in metric names. The label
vocabulary documentation in the help strings satisfies
observability.cardinality-discipline documentation discipline.

## Pattern B: Go Prometheus with same convention

```go
var (
    apiRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "api_requests_total",
            Help: "Total API requests. Labels: tenant_id, endpoint, status.",
        },
        []string{"tenant_id", "endpoint", "status"},
    )

    apiRequestDurationSeconds = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "api_request_duration_seconds",
            Help:    "API request duration. Labels: tenant_id, endpoint.",
            Buckets: []float64{0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10},
        },
        []string{"tenant_id", "endpoint"},
    )
)
```

Why this satisfies observability.metric-naming-convention: the names mirror the Python
example exactly. Cross-service consistency is the load-
bearing benefit; an operator querying api_request_duration_seconds
across services finds the same metric regardless of the
implementation language.

## Pattern C: OpenTelemetry instrument naming (any language)

```python
from opentelemetry import metrics

meter = metrics.get_meter(__name__)

api_request_duration = meter.create_histogram(
    name="api.request.duration",
    description="API request duration in seconds",
    unit="s",
)

api_requests_count = meter.create_counter(
    name="api.requests",
    description="API request count",
    unit="{request}",
)
```

Why this satisfies observability.metric-naming-convention (with consumer profile
tailoring): OpenTelemetry uses dot-separated names rather
than Prometheus snake_case. Consumers using OpenTelemetry-
native backends select this convention via profile tailoring;
the binding's rule-format-override hook accepts the
alternative regex. The principle (consistent naming, semantic
unit awareness) is preserved.

## Pattern D: Vendor-rename for third-party metrics (Prometheus configuration)

```yaml
metric_relabel_configs:
  - source_labels: [__name__]
    regex: 'http_server_requests_seconds_count'
    target_label: __name__
    replacement: 'api_requests_total'
  - source_labels: [__name__]
    regex: 'http_server_requests_seconds_max'
    target_label: __name__
    replacement: 'api_request_duration_seconds_max'
```

Why this complements observability.metric-naming-convention: Spring Boot Actuator emits
metrics with names the consumer cannot rename at source.
metric_relabel_configs normalize at the Prometheus ingestion
boundary so downstream consumers (dashboards, alerts, stored
queries) see substrate-convention names. The rename is
documented in the Prometheus configuration with a comment
identifying the source library.

## Pattern E: promtool wrapper enforcing the convention

```bash
#!/usr/bin/env bash
set -euo pipefail

RULES_DIR="${1:-prometheus/rules}"
NAME_REGEX='^[a-z][a-z0-9_]*(_total|_seconds|_bytes|_ratio|_count|_info)$'

promtool check rules "${RULES_DIR}"/*.yml

# Additional check: metric names referenced in rules match the convention.
for f in "${RULES_DIR}"/*.yml; do
  metrics=$(yq '.. | select(.expr) | .expr' "$f" | grep -oE '[a-zA-Z_][a-zA-Z0-9_]*' | sort -u)
  for m in $metrics; do
    if ! [[ "$m" =~ $NAME_REGEX ]]; then
      echo "Rule file $f references non-convention metric: $m"
      exit 1
    fi
  done
done
```

Why this complements observability.metric-naming-convention: promtool natively checks
that referenced metrics exist but does not enforce a naming
convention. The wrapper adds the substrate-convention regex
assertion. CI runs the wrapper on every change to alert rule
or recording rule files.

## Cross-reference

- Substrate rule: observability.metric-naming-convention in catalogs/concerns/observability.oscal.yaml
- L1 binding: binding.yaml
- Anti-pattern examples: examples/observability/metric-naming-convention-anti-pattern.md
- Related: observability.cardinality-discipline (label vocabulary documentation); observability.semantic-convention-coverage (OpenTelemetry semantic conventions)
