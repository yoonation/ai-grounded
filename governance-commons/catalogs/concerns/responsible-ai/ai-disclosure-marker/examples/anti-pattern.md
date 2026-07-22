<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.ai-disclosure-marker AI disclosure marker (anti-pattern)

Substrate-original illustration.

```python
# A generative endpoint returns model output to a person with no disclosure.
@app.post("/assistant")
def assistant(prompt: str):
    return {"reply": llm.complete(prompt)}  # no AI disclosure
```

## Why this violates the rule

The endpoint returns model-generated content to a person with no marker that the
content is AI-generated. The person cannot tell they are consuming AI output, so
they cannot calibrate trust or seek a human alternative, and every further
transparency protection is undercut. Attaching a disclosure marker, preferably on
a shared response wrapper, is the fix.
