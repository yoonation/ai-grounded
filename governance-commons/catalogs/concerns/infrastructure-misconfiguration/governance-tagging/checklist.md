---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.governance-tagging-governance-tagging"
title: "infrastructure-misconfiguration.governance-tagging review checklist: mandatory governance tagging"
substrate-rule: "infrastructure-misconfiguration.governance-tagging"
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
  - "Initial provider configuration (Terraform provider block, Pulumi provider construction)"
  - "Change to a provider default_tags block or equivalent"
  - "Introduction of a new resource type to the IaC repository"
  - "Change to an AWS Organization tag policy, Azure Policy resource-tag rule, or GCP Organization Policy resource-tag rule"
  - "Change to the substrate's data-sensitivity vocabulary once the data-classification concern is authored (anticipated post-M4)"
  - "Annual tagging-schema posture review per substrate-recommended cadence"
---

# infrastructure-misconfiguration.governance-tagging review checklist: mandatory governance tagging

## How to use this binding

Reviewers answer every question below when reviewing IaC that
declares or modifies provider configuration, introduces a new
resource type, or changes the organization-level tag-enforcement
policy. Governance tagging at provision time is the cheapest
available control for the downstream operations the substrate
enables: cost attribution requires `cost-center`; on-call routing
requires `owner`; environment-aware policies require
`environment`; data-class-aware access controls require
`data-sensitivity`. Tag-presence is mechanically detectable (and
the substrate considered a candidate L1 rule) but tag-value
correctness requires review-time judgment that an L1 rule cannot
encode, which is why the rule is L2.

Where the consumer's existing tag schema differs from the
substrate's recommended schema, the substrate accepts the
alternative provided the schema is internally consistent and
captures the substrate's required information (owner,
environment, cost-center, data-sensitivity) under whatever keys
the consumer uses. The L2 review confirms the mapping.

## Review questions

### 1. Does the IaC declare a provider default_tags block (or equivalent) carrying the substrate-required keys?

- For Terraform, does the AWS provider declare a `default_tags`
  block? Does the Azure provider declare default tag handling
  per provider conventions? Does the GCP provider declare the
  default labels handling?
- For Pulumi, does the provider construction carry a
  defaultTags equivalent that applies to descendant resources?
- Are the substrate-required keys present: `owner`,
  `environment`, `cost-center`, and (for data-bearing resources)
  `data-sensitivity`?

### 2. Are tag values from the substrate's accepted vocabulary for each key?

- Is `environment` from the closed vocabulary
  (`production`, `staging`, `development`, `ephemeral`)?
- Is `data-sensitivity` from the closed vocabulary
  (`public`, `internal`, `confidential`, `restricted`) where
  declared? (Substrate notes: the data-classification concern is
  not yet authored; the vocabulary above is a placeholder. When
  the data-classification concern is authored, this rule's
  vocabulary realigns with that concern's scheme.)
- Is `owner` a substrate-author or team identity that maps to
  an on-call channel (per infrastructure-misconfiguration.deletion-protection-and-drift's drift-alerting target)?
- Is `cost-center` a value that maps to the consumer's
  cost-attribution unit per the cost-model-selection concern's
  cost-model-selection.cost-attribution-tags rule that this rule cross-references?

### 3. Do data-bearing resources carry the data-sensitivity tag?

- For each resource in the infrastructure-misconfiguration.data-resource-encryption-at-rest data-bearing set (RDS,
  DynamoDB, S3, EBS, RDS snapshots, Aurora clusters, Redshift,
  Azure SQL, Azure Cosmos, Azure Storage, Azure Disk, GCP
  CloudSQL, GCS, Persistent Disks, Spanner, Bigtable,
  PersistentVolume), does the resource carry `data-sensitivity`?
- Is the value correctly assigned for the data the resource
  holds? (This is the judgment the L1 candidate could not
  encode.)
- Where the resource is data-bearing but holds data that is
  legitimately `public` (a public website's static-asset bucket),
  is the explicit `public` tag declared rather than omitted?

### 4. Is the tag schema consistent across modules and across providers?

- Is the same logical concept always under the same key?
  (`owner`, never `Owner` / `ownedBy` / `team` drifting across
  modules.)
- Where the IaC repository spans multiple providers (AWS +
  Azure + GCP), does the schema apply uniformly?
- Where the IaC repository spans multiple substrate-authors or
  teams, is the schema documented in a README or equivalent so
  new contributors do not reinvent keys?

### 5. Are organization-level tag-enforcement policies declared in IaC?

- For AWS, does the IaC declare AWS Organization tag policies
  enforcing tag presence at the organization level?
- For Azure, does the IaC declare Azure Policy resource-tag
  enforcement at the subscription or management-group scope?
- For GCP, does the IaC declare GCP Organization Policy
  resource-tag enforcement at the org or folder level?
- Where organization-level enforcement is intentionally
  deferred (the consumer is at a single-account / single-
  subscription / single-project scale and policy-as-code is
  excessive), is the deferral documented in the consumer's
  infrastructure-misconfiguration.infrastructure-security-baseline ADR?

### 6. Where the consumer's existing tag schema differs from the substrate's, does the IaC document the mapping?

- Is there a README or inline comment that maps the consumer's
  keys to the substrate's required information (owner,
  environment, cost-center, data-sensitivity)?
- Does the mapping cover every substrate-required information
  type, even when the consumer's key naming differs (the
  substrate cares about the information, not the key spelling)?

## Outcome

The L2 review for infrastructure-misconfiguration.governance-tagging succeeds when every question above
has an affirmative answer or a documented exception. Where the
consumer's schema diverges from the substrate's recommendation,
the divergence is acceptable provided the mapping is documented
and the substrate's required information is captured.
