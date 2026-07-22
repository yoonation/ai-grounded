<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.semantic-convention-coverage semantic convention coverage (good patterns)

Substrate-original good-pattern examples for observability.semantic-convention-coverage.

## Pattern A: HTTP server span with required attributes (Python)

```python
from flask import Flask, request
from opentelemetry import trace

app = Flask(__name__)
tracer = trace.get_tracer(__name__)


@app.route("/api/v1/users/<user_id>", methods=["GET"])
def get_user(user_id):
    span = trace.get_current_span()
    span.set_attribute("http.request.method", request.method)
    span.set_attribute("http.route", "/api/v1/users/{user_id}")
    span.set_attribute("server.address", request.host)

    user = lookup_user(user_id)
    response_status = 200 if user else 404
    span.set_attribute("http.response.status_code", response_status)

    return user_dict(user), response_status
```

Why this satisfies observability.semantic-convention-coverage: the span carries the
OpenTelemetry HTTP server convention attributes by their
exact names. The http.route is the templated pattern not the
substituted URL (the substitution would inflate trace
explorer cardinality and is unhelpful for aggregation). With
opentelemetry-instrumentation-flask installed, these
attributes are set automatically; the manual setting above
is shown for illustration.

## Pattern B: Database client span with semantic-convention attributes (Java)

```java
public List<User> findUsersByTenant(String tenantId) {
    Span span = Span.current();
    span.setAttribute("db.system", "postgresql");
    span.setAttribute("db.operation", "SELECT");
    span.setAttribute("db.namespace", "production_users");

    String query = "SELECT * FROM users WHERE tenant_id = ?";
    return jdbcTemplate.query(query, new Object[]{tenantId}, userMapper);
}
```

Why this satisfies observability.semantic-convention-coverage: db.system uses the
OpenTelemetry registry value ("postgresql" not "postgres" or
"pg"); db.operation identifies the kind; db.namespace
identifies the database. Note: db.statement is intentionally
NOT set because the substituted parameter (tenantId) could
contain sensitive context in other queries (observability.no-sensitive-data-in-telemetry
cross-discipline).

## Pattern C: Messaging spans linking producer to consumer (Go)

```go
import "go.opentelemetry.io/otel/semconv/v1.21.0/messaging"

func publishOrder(ctx context.Context, order Order) error {
    ctx, span := tracer.Start(ctx, "kafka.publish",
        trace.WithSpanKind(trace.SpanKindProducer),
        trace.WithAttributes(
            attribute.String("messaging.system", "kafka"),
            attribute.String("messaging.destination.name", "orders.created"),
            attribute.String("messaging.operation", "publish"),
        ),
    )
    defer span.End()

    headers := injectTraceContext(ctx)
    return kafkaProducer.Produce(headers, order)
}

func consumeOrder(headers map[string][]byte, order Order) {
    ctx := extractTraceContext(headers)
    ctx, span := tracer.Start(ctx, "kafka.consume",
        trace.WithSpanKind(trace.SpanKindConsumer),
        trace.WithAttributes(
            attribute.String("messaging.system", "kafka"),
            attribute.String("messaging.destination.name", "orders.created"),
            attribute.String("messaging.operation", "process"),
        ),
    )
    defer span.End()

    processOrder(ctx, order)
}
```

Why this satisfies observability.semantic-convention-coverage: both producer and consumer
spans carry the messaging.* attributes; consumer trace
context is extracted from message headers (cross-reference
observability.trace-context-propagation trace propagation through message headers); the
consumer span attaches to the producer's trace through the
extracted context.

## Pattern D: gRPC client span with rpc.* attributes (Node.js)

```javascript
import { trace, SpanKind } from '@opentelemetry/api';

const tracer = trace.getTracer('my-service');

async function callUserService(userId) {
  return tracer.startActiveSpan(
    'UserService.GetUser',
    { kind: SpanKind.CLIENT },
    async (span) => {
      span.setAttribute('rpc.system', 'grpc');
      span.setAttribute('rpc.service', 'users.v1.UserService');
      span.setAttribute('rpc.method', 'GetUser');
      try {
        return await userServiceClient.getUser({ id: userId });
      } finally {
        span.end();
      }
    },
  );
}
```

Why this satisfies observability.semantic-convention-coverage: rpc.service is the fully-
qualified protobuf service name (users.v1.UserService, not
just "UserService"); rpc.method matches the method name in
the protobuf definition; span kind is CLIENT explicitly.

## Pattern E: Schema URL emitted on resource attributes

```python
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

resource = Resource.create(
    {
        ResourceAttributes.SERVICE_NAME: "user-service",
        ResourceAttributes.SERVICE_VERSION: "1.2.3",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: "production",
    },
    schema_url="https://opentelemetry.io/schemas/1.21.0",
)
```

Why this satisfies observability.semantic-convention-coverage: the schema URL declares which
OpenTelemetry semantic conventions version the service
follows. Downstream tooling reads the schema URL to interpret
attributes correctly across convention versions. The
consumer's instrumentation ADR records the convention version
the service follows.

## Cross-reference

- Substrate rule: observability.semantic-convention-coverage in catalogs/concerns/observability.oscal.yaml
- Review checklist: checklist.md
- Test template: test-template.md
- Anti-pattern examples: examples/observability/semantic-convention-coverage-anti-pattern.md
