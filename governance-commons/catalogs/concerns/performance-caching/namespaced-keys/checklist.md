---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
rule: performance-caching.namespaced-keys
layer: L2
status: stable
reclassified-from: mechanical
reclassification-rationale: >
  Whether a cache key is well namespaced and versioned is a design judgment about
  the key's components and the value's shape-change risk, which a static tool
  cannot fully resolve.
review-triggers:
  - New cache key construction or a new cached value type
  - A cached value's shape changes across a deploy
  - Changes to cache key derivation logic
---

# Review checklist: cache keys are namespaced and versioned

## Review questions

- Is the key built from a stable namespace prefix (a data-type or domain prefix)
  plus structured components, rather than an ad hoc concatenation?
- Where the cached value's shape can change across deploys, does the key carry a
  version component so stale-shape reads cannot occur?
- Are key components collision-safe across distinct entities?

## Mechanical assist

The sast gate can flag clearly unstructured key construction in some cases; the
namespacing and versioning judgment is review-decidable.
