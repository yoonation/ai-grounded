<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Catalog Format

This document specifies the format used for substrate catalogs. The
format is OSCAL-based with substrate-specific extension properties
that encode the substrate's three-layer model, layer-specific
references, and provenance discipline.

The format is referenced by Charter Article IV (catalog identity and
immutability), Charter Article II (authoring discipline), and the
catalog-related READMEs in `../catalogs/`. Mechanical validation
lives at the source layer: `../schemas/concern.schema.json`,
`../schemas/rule.schema.json`, and `../schemas/binding.schema.json`,
run by `../tooling/assemble/validate.py`; the assembled `../dist/`
catalogs are generated output.

## Why OSCAL with extensions

OSCAL is the National Institute of Standards and Technology's
machine-readable representation for control catalogs, profiles,
component definitions, and assessment artifacts. The substrate
adopts OSCAL because:

- It is a published standard with active maintenance
- It is consumed by audit and compliance tooling consumers may
  already use
- It supports profile selection and tailoring natively
- It is JSON/YAML/XML serializable
- It is licensed permissively for adoption and extension

OSCAL is not, however, designed for the substrate's three-layer
model, rule severity, enforcement bindings, or provenance discipline.
The substrate extends OSCAL through OSCAL's own extension mechanism:
`props` arrays with namespaced property names. The result is OSCAL-
valid content that substrate tooling reads with full semantic
richness and that OSCAL-compatible tooling reads as a standard
control catalog.

## File format and serialization

Substrate catalogs are serialized as YAML. The `.oscal.yaml` suffix
indicates OSCAL content. YAML is chosen over JSON for human
authoring readability; consumers using OSCAL tooling that requires
JSON can convert with standard tools.

Filenames follow the pattern:

```
<catalog-name>.oscal.yaml
```

Examples (concern catalogs):

- `authentication.oscal.yaml`
- `logging.oscal.yaml`

Threat and design-pattern catalogs are reference catalogs in a flatter,
non-OSCAL form (a `metadata` block plus an item collection), named
`<catalog-name>.yaml` and validated by their own schemas
(`schemas/threat-catalog.schema.json`,
`schemas/design-pattern-catalog.schema.json`); for example
`catalogs/threats/stride.yaml` and `catalogs/design-patterns/solid.yaml`.
The OSCAL structure described in the rest of this document applies to
concern and compliance catalogs.

## Top-level document structure

This describes the assembled catalog: the OSCAL document the assembler
(`tooling/assemble/`) emits. Source content is authored in a flatter form, a
per-concern `concern.yaml` plus a co-located `rule.yaml`, `checklist.md`, and
`decision.md` per rule (see `tooling/assemble/README.md`). The assembler reads
that source and produces the OSCAL document described here, so the `props`,
`parts`, and `links` structures below belong to the serialized output, not to
the hand-authored `rule.yaml`.

A catalog document has the following top-level shape per OSCAL:

```yaml
catalog:
  uuid: <RFC 4122 UUID v4>
  metadata:
    title: <human-readable catalog title>
    published: <ISO 8601 timestamp>
    last-modified: <ISO 8601 timestamp>
    version: <catalog version per Charter Article VIII Section 8.4>
    oscal-version: 1.1.2
    props: <substrate extension properties; see below>
    links: <cross-references to other substrate artifacts>
    parties: <authors and reviewers per Charter Article II>
  groups: <optional; groups rules by layer or sub-concern>
  controls: <the rules themselves>
  back-matter: <citations, references>
```

OSCAL's `controls` are what the substrate calls `rules`. The naming
diverges only because OSCAL's heritage is compliance controls; in
substrate vocabulary, every catalog rule is a control in OSCAL's
sense. The substrate uses `rule` in prose and `control` in OSCAL
serialization. Both terms refer to the same thing.

## Substrate extension properties on the catalog

The catalog's top-level `metadata.props` array carries substrate
extension properties. Property names use the namespace prefix
`governance-commons:` to distinguish them from OSCAL native
properties.

Required properties on every catalog:

