---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.infrastructure-misconfiguration.network-segmentation-network-segmentation"
title: "infrastructure-misconfiguration.network-segmentation test template: network segmentation and defense-in-depth"
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
framework-agnostic: true
---

# infrastructure-misconfiguration.network-segmentation test template: network segmentation and defense-in-depth

## How to use this binding

Network-segmentation tests exercise the IaC-declared topology
against reachability claims: each test asserts that a path
between two points exists (when it should) or does not exist
(when it should not). The tests are framework-agnostic: consumers
running reachability-analysis tooling (AWS VPC Reachability
Analyzer, Azure Network Watcher Connection Monitor, GCP Network
Intelligence Connectivity Tests, terraform-plan-based static
graph analysis with `inframap` or `rover`) implement the
scenarios using the consumer's chosen tooling.

Substrate-recommended cadence: pre-merge for every PR that
modifies a network topology resource; weekly drift-detection
re-run against the live infrastructure state; quarterly full-
suite execution as part of the infrastructure-misconfiguration.network-segmentation review-checklist
cadence.

## Scenario 1: Public subnets contain only public-facing resources

**Intent:** Application and data resources must not be placed in
public subnets.

**Test approach:**

1. Enumerate every subnet declared with a route table containing
   a default route to an internet gateway.
2. Enumerate every resource attached to those subnets.
3. Assert each attached resource type is in the substrate's
   public-tier allow-list (load balancers, NAT gateways, bastion
   hosts, identity-aware proxy endpoints).

**Pass criterion:** No application or data resource is attached
to a public subnet.

## Scenario 2: Data-tier subnets have no internet egress path

**Intent:** Data-bearing resources should be in subnets without
default-route-to-internet, so a compromised data resource cannot
exfiltrate to arbitrary internet destinations.

**Test approach:**

1. Enumerate every subnet hosting a data-bearing resource (per
   the infrastructure-misconfiguration.data-resource-encryption-at-rest data-bearing resource set).
2. Inspect the route table associated with each.
3. Assert no default route targets an internet gateway or NAT
   gateway directly (egress to managed services is via VPC
   endpoint / Private Endpoint / Private Service Connect).

**Pass criterion:** Every data-tier subnet has no direct internet
egress path.

## Scenario 3: East-west traffic between application services follows explicit allow-lists

**Intent:** Within the application tier, services should be
restricted to communicating with their declared dependencies.

**Test approach:**

1. Enumerate every security group / NSG / firewall rule / NetworkPolicy
   permitting ingress to a service.
2. For each, identify the source (CIDR, security group reference,
   pod selector).
3. Assert the source is a specific peer service's security group /
   pod selector, not a broad CIDR range or empty selector.

**Pass criterion:** Every east-west allow rule references a
specific peer, not a CIDR-block-as-allow-list pattern.

## Scenario 4: Managed-service access is routed via VPC endpoints / Private Endpoints / Private Service Connect

**Intent:** Calls to S3, KMS, STS, DynamoDB, and equivalent
managed services should not traverse the public internet from
private subnets.

**Test approach:**

1. Enumerate every VPC / VNet / VPC-equivalent.
2. For each, assert the presence of endpoint resources for the
   managed services the consumer's workloads invoke (substrate
   minimum: S3, KMS, STS, ECR, Secrets Manager, EC2 Instance
   Metadata equivalents per cloud).
3. For each endpoint, assert the endpoint policy is scoped (not
   `Allow * on *`).

**Pass criterion:** Every required managed-service endpoint is
present with a scoped policy.

## Scenario 5: Kubernetes NetworkPolicy enforces namespace-level segmentation

**Intent:** Without an explicit NetworkPolicy, Kubernetes
namespaces are open; pods in any namespace can reach pods in any
other namespace.

**Test approach:**

1. Enumerate every namespace in the cluster IaC.
2. For each, assert the presence of a default-deny NetworkPolicy
   (matching all pods, with empty `ingress` / `egress`).
3. For each explicit allow rule, assert the `from` / `to`
   selector references a specific peer (namespace + pod label),
   not an empty selector.

**Pass criterion:** Every namespace has default-deny in place;
explicit allow rules are scoped.

## Scenario 6: Cross-VPC / cross-account paths are intentional

**Intent:** Peering connections, transit gateway attachments,
and cross-cloud connectivity should be enumerable against a
documented inventory.

**Test approach:**

1. Enumerate every peering, transit gateway attachment, VPN,
   Direct Connect / ExpressRoute / Cloud Interconnect, and
   cross-cloud connector.
2. Assert each is in the consumer's documented connectivity
   inventory.
3. For each, assert non-routable RFC1918 CIDR collisions are
   absent across the connected networks.

**Pass criterion:** Every cross-VPC / cross-account path is
documented; no CIDR collisions.

## Scenario 7: Public-by-design resources are defended in depth

**Intent:** Resources carrying the
`governance-commons.intent = public-by-design` tag must have
additional defenses (WAF, rate-limiting, DDoS protection,
authentication-first design or explicit anonymous).

**Test approach:**

1. Enumerate every resource carrying the public-by-design tag.
2. For each, assert the appropriate defenses:
   - For HTTP/S surfaces: a WAF (AWS WAF, Azure Front Door
     WAF, GCP Cloud Armor) is attached.
   - For all surfaces: rate-limiting is configured.
   - For data-bearing surfaces: authentication is enforced or
     anonymous-by-design is documented.

**Pass criterion:** Every public-by-design resource has the
substrate-recommended defenses in place.

## Outcome

The L2 test suite for infrastructure-misconfiguration.network-segmentation succeeds when every scenario
above passes against the IaC's current state. Failures are
treated as PR-blocking findings unless the IaC is on the
consumer's documented exception list per the infrastructure-misconfiguration.network-segmentation review-
checklist's exception governance.
