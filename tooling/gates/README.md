# gates - the self-describing gate inventory

Guidance kept drifting behind the gate chain: workflow skills named tools that no
longer matched `pre-commit.d/`, and a hand-maintained gate list is just another
declaration that disagrees with disk. The durable fix is to make the inventory
derive from the source of truth (the gate files) rather than restate it.

Every gate in `.githooks/pre-commit.d/` carries a machine-readable header:

```sh
# gate-meta:
#   order: 40
#   name: quality
#   posture: report-only        # fail-closed | report-only
#   skip: SKIP_QUALITY
#   strict: QUALITY_STRICT       # the *_STRICT var, or none
#   summary: one line, what it checks and why
# end-gate-meta
```

`describe.py` scans the executable gates (the dispatcher's own rule; `.md` files
and non-executables are skipped), parses those headers, also inventories the
on-demand `tooling/*/` tools, and emits the inventory as Markdown (default) or
`--json`. The committed inventory lives at `docs/GATES.md`.

`describe.py --check` is the anti-drift enforcement. It fails on two conditions: a
gate missing or with a malformed `gate-meta` header (a new gate cannot ship
undescribed), and a committed `docs/GATES.md` that no longer matches the gates on
disk (drift). Report-only by default (exit 0); `--strict` exits 1.

The `gate-inventory` meta-gate (`.githooks/pre-commit.d/00-gate-inventory`) runs
`--check` on every commit, report-only by default, `GATES_STRICT=1` to enforce,
`SKIP_GATES=1` to bypass. It runs first (order 0) and describes itself, so it is
held to the same header rule.

Regenerate the committed inventory after adding or changing a gate:

```
python3 tooling/gates/describe.py > docs/GATES.md
```

Tests: `python3 tooling/gates/test_describe.py`
