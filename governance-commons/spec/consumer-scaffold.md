<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Consumer Scaffold

This document specifies the normative consumer scaffold contract: the
five obligations a consumer satisfies to integrate Governance Commons
end-to-end, and the substrate-published patterns for each. The
contract unifies three existing spec docs (`manifest-format.md`,
`consultation-evidence.md`, `consumption-contract.md`) under a single
normative narrative, and adds two topics not previously covered at
spec depth: agent prompt injection patterns and CI workflow
integration.

Mechanical validation of the manifest happens via
`../schemas/manifest.schema.json`. Mechanical validation of
consultation events happens via
`../schemas/consultation-event.schema.json`. The agent prompt
injection contract and the CI workflow integration contract are
prose specifications in this document; their reference
implementations are consumer-side files pointed to from Section 5
below.

This document is the substrate's normative reference for "how to
build a consumer scaffold that integrates the substrate end-to-end."
It is published by the substrate; the scaffold implementations
themselves live consumer-side, not in the substrate. The substrate
ships the contract and a reference manifest; consumers author their
own scaffold per their own discipline.

## Why this document exists

The substrate ships fragments without a consuming workflow. Charter,
catalogs, profiles, bindings, schemas, and decision frameworks are
all in place; the manifest format, evidence contract, and consumption
contract are all specified. What is not specified at spec depth is
how a consumer wires the fragments together into a working scaffold.
Consumers face five open questions when they integrate:

- Where does the consumer's `governance-manifest.yaml` live, what
  fields are required, and what does a complete instance look like?
  Answered in `manifest-format.md` and in the reference manifest at
  Section 5.
- How does the manifest get injected into AI agent invocations so
  that each agent sees only its assigned catalogs and its assigned
  Charter articles? Answered in Section 3 of this document.
- How does the CI workflow consume substrate bindings and emit
  findings that cross-reference the manifest's required-consultation
  contract? Answered in Section 4 of this document.
- How does the agent emit consultation evidence conforming to
  `consultation-event.schema.json` such that closure verification
  can confirm the agent satisfied the manifest's contract? Answered
  in `consultation-evidence.md` and referenced in Section 2 below.
- What does the closure verification step actually do, and where
  does it run? Answered in `consultation-evidence.md` and in this
  document's Section 4 (CI workflow integration) where closure
  verification is the gating step before merge.

Until M3 lands, all catalogs (M1, M2, and beyond) are content
without a reader. Each catalog increases substrate value zero until
the consumer scaffold is operational. This document is the substrate's
authoritative answer to "what does operational mean for a consumer."

## The substrate-author guarantee

Authoring this document at substrate-published depth carries a
substrate-author guarantee: the contracts specified here are stable
under the same Charter Article IV immutability semantics as the
concern catalogs. Once promoted from draft to stable, the agent
prompt injection contract and the CI workflow integration contract
cannot break consumers without a Charter-amendment justification.
Consumers who build to this spec at version N are not silently
broken at version N+1.

The draft lifecycle in this M3 Session 1 authoring period is
deliberate: the contract exercises the substrate's first end-to-end
reference scaffold in Section 5 and gives the substrate-author the
M3 cooling-off interval to validate the contract against real
consumer scaffold construction before commitment grade.

## Section 1: The five obligations the consumer scaffold satisfies

A consumer scaffold that integrates Governance Commons end-to-end
satisfies five obligations. The first three concern declaration of
intent (what the consumer commits to consulting); the last two
concern verification of action (what the consumer actually did).

### Obligation 1: A complete governance manifest

The consumer publishes a `governance-manifest.yaml` (location
consumer-defined; substrate recommends repo root) that declares:

- The commons version the consumer integrates against
- The profile the consumer uses for selections
- The checkpoints in the consumer's workflow at which substrate
  consultation occurs, with each checkpoint mapping to the catalogs,
  rules, mappings, or decision frameworks consulted
- The audit medium and integrity guarantee for consultation evidence

The manifest format is specified in `manifest-format.md`. The schema
is `../schemas/manifest.schema.json`. The reference instance is at
the consumer-scaffold path documented in Section 5.

The manifest is the cost-and-time efficiency mechanism. Without it,
consumers either hard-code substrate consultation into every agent
prompt (which fragments knowledge and resists update) or consult
all of governance-commons every time (which exceeds the context-rot
inflection point and produces lower-quality outputs). The manifest
declares once what each checkpoint consults, and substrate tooling
plus consumer workflow read the same source of truth.

