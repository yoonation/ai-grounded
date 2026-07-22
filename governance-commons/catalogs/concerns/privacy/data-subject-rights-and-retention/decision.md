---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: privacy.data-subject-rights-and-retention
title: "Privacy Data-Subject-Rights and Retention Architecture: Erasure Propagation, Portability Format, Request Handling, and the Retention Schedule"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with privacy.data-subject-rights-and-retention. Portfolio-of-sub-decisions structure mirroring the responsible-ai-policy and data-classification-policy precedents: the store inventory, erasure propagation, the portability format, request handling and verification, the retention schedule, and ownership and review cadence, rather than a single option pick. Draft lifecycle per M5 Session 4; stable promotion at M5 close."
authoritative-sources:
  - "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
  - "https://oag.ca.gov/privacy/ccpa"
  - "https://www.iso.org/standard/71670.html"
  - "https://www.nist.gov/privacy-framework"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.privacy-lawful-basis-and-consent-policy
  - decision-frameworks.data-classification-policy
---

# Privacy Data-Subject-Rights and Retention Architecture: Erasure Propagation, Portability Format, Request Handling, and the Retention Schedule

## Context and Problem Statement

Making data-subject rights operable (privacy.data-subject-rights) and retention enforceable
(privacy.retention-limitation) is an architecture problem, not a per-request one. A right that
works in the primary database but not in the cache, the search index, the
warehouse, or the backup is partial in a way the subject cannot see, and a
retention period with no mechanism behind it is a sentence in a policy that the
data never obeys. privacy.data-subject-rights-and-retention requires the architecture be decided and recorded,
because the operability of rights and the enforcement of retention emerge from
how the stores, the propagation, and the schedule cohere, not from any single
handler. The failure this prevents is the erasure that leaves copies behind, the
export assembled from one source while three others are forgotten, and the
retention policy that exists only on paper. This framework pairs with the
lawful-basis and consent policy (privacy.lawful-basis-and-consent-policy): that one decides what may be
processed and why, this one decides how the subject's rights over it are made
real.

## Decision Drivers

- A right is only operable if it reaches every store holding the subject's
  personal data, so the architecture must know the full set of stores.
- Erasure has to propagate to derived and backup copies, including stores that
  cannot be edited in place, so the propagation approach must be explicit.
- Request handling must be reliable and verifiable (identity-checked, tracked,
  completed within the statutory window) rather than ad hoc.
- Retention has to be enforced by a mechanism per category, coordinated with
  the logging-sink retention it cross-references rather than restates.

## Considered Options

The architecture is a portfolio of sub-decisions, not a single option pick.
Each sub-decision below is recorded with its rationale.

### Sub-decision 1: The store inventory

Record the full set of stores that hold the subject's personal data (primary
database, caches, search indexes, queues, warehouses, backups, third-party
processors) so a rights request has a complete target list. The inventory is the
foundation; a right can only be as complete as the inventory it fans out to.
This cross-references data-classification.propagation-inheritance for the data-classification store inventory
rather than duplicating it.

### Sub-decision 2: Erasure propagation

Decide how an erasure reaches every store in the inventory, including stores
that cannot be edited in place. For backups and append-only stores, record the
approach (expiry of the backup window, crypto-shredding by destroying the key,
or tombstoning) so erasure is real rather than best-effort on the primary store
alone.

### Sub-decision 3: The portability format

Fix the export format for portability requests (a structured, commonly used,
machine-readable form) so a portability request produces a usable artifact
rather than a one-off dump.

### Sub-decision 4: Request handling and verification

Decide the request-handling flow: intake, identity verification proportionate to
the sensitivity, fan-out to the stores, a completion record, and the statutory
timing. The flow makes privacy.data-subject-rights testable (an unverified request is not
fulfilled, a fulfilled request reaches every store).

### Sub-decision 5: The retention schedule

Record a retention period per personal-data category and the mechanism that
deletes or irreversibly anonymizes at expiry. Coordinate the retention of any
sink that may hold personal data (logs in particular) with the logging-sink
retention it cross-references (logging.retention-policy) rather than defining a conflicting
period here.

### Sub-decision 6: Ownership and review cadence

State who owns the rights-and-retention architecture and the cadence on which it
is reviewed, including the events (a new store, a new derived copy, a change to
the portability format) that force a review.

## Decision Outcome

The application records a data-subject-rights and retention architecture ADR
covering the six sub-decisions, discoverable from the service documentation and
current relative to the last store or schema change. A simple system's
architecture is short, but it still names every store, the erasure propagation,
the portability format, the request flow, and the retention schedule, so
privacy.data-subject-rights and privacy.retention-limitation have an architecture to rely on rather than
improvising per incident.

## Substrate Alignment

The architecture is the anchor privacy.data-subject-rights (rights operable across stores) and
privacy.retention-limitation (retention enforced) conform to. It pairs with privacy.lawful-basis-and-consent-policy (the
lawful-basis and consent policy) and cross-references data-classification.propagation-inheritance for the store
inventory and logging.retention-policy for logging retention, drawing on those rather than
restating them. It is the operability decision that turns the privacy rights the
lawful-basis policy implies into a system that can actually exercise them.

## Consequences

A recorded architecture makes the subject's rights operable and retention
enforceable across the whole estate, not just the primary store, and gives the
conformance rules an architecture to test against. The cost is the discipline of
maintaining the store inventory and the propagation as the system grows; an
inventory that drifts from reality is the main failure mode, so the architecture
is reviewed when a store is added or a derived copy is introduced.

## References

- GDPR Regulation 2016/679, the data-subject-rights and storage-limitation
  provisions (concept).
- CCPA and CPRA, the access, deletion, and portability provisions (concept).
- ISO/IEC 27701 privacy information management (concept).
- NIST Privacy Framework, the CONTROL function (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed on a periodic cadence and whenever a store is added, a derived copy of
personal data is introduced, the portability format changes, or the retention
schedule is materially revised.
