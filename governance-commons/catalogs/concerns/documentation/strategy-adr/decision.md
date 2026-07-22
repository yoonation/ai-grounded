---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: documentation.strategy-adr
title: "Documentation Strategy Policy"
lifecycle-status: stable
commons-version: "0.8.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-05"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M6 close consolidation (2026-06-06) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M6 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-06. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent following the backup-recovery-strategy.madr.md precedent; fourth and final decision framework authored in Milestone 6; exercises the established MADR pattern for the documentation concern. SPDX header placed as YAML comments inside frontmatter per Section 10 settled decision 15. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft. Substrate-author review required for stable promotion at the M6 close."
authoritative-sources:
  - "https://diataxis.fr/"
  - "https://keepachangelog.com/en/1.1.0/"
  - "https://adr.github.io/madr/"
---

# Documentation Strategy Policy

This decision framework provides the substrate's analysis of the
documentation strategy decisions a consumer must make. Consumers reference
this framework when authoring their own ADR documenting what they document,
to what standard, where it lives, and how it stays accurate. The
substrate-recommended location for the consumer's ADR is
`/docs/decisions/ADR-XXX-documentation-strategy.md`.

The framework is referenced by substrate rule documentation.strategy-adr, which requires the
consumer to have an explicit, recorded documentation strategy. Consumers
satisfy documentation.strategy-adr by authoring an ADR that adapts the analysis here to
their context.

The lower-layer documentation rules enforce the consequences of this
strategy: documentation.public-api-documented requires public surfaces to carry a doc comment,
documentation.no-placeholder-documentation requires shipped documentation to be free of placeholders,
documentation.accuracy-and-sync requires documentation to stay accurate and in sync, and
documentation.decisions-and-operations requires decisions and operational knowledge to be recorded. This
framework is where the consumer decides the surface those rules then police.

## Context

Documentation strategy is a set of decisions about what to document, to what
standard, where it lives, and how it stays true. Left implicit, the result
is inconsistent: some modules over-documented, public contracts bare,
decisions unrecorded, and no shared notion of what good documentation is.
The Diataxis framework offers a useful decomposition of documentation into
distinct kinds (tutorials, how-to guides, reference, and explanation) that
serve different reader needs, which helps a consumer decide what each surface
requires. The substrate cannot make these decisions for the consumer because
they depend on the consumer's audience, toolchain, and release model. The
substrate provides recommended defaults and documents the trade-offs so the
consumer can deviate deliberately.

## Decision Drivers

- Accuracy over volume: documentation that is wrong is worse than absent, so
  the strategy prioritizes keeping documentation true over documenting
  everything.
- Reader-fit: documentation serves a reader's task; the kinds of
  documentation a surface needs follow from who reads it and why.
- Durability of knowledge: decisions and operational knowledge survive the
  departure of the people who hold them.
- Discoverability: documentation that cannot be found is not documentation.
- Enforceability: the per-surface standard is concrete enough for the
  lower-layer rules to check.
- Sustainability: the documentation burden is proportionate, so the
  discipline is maintained rather than abandoned.

## Considered Options

### What must be documented and to what standard per surface

Option A, document everything uniformly: produces noise, over-documents
internals, and is unsustainable. Rejected.

Option B, per-surface standards: the public API surface is documented to a
reference standard (documentation.public-api-documented); internal modules are documented where
non-obvious; decisions and operations are recorded per documentation.decisions-and-operations; the
standard for each surface is concrete enough to enforce.

Substrate-recommended default: Option B, with the public surface as the
non-negotiable floor and internal documentation guided by non-obviousness.

### Where documentation lives and how it is discovered

Option A, scattered (wherever each author put it): undiscoverable. Rejected.

Option B, a defined home with a single obvious entry point: doc comments
with the code, narrative and reference docs in a known docs location,
decisions in a decisions directory, the changelog at the repository root,
all linked from one entry point.

Substrate-recommended default: Option B.

### How documentation stays accurate

Option A, periodic cleanups: documentation drifts between cleanups and is
trusted while stale. Rejected as the primary mechanism.

Option B, accuracy as part of the change plus verification: the
documentation update travels with the change that alters behavior, and
examples are executed so drift fails a check (documentation.accuracy-and-sync).

Substrate-recommended default: Option B, with a periodic accuracy review of
high-traffic documents as a backstop.

### Decision-record convention and significance threshold

Option A, none: decisions live in memory and chat. Rejected.

Option B, a decision-record convention (the substrate ships MADR as the
companion format) with an explicit threshold for what counts as
architecturally significant, so the team records the decisions that matter
without recording trivia.

Substrate-recommended default: Option B, MADR-format decision records with a
consumer-defined significance threshold.

### Changelog convention

Option A, none or commit-log-only: consumers reconstruct change history from
commits. Rejected for consumer-visible software.

Option B, a maintained changelog (the substrate references the Keep a
Changelog convention) with an entry per consumer-visible release.

Substrate-recommended default: Option B.

### Placeholder and known-gap convention

Option A, allow placeholders to ship: defeats reader trust silently
(documentation.no-placeholder-documentation). Rejected.

Option B, no placeholders in shipped documentation; a gap is either filled
or recorded as an explicit, visible known-gap notice that the placeholder
rule is configured to allow.

Substrate-recommended default: Option B.

### Ownership and review cadence

Option A, unowned: the strategy and the documentation drift. Rejected.

Option B, a named owner and a review cadence, with the strategy revisited on
toolchain or significance-threshold changes.

Substrate-recommended default: Option B.

## Decision Outcome

The substrate-recommended strategy for the common case: per-surface
documentation standards with the public surface as the floor; a defined
documentation home with a single entry point; accuracy maintained as part of
the change and verified by executing examples; MADR-format decision records
with a defined significance threshold; a maintained changelog per
consumer-visible release; no placeholders in shipped documentation with
visible known-gap notices instead; and an owned, periodically reviewed
strategy. Consumers deviate deliberately and record the deviation and its
rationale in their ADR.

## Substrate Alignment

This framework is the L3 companion to the documentation catalog. It draws
boundaries to sibling concerns rather than absorbing them. The arrangement,
naming, and layering of the code is owned by code-organization, which this
strategy documents rather than redefines. The operational telemetry,
dashboards, and alerts a runbook references are owned by observability and
monitoring-alerting; the runbook is documentation, the signals it points to
are not. The test-suite discipline that may execute documentation examples
is owned by testing; this concern owns that the examples exist and are
accurate. The substrate's own internal specification and authoring documents
are not consumer documentation and are out of scope. The strategy records
how each boundary is honored rather than restating the sibling rules.

## Consequences

Positive: consistent documentation to one enforceable standard; a public
surface that is self-describing; documentation that can be trusted because
it is kept accurate; decisions and operational knowledge that survive
turnover; honest documentation free of placeholders.

Negative or cost: maintaining accuracy as part of every behavior-altering
change and recording decisions and changelog entries is an ongoing
discipline tax; the strategy keeps it proportionate by prioritizing accuracy
and the public surface over exhaustive coverage.

## References

See the authoritative-sources frontmatter: the Diataxis documentation
framework (kinds of documentation and the reference-documentation standard),
the Keep a Changelog convention (change records), and the MADR format
(decision records).

## Decision Review Schedule

The consumer's ADR is reviewed at substrate adoption, at a change to the
documentation toolchain or hosting, at a change to what counts as an
architecturally significant decision, and on a substrate-recommended annual
cadence.
