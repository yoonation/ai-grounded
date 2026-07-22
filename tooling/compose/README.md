# compose — deterministic context composition

Assembles every agent's context in one fixed order and nothing else, the "one mechanism
per horizon" rule from the context-memory design:

1. **North star** (`NORTH-STAR.md`) — always first. Durable intent; why the project exists.
2. **Working set** — the `project-manifest.yaml` slice for this checkpoint (catalogs,
   decision frameworks, constitution articles), resolved by position (C1..C4 map 1:1 to
   the manifest's `workflow.checkpoints`).
3. **Open log items** — `PROJECT-LOG.md` entries not yet promoted to an ADR.

The order is cache-favorable: most-stable content first (north star, changed only at
phase boundaries), then the stable per-checkpoint slice, then the volatile open items
last, maximizing the cacheable prefix. Intent stays human-authored; composition stays
deterministic and auditable.

Advisory: always exits 0. It is a tool, not a hook — you run it and inject its output.

```
uv run --with pyyaml python3 tooling/compose/compose_context.py \
    --checkpoint C1 --north-star NORTH-STAR.md \
    --manifest project-manifest.yaml --log PROJECT-LOG.md
```

Tests (hyphen-dir, invoke directly): `python3 tooling/compose/test_compose.py`
