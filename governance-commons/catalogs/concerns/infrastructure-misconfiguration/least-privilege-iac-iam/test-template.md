---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.infrastructure-misconfiguration.least-privilege-iac-iam-least-privilege-iac-iam"
title: "infrastructure-misconfiguration.least-privilege-iac-iam test template: least-privilege IaC IAM"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 1 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# infrastructure-misconfiguration.least-privilege-iac-iam test template: least-privilege IaC IAM

## How to use this binding

IAM least-privilege tests exercise IaC-declared cloud-IAM policies
against the policies' intended scope: each test asserts that a
specific high-risk capability is *not* granted to the policy's
principals when it should not be, and *is* granted when it should
be. The tests are framework-agnostic: consumers running policy-
simulation tooling (AWS IAM Policy Simulator API, Azure RBAC
who-can-do queries, GCP `policy-troubleshooter`) implement the
scenarios using the consumer's chosen tooling.

Substrate-recommended cadence: pre-merge for every PR that
modifies an IAM resource; nightly drift-detection re-run of the
suite against the live IaC state; quarterly full-suite execution
as part of the infrastructure-misconfiguration.least-privilege-iac-iam review-checklist cadence.

## Scenario 1: Wildcard actions resolve to a bounded resource scope

**Intent:** A policy granting `s3:*` is acceptable when the
Resource ARN list is bounded to specific buckets; the same
wildcard is a finding when paired with `Resource: "*"`.

**Test approach:**

1. Enumerate every policy statement in the IaC that uses a
   wildcard action (`*` or `s3:*`, `ec2:*`, etc.).
2. For each, assert the statement's Resource list contains at
   least one specific ARN and no statement granting the same
   wildcard action also grants `Resource: "*"`.
3. Where the policy-simulation tooling supports it, simulate
   the wildcard action against a representative out-of-scope
   resource and assert the simulation returns explicit `deny`
   or implicit `deny` (no matching `allow`).

**Pass criterion:** Every wildcard-action statement has a bounded
Resource list, OR is on the consumer's documented exception list
with a valid (unexpired) exception record.

## Scenario 2: iam:PassRole grants are scoped to specific role ARNs

**Intent:** `iam:PassRole` permits role chaining; a broad grant
(`Resource: "*"`) enables privilege escalation by passing higher-
tier roles to services.

**Test approach:**

1. Enumerate every policy statement with action
   `iam:PassRole` (and equivalents: GCP
   `iam.serviceAccounts.actAs`, Azure `assignRole`).
2. Assert the Resource is a specific role ARN or ARN pattern
   bounded to a substrate-author-controlled namespace.
3. Assert the `iam:PassedToService` condition is present and
   names a specific service principal.

**Pass criterion:** Every PassRole grant has a bounded Resource
and a PassedToService condition.

## Scenario 3: Administrator policies are scoped to break-glass principals

**Intent:** `AdministratorAccess` (or equivalents `Owner`,
`Editor`) attached to daily-use principals creates excessive
blast radius. The substrate's bias is break-glass-only.

**Test approach:**

1. Enumerate every attachment of `AdministratorAccess`,
   `arn:aws:iam::aws:policy/AdministratorAccess`,
   `roles/owner`, or equivalent Azure built-in `Owner` /
   `Contributor` at subscription scope.
2. Assert each attached principal is in the consumer's
   documented break-glass roster.
3. Assert each attachment is accompanied by step-up authentication
   or just-in-time elevation (PIM, AWS IAM Identity Center
   permission-set with step-up MFA, GCP IAM conditions).

**Pass criterion:** Every administrator attachment is to a
documented break-glass principal with step-up authentication.

## Scenario 4: Trust policies do not permit cross-account access without ExternalId

**Intent:** AWS IAM cross-account trust without an `ExternalId`
condition (or equivalent in other clouds) is vulnerable to the
"confused deputy" pattern.

**Test approach:**

1. Enumerate every IAM role trust policy that includes a
   Principal outside the local account (or local subscription,
   local project).
2. Assert the trust policy carries a condition restricting the
   trust (AWS `aws:SourceAccount` plus `sts:ExternalId`; Azure
   federated credential audience; GCP service-account
   impersonation IAM condition).

**Pass criterion:** Every cross-account trust has a condition
restricting the trust scope.

## Scenario 5: Resource-based policies do not grant access to anonymous principals

**Intent:** A resource policy granting access to `Principal:
"*"` without conditions opens the resource to the entire
internet's compute identities.

**Test approach:**

1. Enumerate every resource-based policy (S3 bucket policy,
   KMS key policy, SNS topic policy, SQS queue policy, Lambda
   resource policy, ECR repository policy, equivalents in
   Azure / GCP).
2. Assert no statement grants `Principal: "*"` without an
   `aws:SourceAccount`, `aws:SourceArn`, or `aws:PrincipalOrgID`
   condition that bounds the principal to the consumer's
   accounts.

**Pass criterion:** Every wildcard-principal grant has a binding
condition.

## Scenario 6: Service accounts and workload identities follow least privilege

**Intent:** Kubernetes service accounts, GCP service accounts,
Azure managed identities, and AWS IAM roles for service accounts
(IRSA) often accumulate permissions over time as workloads grow.

**Test approach:**

1. For each service account / workload identity, enumerate the
   attached roles and policies.
2. Assert the attached set is in the consumer's documented
   workload-identity matrix (each workload has a known set of
   permissions).
3. For workloads with elevated permissions, assert the workload
   identity is not reused across unrelated workloads.

**Pass criterion:** Every workload identity has a documented
permission set that matches its IaC declaration.

## Scenario 7: ABAC conditions are evaluated against verifiable tag state

**Intent:** Policies using ABAC conditions (resource tag,
principal tag) depend on tags being reliably applied; if tags
are inconsistent, ABAC conditions silently fail open or closed.

**Test approach:**

1. Enumerate every policy condition referencing
   `aws:ResourceTag/...`, `aws:PrincipalTag/...`, or equivalent
   Azure / GCP attribute-based conditions.
2. For each condition's tag key, run the infrastructure-misconfiguration.governance-tagging governance-
   tagging tests (or query the live tag state) and assert the
   tag is reliably applied across the policy's resource scope.
3. For principal-tag conditions, assert the principal tagging
   pipeline (SSO attribute mapping, workload-identity tagging
   automation) is documented and operational.

**Pass criterion:** Every ABAC condition resolves against a
reliably-applied tag.

## Outcome

The L2 test suite for infrastructure-misconfiguration.least-privilege-iac-iam succeeds when every scenario
above passes against the IaC's current state. Failures are
treated as PR-blocking findings unless the IaC is on the
consumer's documented exception list per the infrastructure-misconfiguration.least-privilege-iac-iam review-
checklist's exception governance.
