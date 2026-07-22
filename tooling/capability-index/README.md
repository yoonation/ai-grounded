<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# capability-index: the what-already-exists generator

Builds a machine map of a codebase's capabilities, the declared dependencies and
the exported symbols, so a later reuse claim can be checked against an independent
artifact rather than taken on faith. The third Phase B module of the SPS rewire,
built standalone and unit-tested before any wiring.

## What it is, and why

It is a tool, not a hook; you run it on demand and read or store the index. It
never blocks. Its purpose is to refute a faked "I checked, nothing like this
exists": the discovery agent and the duplication gate read this index instead of
trusting an agent's self-report, which is the same never-trust-self-attestation
discipline the consultation audit applies to catalog reads.

## What it produces

A JSON index with three parts:

- dependencies: declared packages, grouped by ecosystem (npm, python, go, rust,
  mise-tools).
- exports: per source file, the exported symbol names, the language, and the
  extraction method.
- summary: counts, the list of toml files skipped when tomllib was unavailable, and
  a note on method precision.

## Honesty about method

Each export entry carries how it was extracted, because the methods differ in
precision:

- Python: the stdlib ast module. Precise. Top-level functions and classes, and
  __all__ is authoritative when present. Private names (leading underscore) are
  excluded unless named in __all__.
- JavaScript and TypeScript: a regex heuristic, method "regex-heuristic". A surface
  scan of export declarations, brace exports (including `as` aliases), and
  `exports.name` assignments. It surfaces named exports well enough to refute a
  faked reuse claim; it is not a parser and does not guarantee completeness. The
  label tells the reader not to treat it as exhaustive.

Dependencies are parsed from the files found in the tree: package.json (json),
requirements.txt and go.mod (line parse), and pyproject.toml, Cargo.toml, and
.mise.toml (tomllib, Python 3.11+). When tomllib is absent the toml files are
skipped and listed under summary.skipped_toml_no_tomllib, so the tool still runs on
3.9 and 3.10 (it just omits toml-declared dependencies).

Noise directories are skipped: .git, node_modules, __pycache__, virtualenvs, build
and dist trees, vendor, target, and governance-commons (the substrate is not the
consumer's own capability surface).

## Run

    python3 tooling/capability-index/generate.py . --out .capability-index.json
    python3 tooling/capability-index/generate.py path/to/project

With --out it writes the index file and prints a one-line summary; without, it
prints the index JSON to stdout. Python 3.9+ stdlib only; tomllib used if present.
Exit code is always 0.

## Tests

The directory name has a hyphen, so run the test file directly rather than as a
dotted module:

    python3 tooling/capability-index/test_generate.py

The tests build trees inline in temp directories (including a node_modules tree
that must be skipped), plus a smoke test against fixtures/sample-project.

## Boundaries

This generates the index; it does not decide what is a duplicate (that is the
duplication gate) and it does not survey for reuse (that is the discovery agent).
It is the artifact those read. Language coverage is Python (precise) and JS/TS
(heuristic) for exports, with dependency parsing across the common ecosystems;
adding a language is adding an extractor, not rewriting the tool.
