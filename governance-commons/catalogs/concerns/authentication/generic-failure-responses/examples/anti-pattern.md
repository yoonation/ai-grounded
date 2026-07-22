<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.generic-failure-responses generic error messages (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Distinguishing user existence (Python / Flask)

```python
@app.route("/login", methods=["POST"])
def login_BAD():
    body = request.get_json()
    user = lookup_user(body["username"])
    # FORBIDDEN: response distinguishes whether the account exists.
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if not verify_password(user.password_hash, body["password"]):
        return jsonify({"error": "Incorrect password"}), 401
    return issue_session(user)
```

Why this violates authentication.generic-failure-responses:
- Different responses for non-existent user vs wrong password
- Attacker submits candidate usernames and observes which
  return 404 (does not exist) vs 401 (exists)
- Enumeration enables credential stuffing and targeted
  phishing

## Anti-pattern B: Distinguishing account state (Node.js)

```javascript
app.post("/login", async (req, res) => {
  const user = await lookupUser(req.body.username);
  if (!user) return res.status(401).json({error: "Invalid credentials"});
  if (!await verifyPassword(user.passwordHash, req.body.password)) {
    return res.status(401).json({error: "Invalid credentials"});
  }
  // FORBIDDEN: response reveals account state to the client.
  if (user.isLocked) {
    return res.status(403).json({error: "Account locked. Try again in 15 minutes."});
  }
  if (!user.isVerified) {
    return res.status(403).json({error: "Email not verified. Check your inbox."});
  }
  return issueSession(res, user);
});
```

Why this violates authentication.generic-failure-responses:
- Locked-account and unverified-account responses reveal that
  the credentials WERE correct
- An attacker who finds credentials in a breach can confirm
  they work against this service even on locked accounts
- The right pattern is to log the cause internally and
  return the same generic failure to the client

## Anti-pattern C: Timing-revealing fast-path on missing user

```python
def login_BAD(username, password):
    user = lookup_user(username)
    if user is None:
        # FORBIDDEN: fast return when user is missing. The
        # password verification path (which takes 250+ ms with
        # Argon2id) is skipped, making the missing-user path
        # measurably faster.
        return GENERIC_AUTH_FAILURE
    if not verify_password(user.password_hash, password):
        return GENERIC_AUTH_FAILURE
    return issue_session(user)
```

Why this violates authentication.generic-failure-responses:
- Even with identical response text and status, timing
  differs measurably between paths
- The mitigation is the dummy-hash verification shown in
  the good pattern

## Anti-pattern D: Email enumeration in password reset

```javascript
app.post("/forgot-password", async (req, res) => {
  const user = await lookupUserByEmail(req.body.email);
  if (!user) {
    // FORBIDDEN: response reveals the email is not registered.
    return res.status(404).json({error: "No account with that email"});
  }
  await sendPasswordResetEmail(user);
  return res.status(200).json({message: "Reset link sent"});
});
```

Why this violates authentication.generic-failure-responses:
- 404 response is unambiguous enumeration disclosure
- Reset flows must return identical responses for registered
  and unregistered emails

## Anti-pattern E: Signup enumeration

```python
@app.route("/signup", methods=["POST"])
def signup_BAD():
    body = request.get_json()
    if user_exists(body["email"]):
        # FORBIDDEN: response reveals email is already registered.
        return jsonify({"error": "Email already registered"}), 409
    create_user(body)
    return jsonify({"message": "Account created"}), 201
```

Why this violates authentication.generic-failure-responses:
- 409 Conflict is unambiguous enumeration
- Signup forms must return success-like responses even when
  the email is taken; differentiation happens via the email
  channel (see good-pattern Pattern C)

## What anti-patterns have in common

- Response differentiation visible to the client
- Status code differentiation (404 vs 401 vs 403 vs 409)
- Timing differentiation between paths
- Account-state disclosure (locked, disabled, unverified) in
  authentication response

## Cross-reference

- Substrate rule: authentication.generic-failure-responses in catalogs/concerns/authentication.oscal.yaml
- Tool binding: checklist.md
- Good examples: examples/authentication/generic-error-messages-good.md
