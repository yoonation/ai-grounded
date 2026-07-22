<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: authorization.authorization-model-selection authorization model selection (good ADR)

Substrate-original example showing a well-formed consumer ADR
adapting decision-frameworks.authorization-model-selection to
a hypothetical application. The example shows what a reviewer
applying the authorization.authorization-model-selection review checklist would see as a
passing artifact.

## Example consumer ADR

The following content represents a fictional consumer's ADR
file at `/docs/decisions/ADR-007-authorization-model.md`.

```markdown
# ADR-007: Authorization Model

## Status
Accepted (2026-04-12). Reviewed annually; next review
2027-04-12.

## Deciders
- Application Engineering Lead
- Security Architect
- Platform Operations Lead

## Context and Problem Statement

ContractFlow is a B2B SaaS for contract lifecycle management
serving 200+ enterprise tenants. The application stores
contracts, attachments, and metadata; users within a tenant
collaborate on contracts via comments, approval workflows,
and shared signing flows. Enterprise customers require
data isolation between tenants, granular role separation
within their organization (legal team, finance team,
executives), and audit trails sufficient for SOC 2 Type 2.

This ADR documents the foundational authorization model
choice for ContractFlow per substrate rule authorization.authorization-model-selection.
The substrate's decision-frameworks.authorization-model-
selection provides the analysis framework adapted here.

The choice affects every subsequent authorization
implementation decision: which substrate L2 rules apply
with what nuances, which policy engine fits, what
operational mechanisms are required for grants and
attribute provisioning.

## Decision Drivers

The substrate's drivers D1-D9 applied to ContractFlow:

D1. Resource model shape: hybrid. Within a tenant, contracts
form a flat collection (most contracts are independent
documents). However, sharing relationships are present:
contracts can be shared with specific named users outside
the contract's owning team, and approval workflows create
relationships between contract and approver.

D2. User population structure: clear job functions per
tenant (Lawyer, Paralegal, Finance Reviewer, Executive,
Admin) but the same person may hold different roles in
different tenants (e.g., a fractional general counsel
serves multiple tenants with different roles).

D3. Permission change cadence: slow. Role-to-permission
mappings change at quarterly cadence based on customer
feedback and SOC 2 audit findings.

D4. Per-request context dependence: present but bounded.
Approval workflows require time-of-day restrictions for
some enterprise tenants (no approvals outside business
hours per their internal policy). Document classification
levels (Confidential, Restricted, Public) affect access.

D5. Relationship-driven access: present. "Document shared
with Alice" must propagate via the share relationship.
Approval workflows are inherently graph-shaped.

D6. Operational maturity: medium. Team has policy-authoring
experience from a prior product but no ReBAC experience.

D7. Engine availability: Cedar (preferred for AWS-native
deployment), OPA (organizational standard), Pundit
(application is Rails).

D8. Audit and reasoning requirements: high. SOC 2 Type 2
requires "denied access" reasoning traceable to specific
policy rules.

D9. Time to first authorized request: 8 weeks from this
decision to authorization layer in production for the
new contract approval feature.

## Considered Options

- **Option 1 (RBAC)**: substrate-preferred default.
  Applicable for the role-driven access (Lawyer, Paralegal,
  etc.).
- **Option 2 (ABAC)**: substrate-preferred for context-
  dependent access (time-of-day, classification level).
- **Option 3 (ReBAC)**: substrate-preferred for sharing
  and approval relationships.
- **Option 4 (Hybrid)**: substrate-acceptable. Combines
  the above.
- **Option 5 (Minimal)**: excluded; ContractFlow's
  authorization surface is significant.

## Decision Outcome

**Chosen option**: Option 4 (Hybrid) with RBAC + ABAC via
Cedar as the primary model, plus a documented ReBAC-style
sharing extension implemented in application code (not in
the Cedar engine, due to team's lack of ReBAC experience
per D6 and time pressure per D9).

### Substrate Alignment

The choice aligns with substrate-preferred options for the
application context. ContractFlow's resource and user
structure clearly calls for both role and attribute
discrimination (substrate prefers Hybrid over single-model
when the application has distinct concern domains). The
deviation from pure ReBAC for relationship-driven access
is justified by D6 (operational maturity) and D9 (time to
production); the team accepts the trade-off of less
elegant relationship modeling in exchange for shipping a
production-ready authorization layer within 8 weeks.

### Rationale

- Roles (Lawyer, Paralegal, etc.) are stable per-tenant
  (D2, D3). RBAC fits.
- Context-dependent access (time-of-day, classification)
  cannot be expressed in pure RBAC without role explosion.
  ABAC via Cedar attribute conditions fits.
- Sharing and approval relationships are graph-shaped but
  the graph depth is bounded (sharing is one-hop;
  approvals are a small chain). The team can implement
  this in application code with explicit share-record
  lookups, accepting that pure ReBAC would express it
  more elegantly.
- Cedar supports RBAC and ABAC natively, is AWS-aligned
  (D7), and produces traceable decisions (D8) satisfying
  SOC 2 requirements.

## Consequences

### Positive

- Cedar policy files capture the authorization vocabulary
  in a form security and compliance reviewers can audit
- Cross-tenant role differences (D2) handled by per-tenant
  policy instances
- Context-dependent restrictions (business-hours approvals,
  classification access) expressible without role explosion
- Decisions are traceable per SOC 2 requirement (D8)

### Negative

- Hybrid composition adds operational surface: two
  authorization mechanisms (Cedar + application sharing
  records) to maintain
- Sharing record updates must invalidate any caching
  separately from role grant changes
- The team commits to revisiting the ReBAC question if
  approval workflows become deeper than two levels or if
  sharing patterns expand beyond direct one-hop sharing

### Substrate Rules in Scope

The chosen model brings the following substrate L2 rules
into scope; the team has tickets for each:

- authorization.object-level-authorization: object-level authorization (every
  contract, attachment, comment)
- authorization.least-privilege-role-design: least-privilege role design (Cedar
  role catalog as data; quarterly review)
- authorization.step-up-and-audit-for-privilege-changes: step-up for privilege changes
  (role grants and ownership transfers)
- authorization.multi-tenant-data-layer-isolation: multi-tenant data-layer isolation
  (PostgreSQL RLS per tenant, plus Cedar tenant
  context as defense-in-depth)
- authorization.centralized-deny-by-default-policy: centralized deny-by-default policy
  (Cedar engine is the single policy point)
- authorization.audit-events-on-decisions: audit events on decisions (Cedar
  emission integrated with logging stack; SOC 2
  audit consumes)

### Engine and Library Choices

- Authorization engine: Cedar (AWS-aligned per D7)
- Sharing records: PostgreSQL table with explicit
  application code consulting Cedar for tenant + role,
  then consulting sharing records for grants
- Database: PostgreSQL with RLS for tenant isolation
- Audit: structlog with JSON output to OpenSearch (per
  decision-frameworks.logging-architecture)

## Pros and Cons of the Options

### Option 1 (RBAC) only
- Pro: simplest implementation; matches D3 (slow change)
- Con: fails D4 (context-dependent restrictions) without
  role explosion; sharing (D5) impossible to express
- Why rejected: insufficient for ContractFlow's actual
  access patterns

### Option 2 (ABAC) only
- Pro: handles D4 elegantly
- Con: roles can be expressed as attributes but the team
  loses the role catalog as a SOC 2 reviewable artifact
  (D8 implications); pure ABAC for sharing is awkward
- Why rejected: Hybrid retains RBAC's role catalog while
  adding ABAC where needed

### Option 3 (ReBAC) only
- Pro: handles D5 natively
- Con: D6 (no team experience) and D9 (time pressure)
  make adoption risky; OpenFGA or SpiceDB would be the
  engine choice with steep learning curve
- Why rejected: deferred to a future review when team
  experience matures

### Option 5 (Minimal)
- Pro: shortest time to first authorized request
- Con: SOC 2 cannot be achieved with minimal model;
  customer requirements not met
- Why rejected at outset

## References

- Substrate rule authorization.authorization-model-selection in catalogs/concerns/authorization.oscal.yaml
- Substrate framework decision-frameworks.authorization-model-selection
- Cedar policy engine documentation (AWS)
- SOC 2 Type 2 control mappings (internal compliance doc)
- ContractFlow threat model (internal)
- Prior ADR-005 authentication strategy (this ADR is
  independent but referenced)

## Decision Review Schedule

- Next scheduled review: 2027-04-12
- Earlier review triggered by:
  - Approval workflow expanding beyond two-level chains
  - Sharing patterns expanding beyond one-hop direct
    sharing
  - New customer tenant requiring access patterns this
    model cannot express
  - SOC 2 audit finding affecting authorization
  - Material security incident affecting authorization
```

## Why this ADR satisfies authorization.authorization-model-selection

The authorization.authorization-model-selection review checklist asks:

- **Status documented**: Yes, "Accepted (2026-04-12)" with
  review schedule
- **Context covers substrate drivers D1-D9**: Yes, every
  driver addressed with application-specific reasoning
- **Considered options**: Yes, all five options addressed,
  with reasons for excluding three
- **Decision outcome with reasoning**: Yes, the rationale
  references the decision drivers explicitly
- **Substrate alignment statement**: Yes, includes
  acknowledgment of the substrate-preferred pure-ReBAC for
  D5 and justifies the deviation
- **Consequences (positive, negative, substrate rules in
  scope)**: Yes, comprehensive
- **Pros and cons of each option**: Yes, option-comparative
- **References**: Yes, substrate rule, framework, internal
  documents, and external engine documentation
- **Review schedule**: Yes, annual with explicit triggers
  for earlier review

The ADR is substantive (not a checkbox exercise), specific
to the application (not boilerplate), and explicit about
trade-offs the team consciously made.
