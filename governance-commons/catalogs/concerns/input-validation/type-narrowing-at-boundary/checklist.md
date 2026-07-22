---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.input-validation.type-narrowing-at-boundary-type-narrowing-at-boundary"
title: "input-validation.type-narrowing-at-boundary review checklist: type narrowing at boundary"
substrate-rule: "input-validation.type-narrowing-at-boundary"
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
  - "Code changes that add or modify input boundary schemas"
  - "Code changes that introduce new domain types (UUID, EmailAddr, Money, etc.)"
  - "Code changes that pass values across module boundaries"
  - "Periodic input-validation self-assessment"
---

# input-validation.type-narrowing-at-boundary review checklist: type narrowing at boundary

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block
merge.

This checklist enforces the "parse, don't validate" principle:
domain values with structural constraints are parsed into domain
types at the input boundary; handlers and downstream code receive
the domain type, not a primitive string. The pattern eliminates
defensive re-validation throughout the codebase and surfaces
malformed input as a parse failure at the edge.

## Review questions

### 1. Structured fields: are constrained values typed as domain types?

Confirm that fields with structural constraints (UUID, email
address, URL, monetary amount, date, phone number, country code,
ISO currency code) are declared in the schema as domain types
rather than as primitive strings.

What good looks like: a UUID field is typed as uuid.UUID (Python),
java.util.UUID (Java), uuid.UUID (Go); an email field is typed as
EmailStr or the framework's email-validating type; a monetary
amount is typed as a Decimal with explicit precision policy; a
date is typed as datetime.date or LocalDate.

What needs follow-up: the schema declares these fields as str or
int and the handler re-parses or re-validates; some endpoints use
domain types while others use primitives; the type choices are
inconsistent across modules.

### 2. Strict constructors: do domain types reject malformed input?

Confirm that the domain type's constructor is strict: it rejects
malformed input by raising a structured error rather than
producing a possibly-invalid instance. The schema layer surfaces
the error; downstream code never sees a malformed value.

What good looks like: uuid.UUID(value) raises ValueError on a
malformed UUID; the EmailStr type validates against RFC 5322; the
Money type rejects negative-zero, NaN, and infinity; the schema
translates the constructor error into a structured 400 response.

What needs follow-up: the constructor accepts any string and
produces an instance whose validity must be checked separately;
malformed values reach handler code; the type's invariants are
not enforced at construction.

### 3. Downstream signatures: do handlers receive domain types?

Confirm that handler function signatures show the domain types
(not str) for fields that have domain types in the schema. The
type system enforces the contract: a function that expects a
UUID cannot accept a str without explicit conversion.

What good looks like: handler signatures show the domain types;
the IDE or type checker enforces correct types at call sites;
function callers cannot pass arbitrary strings where domain types
are expected.

What needs follow-up: handler signatures show str for fields
that are domain types in the schema; the handler re-parses the
string into the domain type; type information is lost at module
boundaries.

### 4. Cross-module consistency: do domain types travel intact?

Confirm that domain types are used consistently across the
application's modules. A UUID parsed at the HTTP boundary remains
a UUID through the service layer, the repository layer, and the
database driver (or is explicitly converted to the storage
representation at the storage layer, with the conversion
documented).

What good looks like: domain types appear in repository method
signatures, service method signatures, and inter-module
interfaces; conversions to and from storage representations are
isolated in dedicated adapter classes.

What needs follow-up: domain types are stripped to primitives at
module boundaries and reconstructed in each module; type
information degrades as values flow through the application;
defensive re-validation appears at each module boundary.

### 5. Test fixtures: do tests use domain types directly?

Confirm that unit tests construct domain-type fixtures directly
rather than passing string values that the handler re-parses.
The handler test exercises handler logic, not parsing logic;
parsing tests are separate.

What good looks like: handler unit tests pass domain-type
instances (a uuid.UUID object, a Money instance) directly to the
handler function; separate parsing tests exercise the schema's
constructor.

What needs follow-up: handler unit tests pass strings and the
handler re-parses them; parsing errors are mixed with handler
logic errors in the same test cases; tests cannot exercise
handler error paths without crafting parser-valid inputs.

### 6. Library coverage: where domain types are not available, is the gap closed?

Confirm that fields without library-provided domain types (an
application-specific identifier format, a project-internal status
enum) are handled by application-defined types in the same
fashion as library-provided types: a constructor that validates,
a downstream signature that requires the type, no string passing.

What good looks like: the application has a types module
containing project-specific domain types; their constructors are
strict; they are used in handler signatures the same way library
types are.

What needs follow-up: project-specific fields are carried as
strings everywhere; no domain-type abstraction exists for them;
each consumer re-validates ad hoc.

## Output

Each question receives GOOD, NEEDS FOLLOW-UP, or NOT APPLICABLE
per the standard checklist output convention.
