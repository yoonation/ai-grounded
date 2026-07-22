---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.infrastructure-misconfiguration.state-backend-hardening-state-backend-hardening"
title: "infrastructure-misconfiguration.state-backend-hardening test template: IaC state-backend hardening"
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
framework-agnostic: true
---

# infrastructure-misconfiguration.state-backend-hardening test template: IaC state-backend hardening

## How to use this binding

State-backend tests exercise the access-control, encryption,
locking, versioning, and audit posture of the consumer's IaC
state backend. Tests are framework-agnostic: the same scenario
applies whether the backend is S3 + DynamoDB, GCS native locking,
Azure Blob with lease locking, or a managed platform (Terraform
Cloud, HCP Terraform, Spacelift, Env0).

Substrate-recommended cadence: pre-merge for every PR that
modifies the state-backend configuration; quarterly full-suite
execution as part of the infrastructure-misconfiguration.state-backend-hardening review-checklist cadence;
ad-hoc execution after any incident involving suspected state
tampering.

## Scenario 1: State is on a remote backend, not local

**Intent:** A `terraform.tfstate` file committed to the
repository or held locally has no access control beyond the
filesystem; it routinely contains secrets.

**Test approach:**

1. Search the IaC repository for `terraform.tfstate` and
   `terraform.tfstate.backup` files.
2. Inspect the Terraform / OpenTofu / Pulumi backend
   configuration for each workspace.
3. Assert the backend block names a remote object store or
   managed platform.

**Pass criterion:** No local state files committed; all
workspaces use a remote backend.

## Scenario 2: State storage is encrypted at rest

**Intent:** State storage is itself a data-bearing resource and
must follow infrastructure-misconfiguration.data-resource-encryption-at-rest's encryption-at-rest discipline.

**Test approach:**

1. Identify the backend storage resource (S3 bucket, GCS bucket,
   Azure Storage account, managed platform).
2. Apply the infrastructure-misconfiguration.data-resource-encryption-at-rest test logic to the backend storage
   resource.
3. For consumers requiring CMK (per data-classification matrix),
   assert the backend storage uses a customer-managed key.

**Pass criterion:** Backend storage is encrypted at rest at the
key tier required by the consumer's classification.

## Scenario 3: Backend access is restricted to named principals

**Intent:** Read access to the state file is read access to the
secrets and resource ARNs it contains; write access is the
authority to inject phantom resources or alter recorded state.

**Test approach:**

1. Inspect the backend storage's resource-based policy (S3
   bucket policy, Storage account ACL, GCS IAM bindings,
   managed-platform team-membership configuration).
2. Enumerate the principals granted access.
3. Assert each principal is in the consumer's named CI service
   role or break-glass roster.
4. Assert no wildcard principal grant is present.

**Pass criterion:** Every principal with backend access is named
and authorized.

## Scenario 4: State locking is operational

**Intent:** Locking prevents concurrent applies from corrupting
state.

**Test approach:**

1. Inspect the backend configuration for the locking mechanism
   (DynamoDB table for S3, native locking for GCS, blob lease
   for Azure, managed-platform locking).
2. For S3 + DynamoDB: assert the DynamoDB table exists, has
   the correct partition key (`LockID`), and is in the same
   region as the bucket.
3. Where the consumer can safely exercise it, run a concurrent
   `terraform plan` from two sessions and assert the second
   waits or fails on the lock (this is a destructive scenario,
   run only against a test workspace).

**Pass criterion:** Locking is configured and operationally
verified.

## Scenario 5: State storage is versioned

**Intent:** State corruption, accidental destroy, or malicious
modification must be recoverable.

**Test approach:**

1. Inspect the backend storage's versioning attribute.
2. Assert versioning is enabled.
3. Inspect the lifecycle policy (if any) and assert old
   versions are retained for the substrate's minimum (30 days)
   or longer per the consumer's regulatory retention.

**Pass criterion:** Versioning is enabled with appropriate
retention.

## Scenario 6: State access is logged

**Intent:** State access logs are the evidence base for incident
response if state compromise is suspected.

**Test approach:**

1. Inspect the backend storage's access-log configuration (S3
   server access logging, GCS access logs, Azure Storage
   diagnostic settings, managed-platform audit logs).
2. Assert logs are emitted.
3. Assert the log destination is separate from the backend
   itself (so a compromise of the backend does not also
   compromise the evidence).
4. Assert the log destination is access-restricted and
   itself encrypted (per infrastructure-misconfiguration.data-resource-encryption-at-rest).

**Pass criterion:** Access logs are emitted to a separate,
restricted destination.

## Scenario 7: Bootstrap procedure is documented and reproducible

**Intent:** The state backend is itself infrastructure; the
bootstrap procedure must be documented and exercisable in a
disaster-recovery scenario.

**Test approach:**

1. Locate the bootstrap documentation (typically a README in
   the IaC repository's bootstrap module, or a separate runbook).
2. Verify the documented procedure includes: which permissions
   are required to bootstrap; how the initial state is held
   (local then imported, or self-managed in a separate
   workspace); how the backend's own state is recovered if lost.
3. Run the bootstrap against a test environment if the
   consumer's risk tolerance permits.

**Pass criterion:** Documentation exists; procedure is current;
test execution succeeds.

## Outcome

The L2 test suite for infrastructure-misconfiguration.state-backend-hardening succeeds when every scenario
above passes against the IaC's current state. Failures are
treated as PR-blocking findings unless the IaC is on the
consumer's documented exception list per the infrastructure-misconfiguration.state-backend-hardening review-
checklist's exception governance. State-backend failures are
high-severity; the substrate-recommended response cadence on a
fresh finding is same-business-day.
