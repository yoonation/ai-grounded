---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: error-handling.error-handling-strategy
title: "Error-Handling Strategy"
lifecycle-status: stable
commons-version: "0.5.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-24"
entered-status-at: "2026-05-26"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Authoring and attestation in separate commits; cooling-off interval of one calendar day or more between authored and reviewed dates honored; reviewer identity suffixed with -self-attested per Section 2.4.1 convention. Promoted to stable at M2 close consolidation (Path A precedent) on 2026-05-26 alongside the four other M2 draft MADRs and the five M2 draft catalogs they pair with."
ai-assistance: "AI drafted from substrate-author intent. Pairs with error-handling.error-handling-strategy substrate rule; mirrors the input-validation-strategy.madr.md, authorization-model-selection.madr.md, and auth-strategy.madr.md precedents for L3-as-pre-build-gate. Draft lifecycle per M2 Session 3; promotion to stable deferred to M2 close per Path A precedent."
authoritative-sources:
  - "https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V7-Error-Logging.md"
  - "https://datatracker.ietf.org/doc/html/rfc7807"
  - "https://datatracker.ietf.org/doc/html/rfc9457"
  - "https://docs.aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/"
  - "https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.auth-strategy
  - decision-frameworks.authorization-model-selection
  - decision-frameworks.input-validation-strategy
  - decision-frameworks.logging-architecture
  - decision-frameworks.observability-slo-policy
---

# Error-Handling Strategy

This decision framework provides the substrate's analysis of
error-handling strategy options. Consumers reference this
framework when authoring their own ADR documenting their
application's error-handling strategy choice (substrate-
recommended location for the consumer's ADR:
`/docs/decisions/ADR-XXX-error-handling-strategy.md`).

The framework is referenced by substrate rule error-handling.error-handling-strategy, which
requires applications to have an explicit, documented error-
handling strategy decision before substantive error-handling
implementation begins. Consumers satisfy error-handling.error-handling-strategy by authoring
an ADR that adapts the analysis in this framework to their
application context.

This framework is the error-handling counterpart to
decision-frameworks.input-validation-strategy,
decision-frameworks.authorization-model-selection, and
decision-frameworks.auth-strategy. The four "request lifecycle"
decisions (authentication strategy, authorization model, input-
validation strategy, error-handling strategy) close the inbound
side (authentication, authorization, input validation) and the
outbound side (error handling) of the boundary. The error-
handling strategy is independent of the other three; an
application authors each as a separate ADR.

This framework also has structural relationships with the
logging and observability concerns. Error-handling strategy
choices about logging severity, alerting thresholds, and SLO-
sensitive retry bounds reference the logging-architecture and
observability-slo-policy decision frameworks rather than
duplicating their content.

## Context

Error-handling strategy is the foundational structural choice
that determines how the application detects, classifies, and
responds to exceptional conditions. The choice propagates through
every request handler, every queue consumer, every background
job, and every external dependency call the application makes.
The wrong-strategy failure mode is consistent: error-handling
logic accumulates ad hoc across modules, error response shapes
diverge across endpoints, retry policies are inconsistent across
dependencies, and operational visibility into failures is
fragmented.

Six classes of decision compose to make the strategy:

One, **error response contract**: the shape and protocol of
client-facing error responses. The substrate-preferred default
is RFC 7807 (or RFC 9457) Problem Details for HTTP APIs;
alternatives (JSON:API errors, GraphQL error extensions, custom
application shapes) are acceptable when documented and applied
consistently.

Two, **typed error hierarchy**: how the application classifies
errors at the type level. Substrate-preferred minimum is a
top-level distinction between DomainError (user-actionable
outcomes mapping to 4xx) and InfrastructureError (operational
failures mapping to 5xx); applications layer additional
subclasses per their domain.

Three, **retry and timeout policy**: per-dependency-class
defaults for timeout duration, retry attempt count, backoff
characteristics, and idempotency-key requirements. The choices
reference observability SLO budgets to ensure retry-amplified
load does not violate the application's contract with its own
clients.

Four, **circuit-breaker and degradation policy**: which
dependencies are protected by circuit-breakers, what the
breaker thresholds are, and what the fallback behavior is when
the breaker is open. The substrate-recommended minimum is a
circuit-breaker on any dependency with a known degradation
history; "graceful degradation" implies a fallback path that
returns a degraded response rather than failing.

