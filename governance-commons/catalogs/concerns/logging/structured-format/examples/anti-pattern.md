<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.structured-format structured logging format

Substrate-original anti-pattern examples for logging.structured-format.

## Anti-pattern A: print statements in production code

```python
# Anti-pattern: print bypasses the logger entirely
def handle_user_login(user, request):
    print(f"User {user.id} logged in from {request.remote_addr}")
    return success_response()
```

Why this violates logging.structured-format: print writes prose to stdout
with no severity field, no correlation ID, no structured
parseable fields. Downstream aggregators must apply per-line
regex to extract any useful information; aggregation tooling
treats every log line as opaque text.

## Anti-pattern B: console.log scattered through Node.js handlers

```javascript
// Anti-pattern: console.log produces unstructured output
app.post('/login', async (req, res) => {
    console.log('user login attempt');
    const user = await authenticate(req.body);
    console.log('user authenticated:', user.id);
    res.json({ success: true });
});
```

Why this violates logging.structured-format: console.log emits prose;
the second call uses string concatenation that produces
parser-fragile output. The aggregator cannot index user_id
as a queryable field.

## Anti-pattern C: prose formatting with logger.info

```python
import logging
log = logging.getLogger(__name__)

# Anti-pattern: structured logger used for unstructured output
log.info(f"User {user.id} performed action {action} at {timestamp}")
```

Why this violates logging.structured-format: although a logger is used, the
message is a prose interpolation. Parsing user_id, action, and
timestamp from the formatted string requires brittle regex.
The structured-logger benefits are forfeited.

## Anti-pattern D: System.out.println in Java production code

```java
public void processOrder(Order order) {
    System.out.println("Processing order: " + order.getId());
    orderRepository.save(order);
    System.out.println("Order saved successfully");
}
```

Why this violates logging.structured-format: System.out.println bypasses
the structured logger framework. The output is prose,
intermixed with logger output if logger is also used, and
typically lacks timestamps or severity.

## Anti-pattern E: fmt.Println in Go production code

```go
func handleRequest(w http.ResponseWriter, r *http.Request) {
    fmt.Println("Received request from", r.RemoteAddr)
    user, err := authenticate(r)
    if err != nil {
        fmt.Println("Authentication failed:", err)
        return
    }
    fmt.Println("User authenticated:", user.ID)
}
```

Why this violates logging.structured-format: fmt.Println emits prose to
stdout with no structure. Error context is lost (the err
value is stringified). The output is not suitable for
aggregator ingestion.

## Anti-pattern F: Hand-built JSON strings

```python
# Anti-pattern: appears structured but is hand-constructed
log.info(f'{{"event":"user_login","user_id":"{user.id}","ip":"{ip}"}}')
```

Why this violates logging.structured-format: while the output happens to be
JSON-shaped, the construction is hand-built string
interpolation that produces malformed JSON when any
interpolated value contains a quote, backslash, or newline.
The substrate-recommended approach is a structured logger
that handles escaping correctly.

## Anti-pattern G: puts in Ruby production code

```ruby
# Anti-pattern: puts produces prose with no metadata
class OrdersController < ApplicationController
  def create
    puts "Creating order for user #{current_user.id}"
    @order = Order.create!(order_params)
    puts "Order created with id #{@order.id}"
  end
end
```

Why this violates logging.structured-format: puts emits prose to stdout.
Rails apps typically have Rails.logger configured with a
structured formatter; using puts bypasses it.

## Cross-reference

- Good patterns: examples/logging/structured-format-good.md
- Substrate rule: logging.structured-format
