# constitution — constraint injector (construct-time poka-yoke)

Assembles the constitution's hard "do not write this" constraints into the implement
context as hard inputs, ahead of the coding pass, so the forbidden patterns are not
written in the first place. The active-constitution complement to the review wave: the
review agents read articles to verify after the fact; this puts the forbidden-pattern
slice in front of construction, shrinking what verification must catch.

Extracts deterministically from `.specify/memory/constitution.md`:
- Article II §2.5 "forbidden without an ADR" (the anti-pattern list)
- Article II §2.5 "forbidden absolutely, no ADR override" (the bright lines)
- Article II §2.6 secrets-management constraints
- Article V's named OWASP security vocabulary (the mapping note, verbatim)

A transform: reads the constitution read-only, emits the constraint block, always
exits 0. The implement skill injects `--text` output as hard inputs before coding.

```
python3 tooling/constitution/inject.py --text          # the injectable block
python3 tooling/constitution/inject.py                 # structured JSON
```

Tests (hyphen-dir, invoke directly): `python3 tooling/constitution/test_inject.py`
