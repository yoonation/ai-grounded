---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.deletion-protection-and-drift-deletion-protection-and-drift"
title: "infrastructure-misconfiguration.deletion-protection-and-drift review checklist: deletion protection and drift monitoring"
substrate-rule: "infrastructure-misconfiguration.deletion-protection-and-drift"
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
  - "Initial IaC declaration of a stateful resource (RDS, DynamoDB, S3, KMS, CosmosDB, Storage Account, CloudSQL, GCS, PersistentVolumeClaim)"
  - "Change to a lifecycle block on a stateful resource"
  - "Removal or modification of a deletion-protection attribute"
  - "Change to the drift-detection cadence or alerting target"
  - "Promotion of a workspace or stack from ephemeral to production classification"
  - "Annual stateful-resource posture review per substrate-recommended cadence"
---

# infrastructure-misconfiguration.deletion-protection-and-drift review checklist: deletion protection and drift monitoring

## How to use this binding

Reviewers answer every question below when reviewing IaC that
declares or modifies a stateful resource, or when reviewing
drift-detection infrastructure (the scheduled job, the alerting
target, the on-call response procedure). Stateful resources are
irreversible on deletion: the substrate's bias is layered
protection at three tiers (provider-level deletion-protection
attribute, IaC-level lifecycle prevent_destroy, policy-as-code
gate against `terraform destroy` on production workspaces), and
the substrate's bias for drift detection is scheduled rather than
on-demand because manual console changes that disable protection
must surface deliberately rather than wait for the next time a
human happens to run a plan.

This checklist applies asymmetrically: production stateful
resources get the full layered protection; ephemeral resources
(test fixtures, CI scratch environments, developer sandboxes)
intentionally disable the protections and the IaC documents the
choice. The reviewer distinguishes production from ephemeral
by workspace name, environment tag (per infrastructure-misconfiguration.governance-tagging), or
profile-tilt selection.

## Review questions

### 1. Does the production stateful resource declare the provider's deletion-protection attribute?

- Does the AWS `aws_rds_cluster` / `aws_db_instance` declare
  `deletion_protection = true`?
- Does the AWS `aws_dynamodb_table` declare
  `deletion_protection_enabled = true`?
- Does the AWS `aws_s3_bucket` declare `versioning` and, for
  regulated data, `object_lock_configuration`?
- Does the AWS `aws_kms_key` declare `deletion_window_in_days`
  at the substrate's minimum (30 days for production)?
- Does the Azure `azurerm_cosmosdb_account` declare
  `soft_delete` and `continuous_backup`?
- Does the Azure `azurerm_storage_account` declare
  `blob_properties` with soft-delete enabled?
- Does the GCP `google_sql_database_instance` declare
  `deletion_protection = true`?
- Does the GCP `google_storage_bucket` declare `versioning`?
- Does the Kubernetes `PersistentVolumeClaim` declare
  `reclaim_policy = "Retain"` for production-state PVs?

### 2. Does the production stateful resource declare lifecycle prevent_destroy?

- Is `lifecycle { prevent_destroy = true }` declared on the
  stateful resource?
- If the resource is intentionally re-creatable (rare for
  stateful resources, common for ephemeral environments), is
  the omission documented in a comment that names the workspace
  or environment classification?

### 3. Is scheduled drift detection configured for production environments?

- Is there a scheduled CI job (GitHub Actions, GitLab CI, Azure
  DevOps, Jenkins, Tekton, or equivalent) that runs `terraform
  plan` / `pulumi preview` / CloudFormation drift detection
  against the production workspaces?
- Is the cadence at least daily (substrate baseline) or hourly
  (substrate-recommended for regulated environments)?
- Does the job run with read-only credentials so the drift
  detection cannot itself modify the infrastructure?
- Is the job configured to fail loudly (non-zero exit, alert
  emission) rather than fail silently?

### 4. Are drift findings alerted to the substrate-author on-call channel?

- Does the drift-detection job emit alerts via the
  observability concern's alerting surface (cross-references
  the substrate's observability and logging concerns)?
- Does the alert payload include the affected resource, the
  detected drift (added, modified, removed), and a link to the
  CI run?
- Is the on-call channel correct for the workspace's
  ownership (per the owner tag in infrastructure-misconfiguration.governance-tagging)?

### 5. Are ephemeral resources distinguished from production resources in the IaC's labeling?

- Does the workspace name or environment tag distinguish
  ephemeral from production?
- Does the IaC's documentation describe the asymmetric
  application of this rule (production gets layered protection;
  ephemeral does not)?
- Where ephemeral resources omit the protections, does the
  IaC carry a brief comment naming the reason (the
  substrate's bias is explicit-omission-with-rationale over
  silent omission)?

### 6. Is the substrate's `terraform destroy` gate documented or in place?

- Is there a policy-as-code rule (Sentinel, OPA Conftest,
  Checkov custom check, or equivalent per the consumer's
  infrastructure-misconfiguration.infrastructure-security-baseline enforcement-model selection) that requires
  out-of-band approval for `terraform destroy` operations on
  production workspaces?
- Where the consumer's infrastructure-misconfiguration.infrastructure-security-baseline ADR selects an enforcement
  model that lacks this gate (Option A cloud-native guardrails
  only, Option D detective-only), is the alternative procedure
  documented?

## Outcome

The L2 review for infrastructure-misconfiguration.deletion-protection-and-drift succeeds when every question above
has an affirmative answer or a documented exception. Document
the exceptions in the consumer's ADR (per infrastructure-misconfiguration.infrastructure-security-baseline) so the
substrate's L3 review surface captures the deviation.
