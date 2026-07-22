<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: error-handling.error-handling-strategy error-handling strategy ADR (forbidden patterns)

Substrate-original anti-patterns. Do not pattern your own ADR
on these.

## Anti-pattern A: No ADR exists

The service has been in production for three years. The retry
policy was decided implicitly by the team that wrote the first
gateway client; subsequent additions copied that retry policy
or invented their own. Each call site has its own backoff
constants, retry caps, and timeout values. No documented
strategy exists.

The error-handling.error-handling-strategy review checklist's Question 1 produces
NEEDS FOLLOW-UP. The substrate's L3 gate fails.

## Anti-pattern B: ADR exists but Status remains Proposed indefinitely

```markdown
# ADR-0011: Error-handling strategy
- Status: Proposed
- Date: 2024-08-15
- ...
```

The ADR was authored 20 months ago and never moved to Accepted.
The team has continued shipping changes; the implementation has
drifted from what the ADR proposed.

The error-handling.error-handling-strategy review checklist's Question 2 produces NEEDS
FOLLOW-UP. Proposed indefinitely is treated as no decision.

## Anti-pattern C: ADR with no Considered Options

```markdown
# ADR-0011: Error-handling strategy
- Status: Accepted
- Date: 2026-04-22

## Decision
We use exponential backoff for retries.

## Reasoning
Exponential backoff is industry standard.
```

The substrate-recommended MADR format includes Considered
Options for a reason: the L3 gate checks that the author
considered alternatives before settling. An ADR with no
alternatives is indistinguishable from an undocumented choice.

The error-handling.error-handling-strategy review checklist's Question 3 produces NEEDS
FOLLOW-UP.

## Anti-pattern D: ADR with no failure-mode classification

```markdown
# ADR-0011: Error-handling strategy
- Status: Accepted

## Decision
Retry 3 times with 100ms backoff. Circuit breaker at 50% error rate.
```

The decision applies a single retry policy to all failure
classes. There is no distinction between "hard decline"
(retrying is wrong) and "gateway timeout" (retrying is right).
The first retry against a hard decline will produce a duplicate
charge.

The substrate framework's D1 (failure-mode classification) is
not addressed.

## Anti-pattern E: ADR with no total-wall-budget

```markdown
# ADR-0011: Error-handling strategy
- Status: Accepted
- Decision: retry 5 times with exponential backoff starting at 500ms

## Reasoning
500ms * 2^0 + 500ms * 2^1 + ... + 500ms * 2^4 = 15.5 seconds total
```

The ADR makes the retries explicit but does not relate the
total wall budget to a customer SLA. A 15-second worst-case
retry chain is incompatible with most synchronous customer
flows. Substrate framework's D2 (customer expectation) is
not addressed.

## Anti-pattern F: ADR copy-pasted from another service without context

```markdown
# ADR-0011: Error-handling strategy
- Status: Accepted

## Decision
Identical to NotificationService's ADR-0009.
```

NotificationService is an async queue consumer with 30-minute
retry budgets. PaymentService is a synchronous customer-facing
authorizer with 8-second SLA. The policies are not
substitutable. Per substrate framework Section 3, error-handling
strategies must be context-sensitive.

## Anti-pattern G: ADR documents intent but no enforceable artifacts

```markdown
# ADR-0011: Error-handling strategy
- Status: Accepted

## Decision
Developers should retry safely with bounded backoff.
```

The decision is aspirational text with no enforceable surface.
There is no library choice, no per-failure-mode policy, no
timeout values, no observability binding. The next engineer to
add a gateway call site cannot derive the right behavior from
the ADR.

error-handling.error-handling-strategy's intent is that the ADR is implementable. Anti-
pattern G is the failure mode where the ADR satisfies the
shape requirement (markdown file exists, status Accepted) but
not the substance (developer can derive the policy at the
call site).

## Anti-pattern H: ADR adopted but observability not wired

```markdown
# ADR-0011: Error-handling strategy
- Status: Accepted
- Decision: hybrid with service-tier policy
- Observability: per-failure-mode counters
```

The ADR mentions observability but the counters were never
created in the metrics emitter. Operators cannot tell whether
the circuit breaker is opening, whether retries are exhausting
the budget, or whether soft declines are spiking. The
incident-response surface is blind.

Substrate framework D5 (observability) is mentioned but not
discharged.

## Why these patterns fail the L3 gate

The L3 gate is not a markdown lint. It is a check that the
strategic decision is *operational*: that an engineer with a
new gateway call site can derive correct behavior, that
operators can observe the system's decisions, that the
customer-facing contract matches the strategy, and that the
strategy survives reviewer scrutiny by considering and
rejecting alternatives.

Each anti-pattern above fails one or more of these substantive
checks. Substrate-author guidance: review the consumer's ADR
against the substrate framework's D1-D9 decision drivers,
the five considered options, and the substrate-recommended
library defaults. Gaps surface as L3 review findings, not as
file-format complaints.
