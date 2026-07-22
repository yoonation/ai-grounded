---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: data-classification.data-classification-policy
title: "Data-Classification Policy: Scheme, Determination, Per-Class Handling, Propagation, Tag Binding, and Ownership"
lifecycle-status: stable
commons-version: "0.6.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M4 close consolidation (2026-06-01) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M4 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-01. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with data-classification.data-classification-policy substrate rule. Portfolio-of-sub-decisions structure mirroring the caching-strategy and data-access-performance-strategy MADR precedents: six sub-decisions (the scheme and closed vocabulary, the determination rule including aggregation, the per-class handling matrix, the propagation rules, the tag-and-label binding to infrastructure-misconfiguration.governance-tagging, and ownership and review cadence) plus a review cadence, rather than a single option pick. Draft lifecycle per M4 Session 6; stable promotion at M4 close."
authoritative-sources:
  - "https://csrc.nist.gov/pubs/fips/199/final"
  - "https://csrc.nist.gov/pubs/sp/800/60/v1/r1/final"
  - "https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final"
  - "https://csrc.nist.gov/pubs/sp/800/88/r1/final"
  - "https://www.iso.org/standard/27001"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.caching-strategy
---

# Data-Classification Policy: Scheme, Determination, Per-Class Handling, Propagation, Tag Binding, and Ownership

## Context and Problem Statement

Any application that stores business or personal data has a data-
classification policy. The only choice is whether it is decided and written
down or left to accrete from whatever each author happened to label. DATA-
L3-001 requires that the policy be explicit, because data classification is
a system property that emerges from how a set of decisions cohere, not from
any one of them. The mechanical rules (a label exists, a label is in
vocabulary, classified data is not logged) and the semantic rules
(classification correctness, encryption per class, access per class,
retention per class, propagation) are each local conformance checks; what
they conform to is this policy. The failure this prevents is the pile of
locally reasonable decisions that do not cohere: one team's labels differ
from another's, a class is encrypted in one store and not the next, an
aggregate is classified by guess, and a sensitive value is logged because no
one wrote down that its class forbids it.

This policy is also the authoritative source for the data-sensitivity
vocabulary that infrastructure-misconfiguration infrastructure-misconfiguration.governance-tagging enforces as tags
at provision time, and it is the classification substrate the privacy
concern (scheduled in M5) will build its personal-data obligations on.

## Decision Drivers

- The sensitivity of the data the application actually holds, and the harm
  of its exposure.
- The regulatory and contractual obligations that attach to particular data
  (personal data, payment data, health data), recorded here as drivers and
  elaborated by the privacy concern.
- The need for one closed vocabulary that the application labels, the
  infrastructure tags, and the handling rules all key off.
- The operational cost of the per-class controls (encryption, minimized
  access, retention disposal), balanced against the exposure they prevent.

## Considered Options

The policy is a portfolio of six sub-decisions. Each is recorded with the
option chosen and the drivers that selected it.

### Sub-decision 1: The scheme and closed vocabulary

Decide the set of classes and their order. The substrate default is a
four-class tiered scheme (public, internal, confidential, restricted), the
same vocabulary infrastructure-misconfiguration infrastructure-misconfiguration.governance-tagging enforces as
data-sensitivity tags. The options are depth levels: the four-class default
for most applications, a coarser three-class scheme for a simple system, or
a finer scheme with sub-classes for a regulated one. The driver is the range
of sensitivity the data actually spans. Whatever is chosen is closed (a
fixed, agreed set) so that every label, tag, and handling rule joins to it;
data-classification.closed-vocabulary checks labels against this vocabulary.

### Sub-decision 2: The determination rule, including aggregation

Decide how the class of a data element is determined: the rule that maps
what a datum is to its class. The options range from a simple field-type
mapping (this field type is always confidential) to a data-content rule
(classify by what the field can contain, including free text) to a
risk-based assessment for a regulated system. The rule must address
aggregation: a combination of lower-class fields that together reveal a
higher-class fact takes the higher class, and derived or aggregated data
takes the most restrictive class of its inputs. The driver is how the data
combines and derives. This rule is what data-classification.classification-correctness checks classification
correctness against.

### Sub-decision 3: The per-class handling matrix

Decide, for each class, the handling it requires across encryption (at rest
and in transit), access (the need-to-know posture and audit), retention (the
period and disposal), logging (whether the class may appear in logs and
under what masking), and masking or redaction in non-production environments.
The driver is the exposure each class represents. This matrix is what
data-classification.encryption-per-class (encryption), data-classification.access-least-privilege (access), and data-classification.retention-disposal (retention)
check the per-class controls against, and what data-classification.no-classified-data-in-logs (no classified
data in logs) draws its logging line from.

### Sub-decision 4: The propagation rules

