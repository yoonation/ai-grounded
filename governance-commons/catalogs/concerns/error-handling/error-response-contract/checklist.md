---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.error-handling.error-response-contract-error-response-contract"
title: "error-handling.error-response-contract review checklist: error response contract"
substrate-rule: "error-handling.error-response-contract"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-24"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove HTTP/RPC/queue response paths"
  - "Code changes that touch the central error handler or error-response builder"
  - "Code changes that introduce new error classes or modify error-class hierarchy"
  - "Code changes that modify OpenAPI specifications for error responses"
  - "Periodic error-handling self-assessment"
---

# error-handling.error-response-contract review checklist: error response contract

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with error-handling.no-stack-trace-in-response (no stack trace in response)
and error-handling.error-status-code (error status code) mechanical detection. L1 catches
the explicit antipatterns; this L2 review confirms the application-
wide consistency of the error response contract.

## Review questions

### 1. Contract declaration: is the error response shape documented in a single place?

Confirm that the application's error response contract (RFC 7807 /
9457 Problem Details, JSON:API errors, GraphQL extensions, or
documented custom shape per the error-handling.error-handling-strategy ADR) is declared in a
single discoverable module: a Problem Details builder, a shared
error response DTO, or an OpenAPI specification component that
all endpoints reference.

What good looks like: a single module (e.g., `app/errors.py`,
`com.example.errors.ProblemDetails`, `lib/errors.js`) declares the
shape; every endpoint's error path constructs responses through
this module; the OpenAPI specification's components/schemas
references the same shape.

What needs follow-up: each endpoint constructs its own error
response shape; the OpenAPI specification declares different
shapes for different endpoints; the contract is implicit in
serializer behavior rather than declared.

### 2. Central routing: do all error responses flow through the central handler?

Confirm that every endpoint routes error responses through the
central error handler (Flask errorhandler, FastAPI
exception_handler, Spring @ControllerAdvice, Express error
middleware, Rails rescue_from). Endpoint-local error returns
that bypass the central handler are the antipattern.

What good looks like: handlers raise typed exceptions; the
central handler maps each exception to the error contract; no
endpoint constructs JSON error responses inline.

What needs follow-up: some endpoints return error responses
inline (jsonify(error="..."), return res.status(400).json({
error: "..."})); the central handler exists but is not used
consistently.

### 3. Field completeness: does every error response carry the required fields?

Confirm that every error response includes the contract's required
fields. For RFC 7807 / 9457: type (URI), title (short human-
readable), status (HTTP status mirrored in body), detail (longer
human-readable specific to this occurrence), instance (URI
identifying this occurrence). For alternatives: the fields the
ADR documents as required.

What good looks like: every error response contains all required
fields; type URIs resolve to documented problem-class definitions;
instance URIs uniquely identify the occurrence for log
correlation.

What needs follow-up: some responses omit fields; type URIs are
not documented (the URI does not resolve to a problem-class
definition); instance URIs are missing.

### 4. Application alignment: do typed exceptions map to contract responses cleanly?

Confirm that the application's typed exception hierarchy (per
error-handling.typed-error-classification) maps cleanly to the error response contract. Each
exception class corresponds to one error response shape; the
mapping is explicit in the central handler.

What good looks like: the central handler has an explicit case
for each exception class; new exception classes require a new
mapping entry; the mapping is tested.

What needs follow-up: the central handler has a generic fallback
that catches every exception with a generic 500 response; new
exception classes silently fall to the generic case; the mapping
is not tested.

### 5. OpenAPI alignment: does the specification declare error responses?

Confirm that the application's OpenAPI specification declares
error responses (4xx, 5xx) for every operation with the
contract's response schema. The runtime responses match the
specification.

What good looks like: every operation declares its expected
error responses; the responses reference a shared component
schema for the contract; Schemathesis or Dredd integration
testing verifies conformance.

What needs follow-up: only success responses are declared; error
responses are documented in prose comments rather than schema;
conformance testing is not part of CI.

### 6. Cross-surface consistency: do all surfaces use the same contract?

Confirm that the application uses one contract across all
surfaces (HTTP API, gRPC, GraphQL, message queue responses,
WebSocket close frames). When the application has multiple
surfaces, the ADR documents the per-surface variations
(GraphQL's response.errors array is a documented exception per
the error-handling.error-handling-strategy ADR).

What good looks like: one contract is the default; per-surface
variations are documented in the ADR; the variations have
mechanical translation between them (the type URIs in the
HTTP surface correspond to error codes in the GraphQL
extensions).

What needs follow-up: each surface invents its own shape;
clients consuming multiple surfaces face multiple parsers;
variations are not documented.

### 7. Privacy: do error responses respect data classification?

Confirm that error responses do not include sensitive data
(authentication credentials, personal data covered by GDPR or
HIPAA, payment card data covered by PCI DSS) per the
substrate's data-classification policies and per error-handling.no-stack-trace-in-response.
The detail field in particular is reviewed for accidental
inclusion of input values that may be sensitive.

What good looks like: error responses contain references (the
field that failed, the validation rule) but not the rejected
values when the values are sensitive; type URIs are public
documentation references, not internal identifiers.

What needs follow-up: error responses echo the rejected
credential, the rejected card number, or the rejected personal
data; type URIs are internal database IDs that leak schema
information.

## Output

Each question receives one of three answers: GOOD (the rule's
expectation is met), NEEDS FOLLOW-UP (the rule's expectation is
not met; remediation required before merge), or NOT APPLICABLE
(the question does not apply to this change; the reviewer
documents why).

NEEDS FOLLOW-UP answers block merge until resolved. NOT APPLICABLE
answers require a one-line justification in the review thread.
