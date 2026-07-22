<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.password-policy password policy (good patterns)

## Pattern A: NIST-compliant policy with Pwned Passwords API (Python)

```python
import hashlib
import httpx

MIN_LENGTH = 12
MAX_LENGTH = 64
PWNED_API = "https://api.pwnedpasswords.com/range/"

class PasswordValidationError(Exception):
    def __init__(self, reason):
        self.reason = reason


def validate_password(password):
    if len(password) < MIN_LENGTH:
        raise PasswordValidationError(
            f"Password must be at least {MIN_LENGTH} characters"
        )
    if len(password) > MAX_LENGTH:
        raise PasswordValidationError(
            f"Password must be at most {MAX_LENGTH} characters"
        )
    if _is_breached(password):
        raise PasswordValidationError(
            "This password appears in a known breach corpus and cannot be used"
        )


def _is_breached(password):
    """Query Pwned Passwords using k-anonymity (5-char SHA-1 prefix)."""
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    response = httpx.get(f"{PWNED_API}{prefix}", timeout=5.0)
    if response.status_code != 200:
        # If breach service is unavailable, fail closed in
        # high-risk environments; fail open in low-risk with
        # alert. Choose deliberately.
        return False

    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return True
    return False
```

Why this satisfies authentication.password-policy:
- Length minimum 12, maximum 64
- No composition rules
- Breach corpus screening via k-anonymity (only 5-char prefix
  sent to third party; full password and hash never transmitted)
- Shared validation function used by signup and password change

## Pattern B: Local Pwned Passwords list with bloom filter (Node.js)

```javascript
const fs = require("fs");
const crypto = require("crypto");
const ScalableBloomFilter = require("bloom-filters").ScalableBloomFilter;

const MIN_LENGTH = 12;
const MAX_LENGTH = 64;

// Load a downloaded copy of Pwned Passwords into a bloom filter
// at startup. The filter is fast (microsecond lookup) and
// memory-efficient. Periodic refresh keeps it current.
const breachFilter = new ScalableBloomFilter(1e9, 0.001);
loadBreachedHashesIntoFilter("./data/pwned-passwords.txt", breachFilter);

function validatePassword(password) {
  if (password.length < MIN_LENGTH) {
    throw new ValidationError(`Password must be at least ${MIN_LENGTH} characters`);
  }
  if (password.length > MAX_LENGTH) {
    throw new ValidationError(`Password must be at most ${MAX_LENGTH} characters`);
  }
  const sha1 = crypto.createHash("sha1").update(password).digest("hex").toUpperCase();
  if (breachFilter.has(sha1)) {
    throw new ValidationError("This password appears in a known breach corpus");
  }
}

// Shared by signup and password-change flows
app.post("/signup", (req, res) => {
  try {
    validatePassword(req.body.password);
  } catch (e) {
    if (e instanceof ValidationError) {
      return res.status(400).json({error: e.message});
    }
    throw e;
  }
  // ... rest of signup
});

app.put("/password", (req, res) => {
  try {
    validatePassword(req.body.newPassword);
  } catch (e) {
    if (e instanceof ValidationError) {
      return res.status(400).json({error: e.message});
    }
    throw e;
  }
  // ... rest of password change
});
```

Why this satisfies authentication.password-policy:
- Local breach corpus eliminates third-party dependency
- Bloom filter is fast enough for inline validation
- Shared function applied at signup and password change

## Pattern C: Memorable passphrase generator suggestion (Python)

```python
import secrets
from words import EFF_LONG_WORDLIST  # EFF's diceware list

def suggest_passphrase(num_words=4):
    """Generate a substrate-recommended passphrase for users
    who want a strong memorable password."""
    return "-".join(secrets.choice(EFF_LONG_WORDLIST) for _ in range(num_words))

# 4 words from the EFF long list gives roughly 51 bits of entropy
# (12.92 bits per word). 5 words gives 64 bits. Both are
# substantially stronger than typical user-chosen passwords.

# Example signup flow with suggestion:
@app.route("/signup", methods=["GET"])
def signup_form():
    return render_template(
        "signup.html",
        suggested_passphrase=suggest_passphrase(),
    )
```

Why this satisfies authentication.password-policy:
- Encourages long memorable passphrases over short complex passwords
- Cryptographically secure random source (secrets.choice)
- Aligns with NIST guidance on length-over-complexity

## What good patterns have in common

- Length minimum 12+ (substrate-recommended), absolute floor 8
- Length maximum 64+
- No composition rules
- Breach corpus screening (HaveIBeenPwned API or local copy)
- Shared validation function across signup and password change
- No mandatory periodic expiration

## Cross-reference

- Substrate rule: authentication.password-policy in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Anti-patterns: examples/authentication/password-policy-anti-pattern.md
