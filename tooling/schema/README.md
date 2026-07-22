# schema - schema-enforcement gate

The framework ships JSON Schemas for its structured artifacts
(`.specify/schemas/project-manifest.schema.json`, `feature-concerns.schema.json`)
and instructs agents to emit conforming output, but nothing verified that the
actual instances conform. The schema is a declaration; whether the instance matches
it was never checked, which is the framework's own declared-vs-actual failure class
turned on itself. A malformed `project-manifest.yaml` or `feature-concerns.yaml`
silently breaks the tools that read it (the dial, the quality gate's language read,
the concern selector). This gate wires the validators the framework already owns
into the loop.

For each recognized instance among the staged files (or, with no files, every
instance it finds), it validates the instance against its schema:

| instance | schema |
|---|---|
| `project-manifest.yaml` | `project-manifest.schema.json` |
| `specs/*/feature-concerns.yaml` | `feature-concerns.schema.json` |

`events.jsonl` is deliberately excluded: its schema is permissive by design
(`additionalProperties: true` for cross-tool events), so validating it catches
little. The consumer sections of the manifest are validated against the consumer
schema; the substrate `manifest:` block is the substrate's concern.

Report-only by default (exit 0); `SCHEMA_STRICT=1` makes a nonconforming instance
block; `SKIP_SCHEMA=1` bypasses. Graceful no-op when the validator (`jsonschema`)
or YAML parser (`PyYAML`) is absent. Same posture as `30-sast` and `40-quality`;
not fail-closed like `10-gitleaks`.

The pure core (which files are instances; the verdict given a validator) is
stdlib-only and unit-tested without `jsonschema`/`PyYAML`; both are imported lazily
and supplied at run time via `uv`.

```
uv run --with jsonschema --with pyyaml python3 tooling/schema/check.py project-manifest.yaml --repo-root . --text
```

The gate wrapper is `.githooks/pre-commit.d/50-schema`, run automatically by the
pre-commit dispatcher. Tests (invoke directly): `python3 tooling/schema/test_check.py`
