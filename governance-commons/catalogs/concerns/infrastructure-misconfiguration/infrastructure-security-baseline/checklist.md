---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.infrastructure-security-baseline-infrastructure-security-baseline"
title: "infrastructure-misconfiguration.infrastructure-security-baseline review checklist: infrastructure security baseline ADR conformance"
substrate-rule: "infrastructure-misconfiguration.infrastructure-security-baseline"
substrate-rule-href: "rule.yaml"
layer: "L3"
lifecycle-status: "stable"
commons-version: "0.6.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-31"
last-modified: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule, promoted to stable at the M4 close consolidation (2026-06-01); cooling-off honored, authoring landed on a prior calendar day in the concern's M4 authoring session and attestation lands in a discrete close commit on 2026-06-01."
ai-assistance: "AI drafted from substrate-author intent at M4 Session 1 (2026-05-31). Substrate-author review required for stable promotion."
review-triggers:
  - "Initial substantive IaC authoring at the consumer's scale (more than a single small workload in a single cloud account, or any deployment in a regulated environment)"
  - "Initial authoring or material revision of the consumer's infrastructure-security-baseline ADR"
  - "Change of enforcement-model (Option A through E in the paired MADR)"
  - "Change of baseline benchmark version (e.g. CIS AWS Foundations v3.0.0 to v4.0.0)"
  - "Regulatory regime change (consumer enters or exits FedRAMP, HIPAA, PCI DSS, FFIEC scope)"
  - "Multi-account or multi-cloud topology change (new cloud provider added, account proliferation crosses operational threshold)"
  - "Annual ADR currency review per substrate-recommended cadence; ADR's stated review-cadence date approaching"
  - "Drift between the IaC's actual posture and the ADR's chosen option observed during another L2 review"
---

# infrastructure-misconfiguration.infrastructure-security-baseline review checklist: infrastructure security baseline ADR conformance

## How to use this binding

Reviewers answer every question below when reviewing the consumer's
infrastructure-security-baseline Architecture Decision Record (ADR)
at initial authoring, at material revision, or during the periodic
currency review. The L1 and L2 rules in this concern provide the
detailed surface; the L3 ADR provides the strategic shape that
determines how the L1 and L2 rules are operationalized. The
substrate treats the ADR as rule-required (rather than rule-
recommended) because consumers who skip the strategic layer
consistently re-author the same per-resource decisions in
non-documented ways across multiple substrate-authors, drifting
from any consistent posture.

This checklist verifies three properties of the ADR: **presence**
(the ADR exists), **currency** (the ADR is not stale relative to
the consumer's evolving context), and **conformance** (the
consumer's actual IaC posture matches the ADR's chosen option).
The paired MADR at
`governance-commons/decision-frameworks/infrastructure-security-baseline.madr.md`
is the template the consumer's ADR follows; this checklist verifies
the consumer's ADR is a valid instantiation of that template, not
a re-litigation of the template's own structure.

## Review questions

### 1. Does the ADR exist at the consumer's documented ADR location?

- Is there an ADR file (per the consumer's chosen ADR convention:
  MADR markdown, ADR markdown, RFC, design doc) at the consumer's
  ADR location (typically `docs/decisions/` or equivalent)?
- Is the ADR discoverable by a new substrate-author joining the
  consumer team (link from the repository README, index file,
  documentation site)?
- Was the ADR authored before substantive IaC at the consumer's
  scale began, or is it being retro-authored against pre-existing
  IaC? Either is acceptable; the L3 rule requires the ADR to exist,
  not that it precede every line of IaC.

### 2. Does the ADR document which baseline benchmark the consumer adopts?

The substrate's MADR enumerates baseline choices:

- CIS AWS Foundations v3.0.0
- CIS Microsoft Azure Foundations v2.1.0
- CIS GCP Foundation v2.0.0
- CIS Kubernetes Benchmark v1.9.0
- NIST SP 800-53 Rev. 5 profile (with FIPS / Moderate / High selection)
- FedRAMP Moderate or High
- HIPAA security rule baseline
- PCI DSS v4.0
- A consumer-internal custom baseline mapped to one of the above

Verify:

- Is one of these baselines named (or a defensible alternative)?
- Is the version pinned (CIS benchmark version; NIST SP 800-53 revision)?
- For multi-cloud consumers, is each cloud's baseline named (a
  single ADR may reference multiple baselines provided the mapping
  to each cloud is explicit)?

### 3. Does the ADR document which enforcement-model the consumer adopts?

The substrate's MADR enumerates five options:

- **Option A: cloud-native guardrails only** (AWS SCP + Config, Azure Policy + Defender, GCP Org Policy + SCC)
- **Option B: preventive policy-as-code in pipeline** (OPA Conftest, Sentinel, Checkov-as-gate, Kyverno)
- **Option C: hybrid preventive plus detective** (substrate-preferred for medium-to-large regulated consumers)
- **Option D: detective scanning only** (Wiz, Lacework, Prisma Cloud, Orca, native security hubs)
- **Option E: managed-tooling** (HCP Terraform, Pulumi Cloud, GitHub Advanced Security)

