<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.rate-limiting rate limiting (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: No rate limiting on login (Python / Flask)

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# FORBIDDEN: login endpoint with no rate limiting at all.
# Attacker can submit unlimited credential pairs.
@app.route("/login", methods=["POST"])
def login_BAD():
    body = request.get_json()
    user = authenticate(body["username"], body["password"])
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({"session": issue_session(user)})
```

Why this violates authentication.rate-limiting:
- No coverage at all on the most critical authentication endpoint
- Credential stuffing and brute force trivially succeed
- This is the most common authentication.rate-limiting failure

## Anti-pattern B: Per-IP only, no per-account limit (Node.js)

```javascript
const rateLimit = require("express-rate-limit");

// FORBIDDEN: per-IP limit but no per-account limit.
// Attacker with a botnet (many IPs) can target a single account
// without ever triggering the per-IP threshold.
app.post("/login", rateLimit({windowMs: 15 * 60 * 1000, max: 10}), async (req, res) => {
  const user = await authenticate(req.body.username, req.body.password);
  return user ? res.json({session: issueSession(user)}) : res.status(401).json({error: "Invalid"});
});
```

Why this violates authentication.rate-limiting:
- Missing the per-account granularity
- Distributed credential stuffing succeeds because each IP makes
  one attempt and never trips the limit, but each TARGET account
  receives unlimited attempts from different IPs

## Anti-pattern C: In-process memory rate limiting

```python
# FORBIDDEN: rate-limit counter is in-process memory.
# When the application runs as 4 replicas behind a load balancer,
# each replica has its own counter. The effective rate limit is
# 4 times what was configured.
attempts_by_ip = {}

@app.route("/login", methods=["POST"])
def login_BAD():
    ip = request.remote_addr
    attempts_by_ip[ip] = attempts_by_ip.get(ip, 0) + 1
    if attempts_by_ip[ip] > 10:
        return jsonify({"error": "Too many requests"}), 429
    return process_login()
```

Why this violates authentication.rate-limiting:
- In-process counter not shared across replicas
- The advertised limit is divided among replicas; configured 10
  per IP becomes 40 per IP across 4 replicas
- Also: the dictionary grows unbounded; memory leak

## Anti-pattern D: Login rate-limited but password reset is not

```javascript
const loginLimiter = rateLimit({windowMs: 15 * 60 * 1000, max: 10});

app.post("/login", loginLimiter, handleLogin);

// FORBIDDEN: password reset endpoint not rate limited.
// Attackers use password reset for email enumeration:
// submit candidate emails and observe which return
// success-shaped responses (per authentication.generic-failure-responses these should
// be identical, but the rate-limit gap is independently bad
// because it allows mass email enumeration if authentication.generic-failure-responses
// is also weak).
app.post("/password-reset", handlePasswordReset);
```

Why this violates authentication.rate-limiting:
- Coverage gap on a real auth endpoint
- Common oversight; password reset is one of the most
  forgotten rate-limit targets

## Anti-pattern E: Rate-limit response leaks authentication outcome

```python
# FORBIDDEN: rate-limit check happens AFTER authentication.
# The response shape tells the attacker which credentials
# were correct just-before-being-rate-limited.
def login_BAD(username, password):
    user = authenticate(username, password)
    if user is None:
        return generic_auth_failure()

    if check_rate_limit_exceeded(username):
        # FORBIDDEN: this branch is reached only when the
        # credentials were CORRECT. Attacker who triggers
        # rate limit and sees this response confirms the
        # password is valid even though they couldn't log in.
        return jsonify({"error": "Too many requests; try again later"}), 429

    return issue_session(user)
```

Why this violates authentication.rate-limiting:
- Rate-limit response varies with authentication outcome
- Attacker uses the rate-limit response as an authentication
  oracle
- The rate-limit check must happen BEFORE the authentication
  check, or the responses must be identical

## Anti-pattern F: Permissive bypass via untrusted header

```python
# FORBIDDEN: rate-limit bypass triggered by X-Forwarded-For
# header. The application is not behind a verified proxy so
# the header can be set by the client.
def get_source_ip(request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr

# Attacker submits X-Forwarded-For: 1.1.1.1, then 1.1.1.2, etc.,
# defeating the per-IP rate limit one fake IP at a time.
```

Why this violates authentication.rate-limiting:
- Rate-limit identifier derived from client-controlled header
- Bypass surface is the entire rate-limit defense
- The right pattern: trust X-Forwarded-For only when a verified
  proxy sets it (and only the verified proxy's overlay segment
  is trusted), and use the connection's real IP otherwise

## Anti-pattern G: Permanent lockout (denial of service)

```python
# FORBIDDEN: lockout is permanent and requires admin unlock.
# Attacker submits 5 failed logins per user account and locks
# every user out. Denial of service against the user
# population.
def login_BAD(username, password):
    if account_status.is_locked(username):
        return jsonify({"error": "Account locked"}), 401

    user = authenticate(username, password)
    if user is None:
        failures = account_status.incr_failures(username)
        if failures >= 5:
            account_status.lock_permanently(username)
        return generic_auth_failure()

    return issue_session(user)
```

Why this violates authentication.rate-limiting:
- Lockout has no expiration; attacker can lock arbitrary
  accounts indefinitely
- Lockout response distinguishes locked from invalid credentials
  (leaks state via response)
- The right pattern: time-bounded lockout (15-30 minutes) with
  generic response

## What anti-patterns have in common

- Missing rate limiting on one or more auth endpoints
- Single-granularity limits (per-IP only or per-account only)
- In-process state with multi-replica deployment
- Rate-limit decision after authentication
- Bypass surfaces (untrusted headers, blanket exemptions)
- Permanent lockout enabling denial of service

## Cross-reference

- Substrate rule: authentication.rate-limiting in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Good examples: examples/authentication/rate-limiting-good.md
