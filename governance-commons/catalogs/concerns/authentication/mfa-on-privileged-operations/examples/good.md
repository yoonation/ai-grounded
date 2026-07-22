<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authentication.mfa-on-privileged-operations MFA on privileged operations (good patterns)

## Pattern A: Decorator-based freshness check (Python / Flask)

```python
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import g, jsonify, request


def require_fresh_mfa(window_minutes=15):
    """Decorator: privileged op requires MFA challenge within window."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = g.user
            if not user:
                return jsonify({"error": "Authentication required"}), 401

            mfa_completed_at = session_store.get_mfa_timestamp(g.session_id)
            if mfa_completed_at is None:
                return jsonify({
                    "error": "MFA required",
                    "code": "mfa_required",
                }), 401

            age = datetime.now(timezone.utc) - mfa_completed_at
            if age > timedelta(minutes=window_minutes):
                audit_log.privileged_attempt(
                    user_id=user.id,
                    operation=view_func.__name__,
                    result="stale_mfa",
                )
                return jsonify({
                    "error": "MFA required",
                    "code": "mfa_stale",
                }), 401

            audit_log.privileged_attempt(
                user_id=user.id,
                operation=view_func.__name__,
                result="passed",
            )
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# Apply to privileged operations with appropriate windows
@app.route("/account/delete", methods=["POST"])
@require_fresh_mfa(window_minutes=5)
def delete_account():
    return _execute_account_deletion(g.user)


@app.route("/payment-methods/<method_id>", methods=["PUT", "DELETE"])
@require_fresh_mfa(window_minutes=10)
def manage_payment_method(method_id):
    return _execute_payment_method_change(g.user, method_id)


@app.route("/password", methods=["PUT"])
@require_fresh_mfa(window_minutes=15)
def change_password():
    return _execute_password_change(g.user, request.json)
```

Why this satisfies authentication.mfa-on-privileged-operations:
- Decorator centralizes the freshness check
- Different windows tuned per operation sensitivity
- Audit logging on every attempt
- Operation does not execute until check passes

## Pattern B: Middleware-based for grouped routes (Node.js / Express)

```javascript
function requireFreshMFA(windowMinutes) {
  return async (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({error: "Authentication required"});
    }

    const mfaCompletedAt = await sessionStore.getMFATimestamp(req.sessionID);
    if (!mfaCompletedAt) {
      return res.status(401).json({error: "MFA required", code: "mfa_required"});
    }

    const ageMinutes = (Date.now() - mfaCompletedAt) / 60000;
    if (ageMinutes > windowMinutes) {
      await auditLog.privilegedAttempt({
        userId: req.user.id,
        operation: req.path,
        result: "stale_mfa",
      });
      return res.status(401).json({error: "MFA required", code: "mfa_stale"});
    }

    await auditLog.privilegedAttempt({
      userId: req.user.id,
      operation: req.path,
      result: "passed",
    });
    next();
  };
}

const privilegedRouter = express.Router();
privilegedRouter.use(requireFreshMFA(10));
privilegedRouter.post("/account/delete", requireFreshMFA(5), deleteAccountHandler);
privilegedRouter.put("/payment-methods/:id", managePaymentHandler);
privilegedRouter.put("/password", requireFreshMFA(15), changePasswordHandler);

app.use("/api/privileged", privilegedRouter);
```

Why this satisfies authentication.mfa-on-privileged-operations:
- Middleware applied to all routes under /api/privileged
- Per-route override allows custom windows
- Centralized telemetry via auditLog

## Pattern C: MFA challenge completion updates freshness

```python
@app.route("/mfa/challenge", methods=["POST"])
def submit_mfa_challenge():
    user = g.user
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    presented = request.json.get("code", "")
    if verify_totp(user.totp_secret, presented):
        # Update the server-side freshness timestamp.
        session_store.set_mfa_timestamp(g.session_id, datetime.now(timezone.utc))
        audit_log.mfa_challenge(user_id=user.id, result="passed")
        return jsonify({"status": "ok"})

    audit_log.mfa_challenge(user_id=user.id, result="failed")
    return jsonify({"error": "Invalid code"}), 401
```

Why this satisfies authentication.mfa-on-privileged-operations:
- Freshness timestamp updates only on successful challenge
- Freshness is server-side (client cannot forge it)
- Audit log captures every challenge attempt

## Cross-reference

- Substrate rule: authentication.mfa-on-privileged-operations in catalogs/concerns/authentication.oscal.yaml
- Review binding: checklist.md
- Test binding: test-template.md
- Anti-patterns: examples/authentication/mfa-on-privileged-ops-anti-pattern.md
