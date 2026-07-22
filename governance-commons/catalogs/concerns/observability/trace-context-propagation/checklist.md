---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: observability.trace-context-propagation
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether outbound calls correctly propagate the active trace context depends on
  instrumentation setup and the call's runtime context, which a static tool
  cannot fully resolve.
review-triggers:
  - New or changed outbound HTTP or gRPC call sites
  - Changes to instrumentation, interceptors, or HTTP client setup
  - A new downstream dependency is integrated
---

# Review checklist: trace context propagates to downstream calls

## Review questions

- Do outbound HTTP and gRPC calls propagate the active context via W3C Trace
  Context headers (traceparent and where used tracestate)?
- Is propagation applied through shared instrumentation or interceptors rather
  than ad hoc per call site, so new calls inherit it?
- For calls made outside an active span, is context creation or continuation
  handled correctly rather than silently dropped?

## Mechanical assist

The lint gate can confirm an instrumentation library is imported; it cannot
confirm propagation is wired at every outbound call. Review confirms coverage.
