<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.no-credentials-in-logs credentials in logs (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Credentials in log message (Python)

```python
import logging
logger = logging.getLogger(__name__)

# FORBIDDEN: password in log message via f-string.
def login(username, password):
    logger.info(f"Login attempt: username={username} password={password}")

# FORBIDDEN: token in log message.
def call_api(token):
    logger.debug(f"Calling API with token {token}")

# FORBIDDEN: credentials in log via format() or %.
logger.info("User %s logged in with password %s", username, password)
logger.info("Authorization header: {}".format(auth_header))
```

Why this violates authentication.no-credentials-in-logs:
- Credential is the literal log message content
- Persisted to log files, shipped to aggregators, retained for weeks or months
- Visible to every operator with log read access

## Anti-pattern B: Console.log of credential (JavaScript / Node.js)

```javascript
// FORBIDDEN: token in console.log. Even in development this
// is dangerous because development output is sometimes
// captured by error tracking, screenshot tooling, or shared
// in support tickets.
async function fetchUser(token) {
  console.log("Token received:", token);
  return await fetch("/api/user", {
    headers: {Authorization: `Bearer ${token}`},
  });
}

// FORBIDDEN: logging entire request includes Authorization
// header and any body credentials.
app.use((req, res, next) => {
  console.log("Request:", req.method, req.url, req.headers, req.body);
  next();
});
```

Why this violates authentication.no-credentials-in-logs:
- Token directly logged
- "Just for debugging" comments do not protect logged credentials
- Catch-all request logging is a common silent violator

## Anti-pattern C: Print debugging in production code (Python)

```python
# FORBIDDEN: print() output is captured by stdout redirection
# in production environments. Container orchestrators ship
# stdout to log aggregators identically to logger output.
def verify_session(session_token):
    print(f"Verifying session: {session_token}")
    return session_store.lookup(session_token)
```

Why this violates authentication.no-credentials-in-logs:
- print() in production is logging by another name
- Container stdout is ingested by every modern log aggregator

## Anti-pattern D: Exception traceback containing request data (Python)

```python
import logging
logger = logging.getLogger(__name__)

# FORBIDDEN: exception handler that logs the full request
# context including credential headers and body.
@app.errorhandler(Exception)
def handle_error(e):
    logger.error(
        "Request failed",
        extra={
            "request_headers": dict(request.headers),
            "request_body": request.get_data(as_text=True),
            "exception": str(e),
        },
        exc_info=True,
    )
    return "Internal error", 500
```

Why this violates authentication.no-credentials-in-logs:
- request.headers includes Authorization
- request body may include passwords in login flow
- The well-meaning error-handler pattern silently leaks
  credentials on every error

## Anti-pattern E: Third-party library that logs its inputs

```python
# Suppose a third-party HTTP client library logs requests at
# DEBUG level. If logging level is set to DEBUG in production,
# the library leaks credentials passed to it.
import third_party_client
import logging
logging.basicConfig(level=logging.DEBUG)  # FORBIDDEN in prod

client = third_party_client.Client(api_key=secret_api_key)
client.request("POST", "/data", json={"value": 1})
# Library logs: "Request: POST /data, headers={'X-API-Key': 'sk_live_xxx'}"
```

Why this violates authentication.no-credentials-in-logs:
- Production logging level should not be DEBUG
- Production credential transport should not pass through
  libraries that log unredacted headers
- The violation is not in code we wrote but in code we
  configured

## What anti-patterns have in common

- Credential variable as an argument to a log-emitting call
- Whole-object dumping (request, headers, body) that includes
  credentials by inclusion
- DEBUG-level logging in production
- Exception handlers that capture request context

## Cross-reference

- Substrate rule: authentication.no-credentials-in-logs in catalogs/concerns/authentication.oscal.yaml
- Tool binding: checklist.md
- Good examples: examples/authentication/credentials-in-logs-good.md
