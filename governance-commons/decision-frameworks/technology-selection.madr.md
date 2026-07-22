---
framework-id: decision-frameworks.technology-selection
title: Technology Selection
lifecycle-status: stable
commons-version: 1.1.0
framework-version: 0.1.0
author: myoung
authored: 2026-06-28
entered-stable: 2026-06-29
reviewer: myoung-self-attested
reviewed: 2026-06-29
ai-assistance: >
  AI drafted the framework structure and substrate-original prose against
  spec/decision-framework-format.md, realizing the technology-selection gap that
  staff-engineer flagged when its inline canon moved to the substrate. The human
  authors intent and ratifies per Charter Article II; the framework entered draft
  and was promoted to stable under Charter Section 2.4.1 solo-author attestation.
authoritative-sources:
  - https://mcfunley.com/choose-boring-technology
  - https://www.thoughtworks.com/radar
  - https://adr.github.io/madr/
related-frameworks: []
---

# Technology Selection

## Context and Problem Statement

What technology should this project adopt to satisfy a given need, when several
candidates exist?

The need might be a language, a framework, a datastore, a message broker, a
significant library, a managed or SaaS service, or a vendor. The question matters
because a technology choice is sticky in a way most code is not: it shapes hiring,
operations, architecture, and cost for years, and reversing it later is expensive
and risky. Choosing by novelty, by familiarity alone, or by what is trending
produces predictable, recurring failure. This framework names the forces, the
stances available, and what the consumer must record so the choice is made
deliberately rather than by default or by enthusiasm.

Scope. In scope: adopting a new technology into a project's stack where the choice
carries lock-in, operational burden, or a meaningful learning cost (languages,
frameworks, datastores, brokers, major libraries, managed services, vendors). Out
of scope: choosing between two designs within a technology already adopted (that is
an architecture decision, not a selection), and trivial library picks with no
lock-in and a cheap exit (just pick one and move on; this framework would be
ceremony there).

## Decision Drivers

The forces below pull in different directions; that conflict is what makes the
choice judgmental rather than mechanical. State each as an observable factor for the
specific candidate, not as a value. The set is the technology-selection checklist,
formalized.

- Fit for the problem: does the candidate solve the actual requirement, not an
  adjacent or larger one. A tool that solves a superset adds carrying cost for
  capability you do not need.
- Team familiarity and learning cost: does the team already operate it, and if not,
  what is the ramp to competence and to on-call confidence.
- Operational maturity: production track record at the scale you expect, release
  history, documented and understood failure modes, age past the early-adopter
  phase.
- Maintenance and community health: active maintainers, release cadence, issue and
  security-response time, and bus factor (one maintainer is a risk).
- Total cost of ownership: licensing plus infrastructure plus the operational
  headcount, training, and migration cost over the expected lifetime, not the
  sticker cost today.
- Failure mode and blast radius: how it fails, whether it degrades or falls over,
  how recoverable the failure is, and how far the failure spreads.
- Licensing: license compatibility with the project, copyleft obligations, and
  commercial terms including cost growth at scale.
- Vendor lock-in and exit cost: proprietary formats or APIs, data portability, and
  the concrete cost of switching away later.
- Security posture: CVE history, patch cadence, and supply-chain hygiene (signed
  releases, reproducible builds, dependency hygiene).
- Scalability headroom: does it meet projected load, not just current load, without
  a re-platform.
- Reversibility: how cheaply the choice can be undone if it proves wrong, which is
  the single best hedge against the uncertainty in all the drivers above.

These conflict in normal cases. The most familiar option is often not the best fit;
the best-fit emerging option is often the least mature; the lowest-TCO managed
option is often the highest lock-in. Weighing the conflict against the project's
context is the decision.

## Considered Options

Five stances for making the selection. They are approaches to choosing, not specific
products. A consumer applies one stance (or a blend) and lands on a concrete
technology.

1. Boring and proven: default to mature, widely deployed, well understood technology
2. Best-fit emerging: adopt newer technology that fits the problem markedly better
3. Standardize on the existing stack: minimize stack diversity by reusing what the
   team already runs
4. Buy or managed service: offload operation of the capability to a vendor
5. Build in-house: author a bespoke solution

## Decision Outcome

Consumer chooses one of the Considered Options (or a deliberate blend) based on their
specific context. The chosen option and the concrete technology are documented in a
consumer-side ADR that captures the rationale per the Documentation Required section
below.