### Obligation 2: Agent prompt patterns the manifest injects into

The consumer authors agent prompts that accept manifest-supplied
slots at invocation time. The patterns specified in Section 3 of
this document define the injection contract: what slots the agent
prompt declares, what the orchestrator (or invoker) fills, and what
the agent is required to produce in return.

This is new normative content. Prior spec docs specified the
manifest format and the evidence contract; they did not specify the
agent prompt structure that connects them.

### Obligation 3: Constitution slicing

The consumer ensures each agent invocation receives only the
Charter articles relevant to that invocation's checkpoint, not the
whole Charter. The constitution slicing mechanism is part of the
manifest (per-checkpoint constitution-articles consumer extension
field, or per-agent in consumer-side agent definition); the
substrate's contract is that consumers do not inject the whole
Charter at every invocation, since doing so degrades agent
performance past the context-rot inflection point.

The substrate-recommended hard cap on context tokens injected per
agent invocation is 30K to 50K. The Charter alone is approximately
36K and is at the upper end of this cap before any catalog content
is added; thus, constitution slicing is required, not optional.

### Obligation 4: Consultation evidence emission

When an agent finishes a checkpoint, it emits one or more
consultation events conforming to `consultation-event.schema.json`.
The event records what the agent consulted, what findings the agent
produced, and any closure claims the agent made. The evidence
contract is specified in `consultation-evidence.md`.

The agent may emit events directly (by instruction in the agent
prompt to produce a structured JSON block at the end of the agent's
response), or an orchestrator wrapping the agent may emit on the
agent's behalf. Both paths satisfy the contract. The substrate is
agnostic to the emission mechanism; the substrate is opinionated
that the event shape conforms to the schema.

### Obligation 5: Closure verification

A closure step reads emitted consultation events and verifies that
they reference the rules the manifest required consulting. Charter
Article VI Section 6.1 names this the consultation evidence
contract. Operationally, the closure step runs as a pre-commit
hook, as a pre-merge CI job, or as both. The closure step is the
mechanical enforcement of the manifest's declared intent.

Closure failure modes the contract detects:

- Required-rule omission: the manifest declared the checkpoint
  consults catalog X, but no event references catalog X's rules
- Findings without closure: the agent reported a finding but did
  not record how it was addressed (acknowledgment, mitigation,
  exception, deferral)
- Substrate drift: the agent referenced rule IDs that do not exist
  in the pinned commons version (typo, hallucination, or substrate
  upgrade out of sync with the manifest)

The reference closure-verification implementation is the CI
workflow described in Section 4.

## Section 2: How the obligations map to existing substrate documents

Each obligation has prior substrate documentation that this
document does not duplicate. The cross-references below are
authoritative; this document only narrates the unifying narrative
and adds Sections 3 and 4 (agent prompt patterns and CI workflow
integration) as new normative content.

- **Obligation 1 (manifest)** -> `manifest-format.md` for the
  format specification and `schemas/manifest.schema.json` for the
  mechanical validator. Section 5 of this document points to the
  reference manifest instance.
- **Obligation 2 (agent prompts)** -> Section 3 of this document.
  No prior substrate spec doc covered this at normative depth.
- **Obligation 3 (constitution slicing)** -> The substrate's
  position is recorded in this document's Section 1 Obligation 3.
  Constitution slicing is a manifest extension; per-checkpoint
  `constitution-articles` is a consumer extension under the
  `additionalProperties: true` allowance in
  `schemas/manifest.schema.json`. Future substrate work may
  formalize the slot.
- **Obligation 4 (evidence emission)** -> `consultation-evidence.md`
  for the contract; `schemas/consultation-event.schema.json` for
  the mechanical validator.
- **Obligation 5 (closure verification)** ->
  `consultation-evidence.md` Section "Verification requirements"
  for the contract; Section 4 of this document for the reference
  CI workflow implementation.

The two pieces of new normative content (Sections 3 and 4 below)
fill gaps that prior spec docs left open. Each is bounded so the
substrate-author can author the contract at spec depth without
spilling into consumer-side implementation.

## Section 3: Agent prompt injection patterns

This section is new normative content. It specifies the contract
between manifest, orchestrator, and agent at each consultation
checkpoint.

### 3.1 The injection problem

An agent invoked at a checkpoint needs three categories of context:

