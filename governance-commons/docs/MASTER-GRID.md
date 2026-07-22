# Governance Commons Master Grid

Status: stable (promoted from draft 2026-07-01; counts reconciled). Role: this is the authoritative index of the
governance-commons taxonomy. It defines the two axes, cites the authority for
each, shows what content exists in each cell today as counts only, and defines
the upgrade path for growing the substrate. It is the always-start-here file.

This document is deliberately thin. It does not contain the L1 binding tables,
the L2 checklist inventories, or the L3 decision lists. Those live in three
separate detail documents, one per row, linked below. The master changes only
when the taxonomy itself changes; the detail documents change when content
inside a row changes. This separation is the single-responsibility discipline
applied to documentation, and it is what keeps this file stable and trusted.

---

## 1. The model: two axes

Governance Commons is organized as a grid. Every rule, checklist, and decision
framework occupies exactly one cell.

- Columns are subject: what quality dimension the content is about.
- Rows are enforcement mechanism: who or what decides whether the content is
  satisfied.

A given concern spans all three rows. Security has machine-decidable rules, has
review-decidable rules, and has decisions-with-recorded-rationale. The columns
run vertically through the rows. Subject and mechanism are orthogonal, and
keeping them orthogonal is what prevents the taxonomy from collapsing.

Two assignment disciplines hold the grid together:

- Row assignment, the strongest-full-resolver test. A rule belongs to the row
  of the strongest mechanism that fully resolves it as written. If a tool can
  fully decide it, it is L1, even when a richer related question needs review.
  The related question is a separate rule in L2.
- Column assignment, single-primary-with-cross-reference. Each rule has one
  primary subject column (the one a domain expert names first) and may
  reference secondary columns. It is never duplicated across columns.

---

## 2. Rows (enforcement mechanism) and their cited authority

The row axis is the assurance-mechanism axis used in software security
engineering, which separates automated static checks, human review, and design
decisions as distinct assurance types.

| Row | Name | Decided by | The test | Cited authority |
|---|---|---|---|---|
| L1 | Machine-decidable | A tool, deterministically, no human | Can a static checker fully resolve this rule as written | NIST SSDF SP 800-218 (automated check practices); OWASP ASVS (tool-verifiable requirements) |
| L2 | Review-decidable | A human or agent reviewing against a checklist | Does correctness require contextual judgment a tool cannot make | NIST SSDF SP 800-218 (manual review practices); OWASP ASVS (review-verifiable requirements) |
| L3 | Decision-with-recorded-rationale | A reasoned choice among legitimate alternatives, recorded as an ADR/MADR | Are there multiple defensible answers that must be chosen and justified | MADR (Markdown Any Decision Records); Nygard ADR practice |

Why three rows and not two or five. Two rows (automated versus manual) would
collapse L2 and L3, losing the real distinction between reviewing against a
rubric and choosing-and-recording a strategy, which are different acts with
different artifacts. Adding rows for dynamic testing or runtime monitoring was
rejected: those are consumer activities, not substrate-authored content, so
they do not earn a row in a taxonomy of what the substrate ships. Three is the
minimum that preserves the real distinctions and the maximum that stays inside
what the substrate authors.

Naming note: L3 is named for its artifact (recorded rationale), not for being
opinionated. L2 is opinionated too; the distinguishing property of L3 is that
the choice has legitimate alternatives and must be justified, not merely
reviewed.

---

## 3. Columns (subject) and their cited spines

The substrate has multiple spines, not one. Each column cites the external
authority it is based on. The substrate authors the rules inside a column;
the spine provides the organizing vocabulary and the provenance, per Charter
Section 2.6 (cite authoritative sources, do not claim to invent what is
curated).

### 3a. Primary subject spine: software quality characteristics

The column backbone for quality is ISO/IEC 25010:2023, the international
standard for a software product quality model. The 2023 revision defines nine
characteristics. Concerns map onto these as their primary column.

| 25010:2023 characteristic | Example concerns mapped here |
|---|---|
| Functional suitability | input-validation (correctness aspects), testing-strategy |
| Performance efficiency | performance-database, performance-caching, cost-model-selection |
| Compatibility | dependency-management (interop aspects), configuration-management |
| Interaction capability | documentation (consumer-facing aspects) |
| Reliability | reliability, error-handling, backup-recovery, monitoring-alerting |
| Security | authentication, authorization, secrets-management, input-validation, supply-chain, data-classification, privacy |
| Maintainability | code-organization, observability, logging, feature-flags |
| Flexibility | configuration-management (portability aspects) |
| Safety | responsible-ai, agentic-systems (harm-prevention aspects) |

