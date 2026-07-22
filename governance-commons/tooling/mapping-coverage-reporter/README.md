<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# mapping-coverage-reporter

Reports the coverage a substrate cross-taxonomy mapping provides: which
source-taxonomy items are addressed by substrate concern rules, which
substrate concerns carry the load, and which source items are recorded as
coverage gaps.

This directory is a tooling skeleton: a documented contract, a procedure,
and a thin read-only reference script. It ships no runtime engine (Charter
Article VII).

## Why this exists

The substrate ships six cross-taxonomy mappings at `../../mappings/`:
STRIDE, OWASP Top 10, OWASP LLM Top 10, OWASP Agentic ASI, OWASP Agentic
Skills Top 10, and MITRE ATLAS, each mapping a source threat taxonomy to
substrate concern rules. A mapping is only honest if its coverage is legible: which source
items are addressed, by which target rules, and which are explicitly not
covered. This tool makes that legibility a repeatable report rather than a
manual read, so coverage regressions (a renamed target rule, a dropped
relation) are caught and the coverage-gap records stay honest.

## Inputs

- A mapping at `../../mappings/<taxonomy>-to-concerns.oscal.yaml`. Each
  carries a `relations` array of `{ source-rule, target-rule, relation-type,
  rationale }` entries and a set of explicit coverage-gap records.
- Optionally, the source threat catalog at `../../catalogs/threats/` and the
  target concern catalogs at `../../catalogs/concerns/`, to compute the
  source items that have no relation at all (uncovered) versus those
  recorded as an explicit gap.

## Outputs

A per-mapping report: count of relations, distinct source items addressed,
distinct target concerns carrying relations, and the coverage-gap entries.
Cross-checking against the source catalog yields the set of source items
with neither a relation nor a recorded gap (the silent-gap set, which should
be empty in an honest mapping). The output names no consumer architecture.

## Procedure

1. Parse the mapping's `relations` array; collect distinct `source-rule`
   values (items addressed) and distinct target concern prefixes (the
   concern portion of `target-rule`, for example `input-validation`).
2. Collect the explicit coverage-gap records.
3. If the source catalog is supplied, diff its full item set against the
   addressed and gap-recorded sets to find silent gaps.
4. Emit the report per mapping and, optionally, aggregate across all six.

The reference script `report-mapping-coverage.sh` performs steps 1 and 2 for
a single mapping (read-only). Step 3's source-catalog diff is documented as
the contract; it depends on the source catalog being parseable (the legacy
ASI threat catalog is known-malformed YAML, tolerated because nothing
validates threat catalogs) and is left as the extension point.

## Status

Skeleton. `report-mapping-coverage.sh` is a thin read-only reference
implementation of steps 1 and 2 (illustrative, not a maintained substrate
runtime).

## Cross-references

- `../../mappings/` (the mappings this tool reports on)
- `../../schemas/mapping.schema.json` (the mapping contract)
- `../../catalogs/threats/` and `../../catalogs/concerns/` (source and target)
- `../../CHARTER.md` Article VII (consumer-agnostic tooling)
