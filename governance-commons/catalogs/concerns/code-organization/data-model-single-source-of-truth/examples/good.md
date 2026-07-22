<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.data-model-single-source-of-truth data-model single source of truth (good pattern)

Substrate-original illustration. An operator owns many personas. The
operator's home region is one fact about the operator, the same for every
persona they own, so it lives once on the operator and the personas
reference the operator by key. The model states this cardinality decision
explicitly rather than leaving it implicit.

## SQL: a shared fact normalized to the parent it describes

```sql
-- home_region is constant across all of an operator's personas, so it is
-- one fact about the operator and lives on the operator.
CREATE TABLE operator (
    operator_id   uuid PRIMARY KEY,
    home_region   text NOT NULL          -- shared across the operator's personas
);

CREATE TABLE persona (
    persona_id    uuid PRIMARY KEY,
    operator_id   uuid NOT NULL REFERENCES operator(operator_id),
    display_name  text NOT NULL          -- genuinely per-persona
);
```

The data model records the decision so it can be reviewed and the gate can
confirm it was made:

```
# data-model.md (cardinality declaration)
operator.home_region    shared-across: persona      home: operator
persona.display_name    owned-per-instance
```

Why this passes: home_region is one piece of knowledge about the operator,
the same for every persona they own, so it is stored once and referenced by
key. A change of region is one edit in one place, and no export or cache can
carry a stale copy of it. display_name genuinely varies per persona and is
correctly left on the persona. The cardinality decision is stated, not
skipped, so a reviewer can confirm it is right and the
data-model-normalization gate can confirm it was declared.
