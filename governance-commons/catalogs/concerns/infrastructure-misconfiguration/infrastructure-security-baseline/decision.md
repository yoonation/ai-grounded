---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: infrastructure-misconfiguration.infrastructure-security-baseline
title: "Infrastructure Security Baseline and Enforcement-Model Selection"
lifecycle-status: stable
commons-version: "0.6.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-05-31"
reviewer: "myoung-self-attested"
reviewed: "2026-06-01"
entered-status-at: "2026-06-01"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M4 close consolidation (2026-06-01) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M4 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-01. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent. Pairs with infrastructure-misconfiguration.infrastructure-security-baseline substrate rule. Portfolio-of-sub-decisions structure mirroring the supply-chain-integrity-strategy MADR precedent: four sub-decisions (baseline benchmark, enforcement model, exception governance, drift cadence) rather than a single option pick. Draft lifecycle per M4 Session 1; stable promotion at M4 close."
authoritative-sources:
  - "https://www.cisecurity.org/cis-benchmarks/"
  - "https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home"
  - "https://csrc.nist.gov/pubs/sp/800/190/final"
  - "https://csrc.nist.gov/pubs/sp/800/207/final"
  - "https://cloudsecurityalliance.org/research/cloud-controls-matrix/"
  - "https://www.fedramp.gov/"
  - "https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html"
  - "https://www.pcisecuritystandards.org/document_library/"
  - "https://www.ffiec.gov/cybersecurity.htm"
  - "https://attack.mitre.org/matrices/enterprise/cloud/"
  - "https://attack.mitre.org/matrices/enterprise/containers/"
  - "https://adr.github.io/madr/"
related-frameworks:
  - decision-frameworks.supply-chain-integrity-strategy
  - decision-frameworks.logging-architecture
  - decision-frameworks.secrets-management-platform
  - decision-frameworks.authorization-model-selection
---

# Infrastructure Security Baseline and Enforcement-Model Selection

This decision framework provides the substrate's analysis of
infrastructure security baseline and enforcement-model options.
Consumers reference this framework when authoring their own ADR
documenting their organization's infrastructure security strategy.
Substrate-recommended location for the consumer's ADR:
`/docs/decisions/ADR-XXX-infrastructure-security-baseline.md`.

The framework is referenced by substrate rule infrastructure-misconfiguration.infrastructure-security-baseline, which
requires consumers to have an explicit, documented baseline and
enforcement-model strategy before substantive IaC authoring at
scale begins (more than a single small workload in a single cloud
account, or any deployment in a regulated environment). Consumers
satisfy infrastructure-misconfiguration.infrastructure-security-baseline by authoring an ADR that adapts the analysis in
this framework to their organizational context.

Unlike single-option decision frameworks (authorization-model-
selection, auth-strategy), the infrastructure security baseline
is a portfolio of four sub-decisions. The four sub-decisions
interact: choosing a regulated baseline implies stricter
enforcement which implies preventive policy-as-code which implies
specific exception-governance discipline. The consumer's ADR
addresses all four sub-decisions; this framework provides the
substrate's analysis for each.

## Context

Cloud infrastructure has become the substrate on which every
non-trivial application runs. The security and correctness of
that substrate is determined at IaC declaration time: a
misconfigured S3 bucket, an over-permissioned IAM role, a flat
network, an unencrypted database, an unpinned provider version,
or an absent audit log creates a failure mode that all
application-layer controls subsequently inherit. The
infrastructure-misconfiguration concern catalog (infrastructure-misconfiguration.data-resource-encryption-at-rest
through infrastructure-misconfiguration.iac-sources-version-pinned mechanical rules, infrastructure-misconfiguration.least-privilege-iac-iam through
infrastructure-misconfiguration.governance-tagging semantic rules, infrastructure-misconfiguration.infrastructure-security-baseline judgmental rule) encodes
the substrate's curated rule set for that declaration-time
correctness.

The L1 and L2 rules provide the detailed surface. They do not,
however, answer the strategic questions that determine *how* the
rules are operationalized: against which baseline benchmark, with
what enforcement mechanism, under what exception discipline, at
what drift-detection cadence. The L3 rule (infrastructure-misconfiguration.infrastructure-security-baseline) requires
the consumer to answer these strategic questions in an ADR; this
framework is the analytic template the ADR adapts.

The substrate treats the L3 ADR as rule-required (rather than
rule-recommended) because consumers who skip the strategic layer
consistently re-author the same per-resource decisions in
non-documented ways across multiple substrate-authors, drifting
from any consistent posture. The ADR is not paperwork; it is the
artifact that determines whether the L1 and L2 rules compose into
a coherent governance posture or accumulate as a checklist that
nobody owns.

