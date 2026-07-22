<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.output-safety output safety (good pattern)

Substrate-original illustration.

```python
# The output path filters, checks groundedness, and can refuse.
def answer(query: str, context: list[str]) -> Response:
    draft = llm.complete(query, context)
    if not grounded_in(draft, context):
        return refuse("I can't support that from the available sources.")
    if content_filter.flags(draft):
        return escalate(draft)
    return ai_response(draft)
```

## Why this satisfies the rule

The output path applies content filtering scaled to the system's harms, checks
that an answer is grounded in its source before returning it, and has a defined
refusal and escalation behavior, all before content reaches the person. The
input-side prompt-injection defense is owned by input-validation and
agentic-systems; this is the output side, and it is testable against adversarial
prompts.
