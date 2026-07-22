---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: logging.no-sensitive-data-in-logs
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Deciding that log records never carry sensitive data classes (credentials,
  PII, PHI, payment data) as field values requires judgment about what a value
  represents in context, which a static tool cannot fully resolve. Static
  analysis flags a partial set of patterns; the full property is review-decidable.
review-triggers:
  - New or changed logging code, especially structured-field population
  - A log call begins carrying a value derived from user or account data
  - Introduction of a new data class into the system
  - Periodic security self-assessment
---

# Review checklist: log records do not carry sensitive data

## How to use this binding

Apply to logging code that populates message bodies or structured fields with
values that could be sensitive. The sast gate assists; this review confirms.

## Review questions

- Do log records exclude authentication credentials (passwords, secret keys, API
  tokens, OAuth client secrets, full bearer tokens) as field values or message
  fragments?
- Do log records exclude personal data (names, emails, addresses, government
  identifiers), health data, and payment card data, or carry only masked or
  tokenized forms where an identifier is required?
- For values derived from user or account input, is the sensitive portion masked,
  hashed, or omitted before it reaches the logger?
- Is the same discipline applied across all environments, not only production?

## Mechanical assists (sast gate)

The sast gate flags known sensitive-logging patterns. Treat findings as
violations pending review; a clean run is necessary but not sufficient.