This framework does not select a default option. Every option is acceptable when its
trade-offs match the consumer's drivers. A framework that prescribed the answer would
be a rule, not a framework.

## Pros and Cons of the Options

### 1. Boring and proven

What it is: prefer technology that is mature, widely deployed, and well understood,
spending the project's limited novelty budget only where novelty buys a real
advantage. The canonical articulation is "choose boring technology."

When it works well: most line-of-business needs, small teams, thin on-call coverage,
and anywhere the technology is a means rather than the product itself.

When it works poorly: when the problem genuinely sits outside what proven tools do
well, and forcing a mature-but-wrong tool costs more than adopting a better-fit newer
one.

Pros:
- Deep operational knowledge exists, in the team and on the public internet
- Failure modes are documented and the hiring pool is large
- Low surprise: the unknowns are mostly known

Cons:
- Can leave real efficiency or capability on the table when a newer tool fits better
- "Boring" can shade into stagnation if applied without judgment

Operational considerations: lowest ongoing learning and on-call cost; the main risk
is under-serving a need that actually warranted novelty.

### 2. Best-fit emerging

What it is: adopt a newer technology because it fits the problem markedly better than
mature alternatives, accepting lower maturity in exchange for fit.

When it works well: when the fit advantage is large and measurable, the team has
capacity to absorb a less-trodden path, and the choice is reversible enough that
being early is survivable.

When it works poorly: when the fit advantage is marginal or speculative, or when the
team has no slack to absorb sharp edges, missing documentation, and breaking changes.

Pros:
- Can deliver a capability or efficiency the mature options cannot
- Positions the project well if the technology becomes standard

Cons:
- Thinner documentation, smaller hiring pool, more breaking changes
- Higher chance the technology is abandoned or pivots
- Failure modes are less charted, so incidents take longer to resolve

Operational considerations: budget for the team to become the local experts, because
the internet will not yet have your answer; pair with high reversibility.

### 3. Standardize on the existing stack

What it is: reuse a technology the team already runs rather than introducing a new
one, valuing stack consolidation over per-need optimization.

When it works well: when the existing technology is an adequate fit, and the
marginal operational cost of one more distinct technology (another thing to patch,
monitor, staff, and reason about) outweighs a modest fit gain.

When it works poorly: when the existing technology is a poor fit and standardizing
forces a square peg into a round hole, accumulating workarounds that cost more than
the new technology would have.

Pros:
- No new operational surface, no new on-call competence to build
- Shared tooling, monitoring, and expertise amortize across uses

Cons:
- Risks the golden-hammer trap, using one tool for everything regardless of fit
- Can entrench an aging technology past the point it should have been replaced

Operational considerations: the cheapest stance operationally; guard against using it
to avoid a genuinely warranted new adoption.

### 4. Buy or managed service

What it is: pay a vendor to operate the capability (a managed database, a hosted
queue, an authentication provider) rather than running it yourself.

When it works well: when operating the capability well is hard and not the project's
differentiator, the team is small, and the managed option's reliability exceeds what
the team could achieve.

When it works poorly: when the capability is core to the product (outsourcing the
differentiator), when cost scales badly with growth, or when lock-in and data
portability are unacceptable.

Pros:
- Offloads operational burden, patching, and much of the reliability work
- Faster time to market; smaller ops footprint

Cons:
- Ongoing cost that can grow sharply with scale
- Vendor lock-in and exit cost; data portability must be checked up front
- Less control over failure modes and maintenance windows

Operational considerations: read the pricing curve at projected scale, not current
scale, and confirm a concrete exit path before committing.

### 5. Build in-house

What it is: author a bespoke solution rather than adopting an existing technology.

When it works well: when the need is genuinely the project's differentiator and no
existing option fits, or when every option carries unacceptable lock-in and the
capability is small and well understood.

When it works poorly: for anything that is a solved, commodity problem, where
building duplicates a maintained solution and creates a permanent maintenance
liability. This is the not-invented-here trap and connects to the
reinventing-the-standard-library code smell.

Pros:
- Exact fit and full control
- No external lock-in or licensing constraint

Cons:
- The full lifetime cost of building, maintaining, securing, and documenting it
  falls on the team forever
- Almost always underestimated; the commodity case is rarely worth it

