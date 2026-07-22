---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: secrets-management.no-secrets-in-logs
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Detecting that no secret value reaches any log, span, metric label, or error
  emission, and that a masking wrapper is applied wherever a secret is handled,
  requires contextual judgment a static tool cannot fully resolve. Static
  analysis catches a partial set of anti-patterns (debug mode enabled, stack
  trace exposure, logging of secret-named variables); the full property is
  review-decidable. The mechanical anti-pattern detection is available through
  the sast gate as an assist, not as the resolver.
review-triggers:
  - A code path begins handling a secret value (key, token, credential)
  - New or changed logging, tracing, metric, or error-response code
  - Introduction or change of a secret-wrapping or masking type
  - Periodic security self-assessment
---

# Review checklist: secrets do not reach logs, telemetry, or error responses

## How to use this binding

Apply these questions to any code path that both handles a secret value and
emits to an observability or error surface. A static analyzer (the sast gate)
can flag obvious cases; this review confirms the property the tool cannot.

## Review questions

- Are secret values held in a wrapper or context type whose string conversion
  masks the content, rather than passed as raw strings into loggers, span
  attributes, metric labels, error messages, or analytics events?
- For each log, trace, metric, and error emission on a secret-handling path, is
  the emitted value the masked form, never the raw secret?
- Are stack traces and debug dumps configured so local variable values are not
  included by default, and where introspection is enabled in developer
  environments does the masking wrapper still apply?
- Are error responses returned to clients free of secret values, including
  values that might be embedded in exception messages?
- Are placeholder or test secrets treated the same as production secrets, so a
  masked-only discipline holds even for non-production credentials?

## Mechanical assists (sast gate)

The sast gate flags a partial set: debug mode enabled in production, stack trace
exposure to clients, and logging of secret-named variables. Treat findings as
violations pending review; treat a clean sast run as necessary but not
sufficient.
