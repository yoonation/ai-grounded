---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: input-validation.input-validation-strategy
title: "Input Validation Strategy"
lifecycle-status: stable
commons-version: "0.5.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-23"
entered-status-at: "2026-05-26"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention. Promoted to stable at M2 close consolidation (Path A precedent) on 2026-05-26 alongside the four other M2 draft MADRs and the five M2 draft catalogs they pair with."
ai-assistance: "AI drafted from substrate-author intent. Pairs with input-validation.input-validation-strategy substrate rule; mirrors the authorization-model-selection.madr.md and auth-strategy.madr.md precedents for L3-as-pre-build-gate. Draft lifecycle per M2 Session 2; promotion to stable deferred to M2 close per Path A precedent."
authoritative-sources:
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x13-V5-Validation-Sanitization-Encoding.md"
  - "https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home"
  - "https://owasp.org/Top10/A03_2021-Injection/"
  - "https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.auth-strategy
  - decision-frameworks.authorization-model-selection
---

# Input Validation Strategy

This decision framework provides the substrate's analysis of
input-validation strategy options. Consumers reference this
framework when authoring their own ADR documenting their
application's input-validation strategy choice (substrate-
recommended location for the consumer's ADR:
`/docs/decisions/ADR-XXX-input-validation-strategy.md`).

The framework is referenced by substrate rule input-validation.input-validation-strategy, which
requires applications to have an explicit, documented input-
validation strategy decision before substantive input-validation
implementation begins. Consumers satisfy input-validation.input-validation-strategy by
authoring an ADR that adapts the analysis in this framework to
their application context.

This framework is the input-validation counterpart to
decision-frameworks.authorization-model-selection and
decision-frameworks.auth-strategy. The three "request boundary"
decisions (authentication strategy, authorization model, input-
validation strategy) are independent; an application authors
each as a separate ADR.

## Context

Input-validation strategy is the foundational structural choice
that determines how the application validates every value
crossing the trust boundary. The choice propagates through every
request handler, every queue consumer, every file processor, and
every CLI tool the application exposes. The wrong-strategy
failure mode is consistent: validation logic accumulates ad hoc
across modules, canonical forms diverge across endpoints, and
the application's input contract becomes implicit in the union
of handler-body checks rather than declared in schemas.

Three classes of decision compose to make the strategy:

One, **where validation sits**: declared in schemas at the
boundary (schema-first) or imperative within handler bodies
(handler-first). The substrate strongly prefers schema-first;
the handler-first option exists for legacy compatibility and
framework constraints.

Two, **which library encodes the schemas**: Pydantic,
Marshmallow, Zod, Joi, Yup, JSON Schema with a validator,
Cerberus, attrs, dataclasses with validators, or framework-
native bindings. The choice depends on language, ecosystem fit,
and team familiarity.

Three, **what canonical-form and error-shape policies apply**:
Unicode normalization (NFC vs NFKC), URL decoding count,
case-folding rule, error response format (RFC 7807, JSON:API,
custom), schema evolution policy.

Making these choices without explicit analysis is a common
substrate failure mode. Teams default to "whatever the framework
provides" without examining whether the framework's defaults
match the application's input shape. The result is a validation
layer that mostly works but has predictable gaps (no Unicode
normalization, inconsistent error shapes, ad-hoc handling of
unknown fields).

The substrate provides analysis of each viable option but does
not prescribe a single choice for all dimensions. Some choices
are substrate-preferred (schema-first placement; reject unknown
fields by default; NFC normalization for most applications);
others depend on application context (library choice, error
shape, versioning policy).

## Decision Drivers

The substrate identifies the following drivers that should
inform the input-validation strategy. Consumers may add
application-specific drivers but should address each substrate
driver in their ADR.

- **D1. Placement: schema-first vs imperative.** Where in the
  request lifecycle does validation execute? Schema-first places
  validation at the boundary (framework dispatches to a schema-
  parsed typed object). Imperative places validation inside
  handler bodies (after the framework delivers a raw request).
  The substrate prefers schema-first; deviation requires
  justification.

- **D2. Library choice.** Which validation library encodes the
  schemas? Choice depends on language, ecosystem maturity, type-
  system integration, error-model quality, and team familiarity.
  Substrate-recommended options per language are documented
  under Considered Options.