Sparse cells are expected and correct. Interaction capability and Safety are
thin on L1 (few machine-decidable rules) and concentrate in L2 and L3. Do not
force a rule into an empty cell; absence of a machine-decidable rule is a
true property of some characteristics, not a gap to fill.

### 3b. Cross-reference band: threat spines

Threats are lenses over the quality characteristics, not characteristics
themselves. A single threat maps onto several columns, so threats are recorded
as a cross-reference band, not as peer columns. Each is an external spine the
substrate cites and slices.

| Threat spine | Layer it addresses | Status in commons |
|---|---|---|
| STRIDE | General application threat modeling | Present (mapped to concerns) |
| OWASP Top 10 | Traditional web application risks | Present (mapped to concerns) |
| OWASP LLM Top 10 | Model layer | Present (mapped to concerns) |
| OWASP Agentic ASI | Orchestration layer | Present (mapped to concerns) |
| OWASP Agentic Skills Top 10 | Skill layer | Present (mapped to concerns) |
| MITRE ATLAS | Adversarial ML | Present (mapped to concerns) |

### 3c. Cross-reference band: compliance spines

Compliance regimes are also lenses, applied through profiles that raise
emphasis. They cite external regimes and do not by themselves make a consumer
compliant.

| Compliance spine | Applied via |
|---|---|
| NIST (SSDF, AI RMF, SP 800-53) | profiles, threat mappings |
| ISO/IEC 42001 | regulated-ai profile |
| SOC2 TSC, PCI-DSS, HIPAA, FedRAMP | industry-tilt profiles |

### 3d. Cross-reference band: design patterns

Design patterns are a present cross-reference band of 9 catalogs: SOLID,
Gang of Four, design principles, architecture, code smells, complexity classes,
cloud scaling failure modes, distributed systems fallacies, and domain-driven
design. Per the reference-not-author principle, the substrate cites these
catalogs and adds only the stack-applicability and the review checklist, not the
pattern bodies.

---

## 4. What exists today (counts only)

Counts are primary-home rule IDs per concern: each rule is counted once, at
the concern it lives in, so the columns sum to the totals above (62 / 131 / 33).
A rule cross-referenced by another concern is still counted only at its home,
not in each citing concern. Detail lives in the row documents, not here.

Substrate-wide totals (regenerate with tooling/grid-counts/counts.py):

- 25 concern catalogs (stable).
- L1 machine-decidable: 62 mechanical rules, each naming a capability gate the
  toolchain resolves to an OSS tool.
- L2 review-decidable: 131 review checklists plus 102 test templates.
- L3 decision-with-recorded-rationale: 33 MADR decision frameworks homed in
  concerns (34 decision-framework files total, including the top-level
  technology-selection framework).
- 6 threat spines, 5 profiles (1 base plus 4 industry tilts), 6 threat/
  compliance mappings.
- 9 design-pattern catalogs (SOLID, Gang of Four, design principles,
  architecture, code smells, complexity classes, cloud scaling failure modes,
  distributed systems fallacies, domain-driven design).

Per-concern shape (L1 / L2 / L3 primary-home counts):

| Concern | L1 | L2 | L3 |
|---|---|---|---|
| agentic-systems | 0 | 8 | 4 |
| authentication | 5 | 9 | 2 |
| authorization | 2 | 9 | 1 |
| backup-recovery | 2 | 2 | 1 |
| code-organization | 3 | 5 | 1 |
| configuration-management | 2 | 2 | 1 |
| cost-model-selection | 2 | 2 | 1 |
| data-classification | 1 | 7 | 1 |
| dependency-management | 2 | 2 | 1 |
| documentation | 2 | 2 | 1 |
| error-handling | 4 | 5 | 1 |
| feature-flags | 2 | 2 | 1 |
| infrastructure-misconfiguration | 5 | 6 | 1 |
| input-validation | 5 | 6 | 1 |
| logging | 3 | 6 | 1 |
| monitoring-alerting | 2 | 5 | 1 |
| observability | 1 | 6 | 1 |
| performance-caching | 2 | 6 | 1 |
| performance-database | 4 | 7 | 1 |
| privacy | 0 | 7 | 2 |
| reliability | 3 | 4 | 1 |
| responsible-ai | 0 | 8 | 4 |
| secrets-management | 2 | 5 | 1 |
| supply-chain | 4 | 7 | 1 |
| testing-strategy | 4 | 3 | 1 |

