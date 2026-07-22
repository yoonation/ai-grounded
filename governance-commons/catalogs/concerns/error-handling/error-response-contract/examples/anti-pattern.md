<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.error-response-contract inconsistent error response shape

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Per-endpoint ad-hoc shapes

```javascript
// /accounts endpoint
res.status(409).json({error: 'duplicate_email'});

// /orders endpoint
res.status(409).json({message: 'order conflict', code: 'CONFLICT'});

// /products endpoint
res.status(409).json({errors: [{type: 'duplicate', detail: 'already exists'}]});
```

Three endpoints produce three different shapes for the same
error class (409 Conflict). Each client must implement three
parsers. Observability tools cannot classify errors uniformly.

## Antipattern B: Inconsistent field naming

```python
# Some endpoints
return jsonify({"error_message": "..."}), 400

# Other endpoints
return jsonify({"errorMessage": "..."}), 400

# Yet other endpoints
return jsonify({"err": "..."}), 400
```

Field name casing and abbreviation vary; clients with
strongly-typed bindings cannot share a schema.

## Antipattern C: Mix of success-shape and error-shape

```python
# Success returns the resource
return jsonify(order)

# Failure returns a different envelope
return jsonify({"success": false, "error": "..."}), 400
```

Success and error use entirely different shapes. The client
must inspect each response to determine the shape; auto-
generated client bindings produce poor abstractions.

## Antipattern D: Generic error key with no structure

```python
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500
```

The handler emits whatever str(e) produces; the shape is
implicit in the exception's __str__ method. Different
exception classes produce different (and unpredictable)
content in the error field. The substrate's L1 binding
(error-handling.no-stack-trace-in-response) catches this for the stack-trace case;
error-handling.error-response-contract catches the design-time absence of a contract.

## Antipattern E: Multiple contracts within one application

```python
# Auth endpoints use one shape
return jsonify({
    "error_code": "INVALID_CREDENTIALS",
    "error_message": "...",
}), 401

# Order endpoints use another
return jsonify({
    "type": "https://api.example.com/errors/...",
    "title": "...",
    "status": 409,
    "detail": "...",
}), 409
```

Two contracts coexist in one application. Clients need two
parsers. The team made different decisions over time without
consolidating.

## Antipattern F: HTML for some errors, JSON for others

```python
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "internal"}), 500
```

The 404 handler returns HTML; the 500 handler returns JSON.
API clients consuming the 404 receive an HTML response their
JSON parser cannot handle. The substrate-required pattern is
content negotiation: emit HTML when the Accept header
requests it, emit Problem Details JSON for application/json
or application/problem+json.

## Antipattern G: Stack trace in some responses, contract in others

```python
@app.errorhandler(DuplicateKeyError)
def handle_duplicate(e):
    return jsonify({"type": "...", "title": "...", "status": 409}), 409

@app.errorhandler(Exception)
def handle_other(e):
    return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500
```

The DuplicateKeyError handler is good; the generic handler
violates error-handling.no-stack-trace-in-response by leaking the trace. error-handling.error-response-contract catches
the inconsistency: not every error class flows through the
contract.

## Antipattern H: GraphQL-style errors-in-200 outside GraphQL

```python
# REST endpoint
return jsonify({"data": None, "errors": [{"message": "..."}]})
```

The "always 200 with errors array" shape is GraphQL's
convention; applied to a REST endpoint, it violates both
error-handling.error-status-code (no error status code) and error-handling.error-response-contract
(inconsistency with the rest of the REST surface, which
presumably uses status codes).

## Remediation

For each antipattern above:

1. Select the substrate-preferred contract (RFC 7807 / 9457
   Problem Details for HTTP APIs) or the alternative
   documented in the application's error-handling.error-handling-strategy ADR.

2. Implement a central error handler that all endpoints
   route through. The handler is the only place that
   constructs error response bodies.

3. Refactor endpoint-local error returns to raise typed
   exceptions per error-handling.typed-error-classification; the central handler maps each
   to the contract.

4. Update the OpenAPI specification to declare error
   responses with the contract's schema. Use Schemathesis
   or Dredd in CI to verify runtime conformance.

5. Document the contract in the error-handling.error-handling-strategy ADR. Note any
   deviations (e.g., GraphQL-specific endpoints) with
   rationale.
