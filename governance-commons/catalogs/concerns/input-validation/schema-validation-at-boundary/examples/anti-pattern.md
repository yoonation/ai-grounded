<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: input-validation.schema-validation-at-boundary schema validation at boundary (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Handler reads request.json directly (Python / Flask)

```python
# FORBIDDEN: no schema; the handler accesses dict keys with
# ad-hoc isinstance checks. The input contract is implicit.
@app.route("/orders", methods=["POST"])
def create_order_BAD():
    body = request.get_json()
    if not isinstance(body, dict):
        return jsonify({"error": "must be object"}), 400
    customer_id = body.get("customer_id")
    if not isinstance(customer_id, str):
        return jsonify({"error": "customer_id required"}), 400
    quantity = body.get("quantity", 1)
    if not isinstance(quantity, int) or quantity < 1 or quantity > 10000:
        return jsonify({"error": "invalid quantity"}), 400
    # ... more ad-hoc checks ...
    return OrderService.create(customer_id, quantity)
```

Why this violates input-validation.schema-validation-at-boundary:
- Schema is implicit in the handler body
- Cannot enumerate the input contract without reading every
  handler
- Defensive checks repeat across handlers
- Adding a new field requires editing handler logic; the
  schema cannot be reviewed independently

## Anti-pattern B: Partial validation with silent defaults (Node.js)

```javascript
// FORBIDDEN: missing fields produce silent undefined; type
// mismatches are caught at use site (or in production).
app.post('/orders', async (req, res) => {
  const order = {
    customerId: req.body.customer_id,
    quantity: req.body.quantity || 1,
    itemSku: req.body.item_sku,
    priority: req.body.priority || 'standard',
  };
  // No validation; OrderService.create receives whatever shape
  // the client supplied.
  const created = await OrderService.create(order);
  res.json(created);
});
```

## Anti-pattern C: Spring controller accepting Map<String, Object>

```java
// FORBIDDEN: untyped Map; no @Valid; handler does the
// parsing manually.
@PostMapping("/orders")
public Order createOrderBAD(@RequestBody Map<String, Object> body) {
    String customerId = (String) body.get("customer_id");
    Integer quantity = (Integer) body.get("quantity");  // ClassCastException risk
    String itemSku = (String) body.get("item_sku");
    // ... ad-hoc checks ...
    return orderService.create(customerId, quantity, itemSku);
}
```

## Anti-pattern D: Express handler with no validation

```javascript
// FORBIDDEN: req.body flows directly into the service without
// schema validation. Forward-compatibility hides bugs:
// adding a field to the schema breaks nothing visibly until
// the handler dies on the missing key at deeper layers.
app.post('/orders', async (req, res) => {
  const created = await OrderService.create(req.body);
  res.json(created);
});
```

## Anti-pattern E: Mixed strict and lenient schemas

```python
# FORBIDDEN: different endpoints disagree on unknown-field
# handling. Clients cannot rely on consistent behavior.

class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # strict
    customer_id: UUID
    quantity: int

class UpdateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="allow")  # lenient
    quantity: int
```

When the schema policy varies across the application, clients
cannot rely on either behavior. The substrate-recommended
posture is to choose one (strict, substrate-preferred) and
apply it consistently.

## Why review identifies these

The input-validation.schema-validation-at-boundary review checklist's seven questions flag:
- Schema is not located in a discoverable place
- Handler operates on a raw dict, not a typed instance
- Required vs optional is implicit
- Domain constraints are reimplemented in handler bodies
- Error responses are not consistent across endpoints
- Unknown-field policy varies
- Schema rejections are not surfaced to audit logging
