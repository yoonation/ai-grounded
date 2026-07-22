<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.output-safety output safety (anti-pattern)

Substrate-original illustration.

```python
# Raw model output returned to the person with no controls.
def answer(query: str) -> str:
    return llm.complete(query)   # no filter, no groundedness, no refusal
```

## Why this violates the rule

The model's output is returned directly to the person with no content filtering,
no groundedness check, and no refusal behavior, so a harmful completion or a
confident hallucination reaches the person unimpeded at the last point where it
could have been caught. Output-safety controls scaled to the system's harms, with
adversarial testing, are the fix.
