<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Repo scripts

Substrate-maintainer tooling: repo-level scripts that assist with
substrate development workflow.

These scripts are NOT part of the portable substrate (the substrate
itself lives at `governance-commons/`). They are repo-level tooling for
the substrate's maintainer. Consumers receiving the substrate do not
need them.

## Substrate content validation

Substrate content is validated by a single authoritative validator:

```
make gc-validate
```

It validates concerns, rules, bindings, the toolchain registry and
selection, profiles, threat catalogs, and mappings against their
schemas (`governance-commons/tooling/assemble/validate.py`). The former
per-artifact shell validators (`validate-all.sh`, `validate-catalogs.sh`,
`validate-profiles.sh`, `validate-threats.sh`) were retired in favour of
this one entry point; their coverage now lives in `validate.py`, which
additionally validates mappings (a gap the shell validators never
covered).

## Other scripts

### `bootstrap.sh`

Spec-kit project infrastructure. Pre-existing.

## Adding new scripts

New substrate-maintainer scripts go in this directory. Follow the
established conventions:

- SPDX header at the top
- Usage docstring covering invocation forms, arguments, environment
  variables, exit codes, and dependencies
- `set -u` for unset-variable safety
- Auto-detect repo root via `git rev-parse --show-toplevel` with a
  `REPO_ROOT` environment variable override

Substrate content validation belongs in
`governance-commons/tooling/assemble/validate.py` (run via
`make gc-validate`), not in a new shell script.
