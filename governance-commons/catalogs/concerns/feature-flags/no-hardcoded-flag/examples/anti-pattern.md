<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: feature-flags.no-hardcoded-flag no hardcoded flag (anti-patterns)

Substrate-original anti-pattern examples for feature-flags.no-hardcoded-flag. A flag identity still
lives in the code, but its value is pinned to a constant or the evaluation is
short-circuited, so the flag can no longer be targeted or rolled back.

## Python: the flag is pinned to a literal

```python
# the provider is bypassed; the "flag" is now a constant in disguise
SEMANTIC_RANKING = True  # was flags.get_boolean("search.semantic-ranking")
if SEMANTIC_RANKING:
    results = semantic_rank(query)
else:
    results = lexical_rank(query)  # dead, but the flag looks live
```

## TypeScript: evaluation short-circuited before the provider call

```typescript
// the provider call is ORed out, so targeting and kill-switch are dead
const on = true || (await flags.getBooleanValue("search.semantic-ranking", false));
```

Why this is flagged: the flag identity remains in source, implying it is
controllable, but no provider evaluation reaches it, so staged rollout and the
kill switch silently do nothing. The remediation is either to evaluate the flag
through the provider again or, if the rollout is complete, to retire the flag
and remove the dead branch.
