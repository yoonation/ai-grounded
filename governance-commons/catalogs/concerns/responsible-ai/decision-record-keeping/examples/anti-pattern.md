<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.decision-record-keeping decision record-keeping (anti-pattern)

Substrate-original illustration.

```python
# The decision is made and returned; nothing is recorded.
def decide(payload):
    return model.predict(payload)   # no record of input, version, or output
```

## Why this violates the rule

The decision leaves no trace: there is no record of the input, the model version,
or the output, so a later complaint, incident, or audit has nothing to examine
and the decision cannot be reconstructed. A bounded record capturing the input
reference, model version, output, and any override, written through the logging
mechanism, is the fix.
