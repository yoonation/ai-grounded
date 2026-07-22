<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Consumption Contract

This document specifies the obligations and entitlements between
Governance Commons and any consumer that adopts the substrate. The
contract is referenced by Article VII of `CHARTER.md` and binds both
the substrate and its consumers.

This document is the **operational checklist** for the principles in
Article VII. Where the Charter states obligations in principle, this
document states them as concrete things to verify, build, and
maintain.

## Why this contract exists

The substrate provides value only when consumers can reliably depend
on it. The substrate's value erodes when consumers depend on
behaviors that are not contractually promised.

Three failure modes the contract prevents:

- **Silent breaking changes.** A consumer integrated against the
  substrate at version N discovers their integration broken at
  version N+1 because the substrate changed behavior the consumer
  reasonably depended on but that was not contractually guaranteed.
- **Inadvertent fork.** A consumer modifies the substrate locally to
  fit their workflow, accumulates local modifications, and silently
  forks. The consumer no longer benefits from substrate improvements;
  the substrate no longer benefits from the consumer's experience.
- **Substrate creep.** The substrate grows features to serve a
  specific consumer's use case, accumulating dependencies the
  substrate's portability rules forbid.

The contract is bidirectional. The substrate has obligations to
consumers. Consumers have obligations to the substrate. Both sides
have what they must not assume about the other.

## The contract in two sentences

The substrate provides identified, versioned, schema-validated
artifacts under semantic versioning discipline. Consumers integrate
through documented contracts, signal their commons version dependency
explicitly, and respect the substrate's portability and authoring
rules without taking unilateral modifications.

## What the substrate provides (substrate obligations)

The substrate commits to the following. Failure of the substrate to
meet these commitments is a substrate defect addressable under
Charter Article IX.

### Stable identifiers

Every catalog, profile, rule, mapping, decision framework, and schema
has a stable identifier. Once an artifact reaches stable lifecycle
status (per Charter Article VIII), its identifier never changes.
Renumbering, renaming, or re-keying after stable promotion is a
substrate defect.

Consumers reference artifacts by identifier in their manifests, audit
trails, and ADRs with confidence that the references remain valid
across substrate versions within the same major version.

### Schemas for all data formats

The substrate publishes JSON Schema (or equivalent structured schema)
for every data format it produces. Schemas live in
`governance-commons/schemas/`. Consumers validate their integration
against published schemas mechanically.

Schemas covered:

