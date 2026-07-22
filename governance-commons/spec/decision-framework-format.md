<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Decision Framework Format

This document specifies the format used for substrate decision
frameworks. A decision framework is a structured document that
supports engineers in making a judgmental decision: it names the
question, names the trade-offs, asks the contextual questions, and
specifies what documentation the consumer must produce when the
decision is made.

The format is based on MADR (Markdown Any Decision Records) with
substrate-specific extensions. The format is referenced by Charter
Article II (authoring discipline) and the decision-frameworks
README (`../decision-frameworks/README.md`). The front-matter
metadata is an authoring convention enforced by substrate-author
review, not by a mechanical schema.

## Why MADR

MADR is a community-developed format for architectural decision
records, published at https://adr.github.io/madr/. It is:

- Markdown-based, human-authorable and human-readable
- Structurally consistent (predictable section names and order)
- Widely adopted in the architectural decision records community
- Free to use under permissive terms

The substrate adopts MADR's section structure with one important
adaptation. MADR is designed for **decision recording** (the
decision has been made; the document captures the rationale).
Substrate decision frameworks support **decision making** (the
decision has not yet been made; the document helps engineers reach
a deliberate decision and prescribes what their ADR must capture).

The result: substrate decision frameworks use MADR's structure with
content tailored to support upstream of decisions. The consumer
authors a consumer-side ADR (also in MADR format) after applying the
framework.

## File format

Decision frameworks are serialized as Markdown with YAML front
matter. The conventional filename:

```
<decision-name>.madr.md
```

The `.madr.md` suffix signals MADR format with substrate
extensions. The decision name is a short, descriptive slug.

Examples:

- `auth-strategy.madr.md`
- `database-choice.madr.md`
- `microservice-vs-monolith.madr.md`
- `caching-strategy.madr.md`
- `concurrency-model.madr.md`

## Top-level structure

A decision framework document has the following overall shape:

```markdown
---
# YAML front matter with substrate metadata
---

# <Decision title>

## Context and Problem Statement

<what decision is being made and why this question matters>

## Decision Drivers

<the forces pushing the decision in different directions>

## Considered Options

<the alternatives this framework supports>

## Decision Outcome

<intentionally left for consumer to fill in their ADR; this
framework provides scaffolding, not the decision>

## Pros and Cons of the Options

<detailed analysis per option>

## Documentation Required

<what the consumer's ADR must capture per Charter Article II
discipline>

## More Information

<authoritative sources, references, related frameworks>
```

The substrate uses standard MADR sections with the addition of
`Documentation Required`, which specifies what the consumer must
produce in their own ADR after applying this framework.

## Front matter

The YAML front matter carries substrate metadata about the
framework itself.

Required fields:

```yaml
---
framework-id: decision-frameworks.<decision-name>
title: <human-readable title>
lifecycle-status: draft | stable | deprecated | retired
commons-version: <commons version>
framework-version: <framework's own version>
author: <human identity>
authored: <ISO 8601 date>
---
```

Optional fields:

```yaml
---
reviewer: <distinct human identity>
reviewed: <ISO 8601 date>
ai-assistance: <description per Charter Article II Section 2.2>
authoritative-sources:
  - <URL or canonical reference>
  - <URL or canonical reference>
entered-status-at: <ISO 8601 date>
superseded-by: <framework identifier when deprecated>
deprecation-window-ends: <ISO 8601 date when deprecated>
related-frameworks:
  - <related framework identifier>
---
```

Front matter is required on every framework. Substrate tooling reads
it for validation, indexing, and lifecycle tracking.

## Identifier convention

Framework identifiers follow:

```
decision-frameworks.<decision-name>
```

The identifier is immutable per Charter Article IV Section 4.1 once
the framework reaches stable lifecycle status.

Layer 3 rules in concern catalogs reference frameworks by this
identifier through the `decision-framework` part per
`catalog-format.md`. The framework's own front matter declares the
identifier; tooling cross-validates the reference.

## Section requirements

### Context and Problem Statement (required)

States the decision being supported. The substrate's convention:
phrase as a question the consumer is trying to answer, not as a
statement of the decision-maker's situation.

Good: "What authentication strategy should this service use?"

Less good: "We need to decide on authentication."

The question framing matters because it makes the framework's
purpose explicit. A framework that does not answer a specific
question well does not belong here.

The section includes:

- The decision question
- Why this question matters (consequences of getting it wrong, of
  not deciding deliberately)
- Scope (what kinds of services/contexts this framework supports;
  what is out of scope)

### Decision Drivers (required)

