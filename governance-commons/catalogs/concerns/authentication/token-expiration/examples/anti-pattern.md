<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.token-expiration token expiration (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: JWT without exp claim (Python)

```python
import jwt

# FORBIDDEN: no exp claim. Token authenticates forever.
def issue_access_token_BAD(user_id):
    payload = {"sub": str(user_id), "type": "access"}
    return jwt.encode(payload, signing_key, algorithm="HS256")
```

Why this violates authentication.token-expiration:
- No expiration claim means token is valid indefinitely
- A leaked token cannot be aged out; only explicit revocation
  invalidates it
- Most JWT libraries treat the absence of exp as "never expires"

## Anti-pattern B: JWT with very long expiration (JavaScript)

```javascript
const jwt = require("jsonwebtoken");

// FORBIDDEN: 10-year expiration on an access token. Technically
// the token has expiration, but the value is so long it
// defeats the purpose.
const accessToken = jwt.sign(
  {sub: userId, type: "access"},
  secret,
  {expiresIn: "10y"}
);

// FORBIDDEN: number-of-seconds form that mistakenly expresses
// a long duration. 31536000 seconds = 1 year. Common bug:
// developer intended 31536 (about 9 hours).
const tokenSecondsBug = jwt.sign(payload, secret, {expiresIn: 31536000});
```

Why this violates authentication.token-expiration:
- The rule's intent is to bound credential exposure window
- 10-year expiration provides effectively no bound
- The number-of-seconds bug pattern is a known footgun;
  prefer the string-duration form ("15m", "8h", "7d")

## Anti-pattern C: Reset token stored without expiration column

```python
import secrets

# FORBIDDEN: no expires_at column; tokens never age out.
def create_password_reset_token_BAD(user_id):
    token = secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO password_reset_tokens (token_hash, user_id) "
        "VALUES (%s, %s)",
        (hash_token(token), user_id),
    )
    return token

# Verification only checks presence, not freshness.
def consume_password_reset_token_BAD(token):
    row = db.execute(
        "DELETE FROM password_reset_tokens WHERE token_hash = %s "
        "RETURNING user_id",
        (hash_token(token),),
    ).fetchone()
    return row["user_id"] if row else None
```

Why this violates authentication.token-expiration:
- Reset tokens are bearer credentials
- Without expiration, a leaked reset email from years ago is
  still exploitable
- The verification path has no opportunity to reject stale
  tokens

## Anti-pattern D: Session config without timeout

```javascript
const session = require("express-session");

// FORBIDDEN: no maxAge set. Cookie is a session cookie that
// expires only when the browser closes. In long-running
// browser sessions (laptop never closed, browser process
// persists across reboots) this is effectively no expiration.
app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    httpOnly: true,
    secure: true,
    // maxAge omitted
  },
}));
```

Why this violates authentication.token-expiration:
- Browser-session-only cookies are not equivalent to
  explicit expiration
- Server-side session entry without TTL also persists
  indefinitely

## Anti-pattern E: Expiration set but not enforced at verification

```python
import jwt

# The issuance side LOOKS correct: exp is set.
def issue_token(user_id):
    return jwt.encode(
        {"sub": str(user_id), "exp": some_future_timestamp},
        secret,
        algorithm="HS256",
    )

# FORBIDDEN: verification with options that disable exp
# enforcement.
def verify_token_BAD(token):
    return jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        options={"verify_exp": False},  # ← disables expiration check
    )
```

Why this violates authentication.token-expiration:
- The rule applies to the effective behavior, not the issuance
  call alone
- A token with exp that the verifier ignores is equivalent to
  a token without exp

## What anti-patterns have in common

- Issuance without expiration, or expiration so long it
  provides no bound
- Verification that does not enforce expiration
- Session and token configurations that rely on implicit
  expiration (browser close, manual logout) rather than
  explicit time bounds

## Cross-reference

- Substrate rule: authentication.token-expiration in catalogs/concerns/authentication.oscal.yaml
- Tool binding: checklist.md
- Good examples: examples/authentication/token-expiration-good.md
