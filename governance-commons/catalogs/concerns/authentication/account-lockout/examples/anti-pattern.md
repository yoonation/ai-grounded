<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.account-lockout lockout policy (forbidden patterns)

## Anti-pattern A: Permanent lockout

```python
# FORBIDDEN: lockout never clears automatically. Attacker who
# submits 5 failed logins per account creates a denial-of-service
# at scale.
def login_BAD(username, password):
    user = lookup_user(username)
    if user is None:
        return generic_auth_failure()
    if user.is_locked:
        return generic_auth_failure()

    if not verify_password(user.password_hash, password):
        user.failure_count += 1
        if user.failure_count >= 5:
            user.is_locked = True  # ← permanent
        db.commit()
        return generic_auth_failure()

    user.failure_count = 0
    db.commit()
    return issue_session(user)
```

Why this violates authentication.account-lockout:
- Lockout requires manual admin intervention (or "contact support")
- Attacker can disable arbitrary accounts at will
- Even legitimate users with typos can get locked indefinitely

## Anti-pattern B: Lockout window resets on each attempt

```javascript
// FORBIDDEN: every failed attempt extends the lockout window.
// Attacker can keep an account locked indefinitely by submitting
// one failed attempt per window.
async function recordFailure_BAD(accountId) {
  const key = `lockout:fail:${accountId}`;
  const count = await redis.incr(key);
  // FORBIDDEN: expire reset on each call. Counter never times out
  // while attacker is active.
  await redis.expire(key, 900);
  if (count >= 5) {
    await redis.set(`lockout:${accountId}`, "locked", "EX", 900);
    // FORBIDDEN: same issue here. Lockout extends on each attempt.
  }
}

async function login_BAD(username, password) {
  if (await redis.exists(`lockout:${username}`)) {
    await recordFailure_BAD(username);  // even during lockout
    return genericAuthFailure();
  }
  // ... normal flow
}
```

Why this violates authentication.account-lockout:
- Lockout window resets on every attempt
- Attacker keeps account locked by sending one failed attempt
  per window
- Window must expire on the timer, not on activity

## Anti-pattern C: Lockout state revealed in response

```python
# FORBIDDEN: response distinguishes locked from invalid-credentials.
# Attacker can probe to find which accounts exist (lockout
# response implies the account was real).
def login_BAD(username, password):
    user = lookup_user(username)
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401

    if user.is_locked:
        return jsonify({
            "error": "Account locked. Try again in 15 minutes.",
            "lockout_until": user.lockout_until.isoformat(),
        }), 423  # ← distinguishable status code
    # ... normal flow
```

Why this violates authentication.account-lockout:
- Status code 423 reveals account is locked (and therefore exists)
- Response body contains the lockout-until timestamp (useful to
  attacker for timing the next attack)
- Combined violation: authentication.account-lockout (state leak) and authentication.generic-failure-responses
  (enumeration)

## Anti-pattern D: Lifetime failure count

```javascript
// FORBIDDEN: failure count accumulates without time-window reset.
// Years of legitimate typos accumulate; the user gets locked out
// because they've made 5 typos over five years.
async function recordFailure_BAD(accountId) {
  await db.query(
    "UPDATE users SET lifetime_failure_count = lifetime_failure_count + 1 WHERE id = $1",
    [accountId],
  );

  const result = await db.query(
    "SELECT lifetime_failure_count FROM users WHERE id = $1",
    [accountId],
  );

  if (result.rows[0].lifetime_failure_count >= 5) {
    await db.query("UPDATE users SET is_locked = true WHERE id = $1", [accountId]);
  }
}
```

Why this violates authentication.account-lockout:
- Counter has no time window
- Failures from arbitrary past time contribute to current lockout
- User experience degrades over time as failures accumulate

## Anti-pattern E: Password reset does not clear lockout

```python
# FORBIDDEN: user is locked out and uses password reset, but
# the reset does not clear the lockout. User remains locked out
# until the timer expires.
def reset_password_BAD(reset_token, new_password):
    user = consume_reset_token(reset_token)
    if user is None:
        return generic_failure()
    user.password_hash = hash_password(new_password)
    # ← does NOT clear lockout state
    db.commit()
    return success_response()


def login_BAD(username, password):
    user = lookup_user(username)
    if user is None:
        return generic_auth_failure()
    if user.is_locked:
        return generic_auth_failure()
    # ...
```

Why this violates authentication.account-lockout:
- Password reset (the substrate's primary self-service recovery)
  does not clear lockout
- User is in a confusing state: knows the new password but can't
  log in
- Reset must atomically clear lockout per authentication.account-lockout

## Anti-pattern F: No lockout at all on auth endpoints (paired with no rate limiting)

```python
# FORBIDDEN: no per-account limit. authentication.rate-limiting covers per-IP, but
# this anti-pattern omits the per-account dimension entirely.
# Attacker with botnet performs distributed credential stuffing
# against one account without ever tripping a limit.
@app.route("/login", methods=["POST"])
def login_BAD():
    user = authenticate(request.json["username"], request.json["password"])
    if user is None:
        return generic_auth_failure()
    return issue_session(user)
```

Why this violates authentication.account-lockout:
- No per-account threshold means lockout never triggers
- Distributed attacks bypass the per-IP-only protection
- authentication.rate-limiting and authentication.account-lockout work together; both are needed

## Cross-reference

- Substrate rule: authentication.account-lockout in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Good examples: examples/authentication/lockout-policy-good.md
