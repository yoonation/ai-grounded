---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.data-classification.encryption-per-class-encryption-per-class"
title: "data-classification.encryption-per-class test template: encryption at rest and in transit per class"
substrate-rule: "data-classification.encryption-per-class"
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
ai-assistance: "AI drafted from substrate-author intent at M4 Session 6 (2026-05-31). Substrate-author review required for stable promotion."
framework-agnostic: true
---

# data-classification.encryption-per-class test template: encryption at rest and in transit per class

## How to use this binding

Encryption posture is testable against the datastore and transport
configuration. The at-rest check is a configuration assertion; the in-transit
check connects and asserts a plaintext connection is refused. Adapt to the
consumer's datastore and TLS setup.

## Scenario 1: a classified store rejects an unencrypted connection

Attempt to connect to a store holding confidential or restricted data over a
plaintext (non-TLS) connection.

Pass criteria: the connection is refused. A store that accepts a plaintext
connection for classified data is the finding.

## Scenario 2: at-rest encryption is enabled for the higher-class stores

As a configuration test, assert the deployed manifest for each store holding
confidential or restricted data declares at-rest encryption enabled with a
managed key.

Pass criteria: every higher-class store declares at-rest encryption with a
policy-managed key; an unencrypted classified store fails.

## Scenario 3: the per-class encryption standard is recorded

Assert that the classification policy records an encryption standard for each
class and that each classified store's configuration meets at least its
class's standard.

Pass criteria: each store meets or exceeds its class's recorded standard. A
store weaker than its class requires is the finding.
