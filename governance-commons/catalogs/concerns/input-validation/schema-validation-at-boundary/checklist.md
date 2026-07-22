---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.schema-validation-at-boundary-schema-validation-at-boundary"
title: "input-validation.schema-validation-at-boundary review checklist: schema validation at boundary"
substrate-rule: "input-validation.schema-validation-at-boundary"
substrate-rule-href: "rule.yaml"
layer: "L2"
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
  - "Code changes that add, modify, or remove HTTP/RPC/queue input boundaries"
  - "Code changes that touch request-parsing logic on existing endpoints"
  - "Code changes that introduce new input contracts (new request DTOs, new schemas)"
  - "Periodic input-validation self-assessment"
---

# input-validation.schema-validation-at-boundary review checklist: schema validation at boundary

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with the input-validation mechanical (L1) rules's
mechanical detection of injection patterns at the handler-body
level. L1 catches the unsafe call sites; this L2 review confirms
the input boundary's structural shape is declared and validated
before the handler body executes. The semantic correctness of the
schema (does it describe the right shape?) is the L2 review
surface.

## Review questions

### 1. Schema location: is the input schema declared in a discoverable place?

Confirm that the input boundary has an explicit schema declaration
(Pydantic model, JSON Schema, Joi schema, Zod schema, Marshmallow
schema, attribute annotation on a typed DTO) located in a
discoverable module. The schema is referenced from the handler
function rather than reconstructed inside it.

What good looks like: the schema is in a schemas module or a
models module; the handler signature consumes the schema's typed
output (e.g., `def handler(body: CreateOrderRequest)`); the
application's input contract can be enumerated by listing the
declared schemas.

What needs follow-up: the handler reads request.json or
request.body and applies inline isinstance or hasattr checks; the
schema is implicit in the handler's branching logic; the input
contract is not enumerable.

### 2. Parse not validate: does the handler receive a typed instance?

Confirm that the framework parses the request into the schema's
target type (not into a dict that the handler then accesses). The
handler operates on the typed instance; field accesses are
type-checked at compile time (typed languages) or at attribute
access (Python with strict schemas).

What good looks like: handler signature shows the schema type;
handler body uses attribute access (`body.customer_id`) rather
than key access (`body["customer_id"]`); the IDE or type checker
flags references to undeclared fields.

What needs follow-up: handler accepts a dict and accesses keys
directly; field name typos are not caught at type-check time;
the handler defensively re-validates fields that the schema
already constrains.

### 3. Required vs optional: are field requirements documented in the schema?

Confirm that the schema declares which fields are required and
which are optional. Optional fields have explicit default values
or are typed as Optional / nullable. The schema rejects requests
missing required fields with a structured error response.

What good looks like: every field has explicit required/optional
marking; the schema is the source of truth for the input contract;
generated API documentation matches the schema.

What needs follow-up: the schema marks all fields as optional and
the handler body checks required fields; required-versus-optional
status is implicit; some endpoints accept missing fields with
implicit None defaults that downstream code did not anticipate.

### 4. Domain constraints: do schema field types reflect domain constraints?

Confirm that fields with domain constraints beyond shape (string
length bounds, numeric ranges, enumerated values, regex patterns,
format-checked types like email and URL) carry those constraints
in the schema declaration rather than in the handler body.

What good looks like: a quantity field is declared with min=1
max=10000; an email field is declared as EmailStr; a status field
is declared as a Literal["pending", "confirmed", "shipped"]; the
schema enforces the constraint at parse time.

What needs follow-up: the schema declares fields as primitive str
or int and the handler validates ranges after parsing; the same
constraint is reimplemented across multiple handlers; domain
violations produce ad-hoc error responses rather than the
schema's standard format.

### 5. Error responses: what happens when the schema rejects input?

Confirm that schema-rejection produces a structured error response
(HTTP 400 with a body describing which fields failed; or the
framework's equivalent for non-HTTP boundaries). The handler does
not execute on a partially-valid input. The error response does
not leak internal implementation details (stack traces, internal
field names that differ from API field names).

What good looks like: the framework returns a 400-level response
with a body listing field errors; the response format is consistent
across all endpoints; the error body uses field names from the
API contract, not internal types.

What needs follow-up: schema rejection produces an unhandled
exception and a 500 response; rejections trigger different error
formats per endpoint; the error body includes internal type names
or stack traces.

### 6. Unknown fields: how does the schema treat unexpected fields?

Confirm the application's policy on unknown fields (fields in the
input that are not declared in the schema). The substrate-
recommended default is to reject unknown fields (strict mode);
silent stripping is acceptable when documented as the application's
chosen behavior in the input-validation-strategy ADR.

What good looks like: the schema is configured with strict
unknown-field handling (Pydantic `extra="forbid"`, Joi
`unknown(false)`, Zod `.strict()`); the choice matches the ADR.

What needs follow-up: unknown-field behavior varies across
endpoints; some endpoints silently accept unknown fields and
others reject; the choice is not documented.

### 7. Audit logging: are schema rejections logged?

Confirm that schema rejections are visible to audit logging per
the logging concern (logging.integrity or equivalent). Systematic invalid
input (a probe, a misconfigured client, a regression in a
caller) is detectable from logs without manual inspection.

What good looks like: rejected requests appear in the application
log with the endpoint name, the field that failed, and the
rejection reason; an audit dashboard surfaces rejection rates by
endpoint.

What needs follow-up: rejections are silent; only the client sees
the rejection; systematic probing or upstream regressions are not
detectable from the server side.

## Output

Each question receives one of three answers: GOOD (the rule's
expectation is met), NEEDS FOLLOW-UP (the rule's expectation is
not met; remediation required before merge), or NOT APPLICABLE
(the question does not apply to this change; the reviewer
documents why).

NEEDS FOLLOW-UP answers block merge until resolved. NOT APPLICABLE
answers require a one-line justification in the review thread.
