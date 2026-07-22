<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.semantic-convention-coverage semantic convention coverage (anti-patterns)

Substrate-original anti-pattern examples for observability.semantic-convention-coverage.

## Anti-pattern A: Local attribute names instead of conventions (Python)

```python
@app.route("/api/v1/users/<user_id>", methods=["GET"])
def get_user(user_id):
    span = trace.get_current_span()
    span.set_attribute("method", request.method)
    span.set_attribute("path", request.path)
    span.set_attribute("status", response_status)
    return result
```

Why this violates observability.semantic-convention-coverage: the attribute names are local
("method", "path", "status") rather than the OpenTelemetry
convention names ("http.request.method", "http.route",
"http.response.status_code"). Cross-service queries that ask
about http.route latency see no data because the convention
name is not used. Vendor backends and open-source trace
explorers that key on the convention attributes display
incomplete information.

Remediation: rename to the OpenTelemetry convention names.
With opentelemetry-instrumentation-flask installed, this
happens automatically; the manual code shown above is the
anti-pattern of overriding the convention.

## Anti-pattern B: Substituted URL instead of route template (Python)

```python
@app.route("/api/v1/users/<user_id>")
def get_user(user_id):
    span = trace.get_current_span()
    span.set_attribute("http.route", f"/api/v1/users/{user_id}")
    return result
```

Why this violates observability.semantic-convention-coverage: http.route should be the
templated pattern ("/api/v1/users/{user_id}"), not the
substituted URL. With the substituted URL, every distinct
user_id produces a unique http.route value; the trace
explorer's "group by route" query becomes useless (every
group has one trace). The convention exists specifically to
aggregate across substituted parameters.

Remediation: set http.route to the route pattern from the
framework (Flask: request.url_rule.rule; Express: req.route.path;
Spring: handlerMapping pattern).

## Anti-pattern C: Wrong db.system value (Java)

```java
span.setAttribute("db.system", "postgres");
span.setAttribute("db.operation", "select");
```

Why this violates observability.semantic-convention-coverage: the OpenTelemetry registry
value for PostgreSQL is "postgresql", not "postgres" or "pg".
The convention's value list is normative; local variants
produce trace explorer filters that miss data. Similarly,
db.operation uses uppercase SQL command names by convention
(SELECT, not select), so vendor query languages can compare
unambiguously.

Remediation: use registry values. The OpenTelemetry
semconv-java module provides constants
(SemanticAttributes.DB_SYSTEM, DbSystemValues.POSTGRESQL)
that eliminate this class of error.

## Anti-pattern D: Wrong span kind for messaging (Go)

```go
ctx, span := tracer.Start(ctx, "publish_order",
    trace.WithSpanKind(trace.SpanKindClient),
    trace.WithAttributes(
        attribute.String("queue.name", "orders.created"),
    ),
)
```

Why this violates observability.semantic-convention-coverage: Kafka producer spans should
have kind PRODUCER, not CLIENT. Span kind drives display
behavior in trace explorers; PRODUCER and CONSUMER spans are
displayed as messaging-specific shapes that operators
recognize. The attribute key is also wrong: queue.name is
not the OpenTelemetry convention; messaging.destination.name
is.

Remediation: span kind PRODUCER for publish, CONSUMER for
receive; messaging.system and messaging.destination.name as
the conventional attribute names.

## Anti-pattern E: gRPC modeled as generic HTTP (Node.js)

```javascript
const span = tracer.startSpan('http.client', { kind: SpanKind.CLIENT });
span.setAttribute('http.method', 'POST');
span.setAttribute('http.url', `grpc://${target}/users.v1.UserService/GetUser`);
await userServiceClient.getUser({ id: userId });
span.end();
```

Why this violates observability.semantic-convention-coverage: gRPC has its own convention
(rpc.system, rpc.service, rpc.method). Modeling it as HTTP
loses the rpc.* attribute structure that gRPC-specific
tooling depends on. The trace explorer's gRPC-aware features
(service-level latency aggregation, method-level error
rates) do not fire for this span.

Remediation: use the rpc.* convention attributes; or rely on
opentelemetry-instrumentation-grpc to set them automatically.

## Anti-pattern F: Convention version not tracked (any language)

The service emits spans but the resource attribute does not
include a schema_url field. The consumer's instrumentation
ADR does not record which OpenTelemetry semantic conventions
version the service follows.

Why this violates observability.semantic-convention-coverage: convention versions change
over time. Without the schema_url, downstream tooling cannot
verify the service emits compatible attributes; convention
migrations (e.g., the deprecation of http.method in favor of
http.request.method) cannot be tracked.

Remediation: emit schema_url on the resource; record the
convention version in the consumer's instrumentation ADR;
review on the substrate-recommended quarterly cadence for
upgrades.

## Anti-pattern G: Auto-instrumentation disabled, manual spans use ad-hoc names

```python
# Auto-instrumentation has been disabled for performance reasons
@app.route("/api/users")
def get_users():
    with tracer.start_as_current_span("handle_users_request") as span:
        span.set_attribute("request_type", "list")
        span.set_attribute("api_version", "v1")
        return jsonify(users)
```

Why this violates observability.semantic-convention-coverage: auto-instrumentation was the
substrate-recommended path to convention adherence. Disabling
it without replacing the convention coverage produces spans
that look reasonable in isolation but cannot be queried by
the convention vocabulary.

Remediation: keep auto-instrumentation enabled; if performance
is genuinely the concern, profile the overhead and tune
sampling rather than disabling instrumentation entirely. If
manual spans are necessary, set the convention attributes
manually.

## Cross-reference

- Substrate rule: observability.semantic-convention-coverage in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Good-pattern examples: examples/observability/semantic-convention-coverage-good.md
