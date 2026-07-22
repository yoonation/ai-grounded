<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.model-documentation-artifact model documentation artifact (anti-pattern)

Substrate-original illustration.

```python
# A model deployed straight from a training run with no model card.
model = joblib.load("artifacts/latest.pkl")
registry.deploy(model, endpoint="fraud-scorer")  # no documentation artifact
```

## Why this violates the rule

The model is deployed with no documentation artifact, so its intended use, its
limitations, and how it was evaluated were never recorded. Nothing states where
the model must not be used or what it was tested against, and the responsible-ai
conformance rules have no anchor. A model card or system card carrying the
required fields is the fix.