| Property | Value | Purpose |
|---|---|---|
| `governance-commons:catalog-kind` | `concern`, `threat`, `compliance`, or `design-pattern` | Which catalog kind this is |
| `governance-commons:catalog-id` | Stable identifier (e.g., `concerns/authentication`) | The catalog's substrate identity per Charter Article IV |
| `governance-commons:lifecycle-status` | `draft`, `stable`, `deprecated`, or `retired` | Per `rule-lifecycle.md` |
| `governance-commons:commons-version` | The commons version this catalog targets (e.g., `0.1.0`) | Per Charter Article VIII |
| `governance-commons:catalog-version` | The catalog's own version | Per Charter Article VIII Section 8.4 |

Optional properties on the catalog:

| Property | Value | Purpose |
|---|---|---|
| `governance-commons:entered-status-at` | ISO 8601 date | When the catalog entered its current lifecycle state |
| `governance-commons:superseded-by` | Catalog identifier | When deprecated, the superseding catalog |
| `governance-commons:deprecation-window-ends` | ISO 8601 date | When deprecation ends and retirement begins |
| `governance-commons:authoritative-source` | URL or canonical reference | When the catalog derives from external standard |

Example `metadata.props` for the authentication concern catalog:

```yaml
metadata:
  props:
    - name: catalog-kind
      ns: governance-commons
      value: concern
    - name: catalog-id
      ns: governance-commons
      value: concerns/authentication
    - name: lifecycle-status
      ns: governance-commons
      value: draft
    - name: commons-version
      ns: governance-commons
      value: 0.1.0
    - name: catalog-version
      ns: governance-commons
      value: 0.1.0
    - name: entered-status-at
      ns: governance-commons
      value: 2026-05-17
```

## Rule (control) structure

Each rule in the catalog's `controls` array has the following shape:

```yaml
- id: <rule identifier per substrate convention>
  class: <substrate rule class>
  title: <intent statement per Charter Article IV Section 4.2>
  props: <substrate extension properties on the rule>
  links: <cross-references for this rule>
  parts: <rule body sections; see below>
  controls: <nested rules, rare; flat structure preferred>
```

## Rule identifier convention

Rule identifiers within a catalog follow:

```
<RULE-PREFIX>-L<LAYER>-<NUMBER>
```

- `RULE-PREFIX`: stable abbreviation for the concern/topic
- `LAYER`: `1`, `2`, or `3` per the substrate's layer model
- `NUMBER`: zero-padded three-digit sequence

Examples:

- `authentication.password-hashing`
- `authentication.rate-limiting`
- `logging.correlation-ids`
- `observability.cardinality-discipline`

For catalogs derived from external sources (compliance regimes,
OWASP top-10 lists), the source identifier is preserved as the
primary identifier. Substrate rule prefixes apply to substrate-
authored content (concerns, design-patterns).

The identifier is the OSCAL `id` field. Per Charter Article IV
Section 4.1, the identifier is immutable once the rule reaches
stable lifecycle status.

## Required rule properties

Every rule has the following `props` entries with the
`governance-commons` namespace:

| Property | Value | Purpose |
|---|---|---|
| `governance-commons:layer` | `1`, `2`, or `3` | The substrate layer per the three-layer model |
| `governance-commons:severity` | `P1`, `P2`, or `P3` | Default severity for this rule |
| `governance-commons:lifecycle-status` | `draft`, `stable`, `deprecated`, or `retired` | Per `rule-lifecycle.md` |
| `governance-commons:layer-rationale` | Free-text rationale | Why this rule is L1 vs L2 vs L3 per Charter Article II Section 2.3 |
| `governance-commons:severity-rationale` | Free-text rationale | Why this rule is P1 vs P2 vs P3 per Charter Article II Section 2.3 |

Optional rule properties:

| Property | Value | Purpose |
|---|---|---|
| `governance-commons:applicability` | Free-text or structured | Which features, languages, environments this rule applies to |
| `governance-commons:authoritative-source` | URL or canonical reference | External source for this rule, if any |
| `governance-commons:entered-status-at` | ISO 8601 date | When rule entered its current lifecycle state |
| `governance-commons:superseded-by` | Rule identifier | For deprecated rules |
| `governance-commons:deprecation-window-ends` | ISO 8601 date | For deprecated rules |
| `governance-commons:ai-assistance` | `none`, `proposed`, `drafted`, `validated`, or composite | Per Charter Article II Section 2.2 |

