<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Design pattern catalogs

This directory holds substrate-authored design-pattern catalogs:
named, reusable solutions to recurring design problems that an
engineer or AI agent consults while designing code, objects, and
systems.

## Why this is its own catalog kind

A design pattern is a third kind of knowledge, distinct from the two
the concern catalogs carry:

- An L2 semantic rule is a do-or-do-not check a reviewer applies to
  code that exists.
- An L3 decision framework structures a judgmental decision and yields
  an ADR.
- A design pattern is reference material: a named solution, when it
  applies, and what it costs, consulted while a design is being formed.

Neither a check nor a decision framework supplies a pattern library, so
design patterns live here as their own catalog kind. The `catalog-format.md`
spec recognizes `design-pattern` as a kind, and a concern rule may point at
a pattern through the `applies-pattern` link relation.

## Catalogs in this directory

- `solid.yaml`: the five SOLID object-oriented design principles.
- `gang-of-four.yaml`: the 23 Gang of Four patterns, grouped creational,
  structural, behavioral.
- `architecture.yaml`: architecture and distributed-systems patterns,
  grouped structure, resilience, integration, and data.
- `code-smells.yaml`: 22 code smells grouped bloaters, object-orientation
  abusers, change preventers, dispensables, and couplers. Smells are what a
  reviewer or agent detects; each entry names the refactorings that address
  it and cross-references the relevant SOLID principle or GoF pattern.

This is a focused first set, not the full design-pattern universe.
`spec/substrate-scope.md` projects further families at maturity (Clean
Code rules, Fowler refactoring smells, enterprise integration and cloud
patterns); they can be added as additional catalog files under this
directory without schema change.

## Format and lifecycle

Each catalog is a flat YAML file: a `metadata` block plus a `patterns`
collection. Every pattern carries at least an `id` and `name`; the
descriptive fields (`category`, `intent`, `when_to_use`, `consequences`,
`avoid_when`, and where relevant `applies_pattern_to`) are open by
design because pattern families describe themselves differently. The
shape is validated by `schemas/design-pattern-catalog.schema.json`, run
as part of `make gc-validate`.

Like the threat catalogs, these are review-cadence reference catalogs,
not rules on the draft/stable lifecycle. They are reviewed on the cadence
in each catalog's `metadata` and revised when the underlying body of
knowledge or the substrate's usage of it changes.

## Copyright discipline

The patterns named here are public design concepts; their names and
ideas are not copyrightable, but the original texts, code, and diagrams
that describe them are. Every description in these catalogs is
substrate-original paraphrase. No source text, sample code, or diagram
is reproduced. When adding patterns, describe the concept in your own
words and cite the body of knowledge in `metadata.upstream_source`,
never paste from a source.

## Cross-references

- `../README.md` (catalog kinds overview)
- `../../spec/catalog-format.md` (the `design-pattern` kind and the
  `applies-pattern` link relation)
- `../../spec/substrate-scope.md` (size estimate and projected families)
- `../../schemas/design-pattern-catalog.schema.json` (the validating schema)
- `../threats/` (the sibling reference-catalog kind this format mirrors)
