<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.no-secrets-in-logs no secrets in logs (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.no-secrets-in-logs.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: Logging request body (Python)

```python
# DO NOT DO THIS
@app.post("/login")
async def login(request):
    body = await request.json()
    logger.info("Login attempt", body=body)
    # body contains {"username": "alice", "password": "hunter2"}
```

Why this violates secrets-management.no-secrets-in-logs: the request body is
logged verbatim. Any credential field passes through to
the log destination. Semgrep's
`python.lang.security.audit.logging-sensitive-data`
catches the pattern; producer-side redaction prevents the
disclosure.

## Anti-pattern B: Logging full Authorization header (Node.js)

```javascript
// DO NOT DO THIS
app.use((req, res, next) => {
  logger.info("Request received", {
    method: req.method,
    path: req.path,
    headers: req.headers,  // includes Authorization
  });
  next();
});
```

Why this violates secrets-management.no-secrets-in-logs: the headers object
includes Authorization, Cookie, and X-API-Key. Logging
the full headers object disclosures every secret in
transit. Substrate-recommended pattern: log allow-listed
headers only, or apply redaction.

## Anti-pattern C: Whole-object dump of credential holder (Java)

```java
// DO NOT DO THIS
DatabaseConfig config = new DatabaseConfig(url, user, password);
logger.info("Initialized database config: " + config);
// config.toString() includes the password field
```

Why this violates secrets-management.no-secrets-in-logs: the default `toString()`
in many language idioms dumps every field including
secrets. Substrate-recommended pattern: implement
`toString()` explicitly to redact sensitive fields, or
use a SecretString wrapper.

## Anti-pattern D: Exception with secret in message (Python)

```python
# DO NOT DO THIS
try:
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
except requests.HTTPError:
    raise RuntimeError(f"API call failed with token {token}")
```

Why this violates secrets-management.no-secrets-in-logs: the exception message
embeds the token. Stack trace logging and error monitoring
will capture the message. The exception's caller may also
log the message at a higher level.

## Anti-pattern E: Stack trace with local variables to client (Flask)

```python
# DO NOT DO THIS - production with DEBUG enabled
app = Flask(__name__)
app.config["DEBUG"] = True

# Any unhandled exception returns Werkzeug debugger page
# showing local variables, including credentials.
```

Why this violates secrets-management.no-secrets-in-logs: Werkzeug's debug page
exposes local variables in stack frames. When an
exception happens in code that has loaded a secret, the
secret value is rendered to the response.
Semgrep's `python.flask.debug.flask-debug-true` catches
this; production deployments must have DEBUG=False.

## Anti-pattern F: Logging SQL query parameters (raw)

```python
# DO NOT DO THIS
def find_user(email, password_hash):
    query = "SELECT * FROM users WHERE email = '%s' AND pw_hash = '%s'" % (email, password_hash)
    logger.debug("Executing query: " + query)
    return db.execute(query)
```

Why this violates secrets-management.no-secrets-in-logs: the query string
contains the password hash (sensitive material).
Additionally, the string-interpolation pattern is SQL
injection vulnerable. Substrate-recommended: log the
parameterized query template (without values), or log
the operation type and table without parameters.

## Anti-pattern G: Sentry without redaction (Node.js)

```javascript
// DO NOT DO THIS - Sentry SDK with default settings
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  // no beforeSend, no scrubbing configuration
});

// Sentry captures request headers (Authorization), request
// body (credentials), and local variables (secrets).
```

Why this violates secrets-management.no-secrets-in-logs: error monitoring SDKs
capture rich context by default. Without a beforeSend
hook or server-side scrubbing rules, secrets transit to
the monitoring backend. Substrate-recommended: configure
producer-side scrubbing as the primary control.

## Anti-pattern H: Audit log includes secret value (Go)

```go
// DO NOT DO THIS
func RotateCredential(name string, newValue string) error {
    auditLog.Printf("Rotated credential %s to value %s",
                    name, newValue)
    return secretStore.Update(name, newValue)
}
```

Why this violates secrets-management.no-secrets-in-logs: audit logs should
record that a rotation happened, not the new value.
Substrate-recommended: log the credential identifier,
who initiated the rotation, and the timestamp. The new
value is in the secrets platform; the audit log records
the action.

## Cross-reference

- Good patterns: examples/secrets-management/no-secrets-in-logs-good.md
- Substrate rule: secrets-management.no-secrets-in-logs
- Static analysis binding: checklist.md