- **D3. Canonical encoding policy.** Which Unicode normalization
  form does the application use (NFC, NFKC, neither)? How many
  times is URL decoding applied? Are identifier fields case-
  folded? The choices underlie input-validation.canonical-encoding-before-validation and affect
  identifier comparison behavior application-wide.

- **D4. Error response shape.** What is the structured error
  format when validation fails? Substrate-recommended options:
  RFC 7807 Problem Details for HTTP APIs, JSON:API error format,
  GraphQL error extensions for GraphQL APIs, or a documented
  application-specific format. Consistent shape across endpoints
  is required; the choice of format depends on client tooling
  alignment.

- **D5. Unknown-field handling.** When a request contains fields
  not declared in the schema, does the application reject the
  request (strict mode, substrate-recommended) or strip the
  unknown fields silently (lenient mode)? The choice affects
  forward compatibility (clients adding new fields the server
  does not yet recognize) versus security posture (rejecting
  unknown fields catches malicious additions and client bugs).

- **D6. Schema versioning policy.** How do input schemas evolve?
  Options: URL versioning (/v1/, /v2/), header versioning,
  no versioning with strict backward compatibility (additive
  changes only), or per-endpoint versioning. The choice affects
  client coordination and deprecation workflow.

- **D7. Type-narrowing depth.** Which domain types does the
  application define (UUID, EmailAddr, Money, etc.) versus
  carrying primitive strings? Deep type narrowing produces
  durable contracts but adds upfront design cost. Shallow type
  narrowing is faster to write but accumulates defensive checks
  over time.

- **D8. Validation error logging.** Are validation rejections
  logged at INFO, WARN, or DEBUG severity? Are systematic
  rejections surfaced via dashboards? The choice integrates
  with the logging concern (logging.structured-format, logging.aggregation) and the
  observability concern (observability.semantic-convention-coverage).

- **D9. Performance constraints.** Do input boundaries face
  latency or throughput constraints that affect library choice?
  Some validation libraries (Pydantic v2 with its Rust core,
  Zod with TypeScript inference, fastjsonschema for Python) are
  optimized for high throughput; others trade performance for
  developer experience.

## Considered Options

### Option 1: Schema-first with framework-integrated library (substrate-preferred)

**Substrate preference:** Substrate-preferred for the placement
dimension across all application types. Substrate-preferred
default for new applications.

**Applicable when:** The application's framework has first-class
schema integration (Pydantic in FastAPI, Joi or Zod in Express,
Spring's @Valid with Jakarta Bean Validation, Rails strong
parameters with custom validators).

**Pros:**
- Validation is declarative and discoverable; the input contract
  is enumerable from the schema modules
- Handler bodies operate on typed instances; defensive re-
  validation is eliminated
- Generated API documentation (OpenAPI, GraphQL SDL) derives
  from the same schemas
- Substrate L1 mechanical rules and L2 review checklists have
  direct alignment with this placement
- Library ecosystems (Pydantic, Zod) provide rich type-narrowing
  primitives that reduce ad-hoc validation

**Cons:**
- Migration cost from existing imperative validation can be
  substantial
- Framework constraints may limit schema placement (some legacy
  frameworks parse requests before any schema layer can act)
- Some libraries have steep learning curves for advanced
  patterns (discriminated unions, recursive types)

### Option 2: Schema-first with standalone JSON Schema library

**Substrate preference:** Substrate-acceptable for applications
where the framework does not integrate cleanly with native
schema libraries, or where multiple services share schemas
across language boundaries.

**Applicable when:** A polyglot environment requires schema
sharing (the same JSON Schema document validates inputs in
multiple service implementations); the framework lacks first-
class schema integration.

**Pros:**
- JSON Schema is language-agnostic; schemas can be shared
  across services
- Tooling for JSON Schema is mature (validators, code
  generators, documentation generators)
- Schemas are externally readable; partners and clients can
  inspect them

**Cons:**
- JSON Schema's type system is limited compared to language-
  native types; domain types require custom format extensions
- Error messages from JSON Schema validators are often less
  ergonomic than native-library errors
- Round-trip between JSON Schema and language-native types
  requires explicit conversion

### Option 3: Imperative validation with helpers

