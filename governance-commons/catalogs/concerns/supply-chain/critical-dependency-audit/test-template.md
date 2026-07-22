---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.supply-chain.critical-dependency-audit-critical-dependency-audit"
title: "supply-chain.critical-dependency-audit test template: critical dependency audit"
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
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter test-scenario content."
framework-agnostic: true
---

# supply-chain.critical-dependency-audit test template: critical dependency audit

## How to use this binding

This binding describes verification that the consumer's tiered
dependency inventory exists, classifies all production
dependencies, and is being audited on the substrate-recommended
cadence.

## Scenario 1: tiered dependency inventory exists

**Preconditions**
- Substrate-recommended inventory path established (substrate-
  default: `docs/dependency-inventory.md` or
  `docs/dependency-inventory.yaml`)

**Verification**
- File exists at the substrate-recommended path
- File contains substrate-required structure: tier-1, tier-2,
  tier-3 sections (or substrate-acceptable equivalent tier
  schema documented in the supply-chain.supply-chain-integrity-strategy ADR)

**Substrate-recommended assertion shape**
- Assert: inventory file exists; tier sections present

## Scenario 2: production dependencies classified

**Preconditions**
- Inventory exists per Scenario 1
- Production dependencies are mechanically identifiable (lockfile-
  resident, manifest-resident, or substrate-acceptable equivalent
  surface)

**Verification**
- The CI gate cross-references the production dependency list
  (derived from lockfiles and substrate-recognized manifests)
  against the inventory's tier sections
- Each production dependency appears in exactly one tier section
- Dependencies in the inventory not present in lockfiles are
  flagged (stale entries)
- Dependencies in lockfiles not present in the inventory are
  flagged (unclassified)

**Substrate-recommended assertion shape**
- Assert: union of inventory tier entries equals (or is superset
  of) production dependency set from lockfiles
- Assert: no dependency appears in more than one tier

## Scenario 3: audit cadence is being met per tier

**Preconditions**
- Substrate-recommended audit-record directory (substrate-default:
  `docs/dependency-audits/`)

**Verification**
- For each tier-1 dependency: audit record exists from within
  past 90 days (quarterly cadence)
- For each tier-2 dependency: audit record exists from within
  past 180 days (semi-annual)
- For each tier-3 dependency: audit record exists from within
  past 365 days (annual)

**Substrate-recommended assertion shape**
- Assert: per-dependency audit-record-most-recent date is within
  the tier's substrate-recommended cadence window

## Scenario 4: deprecation triggers flagged

**Preconditions**
- Inventory exists per Scenario 1
- Audit records exist per Scenario 3

**Verification**
- The CI gate cross-references each tier-1 dependency against
  substrate-recommended deprecation triggers (no upstream
  commit in 18 months, no distinct contributors in 12 months,
  upstream sunset announcement)
- Fired triggers without migration plan in the audit record are
  flagged

**Substrate-recommended assertion shape**
- Assert: for each tier-1 dependency, deprecation-trigger status
  is recorded in the audit record; fired triggers have a
  documented migration plan

## Scenario 5: OpenSSF signals tracked

**Preconditions**
- Audit records contain substrate-recommended fields including
  OpenSSF Scorecard score (where available)

**Verification**
- Audit records show Scorecard score for dependencies with
  available scores; "not available" with substrate-acceptable
  rationale for the rest
- Score regression beyond substrate-recommended threshold (0.2
  on the 0-10 scale) since last audit is flagged

**Substrate-recommended assertion shape**
- Assert: audit record contains scorecard-score field with
  numeric value or "not available" sentinel
- Assert: score-regression flag fires when current minus previous
  exceeds 0.2

## Out of scope for this test template

- Tier classification correctness (is tier-1 really the right
  tier for this dependency) is L2 reviewer territory
- Audit-record content quality (depth of signal review,
  thoroughness of advisory analysis) is reviewer territory
