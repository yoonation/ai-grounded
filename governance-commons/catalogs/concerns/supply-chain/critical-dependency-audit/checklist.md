---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.supply-chain.critical-dependency-audit-critical-dependency-audit"
title: "supply-chain.critical-dependency-audit review checklist: critical dependency audit"
substrate-rule: "supply-chain.critical-dependency-audit"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.4.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-23"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-26"
entered-status-at: "2026-05-26"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Periodic tier-1 quarterly audit"
  - "Periodic tier-2 semi-annual audit"
  - "Periodic tier-3 annual audit"
  - "Pull requests adding a dependency requiring tier classification"
  - "Tier-reclassification proposals (substrate-recommended annual review)"
---

# supply-chain.critical-dependency-audit review checklist: critical dependency audit

## How to use this binding

Reviewers answer every question below during the periodic audit
for each tiered dependency. Substrate-recommended audit cadence
per tier:

- Tier-1 (critical): quarterly
- Tier-2 (important): semi-annual
- Tier-3 (commodity): annual

This checklist pairs with supply-chain.dependency-vetting (vetting at adoption);
re-vetting via this checklist verifies signals remain
substrate-acceptable.

## Review questions

### 1. Tier classification: is the assigned tier still substrate-accepted?

Confirm the dependency's current tier classification matches the
substrate-recommended criteria (per supply-chain.critical-dependency-audit catalog rule
guidance). Common drift sources: dependency's scope expanded
(commodity moved to important; important moved to critical);
dependency's scope reduced; criticality criteria changed in
substrate-scope.md. Drift surfaces a reclassification proposal.

### 2. Signal drift: have substrate-recognized signals regressed since the last review?

For each substrate-recognized signal, compare the current value
to the supply-chain.dependency-vetting vetting artifact value:

- Maintainer activity: has the active-maintainer count decreased
  significantly? Have substrate-recommended commit-cadence
  signals (commits in last 90 days, distinct contributors in
  last year) regressed?
- OpenSSF Scorecard score: has the score regressed by more than
  one band (substrate-recommended threshold: 0.2 on the 0-10
  scale)?
- Release recency: has the most-recent-release date drifted
  toward staleness (substrate-recommended threshold: no release
  in 12 months for tier-1, 18 months for tier-2, 24 months for
  tier-3)?
- Signing posture: has signing been removed or downgraded?
- SBOM availability: has upstream stopped publishing SBOMs?
- SLSA provenance availability: has upstream stopped publishing
  provenance attestations?

Regressions are findings; the substrate-recommended response
depends on regression severity (see Question 4).

### 3. Advisory history: have advisories affected this dependency since the last review?

Confirm the audit records advisories affecting the dependency in
the audit window, the consumer's response (patched, mitigated,
accepted-risk-with-documentation), and any open issues. Active
unmitigated advisories block continuation at the current tier.

### 4. Deprecation-trigger evaluation: have any deprecation triggers fired?

Substrate-recommended deprecation triggers: maintainer
abandonment (no commit activity in 18 months, no distinct
contributors in 12 months); explicit upstream sunset
announcement; persistent unpatched critical advisory; license
change to a substrate-incompatible license; ecosystem migration
to a substrate-recommended successor.

Fired triggers escalate to a migration plan or a substrate-
acceptable accept-risk decision with documented rationale and
expiry date.

### 5. Continued-adoption decision: is the audit conclusion documented?

Confirm the audit records the conclusion: continue at current
tier, reclassify, migrate, accept-risk-with-expiry, or replace.
Conclusions without rationale or owner are substrate-rejected.

### 6. Next-audit scheduling: is the next audit on the cadence?

Confirm the next audit is scheduled within the tier's substrate-
recommended cadence (tier-1 quarterly, tier-2 semi-annually,
tier-3 annually).

## Findings disposition

Findings retained per supply-chain.attestation-and-sbom-retention. Critical findings (fired
deprecation triggers without migration plan; active unmitigated
advisories) escalate to engineering management within one week.
Non-critical findings (minor signal drift, classification
proposals) handle in the next audit cycle.
