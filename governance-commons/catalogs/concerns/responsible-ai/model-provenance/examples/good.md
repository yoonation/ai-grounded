<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: responsible-ai.model-provenance model provenance (good pattern)

Substrate-original illustration.

```json
{
  "serving_model": {
    "name": "fraud-scorer",
    "version": "4.2.0",
    "training_data_snapshot": "claims-2025@sha256:9f2c…",
    "evaluation_run": "eval-2026-q1#run-118",
    "rollback_target": "4.1.0"
  }
}
```

## Why this satisfies the rule

The serving model exposes its version bound to the artifact, references the
training-data snapshot it was trained on and the evaluation run it passed, and
names an addressable prior version for rollback. At incident time the model is an
investigable object. The cryptographic attestation of the artifact is owned by
supply-chain; this rule confirms the lineage is recorded and exposed.
