---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.authorization.authorization-model-selection-authorization-model-selection"
title: "authorization.authorization-model-selection review checklist: authorization model selection"
substrate-rule: "authorization.authorization-model-selection"
substrate-rule-href: "rule.yaml"
layer: "L3"
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
  - "New application before any authorization code is written (pre-build gate)"
  - "Existing application changing or materially extending its authorization model (adding ABAC to RBAC, adding ReBAC to existing role-based system)"
  - "Periodic review of the existing MADR (substrate-recommended annually)"
  - "Pull requests adding authorization-related code when no model MADR exists in the application"
reviews-what: "the consumer's filled-in MADR document"
reviews-where: "typically /docs/decisions/ADR-XXX-authorization-model.md"
---

# authorization.authorization-model-selection review checklist: authorization model selection

## How to use this binding

L3 review is fundamentally different from L1 mechanical scan
and L2 code/test review. The reviewer reviews a DOCUMENT (the
consumer's filled-in MADR), not code or test scenarios. The
questions below verify that the MADR satisfies the substrate's
quality requirements.

The MADR is a pre-build gate per authorization.authorization-model-selection. Reviewers must
complete this checklist before substantive authorization
implementation work proceeds. The MADR review can be done by
the same reviewers who do code review, or by a designated
security architect, depending on the consumer's organization.

The substrate's paired decision framework is at
decision-frameworks/authorization-model-selection.madr.md.
The framework provides the substrate's option-space analysis;
the consumer's MADR adapts the framework to their application
context. Reviewers should be familiar with both the framework
and this checklist.

## Review questions

### 1. MADR exists and is in the standard location

Is there a MADR document for authorization model selection in
the application's decision-records location?

What good looks like: a document at
`/docs/decisions/ADR-XXX-authorization-model.md` (or the
consumer's adapted location); the document is linked from the
application's architectural documentation; the document
references the substrate's decision framework.

What needs follow-up: no MADR exists; the MADR is buried in an
unobvious location; the MADR is in a private wiki not
accessible to engineering review; the application's
authorization implementation predates any MADR.

### 2. Status is Accepted (or explicitly transitional)

Does the MADR have an accepted status, or is the transitional
status (Proposed, Superseded) explicitly explained?

What good looks like: Status is "Accepted" with date; or
status is "Proposed" with named timeline for acceptance; or
status is "Superseded by ADR-YYY" with reference to the
successor.

What needs follow-up: status is missing; status is "Proposed"
indefinitely without acceptance plan; status is "Accepted" but
the running implementation has diverged from the documented
model.

### 3. Context section is substantive

Does the Context and Problem Statement section adequately
describe the application's authorization situation?

What good looks like: covers user population structure (job
functions, organizational boundaries, external versus
internal users), resource model shape (flat list of objects
versus graph of related objects versus attribute-classified
resources), how access decisions actually need to be made
(role-driven, attribute-driven, relationship-driven), and the
operational maturity available to maintain the chosen model.
Specific to the application, not generic boilerplate.

What needs follow-up: section is one or two sentences of
generic content ("We need authorization"); fails to describe
the user population or resource model; describes context that
the model choice does not address.

### 4. Decision drivers are concrete

Are the decision drivers concrete and specific to the
application's context?

What good looks like: drivers reference specific aspects of
the user population, the resource model, the regulatory or
contractual obligations, and the operational context.
A reviewer can tell why each driver matters in this
particular application.

What needs follow-up: drivers are vague ("security matters",
"users want flexibility"); drivers are not connected to the
application's actual structure; drivers list desirable
properties of any authorization system without distinguishing
the application's specific requirements.

### 5. Considered options include substrate-analyzed alternatives

Does the Considered Options section include at least the
substrate-analyzed options (RBAC, ABAC, ReBAC, hybrid) that
are plausibly applicable to this application?

What good looks like: at least 3 of the 4 substrate-analyzed
options are considered with reasoning; options excluded early
have brief explicit reasoning (e.g., "ReBAC excluded:
application's resource model is not graph-structured");
substrate-acceptable hybrid composition is considered when
the application's concerns span multiple patterns.

What needs follow-up: only one option is "considered" with
others ignored; substrate-recommended options for the
application's context are not addressed at all; hybrid is
dismissed without analysis even when the application has
multiple concern domains.

### 6. Chosen option is justified

Is the Decision Outcome section's reasoning aligned with the
Decision Drivers and the option analysis?

What good looks like: the chosen option's pros directly
address the named drivers; the chosen option's cons are
acknowledged and accepted with explicit reasoning; the choice
fits the application's resource model and user population
structure as documented in Context.

What needs follow-up: chosen option does not connect to the
drivers; reasoning is post-hoc rationalization of a decision
made elsewhere ("we chose RBAC because the team is familiar");
no acknowledgment of trade-offs; the choice fights the
application's documented structure (RBAC chosen for a graph-
shaped authorization surface, or ReBAC chosen for a flat role-
based application).

### 7. Substrate alignment is explicit

Does the MADR explicitly state whether the choice aligns with
substrate-recommended options for the application's context?

What good looks like: a dedicated "Substrate alignment"
subsection states alignment status (Aligned | Deviation:
justified) with specific reasoning where applicable.
Deviations are explicit and reasoned. Hybrid choices include
the rationale for composition.

What needs follow-up: alignment is not addressed; the MADR
deviates from substrate guidance silently; the alignment
section says "aligned" without reasoning when the choice is
actually a deviation; hybrid composition is chosen without
documenting which concerns use which model.

### 8. Consequences include required follow-up work

Does the Consequences section enumerate the substrate rules
that apply to the chosen model and the implementation
implications?

What good looks like: explicit inventory of the L1 and L2
authorization rules that apply given the chosen model (e.g.,
"RBAC choice inherits the authorization mechanical (L1) rules,
authorization.object-level-authorization through authorization.audit-events-on-decisions"); identification of the
policy engine or framework the application will use to
implement the chosen model; identification of the operational
mechanisms the model requires (role assignment workflow,
attribute provisioning, relationship recording).

What needs follow-up: consequences are generic ("we'll need to
implement authorization"); no inventory of substrate rules in
scope; policy engine selection deferred indefinitely;
operational mechanisms not addressed.

### 9. Pros and cons analysis is option-comparative

Does the Pros and Cons section actually compare options, not
just list isolated facts about the chosen option?

What good looks like: each option has both pros and cons; the
chosen option's pros include reasons it was preferred OVER
other options; common failure modes for the chosen model
(role proliferation for RBAC, policy complexity for ABAC,
graph traversal cost for ReBAC) are explicitly acknowledged
with mitigation plan.

What needs follow-up: only the chosen option has pros listed;
other options have only cons; no comparative analysis; the
chosen model's common failure modes are absent.

### 10. Decision review schedule is set

Is there a defined next-review date and a list of triggers
that would force earlier review?

What good looks like: explicit next review date (substrate-
recommended annually); triggers listed including material
change in user population, addition of new resource types
with different authz shape, regulatory change affecting access
control requirements, security incident affecting
authorization.

What needs follow-up: no review schedule; review is "as
needed" without defined triggers; review schedule predates
material changes to the application's authorization surface
that should have triggered review.

## Reviewer attestation

```
authorization.authorization-model-selection review checklist: complete
- MADR exists and in standard location: PASS / FOLLOW-UP / EXEMPT
- Status is Accepted or transitional: PASS / FOLLOW-UP / EXEMPT
- Context section substantive: PASS / FOLLOW-UP / EXEMPT
- Decision drivers concrete: PASS / FOLLOW-UP / EXEMPT
- Considered options include substrate alternatives: PASS / FOLLOW-UP / EXEMPT
- Chosen option justified: PASS / FOLLOW-UP / EXEMPT
- Substrate alignment explicit: PASS / FOLLOW-UP / EXEMPT
- Consequences include follow-up work: PASS / FOLLOW-UP / EXEMPT
- Pros and cons option-comparative: PASS / FOLLOW-UP / EXEMPT
- Decision review schedule set: PASS / FOLLOW-UP / EXEMPT
```

When all questions pass, the MADR is accepted and the pre-
build gate is cleared. Authorization implementation work
proceeds against the substrate rules listed in the MADR's
Consequences section.

## Cross-reference

- Substrate rule: authorization.authorization-model-selection in catalogs/concerns/authorization.oscal.yaml
- Decision framework: decision-frameworks/authorization-model-selection.madr.md
- Good example: examples/authorization/authorization-model-selection-good.md
- Anti-pattern: examples/authorization/authorization-model-selection-anti-pattern.md
- Related L2 rule: authorization.centralized-deny-by-default-policy (centralized policy point implements the chosen model)
- Related L3 rule (paired): authentication.authentication-strategy (authentication strategy selection follows the same pre-build-gate-MADR pattern)
