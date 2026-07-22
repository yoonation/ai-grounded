---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.dependency-management.vetting-policy-vetting-policy"
title: "dependency-management.vetting-policy review checklist: dependency vetting policy"
substrate-rule: "dependency-management.vetting-policy"
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
  - "New application before any direct dependency is introduced (pre-build gate)"
  - "Existing application formalizing previously-implicit vetting practice"
  - "Periodic review of the existing MADR (substrate-recommended annually)"
reviews-what: "the consumer's filled-in MADR document"
reviews-where: "typically /docs/decisions/ADR-XXX-dependency-vetting-policy.md"
---

# dependency-management.vetting-policy review checklist: dependency vetting policy

## How to use this binding

The reviewer reviews a DOCUMENT (the consumer's filled-in MADR),
not code. The questions verify that the MADR satisfies the
substrate's quality requirements. There is no exempt state at
L3; insufficient documentation is the finding.

## Review questions

### 1. MADR exists and is in the standard location

What good looks like: a document at /docs/decisions/ADR-XXX-
dependency-vetting-policy.md (or consumer equivalent),
referenced from PRs introducing new direct dependencies,
discoverable to new engineers.

What needs follow-up: no ADR; ADR in non-standard location;
ADR exists only as a comment in a single PR.

### 2. Context is project-specific

The ADR's context section describes the project's specific
dependency surface: which language ecosystems are in use,
roughly how many direct dependencies exist, what the team's
operational capacity is for vetting and ongoing maintenance.

What good looks like: a context section that an engineer new
to the project could read to understand the project's
dependency-management posture.

What needs follow-up: context is generic; context borrowed
from the framework verbatim; the project's specific dependency
surface is not characterized.

### 3. Decision drivers addressed

The substrate's framework identifies drivers: license posture,
operational capacity for vetting and maintenance, regulatory
context, transitive footprint tolerance, ecosystem maturity,
build-time cost tolerance, team size. The ADR addresses each
substrate driver and may add project-specific drivers.

What good looks like: drivers enumerated with the project's
value for each; project-specific drivers added where the
substrate's general drivers are insufficient.

What needs follow-up: substrate's drivers listed without
adaptation; drivers missing; drivers listed but not connected
to the option analysis.

### 4. Considered options span the substrate's option space

The substrate's framework identifies the major options: strict
allowlist (every direct dependency requires explicit approval),
criteria-based gate (dependencies meeting documented criteria
auto-approved, others require review), lightweight gate (PR
review with informal criteria), no policy (ad-hoc). The
consumer's ADR considers at least the applicable options.

What good looks like: the consumer's ADR enumerates the
substrate's options that are plausibly applicable; options that
do not apply are excluded with brief reasoning.

What needs follow-up: only the chosen option discussed; other
options not enumerated; the chosen option asserted rather than
reasoned to.

### 5. Decision outcome documents criteria and evidence requirements

The chosen option must produce concrete criteria a reviewer can
apply: which signals matter, what evidence accompanies a
dependency-introduction PR.

What good looks like: criteria enumerated (license, maintenance
health, security posture, transitive footprint, etc.) with
specific thresholds (e.g., "OpenSSF Scorecard at or above 7.0",
"no CVE in the last 12 months at severity high or above");
evidence required at PR time enumerated.

What needs follow-up: criteria stated but not measurable
("good maintenance"); evidence requirements not stated; the
policy is unfalsifiable.

### 6. Intake process: who decides, on what timeline?

A vetting policy without an intake process is theoretical. The
ADR documents how dependency-introduction PRs are reviewed.

What good looks like: named reviewer roles (security
architect, tech lead, on-call rotation); turnaround SLA
(substrate-recommended ceiling 5 business days); escalation
path for disagreements.

What needs follow-up: no intake process documented; intake
described abstractly ("the team will decide") without naming
roles; no SLA, leading to indefinite PR delays.

### 7. Substrate alignment is explicit

The framework identifies substrate-preferred options for common
contexts. The ADR states whether the choice aligns and
justifies any deviation.

What good looks like: explicit substrate-alignment statement;
deviation reasoning is substantial; alignment without
deviation is briefly confirmed.

What needs follow-up: no alignment statement; deviation
reasoning is preference-based rather than driver-based.

### 8. Consequences, follow-up work, and review schedule

The ADR enumerates positive consequences (which risks
managed), negative consequences (overhead, acceptable false
rejects), required follow-up (training, tooling, dependency
inventory work), and the schedule for revisiting the policy.

What good looks like: consequences honest including the
negative; follow-up work owned; review schedule with anchoring
date and trigger events (major incident, regulatory change,
substrate version increment, team-size change).

What needs follow-up: consequences positive-only or generic;
follow-up not owned; no review schedule.

## Reviewer attestation

```
dependency-management.vetting-policy review checklist: complete
- MADR exists: PASS / FOLLOW-UP
- Context project-specific: PASS / FOLLOW-UP
- Decision drivers addressed: PASS / FOLLOW-UP
- Considered options span the option space: PASS / FOLLOW-UP
- Decision outcome with criteria and evidence: PASS / FOLLOW-UP
- Intake process documented: PASS / FOLLOW-UP
- Substrate alignment explicit: PASS / FOLLOW-UP
- Consequences and review schedule: PASS / FOLLOW-UP
```

FOLLOW-UP items must be resolved before the policy ADR is
accepted and the policy is treated as the project's binding
intake criteria. There is no exempt state at L3.

## Cross-reference

- Substrate rule: dependency-management.vetting-policy in catalogs/concerns/dependency-management.oscal.yaml
- Decision framework: decision-frameworks/dependency-vetting-policy.madr.md
- Good examples: examples/dependency-management/vetting-policy-good.md
- Anti-patterns: examples/dependency-management/vetting-policy-anti-pattern.md
