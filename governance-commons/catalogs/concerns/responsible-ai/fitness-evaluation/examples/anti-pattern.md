<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.fitness-evaluation fitness evaluation (anti-pattern)

Substrate-original illustration.

```python
# Deploy on a single aggregate number, no subgroups, no gate.
acc = accuracy(model, eval_set)
print(f"accuracy {acc:.2f}")   # logged, not gated
registry.deploy(model)         # ships regardless of the number
```

## Why this violates the rule

The model is judged on one aggregate metric, with no disaggregated reporting and
no deployment gate, so a system that is accurate on average but systematically
wrong for a subgroup ships unmeasured. An evaluation tied to the intended use,
reported per relevant subgroup, and gating deployment is the fix.