Decide how class travels when data moves: that a copy, a derived view, an
export, a message on a bus, or a cached value carries at least the class of
its source, that combinations take the most restrictive input class, and
which destinations each class may reach (which classes may be cached in which
tier, exported to which target, sent to which third party). The driver is the
set of data flows out of the system of record. These rules are what
data-classification.propagation-inheritance checks, and they own the what-may-be-cached-where constraint the
performance-caching concern cross-references.

### Sub-decision 5: The tag-and-label binding

Decide how the scheme binds to the two places it is expressed: the
application's classification labels (the annotations data-classification.model-classification-label and
data-classification.closed-vocabulary govern) and the infrastructure data-sensitivity tags
(infrastructure-misconfiguration infrastructure-misconfiguration.governance-tagging). The decision is that the policy
vocabulary is the single source of truth and both the application labels and
the infrastructure tags draw their values from it, so that a datum's class in
code and the data-sensitivity tag on the store that holds it agree. The
driver is the need for the application layer and the infrastructure layer to
speak the same classification language.

### Sub-decision 6: Ownership and review cadence

Decide who owns the policy, who classifies new data, and when the policy is
revisited. The options are a single owner for a small system or a data-
governance role for a larger one, with a review cadence (annually is a
reasonable default) and triggers (a significant new data type, a new
regulatory obligation). The driver is the rate at which the data and its
obligations change. This sub-decision is what keeps the policy from going
stale.

## Decision Outcome

The outcome is a recorded ADR that states, for each of the six sub-decisions,
the option chosen and the drivers that selected it. The ADR need not be long;
it needs to be explicit and current. The substrate-recommended sequence is to
record the scheme first because it is the premise, then the determination
rule, the per-class handling matrix, the propagation rules, the tag-and-label
binding, and ownership. A small application has a short ADR (the four-class
default; classify free-text and personal-data fields as confidential and
payment or health fields as restricted; encrypt confidential and restricted
at rest and in transit, minimize and audit access to them, retain for the
business period and purge on schedule, never log them unmasked; propagate
class to exports and forbid restricted data in the shared cache; bind the
vocabulary to both the code labels and the infrastructure tags; reviewed
annually by the service owner); the value is that even this short version is
written down and can be updated rather than rediscovered after an exposure.

## Substrate Alignment

This framework is the L3 anchor for the data-classification concern. The
three L1 rules and five L2 rules are conformance checks against the
sub-decisions here: data-classification.model-classification-label and data-classification.closed-vocabulary against the scheme and its
vocabulary (sub-decision 1), data-classification.classification-correctness against the determination rule
(sub-decision 2), data-classification.encryption-per-class and data-classification.access-least-privilege and data-classification.retention-disposal and data-classification.no-classified-data-in-logs
against the per-class handling matrix (sub-decision 3), data-classification.propagation-inheritance against
the propagation rules (sub-decision 4), and the tag-and-label binding
(sub-decision 5) is what aligns the application labels with the
infrastructure tags that infrastructure-misconfiguration infrastructure-misconfiguration.governance-tagging enforces.
The concern owns the classification scheme and the per-class handling
requirements; the mechanisms that implement the controls (the encryption
primitive, the access-control enforcement, the provision-time tag
enforcement) are owned by the security and infrastructure concerns, and this
policy cross-references them rather than restating them. The caching-strategy
framework is the related sibling that consumes this policy's
what-may-be-cached-where constraint, and the privacy concern (M5) will build
its personal-data obligations on this scheme.

## Consequences

Recording the policy forces the interactions between the six sub-decisions
into view at decision time (most importantly that the determination rule
drives the class, the class drives the handling matrix, and the propagation
rules keep the handling from being bypassed by data movement), gives new
contributors the context to classify and handle data consistently, and
creates the artifact a data or regulatory change updates rather than
rediscovers. The cost is the discipline of authoring and maintaining the ADR,
small relative to the failure it prevents: a misclassification that
under-protects restricted data, a sensitive value logged because no one drew
the logging line, or classified data exported to a destination that cannot
protect it. The risk is an ADR that goes stale; the review cadence in
sub-decision 6 is the mitigation.

## References

- FIPS 199 (standardized security categorization).
- NIST SP 800-60 (mapping information types to security categories, including
  aggregation).
- NIST SP 800-53 (the SC, AC, AU, MP, and SI control families).
- NIST SP 800-88 (media sanitization and disposal).
- ISO/IEC 27001 (information classification controls).
- MADR (the decision-record format).

## Decision Review Schedule

Author the policy when the application first handles meaningful classified
data. Revisit it at each significant change in the data handled or the
regulatory context, when a new class of data is introduced, and on a periodic
cadence (annually is a reasonable default). A review confirms the six
sub-decisions are still current, that the scheme vocabulary still binds the
application labels and the infrastructure tags, and that the local L1 and L2
choices still cohere with the recorded policy.
