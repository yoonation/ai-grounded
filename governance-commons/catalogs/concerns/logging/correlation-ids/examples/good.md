<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: logging.correlation-ids correlation IDs (good patterns)

Substrate-original good-pattern examples for logging.correlation-ids.

## Pattern A: Django middleware binding request ID

```python
# settings.py
MIDDLEWARE = [
    'log_request_id.middleware.RequestIDMiddleware',
    # ... other middleware
]

LOGGING = {
    'version': 1,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        }
    },
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(request_id)s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': ['request_id'],
            'formatter': 'json',
        }
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
```

Why this satisfies logging.correlation-ids: the middleware extracts or
generates a request_id for every request; the logging filter
attaches it to every record emitted during the request's
scope. Call sites do not need to remember to pass the ID.

## Pattern B: OpenTelemetry-instrumented Python

```python
from opentelemetry import trace
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=True)

tracer = trace.get_tracer(__name__)
import logging
log = logging.getLogger(__name__)

@tracer.start_as_current_span("process_order")
def process_order(order_id):
    log.info("processing order", extra={"order_id": order_id})
```

Why this satisfies logging.correlation-ids: LoggingInstrumentor injects
trace_id and span_id into every log record automatically.
The trace context propagates across service boundaries via
W3C Trace Context headers.

## Pattern C: Express correlation middleware

```javascript
const expressRequestId = require('express-request-id');
const pinoHttp = require('pino-http');

app.use(expressRequestId());
app.use(pinoHttp({
    customProps: (req) => ({ request_id: req.id }),
}));

app.get('/api/users/:id', async (req, res) => {
    req.log.info({ user_id: req.params.id }, 'fetching user');
    const user = await users.find(req.params.id);
    res.json(user);
});
```

Why this satisfies logging.correlation-ids: express-request-id generates or
extracts a request ID per request; pino-http binds it as a
default field. Every log line during the request's scope
carries the correlation.

## Pattern D: Go context-propagated zerolog

```go
import (
    "context"
    "github.com/rs/zerolog"
)

func withRequestID(ctx context.Context, id string) context.Context {
    return zerolog.Ctx(ctx).With().Str("request_id", id).Logger().WithContext(ctx)
}

func handleRequest(w http.ResponseWriter, r *http.Request) {
    ctx := withRequestID(r.Context(), r.Header.Get("X-Request-ID"))
    log := zerolog.Ctx(ctx)
    log.Info().Str("user_id", userID).Msg("processing request")
    processBusinessLogic(ctx)
}

func processBusinessLogic(ctx context.Context) {
    log := zerolog.Ctx(ctx)
    log.Info().Msg("business logic executed")
}
```

Why this satisfies logging.correlation-ids: the request_id is bound to a
logger stored in the context. Downstream functions retrieve
the logger via zerolog.Ctx(ctx); the correlation propagates
across function boundaries without explicit parameter
passing.

## Pattern E: Java MDC with slf4j

```java
@Component
public class RequestIDFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain chain) throws ServletException, IOException {
        String requestId = request.getHeader("X-Request-ID");
        if (requestId == null) {
            requestId = UUID.randomUUID().toString();
        }
        MDC.put("request_id", requestId);
        try {
            chain.doFilter(request, response);
        } finally {
            MDC.remove("request_id");
        }
    }
}
```

Why this satisfies logging.correlation-ids: slf4j MDC (Mapped Diagnostic
Context) holds the request_id for the thread's scope. All
logger calls within the filter's chain include the field
automatically.

## Pattern F: Background job correlation propagation

```python
import structlog
from celery import Celery, signals

celery = Celery()

@signals.before_task_publish.connect
def add_trace_context(sender, headers, body, **kwargs):
    log = structlog.get_logger()
    trace_id = log._context.get('trace_id')
    if trace_id:
        headers['trace_id'] = trace_id

@signals.task_prerun.connect
def bind_trace_context(task, **kwargs):
    structlog.contextvars.clear_contextvars()
    trace_id = task.request.headers.get('trace_id') if task.request else None
    if trace_id:
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
    else:
        structlog.contextvars.bind_contextvars(job_id=str(task.request.id))
```

Why this satisfies logging.correlation-ids: background jobs receive the
upstream trace_id via the task headers; if no upstream
context exists, a job_id substitutes. The signals ensure the
correlation is bound automatically at job start.

## Cross-reference

- Anti-patterns: examples/logging/correlation-ids-anti-pattern.md
- Substrate rule: logging.correlation-ids
- L1 binding: checklist.md