The forces pushing the decision in different directions. Each
driver is a factor that makes one option more attractive than
others. Drivers conflict with each other; that conflict is what
makes the decision genuinely judgmental.

Authoring discipline: state each driver as a measurable or
observable factor, not as a value. "Latency under 100ms" is a
driver. "Performance" is not (too vague).

Common drivers across many frameworks:

- Performance requirements (specific latency, throughput targets)
- Operational complexity tolerance
- Team expertise distribution
- Compliance requirements
- Cost constraints
- Time-to-market pressure
- Future flexibility requirements

Frameworks should specify drivers relevant to their decision, not
list generic drivers.

### Considered Options (required)

The alternatives this framework supports. Three to seven options is
typical; more becomes unwieldy. Authoring discipline:

- Each option is a real, named approach (not "use a framework," but
  "use OAuth 2.0 Authorization Code flow with PKCE")
- Each option appears in real-world systems (citations to examples
  in the More Information section)
- Options are mutually distinguishable (if two options reduce to
  the same decision, merge them)
- Anti-patterns are named separately, in their own section if the
  framework includes them

The framework does not rank options. Each is acceptable when its
trade-offs are documented per the Pros and Cons section.

### Decision Outcome (intentionally minimal)

In MADR, this is where the decision is recorded. In substrate
decision frameworks, this section is intentionally minimal because
the substrate is not making the decision.

Conventional content:

```markdown
## Decision Outcome

Consumer chooses one of the Considered Options based on their
specific context. The chosen option is documented in a consumer-
side ADR that captures the rationale per the Documentation
Required section below.

This framework does not select a default option. Every option is
acceptable when its trade-offs match the consumer's drivers.
```

A framework that prescribes the answer is a rule, not a framework.
If the substrate has reached a position on which option is correct
in general, that belongs in a Layer 2 rule with examples, not in a
Layer 3 framework.

### Pros and Cons of the Options (required)

Detailed analysis per option. Each option gets a subsection with
explicit pros and cons. Authoring discipline:

- Cons named even if the option is the author's favorite
- Pros named even if the option is unfashionable
- Trade-offs are quantitative where possible (latency numbers,
  cost ranges, operational complexity measured by some scale)
