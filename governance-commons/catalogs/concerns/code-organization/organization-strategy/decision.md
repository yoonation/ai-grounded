---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: code-organization.organization-strategy
title: "Code-Organization Strategy: Architectural Style, Module Boundaries, and the Dependency Rule"
lifecycle-status: stable
commons-version: "0.6.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M4 close consolidation (2026-06-01) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M4 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-01. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with code-organization.organization-strategy substrate rule. Portfolio-of-sub-decisions structure mirroring the infrastructure-security-baseline and supply-chain-integrity-strategy MADR precedents: five sub-decisions (architectural style, module-boundary policy, dependency rule and enforcement, cross-cutting placement, repository topology) plus a review cadence, rather than a single option pick. Draft lifecycle per M4 Session 2; stable promotion at M4 close."
authoritative-sources:
  - "https://en.wikipedia.org/wiki/Single-responsibility_principle"
  - "https://en.wikipedia.org/wiki/Dependency_inversion_principle"
  - "https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)"
  - "https://en.wikipedia.org/wiki/Multitier_architecture"
  - "https://en.wikipedia.org/wiki/Acyclic_dependencies_principle"
  - "https://en.wikipedia.org/wiki/Information_hiding"
  - "https://en.wikipedia.org/wiki/Don%27t_repeat_yourself"
  - "https://import-linter.readthedocs.io/en/stable/contract_types.html"
  - "https://www.archunit.org/userguide/html/000_Index.html"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.infrastructure-security-baseline
---

# Code-Organization Strategy: Architectural Style, Module Boundaries, and the Dependency Rule

## Context and Problem Statement

Every codebase has a code-organization strategy. The only choice is
whether the strategy is decided and written down or left to accrete from
the habits of whoever wrote each file first. code-organization.organization-strategy requires that
the strategy be explicit, because it is the anchoring decision the rest
of the code-organization concern depends on: the four L2 rules are each
conformance checks, and what they conform to is precisely this strategy.
Module cohesion (code-organization.module-boundary-cohesion) is judged against the boundary policy;
dependency direction (code-organization.dependency-direction-layering) against the dependency rule;
public-surface discipline (code-organization.public-interface-minimalism) against the module boundaries;
and the abstraction judgments in code-organization.duplication-and-abstraction against whether a shared
concept may cross a boundary the strategy draws.

This framework is the substrate's analysis of the option space a consumer
chooses within. It does not prescribe one strategy for all codebases;
codebases differ too much in domain complexity, team shape, and expected
longevity for a single answer to fit. Instead it decomposes the strategy
into five sub-decisions, lays out the options and trade-offs for each,
and records the substrate's recommended defaults and the procedure for
choosing. A consumer's own ADR (at /docs/decisions/ADR-XXX-code-
organization-strategy.md) references this framework and records the
choices made, which then satisfies code-organization.organization-strategy.

The problem this framework solves is not "which architecture is best" (a
question with no context-free answer) but "what must a team decide, and
on what grounds, so that the decision is coherent, enforceable, and
checkable." A chosen-and-enforced structure of almost any reasonable
shape beats an unchosen one, because the cost teams actually pay is not
the cost of a slightly-suboptimal style but the cost of having no style
at all: unpredictable placement, eroding boundaries, and changes whose
size has no relation to the size of the requirement that drove them.

## Decision Drivers

The five sub-decisions below are weighed against a common set of drivers,
which the consumer's ADR should state for its own context:

- Team size and topology. One team of three and five teams of eight pull
  toward different boundary policies and repository topologies. Conway's
  observation (that system structure mirrors communication structure) is
  a driver, not a law to fight: boundaries that cut across team lines
  generate coordination cost.
- Domain complexity. A CRUD application over a simple domain needs less
  architectural ceremony than a system with rich, evolving business
  rules. Over-architecting a simple domain is as costly as
  under-architecting a complex one.
- Expected rate and kind of change. If features arrive as vertical slices
  (each touching UI, logic, and storage for one capability), a feature
  or domain organization localizes change; if changes arrive as
  horizontal sweeps (a storage-technology migration), a layered
  organization localizes those instead.
- Deployment topology. A single deployable unit, a modular monolith, and
  a set of independently-deployed services impose different boundary
  hardness and different costs for getting boundaries wrong.
- Testing strategy. A strategy that depends on fast, infrastructure-free
  unit tests of the domain forces a dependency rule that keeps the domain
  free of infrastructure; a strategy leaning on integration tests can
  tolerate looser direction.
- Expected longevity. Code expected to live and evolve for years earns
  more investment in enforced boundaries than a short-lived prototype,
  where the same investment is waste.
- Enforceability. A strategy that cannot be expressed as a checkable
  contract degrades to prose aspiration. The substrate weights
  enforceability heavily: a slightly less elegant strategy that an
  import-linter or ArchUnit contract can hold beats a more elegant one
  that lives only in reviewers' memory.

## Considered Options

### Sub-decision 1: Architectural style