Five, **fail-fast vs graceful-degradation defaults**: the
application's default response to dependency unavailability.
Fail-fast returns an error response immediately; graceful-
degradation returns a partial or cached response with reduced
fidelity. The choice depends on the application's user contract
(some applications must always return a response; others must
never return stale data).

Six, **error logging policy**: severity assignment for
exceptional conditions (which exceptions log at ERROR, which at
WARN, which at INFO or DEBUG), context inclusion (correlation
ID, operation, parameter set minus sensitive data), and
alerting integration (which error rates trigger alerts at
which thresholds). This dimension overlaps with the logging
concern; the error-handling ADR references the logging
architecture ADR rather than duplicating it.

Making these choices without explicit analysis is a common
substrate failure mode. Teams default to "whatever the framework
provides" plus ad-hoc per-endpoint additions. The result is an
error-handling layer that mostly works but has predictable gaps
(inconsistent shapes, unbounded retry on transient failures, no
circuit-breaker protection, observability blind spots).

The substrate provides analysis of each viable option but does
not prescribe a single choice for all dimensions. Some choices
are substrate-preferred (RFC 7807 / 9457 error response shape;
typed DomainError vs InfrastructureError split; bounded retry
with backoff and jitter); others depend on application context
(circuit-breaker thresholds per dependency, fail-fast vs degrade
defaults, severity assignments).

## Decision Drivers

The substrate identifies the following drivers that should
inform the error-handling strategy. Consumers may add
application-specific drivers but should address each substrate
driver in their ADR.

- **D1. Client contract.** What does the application's user
  contract say about responses? Some applications (interactive
  user-facing services) must always return a response; others
  (batch processors, scheduled jobs) can fail and retry later.
  The contract determines whether fail-fast or graceful-
  degradation is the default.

- **D2. Dependency degradation profile.** Which dependencies
  have known degradation modes (third-party APIs with rate
  limits, shared databases under contention, message brokers
  with replication delays, eventually-consistent stores)? Each
  degradation-prone dependency informs circuit-breaker
  configuration and degradation strategy.

- **D3. SLO budget.** What is the application's error-rate
  budget per the observability-slo-policy ADR? The retry
  policy must not exceed the budget; the circuit-breaker
  thresholds must respect the budget's downstream implications.

- **D4. Idempotency profile.** Which application operations
  are idempotent (safe to retry without side effect) and which
  are not (payment authorization, order placement, message
  publish without idempotency key)? Non-idempotent operations
  cannot retry safely without an idempotency-key contract with
  the dependency.

- **D5. Observability surface.** What error context flows
  through the application's tracing, logging, and metric
  surface? The error-handling strategy emits the context the
  observability surface requires; gaps in the observability
  ADR surface here as error-handling deficiencies.

- **D6. Error response standardization.** Which error response
  contract aligns with the application's client tooling and
  documentation pipeline? RFC 7807 / 9457 is broad and well-
  tooled; JSON:API errors fit JSON:API-aligned services;
  GraphQL error extensions fit GraphQL APIs. Custom shapes
  require justification.

- **D7. Operational maturity.** Does the application have a
  documented incident response process, a paging policy, an
  on-call schedule, and runbooks per failure class? The
  error-handling strategy connects to operational maturity;
  applications without operational maturity cannot benefit
  from sophisticated error classification because no one
  responds to the classifications.

- **D8. Failure-mode coverage.** Which failure modes does the
  application handle explicitly and which does it accept as
  unhandled? The substrate-recommended baseline covers
  database unavailability, downstream service unavailability,
  downstream service timeout, downstream service rate limit,
  cache unavailability, queue unavailability, configuration
  error, and unhandled-exception backstop. Applications layer
  additional modes per their dependencies.

- **D9. Compliance and audit requirements.** Do regulatory
  frameworks (PCI DSS, HIPAA, SOC 2, ISO 27001) require
  specific error-handling characteristics (e.g., all errors
  logged centrally with retention, no error responses include
  cardholder data, no error responses include PHI)? Compliance
  requirements layer onto the substrate strategy.

## Considered Options

