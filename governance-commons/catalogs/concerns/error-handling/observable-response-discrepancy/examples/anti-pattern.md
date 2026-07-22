<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.observable-response-discrepancy observable response discrepancy (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: 404 for missing, 403 for forbidden (Python)

```python
# FORBIDDEN: the two error paths return different status codes.
# An attacker enumerates resource existence by submitting random
# IDs and observing 403 (exists) vs 404 (does not exist).
@app.get("/orders/{order_id}")
async def get_order_BAD(order_id, principal=Depends(current_principal)):
    order = await repo.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if not policy.can_read_order(principal, order):
        raise HTTPException(status_code=403, detail="Access denied")
    return order
```

Why this violates error-handling.observable-response-discrepancy:
- A request for orderId="ABC" by an unprivileged user returns
  404 if ABC does not exist and 403 if ABC exists but is owned
  by another user
- The attacker scripts through the orderId space and recovers
  the set of valid IDs
- The discrepancy is the canonical CWE-204 pattern

## Anti-pattern B: distinct error messages (Java)

```java
// FORBIDDEN: the messages distinguish the two cases even though
// the status codes are the same.
@GetMapping("/users/{username}")
public User getUser(@PathVariable String username, Principal principal) {
    User u = repo.findByUsername(username).orElse(null);
    if (u == null) {
        throw new ResponseStatusException(NOT_FOUND, "user does not exist");
    }
    if (!policy.canViewProfile(principal, u)) {
        throw new ResponseStatusException(NOT_FOUND, "user profile is private");
    }
    return u;
}
```

Same status code (404), different bodies. The body string
discloses the existence of the user. The discrepancy in body
content is the violation.

## Anti-pattern C: timing-based existence reveal (Python)

```python
# FORBIDDEN: the lookup short-circuits when the order is missing,
# producing a fast 404 path. The authorization-denied path takes
# longer because it loads the order before checking policy. The
# timing difference is measurable.
async def get_order_BAD(order_id, principal):
    order = await repo.get_order(order_id)
    if order is None:
        # fast path: ~5ms
        raise HTTPException(404)
    # slow path: ~30ms (DB load + policy check)
    if not policy.can_read(principal, order):
        raise HTTPException(404)
    return order
```

The status codes are identical here, but the timing signal
remains. An attacker with statistical timing measurements can
distinguish the two paths over enough samples.

## Anti-pattern D: WWW-Authenticate header leaks the resource exists (Node.js)

```javascript
// FORBIDDEN: the 401 vs 404 distinction reveals existence via
// the protocol-level challenge.
app.get('/api/secret-projects/:id', (req, res) => {
  const project = repo.find(req.params.id);
  if (!project) {
    return res.status(404).json({ error: 'not found' });
  }
  if (!req.user) {
    res.set('WWW-Authenticate', 'Bearer realm="secret-projects"');
    return res.status(401).end();
  }
  if (!policy.canView(req.user, project)) {
    return res.status(403).json({ error: 'forbidden' });
  }
  return res.json(project);
});
```

The WWW-Authenticate challenge fires only when the project
exists. An unauthenticated probe distinguishes existing IDs
by the presence of the challenge header.

## Anti-pattern E: response shape varies (Go)

```go
// FORBIDDEN: the shape of the body differs between the two
// error paths. The body for "not found" has 3 keys; the body
// for "forbidden" has 4 keys.
func GetOrderBAD(w http.ResponseWriter, r *http.Request) {
    order, err := repo.Get(r.Context(), chi.URLParam(r, "id"))
    if errors.Is(err, repo.ErrNotFound) {
        json.NewEncoder(w).Encode(map[string]any{
            "type":   "not-found",
            "title":  "Not Found",
            "status": 404,
        })
        w.WriteHeader(404)
        return
    }
    if !policy.CanRead(principalOf(r), order) {
        json.NewEncoder(w).Encode(map[string]any{
            "type":          "not-found",
            "title":         "Not Found",
            "status":        404,
            "correlationId": correlationID(r),
        })
        w.WriteHeader(404)
        return
    }
    json.NewEncoder(w).Encode(order)
}
```

Same status code, but the second response carries a
correlationId field. The presence/absence of the extra key is
the signal. Even with the same key set, the random length of
the correlation ID would be a timing variance.

## Anti-pattern F: list response shape varies for visibility (Python)

```python
# FORBIDDEN: the list endpoint reveals whether the principal can
# read at least one resource in the scope. Empty-because-scope
# is a different response shape than empty-because-no-resources.
@app.get("/users/{user_id}/orders")
def list_orders_BAD(user_id, principal):
    if not policy.can_list_for(principal, user_id):
        return jsonify({"error": "forbidden", "status": 403}), 403
    orders = repo.list_for(user_id)
    return jsonify({"orders": orders}), 200
```

The 403-vs-200-with-empty-list distinction reveals access
control state. The good pattern returns 200 with empty list
in both cases.

## Anti-pattern G: rate-limited only on found resources

```python
# FORBIDDEN: the rate limiter counts only successful lookups.
# An attacker who hits 404 paths is not rate-limited, allowing
# unbounded enumeration of nonexistent IDs.
@app.get("/orders/{order_id}")
@rate_limit_only_on_success
async def get_order_BAD(order_id, principal):
    ...
```

Rate limits should apply to the route, not to the outcome. The
substrate-recommended pattern applies the same rate limit
regardless of whether the response is 200, 404, or 403.

## Why this matters

error-handling.observable-response-discrepancy is at the L2 layer because L1 mechanical detection
catches only narrow patterns. The full violation is about
*operational behavior*: whether identical inputs from different
principals produce identical responses across status, body,
timing, headers, and rate-limit behavior. L2 review must trace
the full request lifecycle for each error class.
