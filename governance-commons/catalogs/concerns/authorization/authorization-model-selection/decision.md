---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: authorization.authorization-model-selection
title: "Authorization Model Selection"
lifecycle-status: stable
commons-version: "0.5.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-22"
entered-status-at: "2026-05-26"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention. Promoted to stable at M2 close consolidation (Path A precedent) on 2026-05-26 alongside the four other M2 draft MADRs and the five M2 draft catalogs they pair with."
ai-assistance: "AI drafted from substrate-author intent. Pairs with authorization.authorization-model-selection substrate rule; mirrors the auth-strategy.madr.md precedent for L3-as-pre-build-gate. Draft lifecycle per M2 Session 1; promotion to stable deferred to M2 close per Path A precedent established at M1 close."
authoritative-sources:
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md"
  - "https://csrc.nist.gov/publications/detail/sp/800-162/final"
  - "https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home"
  - "https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.auth-strategy
---

# Authorization Model Selection

This decision framework provides the substrate's analysis of
authorization model options. Consumers reference this framework
when authoring their own ADR documenting their application's
authorization model choice (substrate-recommended location for
the consumer's ADR:
`/docs/decisions/ADR-XXX-authorization-model.md`).

The framework is referenced by substrate rule authorization.authorization-model-selection,
which requires applications to have an explicit, documented
authorization model decision before substantive authorization
implementation begins. Consumers satisfy authorization.authorization-model-selection by
authoring an ADR that adapts the analysis in this framework to
their application context.

This framework is the authorization counterpart to
decision-frameworks.auth-strategy. The authentication strategy
choice and the authorization model choice are independent
decisions; an application authors both ADRs as pre-build gates
for their respective concern domains.

## Context

Authorization model selection is the foundational structural
choice that determines how the application encodes "who can do
what to which resources under what conditions". The choice
propagates through every authorization code path, every policy
artifact, every audit event, and every administrative workflow
for the application's lifetime. Unlike most engineering
decisions, the model choice cannot be compensated for downstream
by perfect implementation of individual L1 or L2 rules. A system
designed around RBAC cannot easily express ABAC's attribute-
based policies; a system designed around ReBAC cannot easily
flatten back to RBAC's role grants.

The wrong-model failure mode is consistent across applications:
authorization code that fights the chosen model accretes
complexity. RBAC encoding of attribute-based requirements
produces explosive role proliferation (one role per attribute
combination, dozens of near-duplicate role names). ABAC
encoding of simple role-based requirements produces policy
expressions that replicate what a role lookup would have
expressed in one line. ReBAC encoding of role-based access
produces relationship graphs that flatten back into roles, with
the graph machinery as pure overhead.

Making this choice without explicit analysis is a common
substrate failure mode that mirrors authentication strategy
selection. Teams default to RBAC because it is familiar; they
then encode attribute-based or relationship-based requirements
as proliferating roles, with the rule surface and operational
overhead growing beyond what the original choice accounted for.
This framework forces the choice to be deliberate.

The substrate provides analysis of each viable model but does
not prescribe a single choice. Consumers select based on their
application's resource model, user population structure, and
operational context. The substrate requires the choice to be
documented and reasoned; it does not require consumers to
choose the substrate-preferred option for their context.

## Decision Drivers

The substrate identifies the following drivers that should
inform the model choice. Consumers may add application-specific
drivers but should address each substrate driver in their ADR.

- **D1. Resource model shape.** Is the application's authorized
  resource set a flat collection of objects with consistent
  type? A hierarchy with parent-child containment? A graph of
  related objects where access flows through relationships?
  A typed set with attribute-classified resources? The shape
  determines which model fits without fighting.

- **D2. User population structure.** Are users organized into
  stable job functions with consistent permission grants? Do
  users vary in attributes that should affect access
  (department, clearance, region, employment status)? Do
  users have relationships to resources (ownership,
  collaboration, group membership) that determine access?

- **D3. Permission change cadence.** Do role-to-permission
  mappings change rarely (weeks to months between changes) or
  frequently (daily to hourly)? Slow-change applications fit
  RBAC well; fast-change applications strain RBAC's grant-
  management overhead.

- **D4. Per-request context dependence.** Do authorization
  decisions depend on per-request context that is not captured
  in static role grants (request origin, time of day,
  resource sensitivity, regulatory jurisdiction)? Context-
  heavy applications fit ABAC; static-grant-sufficient
  applications fit RBAC.

