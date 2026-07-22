<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# plan-gate: the hard-fail keystone

The routing pipeline requires an approved `feature-concerns.yaml`, and that plan must
honor the dial's deterministic floor. This gate makes both real, and it is meant to
block: the checkpoint skill runs it and obeys its exit code. There is no fallback. A
missing or proposed plan, a plan that omits a floor catalog, or an inability to run
the dial are all hard stops.

## The two checks

Approval. An approved plan must exist (`feature-concerns.yaml`), be a mapping, carry
the schema's required fields (feature, profile, status, scope, routing), and have
`status: approved`.

Floor coverage. The gate re-runs the profile dial from the manifest context and
requires that the plan's selected-plus-locked catalogs cover the dial's deterministic
floor (`rigor_band.active_concerns`). The concern-selector is a reasoning agent told
to adopt the dial floor; this verifies it actually did, rather than trusting it.
Catalog names are compared by basename, since the dial emits bare names
(authentication) and the plan uses the concerns/ prefix (concerns/authentication).

## Exit codes

    0   approved plan present, well-formed, and covering the dial floor
    1   hard stop (absent/unapproved/malformed plan, uncovered floor, or dial failure)

## Run

    uv run --with pyyaml python3 tooling/plan-gate/check_plan.py specs/001-feature

Run from the repo root (the default --repo-root) so the gate finds
`project-manifest.yaml` and `tooling/dial`. The cores are pure stdlib; only the CLI
reads files and imports the dial resolver, so run it via uv for PyYAML.

## Tests

The directory name has a hyphen, so run the test file directly:

    python3 tooling/plan-gate/test_check_plan.py

The pure cores (approval, plan-catalog extraction, floor coverage) are unit-tested
here; the dial integration is exercised by the CLI smoke test in the COMMIT-GUIDE.

## Boundaries

It gates; it does not produce the plan (the concern-selector at Step 0), it does not
compute the floor (the dial), and it does not route (the dispatcher). It answers two
questions, loudly: is there an approved plan, and does it honor the deterministic
floor.
