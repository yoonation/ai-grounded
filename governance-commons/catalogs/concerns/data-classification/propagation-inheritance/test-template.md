---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "test-templates.data-classification.propagation-inheritance-propagation-inheritance"
title: "data-classification.propagation-inheritance test template: classification propagation through data flows"
substrate-rule: "data-classification.propagation-inheritance"
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

# data-classification.propagation-inheritance test template: classification propagation through data flows

## How to use this binding

Propagation is testable by moving classified data through a flow (a copy, a
derivation, an export, a cache write) and asserting the destination carries
the inherited class, and that a destination which cannot meet a class is
refused the data. Adapt the flow and the classification accessor to the stack.

## Scenario 1: an exported artifact carries the inherited class

Export or derive an artifact from a restricted-class source. Read the class of
the exported artifact.

Pass criteria: the exported artifact carries at least the source's restricted
class. An export that drops the class is the finding.

## Scenario 2: a tier that cannot meet a class is refused that class

Attempt to cache or write a confidential value to a tier or destination that
the policy marks as unable to meet the confidential class (a shared or edge
cache, an analytics store).

Pass criteria: the write is refused or routed away. A confidential value
landing in a tier its class forbids is the finding, regardless of the caching
mechanics.

## Scenario 3: a combination takes the most restrictive class

Combine data of two classes into a single downstream artifact (a merged
export, a joined cache entry). Read the combined artifact's class.

Pass criteria: the combined artifact carries the more restrictive of the two
input classes.