- **D5. Relationship-driven access.** Does access flow through
  relationships (file shared with a group whose member
  inherits access; document accessible to anyone the owner
  has added)? Relationship-driven access fits ReBAC; access
  expressible without relationships fits RBAC or ABAC.

- **D6. Operational maturity for the chosen model.** Each model
  has operational requirements. RBAC requires role grant and
  revocation workflows. ABAC requires attribute provisioning
  and policy authoring discipline. ReBAC requires relationship
  recording, graph maintenance, and traversal cost management.
  Operational maturity matched to the model determines whether
  the implementation will succeed.

- **D7. Engine availability and choice.** What policy engines
  are realistic for the consumer's stack? Cedar (RBAC + ABAC),
  Open Policy Agent (general-purpose, supports all models with
  effort), Casbin (RBAC + ABAC), OpenFGA / SpiceDB (ReBAC,
  Zanzibar-inspired), framework-native authorization layers
  (Pundit / Cancancan for Ruby, django-guardian for Django).
  The choice of engine constrains and is constrained by the
  model choice.

- **D8. Audit and reasoning requirements.** Can the application
  tolerate "I don't know why this decision was made" outcomes?
  Compliance-driven applications often require deny-reason
  explanation that traces to the rule that applied. RBAC and
  Cedar-style ABAC produce traceable decisions; deep ReBAC
  graphs can produce decisions whose reasoning is
  computationally clear but humanly opaque.

- **D9. Time to first authorized request.** How fast must the
  application reach a functioning authorization layer? RBAC
  with framework-native authorization is fastest. ABAC with a
  dedicated policy engine is slower but produces a more
  durable foundation. ReBAC engines have the steepest learning
  curve.

## Considered Options

### Option 1: Role-Based Access Control (RBAC)

**Substrate preference:** Substrate-preferred for applications
with stable user populations divided into clear job functions
and permissions that change rarely. Substrate-preferred default
for small to mid-sized applications without specific need for
ABAC or ReBAC.

**Applicable when:** User population divides into job functions
(admin, editor, viewer, customer-service-rep); permission
grants are stable; authorization decisions do not depend on
per-request context beyond "principal X has role Y".

**Pros:**
- Operationally well-understood; mature tooling across every
  major framework and language
- Policy is naturally expressed as a role-to-permission table
  that non-engineers can review
- Audit events naturally encode "principal in role R was
  allowed action A on resource type T"
- Substrate L1 mechanical rules (authorization.protected-route-declares-authz through L1-005)
  have direct semgrep coverage for RBAC patterns
- Framework-native authorization (Pundit, Cancancan, django-
  guardian) eliminates the engine dependency

**Cons:**
- Role proliferation when authorization requires attribute or
  context discrimination (one role per combination)
- Awkward fit for relationship-driven access (file sharing,
  collaboration); attempts to encode produce role-explosion
- Static grants make per-request context (time of day,
  request origin) impossible to express without leaving the
  model
- Permission change requires role-catalog update and
  potentially user-role regrant across the population

### Option 2: Attribute-Based Access Control (ABAC)

**Substrate preference:** Substrate-preferred for applications
where authorization depends on per-request context that cannot
be captured in static role grants.

**Applicable when:** Data-classified systems (clearance levels);
multi-jurisdiction applications (regional attributes affect
access); applications where resource sensitivity drives policy
(sensitive resources require additional attributes);
applications subject to regulatory frameworks (NIST SP 800-162,
HIPAA, data-residency requirements) that frame access in
attribute terms.

**Pros:**
- Per-request context fits naturally (attributes of principal,
  resource, environment, action all evaluate together)
- Policy expressions can be written by policy authors who are
  not application developers (Cedar policies, OPA Rego)
- Aligned with NIST SP 800-162 ABAC guidance for federated and
  regulated contexts
- Single policy can express what would be dozens of RBAC roles
- Roles can be expressed as attributes within ABAC (the
  reverse is not true), so ABAC subsumes RBAC

**Cons:**
- Policy authoring is a skill; teams without policy-engineering
  experience produce ABAC policies that are RBAC encoded in
  attribute syntax (no benefit, more complexity)
- Engine dependency (Cedar, OPA, Casbin); operational surface
  for the engine itself
- Debugging "why was this decision made" requires policy
  evaluation tracing; deeper than RBAC's "what roles does the
  principal have"
- Audit events must include the evaluated attributes for
  meaningful post-incident analysis

