---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.secrets-management.platform-selection-platform-selection"
title: "secrets-management.platform-selection review checklist: secrets management platform selection"
substrate-rule: "secrets-management.platform-selection"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "New application before any secret is introduced (pre-build gate)"
  - "Existing application changing or extending its secrets platform"
  - "Periodic review of the existing MADR (substrate-recommended annually)"
reviews-what: "the consumer's filled-in MADR document"
reviews-where: "typically /docs/decisions/ADR-XXX-secrets-management-platform.md"
---

# secrets-management.platform-selection review checklist: secrets management platform selection

## How to use this binding

L3 review is fundamentally different from L1 mechanical scan and
L2 code or test review. The reviewer reviews a DOCUMENT (the
consumer's filled-in MADR), not code or test scenarios. The
questions below verify that the MADR satisfies the substrate's
quality requirements.

The MADR is a pre-build gate per secrets-management.platform-selection. Reviewers must
complete this checklist before any secret-handling code is
introduced. The MADR review can be done by the same reviewers
who do code review, or by a designated security architect.

## Review questions

### 1. MADR exists and is in the standard location

Is there a MADR document for secrets management platform in the
application's decision-records location?

What good looks like: a document at /docs/decisions/ADR-XXX-
secrets-management-platform.md (or the consumer's equivalent
location), referenced from PRs that introduce secret handling,
discoverable to new engineers.

What needs follow-up: no ADR; the ADR is in a different
location not linked from the substrate's expected path; the
ADR is in a comment in a single PR rather than a persistent
document.

### 2. Context is application-specific, not boilerplate

The MADR should describe the application's specific context:
which clouds it runs in, which identity systems it uses, what
existing secrets infrastructure it inherits, what compliance
regime applies.

What good looks like: a context section that an engineer new
to the project could read to understand why the application
needs the platform choice it has.

What needs follow-up: context section copies the substrate's
framework verbatim; context is generic ("modern web
application") and could apply to any project; the consumer's
specific drivers are missing.

### 3. Decision drivers are addressed

The substrate's framework identifies drivers: cloud platform,
existing identity infrastructure, regulatory regime, operational
maturity, multi-region requirements, application architecture,
budget. The consumer's ADR addresses each substrate driver and
may add project-specific drivers.

What good looks like: a section enumerating drivers with the
application's value for each (e.g., "Cloud platform: AWS primary,
GCP for analytics overflow"). Application-specific drivers are
called out clearly.

What needs follow-up: substrate's drivers listed without
adaptation; one or more drivers missing without explanation;
drivers listed but not connected to the option analysis.

### 4. Considered options span the substrate's option space

The substrate's framework identifies the major options: cloud-
native KMS-plus-secrets-manager (AWS SM, GCP Secret Manager,
Azure Key Vault), self-managed HashiCorp Vault, hybrid, and
infrastructure-native Kubernetes secrets with operator. The
consumer's ADR considers at least the applicable options.

What good looks like: the consumer's ADR includes the
substrate's options that are plausibly applicable to the
application's context; options that do not apply are excluded
with brief reasoning.

What needs follow-up: only one option discussed (the chosen
one); other plausible options are not enumerated or compared;
the chosen option is asserted rather than reasoned to.

### 5. Decision outcome references decision drivers

The reasoning for the chosen option should connect to the
drivers; "we chose Vault because we like Vault" is not
substrate-acceptable reasoning.

What good looks like: the decision outcome paragraph cites the
specific drivers that pushed toward the chosen option (e.g.,
"chose AWS Secrets Manager because the primary cloud is AWS and
the team's operational maturity does not currently support
running Vault in HA").

What needs follow-up: decision outcome asserts the choice
without driver connection; reasoning is tautological ("we chose
X because X meets our needs"); the choice contradicts the
drivers listed and the contradiction is not acknowledged.

### 6. Substrate alignment is explicit

The framework identifies substrate-preferred options for common
contexts. The consumer's ADR states whether the choice aligns
with substrate preference and justifies any deviation.

What good looks like: an explicit "substrate alignment"
statement; if the choice aligns, brief confirmation; if the
choice deviates, the reasoning for the deviation is
substantial.

What needs follow-up: no substrate-alignment statement; the
deviation reasoning is "we wanted to" or "the team prefers"
rather than driver-based.

### 7. Consequences are addressed

Every choice has consequences. The ADR enumerates positive
consequences (which risks are managed), negative consequences
(operational overhead, vendor lock-in, cost), and required
follow-up work (additional ADRs, tooling, training).

What good looks like: a consequences section that names
specific trade-offs; the negative consequences are honest, not
glossed.

What needs follow-up: consequences are positive-only;
consequences are generic and could apply to any choice;
required follow-up is unspecified.

### 8. Decision-review schedule exists

Decisions decay. The ADR specifies when the decision is next
reviewed and what triggers earlier review.

What good looks like: a review-schedule section with a date or
cadence; trigger events listed (compliance regime change,
significant architectural change, vendor incident, substrate
version increment).

What needs follow-up: no review schedule; review schedule
generic ("annually" with no anchoring date); no trigger events.

## Reviewer attestation

```
secrets-management.platform-selection review checklist: complete
- MADR exists: PASS / FOLLOW-UP
- Context is application-specific: PASS / FOLLOW-UP
- Decision drivers addressed: PASS / FOLLOW-UP
- Considered options span the option space: PASS / FOLLOW-UP
- Decision outcome references drivers: PASS / FOLLOW-UP
- Substrate alignment is explicit: PASS / FOLLOW-UP
- Consequences are addressed: PASS / FOLLOW-UP
- Decision-review schedule exists: PASS / FOLLOW-UP
```

FOLLOW-UP items must be resolved before the MADR is accepted
and any secret-handling code is introduced. There is no exempt
state at L3; insufficient documentation is the finding.

## Cross-reference

- Substrate rule: secrets-management.platform-selection in catalogs/concerns/secrets-management.oscal.yaml
- Decision framework: decision-frameworks/secrets-management-platform.madr.md
- Good examples: examples/secrets-management/platform-selection-good.md
- Anti-patterns: examples/secrets-management/platform-selection-anti-pattern.md
