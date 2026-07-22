<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.data-governance data governance (good pattern)

Substrate-original illustration.

```yaml
# dataset_card.yaml for the training set.
dataset: claims-2025
provenance: "Internal claims system, 2023-2025, collected for claims processing."
composition:
  regions: [northeast, southeast, midwest, west]
  known_gaps: "Rural west under-represented (4% of rows vs 11% of customers)."
representativeness_assessment: "Reweighted to customer base; west gap recorded."
use_basis: "Claims-processing use consistent with collection basis; legal sign-off 2026-01."
personal_data: "Contains personal data; lawful basis and purpose confirmed with privacy concern."
```

## Why this satisfies the rule

The dataset is documented in provenance, composition, and known gaps; its
representativeness for the deployment population is assessed and the under-covered
subgroup is recorded rather than carried silently; and its use is confirmed
consistent with the basis on which it was collected, with the personal-data
obligations routed to the privacy concern. The model's blind spots are visible
rather than hidden.
