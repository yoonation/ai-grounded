<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.timing-safe-comparison timing-safe comparison (good patterns)

Substrate-original good-pattern examples for authentication.timing-safe-comparison.

## Pattern A: hmac.compare_digest (Python)

```python
import hmac

# Compare API key in constant time. compare_digest is in the
# Python standard library hmac module.
def verify_api_key(presented, stored):
    if len(presented) != len(stored):
        return False
    return hmac.compare_digest(presented, stored)

# HMAC signature verification for webhook payloads.
import hashlib

def verify_webhook_signature(payload, presented_signature, secret):
    expected = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, presented_signature)
```

Why this satisfies authentication.timing-safe-comparison:
- compare_digest performs constant-time comparison
- Length is checked first because compare_digest requires
  equal length on some Python versions
- HMAC verification uses the same function

## Pattern B: crypto.timingSafeEqual (Node.js)

```javascript
const crypto = require("crypto");

// Convert both inputs to Buffers of equal length, then compare.
function verifyApiKey(presented, stored) {
  const a = Buffer.from(presented, "utf8");
  const b = Buffer.from(stored, "utf8");
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

// HMAC webhook signature verification (Stripe-style).
function verifyStripeSignature(payload, header, secret) {
  const expected = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest("hex");

  // Parse the presented signature out of the header
  // (header format: "t=...,v1=signature").
  const presented = parseStripeSignatureHeader(header).v1;

  const expectedBuf = Buffer.from(expected, "utf8");
  const presentedBuf = Buffer.from(presented, "utf8");
  if (expectedBuf.length !== presentedBuf.length) return false;
  return crypto.timingSafeEqual(expectedBuf, presentedBuf);
}
```

Why this satisfies authentication.timing-safe-comparison:
- timingSafeEqual is in the Node crypto module
- Both operands converted to Buffer at the same length
- Length-mismatch is rejected before constant-time compare

## Pattern C: MessageDigest.isEqual (Java)

```java
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

public boolean verifyApiKey(String presented, String stored) {
    byte[] a = presented.getBytes(StandardCharsets.UTF_8);
    byte[] b = stored.getBytes(StandardCharsets.UTF_8);
    return MessageDigest.isEqual(a, b);
}
```

Why this satisfies authentication.timing-safe-comparison:
- MessageDigest.isEqual is in the Java standard library
- Implementation is constant-time per Java documentation
- Comparison works on byte arrays of arbitrary length

## Pattern D: subtle.ConstantTimeCompare (Go)

```go
package main

import (
    "crypto/subtle"
)

// Returns 1 if equal, 0 otherwise. The int return type
// discourages callers from short-circuiting on the result.
func VerifyAPIKey(presented, stored []byte) bool {
    return subtle.ConstantTimeCompare(presented, stored) == 1
}

// HMAC signature verification.
import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/hex"
)

func VerifyWebhookSignature(payload, presented, secret string) bool {
    mac := hmac.New(sha256.New, []byte(secret))
    mac.Write([]byte(payload))
    expected := hex.EncodeToString(mac.Sum(nil))
    return subtle.ConstantTimeCompare(
        []byte(expected),
        []byte(presented),
    ) == 1
}
```

Why this satisfies authentication.timing-safe-comparison:
- ConstantTimeCompare is the Go standard library function
- Result is int, not bool, to discourage non-constant-time
  callers from short-circuiting

## Pattern E: CryptographicOperations.FixedTimeEquals (.NET)

```csharp
using System.Security.Cryptography;
using System.Text;

public bool VerifyApiKey(string presented, string stored)
{
    var a = Encoding.UTF8.GetBytes(presented);
    var b = Encoding.UTF8.GetBytes(stored);
    return CryptographicOperations.FixedTimeEquals(a, b);
}
```

Why this satisfies authentication.timing-safe-comparison:
- FixedTimeEquals is the .NET constant-time comparison API
- Handles length-mismatch internally without leaking length
  via timing

## What good patterns have in common

- Each language has a standard-library constant-time function
- Use it for any comparison whose timing could leak credential
  information
- Convert inputs to the function's required form (bytes,
  Buffer, byte array)
- Length comparison is performed before the constant-time call
  or handled by the function itself

## Cross-reference

- Substrate rule: authentication.timing-safe-comparison in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Anti-patterns: examples/authentication/timing-safe-comparison-anti-pattern.md
