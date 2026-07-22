---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.step-up-and-audit-for-privilege-changes-step-up-and-audit-for-privilege-changes"
title: "authorization.step-up-and-audit-for-privilege-changes review checklist: step-up and audit for privilege changes"
substrate-rule: "authorization.step-up-and-audit-for-privilege-changes"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-22"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove privilege-changing operations (grant role, revoke role, modify permissions)"
  - "Code changes that add, modify, or remove impersonation or assume-identity operations"
  - "Code changes that add, modify, or remove tenant-switching operations"
  - "Code changes that modify the policy itself when policy is data"
---

# authorization.step-up-and-audit-for-privilege-changes review checklist: step-up and audit for privilege changes

## How to use this binding

Reviewers answer every question below when reviewing pull
requests that match the triggers. Unanswered items block
merge. The questions cover both the operation's authorization
construct and the surrounding controls (step-up authentication,
audit emission, rate limiting, approval workflows).

Privilege-changing operations are the canonical attacker
target after initial account compromise. The defenses are
friction (step-up), detection (audit), and bounding (rate
limit). This rule pairs with authentication.mfa-on-privileged-operations from the
authentication catalog: authentication.mfa-on-privileged-operations covers the authenticator
requirement, this rule covers the audit-event and approval-
workflow requirements.

## Review questions

### 1. Operation identification: is the operation privilege-changing?

For the change under review, identify which operations shift
the principal's effective privileges or allow the principal to
act with another principal's privileges. Common privilege-
changing operations: grant or revoke a role, add or remove a
permission, create an account with elevated privileges, change
a user's role, impersonate another user (support tooling),
switch effective tenant in multi-tenant systems, modify the
policy itself when policy is data, set a user as the resource
owner.

What good looks like: the inventory is explicit; the operations
are tagged in code or documentation as privilege-changing; the
PR description acknowledges the classification.

What needs follow-up: the operation looks like a routine
update but has privilege-changing effects (an "edit user"
flow that includes a role field; a "create resource" flow
that allows specifying the owner); the classification is
implicit in the code's location rather than declared.

### 2. Step-up authentication: is fresh strong-factor auth required?

The operation requires a step-up authentication challenge.
Step-up means re-authentication with a strong factor (per
authentication.mfa-on-privileged-operations), not just confirmation that the standing session
is authenticated.

What good looks like: the operation calls the framework's
step-up construct (Django's reauth-required decorator,
Rails-style sudo mode, custom step-up middleware) before the
operation executes; expired step-up tokens reject the
operation; step-up requires the same MFA factor required for
the original session or stronger.

What needs follow-up: the operation runs on the standing
session; the step-up is a UI prompt that does not actually
constrain the server; the step-up token has no expiration and
is effectively a session upgrade.

### 3. Audit event emission: is the operation logged with full context?

The operation emits a structured audit event recording the
actor, the target, the change, and the authorizing policy
entry. The event flows through the application's standard
audit pipeline (per authorization.audit-events-on-decisions).

What good looks like: the audit event is emitted from the
operation's success path and from the failure path; the event
includes actor principal, target principal (if different),
the privilege change (role granted, permission added, user
impersonated, tenant switched), and the policy entry that
authorized the change.

What needs follow-up: the audit event is missing; the event
is emitted only for some operations (grant but not revoke);
the event lacks fields needed for forensic investigation (no
policy entry, no correlation ID, no actor disambiguation
when impersonation is in play).

### 4. Rate limiting: are privilege-change operations bounded in frequency?

The operation is bound in frequency per the authentication
catalog's rate limiting rules (authentication.rate-limiting) plus authorization-
specific limits for sensitive operations. Privilege-change
operations are typically much rarer than ordinary operations
and warrant stricter limits.

What good looks like: privilege-changing operations have
explicit rate limits, often stricter than ordinary operations
(5 per hour per actor, not the global 60 per minute); rate-
limit violations emit audit events.

What needs follow-up: no rate limit on privilege-changing
operations; the rate limit is the same as ordinary
operations; rate-limit violations are silent.

### 5. Approval workflow: is a second principal required for high-consequence changes?

For high-consequence privilege changes (granting administrative
privileges in production environments, impersonating users
with sensitive data access), a second-principal approval
workflow runs.

What good looks like: the high-consequence operations require
approval from a second principal; the approving principal also
undergoes step-up; the approval is bound to the specific
operation (approving "grant X to Y on 2026-05-22" is not
approval for any other operation); the approval expires if
not exercised.

