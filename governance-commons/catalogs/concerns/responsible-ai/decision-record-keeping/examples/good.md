<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.decision-record-keeping decision record-keeping (good pattern)

Substrate-original illustration.

```json
{
  "decision_id": "d-90412",
  "input_hash": "sha256:1aa9…",
  "model_version": "4.2.0",
  "output": "route_to_review",
  "human_override": null,
  "ts": "2026-06-02T14:03:11Z"
}
```

## Why this satisfies the rule

The record captures enough to reconstruct the decision (an input reference by
hash, the model version, the output, and any human override) at a granularity
sufficient for review and bounded so it does not store raw sensitive input. It is
written through the logging concern's mechanism and retained per policy; the
redaction of classified or personal fields is owned by data-classification.
