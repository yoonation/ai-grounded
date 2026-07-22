<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.token-expiration token expiration (good patterns)

Substrate-original good-pattern examples for authentication.token-expiration.

## Pattern A: JWT with explicit exp claim (Python / PyJWT)

```python
import jwt
from datetime import datetime, timezone, timedelta

# Issue an access token that expires 15 minutes from now.
def issue_access_token(user_id):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, signing_key, algorithm="HS256")

# Verification rejects expired tokens. PyJWT does this by
# default when exp is present.
def verify_access_token(token):
    try:
        return jwt.decode(token, signing_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
```

Why this satisfies authentication.token-expiration:
- exp claim explicitly set at issuance
- Window is short (15 minutes) for access tokens
- Verification path enforces expiration

## Pattern B: JWT access + refresh token pair (Node.js / jsonwebtoken)

```javascript
const jwt = require("jsonwebtoken");

function issueTokenPair(userId) {
  // Short-lived access token; presented on every API request.
  const accessToken = jwt.sign(
    {sub: userId, type: "access"},
    accessSecret,
    {expiresIn: "15m"}  // explicit expiration
  );

  // Longer-lived refresh token; used only to obtain new
  // access tokens. Also has explicit expiration; the
  // application revokes the refresh token if compromised.
  const refreshToken = jwt.sign(
    {sub: userId, type: "refresh", jti: randomId()},
    refreshSecret,
    {expiresIn: "7d"}  // explicit expiration
  );

  return {accessToken, refreshToken};
}
```

Why this satisfies authentication.token-expiration:
- Both tokens carry explicit expiration
- Two-token pattern bounds access token exposure while
  preserving user convenience
- jti claim allows refresh-token revocation if compromised

## Pattern C: Database-backed reset token with expiration timestamp

```python
import secrets
from datetime import datetime, timezone, timedelta

def create_password_reset_token(user_id):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.execute(
        "INSERT INTO password_reset_tokens (token_hash, user_id, expires_at) "
        "VALUES (%s, %s, %s)",
        (hash_token(token), user_id, expires_at),
    )
    return token

# Verification path rejects expired or already-used tokens.
def consume_password_reset_token(token):
    now = datetime.now(timezone.utc)
    row = db.execute(
        "DELETE FROM password_reset_tokens "
        "WHERE token_hash = %s AND expires_at > %s AND used = FALSE "
        "RETURNING user_id",
        (hash_token(token), now),
    ).fetchone()
    return row["user_id"] if row else None
```

Why this satisfies authentication.token-expiration:
- expires_at column populated at issuance
- Verification path checks expiration
- Single-use enforcement via DELETE on consumption

## Pattern D: Express session with cookie timeout

```javascript
const session = require("express-session");

app.use(session({
  secret: process.env.SESSION_SECRET,
  cookie: {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 8 * 60 * 60 * 1000,  // 8 hours, explicit
  },
  rolling: false,  // do not refresh on every request
}));
```

Why this satisfies authentication.token-expiration:
- maxAge sets explicit cookie expiration
- httpOnly and secure provide defense in depth
- rolling: false means the 8-hour limit is absolute, not
  reset on activity (substrate-recommended for high-risk
  sessions; consumer adjusts per risk profile)

## What good patterns have in common

- Expiration set at the time of token issuance
- Expiration value chosen to match the token's risk profile
  (short for access tokens; longer for refresh tokens;
  bounded for everything)
- Verification path actually enforces expiration

## Cross-reference

- Substrate rule: authentication.token-expiration in catalogs/concerns/authentication.oscal.yaml
- Tool binding: checklist.md
- Anti-patterns: examples/authentication/token-expiration-anti-pattern.md
