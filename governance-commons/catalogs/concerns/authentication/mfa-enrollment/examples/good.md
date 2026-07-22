<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.mfa-enrollment MFA enrollment (good patterns)

## Pattern A: Fresh-auth-gated TOTP enrollment (Python / Flask)

```python
import secrets
import pyotp
from argon2 import PasswordHasher
from datetime import datetime, timezone

# Decorator from authentication.mfa-on-privileged-operations examples
@app.route("/mfa/enroll/totp", methods=["POST"])
@require_fresh_mfa(window_minutes=10)
def enroll_totp():
    user = g.user

    # Generate the TOTP secret
    secret = pyotp.random_base32()

    # Generate 10 backup codes, single-use, cryptographically random
    backup_codes = [secrets.token_urlsafe(8) for _ in range(10)]

    # Store TOTP secret (encrypted at rest via the app's KMS)
    user.totp_secret_enc = encrypt_with_kms(secret)
    user.mfa_enrolled_at = datetime.now(timezone.utc)

    # Store backup codes HASHED, never plaintext
    ph = PasswordHasher()
    user.backup_code_hashes = [ph.hash(code) for code in backup_codes]
    db.commit()

    audit_log.mfa_enrolled(
        user_id=user.id,
        factor_type="totp",
        source_ip=request.remote_addr,
    )

    # Display codes ONCE; user must record them now
    return jsonify({
        "secret": secret,
        "qr_code_uri": pyotp.totp.TOTP(secret).provisioning_uri(
            user.email, issuer_name="ExampleApp"
        ),
        "backup_codes": backup_codes,
        "warning": "Save these backup codes now. They will not be shown again.",
    })


@app.route("/mfa/verify-backup-code", methods=["POST"])
def verify_backup_code():
    user = g.user
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    presented = request.json.get("code", "")
    ph = PasswordHasher()

    # Find the matching hash (timing-safe per authentication.timing-safe-comparison)
    matched_index = None
    for i, stored_hash in enumerate(user.backup_code_hashes):
        try:
            ph.verify(stored_hash, presented)
            matched_index = i
            break
        except Exception:
            continue

    if matched_index is None:
        audit_log.backup_code_attempt(user_id=user.id, result="failed")
        return jsonify({"error": "Invalid code"}), 401

    # Single-use: invalidate the code by removing the hash
    user.backup_code_hashes.pop(matched_index)
    db.commit()

    audit_log.backup_code_attempt(user_id=user.id, result="passed")
    session_store.set_mfa_timestamp(g.session_id, datetime.now(timezone.utc))
    return jsonify({"status": "ok"})
```

Why this satisfies authentication.mfa-enrollment:
- Enrollment gated by fresh MFA (authentication.mfa-on-privileged-operations decorator)
- TOTP secret stored encrypted at rest
- Backup codes generated via cryptographically secure source
- Backup codes hashed with Argon2id server-side
- Single-use enforced atomically on verification
- Audit logging at enrollment and on every code attempt

## Pattern B: WebAuthn passkey enrollment (Node.js)

```javascript
const {
  generateRegistrationOptions,
  verifyRegistrationResponse,
} = require("@simplewebauthn/server");

// Enrollment options endpoint (requires fresh MFA)
app.post("/mfa/passkey/begin-enroll", requireFreshMFA(10), async (req, res) => {
  const user = req.user;

  const options = await generateRegistrationOptions({
    rpName: "ExampleApp",
    rpID: "example.com",
    userID: user.id,
    userName: user.email,
    attestationType: "none",
    excludeCredentials: user.passkeys.map((p) => ({
      id: p.credentialID,
      type: "public-key",
    })),
    authenticatorSelection: {
      residentKey: "preferred",
      userVerification: "preferred",
    },
  });

  // Store challenge server-side (single-use, time-bounded)
  await challengeStore.set(`enroll:${user.id}`, options.challenge, 300);

  res.json(options);
});


app.post("/mfa/passkey/complete-enroll", requireFreshMFA(10), async (req, res) => {
  const user = req.user;
  const expectedChallenge = await challengeStore.get(`enroll:${user.id}`);
  if (!expectedChallenge) {
    return res.status(400).json({error: "No active enrollment"});
  }

  const verification = await verifyRegistrationResponse({
    response: req.body,
    expectedChallenge,
    expectedOrigin: "https://example.com",
    expectedRPID: "example.com",
  });

  if (!verification.verified) {
    await auditLog.passkeyEnroll({userId: user.id, result: "verification_failed"});
    return res.status(400).json({error: "Verification failed"});
  }

  // Store the new passkey
  await db.passkeys.create({
    userId: user.id,
    credentialID: verification.registrationInfo.credentialID,
    publicKey: verification.registrationInfo.credentialPublicKey,
    counter: verification.registrationInfo.counter,
    enrolledAt: new Date(),
  });

  // Invalidate the challenge (single-use)
  await challengeStore.delete(`enroll:${user.id}`);

  await auditLog.passkeyEnroll({userId: user.id, result: "success"});
  res.json({status: "enrolled"});
});
```

