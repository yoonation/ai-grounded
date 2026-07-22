<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.timing-safe-comparison timing-safe comparison (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: == on tokens (Python)

```python
# FORBIDDEN: Python == on credentials short-circuits at the
# first differing byte. Timing leaks the correct prefix length.
def verify_api_key_BAD(presented, stored):
    return presented == stored

# FORBIDDEN: same issue, in if statement.
def verify_token_BAD(presented_token, expected_token):
    if presented_token == expected_token:
        return True
    return False
```

Why this violates authentication.timing-safe-comparison:
- == short-circuits on first byte difference
- Attacker submits candidate tokens and measures response time
- Network noise can be filtered statistically with many samples

## Anti-pattern B: === or != on tokens (JavaScript)

```javascript
// FORBIDDEN: JavaScript === on credentials.
function verifyApiKey_BAD(presented, stored) {
  return presented === stored;
}

// FORBIDDEN: same timing leak with !=.
function authenticateRequest_BAD(req) {
  if (req.headers["x-api-key"] !== expectedKey) {
    return 401;
  }
  return 200;
}
```

Why this violates authentication.timing-safe-comparison:
- === and !== are not constant-time
- The string comparison underlying === short-circuits identically

## Anti-pattern C: String.equals on credentials (Java)

```java
// FORBIDDEN: String.equals is not constant-time. Returns
// early when bytes differ.
public boolean verifyApiKey_BAD(String presented, String stored) {
    return presented.equals(stored);
}

// FORBIDDEN: Arrays.equals on byte arrays also not constant-time.
import java.util.Arrays;
public boolean verifyHmac_BAD(byte[] presented, byte[] expected) {
    return Arrays.equals(presented, expected);
}
```

Why this violates authentication.timing-safe-comparison:
- String.equals and Arrays.equals short-circuit
- The constant-time replacement is MessageDigest.isEqual

## Anti-pattern D: bytes.Equal on credentials (Go)

```go
package main

import "bytes"

// FORBIDDEN: bytes.Equal short-circuits. Not constant-time.
func VerifyAPIKey_BAD(presented, stored []byte) bool {
    return bytes.Equal(presented, stored)
}

// FORBIDDEN: string comparison via == similarly leaks.
func VerifyToken_BAD(presented, stored string) bool {
    return presented == stored
}
```

Why this violates authentication.timing-safe-comparison:
- bytes.Equal optimizes for speed via short-circuit, exactly
  what we don't want for credentials
- subtle.ConstantTimeCompare is the constant-time replacement

## Anti-pattern E: Length comparison leaks length

```python
# FORBIDDEN: even using compare_digest, allowing a fast
# length-mismatch path leaks the correct length.
def verify_api_key_BAD(presented, stored):
    if len(presented) != len(stored):
        return False  # Returns very quickly, leaking length
    return hmac.compare_digest(presented, stored)
```

Why this is subtly wrong: short-circuiting on length is a
known anti-pattern when the credential length is itself
sensitive. For variable-length tokens, the attacker learns
the correct length without learning content. The substrate's
good-pattern examples accept this trade-off for API keys
because API key length is fixed and length disclosure is not
useful. For variable-length secrets, alternate constructions
are needed (hash both sides to fixed length first).

This is a partial violation, listed for completeness. The
common case (fixed-length API keys, JWT tokens) is fine with
the good-pattern shape; the warning matters when token length
is itself secret.

## What anti-patterns have in common

- Language equality operators (==, ===, .equals, bytes.Equal)
  on credential values
- Short-circuiting comparisons of any form on secret material
- Length comparisons that themselves leak information when
  length is sensitive

## Cross-reference

- Substrate rule: authentication.timing-safe-comparison in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Good examples: examples/authentication/timing-safe-comparison-good.md
