---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.error-handling.typed-error-classification-typed-error-classification"
title: "error-handling.typed-error-classification test template: typed error classification"
substrate-rule: "error-handling.typed-error-classification"
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

# error-handling.typed-error-classification test template: typed error classification

## How to use this binding

This binding describes test scenarios in framework-agnostic
language. Consumers translate the scenarios into their test
framework against the application's typed error hierarchy and
the central error handler's classification logic.

These tests verify the typed-hierarchy layer behaves correctly:
the correct exception class is raised at the correct seam, the
classifier routes by type rather than string, and the central
handler maps each class to the contract response.

## Scenario 1: Domain error raised at domain layer

**Preconditions**
- The application's domain layer has business logic that can
  reject an operation (insufficient funds, duplicate key,
  invalid state transition)
- The corresponding DomainError subclass is declared in the
  errors module

**Action**
- Invoke the domain operation under conditions that trigger
  the rejection

**Expected**
- The domain operation raises the typed DomainError subclass
- The exception carries domain-actionable fields (the
  constraint violated, the conflicting field, the rejected
  transition)
- No HTTPException, no framework-specific exception, no
  language base exception is raised at the domain layer

## Scenario 2: Infrastructure error wrapped at adapter layer

**Preconditions**
- The application's adapter layer wraps a library that can
  throw infrastructure exceptions (database driver, HTTP
  client, message broker client)
- The corresponding InfrastructureError subclass is declared

**Action**
- Invoke the adapter operation with the library configured to
  throw (mock the failure, use a test-double)

**Expected**
- The adapter catches the library-specific exception
- The adapter re-raises the application's InfrastructureError
  subclass
- The original library exception is preserved as cause /
  inner exception for diagnostic purposes
- No library-specific exception type propagates above the
  adapter

## Scenario 3: Classifier routes by type

**Preconditions**
- The central error handler maps exception classes to
  responses
- The application has at least three documented exception
  classes (one DomainError subclass, one InfrastructureError
  subclass, one classification fallback)

**Action**
- For each exception class, raise the exception and let it
  propagate to the central handler
- Capture the response

**Expected**
- Each class produces the documented response (status code,
  type URI, detail)
- The classification uses instanceof / errors.As / pattern
  matching on the type, not string matching on the message
- New exception classes that have no documented mapping fall
  to the documented fallback (typically a generic 500)

### Scenario 3a: Message-change invariance

**Action**
- Modify the message field of a documented exception class
  (in test setup only)
- Re-run the classifier

**Expected**
- The classification result is unchanged (because the
  classifier uses the type, not the message)

## Scenario 4: HTTP status mapping is correct

**Preconditions**
- The application's typed hierarchy is documented in the
  error-handling.error-handling-strategy ADR
- The substrate's mapping is: DomainError -> 4xx,
  InfrastructureError -> 5xx, with specific subclasses
  mapped to specific codes

**Action**
- For each documented exception class, raise the exception
  and capture the HTTP status code from the response

**Expected**
- DomainError subclasses produce 4xx status codes (specific
  per subclass: ResourceNotFound -> 404, DuplicateKey -> 409,
  InvalidStateTransition -> 422, etc.)
- InfrastructureError subclasses produce 5xx status codes
  (DatabaseUnavailable -> 503, DownstreamTimeout -> 504, etc.)
- The mapping aligns with the substrate's error-handling.error-status-code status
  code guidance

## Scenario 5: Unhandled-exception backstop

**Preconditions**
- The application has a top-level backstop for unhandled
  exceptions
- A test exception class not in the documented hierarchy is
  introduced (test setup only)

**Action**
- Raise the test exception from a handler

**Expected**
- The backstop catches the exception
- The response is a generic 500 with the contract's required
  fields per error-handling.no-stack-trace-in-response (no internal disclosure)
- The server-side log entry contains the full exception
  context per error-handling.no-exception-swallow

## Scenario 6: Logging on the exception path

**Preconditions**
- The application's logging is configured per LOG-L1-* rules
- The central handler logs each exception per error-handling.no-exception-swallow

**Action**
- For each documented exception class, raise the exception
- Inspect the application log

**Expected**
- A log entry exists for every exception
- The entry includes the exception type, message, correlation
  ID, operation name, parameters minus sensitive data
- Severity is appropriate per the application's logging
  policy (substrate-default: ERROR for InfrastructureError,
  WARN for DomainError that the handler recovers from with a
  fallback)

### Scenario 6a: Log shape preserves type discriminator

**Action**
- Parse the log entry from Scenario 6

**Expected**
- The exception type is captured in a structured field (not
  embedded in a message string)
- An operator querying logs by exception type can locate the
  occurrence without string matching

## Scenario 7: Tests exist for every documented exception class

**Preconditions**
- The error-handling.error-handling-strategy ADR enumerates the documented exception
  classes
- The test suite has classification tests

**Action**
- Run the test suite

**Expected**
- Every documented exception class has at least one test
- Tests fail if a documented class lacks a classifier mapping
- The test suite is part of CI

## Coverage notes

- Test scenarios above are the minimum coverage; consumers add
  domain-specific exception classes to the test suite as the
  hierarchy grows.
- Mock or test-double the dependencies for Scenarios 1, 2, and
  5 to avoid coupling the test to specific infrastructure.
- Tests should run in CI against every PR that modifies the
  errors module or the central handler.
