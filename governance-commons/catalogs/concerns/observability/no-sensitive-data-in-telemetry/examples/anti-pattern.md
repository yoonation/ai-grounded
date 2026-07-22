<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: observability.no-sensitive-data-in-telemetry no sensitive data in telemetry (anti-patterns)

Substrate-original anti-pattern examples for observability.no-sensitive-data-in-telemetry.

## Anti-pattern A: Credential attached as span attribute (Python)

```python
def authenticate(user_id: str, password: str):
    with tracer.start_as_current_span("authenticate") as span:
        span.set_attribute("user.id", user_id)
        span.set_attribute("user.password", password)
        user = users.find(user_id)
        if user and user.verify(password):
            return user
        return None
```

Why this violates observability.no-sensitive-data-in-telemetry: the password is attached as a
span attribute. The trace backend retains the password for the
backend's retention window; every operator with span query
access can read it; the trace exports to vendor SaaS by
default. The credential is now part of the telemetry pipeline
disclosure surface.

Remediation: remove the password attribute. The good-patterns
example shows the substrate-recommended pattern of recording
the bounded outcome (auth.result) rather than the credential.

## Anti-pattern B: User email as metric label (Go)

```go
var requestCounter = prometheus.NewCounterVec(
    prometheus.CounterOpts{
        Name: "api_requests_total",
    },
    []string{"user_email", "endpoint", "status"},
)

func handleRequest(w http.ResponseWriter, r *http.Request) {
    email := r.Header.Get("X-User-Email")
    requestCounter.WithLabelValues(email, r.URL.Path, statusStr).Inc()
}
```

Why this violates observability.no-sensitive-data-in-telemetry and observability.cardinality-discipline together: the
user_email label exposes PII at the metric level. Every
distinct email produces a new time series. The Prometheus
tsdb stores the email as a label value indefinitely (until
retention expires for the series). Vendor billing escalates
with cardinality. Cross-violation: observability.cardinality-discipline fires on the
unbounded label vocabulary.

Remediation: replace user_email with tenant_id and lift the
per-user view to traces (per-request identity in span
attributes) rather than metrics.

## Anti-pattern C: Full exception recorded via recordException (Java)

```java
try {
    processRequest(request);
} catch (Exception ex) {
    span.recordException(ex);
    throw ex;
}
```

Why this violates observability.no-sensitive-data-in-telemetry: Span.recordException captures
the exception's stringification and stack trace as a span
event. When the exception's message includes the request body
or query parameters (a common pattern with framework
exceptions), the sensitive content propagates into the
telemetry channel.

Concrete example: a SQLIntegrityConstraintViolationException
on a unique-email constraint may stringify as "Duplicate
entry 'attacker@example.com' for key 'users.email_unique'".
That string flows directly into the span event payload.

Remediation: capture only the exception type and a sanitized
message (good pattern C). Use Span.setStatus(ERROR) for the
error state; use Span.recordException only after a redaction
layer has scrubbed the exception.

## Anti-pattern D: Session token in baggage (Node.js)

```javascript
function attachContext(ctx, sessionToken, userId) {
  let baggage = propagation.getBaggage(ctx) || propagation.createBaggage();
  baggage = baggage.setEntry('session.token', { value: sessionToken });
  baggage = baggage.setEntry('user.id', { value: userId });
  return propagation.setBaggage(ctx, baggage);
}
```

Why this violates observability.no-sensitive-data-in-telemetry: baggage propagates to every
downstream service inheriting the trace context. The session
token is now visible to services that have no authentication
relationship with the originating user. A microservice
downstream that logs baggage as part of debugging (which is a
common pattern) writes the session token to its logs, which
then propagate to log retention, log archival, and SIEM
ingestion. The disclosure surface multiplies across the
service mesh.

Remediation: never propagate credentials via baggage.
Downstream services that need authentication context perform
their own authentication or receive scoped tokens through
explicit headers with restricted lifetime.

## Anti-pattern E: Whole framework object attached (Python)

```python
@app.route('/api/checkout', methods=['POST'])
def checkout():
    with tracer.start_as_current_span("checkout") as span:
        span.set_attribute("request", str(request))
        return process_checkout(request)
```

Why this violates observability.no-sensitive-data-in-telemetry: str(request) on a Flask request
object includes the request body. Flask checkout requests
typically carry payment card numbers, shipping addresses, or
PII. The full request stringification appears as a span
attribute and propagates to the backend.

Remediation: select the bounded fields explicitly
(request.method, request.path, request.endpoint) and attach
only those. Do not attach framework objects whole.

## Cross-reference

- Substrate rule: observability.no-sensitive-data-in-telemetry in catalogs/concerns/observability.oscal.yaml
- L1 binding: checklist.md
- Good-pattern examples: examples/observability/no-sensitive-data-in-telemetry-good.md
- Related: logging.no-sensitive-data-in-logs (parallel anti-patterns for log records); secrets-management.no-secrets-in-logs (credential disclosure)
