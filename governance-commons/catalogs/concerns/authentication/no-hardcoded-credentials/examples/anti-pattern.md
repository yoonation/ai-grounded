<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.no-hardcoded-credentials credentials hardcoded (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Hardcoded API key (Python)

```python
# FORBIDDEN: API key as string literal in source.
STRIPE_API_KEY = "sk_live_<redacted-example-key>"

# FORBIDDEN: same anti-pattern with different naming.
def call_payment_api():
    api_key = "sk_live_<redacted-example-key>"
    return requests.post(..., headers={"Authorization": f"Bearer {api_key}"})
```

Why this violates authentication.no-hardcoded-credentials:
- Real Stripe live key in source
- Disclosed to every developer with repository read access
- Recovery requires rotating the key at Stripe and auditing
  charges during the exposure window

## Anti-pattern B: Hardcoded JWT signing secret (Node.js)

```javascript
const jwt = require("jsonwebtoken");

// FORBIDDEN: JWT signing secret in source.
const JWT_SECRET = "super-secret-jwt-key-do-not-share";

function issueToken(userId) {
  return jwt.sign({sub: userId}, JWT_SECRET, {expiresIn: "1h"});
}
```

Why this violates authentication.no-hardcoded-credentials:
- Anyone with source access can sign valid tokens for any
  user, completely bypassing authentication
- Public repositories with this anti-pattern are routinely
  found by automated scanners

## Anti-pattern C: Database connection string with password (Java)

```java
// FORBIDDEN: connection string with password in source.
String DB_URL = "jdbc:postgresql://prod-db.example.com:5432/myapp?user=admin&password=hunter2";

Connection conn = DriverManager.getConnection(DB_URL);
```

Why this violates authentication.no-hardcoded-credentials:
- Database admin password exposed
- Production hostname also exposed (reconnaissance value)
- The right pattern uses externalized configuration (see
  good-pattern E)

## Anti-pattern D: Hardcoded private key (Python)

```python
# FORBIDDEN: private key embedded in source. The triple-quoted
# string syntax does not change the fact that this is a real
# private key in version control.
RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxxx...
[remaining key body redacted from this anti-example]
-----END RSA PRIVATE KEY-----"""
```

Why this violates authentication.no-hardcoded-credentials:
- Private key in source
- The substrate's good pattern: load from
  /etc/myapp/private-key.pem at runtime, where the file is
  managed by the deployment system

## Anti-pattern E: "Encrypted" credentials with hardcoded decryption key

```python
import base64
from cryptography.fernet import Fernet

# FORBIDDEN: encryption key and ciphertext both in source.
# The "encryption" is decorative; anyone reading the source
# can decrypt.
_KEY = b"oh4OQ7Cm0YuRMyT5G0ITT7C9Vk5gWoMCZ-fjNVxN0Ic="
_CIPHERTEXT = b"gAAAAABx..."

def get_api_key():
    return Fernet(_KEY).decrypt(_CIPHERTEXT).decode()
```

Why this violates authentication.no-hardcoded-credentials:
- The decryption key is in source, so the encryption is
  obfuscation, not protection
- Externalizing the encryption key (or moving to a secrets
  manager) is the correct pattern

## Anti-pattern F: Hardcoded credentials in test files used in production

```python
# In tests/conftest.py:
TEST_USER_PASSWORD = "test123"

# FORBIDDEN: same credential reused in production code path
# because "it's just for the demo".
def create_demo_account():
    return create_user(email="demo@example.com", password=TEST_USER_PASSWORD)
```

Why this violates authentication.no-hardcoded-credentials:
- A "test" credential used by production code becomes a
  production credential
- Test fixtures should be scoped to test contexts only
- "Demo accounts" need real credentials managed like any
  other production credential

## What anti-patterns have in common

- Credential value appears as a string literal in source
- The "encryption" or "obfuscation" still has its key in
  source
- Test-only credentials used by production-reachable code paths

## Cross-reference

- Substrate rule: authentication.no-hardcoded-credentials in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Good examples: examples/authentication/credentials-hardcoded-good.md
- Related: authentication.no-credential-files-in-repo (credential-bearing files committed to repos)
