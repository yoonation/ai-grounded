<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.instruction-data-separation instruction and data separation (good pattern)

Substrate-original illustration.

```python
# Retrieved content is framed as data; the instruction channel is reserved for
# the system and the authenticated user.
messages = [
    {"role": "system", "content": SYSTEM_POLICY},
    {"role": "user", "content": authenticated_user_request},
    {"role": "user", "content": f"<retrieved_data>{escape(doc)}</retrieved_data>"},
]
# Ingested content cannot expand authority or fire a consequential tool on its
# own; consequential tools still require the authorized, gated path.
```

## Why this satisfies the rule

The system prompt and authenticated user request occupy the instruction channel,
while retrieved content is framed and escaped as data to reason about, so a
planted instruction in a document is not obeyed as a command. Ingested content
cannot widen authority or fire a consequential tool on its own; that still
requires the authorized path with its bounds and gate as defense in depth. The
service input boundary is owned by input-validation.