What needs follow-up: no approval workflow; approval is
implicit (the second principal does not have to act, their
approval is recorded silently); approval is bound to a class
of operations rather than the specific operation; the approval
chain is recorded but not verifiable post hoc.

### 6. Impersonation: is the operator identity preserved in audit?

When the operation supports impersonation (assume-identity,
support tooling), the audit events distinguish the operator
from the impersonated user.

What good looks like: audit event fields include both the
operator (actor) and the impersonated identity (impersonated-
as or on-behalf-of); the events are searchable by either
field; the impersonation is bounded (time-limited session,
specific scope).

What needs follow-up: the impersonation makes the operator's
identity invisible (the audit shows the impersonated user
took the action); the impersonation session has no time
bound; the impersonation has no scope constraint and grants
full operator capability under the impersonated identity.

### 7. Tenant switching: is it gated by explicit operator-mode?

For multi-tenant systems with tenant-switching operations,
the switch requires operator-mode authorization (cross-tenant
access per authorization.multi-tenant-data-layer-isolation exception path).

What good looks like: tenant-switching is a distinct operator-
mode capability; it requires step-up; it emits audit events
identifying the operator and the tenant switched into; it is
rate-limited; cross-tenant data access during the switched
session is logged with operator identity preserved.

What needs follow-up: tenant-switching is implicit in the
admin role; cross-tenant access happens silently; no audit
trail tracks operator activity across tenants.

### 8. Policy-as-data: do data-layer policy changes get the same controls?

When the policy itself is data (policy entries stored in a
database, modifiable via admin UI), changes to the policy
are themselves privilege-changing operations and trigger the
same controls.

What good looks like: policy changes require step-up; emit
audit events; are rate-limited; have approval workflow for
high-consequence changes (adding a new role, broadening a
permission scope); the policy-change pipeline is treated as
a privilege-changing surface.

What needs follow-up: policy-as-data is changed without the
controls because "it is just data"; policy changes are not
audit-logged; the policy-change UI is privileged but has no
step-up.

### 9. Revocation: are revoke operations as controlled as grants?

Revoking a privilege has the same controls as granting one.
Revocation is often under-controlled because "taking away"
seems lower-risk than "giving."

What good looks like: revoke operations require step-up,
emit audit events, are rate-limited. Revocation can be
attacker-useful (lock out the legitimate admin while attacker
retains access); the controls treat it with the same care as
grants.

What needs follow-up: revoke operations are exempt from the
controls because "they reduce privilege"; mass revocation
operations exist without controls; revocation does not emit
audit events.

### 10. Self-grant prohibition: can a principal grant themselves a privilege?

The operation prohibits self-grant: a principal cannot grant
themselves a privilege they do not already have.

What good looks like: the policy explicitly rejects self-
grants of new privileges; the audit events flag attempted
self-grants; the operator-tooling UX makes self-grants
impossible or requires a second principal's approval.

What needs follow-up: a principal with grant capability can
grant themselves any privilege; the only constraint is the
principal's grant scope (which may include all privileges);
the system has no concept of self-grant prohibition.

## Reviewer attestation

When all ten questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review:

```
authorization.step-up-and-audit-for-privilege-changes review checklist: complete
- Operation identification: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Step-up authentication: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Audit event emission: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Rate limiting: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Approval workflow: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Impersonation identity: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Tenant switching: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Policy-as-data controls: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Revocation parity: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Self-grant prohibition: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge until resolved. EXEMPT items
require documented rationale in the pull-request thread.

## Cross-reference

- Substrate rule: authorization.step-up-and-audit-for-privilege-changes in catalogs/concerns/authorization.oscal.yaml
- Paired authentication rule: authentication.mfa-on-privileged-operations (MFA on privileged operations)
- Related rule: authentication.rate-limiting (rate limiting on authentication endpoints)
- Related rule: authorization.audit-events-on-decisions (audit events on authorization decisions)
- Related rule: authorization.multi-tenant-data-layer-isolation (multi-tenant data layer isolation)
- Test binding: test-template.md
- Good examples: examples/authorization/step-up-and-audit-for-privilege-changes-good.md
- Anti-patterns: examples/authorization/step-up-and-audit-for-privilege-changes-anti-pattern.md
- OWASP ASVS v5.0.0 V8.4.3
- NIST SP 800-53 AC-3(7) Role-Based Access Control and AU-2 Event Logging