L1 note (consistent with SUBSTRATE-FIT): the L1 layer is realized. Each
mechanical rule names a capability gate that the toolchain registry and
selection resolve to an OSS tool; there are no per-rule registry references to
drift, so L1 is as authoritative as L2 and L3. The only consumer-side step is
operational: wire the tools through the generated floor and supply the SAST
rule set (see SUBSTRATE-FIT and spec/enforcement-tooling.md).

---

## 5. Row detail documents (the spokes)

Each row has one detail document. The master links to them and never inlines
their content. Build each when you do that row.

- L1 detail: the toolchain model is the L1 source of truth. `toolchain/registry.yaml`
  and `toolchain/selection.yaml` resolve each mechanical rule's co-located
  `binding.yaml` (its capability gate) to an OSS tool; `SUBSTRATE-FIT.md` and
  `spec/enforcement-tooling.md` document the model. Status: realized.
- L2 detail: review-checklist inventory by concern and characteristic.
  Status: planned.
- L3 detail: MADR decision-framework inventory by concern and characteristic.
  Status: planned.

---

## 6. Upgrade path (always start here)

This is the procedure for changing or growing the taxonomy. Any growth of
governance-commons begins by editing this master, then flows to a spoke. The
order matters: the taxonomy decision is made at the hub before content is
authored at the spoke.

### 6a. To add or change a row (enforcement mechanism)

Rare. Rows are an assurance-mechanism taxonomy with cited authority; changing
them is a structural change.

1. State the new mechanism and the cited authority that justifies it.
2. Confirm it is substrate-authored content, not a consumer activity (the test
   that rejected dynamic-testing as a row).
3. Update Section 2 here, then create the spoke document for the row.
4. Charter governance applies: cooling-off, validators, attestation, semver.
   A new row is a major change.

### 6b. To add or change a column (subject)

1. Identify the spine. Is this a new quality characteristic (must trace to
   25010:2023), a new threat lens (cross-reference band), a new compliance
   regime (profile), or the design-pattern spine.
2. If it does not trace to an existing spine, decide whether a new spine is
   warranted and cite its external authority. Do not author a column with no
   external provenance unless it is genuinely original (declared per Charter).
3. Update Section 3 here with the new column and its citation.
4. Author the cell content in the relevant spoke document(s), one row at a time.

### 6c. To add or change a rule (a cell)

1. Assign the row by the strongest-full-resolver test (Section 1).
2. Assign the primary column by single-primary-with-cross-reference (Section 1).
3. For an L1 rule, the spoke records the tool-family binding, not a hand-
   authored rule body, unless it is an orphan with no tool (then it is a
   deliberate substrate-authored ruleset under Apache license).
4. Update the count in Section 4 here; author the detail in the spoke.
5. Charter governance applies at the level the change warrants (tightening a
   threshold or adding a blocking gate is breaking; an advisory addition is
   minor).

### 6d. Invariants the upgrade path must preserve

- Orthogonality: never let a row become a subject or a column become a
  mechanism.
- Single source of truth: a fact (a threshold, a rule) lives in one cell and
  one spoke, cross-referenced elsewhere, never copied.
- Cited provenance: every column names its spine; every row names its
  authority; original content is declared as original.
- Master stays thin: detail never migrates up into this file.

---

## 7. Citation summary

- Column subject spine (quality): ISO/IEC 25010:2023, Systems and software
  engineering, Systems and software Quality Requirements and Evaluation
  (SQuaRE), product quality model (nine characteristics).
- Column threat spines: STRIDE; OWASP Top 10; OWASP LLM Top 10; OWASP Agentic
  ASI; OWASP Agentic Skills Top 10; MITRE ATLAS.
- Column compliance spines: NIST SSDF SP 800-218; NIST AI RMF; NIST SP 800-53;
  ISO/IEC 42001; SOC2 TSC; PCI-DSS; HIPAA; FedRAMP.
- Column design-pattern spine: SOLID; Gang of Four design patterns; design
  principles; architecture; code smells; complexity classes; cloud scaling
  failure modes; distributed systems fallacies; domain-driven design.
- Row mechanism authority: NIST SSDF SP 800-218 (automated, manual, and
  design practice separation); OWASP ASVS (tool-verifiable versus review-
  verifiable); MADR and Nygard ADR practice for the decision row.
- Substrate supreme authority for all changes: CHARTER.md.