## Regulatory Context

The consumer's regulatory regime tilts the substrate's defaults.
The framework distinguishes four regulatory tiers:

- **Greenfield / unregulated:** no specific regulatory regime
  applies; the consumer chooses the baseline. Substrate-default
  baseline at this tier is CIS-Foundations per cloud, with
  Option C hybrid enforcement deferred until consumer scale
  warrants.

- **Standards-aligned / unregulated by law:** the consumer
  voluntarily aligns to NIST SP 800-53 or ISO 27001 for
  commercial-trust reasons (SOC 2 attestation, customer
  contractual requirements). Substrate-default baseline at this
  tier is CIS-Foundations + NIST SP 800-53 Moderate-profile
  mapping, with Option C hybrid enforcement.

- **Industry-regulated:** HIPAA (healthcare), PCI DSS (payment
  cards), FFIEC (financial services), GLBA (financial privacy)
  apply. Substrate-default baseline at this tier is CIS-
  Foundations + NIST SP 800-53 Moderate or High + the
  industry-specific overlay, with Option C hybrid enforcement
  required and preventive policy-as-code biased toward strict
  mode.

- **Government-regulated:** FedRAMP Moderate or High, IL2/IL4/IL5
  for U.S. federal workloads, equivalents in other jurisdictions
  (UK GovAssure, Australian ISM, EU's NIS2 for critical
  infrastructure). Substrate-default baseline at this tier is
  NIST SP 800-53 High + FedRAMP overlay (or equivalent), with
  Option C hybrid enforcement at strict mode and exception
  governance requiring named approval at each tier.

Where the consumer operates across multiple regulatory tiers (a
healthcare company's marketing-website workload is greenfield
while its clinical-records workload is HIPAA-regulated), the ADR
documents the per-workload tier mapping. The substrate accepts
per-workload tiering provided the boundaries are documented and
the workload tagging (infrastructure-misconfiguration.governance-tagging) carries an attribute that
records the tier.

## Decision Drivers

The substrate's analysis is organized around six decision drivers
that determine the appropriate posture for each sub-decision.
Consumers reference these drivers in their ADR; the driver values
constrain the sub-decision choices.

### D1: Regulatory Regime

The most consequential driver. Determines the baseline benchmark
choice, the enforcement-model bias, and the exception-governance
strictness. Tier mapping per the Regulatory Context section
above.

### D2: Multi-Account / Multi-Cloud Topology

A consumer operating in a single cloud account in a single cloud
provider has different enforcement options than a consumer
operating across multiple accounts within a single provider, or
across multiple providers. The single-account single-cloud case
permits Option A cloud-native guardrails as a complete enforcement
mechanism; multi-account within a single provider permits Option A
with organizational policies as the unifying layer; multi-cloud
requires Option B or C with policy-as-code that runs cross-cloud
(OPA Conftest, Kyverno where Kubernetes is the unifying layer,
Sentinel where HashiCorp Cloud Platform is the unifying layer).

### D3: Team Maturity and Substrate-Author Availability

A small team with one or two substrate-authors has limited
capacity to maintain a self-hosted policy-as-code repository.
This driver biases the small-team case toward Option A
cloud-native guardrails (lower operational cost) or Option E
managed-tooling (the platform vendor maintains the policy
infrastructure). A large team with dedicated platform-
engineering substrate-authors can sustain Option B or C with
self-hosted policy-as-code at lower marginal cost per workload.

### D4: Preventive vs Detective Trade-off

Preventive enforcement (CI-time policy-as-code, admission-webhook
on cluster) catches issues before provisioning. The benefit is
that no misconfigured resource reaches the cloud. The cost is
pipeline complexity: every CI run includes a policy-evaluation
step; every Helm install / kubectl apply / Pulumi up runs the
admission webhook; failed policies block deploys, requiring an
exception path that the exception-governance sub-decision
addresses.

Detective enforcement (cloud-config rules, third-party CSPM tools
like Wiz / Lacework / Prisma Cloud / Orca, cloud-native security
hubs like AWS Security Hub / Microsoft Defender for Cloud / GCP
Security Command Center) catches issues after provisioning. The
benefit is that the enforcement does not interrupt deploys. The
cost is remediation latency: an exposed resource exists between
provisioning and detection; depending on the detection cadence
and the resource type, the latency may be minutes (cloud-native
near-real-time rules) or hours (third-party tools that poll on
a schedule).

