<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# floor-generator

Generates the lean runtime floor from the rich L1 layer. This is the bridge from
description (the substrate) to runtime (what a project executes), preserving
Charter Article VII: the substrate stays descriptive, the generated floor is the
runtime artifact.

## What it produces

For a given project stack (its active ecosystems), `generate.py` resolves every
mechanical rule's gate to concrete tools through selection (or a direct tool
reference) and emits:

- `.pre-commit-config.yaml`: local hooks for pre-commit-stage gates.
- `governance-ci.yml`: a GitHub Actions workflow for ci-stage gates, with
  deploy-time provenance gates (cosign, slsa-verifier) called out as a note since
  they run in the deploy pipeline, not on pull requests.
- `REVIEW-CHECKLIST.md`: the L2 review manifest, every semantic rule with its
  checklist path, grouped by concern, to wire into a pull-request template or
  review bot.

## Run

    uv run governance-commons/tooling/floor-generator/generate.py \
        --stack python typescript terraform alerting \
        --out OUTDIR

`make gc-generate-floor` regenerates the worked example under `example-output/`.

The stack is the set of active ecosystems. Rules whose gate resolves to no tool
for the chosen stack (for example iac-scan when terraform is absent) are reported
as not enforced for that stack, because the project has no artifacts of that kind.

## First cut is unpinned

Hooks invoke tools through the project runner (uv, npx, system) rather than
pinned upstream hook revisions, so the generated shape is visible without
committing to version management yet. The pinning pass will add pinned revisions
and lift the per-tool invocation table (currently the one piece of tool knowledge
held in the generator rather than the registry) into the registry entries.
