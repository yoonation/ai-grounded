<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.no-hardcoded-flag no hardcoded flag (good patterns)

Substrate-original good-pattern examples for feature-flags.no-hardcoded-flag. A live flag is
evaluated through the provider, not pinned to a constant or short-circuited in
source. Clean removal after retirement is the intended end state, not a finding.

## Python: the flag is evaluated, not pinned

```python
# the decision is delegated to the provider, which can stage the rollout
if flags.get_boolean("search.semantic-ranking", default=False):
    results = semantic_rank(query)
else:
    results = lexical_rank(query)
```

## Python: a retired flag, removed cleanly (not a finding)

```python
# search.semantic-ranking reached 100 percent and was retired;
# the kept branch now stands alone with no flag reference
results = semantic_rank(query)
```

The live flag routes through the provider so it can be targeted and rolled
back; the retired flag leaves no evaluation behind. Neither shape pins a live
flag to a literal.
