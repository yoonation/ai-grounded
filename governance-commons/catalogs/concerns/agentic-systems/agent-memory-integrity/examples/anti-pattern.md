<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.agent-memory-integrity agent memory integrity (anti-pattern)

Substrate-original illustration.

```python
# Prior memory is trusted as ground truth and replayed as instruction.
def recall(query, ctx):
    notes = memory.search(query)        # shared store, no tenant scope
    return "\n".join(n.text for n in notes)   # concatenated as instruction,
                                              # no provenance, no validation
```

## Why this violates the rule

Prior memory is pulled from a shared, unscoped store and replayed straight into
the agent's reasoning as trusted instruction, so a note planted in one session
(or by another tenant) steers a later, otherwise-clean session, the
memory-poisoning failure that survives across sessions. Carrying provenance,
validating integrity, scoping by tenant, and treating memory as data is the fix.