Why this satisfies authentication.mfa-enrollment:
- Fresh-auth gating on both begin and complete steps
- Challenge is server-stored, single-use, time-bounded
- WebAuthn is phishing-resistant (substrate-preferred factor)
- Audit logging on enrollment outcome

## Pattern C: Recovery with delay window and identity proof (Python)

```python
import secrets
from datetime import datetime, timezone, timedelta

@app.route("/mfa/recovery/initiate", methods=["POST"])
def initiate_recovery():
    """Begin MFA recovery. Does NOT immediately bypass MFA."""
    # Allow unauthenticated; this is for users who lost MFA
    username = request.json.get("username", "")

    # Rate-limited per authentication.rate-limiting
    if rate_limiter.is_limited(f"recovery:{username}", request.remote_addr):
        return generic_response()

    user = lookup_user(username)
    if user is None:
        return generic_response()  # Same response shape per authentication.generic-failure-responses

    # Identity proof: require pre-registered recovery contact
    # (separate from primary email) AND a knowledge-based answer
    # OR a previously-enrolled secondary factor

    recovery_request_id = secrets.token_urlsafe(32)
    db.recovery_requests.create(
        id=recovery_request_id,
        user_id=user.id,
        initiated_at=datetime.now(timezone.utc),
        # 48-hour delay before completion is allowed
        earliest_completion_at=datetime.now(timezone.utc) + timedelta(hours=48),
        status="pending_identity_proof",
    )

    # Notify ALL registered contact channels
    send_notification(
        user.primary_email,
        subject="MFA recovery initiated",
        body=f"If this was not you, cancel here: /recovery/cancel/{recovery_request_id}",
    )
    if user.recovery_email:
        send_notification(user.recovery_email, ...)
    if user.recovery_phone:
        send_sms(user.recovery_phone, ...)

    audit_log.recovery_initiated(
        user_id=user.id,
        request_id=recovery_request_id,
        source_ip=request.remote_addr,
    )
    return generic_response()


@app.route("/mfa/recovery/<request_id>/cancel", methods=["POST"])
def cancel_recovery(request_id):
    """Legitimate user cancels unauthorized recovery."""
    req_record = db.recovery_requests.find(request_id)
    if req_record is None or req_record.status == "completed":
        return jsonify({"status": "ok"})  # Generic response

    req_record.status = "cancelled"
    db.commit()

    audit_log.recovery_cancelled(
        user_id=req_record.user_id,
        request_id=request_id,
    )
    return jsonify({"status": "ok"})


@app.route("/mfa/recovery/<request_id>/complete", methods=["POST"])
def complete_recovery(request_id):
    """Complete recovery after delay window AND identity proof."""
    req_record = db.recovery_requests.find(request_id)
    if req_record is None:
        return jsonify({"error": "Invalid request"}), 400

    if req_record.status == "cancelled":
        return jsonify({"error": "Recovery cancelled"}), 400

    if datetime.now(timezone.utc) < req_record.earliest_completion_at:
        return jsonify({"error": "Delay window not yet elapsed"}), 400

    # Verify identity proof submitted with the request
    if not verify_identity_proof(req_record.user_id, request.json):
        audit_log.recovery_completion_attempted(
            user_id=req_record.user_id,
            request_id=request_id,
            result="identity_proof_failed",
        )
        return generic_response()

    # Disable existing MFA; user must re-enroll
    db.users.update(req_record.user_id, mfa_enabled=False)
    req_record.status = "completed"
    db.commit()

    audit_log.recovery_completed(
        user_id=req_record.user_id,
        request_id=request_id,
    )
    return jsonify({"status": "complete; please re-enroll MFA"})
```

Why this satisfies authentication.mfa-enrollment:
- Recovery does NOT silently bypass MFA
- 48-hour delay window allows legitimate user to detect and cancel
- All registered channels notified at initiation
- Identity proof required at completion (knowledge, secondary
  factor, or support verification)
- Audit logging at every step

## Cross-reference

- Substrate rule: authentication.mfa-enrollment in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Anti-patterns: examples/authentication/mfa-enrollment-anti-pattern.md
