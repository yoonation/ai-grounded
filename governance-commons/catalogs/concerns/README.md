<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Concern Catalogs

This directory contains the substrate's opinionated rules about
engineering concerns: how production-grade software handles
authentication, authorization, error handling, logging, observability,
reliability, performance, testing, cost, privacy, responsible AI, and
related dimensions.

Concerns are the substrate's most heavily-tailored content. The
default profile selects extensively here; industry profiles tilt
these selections toward industry values; consumer profiles tilt
further toward organizational context.

All Tier 1 concerns are authored. Each concern is a directory of
per-rule folders (the package-by-rule storage model). The authored
form is assembled into OSCAL for consumption; see the storage model
design doc for the full rationale.

## What makes a concern

A concern is an engineering dimension that:

- **Cuts across features.** Authentication shows up in every
  authenticated endpoint; logging shows up in every operation worth
  recording; error handling shows up everywhere errors can occur. A
  concern is a pattern of code, not a single component.
- **Has known good and bad shapes.** There is industry consensus
  about what good authentication looks like (defense in depth,
  token expiration, no credentials in URLs). The consensus is not
  universal, but it is identifiable.
- **Benefits from substrate opinionation.** The substrate's value
  is encoding the known-good shapes as rules consumers can adopt
  or tailor. Concerns where the consensus is unclear (e.g., choice
  of database technology) are supported by Layer 3 decision content,
  not stated as mechanical rules.
- **Spans the three layers.** A real concern has Layer 1 rules
  (mechanically enforceable patterns), Layer 2 rules (semantic
  patterns requiring review), and Layer 3 rules (judgmental
  decisions requiring rationale). Concerns that fit only one layer
  are usually subsets of a broader concern.

Concerns that do not cut across features, lack consensus, or fit
only one layer are not appropriate for this directory.

## Storage model: one rule per folder

Each concern is a directory. Inside it, `concern.yaml` carries the
concern metadata (id, ISO/IEC 25010:2023 characteristic, status), and
every rule is its own folder named by a readable slug. A directory
listing reads like a table of contents.

```
catalogs/concerns/<concern>/
  concern.yaml
  <rule-slug>/
    rule.yaml            # id, name, layer, characteristic, severity, status, sources
    binding.yaml         # present when layer = mechanical
    checklist.md         # present when layer = semantic or judgmental
    test-template.md     # present when layer = semantic (where the source had one)
    decision.md          # present when layer = judgmental (the MADR)
    examples/
      good.md
      anti-pattern.md
```

The layer is a field inside `rule.yaml`, never part of a folder or
file name, so a rule can be reclassified by editing one field rather
than renaming anything. The mechanical bindings, review checklists,
decision records, and examples are co-located in the rule folder, not
scattered across sibling trees.

## Consumption: assembled OSCAL

The authored form is granular and readable. The assembler generates
the verbose OSCAL for tools, under `governance-commons/dist/`:

- `dist/concerns/<concern>.oscal.yaml`, one OSCAL catalog per concern
  (committed; profiles import these)
- `dist/index.yaml`, a flat id-to-path index for fast lookup
  (generated and git-ignored)

Never hand-edit `dist/`. Run `make gc-assemble` to regenerate it.

## Rule identifier convention

A rule's canonical id is its readable path: the concern, a dot, and
the rule slug.

```
<concern>.<rule-slug>
```

Examples:

- `authentication.password-hashing`
- `authentication.no-credentials-in-urls`
- `logging.structured-format`
- `observability.slo-policy`

The id mirrors the folder location, carries no layer, is grep-able,
and needs no sequence numbers to stay unique. It is stable under
layer reclassification. Stable ids are immutable per Charter Article
IV once a rule reaches stable status; renaming a slug is treated like
changing a URL path.

## Authoring discipline (summary)

Authoring a concern follows Charter Article II discipline:

- Three or more concrete examples per rule before stable promotion
- Layer assignment with rationale (why this is L1 vs L2 vs L3)
- Severity assignment with rationale
- Authoritative source citation or original rationale recorded
- Anti-pattern alongside the pattern where applicable
- Second-human review before stable promotion
- Real-codebase validation before stable promotion

The substrate does not enforce this discipline on consumer-side
custom catalogs but recommends consumers apply it.

## Cross-references

- `../README.md` (catalog kinds overview)
- `../../CHARTER.md` Article II (authoring discipline)
- `../../CHARTER.md` Article IV (identifier and intent immutability)
- the storage model design doc (package-by-rule rationale and layout)
- `../../tooling/assemble/` (validate and assemble scripts)
- `../../dist/concerns/` (assembled OSCAL catalogs)
- `../../profiles/production-grade-baseline.oscal.yaml` (the
  opinionated default profile that selects from concerns)
- `../../mappings/` (threat and standard mappings that reference rules)
