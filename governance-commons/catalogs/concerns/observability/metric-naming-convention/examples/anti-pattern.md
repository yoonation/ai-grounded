<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.metric-naming-convention metric naming convention (anti-patterns)

Substrate-original anti-pattern examples for observability.metric-naming-convention.

## Anti-pattern A: Mixed case and missing semantic suffix

```python
api_requests = Counter("APIRequests", "...")
http_latency = Histogram("HTTPLatency", "...")
requests_per_second = Gauge("RequestsPerSecond", "...")
```

Why this violates observability.metric-naming-convention: ALL_CAPS and CamelCase fail the
lowercase snake_case requirement; "APIRequests" has no
semantic suffix indicating it is monotonic (should be
_total); "HTTPLatency" has no unit suffix (should be
_seconds); "RequestsPerSecond" misunderstands the convention
(Prometheus stores raw counters and the consumer derives
per-second via PromQL rate(); embedding "per second" in the
name produces a metric where rate() yields per-second-per-
second, which is dimensionally wrong).

Remediation: rename to api_requests_total, http_request_duration_seconds,
api_requests_total (with rate() applied in queries).

## Anti-pattern B: Identifier value in metric name (Python)

```python
def register_per_tenant_counter(tenant_id):
    return Counter(
        f"requests_for_tenant_{tenant_id}_total",
        f"Requests for tenant {tenant_id}",
    )
```

Why this violates observability.metric-naming-convention: the metric name embeds the
tenant_id at registration time. Every tenant produces a new
metric name; the Prometheus registry grows unbounded; queries
cannot aggregate across tenants without enumerating all
metric names.

Remediation: define a single Counter with tenant_id as a
label:

```python
requests_total = Counter(
    "requests_total",
    "Requests. Label: tenant_id (bounded by business unit count).",
    ["tenant_id"],
)
```

## Anti-pattern C: Hyphenated names (Node.js)

```javascript
const counter = new client.Counter({
  name: 'http-requests-total',
  help: '...',
});

const histogram = new client.Histogram({
  name: 'request-duration-ms',
  help: '...',
});
```

Why this violates observability.metric-naming-convention: Prometheus names use snake_case
not kebab-case; the substrate regex rejects hyphens. The
duration histogram uses milliseconds rather than the
substrate-default seconds suffix; Prometheus convention is to
use base units (seconds, bytes) and let display layers
convert as needed.

Remediation: rename to http_requests_total and
http_request_duration_seconds (storing seconds, converting in
the query layer or dashboard).

## Anti-pattern D: Per-method-per-status metric explosion (Go)

```go
var get200Counter = prometheus.NewCounter(prometheus.CounterOpts{Name: "api_get_200_count"})
var get404Counter = prometheus.NewCounter(prometheus.CounterOpts{Name: "api_get_404_count"})
var get500Counter = prometheus.NewCounter(prometheus.CounterOpts{Name: "api_get_500_count"})
var post200Counter = prometheus.NewCounter(prometheus.CounterOpts{Name: "api_post_200_count"})
// ...
```

Why this violates observability.metric-naming-convention: the metric name embeds the
method and status; cross-cutting queries (errors across all
methods, by status) require enumerating metric names. Per-
method-per-status counter proliferation is the most common
expression of the rule violation in service code.

Remediation: a single counter with method and status as
labels:

```go
var apiRequestsTotal = prometheus.NewCounterVec(
    prometheus.CounterOpts{Name: "api_requests_total"},
    []string{"method", "status"},
)
```

## Anti-pattern E: Dot-separated names in Prometheus context (Python)

```python
counter = Counter("api.requests.total", "...")
```

Why this violates observability.metric-naming-convention in a Prometheus context: dots
are not valid Prometheus metric name characters. Prometheus
ingestion converts dots to underscores silently, producing
api_requests_total. The source code does not match the
ingested name; debugging is harder because the operator must
know about the silent conversion.

Remediation: use snake_case at the source. If the consumer
genuinely uses OpenTelemetry-native ingestion (where dots
are valid), select the OpenTelemetry profile through tailoring.

## Anti-pattern F: Pluralization inconsistency

```python
api_request_total = Counter("api_request_total", "...")
api_requests_total = Counter("api_requests_total", "...")
http_response_total = Counter("http_response_total", "...")
http_responses_total = Counter("http_responses_total", "...")
```

Why this violates observability.metric-naming-convention sub-discipline: the same
service uses both singular and plural for related concepts.
Operators querying api_request_total and api_requests_total
get different answers; cross-service queries fail. The
Prometheus convention prefers the plural form for counters
representing event counts.

Remediation: standardize on plural for counter event counts
(api_requests_total, http_responses_total); review the
service for consistency.

## Cross-reference

- Substrate rule: observability.metric-naming-convention in catalogs/concerns/observability.oscal.yaml
- L1 binding: binding.yaml
- Good-pattern examples: examples/observability/metric-naming-convention-good.md
- Related: observability.cardinality-discipline (label cardinality discipline; the substrate-recommended remediation for many naming anti-patterns is to lift identifier values from names into labels)
