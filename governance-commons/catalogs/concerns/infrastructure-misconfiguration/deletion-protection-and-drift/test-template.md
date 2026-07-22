---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.infrastructure-misconfiguration.deletion-protection-and-drift-deletion-protection-and-drift"
title: "infrastructure-misconfiguration.deletion-protection-and-drift test template: deletion protection and drift monitoring"
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
framework-agnostic: true
---

# infrastructure-misconfiguration.deletion-protection-and-drift test template: deletion protection and drift monitoring

## How to use this binding

Deletion-protection-and-drift tests exercise the IaC's protection
posture (deletion-protection attribute, lifecycle prevent_destroy)
and the operational drift-detection infrastructure (scheduled job
cadence, alerting target, on-call routing). Tests are framework-
agnostic: the same scenarios apply across cloud providers and IaC
frameworks.

Substrate-recommended cadence: pre-merge for every PR that touches
a stateful resource; weekly full-suite execution as part of the
infrastructure posture audit; on-trigger after any drift incident.

## Scenario 1: Production stateful resources declare provider-level deletion protection

**Intent:** The provider's native deletion-protection attribute is
the first layer of the substrate's layered protection.

**Test approach:**

1. Enumerate every IaC-declared resource in the substrate's
   stateful-resource set (RDS, Aurora, DynamoDB, S3 bucket
   versioning, KMS keys, EFS, Azure CosmosDB / Storage / SQL,
   GCP CloudSQL / GCS, K8s PVC).
2. For each, determine the environment from tags (per infrastructure-misconfiguration.governance-tagging)
   or workspace.
3. For production environment: assert the deletion-protection
   attribute is set (e.g. `deletion_protection = true` for RDS;
   `deletion_protection_enabled = true` for DynamoDB;
   `deletion_window_in_days >= 30` for KMS; `versioning` for S3;
   etc.).

**Pass criterion:** Every production stateful resource declares
deletion protection at the provider tier.

## Scenario 2: Production stateful resources declare lifecycle prevent_destroy

**Intent:** The IaC-level `lifecycle { prevent_destroy = true }`
is the second layer of layered protection, catching `terraform
apply` operations that would destroy the resource.

**Test approach:**

1. Enumerate every production stateful resource (from Scenario 1).
2. Assert each declares a `lifecycle` block with
   `prevent_destroy = true`.
3. Where the resource omits the lifecycle block, assert the
   omission is documented in an inline comment that names the
   reason and links to an approved exception.

**Pass criterion:** Every production stateful resource declares
lifecycle prevent_destroy, or has a documented exception.

## Scenario 3: Scheduled drift-detection job exists and runs at the substrate-recommended cadence

**Intent:** Drift between IaC and live state must surface
deliberately, not wait for the next time a human happens to run
a plan.

**Test approach:**

1. Locate the drift-detection job in the consumer's CI / CD
   system (GitHub Actions workflow, GitLab CI pipeline, Jenkins
   job, Tekton task).
2. Inspect the schedule expression.
3. Assert the schedule is at least daily for production (baseline)
   or hourly (regulated profile-tilt).
4. Inspect recent run history; assert the job has executed
   successfully within the cadence window (no silent failures).

**Pass criterion:** A drift-detection job exists, runs at the
required cadence, and has not silently failed.

## Scenario 4: Drift-detection job uses read-only credentials

**Intent:** A drift-detection job must observe, not modify; its
credentials must not enable an apply-time change.

**Test approach:**

1. Identify the IAM role / service account / workload identity
   used by the drift-detection job.
2. Inspect the attached policies.
3. Assert no permissions enable a write operation on the
   resources being scanned (no `s3:Put*`, `ec2:Create*`,
   `rds:Modify*`, etc.).

**Pass criterion:** Drift-detection credentials are read-only.

## Scenario 5: Drift findings emit alerts to the correct on-call channel

**Intent:** Alerts must reach the substrate-author responsible
for the affected workload, per the owner tag.

**Test approach:**

1. Trigger a known drift (introduce a manual tag change against
   a test workspace's resource).
2. Run the drift-detection job.
3. Assert the alert payload includes: the affected resource,
   the detected drift, a link to the CI run.
4. Assert the alert routes to the on-call channel mapped from
   the affected workspace's owner tag.

**Pass criterion:** Synthetic drift produces a correctly-routed
alert.

## Scenario 6: Ephemeral resources are correctly distinguished from production

**Intent:** The rule applies asymmetrically; the test verifies
the asymmetric application is implemented correctly.

**Test approach:**

1. Enumerate stateful resources tagged with environment
   `ephemeral` (or equivalent).
2. Assert the deletion-protection attribute is *not* required
   for these resources (the substrate's bias is explicit-
   omission-with-rationale for ephemeral).
3. Assert each ephemeral resource carries an inline IaC comment
   naming the workspace classification.

**Pass criterion:** Ephemeral resources are recognized and the
asymmetric application is in place.

## Scenario 7: The terraform-destroy policy-as-code gate is enforced

**Intent:** Production workspaces must require out-of-band
approval for destroy operations.

**Test approach:**

1. Locate the policy-as-code rule (Sentinel policy, OPA Conftest
   policy, Checkov custom check, or equivalent per infrastructure-misconfiguration.infrastructure-security-baseline).
2. Inspect the rule's logic.
3. Assert the rule blocks `terraform destroy` (or equivalent)
   on production workspaces without an approval token.
4. Where the consumer's infrastructure-misconfiguration.infrastructure-security-baseline selects an enforcement model
   without this gate (Options A or D), assert the alternative
   procedure (cloud-native preventive policy, manual approval
   workflow) is documented and operational.

**Pass criterion:** The destroy gate is operational per the
consumer's infrastructure-misconfiguration.infrastructure-security-baseline chosen option.

## Outcome

The L2 test suite for infrastructure-misconfiguration.deletion-protection-and-drift succeeds when every scenario
above passes against the IaC's current state. Failures are
treated as PR-blocking findings or operational-incident triage
items unless the IaC is on the consumer's documented exception
list per the infrastructure-misconfiguration.deletion-protection-and-drift review-checklist's exception governance.
