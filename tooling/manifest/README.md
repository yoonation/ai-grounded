# manifest - reference validator (semantic half to the schema gate)

The schema gate (`tooling/schema`) proves `project-manifest.yaml` has the right
shape. It cannot prove the strings inside name things that exist. A checkpoint that
consults `concerns/authentcation` (typo) or cites `Article-VIII` (no such article)
passes the schema and then silently consults nothing or slices no constitution.
This validator closes that semantic gap by resolving each declared reference,
built on the shared `tooling/lib/references.py` primitive.

References checked:

| reference | resolves against | coupling |
|---|---|---|
| `constitution-articles` | `## Article N` in the constitution | framework-internal |
| `consulter` (agent) | `.claude/agents/<name>.md` (or a known tool consulter) | framework-internal |
| `stack.pins-source` | a file on disk | framework-internal |
| checkpoint `consults.catalogs`, `concerns.always/never` | `governance-commons/catalogs/<ref>` (dir) or `<ref>.yaml`/`.oscal.yaml` | substrate (best-effort) |

If `governance-commons/catalogs/` is absent, catalog references are reported as
NOT VALIDATED, a loud skip, never a silent pass, and do not block (the substrate
layout is not fixable from here). Deferred: `decision-frameworks` and individual
rule ids (rule resolution would mean parsing OSCAL content, deep substrate coupling
for low marginal value).

Report-only by default (exit 0); `--strict` exits 1 on a dangling reference. The
gate wrapper `.githooks/pre-commit.d/60-manifest` fires when `project-manifest.yaml`
is staged, with `MANIFEST_STRICT=1` to enforce and `SKIP_MANIFEST=1` to bypass,
matching the `50-schema` posture: 50 checks the shape, 60 checks the references.

```
uv run --with pyyaml python3 tooling/manifest/check.py --repo-root . --text
```

Verified against the real manifest: all 51 references resolve. Tests:
`python3 tooling/manifest/test_check.py`
