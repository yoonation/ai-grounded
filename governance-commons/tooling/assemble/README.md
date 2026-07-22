# Assemble and validate

Two deterministic scripts (no AI in the loop) that turn the authored granular
form of the substrate into consumption artifacts and check its invariants.

## What they do

- `validate.py` checks the authored form before assembly:
  - every `concern.yaml` and `rule.yaml` validates against its JSON schema
  - the rule folder name matches the slug half of the rule id
  - each rule id is single-home (never authored in two folders)
  - the required artifact is present per layer (mechanical needs `binding.yaml`,
    semantic needs `checklist.md`, judgmental needs `decision.md`)
- `assemble.py` generates, under `governance-commons/dist/`:
  - `concerns/<concern>.oscal.yaml`, one OSCAL catalog per concern
  - `index.yaml`, a flat id-to-path index for fast lookup

`dist/` is generated and git-ignored. Never hand-edit it.

## Authoring mode

`governance-commons/authoring-mode.yaml` sets the posture:

- `solo` (current): problems are warnings, the validator exits 0. Edit freely.
- `published`: problems are errors, the validator exits 1. Full lifecycle
  discipline for when other people depend on the substrate.

## Triggers

- Manual: `make gc-validate` then `make gc-assemble` (or run the scripts directly).
- Pre-commit: run `gc-validate`; in published mode it blocks a bad commit.
- CI: run validate then assemble; fail the build on any error.

## Run

```
make gc-validate
make gc-assemble
# or directly:
uv run governance-commons/tooling/assemble/validate.py
uv run governance-commons/tooling/assemble/assemble.py
```

The scripts carry PEP 723 inline dependencies, so `uv run` installs `pyyaml`
and `jsonschema` automatically with no global pollution.
