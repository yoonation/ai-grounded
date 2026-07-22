<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Profiles

This directory contains the substrate's tailoring profiles. A profile
selects rules from catalogs, sets profile-specific severity, applies
parameters, and binds enforcement tools. Profiles are the mechanism
by which the substrate's opinionated content gets tailored to specific
organizations, industries, and use cases.

This directory is currently empty (the structure exists; the default
profile lands in the next commit). The first profile authored is
`production-grade-baseline.oscal.yaml`.

## What a profile is

A profile is an OSCAL document that:

- **Inherits from a parent profile** (except the root default profile,
  which inherits from nothing)
- **Selects** which rules from substrate catalogs are active in this
  profile's scope
- **Modifies** the selected rules' tailorable properties (severity,
  applicability, parameters, enforcement bindings) per Charter
  Article IV Section 4.3
- **Records rationale** for any modifications that weaken defaults
  per Charter Article V Section 5.5

Profiles do not modify catalog content. They reference catalog content
by identifier and apply tailoring on top.

## The substrate-shipped profile hierarchy

The substrate ships an opinionated hierarchy. Consumers adopt the
closest fit and tailor from there.

```
production-grade-baseline.oscal.yaml          (the opinionated default)
│
├── financial-services.oscal.yaml             (security tilt)
├── healthcare.oscal.yaml                     (privacy tilt)
├── regulated-ai.oscal.yaml                   (AI RMF tilt)
└── greenfield-startup.oscal.yaml             (speed tilt within reason)
```

Consumers may author their own profiles that inherit from any of the
above. Consumer-side profiles live in the consumer's repository, not
in this directory.

## Choosing a starting profile

For consumers selecting a profile to inherit from:

- **No clear industry fit**: inherit from `production-grade-baseline`
- **Financial services, banking, fintech, payments**: inherit from
  `financial-services`
- **Healthcare, health-tech, clinical, regulated PHI**: inherit from
  `healthcare`
- **AI-first products under EU AI Act, NIST AI RMF, or similar
  regimes**: inherit from `regulated-ai`
- **Early-stage product still establishing engineering maturity**:
  inherit from `greenfield-startup`, then graduate to a more
  rigorous profile as the product matures

Profile inheritance is single by default. Multiple inheritance is
supported by OSCAL but requires careful merge handling; consult
`../spec/extension-contract.md` Section "Selecting a parent profile"
before using.

## Profile structure

Each profile is a single OSCAL profile YAML file. The file's top-level
structure follows the OSCAL profile model. Substrate-shipped profiles
include:

- Profile metadata (identifier, version, lifecycle status, provenance)
- Parent profile reference (the profile this inherits from)
- Profile-level documentation (intended audience, tilt, scope)
- Import entries per parent catalog or parent profile
- Modify entries per tailorable property changed
- Rationale entries for any weakening per Charter Article V Section
  5.5

## Profile identifier convention

Profile identifiers follow:

```
<profile-name>
```

The name is a short, descriptive slug. Substrate-shipped profiles use
unprefixed names. Consumer-side profiles namespace per the consumer's
convention (see `../spec/extension-contract.md`).

The version is independent from the commons version per Charter
Article VIII Section 8.4. A profile may evolve through its own
versions while the commons remains at a stable version, and vice
versa.

## Profile resolution

When a consumer's workflow consults catalogs through a profile, the
profile resolver in `../tooling/profile-resolver/` produces a flat
effective profile. The flat profile contains:

- The union of all selected rules across the inheritance chain
- Modifications applied per inheritance order (later overrides
  earlier)
- Resolution decisions recorded for audit visibility

The flat profile is what AI agents and runtime enforcers actually
consult during workflow execution. The hierarchical source profiles
are what humans author and maintain.

## Weakening vs strengthening

Per Charter Article V Sections 5.5 and 5.6:

Weakening defaults requires rationale:

- Lowering severity (P1 to P2, P2 to P3)
- Narrowing applicability (rule applies to fewer features/languages/
  environments)
- Excluding a rule the parent profile includes
- Relaxing parameters (longer timeout, larger threshold, looser
  validation)
- Replacing enforcement binding with a less strict tool

Strengthening defaults requires no rationale:

- Adding rules the parent does not include
- Raising severity
- Broadening applicability
- Tightening parameters
- Replacing enforcement binding with a stricter tool

The rationale, when required, is recorded in the profile artifact
itself. Substrate-shipped profiles set the example for how rationale
is written; consumer-side profiles follow the same convention.

## Lifecycle of profiles

Profiles follow the same lifecycle as catalog content per
`../spec/rule-lifecycle.md`. A profile may be in draft, stable,
deprecated, or retired status. Substrate-shipped profiles enter
draft status when first authored and promote to stable after
real-consumer validation.

Profile deprecation provides consumers a window to migrate to a
superseding profile. The deprecation window per Charter Article
VIII Section 8.3 applies to profiles as it applies to catalog
content.

## Cross-references

- `../CHARTER.md` Article V (profiles and tailoring)
- `../spec/extension-contract.md` (operational procedures for
  profile authoring)
- `../spec/rule-lifecycle.md` (profile lifecycle)
- `../schemas/profile.schema.json` (mechanical validation)
- `../catalogs/concerns/` (the primary source of selectable rules)
- `../tooling/profile-resolver/` (utility that resolves profile
  inheritance to flat form)
