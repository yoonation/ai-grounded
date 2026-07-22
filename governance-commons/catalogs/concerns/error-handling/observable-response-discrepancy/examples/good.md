<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Good example: error-handling.observable-response-discrepancy observable response discrepancy

Substrate-original good patterns. Adapt to your stack.

error-handling.observable-response-discrepancy governs cases where the response to an unauthorized
request differs from the response to a request for a
nonexistent resource. The discrepancy lets an unauthenticated
or unauthorized client enumerate resource existence by probing.
This is the broader companion to authentication.generic-failure-responses (generic error
messages for authentication).

## Pattern A: identical 404 for missing and forbidden (Python FastAPI)

```python
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    principal: Principal = Depends(current_principal),
):
    order = await repo.get_order(order_id)
    if order is None or not policy.can_read_order(principal, order):
        raise HTTPException(
            status_code=404,
            detail={
                "type": "https://example.com/errors/not-found",
                "title": "Not Found",
                "status": 404,
                "detail": "Order not found",
            },
        )
    return order
```

The handler treats "does not exist" and "exists but principal
may not read" as the same outcome. The client cannot tell
which condition obtains.

## Pattern B: timing-equalized lookup (Python)

```python
import secrets
import asyncio

async def get_order_safe(order_id, principal):
    # Start the policy decision concurrently with the lookup so
    # both timing paths take comparable wall time regardless of
    # whether the order exists.
    order_task = asyncio.create_task(repo.get_order(order_id))
    policy_task = asyncio.create_task(policy.can_read(principal, order_id))

    order = await order_task
    allowed = await policy_task

    if order is None or not allowed:
        # Equal-time random delay reduces residual signal.
        await asyncio.sleep(secrets.randbelow(50) / 1000.0)
        raise NotFound()
    return order
```

The same authorization check runs regardless of whether the
order was found, eliminating the timing channel that
short-circuit code paths create. The random delay is a
defense-in-depth measure, not a replacement for equal-time
code paths.

## Pattern C: 403 for both missing and forbidden when 404 leaks (Java)

```java
@GetMapping("/orders/{orderId}")
public Order getOrder(@PathVariable String orderId, Principal principal) {
    Order order = repo.findById(orderId).orElse(null);
    boolean allowed = policy.canRead(principal, order);
    if (order == null || !allowed) {
        throw new ResponseStatusException(
            HttpStatus.FORBIDDEN,
            "Access denied"
        );
    }
    return order;
}
```

Some APIs prefer 403 as the "blanket" status when even
acknowledging the path structure would leak information. Either
choice is acceptable per error-handling.observable-response-discrepancy; the substrate position is
that the two error paths produce identical responses.

## Pattern D: list-endpoint filter that returns empty (Node.js)

```javascript
app.get('/api/users/:userId/orders', async (req, res) => {
  const { userId } = req.params;
  const principal = req.principal;

  if (!policy.canListOrdersFor(principal, userId)) {
    // Return empty array rather than 403, to match the response
    // for "user exists but has no orders".
    return res.status(200).json({ orders: [] });
  }

  const orders = await repo.listOrdersFor(userId);
  return res.status(200).json({ orders });
});
```

For list endpoints, the substrate-recommended pattern is to
return an empty list rather than a different status code. The
client cannot distinguish "you cannot see this user's orders"
from "this user has no orders".

## Pattern E: HEAD request returns same status as GET (Go)

```go
func (h *Handler) HeadOrder(w http.ResponseWriter, r *http.Request) {
    orderID := chi.URLParam(r, "id")
    principal := middleware.PrincipalFrom(r.Context())

    order, err := h.repo.Get(r.Context(), orderID)
    allowed := h.policy.CanRead(principal, order)

    if err != nil || !allowed {
        w.WriteHeader(http.StatusNotFound)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

HEAD must match GET status. Different HEAD/GET status pairs
also create enumeration vectors.

## Pattern F: shape-stable error body (Python)

```python
def deny_response():
    return {
        "type": "https://example.com/errors/not-found",
        "title": "Not Found",
        "status": 404,
        "detail": "The requested resource was not found or "
                  "is not accessible.",
    }, 404


@app.errorhandler(NotFoundError)
@app.errorhandler(AuthorizationDenied)
def handle_not_found_or_denied(e):
    return deny_response()
```

A single function generates the response for both error classes.
The body is bitwise-identical: no rule ID, no timestamp, no
correlation ID, no message variation that could carry a signal.
The correlation ID is recorded in logs only.

## Substrate-recommended decision table

| Endpoint shape | Resource exists, may read | Resource exists, may not read | Resource missing |
|---|---|---|---|
| GET /resources/{id} | 200 + body | 404 + generic Problem Details | 404 + same generic Problem Details |
| HEAD /resources/{id} | 200 | 404 | 404 |
| GET /resources (list, scoped) | 200 + filtered list | 200 + empty list for unscoped portion | 200 + empty list |
| POST /resources | 201 + Location | 403 + generic Problem Details | n/a (create not lookup) |
| PUT /resources/{id} | 200 + body | 404 + generic Problem Details | 404 + same generic Problem Details |
| DELETE /resources/{id} | 204 | 404 + generic Problem Details | 404 + same generic Problem Details |

The substrate-recommended rule: every "unauthorized read"
response is bitwise-identical to "resource missing" for the
same endpoint.
