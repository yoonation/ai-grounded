# lib - shared tooling primitives

The first shared module across the `tooling/` scripts, which are otherwise
standalone. It exists because the same pattern recurred past the rule-of-three.

## references.py

`find_dangling(edges, resolvers)` detects dangling references: given declared
edges `(source, target, kind)` and a resolver per kind, it returns the edges whose
target does not resolve. It is reference resolution, not graph validation, no cycle
detection or traversal, because the artifacts it serves (tasks, the manifest) have
no such structure.

Two consumers today:
- `tooling/consistency` (IMP-1): a done task's named file must exist on disk.
- `tooling/manifest`: a checkpoint's referenced article, agent, file, and catalog
  must exist.

It is pure (resolvers injected, so it is testable without disk) and never treats a
missing resolver as success: an edge whose kind has no resolver is returned under
`unresolvable` so the caller can surface a loud skip instead of a silent pass.

Standalone scripts import it via a `sys.path` insert to `tooling/lib`:

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from references import find_dangling
```

Tests: `python3 tooling/lib/test_references.py`
