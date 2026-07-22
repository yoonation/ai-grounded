---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.error-handling.error-response-contract-error-response-contract"
title: "error-handling.error-response-contract test template: error response contract"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# error-handling.error-response-contract test template: error response contract

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework against the application's HTTP endpoints (or
equivalent for non-HTTP surfaces).

These tests verify the error response contract layer's behavior
on representative error paths. They are integration tests
against the application's response surface, not unit tests of
the central error handler.

The substrate-recommended coverage target is: every endpoint
has at least one error path test that verifies the contract
fields are populated correctly; the central handler has
coverage for every typed exception class.

## Scenario 1: 4xx response has the contract's required fields

**Preconditions**
- The endpoint under test has a validation that can be
  triggered with a malformed request
- The application's error contract is RFC 7807 / 9457 Problem
  Details (or the application's documented alternative per the
  error-handling.error-handling-strategy ADR)

**Action**
- Submit a request that triggers validation failure

**Expected**
- HTTP status code is 4xx per the contract's mapping
- Response body is JSON (or the contract's documented format)
- For RFC 7807 / 9457: response includes type (URI), title
  (short human-readable), status (matches HTTP status code),
  detail (longer human-readable specific to this occurrence),
  instance (URI identifying this occurrence)
- For alternative contracts: the contract's required fields
  are present

## Scenario 2: 5xx response has the contract's required fields

**Preconditions**
- The endpoint can be made to throw an unhandled exception or
  to encounter an infrastructure failure (mocked downstream
  service failure, simulated database error)
- The contract is the same as Scenario 1

**Action**
- Trigger the infrastructure failure on the endpoint

**Expected**
- HTTP status code is 5xx
- Response body conforms to the contract shape
- For RFC 7807 / 9457: type URI references the documented
  infrastructure-error category; detail is generic per
  error-handling.no-stack-trace-in-response (no internal disclosure); instance URI uniquely
  identifies the occurrence for log correlation

## Scenario 3: Type URI resolves to documented problem class

**Preconditions**
- The application uses RFC 7807 / 9457 Problem Details
- The type URIs are documented at a discoverable location

**Action**
- For each error class the application documents, fetch the
  type URI

**Expected**
- The type URI resolves to a documentation page or schema
  describing the problem class
- The documentation describes when the error occurs and what
  the client should do
- No type URI is "about:blank" except where the contract
  explicitly allows (RFC 9457 reserves about:blank for
  unclassified problems)

## Scenario 4: Instance URI uniquely identifies the occurrence

**Preconditions**
- The application's contract requires instance URIs (typical for
  RFC 7807 / 9457 implementations)
- The application's logging emits correlation IDs per logging.correlation-ids

**Action**
- Trigger an error
- Capture the instance URI from the response
- Inspect the application log

**Expected**
- The instance URI is unique per occurrence (not a constant
  string)
- The instance URI correlates to a log entry (the URI contains
  or references the correlation ID)
- An operator can locate the server-side log entry from the
  instance URI

## Scenario 5: Endpoints route through the central handler

**Preconditions**
- The application has a central error handler (Flask
  errorhandler, FastAPI exception_handler, Spring
  @ControllerAdvice, Express error middleware, Rails
  rescue_from)
- A representative sample of endpoints is selected (substrate-
  recommended: 5 endpoints across HTTP methods and resource
  types)

**Action**
- For each selected endpoint, trigger an error condition
- Compare the response shapes

**Expected**
- All endpoints produce identical response shapes for the
  same error class
- Field names are consistent across endpoints
- No endpoint emits a "ad-hoc" error shape that bypasses the
  central handler

## Scenario 6: OpenAPI conformance

**Preconditions**
- The application publishes an OpenAPI specification
- The specification declares error responses for endpoints

**Action**
- Run Schemathesis or Dredd against the running service with
  the OpenAPI specification

**Expected**
- Runtime error responses conform to the specification's
  declared schemas
- No endpoint returns a response shape not declared in the
  specification
- The conformance check is part of CI

## Scenario 7: Privacy: error response does not echo sensitive input

**Preconditions**
- The endpoint accepts input that could be sensitive (password
  field, payment card number, personal data)
- The validation triggers an error on the sensitive field

**Action**
- Submit a request with a deliberately invalid sensitive value
  (e.g., an invalid email format that includes a known string)
- Inspect the error response

**Expected**
- The error response identifies the field name but does not
  echo the rejected value
- The response does not include the password, card number, or
  personal data from the input

## Coverage notes

- Test scenarios above are the minimum coverage; consumers add
  endpoint-specific scenarios for domain-specific error
  classes.
- Property-based testing (Hypothesis, fast-check, jqwik,
  ScalaCheck) is substrate-recommended for generating diverse
  error-triggering inputs against the contract.
- Tests should run in CI against every PR that modifies the
  central error handler, an OpenAPI specification, or a
  typed exception class.
