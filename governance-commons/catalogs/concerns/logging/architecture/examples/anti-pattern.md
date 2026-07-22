<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-pattern: logging.architecture logging architecture ADR

## Anti-pattern A: No ADR exists

```
$ ls /docs/decisions/
ADR-001-language-choice.md
ADR-002-database-platform.md
ADR-008-deployment-strategy.md
# No logging architecture ADR
```

Why this violates logging.architecture: the absence of an ADR means
the logging architecture was assembled implicitly from
defaults. The substrate-recommended pattern is a single
explicit decision recorded in the repository.

## Anti-pattern B: Single-sentence ADR

```markdown
# ADR-014: Logging

## Status

Accepted

## Decision

We will use CloudWatch.
```

Why this violates logging.architecture: required sections are missing
(context, drivers, considered options, consequences,
substrate-alignment statement, review schedule). The
decision exists in the file system but the reasoning the
substrate requires is absent.

## Anti-pattern C: Substrate framework copy-paste with no application detail

```markdown
# ADR-018: Logging Architecture

## Context

Logging architecture is a platform-level concern with four
interlocking decisions: aggregator selection, transport,
retention bands, and integrity model. [continues to quote
the entire substrate framework verbatim]

## Decision Drivers

D1. Cloud platform footprint.
D2. Existing observability infrastructure.
D3. Regulatory regime.
[list continues with no application-specific response to any
driver]

## Decision Outcome

We will use the recommended approach.
```

Why this violates logging.architecture: the ADR quotes the substrate
framework but provides no application-specific content. The
substrate's drivers are listed but the consumer's responses
to each driver are missing. "The recommended approach" is
not a decision; it pushes the substantive decision back into
the implicit default.

## Anti-pattern D: Decision drivers omitted

```markdown
# ADR-021: Logging Architecture

## Status

Accepted

## Context

We need logs. We chose Splunk.

## Decision

Use Splunk Cloud, ship via UF, retain 90 days.

## Consequences

- We will pay for Splunk.
```

Why this violates logging.architecture: drivers are absent. The
decision is documented but the reasoning is not. A future
reader cannot evaluate whether the choice still applies when
context changes (new regulation, scale change, budget shift).

## Anti-pattern E: Considered alternatives are strawmen

```markdown
## Considered Options

### Option 1: Write logs to /dev/null

Pros: cheapest.
Cons: no logs.

### Option 2: Print everything to stdout

Pros: simple.
Cons: not aggregated.

### Option 3: Use Datadog

Pros: complete solution.
Cons: none.

## Decision: Datadog
```

Why this violates logging.architecture: alternatives are strawmen
nobody would actually choose. The "considered alternatives"
section exists in form but not substance. Datadog appears
without rivals because the comparison was performative.

## Anti-pattern F: Consequences are aspirational

```markdown
## Consequences

- The team will quickly learn the new aggregator.
- Cost will be reasonable.
- Compliance will be satisfied.
- Incident response will be faster.
```

Why this violates logging.architecture: consequences are aspirational
statements about hoped-for outcomes, not operational
implications of the decision. The substrate-recommended
consequences include cost projection (a number), compliance
mapping (which regulator, which control), and risks the
consumer accepts.

## Anti-pattern G: No review schedule or ownership

```markdown
## Status

Accepted

## ...

## Decision-review schedule

We will review as needed.
```

Why this violates logging.architecture: "as needed" without trigger
events is review-never. The substrate-recommended posture is
annual review cadence plus named trigger events; ownership
is assigned. Without this, the ADR rots silently as the
application's context drifts.

## Anti-pattern H: Substrate-alignment statement missing

```markdown
## Decision Outcome

We chose Loki self-hosted on a Kubernetes cluster.

## Consequences

- Operational ownership: SRE team.
- Cost: infrastructure-only, projected $800/mo.
```

Why this violates logging.architecture: the consumer chose a self-
hosted option in a context where the substrate-preferred
option (cloud-native managed, given limited platform
capacity) might apply. The ADR does not name the substrate
preference or explain the deviation. The reviewer cannot
assess whether the consumer's reasoning is sound.

## Cross-reference

- Good patterns: examples/logging/architecture-good.md
- Substrate rule: logging.architecture
- Decision framework: decision-frameworks/logging-architecture.madr.md
