<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.password-policy password policy (forbidden patterns)

## Anti-pattern A: Short minimum with composition rules

```python
# FORBIDDEN: 8-character minimum with character-class requirements.
# Produces predictable substitution patterns (P@ssw0rd) that
# attacker rules handle, while being too short to defeat brute
# force.
def validate_password_BAD(password):
    if len(password) < 8:
        raise ValidationError("Password too short")
    if not any(c.isupper() for c in password):
        raise ValidationError("Need uppercase letter")
    if not any(c.isdigit() for c in password):
        raise ValidationError("Need digit")
    if not any(c in "!@#$%^&*" for c in password):
        raise ValidationError("Need special character")
    # No breach screening
```

Why this violates authentication.password-policy:
- Length floor too low (8 < substrate recommended 12)
- Composition rules produce predictable user behavior
- No breach screening

## Anti-pattern B: Mandatory periodic expiration

```javascript
// FORBIDDEN: passwords expire every 90 days. Users adopt
// minimal-change patterns (winter2025 → spring2026) that
// weaken passwords over time.
function isPasswordExpired_BAD(user) {
  const ageMs = Date.now() - user.passwordChangedAt;
  const ageDays = ageMs / (24 * 60 * 60 * 1000);
  return ageDays > 90;
}

app.use((req, res, next) => {
  if (req.user && isPasswordExpired_BAD(req.user)) {
    return res.redirect("/password-change");
  }
  next();
});
```

Why this violates authentication.password-policy:
- Forces password changes on a calendar
- Users produce weaker passwords over time
- Expiration should trigger only on credible compromise signal

## Anti-pattern C: Low maximum length excludes passphrases

```python
# FORBIDDEN: 20-character maximum excludes the substrate-recommended
# long memorable passphrases. Users who try to use a strong
# passphrase are forced to truncate to something weaker.
def validate_password_BAD(password):
    if len(password) < 8:
        raise ValidationError("Too short")
    if len(password) > 20:  # ← substrate floor for max is 64
        raise ValidationError("Too long")
```

Why this violates authentication.password-policy:
- 20-character maximum is below substrate floor of 64
- Discriminates against strong passphrases
- The right pattern: at least 64; up to bcrypt limit (72) or
  Argon2id practical limit

## Anti-pattern D: No breach corpus screening

```javascript
// FORBIDDEN: policy accepts "password123" because it meets
// length minimum. The breach corpus has this password in
// millions of records.
function validatePassword_BAD(password) {
  if (password.length < 12) {
    throw new ValidationError("Too short");
  }
  // No breach screening
}
```

Why this violates authentication.password-policy:
- Common breached passwords pass the policy
- Length alone is insufficient if the password is known to attackers
- Breach screening is the substrate's primary defense against
  credential-stuffing-with-existing-data

## Anti-pattern E: Password sent to third party for screening

```python
# FORBIDDEN: password sent in plaintext to a third-party API
# for breach checking. Even if the third party is trustworthy,
# the password should not leave the application.
def is_breached_BAD(password):
    response = httpx.post(
        "https://breach-check-service.example.com/check",
        json={"password": password},  # ← plaintext password leaves the application
    )
    return response.json()["breached"]
```

Why this violates authentication.password-policy:
- Plaintext password transmitted to third party
- The right pattern is k-anonymity (send only a 5-character
  SHA-1 prefix); third party returns hash suffixes that match
- Local breach corpus also avoids the third-party dependency

## Anti-pattern F: Validation only at signup, not at password change

```python
# FORBIDDEN: signup applies the policy, password change does not.
# Users can rotate to weaker passwords later.
@app.route("/signup", methods=["POST"])
def signup():
    body = request.get_json()
    validate_password(body["password"])
    create_user(body["username"], body["password"])
    return success()


@app.route("/password", methods=["PUT"])
def change_password_BAD():
    body = request.get_json()
    user = g.user
    # FORBIDDEN: no validation; user can rotate to "12345"
    user.password_hash = hash_password(body["new_password"])
    db.commit()
    return success()
```

Why this violates authentication.password-policy:
- Policy drift between signup and password change
- Users who started with strong passwords can rotate to weak ones
- Shared validation function applied to both flows is the
  correct pattern

## Anti-pattern G: Sending plaintext password back to client

```javascript
// FORBIDDEN: error message echoes the rejected password.
// The password (which the user has now committed to memory
// as their candidate) is at risk in logs and browser history.
function validatePassword_BAD(password) {
  if (password.length < 12) {
    throw new ValidationError(
      `Password "${password}" is too short. Try something longer.`
    );
  }
}
```

Why this violates authentication.password-policy:
- Password appears in error message that may be logged or
  cached
- Even a "rejected" password is a real password the user might
  try at another service
- Error messages should never include the password value

## Cross-reference

- Substrate rule: authentication.password-policy in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Good examples: examples/authentication/password-policy-good.md