The style sets the top-level shape and, with it, the default dependency
direction the L2 rules check.

- Layered (n-tier). Horizontal layers (presentation, application, domain,
  infrastructure) with dependencies pointing downward. Pros: familiar,
  easy to teach, maps cleanly to a layers contract. Cons: a naive layered
  style lets the domain depend on infrastructure below it, which inverts
  the property most teams actually want; "downward" must be defined so
  the domain is the stable bottom, not the volatile one.
- Hexagonal (ports and adapters). The domain core defines ports
  (interfaces); adapters on the outside implement them; all dependencies
  point inward toward the core. Pros: makes the dependency rule explicit
  and testable, yields an infrastructure-free domain, swappable adapters.
  Cons: more upfront structure; the indirection is overhead for a simple
  domain.
- Clean architecture. A concentric refinement of hexagonal with named
  rings (entities, use cases, interface adapters, frameworks) and the
  dependency rule that source dependencies point only inward. Pros: the
  dependency rule is stated crisply and is highly enforceable. Cons: the
  ceremony of the full ring set is rarely justified outside large,
  long-lived systems.
- Modular monolith. A single deployable composed of internally-strong,
  loosely-coupled modules with enforced boundaries, often organized by
  domain. Pros: the boundary benefits of services without the
  distributed-systems cost; a strong default for most teams. Cons:
  boundaries are convention-enforced, not process-enforced, so they need
  an architecture-test contract to hold.
- Vertical slice. Organize by feature, each slice owning its full stack,
  minimizing sharing between slices. Pros: localizes feature change,
  reduces cross-cutting coupling. Cons: risks duplication across slices
  (intersects code-organization.duplication-and-abstraction) and needs a clear rule for genuinely shared
  kernels.

Substrate-recommended default: a modular monolith organized by domain,
with the dependency rule expressed in hexagonal terms (domain core free
of infrastructure), for a team building a non-trivial, long-lived system
without an established reason to distribute. Simpler domains may justify
a plain layered style; large multi-team systems may justify clean
architecture or a move toward services. The recommendation is a starting
point the consumer overrides with recorded reasons.

### Sub-decision 2: Module-boundary policy

Given a style, how are modules cut?

- By layer (package-by-layer). Group all controllers, all services, all
  repositories. Pros: trivially simple. Cons: a single feature is
  scattered across every layer package, maximizing change-coupling
  (code-organization.module-boundary-cohesion question 3); widely considered an anti-pattern for
  anything beyond the smallest codebase.
- By feature (package-by-feature). Group everything for one feature
  together. Pros: localizes change, eases deletion of a feature. Cons:
  needs a rule for shared code so features do not duplicate or reach into
  each other.
- By domain (package-by-domain / bounded context). Group by the bounded
  contexts of the domain. Pros: boundaries track the shape of the problem
  and tend to be the most stable over time; aligns with team ownership.
  Cons: requires enough domain understanding to identify the contexts,
  which a greenfield team may not yet have.

Substrate-recommended default: organize by domain (or by feature where
the domain's contexts are not yet clear), never by layer above trivial
scale. The boundary policy must be stated clearly enough that a newcomer
can place a new file without asking (code-organization.module-boundary-cohesion question 5 and
code-organization.organization-strategy review question 2).

### Sub-decision 3: The dependency rule and its enforcement mechanism

The dependency rule states which way dependencies must point; the
enforcement mechanism is how the rule is held.

- Direction options: domain-inward (hexagonal/clean: nothing the domain
  depends on may depend on infrastructure); strict downward layering
  (each layer depends only on the one below); acyclic-by-context (bounded
  contexts depend only through published interfaces). The choice follows
  from sub-decisions 1 and 2.
- Enforcement options: import-linter layers and forbidden contracts
  (Python); ArchUnit layered-architecture and slice tests (JVM);
  dependency-cruiser forbidden rules (JS/TS); Go internal/ packages and
  build constraints plus a layer linter; Rust crate and module visibility.
  A cross-language option is a SonarQube architecture rule set or a custom
  graph-assertion script in CI.

Substrate-recommended default: state the rule as domain-inward, and
enforce it with the ecosystem-native architecture-test tool wired into
CI as a required check. The substrate weights this sub-decision heavily:
an unenforced dependency rule does not survive contact with a deadline.
The enforced contract is the same mechanism code-organization.no-import-cycles uses for
acyclicity and code-organization.dependency-direction-layering uses for direction, so the three are
configured together.

### Sub-decision 4: Cross-cutting concern placement

Where do logging, authentication, configuration, error handling, and
similar concerns live, given that they are needed everywhere but must not
invert the dependency rule?

- Options: a thin shared kernel the domain may depend on (for logging
  abstractions, error types); dependency-injected adapters wired at a
  composition root (for anything touching infrastructure); decorators or
  middleware at the edges (for HTTP-level concerns); aspect or
  interceptor mechanisms where the language supports them.

Substrate-recommended default: cross-cutting concerns that the domain
legitimately needs are expressed as abstractions in a thin shared kernel
the domain owns; their infrastructure-touching implementations are
adapters injected at the edge, never imported by the domain. Concerns
that belong only at the boundary (request logging, auth checks) live in
edge middleware. The ADR names the home of each major cross-cutting
concern (code-organization.organization-strategy review question 4).

### Sub-decision 5: Repository topology

Where the choice is live, how is the code distributed across
repositories and deployables?

- Options: single module/repo (smallest projects); modular monolith in
  one repo (the common default); multi-package monorepo (several
  publishable packages, one repo, shared tooling); polyrepo /
  service-per-repo (independently-deployed services, separate repos).

Substrate-recommended default: a modular monolith in a single repository
until a concrete, recorded driver (independent deployment cadence, team
autonomy at scale, divergent scaling needs) justifies splitting. Premature
distribution converts in-process boundary violations, which an
architecture test can catch, into network calls, which it cannot, and
adds operational cost the team may not be ready for. Where topology is
genuinely not in scope (a library), the ADR says so rather than leaving
it blank.

## Decision Outcome

A consumer satisfies code-organization.organization-strategy by recording, in its own ADR, a
choice for each of the five sub-decisions above with its drivers, and by
wiring the dependency rule (sub-decision 3) into CI as an enforced
contract. The substrate's recommended defaults (modular monolith,
organize by domain, domain-inward dependency rule enforced by the
ecosystem-native architecture-test tool, cross-cutting concerns as
domain-owned abstractions with injected adapters, single-repository until
a recorded driver justifies splitting) are a coherent starting point that
fits a broad band of non-trivial, long-lived systems. A consumer that
adopts the defaults wholesale still records that it did so and why,
because the value of the ADR is in making the decision conscious and
checkable, not in its novelty.

