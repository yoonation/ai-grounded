<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.audit-events-on-decisions authorization audit events on decisions (forbidden patterns)

Substrate-original anti-patterns. Do not copy into production.

## Anti-pattern A: Unstructured log line (Python)

```python
# FORBIDDEN: plaintext log line with no structure. Cannot be
# parsed, queried, or correlated.
def decide_BAD(principal, action, resource_type, resource_id):
    decision = engine.decide(principal, action, resource_type, resource_id)
    print(f"User {principal.email} attempted {action} on {resource_type} {resource_id}: {decision}")
    return decision
```

Why this violates authorization.audit-events-on-decisions (and logging.structured-format):
- The event is a printf line, not a structured record
- Required fields are embedded in free text
- A log query "show me all denies" requires regex parsing
- principal.email is PII; the substrate's principal identity
  should be a stable subject_id, not an email
- print() bypasses the application's logging configuration
  including any redaction processor

## Anti-pattern B: Only allow events emitted (Node.js)

```javascript
// FORBIDDEN: allow events logged, deny events silently
// dropped. Investigators cannot reconstruct denied attempts.
function decide_BAD(principal, action, resourceType, resourceId) {
  const decision = engine.decide(principal, action, resourceType, resourceId);
  if (decision.allow) {
    logger.info({
      event: "authz_decision",
      principal: principal.subjectId,
      action,
      resourceType,
      resourceId,
      decision: "allow",
    });
  }
  // DENY EVENTS NOT LOGGED
  return decision;
}
```

Why this violates authorization.audit-events-on-decisions:
- Deny events are the substrate's highest-signal audit data
  for incident investigation and anomaly detection
- The pattern fails the substrate's coverage requirement:
  every decision must produce an event
- A surge of denies (attacker probing) is undetectable

## Anti-pattern C: Deny events at INFO severity (Python)

```python
# FORBIDDEN: deny events logged but at INFO severity. SIEM
# rules tuned to WARN-and-above never see them.
def decide_BAD(principal, action, resource_type, resource_id):
    decision = engine.decide(principal, action, resource_type, resource_id)
    logger.info(  # INFO ALWAYS
        "authz_decision",
        principal=principal.subject_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        decision="allow" if decision.allow else "deny",
    )
    return decision
```

Why this violates authorization.audit-events-on-decisions:
- Severity is uniform across allow and deny
- SIEM alerting on WARN-and-above never triggers on denies
- The substrate requires deny severity to be WARN minimum;
  ERROR for sensitive resources

## Anti-pattern D: Audit event contains credential material (Java)

```java
// FORBIDDEN: the audit event includes the principal's
// Authorization header. Logs become a credential reservoir.
@Aspect
public class AuthzAuditAspect_BAD {

    @AfterReturning(
        pointcut = "execution(* PolicyPoint.decide(..))",
        returning = "decision"
    )
    public void emitAudit(JoinPoint joinPoint, Decision decision) {
        HttpServletRequest request = ((ServletRequestAttributes)
            RequestContextHolder.currentRequestAttributes()).getRequest();

        logger.info(Map.of(
            "event", "authz_decision",
            "decision", decision.toString(),
            "authorization_header", request.getHeader("Authorization"),  // CREDENTIAL
            "session_cookie", request.getSession().getId(),  // CREDENTIAL
            "request_body", readBody(request)  // POTENTIAL PAYLOAD
        ));
    }
}
```

Why this violates authorization.audit-events-on-decisions (and logging.no-sensitive-data-in-logs):
- Credential material in audit events makes logs a privileged-
  access source
- Logs persist longer than sessions; replayed credentials
  attack window extended
- The substrate-required redaction processor (logging.no-sensitive-data-in-logs)
  would strip these fields, but the pattern actively adds
  them; the substrate's L2-006 finding includes "audit
  events must not contain credential material"

## Anti-pattern E: Bulk operation produces one event (Python)

```python
# FORBIDDEN: bulk endpoint emits a single audit event for
# the whole batch. Per-decision accountability lost.
@app.post("/resources/batch")
def batch_BAD(payload):
    principal = current_principal()
    allowed_ids = []
    for resource_id in payload.ids:
        decision = engine.decide(principal, "read", "resource", resource_id)
        if decision.allow:
            allowed_ids.append(resource_id)

    # ONE event for the whole batch
    logger.info(
        "authz_batch_decision",
        principal=principal.subject_id,
        action="read",
        resource_type="resource",
        decision="batch_processed",
        count_requested=len(payload.ids),
        count_allowed=len(allowed_ids),
        # Which specific IDs were denied? Not captured.
    )

    return jsonify([Resource.get(i).to_dict() for i in allowed_ids])
```

Why this violates authorization.audit-events-on-decisions:
- The substrate requires per-decision events
- Investigation of "did the attacker enumerate resource X"
  cannot be answered from "batch processed 50 items, 30
  allowed"
- The substrate-recommended pattern is N events with a shared
  correlation_id (the request's correlation ID); batch
  size becomes a downstream aggregation, not a primary event

## Anti-pattern F: Principal identity from request body (Node.js)

```javascript
// FORBIDDEN: the audit event records the principal from the
// request body. An attacker spoofs the user_id field.
function decide_BAD(req, action, resourceType, resourceId) {
  const decision = engine.decide(req.body.user_id, action, resourceType, resourceId);
  logger.warn({
    event: "authz_decision",
    principal: req.body.user_id,  // CLIENT-SUPPLIED
    action,
    resourceType,
    resourceId,
    decision: decision.allow ? "allow" : "deny",
  });
  return decision;
}
```

Why this violates authorization.audit-events-on-decisions:
- The audit event records what the attacker said, not who
  was authenticated
- Forensic value of the log is zero: every audit event
  truthfully records the attacker's claimed identity, which
  is whatever they chose
- Substrate requires principal identity from authoritative
  session (Pattern E in the paired good-example file)