Operational considerations: the highest long-run ownership cost; justify it only for
a true differentiator or a small, well-bounded capability with no acceptable
off-the-shelf option.

## Anti-Patterns

The following are not Considered Options. They are documented so consumers and AI
agents recognize and reject them when proposed.

### Resume-driven development

Choosing a technology to gain or showcase experience with it rather than to fit the
problem.

Why it fails: optimizes for the individual's career surface, not the system's needs,
and leaves the team operating a choice made for the wrong reason.

Common substitute: Boring and proven, or Best-fit emerging when fit (not resume)
actually justifies the newer tool.

### Hype-driven adoption

Choosing a technology because it is trending, has conference momentum, or is what a
large company reportedly uses, without checking fit for this context.

Why it fails: another organization's constraints are not yours; their scale,
staffing, and problem are usually different, so their choice does not transfer.

Common substitute: run the drivers honestly; the trend may or may not survive that.

### Not-invented-here

Rebuilding a capability that a maintained, well-fit technology already provides.

Why it fails: creates a permanent maintenance and security liability to avoid a
dependency that would have been cheaper to adopt.

Common substitute: Buy or managed service, or adopt the existing library; reserve
Build in-house for genuine differentiators.

### One-size-fits-all

Mandating a single technology across every need regardless of fit, the rigid form of
the standardize stance.

Why it fails: turns a reasonable bias toward consolidation into a refusal to weigh
fit, accumulating workarounds.

Common substitute: standardize as a default, but allow a documented exception when
fit clearly warrants it.

## Worked Example

Consider a fictional consumer: a small team (eight engineers, one on-call rotation)
adding a background job queue to an existing Python service backed by PostgreSQL.

### Decision Drivers (consumer-specific weights)

- Team familiarity: high weight, because on-call is thin and learning a new system is
  costly
- Operational maturity: high weight, the queue must not become a 2 a.m. surprise
- Fit for the problem: medium, the workload is modest at thousands of jobs a day
- Lock-in: low weight, jobs are internal and re-runnable
- Total cost of ownership: medium

### Evaluation

- Build in-house: rejected as not-invented-here for a solved problem at this scale
- Best-fit emerging (a new specialized queue): rejected because the fit advantage is
  marginal at thousands of jobs a day and maturity weighs heavily here
- Buy or managed service (a hosted queue): viable, but adds a vendor and a second
  datastore to operate and reason about
- Standardize on the existing stack: the team already runs PostgreSQL reliably, so a
  Postgres-backed queue reuses operational knowledge, backups, and monitoring

### Outcome

Consumer chooses the standardize stance with a Postgres-backed queue. The ADR records
that the choice holds while volume stays modest, and names the revisit trigger:
sustained volume or latency requirements that outgrow a database-backed queue, at
which point the managed-service option is reconsidered.

## Documentation Required

When this framework is applied, the consumer produces an ADR in their repository
(conventionally at `docs/decisions/`) containing:

- Which technology was chosen, and under which stance (option) above
- Which decision drivers applied to the consumer's specific context, with weights or
  rankings, including the conflicts that had to be resolved
- Which considered options and concrete candidates were evaluated, and why each was
  selected or rejected
- The trade-offs accepted with the chosen technology, explicitly including lock-in
  and exit cost where relevant
- The conditions under which this decision should be revisited (a scale threshold, a
  licensing change, a maintainer going dormant, a team-size change)
- Provenance: who made the decision, when, and with what AI assistance, per Charter
  Article II Section 2.2

An ADR that addresses every point above is the evidence that the framework was
applied deliberately rather than skipped.

## More Information

- Dan McKinley, "Choose Boring Technology," the canonical argument for spending a
  finite novelty budget deliberately: https://mcfunley.com/choose-boring-technology
- ThoughtWorks Technology Radar, a running characterization of which technologies are
  worth adopting, trialing, assessing, or holding: https://www.thoughtworks.com/radar
- The buy-versus-build and lock-in trade-offs recur across architecture literature;
  evaluate them against the drivers here rather than against any single source's
  default.
- MADR base format: https://adr.github.io/madr/
- Related substrate content: the design-patterns catalogs (`solid.yaml`,
  `design-principles.yaml`) inform how a chosen technology is then used well; the
  `dependency-management` and `supply-chain` concerns constrain the security and
  provenance drivers above.
