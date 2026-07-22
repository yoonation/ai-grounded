---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.input-validation.schema-validation-at-boundary-schema-validation-at-boundary"
title: "input-validation.schema-validation-at-boundary test template: schema validation at boundary"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# input-validation.schema-validation-at-boundary test template: schema validation at boundary

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework against the application's input boundaries.

These tests verify the schema layer's behavior on positive and
negative inputs. They are integration tests against the request-
parsing layer, not unit tests of the schema library.

The substrate-recommended coverage target is: every endpoint
that accepts a request body has at least one positive scenario
(valid request succeeds) and at least one negative scenario per
declared constraint (missing required, type mismatch, range
violation, unknown field).

## Scenario 1: Valid request succeeds

**Preconditions**
- The endpoint under test has a documented schema with required
  fields, optional fields, and field constraints
- A request body matching the schema is constructed

**Action**
- Submit the valid request to the endpoint

**Expected**
- HTTP 200 (or the endpoint's standard success status)
- The response indicates success per the endpoint's contract
- No schema-rejection error appears in the application log

## Scenario 2: Missing required field is rejected

**Preconditions**
- The schema declares at least one required field
- A request body is constructed with the required field omitted

**Action**
- Submit the request to the endpoint

**Expected**
- HTTP 400 (or the endpoint's validation-error status)
- The error response body identifies the missing field by name
- The handler does not execute (no side effects: no database
  write, no external service call, no metric increment for
  successful handling)

## Scenario 3: Type mismatch is rejected

**Preconditions**
- The schema declares a field with a specific type (int, bool,
  array, nested object)
- A request body is constructed with the field carrying a value
  of the wrong type (string where int expected, scalar where
  array expected)

**Action**
- Submit the request

**Expected**
- HTTP 400
- The error response identifies the field and the expected type
- The handler does not execute

## Scenario 4: Out-of-range value is rejected

**Preconditions**
- The schema declares a field with a numeric range (min, max)
  or a string length range
- A request body is constructed with the field exceeding the
  range

**Action**
- Submit the request

**Expected**
- HTTP 400
- The error response identifies the field and the constraint
  violated
- The handler does not execute

## Scenario 5: Unknown field is rejected (substrate-default strict mode)

**Preconditions**
- The schema is configured in strict mode (the substrate-
  recommended default)
- A request body is constructed with a field name not declared
  in the schema, in addition to all required fields

**Action**
- Submit the request

**Expected**
- HTTP 400
- The error response identifies the unknown field
- The handler does not execute
- If the application has documented strip-mode as its chosen
  behavior, the expected result is HTTP 200 with the unknown
  field silently dropped; the ADR (input-validation.input-validation-strategy) documents this
  exception

## Scenario 6: Schema rejection is logged

**Preconditions**
- The application's log infrastructure is configured to capture
  validation errors
- A request with a schema violation (any of the above scenarios)
  is submitted

**Action**
- Submit the invalid request
- Inspect the application log

**Expected**
- A log entry exists for the rejection with the endpoint name,
  the failed field, and the rejection reason
- The log entry is at an appropriate severity level (WARN or
  INFO per the application's logging policy)
- The log entry includes request correlation identifiers per
  logging.correlation-ids

## Scenario 7: Concurrent requests do not bypass validation

**Preconditions**
- The application uses async or concurrent request handling
- A batch of requests is constructed: half valid, half invalid

**Action**
- Submit the batch concurrently

**Expected**
- Valid requests receive success responses
- Invalid requests receive validation-error responses
- No request bypasses the schema layer through race conditions
  or middleware ordering issues

## Coverage notes

- Test scenarios above are the minimum coverage; consumers add
  endpoint-specific scenarios for domain constraints.
- Property-based testing (Hypothesis, fast-check, jqwik,
  ScalaCheck) is substrate-recommended for generating diverse
  invalid inputs against a generated schema.
- Tests should run in CI against every PR that modifies an
  input boundary.
