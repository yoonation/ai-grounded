<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.agent-memory-integrity agent memory integrity (good pattern)

Substrate-original illustration.

```python
# Memory entries carry provenance, are validated, and are treated as data.
def recall(query, ctx):
    entries = memory.search(query, tenant=ctx.tenant)   # tenant-scoped
    valid = [e for e in entries if e.integrity_ok() and e.provenance]
    # untrusted-origin memory is framed as data, not instruction
    return [as_data(e) for e in valid]
```

## Why this satisfies the rule

Memory is scoped to the tenant so one tenant's memory cannot bleed into
another's, entries are integrity-checked and carry provenance so a tampered or
unattributed entry is dropped, and recalled memory is framed as data subject to
the same instruction/data separation as fresh content (agentic-systems.instruction-data-separation). Memory is
treated as untrusted-until-validated rather than as the agent's own ground
truth; classified memory defers to data-classification.
