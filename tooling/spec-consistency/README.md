# spec-consistency - spec-internal enumeration consistency (IMP-1b)

The feature-003 F7/F10 class: an amendment fixed the FRs to seven dimensions but left
the US1 narrative, FR-017, and both Key Entities saying "six". The spec disagreed with
itself about the size of an enumerated set, and only operator vigilance caught it,
twice. `tooling/consistency` catches declared-vs-actual on disk (a done task naming a
missing artifact); this catches declared-vs-declared inside a spec: the same noun
asserted with two different cardinalities.

## What it does

It extracts `<count> <noun>` phrases (count = a number word `one`..`twenty` or a one-
or two-digit number), groups by the lowercased noun, and flags any noun given more
than one distinct count. "six dimensions ... seven dimensions" flags; "three tracks
... three tracks" does not.

It is a high-precision heuristic, not an NLP parser:

- the noun must be plural (cardinality phrases are: "six dimensions"), which drops
  singular-word mis-parses like "12 real" or "4 would";
- counts above twelve are excluded (years, ids, not set sizes);
- structural nouns (version, section, step, phase, ...) are excluded.

The member-level check (narrative lists `track` where the FRs reference `angle`) is
fuzzier and intentionally not attempted; this is the numeric-agreement half, which is
the half that recurred in feature-003.

## Posture

Advisory. The `70-spec-consistency` gate runs it over staged `spec.md` files, report-
only by default; `SPEC_CONSISTENCY_STRICT=1` makes a conflict block, `SKIP_SPEC_
CONSISTENCY=1` bypasses. Findings are candidates for review, not proof: two unrelated
sets that happen to share a noun can collide, so a human confirms. Stdlib-only.

```
python3 tooling/spec-consistency/check.py specs/003-x/spec.md --text
python3 tooling/spec-consistency/check.py --repo-root . --strict
```

The pure core (extraction, grouping, conflict detection) is unit-tested. Tests:
`python3 tooling/spec-consistency/test_check.py`
