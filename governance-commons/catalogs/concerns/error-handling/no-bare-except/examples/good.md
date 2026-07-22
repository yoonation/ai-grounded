<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.no-bare-except no bare except

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Python typed except

```python
import logging
logger = logging.getLogger(__name__)

def parse_user_age(raw: str) -> int:
    try:
        return int(raw)
    except ValueError as e:
        logger.warning("invalid age", extra={"raw": raw, "err": str(e)})
        raise InvalidUserInput(field="age", value=raw) from e
```

The handler catches the specific `ValueError` that `int()` can
raise; programming defects (NameError, TypeError) propagate to
an outer handler. The original exception is preserved via
`from e` for diagnostic chains.

## Pattern B: Java multi-catch

```java
public Order loadOrder(String id) throws DataAccessException {
    try {
        return jdbcTemplate.queryForObject(SQL, mapper, id);
    } catch (EmptyResultDataAccessException e) {
        throw new OrderNotFound(id);
    } catch (DataAccessResourceFailureException
             | TransientDataAccessException e) {
        throw new DatabaseUnavailable("loadOrder", e);
    }
}
```

Two narrowly-typed catches handle the documented failure modes;
unhandled exceptions propagate.

## Pattern C: JavaScript instanceof narrowing

```javascript
async function fetchProfile(userId) {
  try {
    return await api.getProfile(userId);
  } catch (err) {
    if (err instanceof NotFoundError) {
      return null;
    }
    if (err instanceof TimeoutError) {
      logger.warn({err, userId}, 'profile fetch timed out');
      throw new DownstreamTimeout('fetchProfile', err);
    }
    throw err;
  }
}
```

The catch uses `instanceof` to narrow to documented application
error classes. Other errors re-raise.

## Pattern D: Go errors.Is and errors.As

```go
order, err := repo.Load(ctx, id)
if err != nil {
    if errors.Is(err, repo.ErrNotFound) {
        return nil, OrderNotFound{ID: id}
    }
    var connErr *repo.ConnectionError
    if errors.As(err, &connErr) {
        return nil, DatabaseUnavailable{Op: "Load", Cause: connErr}
    }
    return nil, fmt.Errorf("loadOrder: %w", err)
}
```

The Go-idiomatic equivalent of typed catches: errors.Is for
sentinel comparison, errors.As for typed error unwrap. The
default branch wraps the unknown error with %w to preserve the
chain.

## Pattern E: Ruby narrow rescue

```ruby
def load_user(id)
  User.find(id)
rescue ActiveRecord::RecordNotFound
  raise UserNotFound.new(id)
rescue ActiveRecord::ConnectionNotEstablished, PG::Error => e
  Rails.logger.error("database unavailable: #{e.class}: #{e.message}")
  raise DatabaseUnavailable.new('load_user', e)
end
```

Specific ActiveRecord and PG exception classes are caught;
generic Exception is not.

## Pattern F: Backstop catch that re-raises

```python
def application_dispatch(request):
    try:
        return route(request)
    except KnownApplicationError:
        raise
    except Exception as e:
        logger.exception(
            "unhandled exception in dispatch",
            extra={"path": request.path, "correlation_id": cid(request)},
        )
        metrics.increment("dispatch.unhandled_exception")
        raise
```

The application's top-level dispatcher catches the universal
class only to log and emit a metric, then re-raises so the
framework's backstop produces the controlled 500 per
error-handling.no-stack-trace-in-response and error-handling.error-status-code. The re-raise is what distinguishes
this acceptable pattern from the antipattern.
