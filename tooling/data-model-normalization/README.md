# data-model-normalization - normalization forcing-function gate (IMP-12)

Checks that data-model.md carries an explicit normalization declaration, so a data model cannot ship without stating its single-source-of-truth decision, while staff-engineer judges whether that decision is correct.

This is the deterministic half of the FW-001 fix. The plan phase generates data-model.md
freehand, and a field that is constant across a referencing dimension (one identity column
repeated per persona, one address repeated per order) can be duplicated per-referrer with
no signal, because nothing required the plan to state its cardinality decision at all. That
is the substrate's single-source-of-truth principle
(`code-organization.data-model-single-source-of-truth`, the sibling of
`duplication-and-abstraction`) unapplied at the data layer.

The fix is the framework's force / gate / judge split:

- **force**: the plan skill requires data-model.md to carry a Normalization declaration
  stating, per entity, which fields are owned per-instance and which are shared across a
  referencing dimension and therefore belong in a referenced entity.
- **gate**: this tool. It confirms deterministically that the declaration is present and
  is not a placeholder. It does not judge correctness; a present-but-wrong declaration is
  a reasoning failure for staff-engineer, citing the same rule id. The gate closes the S1
  signal gap: a data model that shipped with no declaration can no longer pass silently.
- **judge**: staff-engineer, reasoning against the substrate rule, decides correctness.

The check is language-agnostic and format-light. It recognizes a declaration by a heading
(`## Normalization`) or a label line (`Cardinality: ...`) naming normalization,
single-source-of-truth, ssot, or cardinality, confirms the section has real content, and
rejects placeholders (tbd, todo, n/a, none, fixme, empty). A data-model.md with no
declaration fails; a feature with no data-model.md at all passes, because there is nothing
to normalize and so no signal to raise.

It enforces the structural contract of the substrate rule
`code-organization.data-model-single-source-of-truth`. The rule carries the human-authored
intent; this tool carries its checkable shadow. Advisory by default (exit 0); `--strict`
exits 1 on a missing or placeholder declaration. Wire `--strict` where the dial's andon is
blocking; leave it advisory where the dial is advisory.

```
python3 tooling/data-model-normalization/check.py --path specs/004-x/data-model.md --text
python3 tooling/data-model-normalization/check.py --repo-root . --strict
```

The declaration-finding core is pure and stdlib-only, so the gate is fully unit-tested
without a real repo.

Tests (invoke directly): `python3 tooling/data-model-normalization/test_check.py`
