<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Mappings

This directory contains cross-taxonomy relations between rules in
different catalogs. Mappings answer questions like:

- Which substrate concern rules satisfy SOC 2 control CC6.1?
- Which OWASP LLM Top 10 items are addressed by the authentication
  concern catalog?
- Which NIST AI RMF subcategories does the responsible-ai concern
  catalog cover?
- Which MITRE ATLAS techniques map to threat-modeling rules in our
  threats catalog?

Mappings are how compliance evidence, gap analysis, and cross-regime
audit get produced. They convert "here are some rules" into "here is
how this body of rules addresses that other body of requirements."

This directory contains the five threat-to-concern mappings listed
below; the three compliance mappings (SOC 2, NIST AI RMF, NIST 800-53)
remain planned and land alongside the substrate-authored content they
connect.

## What a mapping is

A mapping is an OSCAL-format file that records set-theoretic
relations between rule sets in different catalogs. Each mapping
entry asserts one of:

- **requires**: control A in taxonomy X requires implementation of
  rule B in taxonomy Y
- **addressed-by**: requirement A in taxonomy X is addressed by rule
  B in taxonomy Y (similar to requires but weaker; addressed-by
  means partial or indirect satisfaction)
- **satisfies**: rule A in taxonomy X provides evidence for
  satisfying control B in taxonomy Y
- **related-to**: rule A in taxonomy X is related to rule B in
  taxonomy Y without specific requires/addresses semantics
- **contradicts**: rule A in taxonomy X contradicts rule B in
  taxonomy Y (rare but worth recording when it occurs, e.g.,
  when compliance regimes conflict)

Each mapping entry includes the source rule identifier, the target
rule identifier, the relation type, and rationale explaining why
the relation holds.

## Mapping kinds

The five threat-to-concern mappings are authored; the three compliance
mappings are planned and land as the compliance side is built.

| Mapping | File | Status | Description |
|---|---|---|---|
| STRIDE to concerns | `stride-to-concerns.oscal.yaml` | authored | STRIDE threat categories to substrate concern rules |
| OWASP LLM to concerns | `owasp-llm-to-concerns.oscal.yaml` | authored | OWASP LLM Top 10 to substrate concern rules |
| OWASP ASI to concerns | `owasp-asi-to-concerns.oscal.yaml` | authored | OWASP Agentic ASI to substrate concern rules |
| OWASP AST to concerns | `owasp-ast-to-concerns.oscal.yaml` | authored | OWASP Agentic Skills Top 10 to substrate concern rules |
| MITRE ATLAS to concerns | `mitre-atlas-to-concerns.oscal.yaml` | authored | MITRE ATLAS techniques to substrate concern rules |
| SOC 2 to concerns | `soc2-to-concerns.oscal.yaml` | planned | SOC 2 Trust Service Criteria to substrate concern rules |
| NIST AI RMF to concerns | `nist-ai-rmf-to-concerns.oscal.yaml` | planned | NIST AI RMF subcategories to substrate concern rules |
| NIST 800-53 to concerns | `nist-800-53-to-concerns.oscal.yaml` | planned | NIST 800-53 controls to substrate concern rules |

Mappings are typically authored after both source and target catalogs
exist. A mapping that references nonexistent rules is invalid.

## Mapping authoring discipline

Mappings follow Charter Article II authoring discipline like catalog
content. Specifically:

- Every relation entry includes rationale (why this rule maps to
  that rule, what dimension of the requirement is covered)
- Authoritative source for the requirement side is cited (the
  compliance regime's published text, the threat taxonomy's
  documentation)
- The substrate's interpretation is recorded where it differs from
  surface reading
- Coverage gaps are explicit (when a requirement has no substrate
  rule that addresses it, the gap is recorded so consumers know
  not to rely on substrate alone for that requirement)

## What mappings are not

To clarify boundaries:

- Mappings are **not certifications**. A mapping from substrate
  concern rules to SOC 2 controls does not mean adopting those
  concerns produces SOC 2 compliance. Compliance certification
  requires audit by qualified auditors against organization-
  specific implementations.
- Mappings are **not contracts with regulatory bodies**. The
  substrate's interpretation of how concerns address compliance
  controls is the substrate's interpretation. Consumers and their
  auditors form their own interpretations based on their specific
  contexts.
- Mappings are **not exhaustive**. A mapping that records "rule X
  addresses requirement Y" does not claim X is the only rule that
  addresses Y. Multiple substrate rules may address a single
  requirement; multiple requirements may be addressed by a single
  rule.

## How consumers use mappings

Common consumer workflows that depend on mappings:

- **Compliance evidence reports**: which substrate rules and which
  consumer-side findings provide evidence for compliance audit
- **Gap analysis**: given a target compliance regime, which
  requirements lack substrate rule coverage
- **Multi-regime reconciliation**: when a consumer is subject to
  multiple compliance regimes, mappings reveal where the regimes
  reinforce each other and where they conflict
- **Threat-to-control traceability**: connecting threat-model
  findings (from threats catalogs) to mitigating controls (in
  concerns and compliance catalogs)

## Identifier convention

Mapping identifiers follow:

```
<source-catalog>-to-<target-catalog>
```

Examples:

- `soc2-to-concerns`
- `owasp-llm-to-concerns`

The convention is source-first because mappings are typically
queried "given requirement X (in source), what rules address it (in
target)." Reverse queries are supported but read more naturally in
the source-to-target direction.

Each entry within a mapping file has its own identifier following:

```
<source-rule-id>-<relation>-<target-rule-id>
```

This compound identifier is rarely used externally but supports
mechanical referencing of specific mapping entries when needed.

## Mapping lifecycle

Mappings follow the same lifecycle as catalog content per
`../spec/rule-lifecycle.md`. A mapping that becomes stale (because
the source catalog updates or the target catalog updates) requires
review and update. Substrate authoring discipline includes mapping
maintenance when underlying catalogs change.

## Cross-references

- `../CHARTER.md` Article II (authoring discipline for mappings)
- `../catalogs/` (source and target catalogs that mappings connect)
- `../spec/oscal-model.md` (OSCAL mapping model used here)
- `../spec/rule-lifecycle.md` (mapping lifecycle)
- `../schemas/mapping.schema.json` (mechanical validation)
- `../tooling/mapping-coverage-reporter/` (utility for gap analysis)
