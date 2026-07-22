# duplication — duplication / dependency gate (advisory)

Reads the capability index and flags exported symbols that recur under the same name in
more than one file — a lead that the same capability was built twice and should be a
shared helper. Conventional names that are expected to recur (CLI `main`, dunders,
`setup`) are ignored so the real signal isn't drowned in boilerplate.

Pairs with the discovery agent: the agent reasons over the index with fresh eyes before
construction; this gate is the deterministic backstop that names the concrete
collisions. The flag is for a human to confirm on inspection — a recurring name can be
real duplication or an honest coincidence.

Advisory first: always exits 0, emits `passes` and the `duplicates` list. Run it on the
freshly generated index (the implement skill regenerates from source first).

```
python3 tooling/capability-index/generate.py . --out .capability-index.json
python3 tooling/duplication/check.py .capability-index.json --text
```

Tests (hyphen-dir, invoke directly): `python3 tooling/duplication/test_check.py`
