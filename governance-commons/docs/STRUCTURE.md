<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Governance Commons Structure Map

Status: navigation aid. Role: this document says where substrate content
physically lives and why it lives there. It is a signpost, not an authority.
It does not define the taxonomy (the master grid does), it does not define the
rules (the rule folders do), and it does not govern change (the Charter does).
Its single job is to let a human or an AI agent find the right area on the
first look and understand which review moment reaches for it.

This map describes placement, not movement. No files are relocated by writing
it. When the tree changes, this map is updated to match; the tree is the truth.

---

## 1. The mental model in one line

`catalogs/concerns/` is the content: the 226 rules, the whole substance of the
substrate. Every other directory plays exactly one supporting role: other
authored content that orbits concerns, a contract that validates content,
generated output, consumer-facing reference, or tooling. Plus governance docs
at the root, and a small set of vestigial scaffolds slated for removal.

If a directory does not fit one of those roles, it does not belong.

---

## 2. The canonical rule unit

Every rule is one folder under `catalogs/concerns/<concern>/<rule-slug>/`.
Two artifacts are always present:

- `rule.yaml` (the rule: id, name, layer, characteristic, severity, sources,
  statement, rationale)
- `examples/good.md` and `examples/anti-pattern.md`

On top of that base sits the layer-specific artifact, and that artifact is how
you read a rule's layer without opening it:

- `binding.yaml` present, no checklist, no decision -> L1 mechanical (tool decides)
- `checklist.md` present, no decision -> L2 semantic (a reviewer decides in context)
- `checklist.md` and `decision.md` present -> L3 judgmental (a choice is recorded)

L2 rules often also carry `test-template.md`. A small number of rules also
carry a `guidance.md`; that artifact is off the canonical shape and is a known
inconsistency, not a fourth layer signal.

---

## 3. The directories by role

Counts are current as of this writing. They are descriptive, not authoritative;
the master grid owns the taxonomy counts and the rule folders own the truth.

### 3a. Authored content (the value the substrate ships)

- `catalogs/concerns/` : 25 concerns, 226 rule folders. The heart.
- `catalogs/threats/` : 5 threat catalogs (MITRE ATLAS, OWASP LLM Top 10,
  OWASP Agentic ASI, OWASP Agentic Skills, STRIDE). A lens over concerns, not
  a restatement of them.
- `catalogs/compliance/` : ISO 42001 and SOC2 TSC catalogs plus a populated
  trestle-workspace. A lens applied through profiles.
- `mappings/` : 5 threat-and-standard to concern mappings. The traceability
  links that connect the lenses in `threats/` and `compliance/` to concern rules.
- `profiles/` : 5 profiles (production-grade-baseline plus financial-services,
  healthcare, regulated-ai, fedramp tilts). Selections and tailorings over
  concerns for a context.
- `policies/` : 8 Cedar policy files plus a Cedar schema. Concrete machine
  enforcement for the authorization and agentic concerns, mapped to principles
  and threats. Complementary to the rules, not a copy of them.
- `attestation/` : supply-chain attestation reference (cosign, in-toto, SLSA
  v1.0). The how-to material the supply-chain concern rules point at.
- `lib-context/` : 7 library-context files (LangChain, LangGraph, Pydantic,
  FastAPI, Terraform AWS, Cedar, AI model pricing). How rules land on a stack.
- `playbooks/` : 8 incident-response playbooks. Operational reference, used at
  incident time rather than authoring time.

### 3b. Contracts (the rules about the rules)

- `schemas/` : 11 JSON schemas validating every authored artifact kind.
- `spec/` : 17 specification documents (formats, contracts, principles,
  lifecycle, the settled enforcement-tooling engine policy). The most heavily
  referenced area in the substrate.

### 3c. Generated output (derived, never hand-edited)

- `dist/concerns/` : 25 assembled OSCAL catalogs, committed because profiles
  import them. `dist/index.yaml` and resolved profiles stay generated and
  git-ignored. Produced by the assembler from `catalogs/concerns/`.

### 3d. Consumer-facing reference

- `reference/` : example agents, the pre-commit hook example, a governance
  manifest, templates, and a CI workflow. What a consuming project copies.

### 3e. Tooling

- `tooling/assemble/`, `tooling/toolchain/`, `tooling/floor-generator/` : the
  live toolchain (`make gc-validate`, `gc-assemble`, `gc-toolchain-audit`,
  `gc-generate-floor`).
- `tooling/profile-resolver/`, `tooling/mapping-coverage-reporter/` : each
  carries one real script (partial).
- `tooling/tailoring-agent/` : README-only stub, not built.

### 3f. Governance and meta (root files)

`CHARTER.md` (supreme authority for all change), `CHANGELOG.md`, `FUTURE.md`,
`MAINTENANCE.md`, `PORTABILITY.md`, `README.md`, `SUBSTRATE-FIT.md`,
`CONTRIBUTORS.md`, `VERSION`, `authoring-mode.yaml`.

### 3g. Near-empty by design

- `decision-frameworks/` (top level) : README and .gitkeep only; the L3
  decision content lives in each rule's `decision.md`. Retained for its
  orientation README (the L3 format entry point).

---

## 4. How the areas relate to concerns (no duplication)

Concerns hold the rules. The other authored areas are different artifact types
that orbit concerns. They do not duplicate rule content:

- threats and compliance are lenses that point at concerns; the pointing is
  recorded in `mappings/`.
- profiles select and tailor which concern rules apply in a context.
- policies are runnable Cedar enforcement for the authz and agentic concerns,
  mapped to principles and threats rather than to a single rule, which is why
  they live in their own area instead of inside one rule folder.
- attestation is shared supply-chain reference that several supply-chain rules
  point at.
- lib-context is the stack-specific bridge for applying a rule to a library.

The tree has no redundancy. Everything is complementary:
a requirement (the rule), a lens (threats, compliance, mappings, profiles), a
runnable enforcement (policies), or shared reference (attestation, lib-context).

---

## 5. Which area for which review moment

A reviewing agent (for example a staff-engineer or code-review sub-agent)
reaches for different areas depending on what is under review.

| Review moment | Areas to read |
|---|---|
| A feature change against the rules | `catalogs/concerns/` (L2 checklists), `profiles/` for which rules are active and tightened |
| Threat coverage or a compliance question | `mappings/`, `catalogs/threats/`, `catalogs/compliance/` |
| Authorization or agent autonomy | `policies/` (Cedar), the authorization and agentic-systems concerns |
| CI/CD and supply chain | `attestation/`, the supply-chain concern |
| Code that uses a specific library | `lib-context/` |
| Contracts and what is enforceable mechanically | `schemas/`, `spec/`, the per-rule `binding.yaml` files |
| An incident in production | `playbooks/` |

---

## 6. Authority and precedence

This map defers to three authorities and never overrides them:

- The Charter (`CHARTER.md`) governs all change.
- The master grid governs the taxonomy (the two axes and the counts).
- The rule folders are the truth for rule content and layer.

When this document and any of those disagree, they win and this map is corrected.