- Concern catalog format (OSCAL with substrate extensions)
- Profile format (OSCAL profile model)
- Mapping format (OSCAL controls mapping model)
- Decision framework format (substrate-defined)
- Consultation evidence event format (semantic; mapping to syntax is
  consumer's choice)
- Manifest format (substrate-defined for consumers that adopt it)

When a schema changes, the substrate publishes migration notes in
`CHANGELOG.md` and increments the commons version per semantic
versioning.

### Documented contracts

The substrate documents every consumer-facing contract in
`governance-commons/spec/`. Contracts currently published:

- `consultation-evidence.md` (Article VI operationalized)
- `consumption-contract.md` (this document; Article VII
  operationalized)
- `extension-contract.md` (Article V operationalized; tailoring
  procedures)
- `rule-lifecycle.md` (Article VIII operationalized; lifecycle
  transitions)
- `catalog-format.md` (catalog authoring format including OSCAL
  extension properties)
- `manifest-format.md` (manifest schema for consumers that adopt
  manifest-driven integration)
- `decision-framework-format.md` (Layer 3 decision-framework format)
- `audit-envelope.md` (the audit envelope; compatible with
  consultation evidence)
- the toolchain registry and selection (how catalog rules bind to enforcement
  tools)

Contracts are versioned with the commons. Breaking contract changes
follow major version increments per Charter Article VIII Section 7.5.

### Semantic versioning discipline

The substrate version (recorded in `governance-commons/VERSION`)
follows semver:

- **MAJOR version increments** when breaking changes occur
- **MINOR version increments** when functionality is added in a
  backwards-compatible manner
- **PATCH version increments** when backwards-compatible corrections
  are made

What counts as a breaking change is enumerated in Charter Article
VIII Section 7.5. The substrate commits to those definitions.

Consumers reference specific commons versions or use version ranges
with confidence about what changes are permitted within a range.

### Migration guidance for breaking changes

When the substrate releases a breaking change, it publishes:

- The breaking change itself in `CHANGELOG.md`
- Migration guidance describing the recommended consumer response
- A minimum deprecation window per Charter Article VIII Section 8.3
  (at least one major version cycle) before the prior behavior is
  removed

Consumers receive advance notice. Substrate releases that break
consumer integrations without migration guidance are substrate
defects.

### Opinionated default profile

The substrate provides an opinionated default profile
(`production-grade-baseline`) per Charter Article V Section 5.2.
Consumers that need no tailoring adopt the default profile and
inherit the substrate's stance.

The default profile is itself versioned, schema-validated, and
subject to the same lifecycle and migration discipline as other
substrate content.

### Industry and use-case profiles

The substrate provides additional profiles for common industry tilts
(financial services, healthcare, regulated AI, etc.) and common use
cases per Charter Article V Section 5.3. These inherit from the
default profile and apply industry-specific modifications.

Consumers in covered industries adopt the relevant profile directly.
Consumers in industries not yet covered may author their own profile
consumer-side per Article V Section 5.4 and propose it for inclusion
per Article II procedures.

### Tooling that is consumer-agnostic

The substrate provides utilities (validators, profile resolvers,
catalog generators) in `governance-commons/tooling/`. These utilities
operate on substrate content and emit consumer-agnostic outputs.

Tooling that requires consumer-specific assumptions (specific
directory layouts, specific runtime contexts, specific framework
machinery) does not live in the substrate. Consumers build such
tooling consumer-side.

## What the substrate does not provide (consumer must build)

The substrate explicitly does not provide the following. Consumers
must build these themselves or adopt third-party solutions.

### Runtime enforcement of commons content

The substrate provides rule definitions. Consumers provide runtime
mechanisms that read rules, observe consumer behavior, and emit
findings.

For build-time consumers: this typically means linters, SAST tools,
custom analyzers, and AI agents that consult catalogs during
workflow checkpoints.

For runtime consumers: this typically means policy decision points,
policy enforcement points, and observability infrastructure that
applies rules at request time.

The substrate is not a runtime. Consumers are.

### Storage for consultation evidence

The substrate specifies what consumers must record (per
consultation-evidence.md). Consumers provide append-only storage,
tamper-evident integrity, and retention.

The substrate makes no assumption about consumer storage. The
substrate's tooling for evidence verification (when built) operates
on the contract's data shape and adapts to consumer storage via
defined adapters.

### Workflow integration with specific consumer architectures

The substrate is consumer-agnostic. Consumers integrate the substrate
into their specific workflow. The substrate does not provide:

- Build pipeline integration for any specific CI/CD platform
- Editor integration for any specific IDE
- Framework integration for any specific spec-driven development
  framework, agent framework, or coding assistant
- Cloud provider integration for any specific cloud
- Identity integration for any specific identity provider

Consumers build these integrations consumer-side.

### Project-level operational rules

The substrate governs how the substrate functions. Consumers govern
how their projects function. Consumer-side constitutions, project
constitutions, framework constitutions, organizational governance
documents are consumer responsibilities.

The substrate's Charter does not preempt consumer-side governance.
The Charter applies only within the substrate's scope (Article I
Section 1.1).

### Authority over consumer codebases

The substrate provides rules. Consumers decide how to apply them. A
consumer that finds a substrate rule inappropriate for their context
excludes it via profile (per Charter Article IV Section 4.4 and
Article V).

The substrate does not enforce itself. Consumers enforce the rules
they adopt.

### Guarantees about specific tools' presence or behavior

The substrate references specific tools by name in tool bindings
(e.g., Semgrep, Cedar, Trestle) but does not bundle these tools, does
not guarantee their availability in consumer environments, and does
not guarantee their continued behavior across consumer-side updates.

Consumers ensure tool availability and behavior. Tool changes that
break the substrate's tool bindings are addressed in
`CHANGELOG.md` and may trigger migration guidance per substrate
breaking change procedures.

## What consumers must provide (consumer obligations)

Consumers that adopt the substrate commit to the following. Failure
to meet these obligations is a consumer integration defect, not a
substrate defect.

### Explicit commons version dependency

Consumers declare which commons version they integrate against.
Declaration is recorded somewhere the consumer's audit medium can
reference. Acceptable declaration mechanisms:

- Git submodule pinned to a specific commit
- Package manifest dependency with explicit version constraint
- Documented reference in consumer's constitutional or governance
  documents
- Audit event field (`commons_version` per consultation evidence
  contract)

Implicit dependencies (consumers using "whatever is current") do not
satisfy this obligation. Implicit dependencies create silent breakage
when the substrate evolves.

