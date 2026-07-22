<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.error-status-code hardcoded success status on error

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Flask returns 200 with error body

```python
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order = service.create(request.json)
        return jsonify(order)
    except DuplicateKeyError as e:
        return jsonify({"error": "duplicate", "message": str(e)})
```

Both the success path and the error path return implicit 200.
The error path is invisible to load balancers, retry middleware,
observability dashboards, and CDN error tracking. The Semgrep
registry rule
`python.flask.security.audit.hardcoded-200-on-error` flags
the pattern when 200 is explicit; the implicit-200 case (no
status argument to jsonify) is caught by per-framework
linters.

## Antipattern B: Explicit 200 with error key

```python
return jsonify({"error": "duplicate"}), 200
```

The substrate-detection-canonical antipattern: an error body
with an explicit 200 status. The Semgrep registry rule
catches the literal pattern.

## Antipattern C: Express res.json without status

```javascript
app.post('/orders', async (req, res) => {
  try {
    const order = await service.create(req.body);
    res.json(order);
  } catch (err) {
    res.json({error: 'failed', message: err.message});
  }
});
```

`res.json` without `res.status` defaults to 200. Both branches
return 200; clients have no protocol-level signal of failure.

## Antipattern D: Express res.status(200).json(error)

```javascript
res.status(200).json({error: 'internal'});
```

Explicit 200 with error body. The Semgrep registry rule
`javascript.express.best-practice.error-status-200` flags
this.

## Antipattern E: Go w.WriteHeader(200) for error

```go
order, err := svc.CreateOrder(ctx, body)
if err != nil {
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{
        "error": err.Error(),
    })
    return
}
```

`http.StatusOK` (200) on the error branch. This is the most
explicit form of the antipattern: the developer chose the
success status code despite knowing this is an error path.

## Antipattern F: Spring ResponseEntity.ok with error body

```java
return ResponseEntity.ok(new ErrorResponse("duplicate", e.getMessage()));
```

`ResponseEntity.ok(...)` always returns 200 OK. The Semgrep
registry rule
`java.spring.best-practice.return-ok-with-error-body`
flags this. The substrate-required pattern is
`ResponseEntity.status(HttpStatus.CONFLICT).body(...)` or
equivalent.

## Antipattern G: Helper that always returns 200

```python
def respond(data):
    return jsonify(data)

@app.route('/orders/<id>')
def get_order(id):
    try:
        order = service.get(id)
        return respond({"order": order})
    except OrderNotFound:
        return respond({"error": "not found"})
```

The `respond` helper does not accept a status argument; every
call returns implicit 200. The substrate's L1 binding catches
the helper itself with custom rule support but the basic
registry rule may not (taint or call-graph analysis required);
error-handling.error-response-contract review catches the design.

## Antipattern H: GraphQL-style errors-in-200 outside GraphQL

```python
@app.route('/api/v1/users/<id>')
def get_user(id):
    try:
        user = service.get(id)
        return jsonify({"data": user, "errors": []})
    except UserNotFound:
        return jsonify({"data": None, "errors": [{"message": "not found"}]})
```

The "always 200 with errors in body" pattern is the GraphQL
convention but the substrate accepts it only for GraphQL
endpoints documented in the error-handling.error-handling-strategy ADR. Applying the
convention to REST endpoints is the antipattern: REST clients
expect HTTP status codes to classify outcomes, and
infrastructure (load balancers, CDN, retry middleware) cannot
inspect response bodies.

## Antipattern I: HTML error response with 200

```python
@app.errorhandler(404)
def handle_not_found(e):
    return render_template('not_found.html'), 200
```

Even though the handler is wired to the 404 errorhandler, the
return statement overrides with 200. The HTML page may say
"not found" to the user but the protocol says success; CDN
caches the response as a successful 200 and serves it to
other users.

## Remediation

For each antipattern above:

1. Identify the error category per the substrate's status
   mapping in `error-status-code-good.md`.

2. Update the response construction to set the explicit
   status code (jsonify(..., status_code=X); res.status(X);
   ResponseEntity.status(X); w.WriteHeader(X)).

3. Refactor helpers that hardcode 200 to require status as
   a parameter; no default value.

4. Where the GraphQL "always 200" convention applies (only
   for GraphQL endpoints), document the exception in the
   error-handling.error-handling-strategy ADR; ensure REST endpoints follow the
   substrate's status mapping.

5. Update OpenAPI specifications to declare error responses
   at 4xx and 5xx; run Schemathesis or Dredd in CI to verify
   runtime conformance.
