<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.error-response-contract error response contract

Substrate-original good patterns. Adapt to your stack.

## Pattern A: RFC 7807 / 9457 Problem Details (substrate-preferred)

A 4xx response:

```json
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/duplicate-email",
  "title": "Email already registered",
  "status": 409,
  "detail": "An account with this email address already exists.",
  "instance": "urn:uuid:5f1a7b2c-3d4e-4f5a-9b6c-7d8e9f0a1b2c"
}
```

A 5xx response:

```json
HTTP/1.1 503 Service Unavailable
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/database-unavailable",
  "title": "Service temporarily unavailable",
  "status": 503,
  "detail": "The service is temporarily unable to process the request. Please retry after the indicated interval.",
  "instance": "urn:uuid:9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d"
}
```

Both responses use the same five fields with identical
semantics. Clients implement one parser. The `type` URI
resolves to documentation for the problem class.

## Pattern B: Centralized Problem Details builder (Python)

```python
@dataclass
class ProblemDetails:
    type: str
    title: str
    status: int
    detail: str
    instance: str = field(default_factory=lambda: f"urn:uuid:{uuid.uuid4()}")

    def to_response(self):
        return jsonify(asdict(self)), self.status

ERROR_CATALOG = {
    DuplicateEmailError: lambda e: ProblemDetails(
        type="https://api.example.com/errors/duplicate-email",
        title="Email already registered",
        status=409,
        detail="An account with this email address already exists.",
    ),
    DatabaseUnavailableError: lambda e: ProblemDetails(
        type="https://api.example.com/errors/database-unavailable",
        title="Service temporarily unavailable",
        status=503,
        detail="The service is temporarily unable to process the request.",
    ),
}

@app.errorhandler(Exception)
def handle_exception(e):
    builder = ERROR_CATALOG.get(type(e))
    if builder is None:
        return ProblemDetails(
            type="https://api.example.com/errors/internal",
            title="Internal server error",
            status=500,
            detail="An unexpected error occurred. Please contact support if the problem persists.",
        ).to_response()
    return builder(e).to_response()
```

The error catalog is the contract: each typed exception class
has a documented Problem Details mapping. New classes require
catalog entries.

## Pattern C: Spring 6 ProblemDetail built-in

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(DuplicateEmailException.class)
    public ResponseEntity<ProblemDetail> handleDuplicate(DuplicateEmailException e) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.CONFLICT,
            "An account with this email address already exists.");
        problem.setType(URI.create("https://api.example.com/errors/duplicate-email"));
        problem.setTitle("Email already registered");
        problem.setInstance(URI.create("urn:uuid:" + UUID.randomUUID()));
        return ResponseEntity.status(HttpStatus.CONFLICT).body(problem);
    }
}
```

Spring 6's built-in ProblemDetail class implements RFC 7807.
Spring automatically sets the Content-Type to
application/problem+json.

## Pattern D: OpenAPI specification declaring error responses

```yaml
paths:
  /accounts:
    post:
      summary: Register a new account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AccountCreate'
      responses:
        '201':
          description: Account created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Account'
        '400':
          description: Invalid input
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'
        '409':
          description: Email already registered
          content:
            application/problem+json:
              schema:
                $ref: '#/components/schemas/ProblemDetails'

components:
  schemas:
    ProblemDetails:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string
          format: uri
```

The OpenAPI spec declares the error responses with the shared
ProblemDetails schema. Schemathesis or Dredd verifies that
runtime responses conform.

## Pattern E: GraphQL error extensions (when the application is GraphQL)

```json
{
  "data": null,
  "errors": [
    {
      "message": "Email already registered",
      "extensions": {
        "code": "DUPLICATE_EMAIL",
        "type": "https://api.example.com/errors/duplicate-email",
        "instance": "urn:uuid:5f1a7b2c-3d4e-4f5a-9b6c-7d8e9f0a1b2c"
      },
      "path": ["registerAccount"]
    }
  ]
}
```

For GraphQL APIs, the substrate accepts the GraphQL convention
(200 status with errors in body) when documented in the
error-handling.error-handling-strategy ADR. The substrate-preferred extension shape
mirrors the Problem Details fields (type, code, instance).