Example rule props for `authentication.password-hashing`:

```yaml
props:
  - name: layer
    ns: governance-commons
    value: "1"
  - name: severity
    ns: governance-commons
    value: P1
  - name: lifecycle-status
    ns: governance-commons
    value: draft
  - name: layer-rationale
    ns: governance-commons
    value: |
      Mechanically detectable. A static analysis tool can identify
      authentication endpoints lacking middleware invocation by AST
      pattern matching. No human judgment required for detection.
  - name: severity-rationale
    ns: governance-commons
    value: |
      P1 because endpoint without auth middleware is a complete
      authentication bypass. The asset (user data) is high-value
      and the exposure window is unbounded.
  - name: authoritative-source
    ns: governance-commons
    value: https://owasp.org/www-project-application-security-verification-standard
```

## Rule parts

OSCAL's `parts` structure carries the rule's body content. The
substrate uses specific part names per layer to ensure consistency
across catalogs.

### Common parts (all rules)

| Part name | Required | Purpose |
|---|---|---|
| `statement` | Required | The rule itself in plain language |
| `intent` | Required | Why this rule exists; the underlying principle |
| `examples-good` | Required for stable rules | Three or more concrete good examples per Charter Article II Section 2.3 |
| `examples-bad` | Required for stable rules | Anti-pattern examples where applicable |
| `references` | Optional | External references beyond the authoritative-source property |

### Layer 1 (mechanical) parts

| Part name | Required | Purpose |
|---|---|---|
| `enforcement-binding` | Required | The rule's co-located `binding.yaml` (capability gate; resolved via `../toolchain/`) |
| `false-positive-notes` | Optional | Known false-positive scenarios documented for consumers |
| `false-negative-notes` | Optional | Known false-negative scenarios documented for consumers |

### Layer 2 (semantic) parts

| Part name | Required | Purpose |
|---|---|---|
| `example-files` | Required | References to example files in the rule's co-located `examples/` |
| `review-checklist` | Required | Bullet checklist a reviewer uses when evaluating this rule against code |
| `contextual-exceptions` | Optional | Common situations where the rule does not apply |

### Layer 3 (judgmental) parts

| Part name | Required | Purpose |
|---|---|---|
| `decision-framework` | Required | Reference to decision framework in `../decision-frameworks/` |
| `documentation-required` | Required | What consumer-side ADR must capture when this decision is made |
| `acceptable-options` | Optional | Enumeration of options the framework supports (each option is acceptable when its trade-offs are documented) |

## Rule links

OSCAL's `links` array on a rule cross-references other substrate
artifacts. Substrate-defined link relations include:

| Relation | Target | Purpose |
|---|---|---|
| `enforced-by` | `binding.yaml` (co-located) | The co-located binding declaring this L1 rule's capability gate |
| `supported-by-examples` | examples path | Which examples support L2 review of this rule |
| `supported-by-framework` | decision-frameworks path | Which framework supports L3 decision for this rule |
| `addresses` | threat rule ID | Threat rule this concern rule mitigates |
| `satisfies` | compliance control ID | Compliance control this concern rule provides evidence for |
| `applies-pattern` | design-patterns rule ID | Design pattern this rule applies |
| `superseded-by` | rule ID | For deprecated rules |
| `supersedes` | rule ID | For replacement rules |

On direction and naming: `applies-pattern` is the forward relation on a concern
rule (rule to the pattern it applies), expressed as an OSCAL `links` entry and
therefore hyphenated. The design-pattern catalogs carry the reverse pointer
where useful, as a flat-catalog field named `applies_pattern_to` (pattern to
the concern rule that enforces or instantiates it); the underscore follows the
flat reference-catalog field style (`when_to_use`, `avoid_when`), not the OSCAL
link-relation style. The two are complementary. No concern rule declares
`applies-pattern` yet; it is available for when a rule should point at a pattern
it realizes.

Example link block for `authentication.password-hashing`:

```yaml
links:
  - rel: enforced-by
    href: binding.yaml
  - rel: addresses
    href: ../catalogs/threats/owasp-llm-top10.yaml#LLM06
  - rel: satisfies
    href: ../catalogs/compliance/trestle-workspace/catalogs/nist-800-53-rev5/catalog.json#ac-3
```