**Substrate preference:** Substrate-accepts only when schema-
first is impractical (legacy framework that resists schema
integration; performance constraint that no schema library
satisfies). Requires explicit justification in the consumer's
ADR.

**Applicable when:** Legacy compatibility with an existing
imperative validation pattern; framework architecture that
parses requests before any declarative validation layer can
intercept.

**Pros:**
- Maximum flexibility; can express constraints that schema
  libraries cannot
- No external library dependency for validation
- Easy to introduce gradually in an existing codebase

**Cons:**
- Validation scatters across handlers; the input contract is
  not enumerable
- Type narrowing requires manual encoding; downstream code
  cannot rely on the type system
- Each handler reimplements common patterns; bugs in shared
  patterns require multiple-handler fixes
- L1 mechanical rules and L2 review checklists are harder to
  apply when validation is spread across handler bodies

### Option 4: Validation at the domain boundary (DDD style)

**Substrate preference:** Substrate-acceptable for applications
with strong domain modeling that places validation inside
domain types (the type's constructor is the validator).

**Applicable when:** The application follows Domain-Driven
Design with rich domain types; the boundary's role is
translation between transport representations and domain types
rather than independent validation.

**Pros:**
- Domain types are the source of truth for validity; no separate
  validation layer can drift
- Type narrowing is structural; downstream code is statically
  guaranteed to receive valid values
- Aligns with input-validation.type-narrowing-at-boundary (type narrowing at boundary) as a
  primary pattern rather than an additional pattern

**Cons:**
- Requires upfront domain modeling; not appropriate for
  applications without a rich domain layer
- Error reporting requires careful design to surface domain-
  validation errors as structured API errors
- Some inputs (transport-level fields like Content-Type
  headers) do not have domain types; the strategy needs a
  fallback for them

### Option 5: Minimal validation (deferred to framework defaults)

**Substrate preference:** Substrate-rejects for new applications.
Substrate-accepts only for explicitly scoped applications where
input-validation is not part of the application's contract
(internal tools with trusted users, prototypes with documented
caveat).

**Applicable when:** Internal-only applications where the input
trust boundary is essentially absent; throwaway prototypes.

**Pros:**
- Lowest upfront cost
- Framework defaults handle the most basic cases (parsing JSON
  as JSON, decoding URL parameters once)

**Cons:**
- Substrate L1 mechanical rules detect many gaps; this option
  produces substantial review findings
- Production-grade applications require more than framework
  defaults; this option does not produce a substrate-compliant
  posture
- Input contract is undefined; clients cannot rely on
  consistent behavior

## Substrate-recommended library defaults (D2)

These are starting recommendations; consumers may select alternatives with justification.

- **Python:** Pydantic v2 (substrate-preferred); Marshmallow
  (acceptable, older but mature); attrs with validators
  (acceptable for dataclass-style projects); JSON Schema with
  jsonschema (acceptable when cross-language sharing is required)
- **JavaScript/TypeScript:** Zod (substrate-preferred for
  TypeScript); Joi (acceptable for plain JavaScript); Yup
  (acceptable, ecosystem alignment with React forms); JSON
  Schema with ajv (acceptable when cross-language sharing is
  required)
- **Java:** Jakarta Bean Validation with Hibernate Validator
  (substrate-preferred); Spring's built-in validation
  (acceptable, builds on Bean Validation)
- **Go:** validator (go-playground/validator, substrate-preferred);
  ozzo-validation (acceptable for declarative-validation
  preference)
- **Ruby:** dry-validation (substrate-preferred for Rails+ style);
  Active Model validations (acceptable for Rails applications)
- **PHP:** Symfony Validator (substrate-preferred); Laravel
  validation (acceptable for Laravel applications)

## Substrate-recommended defaults for other drivers

- **D3 Canonical encoding:** NFC for most applications; NFKC
  where compatibility variants must collapse (e.g., financial
  identifier systems where halfwidth and fullwidth digits must
  compare equal). URL decoding exactly once at the boundary;
  no downstream re-decoding. Case-folding via locale-independent
  functions (casefold in Python, toLocaleLowerCase("und") in
  JavaScript, or equivalent).

- **D4 Error response shape:** RFC 7807 Problem Details for
  HTTP APIs (substrate-preferred); JSON:API error format for
  JSON:API-aligned services; GraphQL error extensions for
  GraphQL APIs.

- **D5 Unknown-field handling:** Strict (reject) by default.
  Lenient (strip) is acceptable when documented and applied
  consistently; mixing the two is not.

- **D6 Schema versioning:** URL versioning (/v1/, /v2/) for
  public APIs (substrate-preferred); strict backward
  compatibility (additive changes only) for stable APIs with
  large client populations; no versioning for internal APIs
  with coordinated clients.

- **D7 Type-narrowing depth:** Domain types for all structured
  fields (UUID, email, URL, monetary, date, phone) at
  minimum; deeper narrowing for application-specific concepts
  where the type's invariants matter for correctness.

- **D8 Logging:** WARN for client-induced rejections that may
  indicate misuse; INFO for routine rejections (forms missing
  fields during normal user input); DEBUG for verbose payload
  detail when investigating issues.

## Documentation Required

Consumers using this framework satisfy input-validation.input-validation-strategy by producing
an ADR in their application that addresses each of the
following. The consumer's ADR location is substrate-recommended
at `/docs/decisions/ADR-XXX-input-validation-strategy.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: application-specific
  context covering placement (D1), library choice (D2),
  canonical encoding (D3), error shape (D4), unknown-field
  handling (D5), versioning (D6), type-narrowing depth (D7),
  and logging (D8)
- **Decision Drivers**: the substrate's drivers (D1-D9 above)
  adapted to the application's specific context, plus any
  application-specific drivers
- **Considered Options**: at least the substrate options that
  are plausibly applicable to the application; consumers may
  exclude options with brief reasoning
- **Decision Outcome**: the chosen option for each dimension
  (placement, library, canonical forms, error shape, unknown-
  field handling, versioning) with reasoning that references
  the decision drivers and the application's specific context
- **Substrate Alignment**: explicit statement of whether the
  choice aligns with substrate-preferred options for the
  application context; deviations must be justified
- **Consequences**: positive consequences (which input shapes
  are handled well), negative consequences (which shapes
  require workarounds), and required follow-up work
- **Pros and Cons of Each Option**: option-comparative analysis
  showing why the chosen option was preferred over the
  rejected options
- **References**: input-validation.input-validation-strategy substrate rule, related substrate
  rules in scope (typically input-validation.parameterized-queries through L1-005 and
  input-validation.schema-validation-at-boundary through L2-006), application-specific
  references
- **Decision Review Schedule**: next scheduled review date
  (substrate-recommended annually) and triggers that force
  earlier review (regulatory change, material change in input
  shape, security incident affecting validation)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR. Consumers can self-review against the checklist
before submitting their ADR for acceptance.

## More Information

This framework is referenced by:

- **input-validation.input-validation-strategy** (substrate rule): the rule that requires
  consumers to author an input-validation strategy ADR.
- **input-validation.schema-validation-at-boundary through input-validation.deserialization-safe-loaders** (semantic rules):
  apply to most input boundaries; the consumer's ADR
  enumerates which apply given the chosen strategy.
- the input-validation mechanical (L1) rules (mechanical rules):
  apply to all input-validation implementations regardless of
  strategy; static analysis catches the patterns these rules
  govern across schema-first and imperative implementations.

This framework relates to (but is independent of):

- **authentication.authentication-strategy** (authentication strategy selection): the
  authentication and input-validation strategy decisions are
  independent. The authentication strategy informs the identity
  values that flow into validation; the validation strategy
  governs how all values (including identity-bearing values)
  are validated.
- **authorization.authorization-model-selection** (authorization model selection): the
  authorization and input-validation strategy decisions are
  independent. Input validation runs before authorization;
  validation gates the request shape, authorization gates the
  request action.

External references:

- OWASP ASVS v5.0.0 V5 (Validation, Sanitization and Encoding):
  https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x13-V5-Validation-Sanitization-Encoding.md
- OWASP Top 10 2021 A03:2021 Injection:
  https://owasp.org/Top10/A03_2021-Injection/
- NIST SP 800-53 SI-10 Information Input Validation:
  https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home
- Alexis King, "Parse, don't validate" (the framing this
  framework adopts for D1 and D7):
  https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
