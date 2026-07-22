---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: privacy.lawful-basis-and-consent-policy
title: "Privacy Lawful-Basis and Consent Policy: Basis per Purpose, the Consent Model, Records of Processing, and the DPIA Trigger"
lifecycle-status: stable
commons-version: "0.7.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-03"
reviewer: "myoung-self-attested"
reviewed: "2026-06-04"
entered-status-at: "2026-06-04"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M5 close consolidation (2026-06-04) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M5 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-04. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with privacy.lawful-basis-and-consent-policy. Portfolio-of-sub-decisions structure mirroring the responsible-ai-policy and data-classification-policy precedents: the lawful basis per purpose, the consent model, the legitimate-interest assessment approach, the records of processing, the DPIA trigger, the special-category handling, and ownership and review cadence, rather than a single option pick. Draft lifecycle per M5 Session 4; stable promotion at M5 close."
authoritative-sources:
  - "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
  - "https://oag.ca.gov/privacy/ccpa"
  - "https://www.iso.org/standard/71670.html"
  - "https://www.nist.gov/privacy-framework"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.privacy-data-subject-rights-and-retention
  - decision-frameworks.responsible-ai-policy
---

# Privacy Lawful-Basis and Consent Policy: Basis per Purpose, the Consent Model, Records of Processing, and the DPIA Trigger

## Context and Problem Statement

Any system that processes personal data has a lawful-basis posture. The only
choice is whether it is decided and written down or left to accrete from
whatever each feature happened to assume. privacy.lawful-basis-and-consent-policy requires the policy be
explicit, because a defensible privacy posture is a system property that emerges
from how a set of decisions cohere, not from any one annotation. The mechanical
rule (a personal-data field declares a purpose and basis, privacy.personal-data-purpose-annotation) and the
semantic rules (basis valid per purpose, privacy.lawful-basis-and-consent; collection minimized,
privacy.purpose-limitation-and-minimization) are each local conformance checks; what they conform to is this
policy. The failure this prevents is the pile of locally reasonable choices that
do not cohere: a field annotated with a basis nobody assessed, consent collected
in a form that is not freely given, processing that should have triggered a DPIA
and did not. This framework builds on the data-classification sensitivity scheme
(data-classification.model-classification-label is the precondition label) and adds the personal-data regulatory
layer on top; it does not restate classification.

## Decision Drivers

- The policy must anchor every other privacy rule; privacy.lawful-basis-and-consent and privacy.purpose-limitation-and-minimization
  check against the basis and purposes it records.
- The basis has to be decided per purpose, with reasoning, so the per-purpose
  L2 check has something concrete to apply.
- Where consent is the basis, the consent has to be valid by construction
  (specific, informed, freely given, withdrawable) rather than assumed.
- The records of processing and the DPIA trigger must be defined once, not
  reinvented per feature under deadline.

## Considered Options

The policy is a portfolio of sub-decisions, not a single option pick. Each
sub-decision below is recorded with its rationale.

### Sub-decision 1: Lawful basis per purpose

State the lawful basis for each declared processing purpose (consent, contract,
legal obligation, vital interest, public task, or legitimate interest) and why.
The basis is decided per purpose rather than asserted once for the whole system,
because one purpose may rest on contract while another rests on consent.

### Sub-decision 2: The consent model

Where the basis is consent, record how consent is requested, recorded, checked
before processing, and withdrawn. The model fixes that consent is per purpose
and unbundled, that it is not a precondition for a service that does not need
it, and that withdrawal is as easy as granting. This is the policy privacy.lawful-basis-and-consent
applies per request.

### Sub-decision 3: The legitimate-interest assessment approach

Where the basis is legitimate interest, record how the balancing assessment is
done and kept (the interest, the necessity, and the balance against the
subject's rights). Legitimate interest is a basis that requires showing the work,
so the policy fixes how that work is recorded rather than leaving it implied.

### Sub-decision 4: Records of processing

State how the records of processing activities are maintained, what they
capture (purposes, categories, recipients, retention, transfers), and how they
are kept current. The records are the inventory the per-purpose and minimization
checks draw on.

### Sub-decision 5: The DPIA trigger

State the conditions under which a data protection impact assessment is
required (high-risk processing, large-scale special-category data, systematic
monitoring, or new high-risk technology) so the trigger is a rule rather than a
judgment call made under deadline.

### Sub-decision 6: Special-category and sensitive-data handling

Record the additional conditions for processing special-category personal data
(the narrower set of permitted bases and any explicit-consent requirement) so a
sensitive field is not processed under a basis that does not reach it.

### Sub-decision 7: Ownership and review cadence

State who owns the privacy policy, and the cadence on which it is reviewed,
including the events (new processing activity, regulatory change, consent-model
change) that force a review.

## Decision Outcome

The application records a privacy lawful-basis and consent policy ADR covering
the seven sub-decisions, discoverable from the service documentation and current
relative to the last significant processing or regulatory change. A simple
system's policy is short; the requirement is that the basis per purpose, the
consent model, the records of processing, and the DPIA trigger are written down
and updatable rather than rediscovered after a complaint. The local L1 and L2
choices cohere with it.

## Substrate Alignment

The policy is the anchor privacy.lawful-basis-and-consent (basis valid per purpose) and privacy.purpose-limitation-and-minimization
(minimization and secondary use) conform to. It builds on data-classification.model-classification-label (the
sensitivity label is the precondition) and does not restate the
data-classification scheme. It cross-references responsible-ai.human-oversight for automated-decision
rights, which privacy defers to responsible-ai rather than owning, and it pairs
with the data-subject-rights and retention architecture framework
(privacy.data-subject-rights-and-retention) for the operability of the rights this basis implies. It is the
personal-data governance decision made concrete for one system.

## Consequences

A recorded policy makes the system's lawful-basis posture explicit, owned, and
auditable, and gives the conformance rules a standard to check against. The cost
is the discipline of deciding the basis per purpose and keeping the records and
DPIA trigger current; the policy is revisited on a cadence and at significant
change so it does not go stale. A policy that is written once and abandoned is
worse than none, because it gives false assurance.

## References

- GDPR Regulation 2016/679, the lawful-basis and consent provisions (concept).
- CCPA and CPRA, the notice and purpose provisions (concept).
- ISO/IEC 27701 privacy information management (concept).
- NIST Privacy Framework, the GOVERN and CONTROL functions (concept).
- MADR (Markdown Architecture Decision Records).

## Decision Review Schedule

Reviewed on a periodic cadence and whenever a new processing activity, a change
to the consent model, a new transfer or processor, or applicable regulation
changes materially.
