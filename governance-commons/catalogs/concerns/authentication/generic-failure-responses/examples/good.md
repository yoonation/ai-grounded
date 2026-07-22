<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.generic-failure-responses generic error messages (good patterns)

Substrate-original good-pattern examples for authentication.generic-failure-responses.

## Pattern A: Single generic failure response (Python / Flask)

```python
from flask import request, jsonify
import hmac

GENERIC_AUTH_FAILURE = ("Invalid credentials", 401)
# A known-bad password hash to verify against when the user
# does not exist, so the failure path takes the same time as
# a real verification path.
DUMMY_HASH = "$argon2id$v=19$m=19456,t=2,p=1$AAAAAAAA$" + ("A" * 43)

@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    username = body.get("username", "")
    password = body.get("password", "")

    user = lookup_user(username)
    if user is None:
        # Time-equalize: verify against dummy hash so failure
        # path takes the same time as a real verification.
        password_hasher.verify(DUMMY_HASH, password)
        return jsonify({"error": GENERIC_AUTH_FAILURE[0]}), GENERIC_AUTH_FAILURE[1]

    try:
        password_hasher.verify(user.password_hash, password)
    except VerifyMismatchError:
        return jsonify({"error": GENERIC_AUTH_FAILURE[0]}), GENERIC_AUTH_FAILURE[1]

    # Account locked, disabled, MFA required: all return the
    # same response to the client. The differentiation happens
    # in internal logging for security monitoring, not in the
    # response.
    if not user.is_active or user.is_locked:
        log_auth_event(user.id, "blocked_account_attempt")
        return jsonify({"error": GENERIC_AUTH_FAILURE[0]}), GENERIC_AUTH_FAILURE[1]

    return issue_session(user)
```

Why this satisfies authentication.generic-failure-responses:
- All failure paths return the same response text and status
- Time-equalization ensures timing does not leak cause
- Internal logging captures cause for security monitoring;
  the client receives no signal

## Pattern B: Generic response for account recovery (Node.js / Express)

```javascript
app.post("/forgot-password", async (req, res) => {
  const {email} = req.body;

  // Look up the user. If they exist, send the email. If they
  // do not exist, do nothing. In both cases, return the same
  // response to the client.
  const user = await lookupUserByEmail(email);
  if (user) {
    await sendPasswordResetEmail(user);
  }

  // Same response whether or not the email is registered.
  return res.status(200).json({
    message: "If an account exists for that email, a reset link has been sent.",
  });
});
```

Why this satisfies authentication.generic-failure-responses:
- Response is identical for registered and unregistered emails
- The user discovers their email is registered only by
  receiving (or not receiving) the email itself, which only
  the owner of that mailbox can observe

## Pattern C: Signup flow without enumeration leak

```javascript
app.post("/signup", async (req, res) => {
  const {email, password} = req.body;

  // If the email is already registered, do not say so to the
  // client. Send an email to the existing account informing
  // them of the attempted signup. The client gets the same
  // success response as a real signup.
  const existing = await lookupUserByEmail(email);
  if (existing) {
    await sendDuplicateSignupNotification(existing);
    return res.status(200).json({
      message: "Check your email to verify your account.",
    });
  }

  await createUser(email, password);
  await sendVerificationEmail(email);
  return res.status(200).json({
    message: "Check your email to verify your account.",
  });
});
```

Why this satisfies authentication.generic-failure-responses:
- New and existing emails produce identical responses
- The existing user is notified via email that a signup was
  attempted on their email, allowing them to investigate
- The signup attempt does not reveal account existence

## What good patterns have in common

- One response shape for all failure cases
- Time-equalization to defeat timing-based enumeration
- Differentiation lives in internal logging, not in the
  client response
- Account-recovery flows return the same message for
  registered and unregistered identifiers; communication of
  state happens via the registered email address only

## Cross-reference

- Substrate rule: authentication.generic-failure-responses in catalogs/concerns/authentication.oscal.yaml
- Tool binding: checklist.md
- Anti-patterns: examples/authentication/generic-error-messages-anti-pattern.md