### Option 1: RFC 7807 / 9457 Problem Details with typed hierarchy and bounded retry (substrate-preferred default)

**Substrate preference:** Substrate-preferred default for new
applications. Provides the most direct path to satisfying L1
mechanical rules and L2 semantic rules with minimal divergence
from established standards.

**Applicable when:** The application is a new HTTP-based
service. The team can adopt standard library or framework
defaults for the contract layer.

**Pros:**
- RFC 7807 / 9457 is broadly tooled (Spring 6, FastAPI, ASP.NET
  Core 7+, Express with middleware, Rails with gems); the
  application benefits from ecosystem alignment
- Typed DomainError / InfrastructureError split is the
  substrate's L2-aligned classification; mechanical and
  semantic rules apply cleanly
- Bounded retry with backoff and jitter is the AWS Builders
  Library default and the substrate's resilience floor
- Clients with multiple service consumers see a uniform error
  contract across services

**Cons:**
- Requires upfront investment in a typed error hierarchy and a
  centralized error handler
- Existing applications retrofitting to RFC 7807 face migration
  cost across endpoints

**When this option is rejected:** Applications where the
existing error contract is well-established and changing it
would break client commitments; applications where the
framework has stronger native support for an alternative
shape (e.g., legacy SOAP services).

### Option 2: JSON:API error format with typed hierarchy and bounded retry

**Substrate preference:** Substrate-accepts when the application
is JSON:API-aligned or has JSON:API client tooling investment.

**Applicable when:** The application's REST surface follows
JSON:API conventions; clients use JSON:API client libraries
that expect the JSON:API error shape.

**Pros:**
- Aligns with the rest of the JSON:API contract; clients use
  consistent shapes for success and error responses
- JSON:API client libraries handle errors uniformly
- Combines well with JSON:API's resource-oriented design

**Cons:**
- JSON:API is less broadly tooled than RFC 7807; non-JSON:API
  clients see an unfamiliar shape
- The JSON:API error format includes fields (id, links) that
  may be over-specified for typical error responses
- Less directly aligned with the substrate's L1 binding for
  error-handling.no-stack-trace-in-response (which biases toward Problem Details)

### Option 3: GraphQL error extensions

**Substrate preference:** Substrate-accepts for GraphQL APIs
where the application's GraphQL surface is the primary client
interface.

**Applicable when:** The application exposes a GraphQL API as
its primary or sole client interface.

**Pros:**
- Aligns with the GraphQL specification's error protocol
- GraphQL clients handle errors uniformly via the response
  errors array
- Field-level error correlation is built into the GraphQL
  response shape

**Cons:**
- GraphQL's "200 with errors in body" model conflicts with
  error-handling.error-status-code; the consumer's ADR documents the GraphQL
  exception explicitly
- HTTP-level infrastructure (load balancers, CDN error
  tracking) cannot classify GraphQL errors via status code
- Applications with both REST and GraphQL surfaces face
  divergence between the two error shapes

### Option 4: Custom application-specific contract

**Substrate preference:** Substrate-accepts when documented in
the ADR with explicit rationale and applied consistently across
the application.

**Applicable when:** The application's error contract is
established and changing it would break significant client
commitments; the application has documented requirements that
standard shapes do not address (e.g., regulatory requirements
for specific error fields).

**Pros:**
- Optimized for the application's specific requirements
- No migration cost from existing contracts

**Cons:**
- Substrate's review surface (error-handling.error-response-contract) requires verifying the
  custom contract is applied consistently, which adds review
  overhead
- New clients face a non-standard learning curve
- Ecosystem tooling does not apply

### Option 5: Mixed-shape (no enforced contract)

**Substrate preference:** Substrate-rejects. The "every endpoint
chooses" approach is the antipattern error-handling.error-response-contract exists to
prevent.

**Applicable when:** Not applicable. This option is documented
for completeness; the substrate's L2 review rejects this option
during code review.

**Pros:**
- Lowest upfront cost (no investment in a contract layer)

**Cons:**
- error-handling.error-response-contract review will block merge for inconsistent error
  shapes
- Every client must implement per-endpoint adapters; client
  cost is enormous
- Observability classification is fragmented; alert routing
  cannot use error type discriminators
- Substrate-compliant posture is unreachable with this option

## Substrate-recommended defaults for other drivers

