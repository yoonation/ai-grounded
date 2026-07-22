<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.password-hashing password storage hashing (forbidden patterns)

This document provides anti-pattern examples for authentication.password-hashing. All code
examples in this file are substrate-original per the E1 examples
strategy. They illustrate patterns the substrate rule forbids; they
exist only as reference material for reviewers, AI agents performing
L2 review, and consumers learning the rule.

**Do not copy any code from this document into production.**

## Anti-pattern A: MD5 used as a password hash (Python)

```python
import hashlib

# FORBIDDEN: MD5 is cryptographically broken AND is a fast hash.
# Both properties make it unusable for password storage.
def hash_password_BAD(plaintext_password):
    return hashlib.md5(plaintext_password.encode("utf-8")).hexdigest()

# FORBIDDEN: even with a salt, MD5 is too fast.
# Modern GPUs compute billions of MD5 hashes per second.
def hash_password_with_salt_STILL_BAD(plaintext_password, salt):
    return hashlib.md5(
        (salt + plaintext_password).encode("utf-8")
    ).hexdigest()
```

Why this violates authentication.password-hashing:

- MD5 is on the forbidden-algorithms list
- MD5 is fundamentally a digest function designed for speed, not a
  password hash; salts do not change this property
- Cracking large MD5 password databases is routine for attackers

## Anti-pattern B: SHA-1 used as a password hash (Python)

```python
import hashlib

# FORBIDDEN: SHA-1 is cryptographically broken AND is a fast hash.
def hash_password_BAD(plaintext_password):
    return hashlib.sha1(plaintext_password.encode("utf-8")).hexdigest()

# FORBIDDEN: HMAC-SHA-1 over a "secret" is still not password hashing.
# HMAC is for message authentication, not password storage.
import hmac
def hmac_password_STILL_BAD(plaintext_password, secret):
    return hmac.new(
        secret.encode("utf-8"),
        plaintext_password.encode("utf-8"),
        hashlib.sha1,
    ).hexdigest()
```

Why this violates authentication.password-hashing:

- SHA-1 is on the forbidden-algorithms list
- SHA-1 is fundamentally a digest function designed for speed
- HMAC is a message authentication primitive, not a password hash;
  using it here misuses the construction

## Anti-pattern C: SHA-256 used as a password hash (Python)

```python
import hashlib

# FORBIDDEN: SHA-256 is not cryptographically broken, but it is a
# fast hash designed for digest purposes. It is not a password hash.
def hash_password_BAD(plaintext_password, salt):
    return hashlib.sha256(
        (salt + plaintext_password).encode("utf-8")
    ).hexdigest()

# FORBIDDEN: Many iterations of SHA-256 do not make it a password
# hash. Custom iteration schemes are unaudited; use PBKDF2-HMAC-SHA-256
# from a vetted library instead.
def naive_iterated_sha256_STILL_BAD(plaintext_password, salt):
    current = (salt + plaintext_password).encode("utf-8")
    for _ in range(100000):
        current = hashlib.sha256(current).digest()
    return current.hex()
```

Why this violates authentication.password-hashing:

- SHA-256 is on the forbidden-algorithms list for password storage
- Hand-rolled iteration is unaudited and likely flawed in salt
  handling, output mixing, or timing properties
- If PBKDF2-HMAC-SHA-256 is what is wanted, use the library's
  PBKDF2 with substrate-recommended iteration count, not a homegrown
  loop

## Anti-pattern D: Reversible encryption (Python)

```python
from cryptography.fernet import Fernet

# FORBIDDEN: encryption is reversible by design.
# A breach of the encryption key results in plaintext recovery
# of every password in the database.
def store_password_BAD(plaintext_password, encryption_key):
    cipher = Fernet(encryption_key)
    return cipher.encrypt(plaintext_password.encode("utf-8"))

def retrieve_password_BAD(stored_value, encryption_key):
    cipher = Fernet(encryption_key)
    # This recovers the plaintext password. The fact that this
    # function can exist is the violation.
    return cipher.decrypt(stored_value).decode("utf-8")
```

Why this violates authentication.password-hashing:

- Reversible encryption is on the forbidden list
- Password storage must be irreversible; the application should not
  be able to retrieve the user's plaintext password under any
  circumstance
- Breach of the encryption key compromises all stored passwords
  simultaneously

## Anti-pattern E: Plaintext storage (any language)

```python
# FORBIDDEN: plaintext storage. This is the most severe form of
# authentication.password-hashing violation. Listed here for completeness; no example
# code is provided because the violation is trivially obvious.
def store_password_BAD(plaintext_password):
    return plaintext_password  # noqa: PLAINTEXT_PASSWORD
```

Why this violates authentication.password-hashing:

- Plaintext storage is the canonical failure mode the rule prevents
- A database breach exposes every user's actual password
- Many users reuse passwords across services; plaintext breach
  cascades into compromise of unrelated accounts

## Anti-pattern F: Custom hashing scheme

```python
# FORBIDDEN: custom or homegrown hashing schemes. Even when the
# author understands the primitives, the construction is unaudited
# and almost certainly flawed (length-extension, salt reuse,
# constant-time leakage, missing version field).
def proprietary_hash_BAD(plaintext_password, salt):
    import hashlib
    h1 = hashlib.sha512(plaintext_password.encode()).digest()
    h2 = hashlib.sha512(salt.encode() + h1).digest()
    h3 = hashlib.sha512(h1 + h2).digest()
    return h3.hex()
```

Why this violates authentication.password-hashing:

- Custom schemes are not on the approved list
- Unaudited cryptographic constructions are unsafe by default
- Even if the construction were sound today, the lack of a version
  field and parameter encoding makes future migration impossible

## What anti-patterns have in common

The anti-patterns above share at least one of:

- Use of a fast general-purpose hash where a slow password hash is
  required
- Use of a broken algorithm (MD5, SHA-1)
- Reversibility (encryption, recoverable encoding)
- Plaintext (no transformation at all)
- Custom or unaudited construction

A consumer-side reviewer encountering any of these patterns treats
the code as an authentication.password-hashing violation regardless of test coverage or
peer review status.

## Cross-reference

- Substrate rule: authentication.password-hashing in catalogs/concerns/authentication.oscal.yaml
- Tool binding: binding.yaml
- Good examples: examples/authentication/password-hashing-good.md