## Provenance encoding

Charter Article II Section 2.2 requires provenance on every catalog
artifact. Provenance is encoded via OSCAL's `parties` metadata and
linked from rules through the `responsible-roles` mechanism.

Example catalog-level provenance:

```yaml
metadata:
  parties:
    - uuid: <UUID for the author party>
      type: person
      name: <author identity>
      props:
        - name: role
          ns: governance-commons
          value: author
        - name: authored-on
          ns: governance-commons
          value: 2026-05-17
    - uuid: <UUID for the reviewer party>
      type: person
      name: <reviewer identity>
      props:
        - name: role
          ns: governance-commons
          value: reviewer
        - name: reviewed-on
          ns: governance-commons
          value: 2026-06-15
```

Provenance is required on stable rules per Charter Article II
Section 2.4. Draft rules require author provenance; reviewer
provenance is added at promotion to stable.

## Groups (optional structure)

OSCAL supports grouping rules within a catalog. The substrate uses
groups optionally to organize rules by layer:

```yaml
groups:
  - id: layer-1-mechanical
    title: Layer 1 - Mechanically enforceable rules
    controls:
      - id: authentication.password-hashing
        # rule body
      - id: authentication.no-credentials-in-urls
        # rule body
  - id: layer-2-semantic
    title: Layer 2 - Semantic rules requiring review
    controls:
      - id: authentication.rate-limiting
        # rule body
  - id: layer-3-judgmental
    title: Layer 3 - Judgmental decisions
    controls:
      - id: authentication.authentication-strategy
        # rule body
```

Groups are organizational only. They do not affect rule identity or
selection by profiles. Concern catalogs typically use the three-
layer grouping above; design-pattern catalogs may group by pattern
family (creational, structural, behavioral); threat catalogs may
group by attack category.

## Back-matter for citations

OSCAL's `back-matter` holds bibliographic references that rules
cite. Substrate catalogs use back-matter for:

- Citation of authoritative sources (NIST publications, OWASP
  guidelines, IETF RFCs, foundational textbooks)
- Links to substrate's own related artifacts
- Pointers to community resources (Stack Overflow answers, blog
  posts) when the substrate uses them as supporting examples
  rather than authoritative sources

Back-matter resources are referenced from rule `links` and from
inline text in rule parts via OSCAL's standard reference mechanism.

## Catalog versus profile

A catalog defines rules. A profile selects rules from one or more
catalogs and applies tailoring. The substrate keeps these strictly
separated.

Catalogs do not contain selection logic, applicability filters, or
parameter assignments. Those belong in profiles. Catalogs contain
the rule definitions; profiles configure which definitions apply
where.

A catalog file never references a profile. A profile file
references catalogs. The reference direction is one-way.

## Identifier collisions

The substrate-shipped namespace owns identifiers without prefix:

- `AUTH-*` (authentication concern)
- `LOG-*` (logging concern)
- `OBS-*` (observability concern)
- (etc.)

Consumer-side custom catalogs MUST namespace their identifiers to
avoid collision per `extension-contract.md`:

```
<consumer-namespace>.<rule-id>
```

Example:

- `acme-corp.INTERNAL-authentication.password-hashing`

The substrate reserves the unprefixed identifier space. Consumers
proposing rules for substrate inclusion drop their namespace prefix
during the proposal process; the substrate assigns the canonical
unprefixed identifier per `extension-contract.md` Section
"Submission back to the substrate".

## Layer assignment guidance

Authors deciding which layer a rule belongs to follow these tests:

A rule is **Layer 1** if a deterministic algorithm (static
analyzer, linter, AST matcher) can detect violations with high
precision and high recall. Examples: "auth middleware called on
every authenticated endpoint," "no secrets in URLs," "all database
queries use prepared statements."

A rule is **Layer 2** if violations are detectable by a reasonable
human or AI reviewer with examples to compare against, but
mechanical detection produces too many false positives or false
negatives. Examples: "authentication errors return generic
messages, not stack traces," "logging includes sufficient context
for incident response without exposing PII."

