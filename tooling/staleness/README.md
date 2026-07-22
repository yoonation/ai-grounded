# staleness — north-star drift gate

A north-star is loaded first on every run, so a `current-objective` that no longer points
at real work misdirects every agent with authority. This fitness function checks that the
objective still resolves to a real open item: an active feature under `specs/`, or an open
`PROJECT-LOG` entry (one not yet promoted to an ADR).

Advisory: reports a verdict (`resolves`, `referent`, `reason`) and always exits 0.
Enforcement is skill-instructed at the phase boundary where the north-star is updated.

In a template repo with no in-flight feature, the gate correctly reports no active
feature; it does its real work in consumer repos.

```
uv run --with pyyaml python3 tooling/staleness/check.py \
    --north-star NORTH-STAR.md --specs-dir specs --log PROJECT-LOG.md --text
```

Tests (hyphen-dir, invoke directly): `python3 tooling/staleness/test_check.py`
