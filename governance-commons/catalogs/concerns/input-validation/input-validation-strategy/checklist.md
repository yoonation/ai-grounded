---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.input-validation-strategy-input-validation-strategy"
title: "input-validation.input-validation-strategy review checklist: input-validation strategy ADR"
substrate-rule: "input-validation.input-validation-strategy"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Architecture decision review for a new application introducing input validation"
  - "Architecture decision review for a major refactor of an existing application's validation layer"
  - "Periodic ADR audit (substrate-recommended annually)"
  - "Substrate-author audit at authorization.object-level-authorization pre-build gate or equivalent"
---

# input-validation.input-validation-strategy review checklist: input-validation strategy ADR

## How to use this binding

Reviewers answer every question below when reviewing the
consumer's input-validation-strategy ADR. The ADR is a one-time
document per application; subsequent reviews verify the
application's implementation against the ADR rather than
re-authoring the decision.

This checklist pairs with the substrate's decision framework
MADR at decision-frameworks/input-validation-strategy.madr.md.
The framework MADR provides the analysis structure (decision
drivers, considered options); the consumer's ADR is the filled-in
decision document the application commits to.

## Review questions

### 1. ADR existence: is there a documented input-validation strategy ADR?

Confirm that the application has an ADR at a discoverable
location (substrate-recommended /docs/decisions/ADR-XXX-input-
validation-strategy.md). The ADR follows the MADR format
(Status, Context, Decision Drivers, Considered Options, Decision
Outcome, Consequences).

What good looks like: the ADR exists; it is findable from the
project's documentation index; it references the substrate's
framework MADR.

What needs follow-up: no ADR exists; the strategy is implicit
in the codebase; the ADR is in a non-discoverable location.

### 2. ADR status: is the ADR Accepted or Superseded?

Confirm the ADR has Status: Accepted (or Superseded by a
successor ADR). Status: Proposed indefinitely is not acceptable
for an application in production.

What good looks like: Status: Accepted with a date; OR Status:
Superseded by ADR-XXX with a reference to the successor.

What needs follow-up: Status: Proposed without a clear path to
Accepted; the ADR has no status line; Accepted but the
implementation has diverged without updating the ADR.

### 3. Library choice: is the validation library selected and documented?

Confirm the ADR identifies the application's validation library
(Pydantic, Marshmallow, Zod, Joi, Yup, JSON Schema with a
validator, Cerberus, attrs with validators, or equivalent). The
choice is justified against the substrate's framework decision
drivers (developer experience, ecosystem fit, error model,
performance).

What good looks like: the library is named; the choice references
the framework's "Library choice" decision driver; alternatives
considered (Considered Options) include at least 2-3 substrate-
recommended libraries.

What needs follow-up: no library is named; multiple libraries
are used across modules without a primary choice; the choice is
named but no alternatives are documented.

### 4. Placement: is the schema-first vs imperative choice documented?

Confirm the ADR identifies where validation sits in the request
lifecycle: schema-first (declarative schema at the boundary,
handler receives typed instance) or imperative (handler-body
validation, optionally with helpers). The substrate-preferred
choice is schema-first; deviations require explicit justification.

What good looks like: the placement is named (schema-first); the
substrate recommendation is followed; if imperative is chosen,
the ADR explains why (legacy compatibility, performance
constraint, framework limitation).

What needs follow-up: placement is not addressed; the
implementation mixes schema-first and imperative without a
documented rule; deviation from schema-first is not justified.

### 5. Canonical encoding policy: is the Unicode normalization form named?

Confirm the ADR identifies the application's Unicode normalization
form (NFC, NFKC, or neither). The choice underlies input-validation.canonical-encoding-before-validation
(canonical-encoding-before-validation) and affects identifier
comparison behavior across the application.

What good looks like: the normalization form is named (NFC for
most applications, NFKC where compatibility variants matter); the
choice is justified.

What needs follow-up: no normalization form is named; the
application mixes normalized and unnormalized comparisons; the
choice is named but not applied.

### 6. Error response shape: is the validation error format documented?

Confirm the ADR identifies the application's validation-error
response format (field-level error list, top-level error object,
specific HTTP status codes). Consistent error shape across
endpoints is a substrate-recommended client-side affordance.

What good looks like: the error response format is documented
with example payloads; the format is consistent across the
application's endpoints; the format follows a substrate-
recommended pattern (RFC 7807 Problem Details, JSON:API errors,
or a documented application-specific format).

What needs follow-up: error response format is endpoint-specific;
the format is not documented; clients cannot rely on a consistent
error shape.

### 7. Schema versioning: is the schema-evolution policy documented?

Confirm the ADR addresses how input schemas evolve over time
(additive changes vs breaking changes, versioning strategy for
public APIs, deprecation timelines).

What good looks like: the ADR identifies the API versioning
strategy (URL versioning, header versioning, no versioning with
strict backward compatibility); breaking-change policy is
documented; deprecation timelines are specified.

What needs follow-up: schema evolution is not addressed; the
application has no documented versioning strategy; clients
encounter breaking changes without notice.

### 8. Audit reference: does the ADR reference the substrate framework?

Confirm the ADR references the substrate's framework MADR at
decision-frameworks/input-validation-strategy.madr.md and uses
its Decision Drivers section as the analysis template. This is
the audit trail that connects the consumer's decision to the
substrate's framework.

What good looks like: the ADR includes a reference link to the
substrate framework MADR; the Considered Options align with the
framework's recommended options; the Decision Drivers section
mirrors or adapts the framework's drivers.

What needs follow-up: no reference to the substrate framework;
Considered Options are unrelated to the framework's recommended
set; the connection between the consumer's decision and the
substrate's analysis is not documented.

## Output

Each question receives GOOD, NEEDS FOLLOW-UP, or NOT APPLICABLE
per the standard checklist output convention. NEEDS FOLLOW-UP
answers block the substrate-compliance attestation for INPUT-L3-
001 until the ADR is updated.
