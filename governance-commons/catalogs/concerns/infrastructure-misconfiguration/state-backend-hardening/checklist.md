---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.state-backend-hardening-state-backend-hardening"
title: "infrastructure-misconfiguration.state-backend-hardening review checklist: IaC state-backend hardening"
substrate-rule: "infrastructure-misconfiguration.state-backend-hardening"
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
  - "Initial Terraform / OpenTofu / Pulumi state backend configuration"
  - "State backend migration (S3 to Terraform Cloud, local to remote, single-bucket to per-workspace)"
  - "Change of state-backend access policy or backend principal"
  - "Introduction of a state-locking mechanism or change to an existing one"
  - "State-bucket cross-account access grant"
  - "Annual state-backend posture review per substrate-recommended cadence"
---

# infrastructure-misconfiguration.state-backend-hardening review checklist: IaC state-backend hardening

## How to use this binding

Reviewers answer every question below when reviewing the IaC state
backend configuration. The state file is the single most sensitive
artifact in an IaC workflow: it routinely contains secrets (database
passwords stored before they were marked sensitive, ARNs for
internal-only resources, principal identities), and it is the
authoritative record of what infrastructure exists in an account.
Compromise of the state file enables both information disclosure
and apply-time hijacking.

This checklist treats Terraform / OpenTofu state on S3 / GCS / Azure
Blob as the primary case; consumers using Terraform Cloud,
HashiCorp Cloud Platform, Spacelift, Env0, or another managed
backend answer the questions in terms of that platform's equivalent
controls.

## Review questions

### 1. Is the state stored on a remote backend, not locally?

- Is the backend configured to a remote object store (S3, GCS,
  Azure Blob) or a managed platform (TFC, HCP, Spacelift, Env0)?
- Local state files (`terraform.tfstate` committed to the
  repository or held on a workstation) are forbidden except for
  ephemeral experiments; is this consistently honored?

### 2. Is the state encrypted at rest?

- For S3 backend: is the bucket encrypted (relates to infrastructure-misconfiguration.data-resource-encryption-at-rest)
  with CMK appropriate to the data-classification of the IaC?
- For GCS backend: is the bucket encrypted with CMK where the
  classification requires it?
- For Azure Blob backend: is the storage account encrypted with
  CMK where required?
- For managed platforms: does the platform's documented at-rest
  encryption posture meet the consumer's classification
  requirements?

### 3. Is access to the state restricted?

- Is the backend bucket / container access-restricted to the
  specific principals (CI service role, on-call engineer break-
  glass role) that legitimately need it?
- Is the bucket policy / container ACL configured for default-deny
  with explicit allow only for the named principals?
- For multi-environment state, is access scoped per environment
  (the production-state principal cannot read non-production
  state and vice versa)?
- Is access logged (S3 access logging, GCS access logs, Azure
  diagnostic settings) and the log destination secured?

### 4. Is state locking configured?

- For S3 backend: is a DynamoDB table configured for state
  locking via the `dynamodb_table` backend argument? Locking
  prevents concurrent apply collisions that can corrupt state.
- For GCS backend: is GCS native locking enabled (default since
  Terraform 0.10)?
- For Azure Blob: is blob lease-based locking active?
- For managed platforms: does the platform's locking semantics
  meet the consumer's concurrent-apply protection requirement?

### 5. Is versioning enabled?

- Is the backend storage versioned so that state corruption,
  accidental destroy, or malicious modification can be recovered
  by rolling back to a prior version?
- Is the retention period for old versions appropriate (the
  substrate-recommended floor is 30 days; consumers with
  regulatory retention requirements set higher)?

### 6. Is the bootstrap procedure documented?

- The state backend is itself infrastructure; how is it
  bootstrapped without a state backend? Is there a documented
  initial-bootstrap procedure (a thin Terraform module run
  locally once with manual state-import, or a separate platform-
  level bootstrap workflow)?
- Is the bootstrap state recovered or itself stored?

### 7. Are secrets in state addressed?

- Are sensitive-attribute markers (`sensitive = true` on outputs;
  the SECRETS concern's discipline on never declaring secrets
  inline) applied?
- Is the state backend access policy treated as equivalent to a
  secrets-management vault access policy (the SECRETS concern
  applies in parallel)?
- Is there a documented procedure for state-content auditing if
  exposure is suspected?

### 8. Has the L1 mechanical scanner suite been run against the backend resources themselves?

- The state backend's bucket / container / table is itself IaC-
  declared. Have infrastructure-misconfiguration.data-resource-encryption-at-rest (encryption), infrastructure-misconfiguration.no-public-access-without-tag (public
  access), and infrastructure-misconfiguration.audit-and-flow-logging-enabled (logging) been verified for these
  resources?

## Findings disposition

PASS / PASS with note / REWORK / EXCEPTION, per the infrastructure-misconfiguration.least-privilege-iac-iam
disposition section. State-backend exceptions are high-severity
(the blast radius is the entire managed estate); the substrate-
recommended exception cadence for infrastructure-misconfiguration.state-backend-hardening is quarterly with
explicit re-justification each cycle.

## Cross-references

- infrastructure-misconfiguration.data-resource-encryption-at-rest, infrastructure-misconfiguration.no-public-access-without-tag, infrastructure-misconfiguration.audit-and-flow-logging-enabled (mechanical layer applies to
  the backend's bucket and table just as it applies to any other
  resource)
- SECRETS concern (state backends store secrets in practice;
  treat the backend as a secrets vault for access-policy purposes)
- The forthcoming `data-classification` concern (state inherits
  the highest classification of the resources it tracks)
- Terraform / OpenTofu backend documentation referenced in the
  parent catalog
