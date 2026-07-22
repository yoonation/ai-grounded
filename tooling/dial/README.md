<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# dial: the profile dial resolver

Resolves the operator-declared context facts to a profile cell and a rigor band.
The second Phase B module of the SPS rewire, built standalone and unit-tested
against synthetic facts before any wiring.

## What it is

The consumer-side categorize-and-tailor engine the substrate's
`tooling/tailoring-agent` skeleton deliberately leaves open (Charter Article VII:
the substrate is description, the running engine belongs in the consumer). It sits
upstream of the substrate `tooling/profile-resolver`: this picks the profile from
facts; the substrate flattens the chosen profile into effective controls and
severity. It is a tool, not a hook, and it never blocks.

## Inputs: the six context facts

Declared by the operator in the `context:` block of `project-manifest.yaml`,
validated by `.specify/schemas/project-manifest.schema.json`. Each fact is anchored
on a named scheme (see the Stage 0 decision log):

- data-sensitivity: personal-or-none, confidential, regulated (FIPS 199 confidentiality)
- network-exposure: none-local, internal, public-internet (threat-model trust boundary)
- criticality: low, moderate, high (FIPS 199 integrity and availability; blast-radius and reversibility)
- deployment-target: local-only, single-tenant-service, multi-tenant-production
- operator-count: solo, team, org
- agentic-surface: none, llm-assisted, autonomous (EU AI Act, NIST AI RMF, OWASP)

A missing or unknown fact defaults to its lowest level and is reported under
`defaulted_facts`, so an unfilled manifest resolves to the lean cell rather than
failing.

## Mechanics (fixed, in code, tested)

- Risk axis = high-water-mark over data-sensitivity, network-exposure, criticality.
- Process-weight axis = high-water-mark over deployment-target, operator-count.
- agentic-surface is an additive overlay, not an axis input: it switches on the
  agentic catalog and threat packs independent of where the axes sit, and at
  autonomous it layers the regulated-ai sector profile.
- Lean gating: when risk and process are both low, the cell gates down from the
  baseline (the lean-subset flag) with advisory andon.
- High-water-mark means one regulated-data fact raises the risk axis rather than
  being averaged away, matching how the substrate profile-resolver computes
  effective severity (sector tilts raise only).

## Output: the rigor band

For the resolved cell: active concern catalogs, active threat catalogs, severity
floor, andon sensitivity (advisory or blocking), review wave, whether an ADR is
required, the gating mode (lean-subset or full), and the substrate profile(s) to
resolve. No aggregate score; a unit test enforces this.

## The tunable surface

`dial-config.json` is data: the catalog, severity, and review-wave assignments per
axis level and per overlay. Adjust it without touching `resolve.py`. The catalog
names match `governance-commons/catalogs/concerns/` and `catalogs/threats/`, and
the profiles match `governance-commons/profiles/`, exactly. The resolution math is
fixed code; the assignments are the default starting point and are meant to be
reviewed.

## Run

    uv run --with pyyaml python3 tooling/dial/resolve.py project-manifest.yaml --text

The pure core takes a facts dict and needs no YAML; only the CLI reads the manifest
and so imports PyYAML lazily (run it via uv as above). Exit code is always 0.

## Tests

    python3 -m unittest tooling.dial.test_resolve

Synthetic facts only; no manifest and no PyYAML needed. Covers the lean cell, the
off-diagonal regulated-solo case (risk high, process low, the case the two-axis
design exists for), the heavy autonomous cell, the high-water-mark conflict rule,
the agentic overlays, and fact defaulting.
