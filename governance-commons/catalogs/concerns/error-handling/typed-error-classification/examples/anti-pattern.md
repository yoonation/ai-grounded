<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.typed-error-classification string-matching error classification

Substrate-flagged antipatterns. Do not adopt.

## Antipattern A: Classifier greps the message field

```python
def status_for(e: Exception) -> int:
    msg = str(e).lower()
    if "not found" in msg:
        return 404
    if "duplicate" in msg or "already exists" in msg:
        return 409
    if "connection" in msg or "timeout" in msg:
        return 503
    return 500
```

A simple test passes today. Six months later, someone renames
"duplicate" to "conflict" in one message; classification
silently returns 500 instead of 409. The test suite does not
catch the regression unless it covers every message string.

## Antipattern B: Untyped raise with formatted strings

```python
def create_account(email, password):
    if account_exists(email):
        raise Exception(f"Account with email {email} already exists")
    if not is_valid_email(email):
        raise Exception(f"Invalid email format: {email}")
    return account_repo.insert(email, password)
```

Every error is the language's base Exception. The classifier
must grep the message to decide. Type information that should
discriminate is collapsed into a single class.

## Antipattern C: Mixed domain and infrastructure under one class

```python
class AppException(Exception):
    pass

# In account service
raise AppException("account already exists")

# In database adapter
raise AppException("database connection lost")
```

One class for everything. The classifier cannot distinguish
"domain error: user must change input" from "infrastructure
error: operator must act." Both surface as the same HTTP
status; both alert the same on-call rotation; metric dashboards
cannot separate them.

## Antipattern D: Library exceptions propagating through layers

```python
from psycopg import OperationalError, IntegrityError

# In application's order service (not the adapter)
def create_order(order_data):
    try:
        return repo.insert(order_data)
    except IntegrityError as e:  # psycopg-specific class
        raise HTTPException(409, str(e))
    except OperationalError as e:
        raise HTTPException(503, str(e))
```

The application service catches the database driver's
exceptions directly. The application's typed hierarchy is
empty; everything is library-specific. Replacing psycopg with
a different driver requires rewriting every error-handling
site.

## Antipattern E: Status mapping in the domain layer

```python
def transfer_funds(from_acct, to_acct, amount):
    if amount > from_acct.balance:
        raise HTTPException(422, "Insufficient funds")
    # ...
```

The domain service raises `HTTPException` with a hardcoded
status code. The domain layer leaks HTTP awareness. Reusing
this service for a non-HTTP context (background job, message
consumer) is impossible without rewriting.

## Antipattern F: Boolean error flags

```python
def get_order(order_id):
    result = repo.find(order_id)
    if result is None:
        return {"ok": False, "error": "not found"}
    if result.deleted:
        return {"ok": False, "error": "deleted"}
    return {"ok": True, "data": result}
```

Errors are not exceptions but dict envelopes with string codes.
The classifier (somewhere downstream) string-matches on
"not found" vs "deleted." The pattern fights every framework
convention; mixing it with conventional exception-raising
code produces ad-hoc routing logic.

## Antipattern G: Untested classification

```python
# Classifier exists
def classify(e):
    # ...

# No tests for the classifier
```

The classifier exists but has no tests. New exception classes
are added without verifying the classifier handles them.
Production discovers gaps through 500-response spikes.

## Antipattern H: Default case fall-through with disclosure

```python
@app.errorhandler(Exception)
def handle(e):
    return jsonify({"error": str(e), "type": type(e).__name__}), 500
```

The default case (no typed classification) leaks both the
exception message (which may contain internal detail per
error-handling.no-stack-trace-in-response) and the exception class name. error-handling.no-stack-trace-in-response catches
the disclosure; error-handling.typed-error-classification catches the fact that the default
case is hit at all (it should be reserved for genuinely
unexpected exceptions, not for missing classifier entries).

## Remediation

For each antipattern above:

1. Declare a typed error hierarchy in `app/errors.py` (or
   equivalent). Top-level distinction between DomainError
   and InfrastructureError; subclasses per failure mode.

2. Replace string-matching classifiers with type-based
   classifiers (instanceof, errors.As, sealed switch).

3. Refactor domain services to raise domain-typed exceptions
   (not HTTPException, not library-specific exceptions).

4. Refactor adapter layers to wrap library exceptions in
   application-typed InfrastructureError subclasses.

5. Add classifier tests for every documented exception class.
   The tests verify type-based dispatch and assert that
   message changes do not break classification.

6. Configure CI to fail when new exception classes are added
   without classifier entries (sealed types in Java with
   exhaustive switch produce compile-time failure; Python and
   JavaScript can enforce via test enumeration).