Verify:

- Is one of the five options selected (or a defensible composite)?
- Are the consequences of the chosen option documented (per the
  MADR's consequence enumeration)?
- Where the choice is Option D (detective-only), is there a
  documented path to graduate to hybrid as the consumer matures?
- Where the choice is Option B or C with policy-as-code, is the
  specific tool chain named (OPA + Conftest, Sentinel, Checkov-as-
  gate, Kyverno, or combination)?

### 4. Does the ADR document exception governance?

Without exception governance, baselines erode silently. Verify:

- Is the approval authority named (specific role or roles, not just
  "leadership")?
- Is the evidence-record format documented (where exceptions are
  filed, what fields are required, how the exception ties back to
  the affected resource)?
- Is exception decay enforced (exceptions carry an expiration date;
  expired exceptions either renew with re-justification or close)?
- Is there a documented review cadence for the open-exception list
  (substrate-recommended: quarterly for IAM and network exceptions,
  annual for key-management exceptions)?

### 5. Does the ADR document drift-detection cadence per environment?

- Is the cadence named per environment (production, staging,
  development, ephemeral)?
- Does the cadence meet the substrate baseline (daily for
  production) or the profile-tilt for regulated (hourly for
  production)?
- Is the signal-routing target named (which on-call channel
  receives drift alerts; which substrate-author owns triage)?
- Does the cadence match the infrastructure-misconfiguration.deletion-protection-and-drift binding's review-question
  on drift-detection configuration (the two are mutually
  reinforcing)?

### 6. Does the ADR cross-reference the substrate catalog as the detailed rule set?

The ADR provides strategic shape; the substrate's L1 and L2 rules
provide the per-resource surface. The two are complementary, not
substitutes. Verify:

- Does the ADR explicitly reference
  `governance-commons/catalogs/concerns/infrastructure-misconfiguration.oscal.yaml`
  (or the substrate version the consumer adopted)?
- Does the ADR state that the L1 and L2 rules apply *in addition
  to* the ADR-documented baseline, not *instead of*?
- Are the substrate's other concerns referenced where they touch
  this concern (logging, secrets-management, authorization,
  dependency-management, supply-chain)?

### 7. Is the ADR current?

- Is the ADR's stated review-cadence date in the future, or has it
  lapsed?
- Has the consumer's context changed since the ADR was authored
  (new cloud provider, new regulatory regime, new account scale,
  new team composition)?
- Where context has changed, is there a documented re-evaluation
  trigger (per the MADR's decision-drivers enumeration)?

### 8. Does the consumer's actual IaC posture match the ADR's chosen option?

The conformance question. This is the hardest of the eight and
typically requires sampling rather than exhaustive verification:

- For a representative sample of the consumer's IaC repositories,
  does the enforcement mechanism described in the ADR actually run
  in CI / CD or at the cloud-control-plane?
- Where the ADR selects Option B (preventive policy-as-code) or
  Option C (hybrid), is the policy-as-code repository present, are
  the policies authored to match the substrate's L1 and L2 rules,
  and are the policies enforced (PR-blocking vs warning-only)?
- Where the ADR selects Option A (cloud-native guardrails), are
  the SCPs / Azure Policy / GCP Org Policy assignments actually in
  place and not just declared in IaC that has not been applied?
- Where the ADR selects Option D (detective scanning), is the
  detective tool actually deployed, and is there a triage workflow?
- Where the ADR selects Option E (managed-tooling), is the managed
  tooling actually adopted (HCP Terraform workspaces created and
  in use, Pulumi Cloud projects active)?

## Outcome

The L3 review for infrastructure-misconfiguration.infrastructure-security-baseline succeeds when every question above
has an affirmative answer or a documented exception. Where the
ADR diverges from the substrate's MADR template, the divergence
is acceptable provided the alternative captures equivalent
information (the substrate cares about the strategic shape, not
the document's structural conformance).

The substrate's recommended cadence for infrastructure-misconfiguration.infrastructure-security-baseline review is
annual (the ADR's currency check) plus on-trigger (any of the
review-triggers in this binding's frontmatter). Between annual
reviews, the L1 and L2 reviews surface drift between the IaC
posture and the ADR's chosen option; the L3 review reconciles
the drift through ADR revision or IaC remediation.

## Cross-references

- `governance-commons/decision-frameworks/infrastructure-security-baseline.madr.md`
  (the paired MADR template the consumer's ADR instantiates)
- All IAC-L1-* and IAC-L2-* bindings (the per-resource rules the
  ADR's strategic shape operationalizes)
- infrastructure-misconfiguration.deletion-protection-and-drift (drift detection; the cadence question is shared)
- infrastructure-misconfiguration.least-privilege-iac-iam (IAM least-privilege; exception governance is shared)
- The substrate's CHARTER.md Section 2.4 on substrate-author
  attestation (the consumer's ADR is the consumer-side analog
  of the substrate-author attestation: a documented, dated,
  reviewable record of strategic choice)