- Trade-offs are honest about uncertainty (if a claim about an
  option's performance is contested, say so)

Each option's analysis includes:

- **What it is**: brief description
- **When it works well**: contexts where this option dominates
- **When it works poorly**: contexts where this option struggles
- **Pros**: bulleted list
- **Cons**: bulleted list
- **Operational considerations**: ongoing costs, monitoring
  needs, team expertise required

### Documentation Required (required, substrate extension)

What the consumer must produce in their own ADR after applying
this framework. This is the substrate's coupling to Charter
Article II Section 2.2 provenance discipline at the consumer
side.

Conventional content:

```markdown
## Documentation Required

When this framework is applied, the consumer produces an ADR in
their repository (conventionally at `docs/decisions/`) containing:

- Which option was chosen
- Which decision drivers from this framework applied to the
  consumer's specific context, with weights or rankings
- Which considered options were evaluated and why each was
  selected or rejected
- Trade-offs accepted with the chosen option
- Conditions under which this decision should be revisited
- Provenance: who made the decision, when, with what AI
  assistance
```

The Documentation Required section is what makes Layer 3 rules
auditable. A consumer-side ADR that addresses every point above
provides evidence the framework was applied deliberately rather
than skipped.

### More Information (required)

Authoritative sources and references. Authoring discipline:

- Cite the foundational texts, papers, and analyses that inform
  the framework's content
- Cite real-world examples for each considered option where
  public information allows
- Cite related substrate frameworks consumers may also need
- Cite community resources (Stack Overflow, Wikipedia, blog
  posts) only when they are pedagogically useful, not as
  authoritative sources

References use markdown link syntax for human readability. The
front matter `authoritative-sources` field carries the same
references in a machine-readable form for tooling.

## Anti-pattern section (optional)

When a framework's decision space includes notable anti-patterns
(approaches that consistently fail), the framework may include a
separate section:

```markdown
## Anti-Patterns

The following approaches consistently fail across many contexts
and are not Considered Options. They are documented here so
consumers recognize them when proposed.

### <Anti-pattern name>

<description>

**Why it fails**: <explanation>

**Common substitute**: <which Considered Option typically
replaces this in practice>
```

Anti-patterns are documented because they recur. Without
explicit documentation, consumers and AI agents repeatedly
consider them, requiring repeated rejection.

## Worked example section (optional)

Some frameworks benefit from a worked example showing how a
specific consumer applied the framework to their context. The
example is illustrative, not prescriptive.

```markdown
## Worked Example

Consider a fictional consumer: a B2B SaaS payment service with
50 engineers and SOC 2 compliance obligations.

### Decision Drivers (consumer-specific weights)

- Compliance: high (SOC 2 is a hard requirement)
- Performance: medium (sub-200ms p99)
- Operational complexity: high (small ops team)

### Evaluation

- Option A: rejected because of operational complexity
- Option B: selected because compliance and operational fit
- Option C: rejected because performance ceiling

### Outcome

Consumer chooses Option B. The ADR captures the rationale,
including conditions that would trigger reevaluation (team size
above 100, p99 requirement below 50ms, etc.).
```

Worked examples are particularly useful for AI agents traversing
frameworks; they help the AI recognize how reasoning over drivers
produces a decision.

## Length expectations

Decision frameworks are typically 500 to 1500 lines of markdown
total. Shorter frameworks may not provide enough depth; longer
frameworks become exhausting to consult. The substrate's authoring
discipline aims for the middle of that range.

The Pros and Cons section is typically the longest. The Context,
Decision Drivers, and Documentation Required sections are typically
the shortest.

## Cross-references

### From frameworks to other substrate content

Frameworks reference other substrate content through markdown links
and through the front-matter `related-frameworks` field. Common
references:

- Concern catalog Layer 3 rules that point to this framework
- Concern catalog Layer 1 or Layer 2 rules that constrain the
  decision space
- Threat catalog rules that influence specific options
- Compliance controls that constrain specific options
- Other decision frameworks that this one depends on or relates to

### From substrate content to frameworks

Concern catalogs reference frameworks via the `decision-framework`
part per `catalog-format.md`. Profiles do not reference frameworks
directly; selection happens through the catalog rules that
reference frameworks.

Manifests reference frameworks in checkpoint `consults.decision-
frameworks` entries when the consumer's workflow anticipates Layer
3 decisions at that checkpoint.

## Validation

Decision frameworks are L3 judgmental content and are not mechanically
schema-validated. Substrate-author review enforces the front-matter
conventions:

- Required front matter fields present
- Lifecycle status values within allowed enumerations
- Identifier format correct
- Version fields well-formed

Content validation (required sections present, sections non-empty,
etc.) requires markdown parsing. Substrate tooling that consumes
frameworks performs this validation; manual review per Charter
Article II Section 2.4 catches semantic gaps.

## Versioning

Frameworks are versioned per Charter Article VIII Section 8.4.
Framework version is independent from commons version.

Framework version increments:

- Patch: typos, formatting, clarifying language
- Minor: new Considered Options added; new Decision Drivers added;
  Worked Examples added; references updated
- Major: framework intent changes (the decision being supported
  shifts); options removed; structure changes

Material content updates that change the framework's intent require
a new framework with a new identifier per Charter Article IV
Section 4.2. The substrate does not silently rewrite frameworks.

## Lifecycle

Frameworks follow the same lifecycle as catalog content per
`rule-lifecycle.md`. Particularly relevant transitions:

- Frameworks enter draft status when first authored
- Promotion to stable requires second-human review per Charter
  Article II Section 2.4
- Frameworks are deprecated when:
  - A new framework with broader or clearer scope is authored
  - The decision space changes materially (new options become
    standard; old options become obsolete)
- Deprecated frameworks remain consultable through the deprecation
  window per Charter Article VIII Section 8.3

## What the format does not specify

- **The format does not specify the decision itself.** That is the
  consumer's responsibility to make and document.
- **The format does not specify ADR storage.** Consumers store
  ADRs wherever their convention dictates (`docs/decisions/`,
  `adr/`, etc.).
- **The format does not specify ADR format.** While MADR is
  recommended for consumer ADRs (consistent with substrate
  framework format), consumers may use other ADR formats per their
  discipline.
- **The format does not specify framework rendering.** Documents
  are markdown; how they display in consumer tooling is consumer's
  choice.

## Cross-references

- `../CHARTER.md` Article II Section 2.3 (authoring discipline:
  examples, severity rationale, layer rationale; the framework
  format encodes these for Layer 3 content)
- `../CHARTER.md` Article IV (framework identifier and intent
  immutability)
- `../spec/catalog-format.md` (catalog Layer 3 rules reference
  frameworks)
- `../spec/rule-lifecycle.md` (framework lifecycle)
- `../decision-frameworks/README.md` (orientation and reading
  order)
- https://adr.github.io/madr/ (MADR base format)
