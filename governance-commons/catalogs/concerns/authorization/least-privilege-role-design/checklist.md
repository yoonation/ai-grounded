---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.least-privilege-role-design-least-privilege-role-design"
title: "authorization.least-privilege-role-design review checklist: least-privilege role design"
substrate-rule: "authorization.least-privilege-role-design"
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
  - "Pull requests that add or expand a role definition"
  - "Pull requests that grant a new permission to an existing role"
  - "Quarterly role-and-permission audit (substrate-recommended cadence)"
  - "Onboarding of a new user population or persona that requires new role design"
---

# authorization.least-privilege-role-design review checklist: least-privilege role design

## How to use this binding

Two review modes are intended: per-pull-request review when a
change touches role or permission definitions, and quarterly
periodic audit. Both modes use the questions below; quarterly
audits add the per-role inventory step. Unanswered items block
merge or close the audit cycle.

## Review questions

### 1. Purpose statement: does the role have a clear, single-sentence description?

Each role exists to serve a job function. The role's definition
or accompanying documentation states that purpose in one
sentence. Roles without a purpose statement are likely accreted
aggregations that began with a clear purpose and drifted as
permissions were added over time.

What good looks like: role definition file or doc page contains
a one-sentence purpose statement directly adjacent to the role
declaration.

What needs follow-up: role exists with no documented purpose;
purpose statement is multi-paragraph (indicates the role
serves multiple functions and should be decomposed); purpose
statement was added retroactively to cover whatever the role
already grants.

### 2. Permission justification: for each new permission grant, is the rationale documented?

A new permission grant to an existing role requires reviewer
agreement that the permission is needed for the role's purpose.
The PR description or commit message states why this permission
belongs to this role.

What good looks like: PR description explicitly addresses the
fit between the new permission and the role's purpose; the
rationale references the user-facing capability or operational
need being enabled.

What needs follow-up: PR description says "add permission X to
role Y" without rationale; the rationale is "the customer
asked"; the rationale is "this is how the previous role worked"
(replicating a legacy mistake).

### 3. Permission scope: is the permission granted at the narrowest scope that serves the purpose?

A permission "read all users" granted to a role that only needs
"read users in the role's department" is over-broad. Narrowed
permissions reduce blast radius if the role is later assigned
too widely or if a principal in the role is compromised.

What good looks like: the granted permission is the narrowest
form available; broader-scope grants explicitly justify why
narrowing was infeasible (the policy engine cannot express the
narrow form, the resource model does not support the scope).

What needs follow-up: the permission is the broadest form
available "because that's what the API exposes"; the
permission name does not indicate scope and the actual scope
is implicit in the application code.

### 4. Bindable-field cross-check (authorization.mass-assignment-allowlist): does the permission's scope include any mass-assignable fields?

If the permission allows modifying object fields, are those
fields appropriately controlled by the allowlist pattern from
authorization.mass-assignment-allowlist? A permission that grants writability to a field
also bindable from a request creates an escalation path: the
principal can modify the field directly via the API.

What good looks like: bindable-field controls reviewed in the
same PR; no permission grants writability to a sensitive
field without explicit allowlist alignment; the role's
permissions and the allowlist are cross-referenced in
documentation.

What needs follow-up: the permission grants write access to a
field that is mass-assignable from request bodies without an
explicit allowlist; the role grants admin-level writability
that bypasses the allowlist entirely.

### 5. Per-role permission inventory (quarterly audit): what does each role grant in practice?

For each role in production, list every permission the role
grants. Compare against the role's purpose statement. Flag
permissions that no longer align.

What good looks like: an audit report (markdown, spreadsheet,
or generated from the policy engine) listing each role's
current permission set with alignment annotations.

What needs follow-up: no audit cadence exists; the audit
exists but is not reviewed by anyone with authority to remove
permissions; permissions are listed but the role's purpose is
not included for comparison.

### 6. Privilege creep (quarterly audit): which permissions were added since last audit?

For each role, list permissions added since the prior audit
cycle. For each, confirm the justification still holds. Flag
accreted permissions for re-justification or removal.

What good looks like: per-role delta report; explicit decision
(keep / remove / narrow) on each delta; deltas are linked back
to the PRs that introduced them.

What needs follow-up: deltas exist but justifications were not
recorded at grant time, making re-evaluation impossible; the
audit cycle finds dozens of additions per quarter without
remediation; the audit always concludes "keep" without
analysis.

### 7. Permission-overlap analysis (quarterly audit): do multiple roles grant the same permission?

When multiple roles grant the same permission for different
reasons, role consolidation may be warranted, or the
permission may indicate a missing primitive that several
roles need (suggesting a refined permission boundary).

What good looks like: overlap matrix from the audit report;
explicit decisions on consolidation or refinement; the matrix
is reviewed for both unintentional overlap (the same
permission accidentally granted twice) and intentional overlap
(two roles legitimately need the same permission).

What needs follow-up: overlaps exist but are not surfaced;
overlaps are surfaced but the resolution defaults to "keep
both" without analysis.

### 8. Audit-log usage analysis (quarterly audit): which permissions are actually used?

Unused permissions are candidates for removal regardless of
their original justification. Audit logs (per authorization.audit-events-on-decisions)
show which permissions were exercised by which principals.

What good looks like: audit log query against the past audit
cycle showing per-permission usage counts; zero-usage
permissions flagged for review; long-term zero-usage
permissions removed in the next cycle.

What needs follow-up: audit logs do not include sufficient
detail to determine which permission authorized which
action; the usage data is collected but never reviewed for
removal opportunities.

## Reviewer attestation

When all eight questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review or quarterly audit report:

```
authorization.least-privilege-role-design review checklist: complete
- Purpose statement: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Permission justification: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Permission scope: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Bindable-field cross-check: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Per-role inventory: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Privilege creep: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Permission overlap: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Audit-log usage: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or close the audit cycle. EXEMPT
items require documented rationale in the pull-request thread
or the audit report.

## Cross-reference

- Substrate rule: authorization.least-privilege-role-design in catalogs/concerns/authorization.oscal.yaml
- Related rule: authorization.step-up-and-audit-for-privilege-changes (re-assignment as a privilege-change operation)
- Related rule: authorization.audit-events-on-decisions (audit events surface unused permissions)
- Related rule: authorization.mass-assignment-allowlist (mass assignment allowlist)
- Test binding: test-template.md
- Good examples: examples/authorization/least-privilege-role-design-good.md
- Anti-patterns: examples/authorization/least-privilege-role-design-anti-pattern.md
- NIST SP 800-53 AC-6 Least Privilege
