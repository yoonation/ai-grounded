<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Decision Frameworks

A decision framework is Layer 3 decision support: a structured
document that helps an engineer make a judgmental decision by naming
the question, the trade-offs, and the contextual questions, and saying
when an ADR is required. Frameworks are not rules. They do not say
"you must do X." They support making the X decision deliberately
rather than by default.

## Where decision frameworks live now

Each judgmental rule's decision framework is co-located with the rule,
as the rule's MADR:

```
catalogs/concerns/<concern>/<rule-slug>/decision.md
```

This directory no longer holds the per-rule MADR files; they were moved
into their rule folders so that everything for a rule lives in one
place. This directory is retained for shared or cross-concern decision
content should any be authored; per-rule decisions belong with their
rule.

## What Layer 3 is and why it needs frameworks

The substrate's three-layer model treats different rule kinds
differently:

- **Layer 1 (mechanical)**: enforceable by static analysis. Tooling
  decides; no judgment required.
- **Layer 2 (semantic)**: requires contextual application. A human or
  AI reviewer applies the rule using examples.
- **Layer 3 (judgmental)**: requires architectural judgment with
  explicit trade-offs. No correct answer in the abstract; the right
  answer depends on context.

Layer 3 rules cannot specify the answer. They specify the question, the
trade-offs, and the documentation required when the answer is chosen.
The decision framework does that work. Examples of Layer 3 concerns:
authentication strategy, caching strategy, service architecture,
concurrency model. None has a single correct answer; all benefit from
structured deliberation.

## Format: MADR

Decision frameworks use MADR (Markdown Any Decision Records), a
community standard with consistent structure: Context and Problem
Statement, Decision Drivers, Considered Options, Decision Outcome, and
Pros and Cons of the Options. The substrate uses the MADR structure but
adapts the content for decision support (helping reach a decision)
rather than decision recording, leaving the Decision Outcome open for
the consumer to fill in when they apply the framework. See
https://adr.github.io/madr/ for the template.

## When a framework is consulted

A Layer 3 rule's `rule.yaml` states the intent (typically: this
decision requires documented rationale), and its `decision.md` is the
framework. A human or AI reviewer reads the intent, works through the
framework's questions for their specific context, and produces a
consumer-side ADR that captures the answer. The consumer-side ADR lives
in the consumer's repository (commonly `docs/decisions/`). The framework
is the substrate's guidance; the ADR is the consumer's decision record.

## Identifier convention

A judgmental rule is identified, like every rule, by its readable path
`<concern>.<rule-slug>`, and its framework is the `decision.md` in that
rule's folder. The reference chain:

```
rule: authentication.authentication-strategy
  (catalogs/concerns/authentication/authentication-strategy/rule.yaml)
  carries its decision framework alongside it:
    catalogs/concerns/authentication/authentication-strategy/decision.md
```

## Authoring discipline

- Authoritative sources cited (industry analyses, foundational texts)
- Real-world examples of organizations making each considered option
  where public information allows
- Decision drivers explained in terms of consequences, not just listed
- Trade-offs balanced; the framework characterizes options rather than
  advocating one
- Anti-patterns named (the wrong way to make the decision)
- Second-human review before stable promotion

Frameworks are particularly susceptible to author bias because they
involve judgment topics, so review discipline matters more here than in
mechanical rules.

## What decision frameworks are not

- **Not ADRs.** ADRs record decisions already made; frameworks support
  decisions not yet made. The output of using a framework is an ADR.
- **Not opinionated recommendations.** Layer 1 and Layer 2 are
  opinionated; Layer 3 is deliberately not.
- **Not consultant work.** They structure the analysis the consumer
  does; they do not replace contextual analysis.
- **Not exhaustive.** They cover the common options at authoring time.

## Cross-references

- `../CHARTER.md` Article II (authoring discipline)
- `../CHARTER.md` Article IV (identifier and intent immutability)
- the storage model design doc (package-by-rule layout)
- `../catalogs/concerns/` (judgmental rules, each carrying decision.md)
- https://adr.github.io/madr/ (MADR format specification)
