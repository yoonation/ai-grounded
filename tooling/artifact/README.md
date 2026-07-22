# artifact - real-artifact verification (Cap 2)

Tests commonly run against source while humans and CI run a built artifact (vitest
over `.ts`, but `node dist/cli.js` ships). Skip the build step and the shipped
artifact is stale: it does not reflect current source, yet every source test is
green. That gap shipped a real defect in the 003 run (a stale `dist/`). The build
artifact is gitignored, so there is nothing stale in the committed tree to catch at
commit time, the gap is a pre-ship one. This tool closes it by rebuilding from
current source and smoke-running the result.

It reads the `build:` section of `project-manifest.yaml`:

```yaml
build:
  command: "pnpm build"             # build the shipped artifact from source
  artifact: "dist/cli.js"           # what gets run / shipped (informational)
  smoke: "node dist/cli.js --help"  # trivial invocation that must exit 0
  test: "pnpm test"                 # optional, recorded for traceability
```

It runs `command` (build), then `smoke` (run the freshly built artifact). A failed
build skips the smoke. With no `build:` section it has nothing to verify and passes.
On-demand and advisory (exits 0), the same posture as the self-check and staleness
tools; `--strict` exits 1 on a failed step, for CI.

What it does not claim: it does not prove the tests exercise the built artifact
rather than source. Whether tests target `dist/` or source is a testing-strategy
choice (an ADR), not something a generic tool enforces. This verifies freshness and
runnability, which is the mechanism of the stale-artifact defect.

The build and smoke commands are operator-authored in the consumer's own manifest
(same trust boundary as the Makefile), so they run through the shell to allow normal
build syntax; they are never sourced from untrusted input. The template itself has
no build (bash/python/markdown), so the manifest ships a commented `build:` example
a consumer fills in; the tool reports "nothing to verify" until then.

```
uv run --with pyyaml python3 tooling/artifact/check.py --repo-root . --text
```

Tests (invoke directly): `python3 tooling/artifact/test_check.py`
