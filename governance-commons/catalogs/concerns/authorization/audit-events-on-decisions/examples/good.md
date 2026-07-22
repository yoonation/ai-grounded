<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.audit-events-on-decisions authorization audit events on decisions (good patterns)

Substrate-original good-pattern examples for authorization.audit-events-on-decisions.

## Pattern A: Emission inside the centralized policy point (Python)

```python
import structlog

logger = structlog.get_logger("authz")


class PolicyPoint:
    def decide(self, principal, action, resource_type, resource_id=None):
        # Evaluate the policy
        engine_result = self._engine.is_authorized(
            principal=principal.subject_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
        )
        decision = Decision(
            allow=engine_result.is_allow,
            reason=engine_result.reason,
        )

        # Audit event emitted for every decision (allow AND deny)
        logger.log(
            level="WARN" if not decision.allow else "INFO",
            event="authz_decision",
            principal=principal.subject_id,         # from authoritative session
            principal_role=principal.role,
            tenant_id=str(principal.tenant_id),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            decision="allow" if decision.allow else "deny",
            reason=decision.reason,
            correlation_id=current_correlation_id(),
            timestamp=now().isoformat(),
        )

        return decision
```

The substrate-recommended emission site (the policy point per
authorization.centralized-deny-by-default-policy) emits the event. A single emission site covers
every call site automatically.

## Pattern B: Deny events at higher severity for SIEM consumption

```python
# Severity assignment per logging.severity-levels:
# - Allow: INFO (completeness without saturating alerts)
# - Deny: WARN minimum (so SIEM consumes for anomaly detection)
# - Deny on sensitive resource: ERROR (security-critical signal)

class PolicyPoint:
    SENSITIVE_RESOURCE_TYPES = {"medical_record", "payment_info",
                                  "personal_id"}

    def decide(self, principal, action, resource_type, resource_id=None):
        decision = self._engine.decide(principal, action,
                                        resource_type, resource_id)

        if decision.allow:
            severity = "INFO"
        elif resource_type in self.SENSITIVE_RESOURCE_TYPES:
            severity = "ERROR"
        else:
            severity = "WARN"

        logger.log(
            level=severity,
            event="authz_decision",
            principal=principal.subject_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            decision="allow" if decision.allow else "deny",
            severity_class="sensitive-resource" if severity == "ERROR" else "standard",
            correlation_id=current_correlation_id(),
            timestamp=now().isoformat(),
        )

        return decision
```

## Pattern C: Bulk operations emit one event per decision

```python
@app.post("/resources/batch")
def batch_get(payload):
    principal = current_principal()
    results = []

    for resource_id in payload.ids:
        # Each decision produces its own audit event via
        # the policy point's emission
        decision = policy_point.decide(
            principal=principal,
            action="read",
            resource_type="resource",
            resource_id=resource_id,
        )
        if decision.allow:
            results.append(Resource.get(resource_id).to_dict())

    return jsonify(results)
```

The bulk handler calls the policy point N times; the policy
point emits N audit events. Each event has the same
correlation_id (the request's correlation ID), so investigators
can reconstruct the bulk operation.

## Pattern D: Redaction integrated with logging.no-sensitive-data-in-logs

```python
# The application's logging configuration includes a redaction
# processor (per logging.no-sensitive-data-in-logs). Authz audit events flow through
# the same processor.
import structlog


def redact_sensitive_fields(_, __, event_dict):
    """Remove credential and sensitive content from events."""
    for sensitive_key in ("password", "token", "session_cookie",
                          "authorization_header", "ssn",
                          "credit_card_number"):
        if sensitive_key in event_dict:
            event_dict[sensitive_key] = "[REDACTED]"
    # Truncate any free-text field that could contain payload
    for field in ("resource_content", "request_body"):
        if field in event_dict:
            del event_dict[field]
    return event_dict


structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        redact_sensitive_fields,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
```

## Pattern E: Principal identity from authoritative session

```python
def get_authoritative_principal(request):
    """Single source for principal identity used by the
    policy point and audit emission."""
    session_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    claims = jwt.decode(
        session_token,
        key=server_signing_key.public_key(),
        algorithms=["RS256"],  # server-controlled signing
    )
    return Principal(
        subject_id=claims["sub"],
        role=claims["role"],
        tenant_id=claims["tenant_id"],
        session_id=claims["jti"],
    )


# The audit event reads principal from the same function:
# request body fields cannot influence the audit principal.
def some_handler(request):
    principal = get_authoritative_principal(request)
    # ...
    policy_point.decide(
        principal=principal,  # SAME SOURCE; not request.body["user_id"]
        action="...",
        resource_type="...",
        resource_id="...",
    )
```

Why these patterns satisfy authorization.audit-events-on-decisions:
- Every decision (allow and deny) produces a structured event
- Required fields (principal, resource, action, decision,
  timestamp) all present
- Severity assignment aligns with logging.severity-levels; deny at WARN
  minimum
- Principal field comes from authoritative session, not
  request body
- logging.no-sensitive-data-in-logs redaction applies; logging.structured-format structured format
  applies; logging.correlation-ids correlation ID applies; logging.retention-policy
  retention applies
- Bulk operations produce per-decision events
