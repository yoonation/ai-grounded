<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Catalogs

This directory contains all rule collections in the substrate. A
catalog is a structured, identifier-stable, lifecycle-tracked set of
rules that consumers consult through profile selection during their
workflow.

All catalogs share the same format (see `../spec/catalog-format.md`),
the same lifecycle (see `../spec/rule-lifecycle.md`), and the same
identity discipline (see Charter Article IV). They differ in subject
matter, not in mechanics.

## Reading order

If you are new to the substrate:

1. Read `../CHARTER.md` to understand the substrate's authority and
   the rules that bind catalog content
2. Read `../spec/catalog-format.md` to understand how a catalog is
   structured
3. Read `../spec/rule-lifecycle.md` to understand draft/stable/
   deprecated/retired states
4. Browse the four catalog kinds below to see real examples

## The four catalog kinds

The substrate organizes catalogs by what they encode. The kinds are
not mutually exclusive in subject matter; a rule about authentication
may appear in `concerns/authentication/` while related
threat vectors appear in `threats/owasp-llm-top10.yaml` and related
compliance controls appear in `compliance/`. The relationships across
catalogs are encoded in `../mappings/`.

### concerns/

The differentiating tier. Engineering concerns the substrate
opinionates about: authentication, authorization, error handling,
logging, observability, reliability, performance, testing, cost,
privacy, responsible AI. Each concern is a directory of per-rule
folders (`rule.yaml` plus co-located `examples/`, `decision.md`, and
`binding.yaml` as the rule's layer requires), with rules at three
layers (mechanical, semantic, judgmental). The assemble tool builds
each concern into a single OSCAL catalog under `dist/`.

This is the tier most consumers tailor most heavily. The default
profile (`../profiles/production-grade-baseline.oscal.yaml`) selects
extensively from concerns. Industry profiles tilt the concerns
selection toward industry-specific values.

### threats/

Threat-model rule sources. OWASP LLM Top 10, OWASP Agentic ASI,
MITRE ATLAS, STRIDE. These catalogs encode known adversarial patterns
that consumers should defend against.

Threat catalogs currently use a hand-authored YAML format (predates
the substrate's OSCAL adoption). They will migrate to OSCAL format
over time per the lifecycle rules; the migration is non-breaking
because rule identifiers and intent statements remain stable.

Consumers reference threat catalogs primarily during threat-modeling
checkpoints in their workflow.

### compliance/

Compliance regime catalogs in full OSCAL format, managed via Trestle
(see `compliance/trestle-workspace/`). Currently includes NIST 800-53
Rev 5, NIST CSF v2, NIST 800-171 Rev 3, NIST 800-218 SSDF, NIST AI
RMF, EU AI Act, and substrate-authored profiles (ai-security-baseline,
federal-bridge).

Compliance catalogs are authoritative reproductions of external
standards. The substrate does not modify them; it republishes them
in OSCAL format and adds mappings to substrate concerns via
`../mappings/`.

Consumers reference compliance catalogs primarily for audit and
regulatory reporting workflows. Compliance content tends to be
referenced indirectly (via concern rules that satisfy compliance
controls) rather than directly.

### design-patterns/

Design patterns are an authored catalog kind. The substrate houses
substrate-original paraphrase of publicly-recognized design knowledge
(SOLID, Gang of Four, architecture and system-design patterns) as
reference material an engineer or AI agent consults while designing. A
concern rule may point at a pattern through the `applies-pattern` link
relation. See `design-patterns/README.md` for the catalogs, the format,
and the copyright discipline. Like the threat catalogs, these are
review-cadence reference catalogs rather than rules on the draft/stable
lifecycle.

## Catalog identifier conventions

Catalog identifiers follow the pattern:

```
<kind>/<catalog-name>
```

Examples:

- `concerns/authentication`
- `threats/owasp-llm-top10`
- `compliance/nist-800-53-rev5`

Rule identifiers for substrate-authored catalogs (concerns) follow:

```
<catalog>.<rule-slug>
```

Examples:

- `authentication.no-hardcoded-credentials`
- `logging.architecture`
- `agentic-systems.tool-use-authorization`

The rule's layer lives in `rule.yaml`, not in the identifier. An
earlier substrate convention numbered rules by layer
(`AUTH-L1-001`); those identifiers were retired together with the
registry-id binding model in the capability-gate toolchain refactor,
and the support prose that referenced them was migrated to current
slugs in the 2026-07-03 sweep (see `../CHANGELOG.md`). The retired
numbers now appear only in historical records, plus this one
illustrative mention. Catalogs
derived from external authoritative sources preserve source naming:

- `LLM01` (OWASP LLM Top 10, item 1)
- `AC-3` (NIST 800-53, access control, item 3)

## Layer model

The substrate's three-layer model applies across all catalog kinds:

- **Layer 1 (mechanical)**: rules enforceable by static analysis,
  pattern matching, or other deterministic tooling. Bound to
  enforcement tools via the capability gate in each rule's co-located
  `binding.yaml`, resolved through `../toolchain/`.
- **Layer 2 (semantic)**: rules requiring human or AI judgment about
  meaning, context, or pattern application. Supported by examples
  co-located in each rule folder.
- **Layer 3 (judgmental)**: rules requiring genuine architectural
  judgment with explicit trade-offs. Supported by decision
  frameworks co-located in each rule folder (`decision.md`).

Each rule in a catalog declares its layer. The layer determines how
the rule is consulted, how findings are produced, and how closure
is verified.

## Lifecycle discipline

Every catalog file and every rule within it carries a lifecycle
metadata block per `../spec/rule-lifecycle.md`. The substrate's
authoring discipline (Charter Article II) applies to all catalog
content regardless of kind.

Draft rules may exist within otherwise-stable catalogs (a single
catalog can hold rules at mixed lifecycle states). The default
profile (`../profiles/production-grade-baseline.oscal.yaml`) selects
only stable rules.

## Cross-references

- `../CHARTER.md` Article IV (catalog identity and immutability)
- `../spec/catalog-format.md` (format specification for all catalogs)
- `../spec/rule-lifecycle.md` (lifecycle for catalog content)
- `../mappings/` (cross-catalog and cross-taxonomy relations)
- `../profiles/` (selection from catalogs)
- `../toolchain/` (registry and selection that bind Layer 1 rules to tools)
- each rule's co-located `examples/` (support for Layer 2 rules)
- each rule's co-located `decision.md` (support for Layer 3 rules)
- `../schemas/` (source-layer mechanical validation: concern.schema.json, rule.schema.json, binding.schema.json via `../tooling/assemble/validate.py`)
