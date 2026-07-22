<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.error-status-code error status code

Substrate-original good patterns. Adapt to your stack.

## Pattern A: Flask returns 4xx for client errors

```python
@app.errorhandler(InvalidInputError)
def handle_invalid_input(e):
    return jsonify({
        "type": "https://example.com/errors/invalid-input",
        "title": "Invalid input",
        "status": 400,
        "detail": e.message,
        "instance": new_instance(),
    }), 400

@app.errorhandler(DuplicateKeyError)
def handle_duplicate_key(e):
    return jsonify({
        "type": "https://example.com/errors/duplicate-key",
        "title": "Conflict",
        "status": 409,
        "detail": f"A resource with this {e.field} already exists.",
        "instance": new_instance(),
    }), 409
```

Each error class returns its mapped status code (400 for
input, 409 for conflict). The body's `status` field mirrors
the HTTP status per RFC 7807 / 9457.

## Pattern B: FastAPI HTTPException with mapped statuses

```python
from fastapi import HTTPException, status

@app.post("/orders")
async def create_order(order_in: OrderCreate):
    try:
        return await service.create_order(order_in)
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"type": "https://example.com/errors/duplicate-key", "title": "Conflict", "detail": str(e)},
        )
    except InsufficientFundsError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"type": "https://example.com/errors/insufficient-funds", "title": "Unprocessable", "detail": str(e)},
        )
```

The FastAPI HTTPException carries an explicit status code per
error class.

## Pattern C: Express explicit status with json

```javascript
app.post('/orders', async (req, res, next) => {
  try {
    const order = await service.createOrder(req.body);
    return res.status(201).json(order);
  } catch (err) {
    if (err instanceof DuplicateKeyError) {
      return res.status(409).json({
        type: 'https://example.com/errors/duplicate-key',
        title: 'Conflict',
        status: 409,
        detail: `A resource with this ${err.field} already exists.`,
      });
    }
    if (err instanceof InsufficientFundsError) {
      return res.status(422).json({
        type: 'https://example.com/errors/insufficient-funds',
        title: 'Unprocessable',
        status: 422,
        detail: 'Account balance is insufficient.',
      });
    }
    return next(err);
  }
});
```

Every error branch sets the status code explicitly before
emitting the JSON body.

## Pattern D: Spring ResponseEntity with HttpStatus

```java
@PostMapping("/orders")
public ResponseEntity<?> createOrder(@RequestBody OrderCreate body) {
    try {
        Order order = service.create(body);
        return ResponseEntity.status(HttpStatus.CREATED).body(order);
    } catch (DuplicateKeyException e) {
        return ResponseEntity
            .status(HttpStatus.CONFLICT)
            .body(problemDetails("duplicate-key", e.getField()));
    } catch (InsufficientFundsException e) {
        return ResponseEntity
            .status(HttpStatus.UNPROCESSABLE_ENTITY)
            .body(problemDetails("insufficient-funds", e.getMessage()));
    }
}
```

`ResponseEntity.status(HttpStatus.X)` requires an explicit
status. The HttpStatus enum names guide developers toward
correct status selection.

## Pattern E: Go http.Error with status

```go
func handleCreateOrder(w http.ResponseWriter, r *http.Request) {
    order, err := svc.CreateOrder(r.Context(), parseBody(r))
    if err != nil {
        var duplicate *service.DuplicateKeyError
        if errors.As(err, &duplicate) {
            writeProblem(w, http.StatusConflict,
                "duplicate-key", duplicate.Error())
            return
        }
        var insufficient *service.InsufficientFundsError
        if errors.As(err, &insufficient) {
            writeProblem(w, http.StatusUnprocessableEntity,
                "insufficient-funds", insufficient.Error())
            return
        }
        writeProblem(w, http.StatusInternalServerError, "internal", "")
        return
    }
    writeJSON(w, http.StatusCreated, order)
}

func writeProblem(w http.ResponseWriter, status int, problemType, detail string) {
    w.Header().Set("Content-Type", "application/problem+json")
    w.WriteHeader(status)
    _ = json.NewEncoder(w).Encode(map[string]any{
        "type":   "https://example.com/errors/" + problemType,
        "title":  http.StatusText(status),
        "status": status,
        "detail": detail,
    })
}
```

The helper requires status as a parameter; there is no default
that could accidentally produce 200 for an error response.

## Pattern F: Substrate status mapping table

Substrate-recommended mapping for common error classes:

| Error class | Status code | Notes |
|---|---|---|
| Invalid input (schema rejection, malformed body) | 400 | Client must fix the input |
| Missing authentication | 401 | Client must authenticate |
| Authorization denied | 403 | Authenticated but not authorized; **substrate caveat**: per error-handling.observable-response-discrepancy, use 404 instead when the alternative reveals resource existence |
| Resource not found | 404 | Including resource-exists-but-unauthorized per error-handling.observable-response-discrepancy |
| Duplicate key, optimistic lock conflict | 409 | Client may retry with updated state |
| Semantic validation failure (well-formed but invalid) | 422 | E.g., insufficient funds, invalid state transition |
| Rate limit | 429 | Client must back off; include Retry-After header |
| Unhandled server error | 500 | Operator must investigate |
| Downstream dependency error | 502 | Upstream unavailable |
| Planned unavailability | 503 | Include Retry-After if known |
| Downstream timeout | 504 | Caller may retry per error-handling.retry-and-circuit-breaker |
