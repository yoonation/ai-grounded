<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# toolchain

The L1 enforcement toolchain: the single source of tool definitions and the
capability selection that resolves a concern's mechanical gate to concrete
open-source tools.

## Files

- `registry.yaml` is the single source of tool definitions, one entry per tool
  (description, source url, ecosystems, gate-types, license, status, optional
  package-manager and suggested stage). Validated by
  `schemas/registry.schema.json`. Tools are referenced by id, never by name
  string. Open-source is required; a proprietary tool may exist only with
  `paid: true`, `no-oss-alternative: true`, and a `justification`.
- `selection.yaml` maps ecosystem to capability to a list of registry ids. It is
  the one place a tool is swapped for a capability. Lists carry AND semantics:
  every resolved tool must pass. Validated by `schemas/selection.schema.json`.

A capability-bound `binding.yaml` names a gate (capability); the resolver takes
the union over the project's active ecosystems of `selection[ecosystem][gate]`
plus `selection[any][gate]`, deduplicated, and the registry supplies each tool's
facts. A blocking gate that resolves to no live tool is an error, never a silent
pass.

## Manager and audit (`manage.py`)

Run with uv (PEP 723 inline deps).

- `audit` (also `make gc-toolchain-audit`): per tool, source liveness via
  `git ls-remote`, license open-source status, and supersession target existence,
  plus selection-to-registry integrity and ecosystem-by-capability coverage.
  Read-only. Use `--no-network` to skip liveness, `--strict` to exit nonzero on
  problems.
- `add`: verifies the source is live and the license is open-source (or requires
  the paid exception) before writing the entry. Rejects unknown gate-types, dead
  sources, and non-open-source licenses without the exception.
- `update`: changes fields on an existing tool and re-verifies source liveness.

Version currency (bumping pinned versions) is left to a dependency bot such as
Renovate; this tool owns fitness, liveness, and license, not version bumps.
`add` and `update` rewrite `registry.yaml` via the YAML emitter and do not
preserve the file's header comments.

## Status values

`candidate` (verified, override-only), `active` (default-eligible and the only
status a selection may reference), `deprecated`, `archived`, and
`superseded-by:<tool-id>`. The audit proposes transitions from upstream signals;
the author ratifies.

## Open-source rule and its two exceptions

Open-source is required for any tool a base selection references. A non-open-source
tool may exist in the registry only through one of two deliberate, recorded
exceptions, and the audit enforces both:

- Paid, no OSS alternative: `paid: true`, `no-oss-alternative: true`, and a
  `justification`. Use when no open-source tool covers the capability at all.
- Override-only, OSS alternative exists: `oss-alternative: <tool-id>`, a
  `justification`, and `status: candidate`. Use when an open-source default exists
  but a project deliberately chooses the non-open-source tool. Because the entry
  is candidate, it is never a base default; a project selects it only by an
  explicit selection override in its own profile or project-manifest.

Example of the second case: `terraform` (BUSL-1.1) is registered override-only
with `oss-alternative: opentofu`. The base selection keeps the open-source default
(`terraform.format: [opentofu]`). A project that standardizes on the Terraform CLI
overrides its own selection to `terraform.format: [terraform]`; the override-only
status keeps Terraform out of the substrate default while making it a vetted,
source-verified option.