The decision is satisfied not when the ADR is written but when the L1 and
L2 gates are configured consistently with it (code-organization.organization-strategy review
question 6): the acyclicity contract, the dependency-direction contract,
and the function-length and complexity thresholds all reflect the recorded
strategy. The ADR and the enforced contracts are two views of one
decision and must agree.

## Substrate Alignment

This framework operationalizes the code-organization.organization-strategy substrate rule and
anchors the four L2 rules of the code-organization concern. It composes
with the infrastructure-security-baseline framework (which selects the
enforcement engine and CI model the architecture-test contracts run
within) and reuses the same enforcement mechanisms the
code-organization.no-import-cycles acyclicity binding and the code-organization.dependency-direction-layering direction
binding reference (import-linter, ArchUnit, dependency-cruiser). The
substrate provides description and analysis; the consumer's ADR provides
the implementation choice. The one-way reference direction is preserved:
this framework names no consumer and embeds no consumer-specific
structure.

## Consequences

Positive: a recorded, enforced strategy makes file placement predictable,
keeps the size of a code change proportional to the size of the
requirement change, and gives the four L2 reviews a concrete reference to
judge against rather than taste. The enforced dependency contract turns
the most expensive structural mistake (a wrong-direction edge unwound
late) into a CI failure caught early.

Negative and costs: authoring the ADR and wiring the contracts is upfront
work that a short-lived prototype may not repay; the substrate's
remediation guidance accordingly lets short-lived code defer. An enforced
contract can also calcify if never revisited, which the review schedule
below mitigates. Choosing a richer style than the domain warrants imposes
indirection cost; the framework's bias toward the modular-monolith default
is meant to resist that over-engineering.

Neutral: the framework deliberately does not pick one style for all
consumers, which means two substrate-conformant codebases can be organized
quite differently. This is intended: conformance is having chosen,
recorded, and enforced a coherent strategy, not having chosen a particular
one.

## References

The decision drivers and options draw on widely-published engineering
concepts: the Single Responsibility and Common Closure principles
(cohesion and the reason-to-change test), the Dependency Inversion and
Stable Dependencies principles (the dependency rule), the Acyclic
Dependencies Principle (the L1-003 foundation), hexagonal and clean
architecture (the domain-inward direction), information hiding (the
public-surface concern), and Don't-Repeat-Yourself with the rule of three
(the duplication-and-abstraction concern). The authoritative-sources
front-matter lists the reference URLs. The substrate paraphrases these
concepts and does not reproduce any source text.

## Decision Review Schedule

Substrate-recommended review cadence for a consumer's code-organization-
strategy ADR: at each of the code-organization.organization-strategy review triggers (a new
codebase or service reaching the point where reorganization is no longer
cheap; a significant architectural shift; the codebase outgrowing its
original organizing principle; repeated L2 escalations tracing to the
strategy) and at minimum annually. At each review the consumer confirms
the recorded strategy still fits the team and domain, that the enforced
contracts still match the recorded rule, and that accumulated exemptions
have not quietly redefined the strategy. This framework itself is
reviewed on the substrate's own cadence and at draft lifecycle until M4
close consolidation promotes it to stable.
