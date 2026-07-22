---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: observability.no-sensitive-data-in-telemetry
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Deciding that span attributes, metric labels, and trace baggage never carry
  credentials, PII, PHI, or payment data requires contextual judgment a static
  tool cannot fully resolve. Static analysis flags a partial set; the full
  property is review-decidable.
review-triggers:
  - New or changed span attributes, metric labels, or trace baggage
  - Instrumentation begins recording a value derived from user or account data
  - Introduction of a new data class into the system
  - Periodic security self-assessment
---

# Review checklist: telemetry does not carry sensitive data

## How to use this binding

Apply to instrumentation that sets span attributes, metric labels, or baggage.
The sast gate assists; this review confirms the property it cannot fully decide.

## Review questions

- Do span attributes, metric labels, and trace baggage exclude credentials and
  tokens as values?
- Do they exclude personal data, health data, and payment card data, or carry
  only masked or tokenized forms?
- Are high-cardinality user identifiers kept out of metric labels both for
  privacy and for cardinality reasons?
- Is the discipline applied across all environments?

## Mechanical assists (sast gate)

The sast gate flags known sensitive-telemetry patterns. Treat findings as
violations pending review; a clean run is necessary but not sufficient.