### Profile selection

Consumers select a profile (the default profile if no tailoring is
needed, an industry profile if applicable, or a consumer-side profile
that inherits from a substrate profile). The selected profile is
declared explicitly.

Consumers that consult substrate content without an active profile
selection are operating without a defined scope. The substrate
considers this a consumer defect.

### Workflow integration

Consumers wire substrate consultation into their workflow at
appropriate decision points. The specific mechanism is consumer
choice; consultation must actually occur and must be recorded per the
consultation evidence contract.

A consumer that "uses the substrate" but never consults catalogs
during work is not actually using the substrate. The substrate may
provide reference material in this case; it provides no governance
integrity.

### Audit medium

Consumers provide an audit medium that satisfies the consultation
evidence contract (append-only, tamper-evident, retentive,
verifiable). The medium is consumer choice; the requirements are
specified per the contract.

### Verification mechanism

Consumers verify that consultation actually occurred per the
consultation evidence contract (Section 6.5 of the Charter,
operationalized in `consultation-evidence.md`). Verification is a
consumer responsibility regardless of which audit medium is chosen.

### Provenance for consumer-side artifacts

Consumers that author consumer-side artifacts (custom catalogs,
custom profiles, custom manifests, project ADRs) record provenance
for those artifacts per the discipline in Charter Article II Section
2.2.

The substrate cannot enforce this on consumer-side artifacts but
considers the discipline part of the contract. Consumers who skip
provenance on their own artifacts have weakened governance even
though their substrate consumption is technically compliant.

### Respect for portability rule

Consumers do not modify substrate content in place. The substrate's
`PORTABILITY.md` discipline applies to any consumer-side
modifications: substrate content remains separable from consumer
content with zero cross-references from substrate to consumer.

Consumers who need substrate modifications propose them via Charter
Article II procedures (for inclusion in the substrate) or layer them
consumer-side via profiles and custom catalogs.

A consumer that maintains a local fork of substrate content has
forked per Charter Article IX Section 9.3 and is no longer
integrating with Governance Commons.

### Respect for AI authority limits

Consumers that use AI to assist with substrate-related work
(authoring proposals, validating content, generating profiles, etc.)
respect AI authority limits per Charter Article III. AI proposes;
humans approve. The consumer's audit medium records AI assistance.

## What consumers must not assume (consumer obligations, negative)

The substrate explicitly disclaims the following. Consumers that
assume any of these create their own defects.

### That non-stable artifacts will become stable

Draft-status artifacts (per Charter Article VIII Section 8.2) may
change or be retired without the deprecation window that stable
artifacts enjoy. Consumers should not integrate against draft
artifacts in production workflows unless they accept the integration
risk.

### That deprecated artifacts will remain available indefinitely

Deprecated artifacts remain available for at least one major version
cycle, then may be retired. Consumers using deprecated content are
expected to migrate within the deprecation window.

### That the substrate guarantees behavior of bound tools

The substrate binds rules to enforcement tools (Semgrep for L1, etc.)
but does not guarantee those tools' availability, behavior, or
continued maintenance. Consumers verify tool behavior themselves.

### That substrate-suggested workflow integrations will fit any consumer

The substrate's documentation includes architecture mappings (e.g.,
in consultation-evidence.md) as non-normative guidance. Consumers
adapt the mappings to their architecture. The mappings are
illustrative, not prescriptive.

### That the substrate will evolve to serve any specific consumer

The substrate evolves per its own roadmap and the contributions
accepted via Charter Article II procedures. Consumers may propose
substrate evolution but cannot rely on it. Consumers whose needs
diverge from the substrate's direction adapt consumer-side or fork
per Charter Article IX Section 9.3.

### That substrate identifiers are unique across all consumers

Substrate identifiers (rule IDs, catalog IDs, profile IDs) are unique
within the substrate. Consumers that author consumer-side artifacts
must namespace their identifiers to avoid collision with future
substrate additions.

Recommended pattern: consumer-side identifiers prefixed with the
consumer's namespace (e.g., `acme-corp.authentication.password-hashing` for an
ACME-Corp-specific auth rule).

## Boundary cases

This section addresses common ambiguities at the substrate/consumer
boundary.

### A consumer wants a substrate rule with different parameters

The rule's parameters are tailorable per Charter Article IV Section
4.3. The consumer modifies parameters in their profile. The substrate
rule remains unchanged. Both consumer and substrate are satisfied.

### A consumer wants a substrate rule with different intent

