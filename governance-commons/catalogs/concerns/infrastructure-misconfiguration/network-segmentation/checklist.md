---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.network-segmentation-network-segmentation"
title: "infrastructure-misconfiguration.network-segmentation review checklist: network segmentation and defense-in-depth"
substrate-rule: "infrastructure-misconfiguration.network-segmentation"
substrate-rule-href: "rule.yaml"
layer: "L2"
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
  - "Initial VPC, VNet, or VPC-equivalent network topology declaration"
  - "New subnet, route table, or peering connection added to existing topology"
  - "Introduction of cross-VPC, cross-VNet, or cross-region connectivity"
  - "New egress path declared (NAT gateway, egress-only IGW, internet route)"
  - "Application of a public-by-design intent tag to a workload"
  - "Quarterly network-posture review per substrate-recommended cadence"
---

# infrastructure-misconfiguration.network-segmentation review checklist: network segmentation and defense-in-depth

## How to use this binding

Reviewers answer every question below when reviewing IaC-declared
network topology (VPC / VNet / VPC equivalent, subnets, route tables,
security groups / NSGs / firewall rules at the architectural level,
peering connections, transit gateways, service endpoints, private
endpoints, NAT gateways, internet gateways). infrastructure-misconfiguration.no-unrestricted-ingress catches
mechanical patterns of unrestricted ingress; this L2 review verifies
the topology as a whole reflects defense-in-depth.

The reviewer needs a current architecture diagram (or generates one
from the IaC source via a tool like inframap or rover) before
answering: most questions require seeing how subnets compose into
tiers, not just inspecting individual resources.

## Review questions

### 1. Does the topology implement subnet tiering?

- Are public-facing resources (load balancers, NAT, bastions)
  confined to a public-subnet tier?
- Are application workloads confined to a private-subnet tier with
  no direct internet path?
- Are data-bearing resources (databases, caches, managed-service
  endpoints) confined to a data-subnet tier with no internet path
  and restricted ingress from the application tier only?
- Where the topology deviates (a single-tier topology for an
  ephemeral environment, a flat development VPC), is the deviation
  documented and bounded?

### 2. Are egress paths controlled?

- Do private-subnet resources egress via NAT (or egress-only IGW
  for IPv6) rather than via a direct internet path?
- Is egress filtering present (a VPC endpoint policy restricting
  S3 / KMS / STS calls to in-account ARNs; an egress firewall like
  AWS Network Firewall, Azure Firewall, or GCP Cloud NAT with
  network policies)?
- Where the consumer's regulatory regime requires it, is data-
  exfiltration prevention (DLP at the network layer, VPC Service
  Controls, or equivalent) in place?

### 3. Are private endpoints used for managed-service access?

- Are S3, KMS, STS, DynamoDB, and equivalent managed-service calls
  routed via VPC endpoints / Private Link / Private Service
  Connect rather than over the public internet?
- For services with both interface and gateway endpoint options,
  has the choice been documented per workload's latency and cost
  profile?
- Are endpoint policies scoped (the endpoint policy restricts the
  callable API actions to what the workload exercises)?

### 4. Is east-west traffic restricted?

- Within the application tier, are services restricted to
  communicating only with the services they depend on (via
  security-group references, service mesh policies, or Kubernetes
  NetworkPolicy resources)?
- Are flat-network anti-patterns avoided (a single security group
  attached to many unrelated workloads granting cross-workload
  ingress on any port)?
- Are Kubernetes NetworkPolicy resources present with default-deny
  ingress + explicit allow per consumer service, rather than
  empty / absent network policies (which permit all pod-to-pod
  traffic)?

### 5. Are public-by-design resources defended in depth?

For each resource carrying the governance-commons.intent =
public-by-design tag:

- Is there a web application firewall (WAF) in front of the public
  surface where applicable?
- Is rate-limiting / DDoS protection (AWS Shield, Azure DDoS
  Protection, GCP Cloud Armor) attached?
- Is the public endpoint behind an authentication-first path or
  explicitly anonymous (per the consumer's documented intent)?
- Is the public surface logging access (relates to infrastructure-misconfiguration.audit-and-flow-logging-enabled)?

### 6. Are cross-VPC / cross-account paths intentional?

- Are peering connections, transit-gateway attachments, and VPN /
  Direct Connect / ExpressRoute / Cloud Interconnect connections
  documented with the business reason?
- Are cross-account paths gated by IAM cross-account role
  assumption with the infrastructure-misconfiguration.least-privilege-iac-iam trust-policy discipline applied?
- Are non-routable RFC1918 CIDR collisions avoided across peered
  networks?

### 7. Has the substrate's IaC scanner suite been run on the network resources?

- Have Checkov / Trivy / terrascan / KICS network-category findings
  been triaged?
- Where findings are suppressed, is the suppression accompanied by
  an inline comment referencing this checklist's review record?

## Findings disposition

PASS / PASS with note / REWORK / EXCEPTION, as in the infrastructure-misconfiguration.least-privilege-iac-iam
checklist's disposition section. Exceptions to network-segmentation
questions are higher-risk than IAM exceptions because the blast
radius is typically broader; the substrate-recommended exception
review cadence for infrastructure-misconfiguration.network-segmentation is quarterly with monthly check-in for
exceptions still active after one quarter.

## Cross-references

- infrastructure-misconfiguration.no-unrestricted-ingress, infrastructure-misconfiguration.no-public-access-without-tag (mechanical layer for unrestricted ingress
  and public access)
- infrastructure-misconfiguration.least-privilege-iac-iam (IAM scope; cross-account paths depend on IAM trust
  discipline)
- NIST SP 800-53 SC-7 (boundary protection) and SP 800-207 (zero
  trust architecture)
- CIS Benchmarks Foundations networking section per provider