- **Constitution context**: which Charter articles bound this
  invocation. The whole Charter is roughly 36K tokens; injecting
  it whole degrades agent performance past the context-rot
  inflection point. Constitution slicing is the substrate's
  position.
- **Catalog context**: which substrate catalogs, rules, mappings,
  or decision frameworks the agent consults. The manifest declares
  this per checkpoint.
- **Task context**: the artifact under review (a spec, a plan,
  generated code, a PR diff). Task context is consumer-supplied
  per invocation.

The agent prompt is the contract that accepts these three
categories as slots, processes them, and returns a structured
output that satisfies Obligation 4 (evidence emission).

### 3.2 The injection contract

The substrate-published injection contract is the following set of
slots an agent prompt accepts:

- `{{ commons-version }}`: the pinned commons version (string,
  e.g. `0.5.0`). Sourced from `manifest.substrate.commons-version`.
- `{{ profile }}`: the active profile identifier (string, e.g.
  `production-grade-baseline`). Sourced from
  `manifest.substrate.profile`.
- `{{ checkpoint-name }}`: the consulter's checkpoint name (string,
  e.g. `post-spec-drafting`). Sourced from the active checkpoint's
  `name` field.
- `{{ consults-catalogs }}`: a list of catalog references the
  agent must consult at this checkpoint. Sourced from the
  checkpoint's `consults.catalogs` array.
- `{{ consults-rules }}`: a list of rule IDs the agent must
  consult (when the checkpoint targets specific rules rather than
  whole catalogs). Sourced from the checkpoint's `consults.rules`
  array.
- `{{ consults-mappings }}`: a list of mapping references when the
  checkpoint requires consulting threat or compliance mappings.
  Sourced from the checkpoint's `consults.mappings` array.
- `{{ consults-decision-frameworks }}`: a list of L3 MADR
  decision-framework references when the checkpoint requires
  consulting them. Sourced from the checkpoint's
  `consults.decision-frameworks` array.
- `{{ constitution-articles }}`: a list of Charter article
  identifiers (e.g. `Article-V`, `Article-VI`) that bound this
  invocation. Sourced from a consumer-extension field on the
  checkpoint (substrate-recommended field name:
  `constitution-articles`); if absent, the orchestrator selects a
  substrate-recommended default per consulter type.
- `{{ artifact-under-review }}`: the consumer-supplied artifact
  text. Not from the manifest; supplied per invocation.

The orchestrator fills these slots before invoking the agent. The
agent's response references the slot values directly in its
findings so that emitted consultation events reproduce the
manifest's contract values.

### 3.3 The agent's required output shape

The agent's response includes a structured block (substrate-
recommended format: a fenced code block tagged `consultation-event`
or `consultation-events`) containing one or more JSON objects
conforming to `schemas/consultation-event.schema.json`. The
orchestrator parses the block, validates it against the schema,
and writes it to the audit medium declared in
`manifest.evidence.location`.

The agent's narrative response (the human-readable analysis) is
emitted alongside the structured block. The substrate's contract
is on the structured block; the narrative is consumer-decided
content.

### 3.4 Constitution slicing per consulter type

The substrate publishes a substrate-recommended mapping from
common consulter types to the Charter articles each typically
requires. Consumers override the defaults in the manifest
extension or the agent definition. The defaults:

- `threat-modeling-agent`: Articles V (security posture), VI
  (governance loop closure)
- `code-review-agent`: Articles II (authoring discipline as
  consumer-author analog), V (security posture), VI (governance
  loop closure)
- `implementation-planning-agent`: Articles II, V, VI
- `architecture-review-agent`: Articles I (substrate identity),
  V, VI, VII (compatibility with consumers as forward-looking
  consideration)
- `policy-decision-point` (runtime): Article V, VI

These defaults are substrate-recommended and not substrate-
required. Consumers whose threat model includes considerations
beyond the defaults (regulated industries, AI-first deployments,
multi-tenant systems) extend the defaults per consumer discipline.

### 3.5 Hard context cap

The substrate's hard cap on context tokens injected per agent
invocation is 30K to 50K. This includes the constitution articles,
the catalog content for consulted catalogs (or the rule content
for consulted rules), and the artifact under review. The cap is
substrate-recommended, not substrate-enforced. Consumers whose
infrastructure measures token counts at invocation time can
implement the cap mechanically; consumers without such measurement
adopt the cap as a design constraint on agent prompt construction.

Cap breach modes the substrate has observed:

- **Whole-Charter injection**: 36K tokens of Charter at every
  invocation leaves 0K to 14K for catalog plus artifact. The fix
  is constitution slicing per 3.4 above.
- **Whole-catalog injection at high-depth concerns**: a
  high-depth concern catalog (10-15 rules at full depth) plus its
  paired MADR plus paired examples can exceed 50K alone. The fix
  is rule-level rather than catalog-level injection at checkpoints
  where only specific rules are required.
- **Combined-mapping injection**: the four threat catalog mappings
  combined (OWASP LLM Top 10 -> concerns, OWASP Agentic ASI ->
  concerns, MITRE ATLAS -> concerns, STRIDE -> concerns) are
  substantial. The fix is to inject one mapping per consulter or
  to inject mapping summaries rather than full mapping tables.

### 3.6 The reference agent prompt pattern

The substrate ships the agent prompt patterns as reference files
under the consumer-scaffold examples (location documented in
Section 5). The reference is illustrative; consumer agent prompts
need not literally match. The substrate's contract is on the slots
filled and the output shape returned, not on the prose framing
inside the prompt.

## Section 4: CI workflow integration

This section is new normative content. It specifies the contract
between manifest, CI pipeline, and the consultation evidence
record at the closure verification step.

> **L1 enforcement note (as of 1.0.0).** The substrate names a
> capability gate for each mechanical rule and resolves it to an OSS
> tool through the toolchain; it does not ship the tools or their rule
> sets. Wire the L1 tools through the generated enforcement floor
> (`make gc-generate-floor`), and for the SAST gate supply the
> maintained community rule set (see `SUBSTRATE-FIT.md` and
> `spec/enforcement-tooling.md`). This is one-time setup; once wired,
> L1 is authoritative alongside L2 and L3, with no upstream-liveness
> risk because the substrate holds no per-rule registry references.

### 4.1 The CI integration problem

A consumer that satisfies Obligations 1 through 4 (manifest,
agent prompts, constitution slicing, evidence emission) still
needs a mechanical gate that verifies the obligations actually
occurred. The substrate's position is that the CI workflow is
the natural location for this gate: pre-merge or pre-deploy is
where mechanical verification has clear stakes and clear blast
radius.

### 4.2 The substrate-default static-analysis engine

