<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.mfa-enrollment MFA enrollment (forbidden patterns)

## Anti-pattern A: Enrollment without fresh authentication

```python
# FORBIDDEN: MFA enrollment requires only session authenticity.
# A compromised session enrolls the attacker's factor and locks
# the legitimate user out.
@app.route("/mfa/enroll/totp", methods=["POST"])
def enroll_totp_BAD():
    user = g.user
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    # No freshness check. Any authenticated session can enroll.
    secret = pyotp.random_base32()
    user.totp_secret = secret
    db.commit()
    return jsonify({"secret": secret})
```

Why this violates authentication.mfa-enrollment:
- Session compromise alone is enough to enroll an attacker factor
- The legitimate user is locked out as soon as the attacker
  removes the legitimate factor

## Anti-pattern B: Backup codes shown indefinitely in account settings

```javascript
// FORBIDDEN: backup codes are persistently visible in account
// settings. Any session can retrieve them at any time.
app.get("/account/mfa/backup-codes", async (req, res) => {
  const user = req.user;
  // Return the codes whenever asked. The user can see them
  // long after enrollment; so can any attacker with session
  // access.
  return res.json({backupCodes: user.backupCodesPlaintext});
});
```

Why this violates authentication.mfa-enrollment:
- Codes retrievable after initial display defeats their purpose
- Session compromise grants ongoing access to MFA bypass codes
- Substrate pattern: shown once at generation; regenerate flow
  invalidates prior codes

## Anti-pattern C: Backup codes stored plaintext

```python
# FORBIDDEN: backup codes stored as plaintext in the database.
# Database compromise (read-only access) yields all users' MFA
# bypass codes.
@app.route("/mfa/enroll/totp", methods=["POST"])
@require_fresh_mfa(window_minutes=10)
def enroll_totp_BAD():
    user = g.user
    backup_codes = [secrets.token_urlsafe(8) for _ in range(10)]

    # FORBIDDEN: stored plaintext
    user.backup_codes_plaintext = backup_codes
    db.commit()

    return jsonify({"backup_codes": backup_codes})
```

Why this violates authentication.mfa-enrollment:
- Plaintext storage means any database read exposes all codes
- The right pattern: hash with Argon2id or bcrypt; codes are
  password-grade secrets

## Anti-pattern D: Backup codes reusable

```python
# FORBIDDEN: backup codes are not invalidated on use. Replay
# of the same code authenticates indefinitely.
def verify_backup_code_BAD(user, presented):
    ph = PasswordHasher()
    for stored_hash in user.backup_code_hashes:
        try:
            ph.verify(stored_hash, presented)
            return True  # ← no invalidation
        except Exception:
            continue
    return False
```

Why this violates authentication.mfa-enrollment:
- Codes reusable defeats their break-glass design
- Code captured once (over the shoulder, in a screenshot, in a
  password manager export) keeps working forever
- The right pattern: atomic invalidation on successful verification

## Anti-pattern E: Recovery via email confirmation alone

```python
# FORBIDDEN: MFA recovery completes solely on access to the
# primary email. Email compromise (very common in the same
# attack chain) cascades into MFA bypass.
@app.route("/mfa/recovery", methods=["POST"])
def recover_BAD():
    username = request.json.get("username")
    user = lookup_user(username)
    if user is None:
        return generic_response()

    # Send a "click here to disable MFA" link to the user's
    # primary email. No other identity proof.
    token = secrets.token_urlsafe(32)
    cache.set(f"recovery:{token}", user.id, ex=3600)
    send_email(user.email, f"Disable MFA: /recover/{token}")
    return generic_response()


@app.route("/recover/<token>", methods=["GET"])
def complete_recover_BAD(token):
    user_id = cache.get(f"recovery:{token}")
    if user_id is None:
        return "Invalid", 400
    # Immediately disable MFA. No delay. No other identity proof.
    db.users.update(user_id, mfa_enabled=False)
    return "MFA disabled"
```

Why this violates authentication.mfa-enrollment:
- Email-only recovery cascades email compromise into MFA bypass
- No delay window means legitimate user has no chance to detect
  and cancel
- No additional identity proof
- The right pattern: support-channel verification or
  pre-registered separate recovery method, plus delay window

## Anti-pattern F: Recovery completes immediately without delay window

```javascript
// FORBIDDEN: recovery completes at submission time. Even with
// identity proof, the legitimate user has no opportunity to
// detect and cancel unauthorized recovery.
app.post("/mfa/recovery/complete", async (req, res) => {
  const proof = req.body.identityProof;
  if (!await verifyIdentityProof(proof)) {
    return res.status(401).json({error: "Invalid identity proof"});
  }

  // Immediately disable MFA. No delay window. No notifications
  // to the user's other channels.
  await db.users.update({id: proof.userId}, {mfaEnabled: false});
  return res.json({status: "complete"});
});
```

Why this violates authentication.mfa-enrollment:
- No delay window means an attacker who acquires identity proof
  (social engineering, phishing) immediately bypasses MFA
- No notifications give the legitimate user no signal
- The right pattern: 24-48 hour delay; notifications at
  initiation; cancellation affordance

## Anti-pattern G: No audit logging on recovery

```python
# FORBIDDEN: recovery actions are silent. Incident response
# cannot reconstruct the attack timeline.
@app.route("/mfa/recovery/initiate", methods=["POST"])
def initiate_BAD():
    user = lookup_user(request.json.get("username"))
    if user:
        send_recovery_link(user)
    return generic_response()

# No audit_log.recovery_* calls anywhere. The recovery happens;
# no record exists.
```

Why this violates authentication.mfa-enrollment:
- Silent recovery defeats security monitoring
- Incident response cannot tell whether recovery was abused
- The right pattern: every step audit-logged with detail; alerts
  on unusual patterns

## Cross-reference

- Substrate rule: authentication.mfa-enrollment in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Good examples: examples/authentication/mfa-enrollment-good.md
