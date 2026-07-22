<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Schemas

This directory contains JSON Schema files that mechanically validate
substrate content and consumer integrations against substrate
contracts. Schemas are how the substrate enforces format discipline
without relying on convention alone.

This directory is currently empty (the structure exists; schemas
land in the next commit alongside the format specifications they
validate).

## What schemas validate

Every substrate data format has a JSON Schema. Catalogs validate
against catalog schemas. Profiles validate against profile schemas.
Mappings validate against mapping schemas. Manifests validate
against manifest schemas. Decision frameworks validate against
decision framework schemas. Consultation events optionally validate
against the consultation event schema.

The substrate's tooling (in `../tooling/`) uses these schemas to:

- Validate substrate content before commit
- Validate consumer-side artifacts that follow substrate format
- Generate substrate content templates with correct structure
- Drive editor tooling (autocomplete, inline validation) for content
  authors

Consumers may use these schemas independently of substrate tooling.
Schemas are JSON Schema draft 2020-12 compliant and consumable by
any standard JSON Schema validator.

## Schema files

| Schema | File | Validates |
|---|---|---|
| Concern (source) | `concern.schema.json` | `concern.yaml` in each `../catalogs/concerns/<concern>/` |
| Rule (source) | `rule.schema.json` | `rule.yaml` in each rule folder |
| Binding | `binding.schema.json` | `binding.yaml` capability gates on mechanical rules |
| Profile | `profile.schema.json` | Files in `../profiles/` |
| Mapping | `mapping.schema.json` | Files in `../mappings/` |
| Threat catalog | `threat-catalog.schema.json` | Files in `../catalogs/threats/` |
| Design-pattern catalog | `design-pattern-catalog.schema.json` | Files in `../catalogs/design-patterns/` |
| Toolchain registry | `registry.schema.json` | `../toolchain/registry.yaml` |
| Toolchain selection | `selection.schema.json` | `../toolchain/selection.yaml` |
| Manifest | `manifest.schema.json` | Consumer manifest files (consumer-side) |
| Consultation event | `consultation-event.schema.json` | Optional validation for consumer audit events |

The assembled `../dist/` catalogs are generated output of
`../tooling/assemble/` and are validated at the source layer (the
concern, rule, and binding schemas above); the schema that validated
the retired single-file concern-catalog format was retired 2026-07-03
(see `../CHANGELOG.md`).

## What schemas do not validate

Schemas validate structure, not meaning. A catalog that conforms to
its schema may still have content defects:

- Rules with sloppy intent statements
- Severity assignments without rationale
- Missing examples
- Layer assignments inappropriate for the rule
- Contradictions with other catalog content

These defects require human review per Charter Article II Section
2.4 review discipline. Schemas catch the mechanical errors; review
catches the semantic errors.

## Schema authoring discipline

Schemas follow Charter Article II discipline as substrate content:

- Provenance recorded in schema metadata
- Authoritative sources cited where the schema derives from
  external standards (OSCAL, MADR, etc.)
- Changes follow lifecycle procedures per
  `../spec/rule-lifecycle.md`

Schema changes are particularly sensitive to versioning:

- Adding optional fields is non-breaking (minor version)
- Adding required fields is breaking (major version)
- Removing fields is breaking (major version)
- Tightening constraints (e.g., narrowing an enum, requiring
  previously-optional fields) is breaking
- Loosening constraints (e.g., broadening an enum, making
  previously-required fields optional) is non-breaking

Consumers integrating against substrate schemas should pin to the
substrate version they validated against to avoid surprise breakage
when schemas evolve.

## Schema identifier convention

Schema files use the convention:

```
<artifact-type>.schema.json
```

Schema document identifiers (the `$id` field) follow:

```
https://governance-commons/schemas/<artifact-type>.schema.json
```

The URL form is a stable identifier even when the substrate isn't
hosted at that exact URL. Consumers reference schemas by this
identifier; substrate tooling resolves the identifier to local
files for validation.

## Schema lifecycle

Schemas follow the same lifecycle as catalog content per
`../spec/rule-lifecycle.md`. The substrate's commitment per Charter
Article VII Section 7.1: every data format produced by the substrate
has a published schema. Schema deprecation gives consumers a window
to migrate.

## OSCAL relationship

Several substrate schemas extend OSCAL's published JSON Schemas
rather than starting from scratch. OSCAL provides schemas for
catalog, profile, and component-definition models; the substrate's
profile schema imports OSCAL's base structure and adds
substrate-specific extension properties.

See `../spec/oscal-model.md` for the substrate's relationship to
OSCAL and `../spec/catalog-format.md` for the specific extension
properties.

## Cross-references

- `../CHARTER.md` Article VII (schema commitment to consumers)
- `../spec/catalog-format.md` (structurally validated at the source
  layer by concern.schema.json, rule.schema.json, and
  binding.schema.json)
- `../spec/manifest-format.md` (specification validated by
  manifest.schema.json)
- `../spec/decision-framework-format.md` (L3 decision framework
  format; free-form, not schema-validated)
- `../spec/consultation-evidence.md` (semantic contract;
  consultation-event.schema.json is the optional structural
  validation)
- `../tooling/assemble/` (substrate utility that validates content
  against these schemas)
