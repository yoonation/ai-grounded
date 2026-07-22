<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.trace-context-propagation trace context propagation (good patterns)

Substrate-original good-pattern examples for observability.trace-context-propagation.

## Pattern A: Auto-instrumented HTTP client (Python, requests)

```python
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import requests

RequestsInstrumentor().instrument()


def call_downstream(payload):
    return requests.post(
        "https://downstream.internal/api/v1/process",
        json=payload,
        timeout=10,
    )
```

Why this satisfies observability.trace-context-propagation: opentelemetry-instrumentation-
requests wraps the requests library at application startup.
Every subsequent requests call participates in trace context
propagation automatically; the traceparent header is injected
by the instrumentation layer; downstream services see the
header and attach their spans to the same trace.

## Pattern B: Auto-instrumented gRPC client (Go)

```go
import (
    "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
    "google.golang.org/grpc"
)

func newClient(target string) (*grpc.ClientConn, error) {
    return grpc.Dial(
        target,
        grpc.WithUnaryInterceptor(otelgrpc.UnaryClientInterceptor()),
        grpc.WithStreamInterceptor(otelgrpc.StreamClientInterceptor()),
    )
}
```

Why this satisfies observability.trace-context-propagation: otelgrpc interceptors inject
trace context into gRPC metadata for every outbound call
through the channel. The downstream gRPC server attaches its
spans to the same trace by reading the metadata.

## Pattern C: Manual propagation where auto-instrumentation is unavailable (Python)

```python
from opentelemetry import context, propagate

def send_custom_transport(url, payload):
    headers = {}
    propagate.inject(headers)
    custom_transport.post(url, payload, headers=headers)
```

Why this satisfies observability.trace-context-propagation: when the consumer's transport
is not covered by auto-instrumentation, manual injection
puts the traceparent header into the outbound headers
explicitly. The downstream service extracts the context with
propagate.extract on receipt.

## Pattern D: Documented exemption for deliberately-untraced calls (Python)

```python
def ping_third_party_status():
    # observability.trace-context-propagation-exempt: third-party status API; no propagation relationship
    return requests.get("https://status.thirdparty.example/healthz", timeout=2)
```

Why this satisfies observability.trace-context-propagation: the exemption comment marks
the call site as deliberately untraced. The linker recognizes
the substrate-recommended exemption pattern and does not
flag the call. The ADR referenced from the consumer's
instrumentation documentation records the rationale.

## Pattern E: Runtime trace propagation health check (CI test, pseudo-code)

```python
def test_trace_propagates_to_downstream_stub():
    stub = TraceCapturingStub()
    stub.start()

    service_under_test.start()
    service_under_test.invoke_downstream_call_path()

    received_headers = stub.last_request_headers()
    assert "traceparent" in received_headers
    traceparent = received_headers["traceparent"]
    assert traceparent.startswith("00-")
    trace_id = traceparent.split("-")[1]
    assert len(trace_id) == 32
```

Why this complements observability.trace-context-propagation: the test exercises the full
runtime path. Source-level static analysis passes if the
instrumentation package is imported, but a misconfigured
attachment point or a middleware that strips headers would
not surface until runtime. The CI test catches the runtime
gap.

## Pattern F: Per-language instrumentation registry check (CI, pseudo-code)

```python
def test_instrumentation_coverage_against_dependencies():
    deps = parse_pyproject_toml("pyproject.toml")
    registry = fetch_opentelemetry_registry("python")
    for dep in deps:
        if dep.name in registry.instrumented_libraries:
            instrumentation = registry.instrumentation_for(dep.name)
            assert instrumentation in deps, (
                f"{dep.name} requires {instrumentation}, "
                f"add it to dependencies"
            )
```

Why this complements observability.trace-context-propagation: the test catches the case
where the consumer added a new client library but forgot the
matching instrumentation package. The check runs at every
dependency-update pull request.

## Cross-reference

- Substrate rule: observability.trace-context-propagation in catalogs/concerns/observability.oscal.yaml
- L1 binding: checklist.md
- Anti-pattern examples: examples/observability/trace-context-propagation-anti-pattern.md
- Related: logging.correlation-ids (correlation IDs in logs map to the same trace context); observability.semantic-convention-coverage (semantic-convention coverage in propagated spans)
