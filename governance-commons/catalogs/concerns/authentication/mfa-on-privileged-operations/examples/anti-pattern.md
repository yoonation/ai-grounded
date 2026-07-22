<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.mfa-on-privileged-operations MFA on privileged operations (forbidden patterns)

## Anti-pattern A: Privileged op gated only by session

```python
# FORBIDDEN: password change requires authenticated session but
# does not require fresh MFA. A compromised session changes the
# password and locks the legitimate user out.
@app.route("/password", methods=["PUT"])
def change_password_BAD():
    user = g.user
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    new_password = request.json.get("new_password")
    user.password_hash = hash_password(new_password)
    db.commit()
    return jsonify({"status": "ok"})
```

Why this violates authentication.mfa-on-privileged-operations:
- Session validity alone gates the operation
- A stolen session token grants password change ability
- The legitimate user can be locked out via single session compromise

## Anti-pattern B: Freshness window too long

```javascript
// FORBIDDEN: freshness window is 7 days. Effectively disables
// the check; any session that has ever passed MFA can perform
// privileged operations for a week.
function requireFreshMFA(windowDays = 7) {
  return async (req, res, next) => {
    const mfaCompletedAt = await sessionStore.getMFATimestamp(req.sessionID);
    const ageDays = (Date.now() - mfaCompletedAt) / (24 * 60 * 60 * 1000);
    if (ageDays > windowDays) return res.status(401).json({error: "MFA required"});
    next();
  };
}
```

Why this violates authentication.mfa-on-privileged-operations:
- 7-day window provides essentially no freshness protection
- Session compromise inherits the MFA-passed state for a week
- Substrate-recommended ranges are minutes, not days

## Anti-pattern C: Freshness check after partial execution

```python
# FORBIDDEN: the operation begins executing before the freshness
# check. Mutations occur even when the check fails.
@app.route("/account/delete", methods=["POST"])
def delete_account_BAD():
    user = g.user

    # Mark account as pending deletion FIRST, then check MFA.
    user.deletion_requested_at = datetime.now(timezone.utc)
    db.commit()  # ← mutation persisted

    mfa_age = check_mfa_freshness(g.session_id)
    if mfa_age > timedelta(minutes=5):
        return jsonify({"error": "MFA required"}), 401  # too late

    user.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return jsonify({"status": "ok"})
```

Why this violates authentication.mfa-on-privileged-operations:
- Mutation persists before the freshness check
- Even a stale MFA can poison the account state (visible
  pending-deletion flag)
- The check must precede all mutations

## Anti-pattern D: Client-supplied MFA timestamp

```javascript
// FORBIDDEN: the MFA timestamp is read from a client-supplied
// header or cookie. The client (and any attacker who controls
// the client) can forge the value.
function requireFreshMFA(req, res, next) {
  const mfaTimestamp = parseInt(req.headers["x-mfa-timestamp"]);
  const ageSeconds = (Date.now() / 1000) - mfaTimestamp;
  if (ageSeconds > 900) return res.status(401).end();
  next();
}
```

Why this violates authentication.mfa-on-privileged-operations:
- Client-supplied timestamp is forgeable
- Attacker sets header to "now" and bypasses the check
- Freshness must be server-side and tamper-proof

## Anti-pattern E: Recovery flow that bypasses MFA without identity proof

```python
# FORBIDDEN: MFA recovery via "send a code to my email" alone.
# The email is often part of the compromise scope.
@app.route("/mfa/recovery", methods=["POST"])
def recover_mfa_BAD():
    user = g.user
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    recovery_token = secrets.token_urlsafe(32)
    send_email(user.email, f"Reset link: /mfa/recovery/{recovery_token}")
    cache.set(f"recovery:{recovery_token}", user.id, ttl=900)
    return jsonify({"status": "ok"})


@app.route("/mfa/recovery/<token>", methods=["POST"])
def complete_mfa_recovery_BAD(token):
    user_id = cache.get(f"recovery:{token}")
    if user_id:
        # Disable MFA entirely. No identity proof beyond clicking
        # the email link.
        db.execute("UPDATE users SET mfa_enabled = FALSE WHERE id = %s", (user_id,))
        return jsonify({"status": "ok"})
    return jsonify({"error": "Invalid token"}), 400
```

Why this violates authentication.mfa-on-privileged-operations:
- Recovery silently disables MFA based on email access alone
- Email compromise (common scenario) cascades into MFA bypass
- The right pattern: support-channel identity verification with
  delay window (see authentication.mfa-enrollment)

## Cross-reference

- Substrate rule: authentication.mfa-on-privileged-operations in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Good examples: examples/authentication/mfa-on-privileged-ops-good.md