A rule is **Layer 3** if there is no single right answer and the
decision must be made deliberately with documented trade-offs.
Examples: "choose authentication strategy (session, token,
federated)," "choose database paradigm (relational, document, key-
value)."

Rules that span layers (the same concern has L1, L2, and L3
aspects) are split into separate rules at appropriate layers.

## Severity assignment guidance

Severity reflects the impact of violation:

**P1**: Violation creates complete defense bypass, total system
compromise, regulatory violation with significant penalties, or
data exposure of high-value information. Production deployment
blocked until resolved.

**P2**: Violation creates partial defense bypass, significant
operational risk, or degraded user experience that affects most
users. Resolution required before production deployment for
business-critical systems; may be accepted with documented
mitigation for less critical systems.

**P3**: Violation creates minor risk, edge-case exposure, or
maintenance burden. Resolution recommended; may be accepted with
rationale.

Severity is profile-tailorable per Charter Article IV Section 4.3.
The substrate assigns default severity in the catalog; profiles
adjust per organizational context.

## Lifecycle metadata on the catalog and on rules

Both the catalog as a whole and individual rules carry lifecycle
metadata. They can differ:

- A draft catalog may contain stable rules (rare; usually drafts
  contain drafts)
- A stable catalog may contain draft rules (common; authoring
  proceeds incrementally)
- A deprecated catalog typically contains all-deprecated rules
- A retired catalog is removed entirely

When a catalog's status differs from some of its rules' statuses,
the resolution is:

- Catalog's status determines the catalog's status
- Each rule's status determines that rule's status independently
- Profile selection respects rule-level status (a stable catalog's
  draft rules are not selected by default profile per `rule-
  lifecycle.md`)

## What the format does not specify

To clarify boundaries:

- **The format does not specify rule content**. The substrate
  ships rules; this document specifies the structure those rules
  are encoded in.
- **The format does not specify how OSCAL JSON is generated from
  YAML**. Standard YAML-to-JSON conversion suffices; the substrate
  ships YAML.
- **The format does not specify catalog-internal grouping**.
  Groups are optional; the catalog may or may not use them. When
  used, groups follow OSCAL's group structure.
- **The format does not specify rendering**. How the catalog
  appears in human-facing documentation is consumer's choice.

## Validation

Substrate tooling (`../tooling/assemble/validate.py`) validates the
source layer: every `concern.yaml`, `rule.yaml`, and `binding.yaml`
against `../schemas/concern.schema.json`, `../schemas/rule.schema.json`,
and `../schemas/binding.schema.json`. The schemas enforce:

- Required substrate fields present
- Field values within allowed enumerations
- Rule identifier format correct (`<concern>.<rule-slug>`)
- Layer-specific required artifacts present
- Lifecycle metadata consistent

The assembled `../dist/` catalogs are generated from validated
sources by `../tooling/assemble/assemble.py`.

Validation does not check semantic correctness (whether the rule
itself is right). Charter Article II review discipline catches
semantic errors; schemas catch structural errors.

## Versioning

This format specification is versioned with the commons. Changes
follow Charter Article VIII versioning discipline.

Current specification version: **0.1.0** (matches commons VERSION)

Format changes are particularly sensitive because catalog files
across the substrate depend on the format. Breaking changes
require:

- New extension property names (adding without removing existing
  ones is non-breaking)
- Migration scripts in `../tooling/` to convert catalogs to new
  format
- Major version increment per Charter Article VIII

## Cross-references

- `../CHARTER.md` Article IV (catalog identity and immutability)
- `../CHARTER.md` Article II (authoring discipline)
- `../spec/principles.md` (philosophical foundation)
- `../spec/oscal-model.md` (substrate's OSCAL adoption)
- `../spec/rule-lifecycle.md` (lifecycle metadata semantics)
- `../catalogs/README.md` (catalog kinds overview)
- `../catalogs/concerns/README.md` (concern-specific guidance)
- `../schemas/` (source-layer mechanical validation: concern, rule,
  binding)
- `../spec/manifest-format.md` (consumer manifests reference rule
  identifiers from this format)
- `../tooling/toolchain/README.md` (how rules bind to enforcement tools via
  capability gates)
- `../spec/decision-framework-format.md` (how `decision-framework`
  parts reference frameworks)
