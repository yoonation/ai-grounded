<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.no-stack-trace-in-response no stack trace in response

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Flask centralized error handler returning Problem Details

```python
from flask import Flask, jsonify, request
import logging, uuid

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.errorhandler(ResourceNotFound)
def handle_not_found(e):
    instance = f"urn:uuid:{uuid.uuid4()}"
    logger.warning(
        "resource not found",
        extra={
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "instance": instance,
            "correlation_id": request.headers.get("X-Correlation-ID"),
        },
    )
    return jsonify({
        "type": "https://example.com/errors/resource-not-found",
        "title": "Resource not found",
        "status": 404,
        "detail": "The requested resource does not exist or is not accessible.",
        "instance": instance,
    }), 404

@app.errorhandler(Exception)
def handle_unexpected(e):
    instance = f"urn:uuid:{uuid.uuid4()}"
    logger.exception(
        "unhandled exception",
        extra={"instance": instance, "path": request.path},
    )
    return jsonify({
        "type": "https://example.com/errors/internal",
        "title": "Internal server error",
        "status": 500,
        "detail": "An unexpected error occurred. Please contact support if the problem persists.",
        "instance": instance,
    }), 500
```

Centralized handlers produce stable Problem Details responses;
the full exception detail goes to the server log (with the
instance URI for correlation); the client sees only the
contract fields.

## Pattern B: FastAPI exception_handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(ResourceNotFound)
async def resource_not_found_handler(request: Request, exc: ResourceNotFound):
    instance = f"urn:uuid:{uuid.uuid4()}"
    logger.warning("resource not found", extra={"instance": instance, "resource_id": exc.resource_id})
    return JSONResponse(
        status_code=404,
        content={
            "type": "https://example.com/errors/resource-not-found",
            "title": "Resource not found",
            "status": 404,
            "detail": "The requested resource does not exist or is not accessible.",
            "instance": instance,
        },
    )
```

FastAPI's exception_handler infrastructure produces the
controlled response without leaking the underlying exception.

## Pattern C: Spring @ControllerAdvice with ProblemDetail

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ProblemDetail> handleNotFound(ResourceNotFoundException e) {
        String instance = "urn:uuid:" + UUID.randomUUID();
        log.warn("resource not found: type={} id={} instance={}", e.getType(), e.getId(), instance);
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND,
            "The requested resource does not exist or is not accessible.");
        problem.setType(URI.create("https://example.com/errors/resource-not-found"));
        problem.setTitle("Resource not found");
        problem.setInstance(URI.create(instance));
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(problem);
    }
}
```

Spring 6's built-in ProblemDetail support produces RFC 7807 /
9457 responses through the @ControllerAdvice surface.

`application.properties`:

```
server.error.include-stacktrace=never
server.error.include-message=never
server.error.include-exception=false
server.error.include-binding-errors=never
```

The Spring Boot defaults suppress stack traces and exception
messages from the whitelabel page; the application's
@ControllerAdvice handles every path explicitly.

## Pattern D: Express centralized error middleware

```javascript
app.use((err, req, res, next) => {
  const instance = `urn:uuid:${crypto.randomUUID()}`;
  if (err instanceof ResourceNotFoundError) {
    logger.warn({err, instance, path: req.path}, 'resource not found');
    return res.status(404).json({
      type: 'https://example.com/errors/resource-not-found',
      title: 'Resource not found',
      status: 404,
      detail: 'The requested resource does not exist or is not accessible.',
      instance,
    });
  }
  logger.error({err, instance, path: req.path}, 'unhandled exception');
  return res.status(500).json({
    type: 'https://example.com/errors/internal',
    title: 'Internal server error',
    status: 500,
    detail: 'An unexpected error occurred.',
    instance,
  });
});
```

The four-argument middleware is Express's error-handler form;
the response is constructed explicitly without invoking the
development error handler.

## Pattern E: Production environment configuration

`.env` (production):
```
FLASK_ENV=production
FLASK_DEBUG=false
DJANGO_DEBUG=false
NODE_ENV=production
SPRING_PROFILES_ACTIVE=production
RAILS_ENV=production
```

Framework debug modes are explicitly disabled. The deployment
pipeline verifies these settings (Checkov against Terraform
defining the environment; kube-linter against Kubernetes
ConfigMaps; team review against any other deployment
mechanism).
