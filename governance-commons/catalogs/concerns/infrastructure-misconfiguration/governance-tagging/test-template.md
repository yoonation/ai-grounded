---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.infrastructure-misconfiguration.governance-tagging-governance-tagging"
title: "infrastructure-misconfiguration.governance-tagging test template: mandatory governance tagging"
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
framework-agnostic: true
---

# infrastructure-misconfiguration.governance-tagging test template: mandatory governance tagging

## How to use this binding

Governance-tagging tests exercise the IaC-declared tag posture
against the substrate's required tag schema (owner, environment,
cost-center, data-sensitivity on data-bearing resources). Tests
are framework-agnostic: the same scenarios apply across cloud
providers and the consumer's IaC framework selection.

Substrate-recommended cadence: pre-merge for every PR that
modifies provider configuration or introduces a new resource;
weekly full-suite execution as part of the tagging-posture audit;
on-trigger when the data-classification matrix changes.

## Scenario 1: Provider default_tags block declares the substrate-required keys

**Intent:** The default_tags block (or equivalent) is the
substrate-recommended mechanism for applying mandatory tags
uniformly; the absence of the block in favor of per-resource tag
declarations correlates with inconsistent tagging.

**Test approach:**

1. Inspect the IaC's provider configuration (Terraform provider
   block, Pulumi provider construction).
2. Assert a `default_tags` block (AWS) or equivalent default
   tag mechanism is present.
3. Assert the block declares the substrate's required keys:
   `owner`, `environment`, `cost-center`.

**Pass criterion:** Provider-level default tags declare the
substrate's required keys.

## Scenario 2: Tag values are from the substrate's accepted vocabulary

**Intent:** Tag-value correctness is L2's contribution beyond
tag-presence (the substrate considered tag-presence a candidate
L1 rule).

**Test approach:**

1. For each tagged resource, read the values of the substrate's
   required keys.
2. Assert `environment` is in
   `{production, staging, development, ephemeral}`.
3. Assert `data-sensitivity` (where present) is in
   `{public, internal, confidential, restricted}`.
4. Assert `owner` resolves to a known team identifier in the
   consumer's owner registry.
5. Assert `cost-center` resolves to a known cost unit per the
   cost-model-selection concern's matrix.

**Pass criterion:** Every required-key value is from the
substrate-accepted vocabulary or the consumer's documented
equivalent.

## Scenario 3: Data-bearing resources carry the data-sensitivity tag

**Intent:** Data-bearing resources require the data-sensitivity
tag for downstream data-class-aware operations.

**Test approach:**

1. Enumerate every resource in the infrastructure-misconfiguration.data-resource-encryption-at-rest data-bearing set.
2. For each, assert the `data-sensitivity` tag is present.
3. Assert the value is appropriate for the data the resource
   holds (this is the judgment the L1 candidate could not
   encode; the test relies on the consumer's documented
   classification matrix, which the infrastructure-misconfiguration.infrastructure-security-baseline ADR points to).

**Pass criterion:** Every data-bearing resource carries
data-sensitivity at the appropriate value.

## Scenario 4: Tag schema is consistent across modules and across providers

**Intent:** Drift between Owner / owner / ownedBy / team across
modules defeats downstream operations.

**Test approach:**

1. Enumerate every tag key used anywhere in the IaC.
2. Group keys by the logical concept (owner, environment,
   cost-center, data-sensitivity, plus consumer-specific
   additions).
3. Assert each logical concept uses exactly one spelling across
   the entire repository.

**Pass criterion:** Each logical concept has exactly one key
spelling.

## Scenario 5: Organization-level tag-enforcement policies are declared

**Intent:** Organization-level enforcement catches resources
created outside IaC and resources that bypass the provider
default_tags.

**Test approach:**

1. For AWS, locate the AWS Organization tag policy IaC.
2. For Azure, locate the Azure Policy resource-tag rule IaC.
3. For GCP, locate the GCP Organization Policy resource-tag
   rule IaC.
4. Assert each is present and enforces the substrate's required
   keys.
5. Where organization-level enforcement is deferred, assert the
   infrastructure-misconfiguration.infrastructure-security-baseline ADR documents the deferral.

**Pass criterion:** Organization-level enforcement is in place
or the deferral is documented.

## Scenario 6: Where the consumer's schema differs from the substrate's, the mapping is documented

**Intent:** The substrate accepts alternative schemas provided
the substrate's required information is captured.

**Test approach:**

1. Inspect the consumer's repository README, tagging-policy
   document, or equivalent.
2. Assert a mapping document exists.
3. Assert the mapping covers every substrate-required information
   type (owner, environment, cost-center, data-sensitivity).
4. Spot-check that the IaC's actual key usage matches the
   documented mapping.

**Pass criterion:** Mapping is documented; IaC matches the
mapping.

## Scenario 7: Live infrastructure tag state matches IaC declaration

**Intent:** A tag declared in IaC but mutated out-of-band
defeats the substrate's reviewability intent.

**Test approach:**

1. For a representative sample of resources, retrieve the live
   tag state via the cloud provider's API.
2. Compare the live state against the IaC declaration.
3. Assert the live state matches.
4. Where drift exists, raise it as an infrastructure-misconfiguration.deletion-protection-and-drift drift-detection
   finding (the two binding's surfaces touch here).

**Pass criterion:** Live tag state matches IaC declaration, or
drift is detected and triaged.

## Outcome

The L2 test suite for infrastructure-misconfiguration.governance-tagging succeeds when every scenario
above passes against the IaC's current state. Failures are
treated as PR-blocking findings unless the IaC is on the
consumer's documented exception list per the infrastructure-misconfiguration.governance-tagging review-
checklist's exception governance.
