<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.no-secrets-in-logs no secrets in logs (good patterns)

Substrate-original good-pattern examples for secrets-management.no-secrets-in-logs.

## Pattern A: Producer-side redaction processor (Python structlog)

```python
import structlog

SENSITIVE_KEYS = {"password", "api_key", "token", "secret",
                  "authorization", "stripe_key", "private_key"}

def redact_sensitive(logger, method_name, event_dict):
    for key in list(event_dict.keys()):
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = "[REDACTED]"
    return event_dict

structlog.configure(
    processors=[
        redact_sensitive,  # First in the chain
        structlog.processors.JSONRenderer(),
    ],
)
```

Why this satisfies secrets-management.no-secrets-in-logs: redaction runs before
serialization, in the application code that produces the
log event. The processor is positioned first so any
sensitive key is redacted regardless of how the event was
constructed.

## Pattern B: Typed wrapper that masks under str() and repr()

```python
class SecretString:
    __slots__ = ("_value",)
    def __init__(self, value: str):
        self._value = value
    def __repr__(self) -> str:
        return "SecretString(***)"
    def __str__(self) -> str:
        return "***"
    def reveal(self) -> str:
        return self._value

api_key = SecretString(os.environ["STRIPE_KEY"])
logger.info("API client initialized", client_key=api_key)
# Logs: {"event": "API client initialized", "client_key": "***"}
```

Why this satisfies secrets-management.no-secrets-in-logs: the wrapper makes
accidental disclosure visible only via an explicit
`.reveal()` call. Stringification (which is what most
loggers invoke) cannot produce the plaintext.

## Pattern C: Java logback redaction pattern

```xml
<!-- logback.xml -->
<configuration>
  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <encoder>
      <pattern>%d{ISO8601} [%thread] %-5level %logger - %replace(%msg){'(?i)(password|secret|token|api[_-]?key)\s*[:=]\s*[^\s,}]+', '$1=[REDACTED]'}%n</pattern>
    </encoder>
  </appender>
</configuration>
```

Why this satisfies secrets-management.no-secrets-in-logs: the replace converter
applies a regex redaction to every log line before output.
This is a defense-in-depth backstop; the substrate
recommends producer-side redaction in code as the primary
control, but the converter catches mistakes.

## Pattern D: OpenTelemetry attribute redaction (Go)

```go
// SDK setup with redaction span processor
type redactingProcessor struct {
    next sdktrace.SpanProcessor
}

var sensitiveKeys = map[string]bool{
    "http.request.header.authorization": true,
    "db.statement":                       true,  // may contain secrets
    "api.key":                            true,
}

func (r *redactingProcessor) OnEnd(s sdktrace.ReadOnlySpan) {
    // Redact before delegating to next processor (exporter)
    for _, attr := range s.Attributes() {
        if sensitiveKeys[string(attr.Key)] {
            // Replace attribute value before export
        }
    }
    r.next.OnEnd(s)
}
```

Why this satisfies secrets-management.no-secrets-in-logs: tracing carries
attributes that can include secret material. Producer-side
redaction in the span processor ensures the redaction
happens before export, regardless of downstream backend.

## Pattern E: Error response sanitization (Express middleware)

```javascript
// errorHandler.js
app.use((err, req, res, next) => {
  // Log full detail server-side (with redaction in the
  // logger configuration); return only safe context to
  // the client.
  logger.error("Request failed", {
    error: err.message,
    stack: err.stack,
    user_id: req.user?.id,
  });
  res.status(500).json({
    error: "Internal server error",
    request_id: req.id,
    // No request body, no headers, no stack trace returned
  });
});
```

Why this satisfies secrets-management.no-secrets-in-logs: error responses to
clients do not include the request body (which may carry
credentials), headers (Authorization), or stack traces
(which can include local-variable values). The server-side
log captures detail for debugging, with its own redaction.

## Pattern F: Sentry beforeSend redaction (Node.js)

```javascript
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  beforeSend(event) {
    // Redact known sensitive headers
    if (event.request?.headers) {
      delete event.request.headers["authorization"];
      delete event.request.headers["cookie"];
      delete event.request.headers["x-api-key"];
    }
    // Redact request body
    if (event.request?.data) {
      event.request.data = "[REDACTED]";
    }
    return event;
  },
});
```

Why this satisfies secrets-management.no-secrets-in-logs: error monitoring is a
common path for accidental disclosure. The beforeSend hook
redacts at the SDK layer before transmission to the
monitoring backend.

## Cross-reference

- Anti-patterns: examples/secrets-management/no-secrets-in-logs-anti-pattern.md
- Substrate rule: secrets-management.no-secrets-in-logs
- Static analysis binding: checklist.md
