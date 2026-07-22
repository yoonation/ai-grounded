<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authorization.authorization-model-selection authorization model selection (forbidden patterns)

Substrate-original anti-patterns for the L3 model selection
ADR. Each anti-pattern shows what a reviewer applying the
authorization.authorization-model-selection review checklist would reject.

## Anti-pattern A: No ADR exists

```
$ ls /docs/decisions/
ADR-001-language-choice.md
ADR-002-database-choice.md
ADR-003-deployment-platform.md
ADR-004-logging-stack.md
ADR-005-authentication-strategy.md
ADR-006-secrets-management.md

# No authorization model ADR. The application has shipped
# authorization code without explicit model choice
# documentation.
```

Why this violates authorization.authorization-model-selection:
- The substrate's L3 rule requires the ADR to exist before
  substantive authorization implementation begins
- "We did it implicitly" is the substrate's most-common
  L3-001 finding: the model was chosen by accumulation of
  individual code decisions rather than deliberate analysis
- The L3 review checklist's question 1 ("does the ADR
  exist") fails

## Anti-pattern B: ADR exists but has missing sections

```markdown
<!-- /docs/decisions/ADR-007-authorization-model.md -->

# ADR-007: Authorization Model

We will use RBAC.

That's it.
```

Why this violates authorization.authorization-model-selection:
- No Context section explaining application drivers
- No Considered Options enumeration
- No Decision Outcome reasoning
- No Consequences section
- No Substrate Alignment statement
- No Review Schedule
- The substrate's L3 review checklist questions 2-9 all
  fail

## Anti-pattern C: ADR contradicts the running implementation

```markdown
<!-- /docs/decisions/ADR-007-authorization-model.md -->

# ADR-007: Authorization Model

## Status
Accepted (2024-01-15)

## Decision
We will use RBAC implemented via Pundit policy classes
with a fixed catalog of three roles: admin, editor,
viewer.
```

```python
# But the actual implementation:
# app/authz.py
def can_perform(user, action, resource):
    # Authorization based on user.department, user.region,
    # resource.classification, and time of day.
    # Pundit not used.
    if user.department == "legal" and resource.classification == "contract":
        return action in ["read", "edit", "approve"]
    if user.region == "EU" and is_business_hours_eu():
        return ...
```

Why this violates authorization.authorization-model-selection:
- The ADR says RBAC + Pundit; the code uses ABAC-style
  conditions and no Pundit
- The substrate-required property is that the ADR matches
  reality
- An ADR that no longer describes the system is worse than
  no ADR because it actively misleads reviewers
- The substrate-required response is to update the ADR
  (Status: Superseded by ADR-NNN) and write a new ADR

## Anti-pattern D: RBAC chosen for application with graph-shaped access

```markdown
<!-- /docs/decisions/ADR-007-authorization-model.md -->

# ADR-007: Authorization Model

## Status
Accepted (2026-01-15)

## Decision
We will use RBAC.

## Reasoning
RBAC is the substrate's preferred default.
```

```
# Application context: a file-sharing application where
# files can be shared with users, with groups, with anyone
# via a link. Files inherit access from folders. The
# application has 50 million files and 5 million users.
```

Why this violates authorization.authorization-model-selection:
- The ADR exists but ignores the application's actual
  resource model
- The substrate's decision-framework explicitly identifies
  file sharing as the canonical ReBAC use case (D5 in the
  framework)
- The substrate's L3 review checklist question 5 ("does
  the decision align with substrate-preferred options for
  the application context") fails: the substrate prefers
  ReBAC for this context, and RBAC was chosen without
  justification
- The ADR cites the substrate's RBAC preference without
  noting the substrate's qualification ("when the
  application's resource model or user population clearly
  requires another model")
- Substrate-required: either choose ReBAC, or document
  explicitly why RBAC's role-explosion overhead is
  acceptable for this application context

## Anti-pattern E: ADR has Status="Proposed" indefinitely

```markdown
<!-- /docs/decisions/ADR-007-authorization-model.md -->

# ADR-007: Authorization Model

## Status
Proposed (drafted 2024-01-15)

## Decision Drivers
[Comprehensive analysis follows]

## Decision Outcome
We propose Option 4 (Hybrid).

## Status notes
[2024-01-15] Initial draft
[2024-03-20] Discussed; awaiting security review
[2024-07-11] Awaiting platform team input
[2024-12-15] Status check; still proposed
[2025-06-20] Application now in production
[2026-04-22] Still proposed; awaiting consensus
```

Why this violates authorization.authorization-model-selection:
- The application is in production; the ADR is still
  "Proposed"
- An indefinitely-proposed ADR means no decision has been
  made; the application accreted authorization code with
  no documented model
- Substrate-required: an ADR for a shipped feature must be
  in Accepted, Deprecated, or Superseded status
- The L3 review checklist's question 1 distinguishes "ADR
  exists with appropriate status" from "ADR exists as a
  draft document"; this anti-pattern fails the appropriate-
  status check

## Anti-pattern F: ADR lists no Considered Options

```markdown
<!-- /docs/decisions/ADR-007-authorization-model.md -->

# ADR-007: Authorization Model

## Status
Accepted

## Decision
We will use Cedar.

## Reasoning
The team has Cedar experience from the previous project
and it should work fine here too.
```

Why this violates authorization.authorization-model-selection:
- The ADR chose an engine (Cedar) but not a model (Cedar
  supports both RBAC and ABAC)
- No Considered Options enumeration; reviewers cannot tell
  whether ReBAC was considered and excluded, or simply
  not considered
- "Should work fine" is not analysis; the substrate's
  L3 review checklist question 4 ("are options
  comparatively analyzed") fails
- The ADR sidesteps the model choice by anchoring on the
  engine; the substrate's framework treats engine choice
  as a subordinate decision driven by model choice