The substrate's preference is hybrid (Option C) for medium-to-
large regulated consumers: preventive for the high-confidence
mechanical rules (the substrate's L1 surface), detective for the
long-tail compliance and drift (the substrate's L2 surface and
benchmark-wide coverage that exceeds what the substrate authors).

### D5: Exception Governance

Without exception governance, baselines erode silently: every
finding eventually finds a substrate-author who can justify
ignoring it, and the cumulative ignored findings become the
consumer's actual posture rather than the documented one. The
substrate's bias is explicit, dated, time-bounded exceptions
filed in a discoverable registry with a named approval authority.
This driver determines whether the consumer's exception
discipline matches the substrate's bias or diverges (the
substrate accepts divergence provided the alternative captures
the same information).

### D6: Drift-Detection Cadence and Signal Routing

Cadence determines how quickly out-of-band changes surface. The
substrate baseline is daily for production; the regulated
profile-tilt is hourly for production; the ephemeral tilt is
weekly or none. Signal routing determines who acts on drift; the
substrate's bias is the on-call channel mapped from the
workload's owner tag (per infrastructure-misconfiguration.governance-tagging).

## Sub-Decision 1: Baseline Benchmark Selection

The baseline benchmark is the reference set of controls the
consumer's IaC must meet (or exceed). The substrate's L1 and L2
rules are a curated subset; the baseline benchmark is the
broader reference.

### Substrate-preferred default

CIS Foundations Benchmark for the cloud provider in use, pinned
to the latest published version (CIS AWS Foundations v3.0.0; CIS
Microsoft Azure Foundations v2.1.0; CIS GCP Foundation v2.0.0;
CIS Kubernetes Benchmark v1.9.0). Where the consumer's regulatory
regime requires additional controls, the consumer's ADR
documents the overlay (NIST SP 800-53 Moderate/High, FedRAMP,
HIPAA, PCI DSS).

### Considered options

- **CIS Foundations Benchmark (substrate-preferred):** broadest
  industry consensus, regularly updated, mapped to multiple
  regulatory frameworks via NIST OSCAL profiles. Trade-offs:
  cloud-specific (the AWS benchmark differs from the Azure
  benchmark), version pinning required to avoid silent drift,
  some controls are out-of-date for newer services.

- **NIST SP 800-53 Rev. 5 profile:** comprehensive control
  catalog, applicable across cloud providers, mapped to FedRAMP
  and other government regimes. Trade-offs: not IaC-prescriptive
  (controls describe outcomes, not declarations), requires
  consumer-side interpretation to bind controls to IaC patterns.

- **FedRAMP Moderate or High:** required for U.S. federal
  workloads; selects a NIST SP 800-53 profile plus FedRAMP-
  specific overlays. Trade-offs: prescriptive about
  documentation, requires Authority to Operate process.

- **HIPAA Security Rule:** required for U.S. healthcare workloads
  handling Protected Health Information. Trade-offs: control
  set is shorter than CIS or NIST but interpretation is
  domain-specific.

- **PCI DSS v4.0:** required for workloads in scope for payment-
  card processing. Trade-offs: tightly scoped to cardholder data
  environment; consumer's ADR documents the scope boundary.

- **CSA Cloud Controls Matrix v4:** cross-framework mapping,
  useful as a meta-baseline that maps to CIS, NIST, FedRAMP,
  HIPAA, PCI DSS, and others. Trade-offs: less prescriptive than
  any single underlying framework.

- **Consumer-internal custom baseline:** the consumer's own
  curated control set, typically derived from one or more of the
  above. Substrate-acceptable provided the baseline is documented
  and the mapping to industry standards is traceable.

### Decision-driver mapping

| Driver | CIS | NIST 800-53 | FedRAMP | HIPAA | PCI DSS | CCM v4 | Custom |
|---|---|---|---|---|---|---|---|
| D1 unregulated | Substrate-pref | Acceptable | N/A | N/A | N/A | Acceptable | Acceptable |
| D1 standards-aligned | Substrate-pref | Substrate-pref | N/A | N/A | N/A | Acceptable | Acceptable |
| D1 industry-regulated | Required overlay | Substrate-pref | Acceptable | Required | Required | Acceptable | Acceptable |
| D1 government-regulated | Required overlay | Required | Required | Required | Required | Acceptable | Discouraged |

The substrate's bias: CIS Foundations + the regulatory overlay
required by the consumer's tier. Custom baselines are accepted
but discouraged at government tier because traceability suffers.

