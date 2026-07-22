<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# profile-resolver

Resolves a substrate profile, including profile-of-a-profile inheritance,
into a flat effective profile: the full set of selected control identifiers
with their effective severity after all imports and tailoring are applied.

This directory is a tooling skeleton: a documented contract, a procedure,
and a thin read-only reference script. It ships no runtime engine (Charter
Article VII).

## Why this exists

As of M7 the substrate ships five profiles: `production-grade-baseline` and
four industry-tilt profiles (financial-services, regulated-ai, healthcare,
fedramp). Each industry profile is a profile-of-a-profile: it imports
`production-grade-baseline` via a single `include-all` and then raises
severities for its regime through a `modify` block of `alters`, each adding
a `profile-severity-override`. The substrate's profile validation (run by
`make gc-validate`) is a per-file JSON-schema check and deliberately does not
resolve cross-file import hrefs. A consumer adopting an industry profile needs the resolved,
effective answer: for every control, which severity applies after the tilt.
This tool computes that flattening from the substrate's own profile and
catalog content.

## Inputs

- A target profile at `../../profiles/<profile>.oscal.yaml`.
- Its import chain: a profile-of-a-profile names a parent profile in its
  `imports[].href`; the parent in turn imports the concern catalogs at
  `../../catalogs/concerns/`. The resolver follows the chain.

## Outputs

A flat effective profile: one row per selected control identifier with the
effective severity, plus provenance (which profile in the chain set the
effective value). The output is consumer-agnostic and names no consumer
architecture.

## Resolution semantics

1. Start from the target profile. If it imports a parent profile
   (profile-of-a-profile), resolve the parent first, recursively, down to the
   profile that imports concern catalogs directly.
2. The base selection and base severities come from the catalog-importing
   profile's `include-controls` and `modify.alters[].profile-severity-override`.
3. Each more-derived profile applies its `modify.alters` over the resolved
   set; a child `profile-severity-override` on a control wins over the
   parent's (last-write-wins down the chain). `exclude-controls` removes a
   control; `include-controls` or `include-all` widen selection.
4. The effective severity for a control is the value set by the
   most-derived profile that alters it; provenance records which profile that
   was. Severity ordering is low, medium, high, critical.

Because industry tilts only ever raise severity (never lower), the effective
severity of a control under an industry profile is the maximum of the
baseline severity and any tilt override; the resolver reports both the
effective value and whether the industry profile elevated it.

## Procedure

The reference script `list-profile-overrides.sh` performs the read-only core
of step 3 for a single profile: it lists every `control-id` the profile
alters together with the `profile-severity-override` the profile sets. Full
chain resolution (following the parent import and merging the baseline) is
documented here as the contract; a full resolver is the natural extension
point and is intentionally left out of the skeleton to avoid shipping a
maintained engine.

## Status

Skeleton. `list-profile-overrides.sh` is a thin read-only reference
implementation (illustrative, not a maintained substrate runtime) that
surfaces a single profile's overrides; whole-chain flattening is documented
as the contract above.

## Cross-references

- `../../profiles/` (the profiles this tool resolves)
- `../../schemas/profile.schema.json` (the profile and import contract)
- `../../CHARTER.md` Article V (profiles and tailoring), Article VII
  (consumer-agnostic tooling)