The rule's intent is immutable per Charter Article IV Section 4.2. If
the consumer's desired intent differs from the substrate's, the
consumer authors a consumer-side rule with a different identifier and
different intent. The substrate rule remains unchanged. The consumer
may propose the new rule for substrate inclusion per Article II.

### A consumer finds a substrate rule incorrect

The consumer reports the defect via the substrate's contribution
process (currently: substrate maintainer's communication channel; in
future: formal issue tracker). The substrate evaluates the report and
either:

- Confirms the defect and addresses it through Article II authoring
  procedures with a new version
- Disagrees with the report and explains why

In the interim, the consumer may exclude the rule via profile per
Article V Section 5.5 with rationale recorded.

### A consumer needs a substrate rule the substrate does not have

The consumer authors the rule consumer-side, namespaced per the
boundary case above. The consumer may propose the rule for substrate
inclusion per Article II.

The substrate makes no commitment to accept proposed rules. Inclusion
is at substrate maintainers' discretion per Article II Section 2.4
review discipline.

### A consumer's workflow requires substrate consultation at a point the substrate did not anticipate

The substrate is workflow-agnostic. Consumers consult at any point
their workflow requires. Consultation evidence is recorded per the
contract. No substrate change is needed.

### A consumer wants to integrate substrate content into a non-governance use case

The substrate is licensed under Apache 2.0 (see repository `LICENSE`)
and may be reused under those terms. Non-governance reuse is
permitted by license but is not "consumption" in the sense this
contract defines. Such reuse does not invoke the contract's
obligations.

## Substrate-side enforcement

The substrate cannot enforce most consumer obligations mechanically.
Consumers are trusted to honor the contract. The substrate's
recourse for consumer non-compliance is reputational, not technical:

- A consumer that claims governance integrity without satisfying the
  contract makes a false claim that audit can disprove
- A consumer that integrates against the substrate without declaring
  version dependency creates risk that substrate evolution will
  break their integration
- A consumer that modifies the substrate locally has forked per
  Article IX Section 9.3 and is not using Governance Commons

The substrate provides clarity about what compliance means. Consumers
choose whether to comply.

### What the substrate enforces mechanically

Within the substrate's own content authoring, the substrate enforces:

- Portability rule (no references from substrate to consumer-side
  content; mechanically checked per `PORTABILITY.md`)
- Schema validation (catalog content validates against published
  schemas; mechanically checked at substrate authoring time)
- Lifecycle state transitions (artifacts move through states per
  defined procedures; tracked in `CHANGELOG.md`)
- Provenance presence (substrate artifacts include provenance per
  Article II Section 2.2)

These enforcements protect substrate integrity. They do not extend to
consumer-side artifacts.

## Versioning of this contract

This contract is versioned with the commons. Changes follow Charter
Article VIII versioning discipline.

Current contract version: **0.1.0** (matches commons version)

### Breaking changes

The following changes are breaking under semver:

- Adding a new consumer obligation
- Removing a substrate obligation
- Changing the meaning of an existing obligation

### Non-breaking changes

The following are non-breaking:

- Adding a new substrate obligation
- Removing a consumer obligation
- Clarifying existing obligations without changing meaning
- Adding boundary cases or examples
- Documenting previously-implicit behavior

## What this contract is not

To clarify boundaries:

- This contract is not a license. Licensing is governed by the
  repository's `LICENSE` file (currently Apache 2.0).
- This contract is not a service-level agreement. The substrate is
  open content; substrate maintainers provide no operational SLA.
  Migration guidance and deprecation windows are quality-of-service
  commitments but not legally binding.
- This contract is not a support agreement. Consumers receive the
  substrate as-is; substrate maintainers may answer questions and
  accept contributions per Article II but are not obligated to
  provide support.
- This contract is not exhaustive. Specific consumer architectures
  may require additional considerations. Consumers extend the
  contract with their own consumer-side rules; the substrate's
  contract is the minimum.

## Closing

The consumption contract is the bidirectional understanding between
substrate and consumer. Both sides have obligations. Both sides have
limits. Neither side may unilaterally redefine the relationship.

When consumers and substrate disagree about contract interpretation,
resolution mechanisms are:

- Discussion via substrate's contribution channels
- Charter amendment per Article IX if the contract itself needs
  revision
- Consumer-side fork per Article IX Section 9.3 if values diverge
  irreconcilably

The contract exists so that consumers can integrate against the
substrate with confidence and the substrate can evolve without
breaking consumers in surprise. Both outcomes require explicit rules.
This document is the explicit rules.