## Sub-Decision 2: Enforcement Model

How the consumer enforces the baseline against the IaC.

### Substrate-preferred default

Option C hybrid (preventive policy-as-code in CI plus detective
scanning post-deployment) for medium-to-large regulated consumers.
Option A cloud-native guardrails for small unregulated consumers.
Option E managed-tooling for small consumers with managed-platform
tolerance.

### Considered options

- **Option A: cloud-native guardrails only.** AWS Service Control
  Policies + AWS Config rules; Azure Policy + Azure Defender for
  Cloud; GCP Organization Policy + Security Command Center.
  Pros: low operational cost; integrated with cloud-provider
  identity model; near-real-time enforcement. Cons: cloud-
  vendor-specific (multi-cloud requires per-cloud policy
  maintenance); some rules are detective-only at the cloud-
  provider tier (the resource is created, then evaluated, then
  remediated); rule library is provider-managed and may lag the
  substrate's rule set.

- **Option B: preventive policy-as-code in pipeline.** OPA
  Conftest (Kubernetes admission via Gatekeeper; CI gate via
  Conftest); Sentinel (HCP Terraform / Terraform Enterprise);
  Checkov-as-gate (CI failure on policy match); Kyverno
  (Kubernetes-native policy). Pros: highest enforcement strength;
  cross-cloud story strongest (policies run independent of cloud
  provider); custom rules tractable. Cons: pipeline complexity;
  requires substrate-author time to maintain policy library;
  feedback loop is at CI-time, not at authoring-time.

