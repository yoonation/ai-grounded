<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.model-provenance model provenance (anti-pattern)

Substrate-original illustration.

```python
# The endpoint serves "the latest model" with no recorded lineage.
model = registry.load("fraud-scorer:latest")
serve(model)   # no version exposed, no data or eval reference
```

## Why this violates the rule

The deployed model exposes no version, no link to the data it was trained on, and
no reference to the evaluation it passed, so when it regresses or draws a
complaint nobody can say which model produced the result or roll back with
confidence. Recording and exposing the version, the training-data snapshot, and
the evaluation reference, with an addressable prior version, is the fix.