OpenGrep is the substrate-default static-analysis
engine. Mechanical (L1) rules bind to capability gates in each
rule's co-located `binding.yaml` (`binding_status:
capability-bound`), resolved to a concrete OSS tool through
`toolchain/` (registry plus selection); the SAST capability
resolves to OpenGrep (LGPL-2.1) by default and runs the
consumer-supplied maintained community rule set directly.
OpenGrep and Semgrep Community Edition consume the same rule
syntax; consumers may choose either engine.

The substrate does not endorse Semgrep AppSec Platform or
Semgrep Pro; those are proprietary products of the upstream
Semgrep vendor. The substrate's bindings are compatible with
them but the substrate's recommendation is OpenGrep on
license-compatibility grounds.

### 4.3 The CI workflow contract

The substrate-published CI workflow contract is the following
sequence of mechanical steps:

1. **Discover the manifest.** The CI workflow reads
   `governance-manifest.yaml` (or the consumer-defined location)
   at the start of the run. Failure to discover the manifest is
   a substrate-noncompliance signal: the consumer claims
   substrate integration but has not published a manifest. The
   workflow exits with a structured noncompliance message.
2. **Validate the manifest.** The CI workflow validates the
   manifest against `schemas/manifest.schema.json`. Validation
   failure is a substrate-noncompliance signal: the manifest
   exists but does not conform to the contract.
3. **Pin commons version.** The CI workflow reads
   `manifest.substrate.commons-version` and pins all subsequent
   substrate reads to that version. Consumers vendor the
   substrate at the pinned version (substrate-recommended) or
   resolve the version against a substrate registry (future
   substrate tooling).
4. **Run static-analysis bindings for in-scope checkpoints.** For
   each checkpoint whose `consulter` is the static-analysis
   engine (typical name: `pre-commit` or `pre-merge`), the CI
   workflow runs OpenGrep with the substrate's static-analysis
   bindings for the checkpoint's `consults.catalogs` (filtered
   to L1 mechanical rules). The substrate's bindings are at
   co-located `binding.yaml` files (capability gates resolved via `toolchain/`).
5. **Collect consultation events.** For each checkpoint whose
   `consulter` is an AI agent (typical names: `threat-modeling-
   agent`, `code-review-agent`, `implementation-planning-agent`),
   the CI workflow reads the audit medium declared in
   `manifest.evidence.location` and collects events for the
   current consumer artifact (typical scoping: events from the
   current branch or current PR).
6. **Validate consultation events.** The CI workflow validates
   each event against
   `schemas/consultation-event.schema.json`. Validation failure
   means the agent emitted malformed evidence; the consumer
   investigates the agent prompt's structured-output discipline.
7. **Cross-check events against manifest contract.** For each
   manifest checkpoint with `required-findings: report-and-block`
   or `record-and-block`, the CI workflow verifies that at least
   one event references the checkpoint's `consults.catalogs`,
   `consults.rules`, `consults.mappings`, or
   `consults.decision-frameworks` per the manifest contract.
   Missing required consultation is a substrate-noncompliance
   signal and a closure failure.
8. **Block or pass.** Checkpoints whose `blocking: true` field is
   set produce a CI failure exit when any of steps 4 through 7
   detect noncompliance. Checkpoints whose `blocking: false`
   field is set or unset produce a CI warning (substrate-
   recommended) or a CI pass.

### 4.4 The reference CI workflow

The substrate ships the CI workflow example as a reference file
under the consumer-scaffold examples (location documented in
Section 5). The reference is illustrative GitHub Actions YAML;
consumer CI systems (GitLab CI, CircleCI, Jenkins, custom
orchestration) implement the same contract in their native
syntax. The substrate's contract is on the eight-step sequence
above, not on the GitHub Actions surface.

### 4.5 Pre-commit hook integration

For consumers who choose to perform a subset of the closure
verification before commit rather than at CI time, the substrate
ships a pre-commit hook pattern. The hook runs steps 1, 2, and 4
of the contract (manifest discovery, manifest validation,
static-analysis bindings against L1 rules) on the staged diff.
Steps 5 through 8 (consultation event collection and cross-check)
remain CI-time because they depend on the post-agent-invocation
audit medium that is typically populated outside the developer's
local environment.

The pre-commit hook is substrate-recommended for L1 mechanical
rules where the substrate's bindings produce deterministic results
on the staged diff. The pre-commit hook is not appropriate for L2
semantic or L3 judgmental rules (those require human or AI agent
review at the workflow checkpoints, not the local commit step).

### 4.6 What this section does not specify

The substrate's contract is on the eight-step sequence and the
substrate-default engine selection. The substrate does not
specify:

- Which CI provider the consumer uses
- Where in the consumer's branching strategy the gate runs
  (pre-merge to main, pre-deploy to staging, pre-release to
  production, or other consumer-defined gates)
- How the consumer's CI authenticates to the substrate (vendored
  copy, git submodule, package registry pull, or substrate
  registry resolution)
- How consultation events are routed from the agent runtime to
  the audit medium (the agent runtime is consumer-side; the
  audit medium is consumer-side; the routing is consumer-side)
- Performance characteristics of the gate (the substrate's
  static-analysis bindings have their own performance
  characteristics under OpenGrep; consumer CI sizing is consumer-
  side)

These are consumer choices the substrate's bindings and contract
accommodate without restricting.

## Section 5: Reference implementation pointers

The substrate ships a reference consumer-scaffold instance
demonstrating each obligation. Reference files are illustrative
and live **inside the substrate** at `governance-commons/reference/`.
Consumers copy the reference files out of `governance-commons/reference/`
into their own repositories' integration locations (typically the
repo root for the manifest, the consumer's agent-template directory
for agent prompts, and the consumer's CI workflow directory for the
CI workflow) and adapt them to their
tooling. The reference is not a runtime dependency.

The substrate-internal location for reference files reflects the
substrate's isolation invariant: everything inside
`governance-commons/` is substrate-published content (whether
schema-validated rules, MADRs, mappings, or illustrative
references). Everything outside `governance-commons/` is the
consumer's own integration surface. The substrate does not place
files at consumer-side locations on the consumer's behalf.

The reference manifest:

- **`governance-commons/reference/manifest/governance-manifest.yaml`**.
  Demonstrates a complete manifest covering Obligations 1, 4, 5
  (manifest, evidence, closure). Validates clean against
  `schemas/manifest.schema.json`. Pins to the current commons
  version. Uses the substrate-default `production-grade-baseline`
  profile. Declares four checkpoints
  (`post-spec-drafting`, `post-design`, `post-implementation`,
  `pre-commit`) covering the build-time AI coding framework
  pattern from `manifest-format.md`. Consumers copy this file to
  their own repository root (substrate-recommended location) and
  customize.

The reference agent prompt patterns:

- **`governance-commons/reference/agents/threat-modeling-agent.md`**
  (reference for the post-spec-drafting checkpoint).
- **`governance-commons/reference/agents/implementation-planning-agent.md`**
  (reference for the post-design checkpoint).
- **`governance-commons/reference/agents/code-review-agent.md`**
  (reference for the post-implementation checkpoint).

The three templates demonstrate the slot-filling contract from
Section 3, including all 9 substrate-published slots and the
consultation-events output discipline. Consumers copy these files
to their consumer's agent-template directory and adapt the prose
framing to their tooling.

The reference CI workflow:

- **`governance-commons/reference/workflows/governance-commons-gate.yml`**.
  Demonstrates the eight-step contract from Section 4 in GitHub
  Actions syntax. Consumers copy this file to `.github/workflows/`
  (or the consumer-CI-equivalent path) and adapt to their CI
  provider's syntax.

The reference files do not change the contracts in Sections 3 and
4 of this document. The contracts are authoritative; the reference
files are illustrative. The contracts are versioned with the
substrate (substrate version bumps when the contracts change in
material ways per Article VII); the reference files track the
contracts and are updated whenever the contracts change.

## Section 6: What this document is not

To bound the contract clearly:

- This document is not a runbook. It does not tell a consumer
  how to deploy a CI pipeline, how to author an agent prompt
  from scratch, or how to choose between CI providers. Those are
  consumer-side concerns.
- This document is not a tutorial. The reference manifest at
  Section 5 is illustrative; the substrate's discipline is on the
  contract, not on whether the reference manifest matches any
  given consumer's situation.
- This document is not an implementation. The substrate does not
  ship a CI runner, an orchestrator, an agent runtime, or an
  audit medium. The substrate ships the contracts and the
  schemas; consumers implement.
- This document does not duplicate `manifest-format.md`,
  `consultation-evidence.md`, or `consumption-contract.md`. Where
  those documents are authoritative, this document points to
  them. Where new normative content was needed (Sections 3 and
  4 of this document), this document fills the gap.

## Section 7: Versioning

This document follows the substrate's spec-doc versioning
convention. Material changes to the eight-step CI contract or the
agent prompt injection slot list are versioned. Non-material
changes (editorial corrections, cross-reference updates,
clarifications that do not change the contract) are not versioned.

The contract entered the substrate at substrate-version 0.5.0
(M3 Session 1) at lifecycle-status draft and was promoted to
lifecycle-status stable at substrate-version 0.6.0 (M3 Session 5
close consolidation, 2026-05-30) per the Path A precedent
established at M1 and M2 close.
Stable lifecycle places this contract at Charter
Article IV immutability semantics: material changes (eight-step CI
contract surface, agent prompt injection slot list, manifest
extension obligations) require deprecation cycles rather than
in-place edits; non-material changes follow Charter Article IV
Section 4.2 editorial correction discipline.

## Section 8: Cross-references

- `manifest-format.md` (manifest format specification; Obligation
  1 of this document operationalizes it)
- `consultation-evidence.md` (evidence contract; Obligations 4
  and 5 of this document operationalize it)
- `consumption-contract.md` (bidirectional substrate-consumer
  contract; this document is a downstream operationalization)
- `enforcement-tooling.md` (substrate-default engine selection;
  Section 4 of this document operationalizes the OpenGrep
  selection)
- `substrate-scope.md` (Tier 1 declarative content scope; this
  document is registered as a Tier 1 spec doc per the
  substrate-scope cross-references amendment in this session)
- `architecture-rationale.md` (design rationale background)
- `principles.md` (P1-P12 philosophical foundation; especially
  P3 small grounded requests, which the constitution slicing
  position in Section 3 operationalizes)
- `../CHARTER.md` Article VI (consultation evidence contract;
  this document operationalizes it at the consumer-scaffold
  level)
- `../CHARTER.md` Article VII (compatibility with consumers; the
  substrate-author guarantee in this document follows from
  Article VII Section 7.1)
- `../schemas/manifest.schema.json` (manifest mechanical
  validator)
- `../schemas/consultation-event.schema.json` (evidence event
  mechanical validator)
- `../schemas/binding.schema.json` (the
  substrate's binding schema, consumed by the CI workflow in
  Section 4)