These are starting recommendations; consumers may select
alternatives with justification.

- **D2 Retry policy:** Maximum 3 attempts for idempotent calls;
  1 attempt (no retry) for non-idempotent calls without
  idempotency-key support. Exponential backoff with base
  100ms doubling per attempt. AWS-pattern equal jitter
  applied to spread retry storms.

- **D2 Timeout policy:** Substrate-recommended baseline is
  per-call timeout shorter than the caller's deadline by a
  ratio that accommodates retry. For request-response APIs
  with a 1-second total deadline and 3 retry attempts, the
  per-call timeout is 200ms; the math accommodates the worst-
  case retry sequence with backoff and jitter under the total
  deadline.

- **D2 Circuit-breaker policy:** Substrate-recommended minimum
  is a circuit-breaker on any external dependency with a
  documented degradation profile (third-party APIs, shared
  databases under contention, message brokers). Open after
  5 consecutive failures or 50% failure rate in a 30-second
  window; half-open trial after 60 seconds; closed when the
  trial succeeds. Tune per dependency.

- **D2 Substrate-recommended retry libraries:**
  - Python: tenacity (substrate-preferred); backoff (acceptable)
  - JavaScript/TypeScript: cockatiel (substrate-preferred);
    p-retry (acceptable for simple cases); axios-retry for
    Axios-specific retry policies
  - Java: resilience4j (substrate-preferred); Spring Retry
    (acceptable for Spring-only applications)
  - .NET: Polly (substrate-preferred)
  - Go: gobreaker (substrate-preferred for circuit-breaker);
    hashicorp/go-retryablehttp for HTTP retry; cenkalti/backoff
    for general retry
  - Ruby: retriable (acceptable); custom retry with sidekiq for
    background-job retry

- **D6 Error response contract:** RFC 9457 Problem Details
  (substrate-preferred; supersedes RFC 7807 but the
  substrate accepts either); fields type, title, status,
  detail, instance always populated; additional fields per
  application requirements documented in the ADR.

- **D8 Failure-mode coverage minimum baseline:**
  - Database unavailability: circuit-breaker, fail-fast on
    open
  - Downstream service unavailability: circuit-breaker,
    documented degradation or fail-fast
  - Downstream service timeout: bounded retry per D2, then
    fail-fast or degrade
  - Downstream service rate limit: backoff respecting Retry-
    After header, bounded retry, then fail-fast
  - Cache unavailability: bypass to source (the cache is an
    optimization, not a correctness requirement)
  - Queue unavailability: depends on queue role (publish:
    in-memory buffer with bounded drop policy; consume: pause
    and resume on recovery)
  - Configuration error: fail-fast at startup; do not start
    serving traffic
  - Unhandled-exception backstop: catch at application top
    level, log per error-handling.no-exception-swallow, return generic 500 per
    error-handling.no-stack-trace-in-response and error-handling.error-status-code

- **D9 Compliance integration:** When regulatory frameworks
  apply, the ADR documents the specific requirements (e.g.,
  PCI DSS 6.5.5 information leakage requirements aligning
  with error-handling.no-stack-trace-in-response; HIPAA audit requirements aligning with
  error-handling.no-exception-swallow and LOG-L2-*) and the strategy's compliance
  posture.

## Documentation Required

Consumers using this framework satisfy error-handling.error-handling-strategy by producing
an ADR in their application that addresses each of the
following. The consumer's ADR location is substrate-recommended
at `/docs/decisions/ADR-XXX-error-handling-strategy.md`.

The consumer's ADR must contain:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
  status with date and deciders
- **Context and Problem Statement**: application-specific
  context covering client contract (D1), dependency degradation
  profile (D2), SLO budget reference (D3), idempotency profile
  (D4), observability surface (D5), error response
  standardization (D6), operational maturity (D7), failure-mode
  coverage (D8), and compliance and audit requirements (D9)
- **Decision Drivers**: the substrate's drivers (D1-D9 above)
  adapted to the application's specific context, plus any
  application-specific drivers
- **Considered Options**: at least the substrate options that
  are plausibly applicable to the application; consumers may
  exclude options with brief reasoning