- **Option C: hybrid preventive plus detective.** Substrate-
  preferred for medium-to-large regulated consumers: preventive
  in CI for the high-confidence rules (the substrate's L1
  surface), detective for long-tail compliance and drift (the
  substrate's L2 surface and benchmark-wide coverage). Pros:
  defense in depth; preventive catches most issues at CI time,
  detective catches the residual; matches substrate's L1-vs-L2
  partition. Cons: requires both pipeline and cloud-native
  investment; cross-cloud story strongest with detective
  complementing preventive.

- **Option D: detective scanning only.** Wiz, Lacework, Prisma
  Cloud, Orca, AWS Security Hub, Microsoft Defender for Cloud,
  GCP Security Command Center Premium. Substrate-acceptable as a
  starting posture for consumers who cannot yet invest in
  preventive infrastructure. Pros: operational simplicity; no
  pipeline integration; multi-cloud coverage from a single
  vendor. Cons: lowest enforcement (post-provisioning);
  remediation latency depends on detective cadence; vendor-
  lock-in for non-cloud-native options.

- **Option E: managed-tooling.** HCP Terraform / Terraform
  Enterprise (Sentinel policies); Pulumi Cloud (CrossGuard
  policies); GitHub Advanced Security IaC scanning; GitLab
  Ultimate IaC scanning. Substrate-acceptable; bind the
  consumer to the managed-tooling vendor; substrate-recommended
  for small teams without dedicated platform engineering. Pros:
  vendor maintains the policy infrastructure; low operational
  cost. Cons: vendor-bound; policy customization at the vendor's
  cadence; less flexible than self-hosted options.

### Decision-driver mapping

| Driver | Option A | Option B | Option C | Option D | Option E |
|---|---|---|---|---|---|
| D1 unregulated | Substrate-pref | Acceptable | Acceptable | Acceptable | Substrate-pref |
| D1 industry-regulated | Acceptable | Acceptable | Substrate-pref | Discouraged | Acceptable |
| D1 government-regulated | Acceptable overlay | Substrate-pref | Substrate-pref | Discouraged | Acceptable |
| D2 single-cloud | Substrate-pref | Acceptable | Acceptable | Acceptable | Substrate-pref |
| D2 multi-cloud | Discouraged | Substrate-pref | Substrate-pref | Acceptable | Acceptable |
| D3 small team | Substrate-pref | Discouraged | Discouraged | Acceptable | Substrate-pref |
| D3 large team | Acceptable | Acceptable | Substrate-pref | Acceptable | Acceptable |
| D4 preventive bias | Acceptable | Substrate-pref | Substrate-pref | Discouraged | Acceptable |

## Sub-Decision 3: Exception Governance

How the consumer governs deviations from the baseline.

### Substrate-preferred default

Named approval authority per finding category; exceptions filed
in a discoverable registry; expiration date required on every
exception; quarterly review of the open-exception list; expired
exceptions either renew with re-justification or close.

### Considered options

- **Substrate-preferred discipline (above):** explicit, dated,
  time-bounded, named-authority. Pros: prevents silent erosion;
  produces an audit-ready record. Cons: requires sustained
  process discipline.

- **Implicit / inline:** exceptions live as code comments next
  to suppressed findings; no central registry. Pros: low
  process overhead. Cons: silent erosion; no audit trail; no
  systematic review.

- **Approval-only (no expiration):** exceptions require approval
  but persist indefinitely. Pros: lower review burden. Cons:
  exception accumulation; substrate-discouraged because the
  substrate's evidence is that approval-only converges to silent
  erosion over time.

- **External GRC platform:** exceptions filed in a third-party
  GRC tool (ServiceNow GRC, OneTrust, MetricStream, Hyperproof).
  Pros: integrates with broader compliance workflow. Cons: cost;
  off-platform from the IaC repository.

### Decision-driver mapping

| Driver | Substrate-pref | Implicit | Approval-only | External GRC |
|---|---|---|---|---|
| D5 strict (regulated) | Substrate-pref | Discouraged | Discouraged | Substrate-pref |
| D5 standard | Substrate-pref | Acceptable | Acceptable | Acceptable |
| D5 minimal (greenfield) | Acceptable | Acceptable | Acceptable | Discouraged (cost) |

## Sub-Decision 4: Drift-Detection Cadence

How often the consumer reconciles IaC source with live state.

### Substrate-preferred default

Daily for production environments; hourly for regulated; weekly
for non-production; on-trigger for ephemeral.

### Considered options

- **Hourly:** highest signal; high CI cost. Substrate-recommended
  for government-regulated workloads.

- **Daily (substrate-baseline):** balance of signal and cost.
  Substrate-recommended for most production workloads.

- **Weekly:** lower cost; longer drift window. Substrate-
  acceptable for non-production; substrate-discouraged for
  production.

- **On-trigger only:** drift detection runs when a substrate-
  author requests it. Substrate-discouraged for any non-ephemeral
  workload because drift surfaces only when someone looks.

### Decision-driver mapping

| Driver | Hourly | Daily | Weekly | On-trigger |
|---|---|---|---|---|
| D1 unregulated production | Acceptable | Substrate-pref | Acceptable | Discouraged |
| D1 industry-regulated production | Substrate-pref | Substrate-pref | Discouraged | Discouraged |
| D1 government-regulated production | Substrate-pref | Acceptable | Discouraged | Discouraged |
| Non-production | Acceptable (overkill) | Acceptable | Substrate-pref | Acceptable |
| Ephemeral | Discouraged (cost) | Acceptable | Acceptable | Substrate-pref |

## Consequences

The consumer's ADR records the four sub-decision choices. The
consequences below apply across the portfolio:

- **Recurring cost:** the enforcement model determines the
  recurring operational cost. Option A is lowest; Option C is
  highest; Options B/D/E sit between.

- **PR-cycle latency:** preventive enforcement (Options B and C)
  adds CI time to every PR. Typical impact: 30 seconds to 5
  minutes per PR depending on policy library size.

- **Cross-cloud portability:** Option A is least portable;
  Options B and C are most portable; Options D and E sit between.

- **Vendor lock-in:** Options A and E carry vendor lock-in;
  Options B, C, D vary by tool choice.

- **Exception accumulation:** without disciplined exception
  governance, every option converges to the same silent-erosion
  failure mode over 18-36 months. Sub-Decision 3 is the
  load-bearing answer to this risk.

- **Drift latency:** Sub-Decision 4 determines how long an
  out-of-band change persists undetected. Longer drift windows
  correlate with longer mean-time-to-detect for adversarial
  misconfiguration.

## Cross-references

- Substrate rule infrastructure-misconfiguration.infrastructure-security-baseline (this framework's pairing rule)
- Substrate concern catalog
  `governance-commons/catalogs/concerns/infrastructure-misconfiguration.oscal.yaml`
  (the detailed L1 + L2 surface this strategy operationalizes)
- Substrate's CHARTER.md Section 2.4 (the analog discipline for
  substrate-author attestation; the consumer's ADR is the
  consumer-side analog)
- Decision frameworks for related concerns: supply-chain-
  integrity-strategy (artifact integrity to this strategy's
  declaration integrity); logging-architecture (the log
  destinations infrastructure-misconfiguration.audit-and-flow-logging-enabled emits to); secrets-management-platform
  (the runtime-retrieval pattern that complements this
  strategy's state-backend hardening); authorization-model-
  selection (the application-layer authorization that
  complements this strategy's cloud-IAM least privilege)
