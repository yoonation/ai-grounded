<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.typed-error-classification typed error classification

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python typed error hierarchy

```python
# app/errors.py

class ApplicationError(Exception):
    """Base for all application-typed errors."""

class DomainError(ApplicationError):
    """User-actionable outcomes mapping to 4xx."""

class InfrastructureError(ApplicationError):
    """Operational failures mapping to 5xx."""

# Domain subclasses
class ResourceNotFound(DomainError):
    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id

class DuplicateKey(DomainError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value

class InvalidStateTransition(DomainError):
    def __init__(self, current: str, requested: str):
        self.current = current
        self.requested = requested

# Infrastructure subclasses
class DatabaseUnavailable(InfrastructureError):
    def __init__(self, operation: str, cause: Exception):
        self.operation = operation
        self.cause = cause

class DownstreamTimeout(InfrastructureError):
    def __init__(self, service: str, cause: Exception):
        self.service = service
        self.cause = cause

class ConfigurationError(InfrastructureError):
    def __init__(self, setting: str):
        self.setting = setting
```

The hierarchy has a top-level distinction between domain and
infrastructure errors. Each subclass carries fields that the
client (for domain) or operator (for infrastructure) can act
on.

## Pattern B: Type-discriminator classifier

```python
# app/error_handler.py

DOMAIN_STATUS = {
    ResourceNotFound: 404,
    DuplicateKey: 409,
    InvalidStateTransition: 422,
}

INFRA_STATUS = {
    DatabaseUnavailable: 503,
    DownstreamTimeout: 504,
    ConfigurationError: 500,
}

def classify(e: Exception) -> tuple[int, str, str]:
    if isinstance(e, DomainError):
        status = next(
            (status for cls, status in DOMAIN_STATUS.items() if isinstance(e, cls)),
            400,
        )
        return (status, "domain", type(e).__name__)
    if isinstance(e, InfrastructureError):
        status = next(
            (status for cls, status in INFRA_STATUS.items() if isinstance(e, cls)),
            500,
        )
        return (status, "infrastructure", type(e).__name__)
    return (500, "unhandled", type(e).__name__)
```

The classifier uses `isinstance` (the Python type discriminator)
to map to HTTP status; no string matching on the message field.

## Pattern C: Java typed hierarchy with sealed interfaces

```java
// app/errors/DomainError.java
public sealed interface DomainError permits
    ResourceNotFound, DuplicateKey, InvalidStateTransition {}

public final class ResourceNotFound extends RuntimeException implements DomainError {
    private final String resourceType;
    private final String resourceId;
    // constructor, accessors
}

// app/errors/InfrastructureError.java
public sealed interface InfrastructureError permits
    DatabaseUnavailable, DownstreamTimeout, ConfigurationError {}

// app/errors/ErrorClassifier.java
public class ErrorClassifier {
    public HttpStatus statusFor(Exception e) {
        return switch (e) {
            case ResourceNotFound r -> HttpStatus.NOT_FOUND;
            case DuplicateKey d -> HttpStatus.CONFLICT;
            case InvalidStateTransition i -> HttpStatus.UNPROCESSABLE_ENTITY;
            case DatabaseUnavailable d -> HttpStatus.SERVICE_UNAVAILABLE;
            case DownstreamTimeout t -> HttpStatus.GATEWAY_TIMEOUT;
            case ConfigurationError c -> HttpStatus.INTERNAL_SERVER_ERROR;
            default -> HttpStatus.INTERNAL_SERVER_ERROR;
        };
    }
}
```

Java 17+ sealed interfaces give the compiler an exhaustive
check: every DomainError subclass must be listed in the
classifier's switch. Adding a new error class without a
mapping is a compile error.

## Pattern D: Go typed errors with errors.As

```go
// app/errors/domain.go
package errors

type ResourceNotFound struct {
    ResourceType string
    ResourceID   string
}
func (e ResourceNotFound) Error() string {
    return fmt.Sprintf("%s %s not found", e.ResourceType, e.ResourceID)
}

type DuplicateKey struct {
    Field string
    Value string
}
func (e DuplicateKey) Error() string {
    return fmt.Sprintf("duplicate %s: %s", e.Field, e.Value)
}

// app/handler/classify.go
func StatusFor(err error) int {
    var notFound *errors.ResourceNotFound
    if errors.As(err, &notFound) {
        return http.StatusNotFound
    }
    var duplicate *errors.DuplicateKey
    if errors.As(err, &duplicate) {
        return http.StatusConflict
    }
    var dbUnavail *errors.DatabaseUnavailable
    if errors.As(err, &dbUnavail) {
        return http.StatusServiceUnavailable
    }
    return http.StatusInternalServerError
}
```

`errors.As` is the Go-idiomatic type discriminator. The wrap
chain (errors.Wrap, fmt.Errorf with %w) preserves the typed
error through layers; errors.As unwraps to find the typed
instance.

## Pattern E: Adapter wraps library exceptions

```python
# app/adapters/order_repo.py

class OrderRepository:
    def get_order(self, order_id: str) -> Order:
        try:
            row = self._db.execute(SQL, (order_id,)).fetchone()
        except psycopg.OperationalError as e:
            raise DatabaseUnavailable("get_order", e) from e
        except psycopg.IntegrityError as e:
            raise InfrastructureError("get_order: integrity violation", e) from e
        if row is None:
            raise ResourceNotFound("order", order_id)
        return Order.from_row(row)
```

The adapter catches library-specific exceptions
(`psycopg.OperationalError`) and re-raises as application-
typed `DatabaseUnavailable`. The domain "not found" case
raises `ResourceNotFound`. Higher layers see only
application-typed exceptions; library types do not leak.

## Pattern F: Test asserting type-based classification

```python
def test_resource_not_found_maps_to_404():
    err = ResourceNotFound("order", "123")
    status, category, name = classify(err)
    assert status == 404
    assert category == "domain"
    assert name == "ResourceNotFound"

def test_message_change_does_not_affect_classification():
    # Even if we change the message, the classification holds
    err = DatabaseUnavailable("get_order", RuntimeError("connection reset"))
    err.args = ("totally different message",)  # Simulate a refactor
    status, category, _ = classify(err)
    assert status == 503  # Type-based: unchanged
    assert category == "infrastructure"
```

The test verifies the classifier uses the type, not the
message. A future refactor that changes error messages will
not silently break classification.
