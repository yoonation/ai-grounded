<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.password-hashing password storage hashing (good patterns)

This document provides good-pattern examples for authentication.password-hashing. All code
examples in this file are substrate-original per the E1 examples
strategy. They are intended as illustrative reference; consumer code
should be adapted to consumer's stack conventions, library versions,
and parameter tuning needs.

Per spec/substrate-scope.md Rule 2, the substrate does not implement
authentication. These examples demonstrate calling patterns for
established password hashing libraries. The substrate does not ship
any of the libraries used.

## Pattern A: Argon2id via argon2-cffi (Python)

Argon2id is the substrate-recommended default for new applications.

```python
from argon2 import PasswordHasher

# Hasher configured with substrate-recommended minimums.
# Production deployments tune these so a single hash takes
# 250-500 ms on production hardware.
hasher = PasswordHasher(
    memory_cost=19456,   # 19 MiB minimum
    time_cost=2,         # 2 iterations minimum
    parallelism=1,       # 1 parallelism minimum
)

# Hashing on registration or password change. The library
# generates a unique salt per call. The output includes the
# algorithm, parameters, salt, and hash in PHC string format
# suitable for direct database storage.
stored_hash = hasher.hash(plaintext_password)

# Verification on login. The library extracts parameters and
# salt from the stored hash; the call returns None or raises
# on mismatch.
try:
    hasher.verify(stored_hash, presented_password)
    authenticated = True
except Exception:
    authenticated = False
```

Why this satisfies authentication.password-hashing:

- Argon2id is on the approved-algorithms list
- The library generates a unique salt per hash automatically
- Parameters meet substrate-recommended minimums
- The hash format includes algorithm identifier, supporting future
  parameter migration

## Pattern B: bcrypt via bcrypt library (Python)

bcrypt is acceptable for existing applications and legacy environments.

```python
import bcrypt

# Cost factor 12 meets substrate-recommended minimum on modern
# hardware. Re-evaluate annually; raise as hardware improves.
cost_factor = 12

# Hashing on registration or password change. The library
# generates a unique salt per call.
stored_hash = bcrypt.hashpw(
    plaintext_password.encode("utf-8"),
    bcrypt.gensalt(rounds=cost_factor),
)

# Verification on login.
authenticated = bcrypt.checkpw(
    presented_password.encode("utf-8"),
    stored_hash,
)
```

Why this satisfies authentication.password-hashing:

- bcrypt is on the approved-algorithms list
- Cost factor meets substrate-recommended minimum
- Salt is generated automatically by the library

Caveat: bcrypt truncates inputs at 72 bytes. If your application
allows passwords longer than 72 characters and that length matters,
prefer Argon2id.

## Pattern C: bcrypt via bcrypt library (JavaScript/Node.js)

```javascript
const bcrypt = require("bcrypt");

// Cost factor 12 meets substrate-recommended minimum.
const saltRounds = 12;

// Hashing on registration or password change.
// The library generates a unique salt per call.
async function hashPassword(plaintextPassword) {
  return await bcrypt.hash(plaintextPassword, saltRounds);
}

// Verification on login.
async function verifyPassword(presentedPassword, storedHash) {
  return await bcrypt.compare(presentedPassword, storedHash);
}
```

Why this satisfies authentication.password-hashing:

- bcrypt is on the approved-algorithms list
- Cost factor meets substrate-recommended minimum
- Salt is generated automatically by the library

## Pattern D: BCrypt via Spring Security (Java)

```java
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

// Spring Security's BCryptPasswordEncoder with substrate-
// recommended minimum cost factor.
BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

// Hashing on registration or password change.
// The library generates a unique salt per call.
String storedHash = encoder.encode(plaintextPassword);

// Verification on login.
boolean authenticated = encoder.matches(
    presentedPassword,
    storedHash
);
```

Why this satisfies authentication.password-hashing:

- bcrypt is on the approved-algorithms list
- Cost factor meets substrate-recommended minimum
- Spring Security generates a unique salt per encode call

## Pattern E: bcrypt via golang.org/x/crypto/bcrypt (Go)

```go
package main

import (
    "golang.org/x/crypto/bcrypt"
)

// Cost factor 12 meets substrate-recommended minimum.
const passwordCost = 12

// Hashing on registration or password change.
// The library generates a unique salt per call.
func hashPassword(plaintext string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword(
        []byte(plaintext),
        passwordCost,
    )
    return string(bytes), err
}

// Verification on login.
func verifyPassword(presented string, storedHash string) bool {
    err := bcrypt.CompareHashAndPassword(
        []byte(storedHash),
        []byte(presented),
    )
    return err == nil
}
```

Why this satisfies authentication.password-hashing:

- bcrypt is on the approved-algorithms list
- Cost factor meets substrate-recommended minimum
- Salt is generated automatically by the library

## What good examples have in common

Each example above:

- Uses an algorithm from the authentication.password-hashing approved list
- Delegates salt generation to the hashing library
- Stores the hash in a self-describing format that includes
  algorithm and parameters (PHC for Argon2id; bcrypt's prefix
  format)
- Uses a constant-time comparison via the library's verify or match
  function rather than string equality

These properties together mean the application can:

- Survive a database breach without immediately compromising
  passwords
- Migrate to stronger parameters or algorithms over time without
  needing the original plaintexts (rehash on next login)
- Resist timing attacks on the verification path

## Cross-reference

- Substrate rule: authentication.password-hashing in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Anti-examples: examples/authentication/password-hashing-weak-algorithm.md
- External reference: OWASP Password Storage Cheat Sheet (linked from
  the catalog rule)