- **Decision Outcome**: the chosen option for each dimension
  (error response contract, typed hierarchy organization, retry
  and timeout policy, circuit-breaker policy, fail-fast vs
  degrade defaults, error logging policy) with reasoning that
  references the decision drivers and the application's
  specific context
- **Substrate Alignment**: explicit statement of whether the
  choice aligns with substrate-preferred options for the
  application context; deviations must be justified
- **Consequences**: positive consequences (which failure modes
  are handled well), negative consequences (which failure
  modes require workarounds or are accepted unhandled), and
  required follow-up work
- **Pros and Cons of Each Option**: option-comparative analysis
  showing why the chosen option was preferred over the
  rejected options
- **References**: error-handling.error-handling-strategy substrate rule, related substrate
  rules in scope (typically error-handling.no-bare-except through L1-005 and
  error-handling.error-response-contract through L2-004), related substrate ADRs (auth-
  strategy, authorization-model-selection, input-validation-
  strategy, logging-architecture, observability-slo-policy),
  application-specific references
- **Decision Review Schedule**: next scheduled review date
  (substrate-recommended annually) and triggers that force
  earlier review (regulatory change, material change in
  dependency profile, security incident affecting error
  handling, observability SLO budget revision)

The substrate's review checklist at
`checklist.md`
provides the questions reviewers ask when verifying the
consumer's ADR. Consumers can self-review against the checklist
before submitting their ADR for acceptance.

## More Information

This framework is referenced by:

- **error-handling.error-handling-strategy** (substrate rule): the rule that requires
  consumers to author an error-handling strategy ADR.
- **error-handling.error-response-contract through error-handling.observable-response-discrepancy** (semantic rules): apply
  to the chosen strategy's implementation across the
  application; the consumer's ADR enumerates which apply
  given the strategy.
- the error-handling mechanical (L1) rules (mechanical rules): apply
  to all error-handling implementations regardless of strategy;
  static analysis catches the patterns these rules govern.

This framework relates to (but is independent of):

- **authentication.authentication-strategy** (authentication strategy selection): the
  authentication and error-handling strategy decisions are
  independent. Authentication errors are one error class the
  error-handling strategy handles; authentication.generic-failure-responses (generic error
  messages on authentication failure) is the credential-
  specific case of error-handling.no-stack-trace-in-response and error-handling.observable-response-discrepancy.
- **authorization.authorization-model-selection** (authorization model selection): the
  authorization decision produces errors (Forbidden) that the
  error-handling strategy classifies and responds to.
- **input-validation.input-validation-strategy** (input-validation strategy selection):
  input-validation rejection produces errors that the error-
  handling strategy responds to per the chosen contract.

This framework references (and depends on):

- **logging.architecture** (logging-architecture) MADR: the error-
  handling strategy's logging policy (D6 substrate-driver)
  references the logging-architecture ADR for severity
  assignment, context inclusion, and central log destination
  decisions. The error-handling ADR does not duplicate
  logging-architecture content; it references the choices
  made there.
- **observability.slo-policy** (observability-slo-policy) MADR: the error-
  handling strategy's retry and circuit-breaker bounds (D3
  driver) respect the SLO budget set in the observability-
  slo-policy ADR. The error-handling ADR references the SLO
  budget when justifying retry attempt counts and circuit-
  breaker thresholds.

External references:

- OWASP ASVS v5.0.0 V7 (Error Handling and Logging):
  https://github.com/OWASP/ASVS/blob/v5.0.0/5.0/en/0x15-V7-Error-Logging.md
- OWASP Top 10 2021 A09:2021 Security Logging and Monitoring
  Failures:
  https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/
- RFC 7807 Problem Details for HTTP APIs:
  https://datatracker.ietf.org/doc/html/rfc7807
- RFC 9457 Problem Details for HTTP APIs (supersedes 7807):
  https://datatracker.ietf.org/doc/html/rfc9457
- AWS Builders' Library, "Timeouts, retries, and backoff with
  jitter" (substrate-foundational reference for retry policy):
  https://docs.aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Michael T. Nygard, Release It! Design and Deploy Production-
  Ready Software (substrate-recommended reading on circuit-
  breakers, bulkheads, and stability patterns; concepts
  paraphrased throughout this framework)
- MADR (Markdown Any Decision Records) format reference:
  https://adr.github.io/madr/