### Option 3: Relationship-Based Access Control (ReBAC)

**Substrate preference:** Substrate-preferred for applications
whose authorization is fundamentally graph-structured.

**Applicable when:** File sharing applications (file shared
with a user, with a group, with anyone via a link); document
collaboration (document accessible to commenters, editors,
owners with inheritance through folder hierarchy); social
applications (post visible to friends; friend-of-friend
access); supply-chain applications where access flows through
documented business relationships between organizations.

**Pros:**
- Graph-shaped access fits natively; no fighting the model
- Inheritance through relationships ("anyone with edit access
  to the folder has edit access to files inside") expressed
  naturally
- Zanzibar-inspired engines (OpenFGA, SpiceDB, AuthZed) provide
  consistent global authorization with caching designed for
  graph traversal
- Scales to large populations with sparse access patterns
  where RBAC role explosion is impractical

**Cons:**
- Steepest learning curve of the four options
- Engine dependency is heavier (Zanzibar-style engines maintain
  their own consistent data store)
- Graph traversal cost can become a performance concern at
  scale without careful schema design
- Audit and debugging require graph-aware tooling
- Misfit for applications without graph-shaped access (forcing
  ReBAC onto role-based access produces relationship machinery
  as overhead with no benefit)

### Option 4: Hybrid composition

**Substrate preference:** Substrate-acceptable with explicit
composition documentation. The substrate does not push hybrid as
the first choice; it is appropriate when the application's
authorization concerns genuinely span multiple patterns.

**Applicable when:** The application has distinct concern
domains with different authorization shapes. Common patterns:
RBAC for administrative actions plus ABAC for user-facing
attribute-classified content; RBAC for organizational
hierarchy plus ReBAC for collaborative document access.

**Pros:**
- Each concern domain uses the model that fits it
- Migration paths (e.g., starting with RBAC, adding ABAC as
  attribute-based requirements emerge) are naturally
  expressed
- Subsumes the simpler models when needed; doesn't require
  choosing a single all-or-nothing model

**Cons:**
- Operational complexity multiplies: two policy engines,
  two audit conventions, two debugging paths
- Boundary between the models must be documented and
  maintained; ambiguous-boundary cases produce inconsistent
  decisions
- Engineers must understand both patterns; the cognitive load
  is higher than for any single model
- Code review and policy review surface multiplies by
  composition factor

### Option 5: Minimal / Implicit

**Substrate preference:** Substrate-acceptable only when the
authorization surface is genuinely trivial.

**Applicable when:** The application has so few authorization
decisions that any model is operationally equivalent. Typical:
single-tenant single-user applications, internal tools with one
admin role and one user role, applications where authorization
is "is the user authenticated".

**Pros:**
- Lowest operational overhead
- No engine dependency
- Fastest time to first authorized request

**Cons:**
- Failure mode is silent: the application accretes
  authorization concerns without anyone updating the model
  choice
- The "minimal" choice often is in fact an undocumented RBAC
  with two roles; the substrate-preferred path is to document
  it as such rather than leave it undocumented

## Decision Outcome

The substrate's preferred order of consideration for new
applications:

1. **Option 1 (RBAC)** first, for applications with stable user
   populations and clear job functions
2. **Option 2 (ABAC)** for applications with per-request
   context dependence or attribute-classified resources
3. **Option 3 (ReBAC)** for applications whose authorization
   is fundamentally graph-structured (file sharing, document
   collaboration, social, supply chain)
4. **Option 4 (Hybrid)** when the application has distinct
   concern domains with genuinely different authorization
   shapes; the composition is documented explicitly
5. **Option 5 (Minimal)** only when the authorization surface
   is trivial AND the consumer commits to revisiting the
   choice when the surface grows

Consumers may choose any option that fits their context.
Choices that deviate from substrate preference for a given
context must be explicitly justified in the consumer's ADR
(see Documentation Required section).

The substrate's strong recommendation: when the choice is
between Option 1 (RBAC) and any other option, prefer RBAC
unless the application's resource model or user population
clearly requires another model. RBAC is the substrate's
default not because it is the best for every application, but
because it is the substrate-recommended starting point when
the application's structure does not clearly call for
attribute or relationship semantics.

## Pros and Cons of the Options

Detailed analysis is provided per option in the Considered
Options section above. Consumers should adapt this analysis to
their specific application context, adding application-specific
pros and cons that the substrate cannot anticipate.

When the application context aligns clearly with a substrate-
preferred option (e.g., an internal admin tool with three job
functions clearly fits Option 1), the consumer's ADR can be
relatively short, citing the substrate analysis and adding
application-specific details. When the application context
creates tension (e.g., a file-sharing application that nominally
fits Option 3 but the consumer wants to use Option 2 because
their team has policy-engineering experience but no ReBAC
experience), the ADR must address the tension explicitly and
reason through the trade-off.

The substrate-recommended rule of thumb for the migration case:
applications that start with RBAC and grow into ABAC or hybrid
have a well-trodden path. Applications that start with ReBAC and
discover they did not need it have a much harder migration
because relationship data has accreted in the database. Choose
RBAC over ReBAC when in doubt; choose RBAC over ABAC when role
discrimination is sufficient for the current scope.

## Documentation Required

Consumers using this framework satisfy authorization.authorization-model-selection by producing
an ADR in their application that addresses each of the
following. The consumer's ADR location is substrate-recommended
at `/docs/decisions/ADR-XXX-authorization-model.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: application-specific
  context covering resource model shape (D1), user population
  structure (D2), permission change cadence (D3), context
  dependence (D4), relationship-driven access (D5), and
  operational maturity (D6)
- **Decision Drivers**: the substrate's drivers (D1-D9 above)
  adapted to the application's specific context, plus any
  application-specific drivers the substrate cannot anticipate
- **Considered Options**: at least the substrate options that
  are plausibly applicable to the application; consumers may
  exclude options with brief reasoning (e.g., "Option 3
  (ReBAC) excluded: resource model is a flat list of records,
  not a graph")
- **Decision Outcome**: the chosen option with reasoning that
  references the decision drivers and the application's
  resource and user structures
- **Substrate Alignment**: explicit statement of whether the
  choice aligns with substrate-preferred options for the
  application context; deviations must be justified
- **Consequences**: positive consequences (which authorization
  shapes are handled well), negative consequences (which
  shapes require workarounds), and required follow-up work
  (inventory of substrate rules in scope given the chosen
  model, identification of policy engine or framework
  authorization layer, identification of operational
  mechanisms for grant or attribute provisioning)
- **Pros and Cons of Each Option**: option-comparative analysis
  showing why the chosen option was preferred over the
  rejected options
- **References**: authorization.authorization-model-selection substrate rule, related
  substrate rules in scope (typically authorization.protected-route-declares-authz through
  L1-005 and authorization.object-level-authorization through L2-006), application-
  specific references (threat models, regulatory
  documentation, prior ADRs including the application's
  authentication.authentication-strategy authentication strategy ADR)
- **Decision Review Schedule**: next scheduled review date
  (substrate-recommended annually) and triggers that force
  earlier review (regulatory change, material change in
  resource model or user population, security incident
  affecting authorization, addition of new concern domain
  with different authorization shape)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR. Consumers can self-review against the checklist
before submitting their ADR for acceptance.

## More Information

This framework is referenced by:

- **authorization.authorization-model-selection** (substrate rule): the rule that requires
  consumers to author an authorization model selection ADR.
- **authorization.object-level-authorization through authorization.audit-events-on-decisions** (semantic rules): apply
  to most authorization models; the consumer's ADR enumerates
  which apply given the chosen model.
- the authorization mechanical (L1) rules (mechanical rules):
  apply to all authorization implementations regardless of
  model; static analysis catches the patterns these rules
  govern across RBAC, ABAC, and ReBAC implementations.

This framework relates to (but is independent of):

- **authentication.authentication-strategy** (authentication strategy selection): the
  authentication and authorization model decisions are
  independent. An application authors both as separate ADRs.
  The authentication strategy informs the audit-event identity
  source (per authorization.audit-events-on-decisions); the authorization model informs
  what the application does with that identity.

The substrate's substrate-scope.md and Charter (specifically
Article V on opinionated defaults) inform how the substrate
expresses preference without prescribing.

External references:

- OWASP ASVS v5.0.0 V8 (Authorization architectural decisions):
  https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x17-V8-Authorization.md
- NIST SP 800-162 (Guide to ABAC Definition and
  Considerations):
  https://csrc.nist.gov/publications/detail/sp/800-162/final
- NIST SP 800-53 AC-3 control enhancements (AC-3(7) RBAC,
  AC-3(8) DAC, AC-3(13) ABAC):
  https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home
- Zanzibar (Google's consistent global authorization system;
  the canonical ReBAC reference):
  https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
