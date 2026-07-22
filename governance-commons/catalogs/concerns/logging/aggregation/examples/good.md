<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.aggregation aggregation and search readiness (good patterns)

## Pattern A: Centralized aggregator with documented latency SLO

```markdown
# /docs/operations/log-aggregation-slo.md

## Latency targets (producer to queryable in aggregator)

| Stream class    | P50      | P99      | Alert threshold |
|-----------------|----------|----------|-----------------|
| Security audit  | 5s       | 30s      | P99 > 60s       |
| Application     | 15s      | 60s      | P99 > 120s      |
| Operational     | 30s      | 5min     | P99 > 10min     |

## Search SLOs

- Hot tier (0-14 days): sub-second response for indexed fields
- Warm tier (14-90 days): under 10s for indexed fields
- Cold tier (90 days+): up to 5min for indexed fields acceptable
```

Why this satisfies logging.aggregation: per-stream latency targets are
documented; alert thresholds are explicit; search SLOs are
tied to tier. The targets give operators a clear bound to
test against.

## Pattern B: OpenTelemetry Collector with full pipeline

```yaml
# OpenTelemetry Collector configuration
receivers:
  otlp:
    protocols: { grpc: { endpoint: 0.0.0.0:4317 } }
  fluentforward:
    endpoint: 0.0.0.0:24224

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024
  attributes:
    actions:
      - key: service.name
        action: insert
        from_attribute: service
      - key: trace.id
        action: insert
        from_attribute: traceID

exporters:
  loki:
    endpoint: https://loki.internal/loki/api/v1/push
    tenant_id: production
  awsxray:
    region: us-west-2

service:
  pipelines:
    logs:
      receivers: [otlp, fluentforward]
      processors: [batch, attributes]
      exporters: [loki]
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [awsxray]
```

Why this satisfies logging.aggregation: the collector ingests from
multiple sources, attaches service.name and trace.id as
indexed attributes, and ships to a centralized aggregator
within the documented latency SLO. Cross-service join is
supported via the trace.id attribute.

## Pattern C: Loki LogQL query templates in runbook

```markdown
# /docs/runbook/log-queries.md

## Common incident-response queries

### 1. All errors for a user request

\`\`\`logql
{job="application"} | json | trace_id="<TRACE_ID>" | level="error"
\`\`\`

### 2. Authentication failures in last 15 minutes

\`\`\`logql
{job="application", event="auth_failed"}
  | json
  | unwrap user_id
  | rate(15m)
\`\`\`

### 3. 5xx response surge by endpoint

\`\`\`logql
sum by (endpoint) (
  rate({job="application"} | json | status_code >= 500 [5m])
)
\`\`\`

### 4. Logs around a specific timestamp (incident drilldown)

\`\`\`logql
{job=~".+"}
  | json
  | __error__=""
  # Filter time range in Grafana UI: timestamp +/- 5min
\`\`\`
```

Why this satisfies logging.aggregation: the runbook contains executable
query templates for common incident patterns. Operators do
not author queries from scratch under incident pressure;
templates are exercised in drills.

## Pattern D: Cross-service join via shared trace.id field

```python
# Service A
@tracer.start_as_current_span("create_order")
def create_order(order_data):
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id
    log.info("order_created",
        trace_id=f"{trace_id:032x}",
        order_id=order.id)
    inventory_client.reserve(order, trace_id=trace_id)

# Service B (inventory)
def reserve(order, trace_id):
    log.info("inventory_reserved",
        trace_id=f"{trace_id:032x}",
        order_id=order.id,
        items=len(order.items))
```

Why this satisfies logging.aggregation: both services emit log
records with the same trace_id; the aggregator's query
`{} |~ "trace_id=<TID>"` returns the full cross-service
sequence in time order.

## Pattern E: Shipping pipeline health monitoring

```yaml
# Prometheus alert rules
groups:
  - name: log-shipping-health
    rules:
      - alert: LogShipperDown
        expr: up{job="fluent-bit"} == 0
        for: 2m
        annotations:
          summary: "Log shipper unreachable on {{ $labels.instance }}"

      - alert: LogShippingBackpressure
        expr: rate(fluentbit_output_dropped_records_total[5m]) > 0
        for: 5m
        annotations:
          summary: "Log shipper dropping records on {{ $labels.instance }}"

      - alert: LogIngestionLatencyHigh
        expr: histogram_quantile(0.99, log_ingestion_latency_seconds) > 60
        for: 10m
        annotations:
          summary: "P99 log ingestion latency exceeded 60s"
```

Why this satisfies logging.aggregation: the shipping pipeline emits
operational metrics; alerts fire on failure or back-pressure.
The substrate-recommended monitoring prevents silent shipping
failures from creating gaps in the aggregator.

## Pattern F: New-service onboarding checklist

```markdown
# /docs/operations/new-service-onboarding.md

## Logging requirements (logging.aggregation)

- [ ] Service emits structured logs (logging.structured-format)
- [ ] Service propagates correlation IDs (logging.correlation-ids)
- [ ] Service ships logs to central aggregator
- [ ] Aggregator source inventory includes new service
- [ ] Per-stream latency SLO documented
- [ ] Production-readiness review confirms shipping
  is operational under load (load test verifies
  logs reach aggregator within SLO)
- [ ] Runbook for new service references the common
  incident-response query templates
```

Why this satisfies logging.aggregation: new services are required to
ship logs as part of production readiness. The checklist
prevents silent gaps where new services miss the aggregator.

## Cross-reference

- Anti-patterns: examples/logging/aggregation-anti-pattern.md
- Substrate rule: logging.aggregation
- Review checklist: checklist.md
