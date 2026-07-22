---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.infrastructure-misconfiguration.least-privilege-iac-iam-least-privilege-iac-iam"
title: "infrastructure-misconfiguration.least-privilege-iac-iam review checklist: least-privilege IaC IAM"
substrate-rule: "infrastructure-misconfiguration.least-privilege-iac-iam"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 1 authoring (2026-05-31). Substrate-author review required for stable promotion at M4 close."
review-triggers:
  - "Initial IaC IAM-policy implementation in a new account, project, or subscription"
  - "New IAM role created with permissions broader than the substrate's L1 patterns"
  - "Cross-account IAM-trust-policy declaration"
  - "iam:PassRole, sts:AssumeRole, or equivalent role-chaining permission grant"
  - "Quarterly IAM-policy posture review per the substrate-recommended cadence"
  - "Any policy referencing a wildcard action or wildcard resource scope"
---

# infrastructure-misconfiguration.least-privilege-iac-iam review checklist: least-privilege IaC IAM

## How to use this binding

Reviewers answer every question below when reviewing IaC-declared
cloud IAM grants (AWS IAM policies, Azure RBAC role assignments,
GCP IAM bindings, Kubernetes RBAC ClusterRole / Role / Binding
resources) at PR review time or during a periodic posture audit.
The L1 mechanical layer flags wildcard syntactic patterns; this L2
review verifies that any flagged wildcards are justified and that
the policy as a whole reflects least-privilege intent.

This checklist is intentionally not a list of forbidden patterns; it
is a list of *judgment calls the reviewer must make*. Tools surface
the candidates; the reviewer determines whether each candidate is
justified, scoped, or over-broad.

## Review questions

### 1. Are wildcard actions justified or scoped?

Identify every policy statement with Action `*` or with a service-
level wildcard (e.g. `s3:*`, `ec2:*`). For each:

- Is the wildcard scope-bounded by a corresponding wildcard-free
  Resource ARN? A statement granting `s3:*` on a single named bucket
  ARN is narrower than `s3:GetObject` on `*`.
- Is the wildcard service appropriate to the role's purpose? An EC2
  instance role granting `s3:*` typically should be reduced to the
  specific actions the workload exercises (`s3:GetObject`,
  `s3:PutObject` against the specific data bucket).
- If the wildcard cannot be reduced now, is there a documented
  reduction plan with a target date?

### 2. Are Resource wildcards justified?

Identify every policy statement with Resource `*`. For each:

- Is the action restricted enough that the resource wildcard is
  acceptable (e.g. `iam:GetUser` on `*` is read-only, lower risk
  than `s3:DeleteBucket` on `*`)?
- Could the resource scope be narrowed to specific ARN patterns
  (account-scoped, tag-scoped via ABAC conditions, prefix-scoped)?
- Is the use of `*` driven by the policy author's lack of knowledge
  of the resource ARN structure, or by a genuine requirement?

### 3. Is iam:PassRole properly scoped?

`iam:PassRole` is a high-risk privilege: it grants the holder the
ability to attach a named role to a service. For each PassRole grant:

- Is the Resource a specific role ARN or ARN pattern, not `*`?
- Is the iam:PassedToService condition set to the specific service
  the role is intended for (e.g. `ec2.amazonaws.com`)?
- Does the passed role itself follow least privilege?
- Is the principal granted PassRole appropriate (a developer role
  passing a Lambda execution role is acceptable; a Lambda execution
  role passing arbitrary roles is suspicious)?

### 4. Are administrative permissions scoped?

Identify any policy attaching an administrator-equivalent managed
policy (AWS `AdministratorAccess`, Azure `Owner` or `Contributor`
at subscription scope, GCP `roles/owner` or `roles/editor` at
project scope). For each:

- Is the principal a break-glass account, a CI service principal,
  or a daily-use identity?
- If the principal is daily-use, can a substantive least-privilege
  policy replace the managed policy?
- Is access to the administrator role gated by a step-up
  authentication or just-in-time elevation mechanism?

### 5. Are trust relationships and cross-account grants scoped?

Identify every trust policy (AWS IAM role trust, GCP service-account
impersonation, Azure managed-identity federation). For each:

- Is the Principal a specific account or specific identity, not
  organization-wide or `*`?
- Is there an ExternalId / audience condition set where the trust
  crosses an organizational boundary?
- Is the trust documented in the consumer's account-relationship
  registry (or equivalent ADR record)?

### 6. Are ABAC conditions used where they would tighten scope?

For policies that grant access to a class of resources:

- Could a condition (e.g. AWS `aws:ResourceTag/...`, Azure
  `Microsoft.Resources/tags`, GCP `resource.tags.*`) tighten the
  policy from "any matching resource" to "any matching resource
  tagged for this team / environment / data-classification"?
- Where ABAC conditions are present, are they evaluated against
  tags the consumer can verify are reliably applied (relates to
  infrastructure-misconfiguration.governance-tagging governance tagging discipline)?

### 7. Does the policy follow the substrate's documented IAM authoring conventions?

The substrate does not prescribe a single IAM authoring style but
requires reviewable structure:

- Are policy statements grouped by intent with comments where the
  intent is not obvious from the action / resource pair?
- Are role names structured by the substrate's role-naming
  convention (or the consumer's documented equivalent)?
- Are managed policies versus inline policies used per the
  consumer's documented policy (managed for shared, inline for
  role-specific is the substrate-suggested convention; consumer
  variation is acceptable when documented)?

### 8. Are findings from the L1 binding's complementary tools reviewed?

The infrastructure-misconfiguration.no-unrestricted-ingress (no unrestricted ingress) and infrastructure-misconfiguration.no-public-access-without-tag (no public
access) bindings include IAM-policy-content analysis (Checkov,
terrascan). For the IAM resources in this PR:

- Have the IAM-policy findings been triaged?
- Are suppressed findings documented in a per-policy exemption
  comment, not in a global exclusion?
- Has the consumer's iam-policy-analyzer (formerly Parliament) or
  equivalent policy linter run cleanly against the proposed
  policies?

## Findings disposition

For each question, the reviewer records one of:

- **PASS**: the policy meets the substrate's least-privilege intent.
- **PASS with note**: the policy meets the intent but the
  reviewer's reasoning is recorded for future audits (the policy is
  defensible, but the defense is non-obvious).
- **REWORK**: the policy is over-broad; the PR is blocked until
  the policy is tightened.
- **EXCEPTION**: the policy is over-broad but the breadth is
  justified by a documented exception with an owner, a review date,
  and a remediation plan. Exception records are stored in the
  consumer's exception registry.

Exceptions accumulate; the substrate-recommended cadence is a
quarterly exception-registry audit that retires resolved exceptions
and challenges still-active exceptions for whether they remain
necessary.

## Cross-references

- infrastructure-misconfiguration.no-unrestricted-ingress, infrastructure-misconfiguration.no-public-access-without-tag (mechanical layer that surfaces wildcard
  candidates for this review)
- authorization.object-level-authorization (application-layer permission-check correctness;
  this checklist's L2 cloud-IAM counterpart at the application
  layer)
- NIST SP 800-53 AC-6 (least privilege) and AC-5 (separation of
  duties)
- AWS IAM, Azure RBAC, and GCP IAM provider-specific least-
  privilege guidance referenced in the parent catalog
