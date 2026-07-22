<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.data-governance data governance (anti-pattern)

Substrate-original illustration.

```python
# Training data assembled from whatever was on hand, undocumented.
df = pd.concat([read_csv("dump_a.csv"), read_csv("scraped.csv")])
model.fit(df)  # no provenance, no composition, no representativeness check
```

## Why this violates the rule

The training data is of unknown provenance and composition, mixes a source
scraped for a different purpose, and is never assessed for representativeness, so
the model's gaps and its legitimacy are both unknown. A documented dataset with
recorded composition, a representativeness assessment, and a use consistent with
its collection basis is the fix; personal data routes to the privacy concern.
