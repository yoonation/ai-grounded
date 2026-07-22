<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.no-sensitive-data-in-telemetry no sensitive data in telemetry (good patterns)

Substrate-original good-pattern examples for observability.no-sensitive-data-in-telemetry.

## Pattern A: Bounded-identifier span attributes (Python, OpenTelemetry)

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)


def authenticate(user_id: str, password: str):
    with tracer.start_as_current_span("authenticate") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("tenant.id", current_tenant_id())
        user = users.find(user_id)
        if user and user.verify(password):
            span.set_attribute("auth.result", "success")
            return user
        span.set_attribute("auth.result", "failure")
        return None
```

Why this satisfies observability.no-sensitive-data-in-telemetry: the password is never attached
as a span attribute. The span carries the bounded identifiers
(user.id, tenant.id) and the outcome (auth.result with a
bounded vocabulary) that operators need; the credential
itself stays out of the telemetry channel.

## Pattern B: Bounded metric labels (Go, Prometheus)

```go
var requestCounter = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "api_requests_total",
        Help: "Total API requests, labeled by tenant, endpoint, status",
    },
    []string{"tenant_id", "endpoint", "status"},
)

func handleRequest(w http.ResponseWriter, r *http.Request) {
    tenant := tenantFromRequest(r)
    endpoint := r.URL.Path
    // dispatch the request
    statusStr := strconv.Itoa(status)
    requestCounter.WithLabelValues(tenant, endpoint, statusStr).Inc()
}
```

Why this satisfies observability.no-sensitive-data-in-telemetry and observability.cardinality-discipline: labels are
drawn from bounded vocabulary (tenant_id, endpoint template,
HTTP status code). No user identifier, session token, or
request body appears as a label value.

## Pattern C: Exception recording with sanitized summary (Java, OpenTelemetry)

```java
Span span = Span.current();
try {
    processRequest(request);
} catch (Exception ex) {
    span.setAttribute("exception.type", ex.getClass().getName());
    span.setAttribute("exception.message", sanitize(ex.getMessage()));
    span.setStatus(StatusCode.ERROR);
    throw ex;
}
```

Why this satisfies observability.no-sensitive-data-in-telemetry: the exception type and a
sanitized message are recorded; the full exception
stringification (which may contain request body fragments,
query parameters, or framework objects) is not attached via
Span.recordException. The sanitize() helper applies the
consumer's redaction layer (cross-references logging.redaction if
the consumer shares redaction between logs and traces).

## Pattern D: Baggage propagation discipline (Node.js, OpenTelemetry)

```javascript
import { context, propagation } from '@opentelemetry/api';

function attachContext(ctx, tenantId, region) {
  let baggage = propagation.getBaggage(ctx) || propagation.createBaggage();
  baggage = baggage.setEntry('tenant.id', { value: tenantId });
  baggage = baggage.setEntry('region', { value: region });
  return propagation.setBaggage(ctx, baggage);
}
```

Why this satisfies observability.no-sensitive-data-in-telemetry: only bounded vocabulary
(tenant.id, region) propagates via baggage. Session tokens,
user emails, and other credentials remain in the
authentication channel (request headers with explicit scope)
rather than in trace baggage which propagates to every
downstream service automatically.

## Pattern E: Collector-side hardening as defense in depth

```yaml
processors:
  attributes/strip-sensitive:
    actions:
      - key: user.email
        action: delete
      - key: session.token
        action: delete
      - key: password
        action: delete
      - pattern: "credit_card.*"
        action: delete
```

Why this complements observability.no-sensitive-data-in-telemetry: even when source-level
detection misses a case, the collector strips the attribute
before it reaches the backend. Any attribute deletion by this
processor surfaces as a retroactive observability.no-sensitive-data-in-telemetry violation that
the consumer remediates at source.

## Cross-reference

- Substrate rule: observability.no-sensitive-data-in-telemetry in catalogs/concerns/observability.oscal.yaml
- L1 binding: checklist.md
- Anti-pattern examples: examples/observability/no-sensitive-data-in-telemetry-anti-pattern.md
- Related: logging.no-sensitive-data-in-logs (parallel rule for log records); secrets-management.no-secrets-in-logs (credential-channel rule)
