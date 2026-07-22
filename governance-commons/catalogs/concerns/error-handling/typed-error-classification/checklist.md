---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.error-handling.typed-error-classification-typed-error-classification"
title: "error-handling.typed-error-classification review checklist: typed error classification"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that add, modify, or remove application exception classes"
  - "Code changes that touch the central error handler's exception-to-response mapping"
  - "Code changes that introduce error classification logic (status code mapping, retry decision, alerting routing)"
  - "Code review of new modules that raise or handle exceptions"
  - "Periodic error-handling self-assessment"
---

# error-handling.typed-error-classification review checklist: typed error classification

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review-triggers above. Unanswered items block merge.
Answers are recorded in the pull-request review thread; consumers
adapt the format to their tooling.

This checklist pairs with error-handling.error-response-contract (error response contract).
The contract layer assumes a typed hierarchy underneath; this L2
review verifies the hierarchy exists, distinguishes domain from
infrastructure failures, and is used consistently rather than
short-circuited by string matching.

## Review questions

### 1. Hierarchy declaration: is the application's error hierarchy documented?

Confirm that the application declares a typed error hierarchy in
a discoverable module (e.g., `app/errors.py`,
`com.example.errors`, `lib/errors.ts`). The hierarchy has a
top-level distinction between domain errors (user-actionable
outcomes mapping to 4xx) and infrastructure errors (operational
failures mapping to 5xx); subclasses sit under one of the two
top-level classes.

What good looks like: a module declares DomainError and
InfrastructureError (or substrate-equivalent typed-error
sentinels in Go); subclasses are documented; the hierarchy is
the source of truth for error classification across the
application.

What needs follow-up: errors are raised as the language's base
exception class without typing; subclasses exist but do not
descend from a documented top-level distinction; the hierarchy
is split across modules without a single discoverable root.

### 2. Type-discriminator routing: do classifiers use the type, not the message?

Confirm that error classifiers (the function mapping exception
to HTTP status, the function deciding whether to retry, the
function deciding alert routing) use the type discriminator
(instanceof, errors.As, type-pattern matching) rather than
string-matching the message field.

What good looks like: classifiers branch on exception class
via instanceof / pattern matching; new exception classes
require a new classifier case (compile-time or runtime
exhaustive); no `if str(err).startswith("connection")` style.

What needs follow-up: classifiers grep the error message string
to decide routing; error message changes silently break the
classifier; classifier coverage is not tested.

### 3. Domain vs infrastructure separation: are the two classes used distinctly?

Confirm that domain errors carry information the client uses to
recover (the constraint violated, the field that conflicts, the
state transition rejected) and infrastructure errors carry
information the operator uses to recover (the downstream service,
the configuration value, the resource unavailable). The two are
not conflated.

What good looks like: DomainError subclasses (InsufficientFunds,
DuplicateKey, InvalidStateTransition) have user-actionable
fields; InfrastructureError subclasses (DatabaseUnavailable,
DownstreamTimeout, ConfigurationError) have operator-actionable
fields; the central handler maps each to the appropriate status
class.

What needs follow-up: domain errors carry infrastructure details
(stack trace, internal IDs); infrastructure errors carry domain
details (the user-facing rejection reason); the classes are
used interchangeably.

### 4. Domain-layer raising: are domain errors raised at the domain layer?

Confirm that domain errors are raised in the domain layer (the
business logic, the service layer) rather than at the framework
boundary. The framework boundary catches and maps domain errors
to the response contract; domain code does not construct HTTP
responses.

What good looks like: domain services raise typed DomainError
subclasses; the framework boundary's central handler maps them
to HTTP responses; domain code has no awareness of HTTP status
codes.

What needs follow-up: domain services raise HTTPException
directly with status codes; domain code constructs JSON error
responses; the framework's status-code awareness leaks into
the domain layer.

### 5. Infrastructure-layer wrapping: are infrastructure errors caught and wrapped?

Confirm that infrastructure errors from libraries and
dependencies (database driver exceptions, HTTP client exceptions,
message broker exceptions) are caught at the adapter layer
and wrapped in the application's typed InfrastructureError
subclasses before propagating to higher layers.

What good looks like: adapter layers catch library-specific
exceptions (psycopg.OperationalError, requests.ConnectionError,
java.sql.SQLException) and re-raise as application's
DatabaseUnavailable, DownstreamUnavailable, etc.; higher layers
see only application-typed exceptions.

What needs follow-up: library-specific exceptions propagate to
higher layers; the central handler has cases for library types
mixed with application types; the application's error contract
leaks library implementation details.

### 6. Unhandled-exception backstop: is there a documented top-level catch?

Confirm that the application has a top-level backstop for
unhandled exceptions (the framework's default error handler
configured to log and return a controlled 500 response per
error-handling.no-stack-trace-in-response). The backstop catches programming defects (the
exceptions that should not occur in normal operation) and
ensures they produce controlled responses rather than framework
default debug pages.

What good looks like: the framework's default handler is
configured to use the application's central error handler;
exceptions not matching any classifier case fall to the
backstop with a generic 500 response (no internal disclosure);
the backstop logs at ERROR with full context per error-handling.no-exception-swallow.

What needs follow-up: unhandled exceptions produce framework
default debug pages; the backstop response includes a stack
trace; the backstop is silent (no log entry).

### 7. Exception conversion testing: are the mappings tested?

Confirm that the exception-to-response mapping is tested for
every documented exception class. Tests verify the response
shape, status code, and absence of internal disclosure per
error-handling.no-stack-trace-in-response.

What good looks like: a test suite enumerates exception classes
and verifies the central handler maps each to the documented
response; new exception classes require new test cases;
coverage of the central handler is high (every branch tested).

What needs follow-up: the central handler is not tested;
specific exception classes are tested ad hoc per endpoint;
some classes have no test coverage.

## Output

Each question receives one of three answers: GOOD (the rule's
expectation is met), NEEDS FOLLOW-UP (the rule's expectation is
not met; remediation required before merge), or NOT APPLICABLE
(the question does not apply to this change; the reviewer
documents why).

NEEDS FOLLOW-UP answers block merge until resolved. NOT APPLICABLE
answers require a one-line justification in the review thread.
