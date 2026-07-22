<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Substrate Scope

This document specifies what the substrate is, what it contains, what
it deliberately excludes, and how deep individual concern catalogs go.
It is referenced by Charter Article VII (compatibility with consumers)
and by catalog authoring documentation in `../catalogs/`.

This document is normative. Substrate authors follow its rules.
Consumers integrating against the substrate use it to understand what
they can rely on the substrate to provide and what they must build
themselves. AI agents reading the substrate consult it to understand
boundaries before acting.

## Why this document exists

The substrate's surface area is large enough to invite scope creep. A
catalog might grow to thirty rules when ten would suffice. A
substrate utility might grow to a runtime when configuration would
suffice. A tool binding might grow into a workflow engine when a
pattern would suffice.

This document establishes the rules that prevent scope creep. They are
written so that both human authors and AI agents consulting the
substrate have an unambiguous reference for what belongs and what does
not.

## What the substrate is

The substrate is a body of governance content, not a runtime. It
describes what good engineering looks like and provides patterns
consumers enforce. It does not execute, decide, or act.

The substrate is to engineering practice what NIST SP 800-53 is to
information security: a standards document. NIST does not ship code
that implements AC-3 (Access Enforcement). NIST describes what AC-3
requires. Implementation is up to consumers. The substrate works the
same way.

This framing is what keeps the substrate portable across consumers
and stable across years. If the substrate executes anything, it
inherits the consumer's runtime constraints. If the substrate decides
anything, it inherits the consumer's policy authority. If the
substrate acts on anything, it inherits the consumer's data and
identity. The substrate describes; consumers act. The separation is
what makes the substrate reusable.

## Three tiers of substrate content

All substrate content falls into one of three tiers.

### Tier 1: Declarative content (the substrate's bulk)

Pure description. No execution. Read by consumers (human or AI) who
then act on what they read.

Includes:

- The Charter (`CHARTER.md`)
- Specification documents (`spec/*.md`)
- READMEs across the substrate
- Concern catalogs (`catalogs/concerns/`)
- Threat catalogs (`catalogs/threats/`)
- Compliance catalogs (`catalogs/compliance/`)
- Substrate profiles (`profiles/`)
- Cross-taxonomy mappings (`mappings/`)
- Decision frameworks (`decision-frameworks/`)
- Examples supporting Layer 2 rules (`examples/`)
- Schemas validating substrate content (`schemas/`)

Tier 1 is what the substrate IS. The Charter and the catalogs are the
substrate's reason for existing.

### Tier 2: Pattern artifacts (enforcement hints)

Enforcement leverage the substrate ships for consumer-installed tools
to execute. The substrate ships the binding and the tool selection; the
consumer installs and runs the tool.

Includes:

- Capability-bound bindings (each rule's co-located `binding.yaml`)
  naming the rule's mechanical gate (for example `sast`, `secrets`,
  `lint`). The toolchain registry and selection (`../toolchain/`)
  resolve each gate to a concrete OSS tool (OpenGrep for SAST, gitleaks
  for secrets, Ruff and ESLint for lint, and so on). The substrate ships
  the gate and the selection, not the tool's rule set: the consumer
  installs the tool and supplies its maintained rules (for example
  cloning the OpenGrep rule set).
- Cedar policy fragments (`policies/`)

Tier 2 is enforcement leverage. The substrate's Layer 1 rules describe
mechanical checks; the binding names the gate and the toolchain selects
the OSS tool that executes those checks. The tools (OpenGrep, gitleaks,
Cedar, Ruff, ESLint, and the rest of the registry) are installed by
consumers, not shipped by the substrate.

The distinction matters. The substrate authors no executable behavior
and ships no tool rule sets. It declares which mechanical gate a rule
belongs to and which OSS tool the gate resolves to; the consumer's
installed tools do the recognizing and applying.

### Tier 3: Substrate-native utilities (deferred, trace amount)

Code that operates on substrate content and emits consumer-agnostic
outputs. Lives in `governance-commons/tooling/`. Small in scope.

Utilities:

- `assemble/`: validates catalogs and rules against schemas and
  assembles the published catalog form
- `toolchain/`: audits the tool registry and capability selection
- `floor-generator/`: generates the consumer enforcement floor
  (pre-commit, CI, and the L2 review manifest) from the resolved
  toolchain
- `profile-resolver/`: resolves profile inheritance to flat form
  (skeleton)
- `mapping-coverage-reporter/`: identifies gaps between catalogs
  (skeleton)
- `tailoring-agent/`: AI-assisted profile tailoring (skeleton, future)

Tier 3 is for substrate self-maintenance. Each utility:

- Operates on substrate content (not consumer content)
- Emits consumer-agnostic outputs (not framework-specific behavior)
- Is small (hundreds of lines, not thousands)
- Could be replaced by consumer-side tooling if the consumer prefers

Tier 3 began as deferred skeletons. As substrate content stabilized,
the validation, assembly, toolchain-audit, and floor-generation tools
were implemented (`assemble/`, `toolchain/`, `floor-generator/`); the
remaining utilities stay skeletons until a consumer need is concrete.

## Categorically outside the substrate

The following never live in the substrate. Including any of them is a
substrate defect.

- **AI agents that consult catalogs.** Agents live consumer-side. The
  substrate publishes the consultation evidence contract; consumers
  implement agents that satisfy it.
- **Runtime enforcement systems.** Policy decision points, policy
  enforcement points, runtime middleware all live consumer-side. The
  substrate provides rules and patterns; consumers run them.
- **Workflow engines.** Spec-driven development workflows, CI/CD
  pipelines, build orchestrators all live consumer-side. The
  substrate's manifest format declares what should be consulted
  where; the workflow that does the consulting is consumer's.
- **Application code.** Any code that performs business logic, handles
  user requests, processes data, or interacts with the world lives
  consumer-side. Always.
- **Production-grade execution of any kind.** If something runs in
  production handling user traffic, it is consumer code.
- **Long-running processes.** The substrate has no daemons, no
  servers, no message queues. Tier 3 utilities are batch tools that
  start and exit.
- **State storage for consumer data.** Consultation evidence is stored
  consumer-side per Charter Article VI. The substrate provides
  contracts and formats; consumers provide storage.
- **Credentials, secrets, or identity material.** The substrate's
  Cedar policies and bindings describe patterns; they contain no
  actual credentials.

If a contributor proposes adding anything from this list to the
substrate, the proposal is rejected. If the substrate appears to need
any of these, the appearance reveals a consumer-side gap, not a
substrate gap.

## The substrate-author rules

Five normative rules for anyone authoring substrate content. AI agents
proposing substrate changes follow these rules. Human authors follow
these rules. Reviewers verify these rules.

### Rule 1: Authors do not write code in the substrate

Substrate content is markdown, YAML, JSON, and OSCAL. Not Python, not
TypeScript, not Go, not any other application language. The
exceptions are: Tier 2 pattern artifacts (which are tool
configurations, not code) and Tier 3 utilities (which are constrained
to substrate self-maintenance).

If an author finds themselves about to write a function that implements
behavior, they are authoring consumer-side content in the wrong
repository. Stop and reassign the work.

### Rule 2: Authors do not implement what they describe

The substrate describes "authentication middleware required on
authenticated endpoints." The substrate does not ship authentication
middleware. The substrate describes "no credentials in URLs." The
substrate does not ship a URL sanitizer. The substrate's job ends at
the rule and its pattern artifact.

This rule prevents the most common scope creep: authors who care about
a rule wanting to make the rule "useful" by also shipping the
implementation. The implementation is consumer's job.

### Rule 3: Authors match concern depth to intrinsic complexity

Some concerns are intrinsically complex (authentication, error
handling, performance). They warrant deeper catalogs. Other concerns
are intrinsically narrower (dependency management, cost model
selection). They warrant shallower catalogs. The depth guidance in
the next section formalizes this.

Authors do not pad shallow concerns to feel comprehensive. Authors do
not truncate deep concerns to feel manageable. Depth matches the
concern, not the author's mood.

### Rule 4: Authors prefer importing authoritative standards over reauthoring

When NIST publishes 800-53, the substrate imports it via Trestle into
`catalogs/compliance/`. The substrate does not reauthor the controls.
When OWASP publishes ASVS 5.0, the substrate references it from
concern rules; the substrate does not reproduce the requirement text.

Substrate-original content adds value only where authoritative
standards have gaps or where the substrate's three-layer model
reorganizes content meaningfully. Reauthoring what already exists
elsewhere is busy work that creates maintenance burden without value.

### Rule 5: Authors stop at the boundary

The substrate boundary is the line between describing and doing.
Authors stop at the line. If an author finds themselves on the wrong
side of the line, they back up and reframe their contribution.

Common scope-creep patterns the boundary catches:

- A catalog rule that includes implementation steps. Trim to the rule
  itself; implementation lives consumer-side.
- A tool binding that includes runtime configuration. Trim to the
  pattern; runtime configuration is consumer's.
- A utility that orchestrates a consumer workflow. Reject; workflows
  live consumer-side.
- A profile that names specific consumer infrastructure. Reject;
  profiles tailor catalog selections, not consumer deployment.

## Concern depth guidance

Concerns vary in depth based on intrinsic complexity. The substrate
categorizes concerns into three depth tiers. This categorization is
normative for authoring: concerns in each tier target the rule count
range below.

### High depth (10-15 rules)

Concerns with dense industry standards, broad attack surface, or
high consumer impact. These concerns warrant comprehensive catalogs.

Concerns at this depth:

- `authentication` (~15 rules; OWASP ASVS Chapter 6, NIST 800-63B-4)
- `authorization` (~12 rules; OWASP ASVS Chapter 7, NIST 800-53 AC-*)
- `input-validation` (~12 rules; OWASP ASVS Chapter 5)
- `error-handling` (~10 rules)
- `logging` (~10 rules; OWASP ASVS Chapter 11, OWASP Top 10 A09)
- `supply-chain` (~12 rules; SLSA v1.1, NIST SP 800-218 SSDF v1.1, OWASP ASVS Chapter 14, OWASP Top 10 CI/CD Security Risks, EU Regulation 2024/2847 (Cyber Resilience Act), in-toto attestation framework, Sigstore)
- `performance-database` (~12 rules)
- `responsible-ai` (~12 rules; NIST AI RMF, EU AI Act)
- `agentic-systems` (~12 rules; OWASP Agentic Security Initiative (ASI) Top 10, OWASP Agentic Skills Top 10, MAESTRO (CSA), NIST AI RMF, the NIST AI agent standards work, and the agent-security concepts the substrate's threat catalogs operationalize: goal integrity, tool-use authorization and least privilege, autonomy and action bounds, human-in-the-loop action gating, delegation-chain accountability, agent-memory integrity, and multi-agent trust)
- `infrastructure-misconfiguration` (~12 rules; CIS Benchmarks (AWS / Azure / GCP Foundations, Kubernetes), NIST SP 800-53, NIST SP 800-190 (container security), CSA Cloud Controls Matrix, MITRE ATT&CK Cloud Matrix, the cloud providers' Well-Architected / security-pillar guidance, and the open IaC scanner rule corpora that operationalize them: Checkov, Trivy (formerly tfsec), terrascan, KICS, tflint, kube-linter)

The `infrastructure-misconfiguration` concern shares adjacency with two
already-authored concerns and is kept structurally distinct from both.
It is distinct from `dependency-management` (low depth, 5 rules):
`dependency-management` governs application package selection, manifest
and lockfile pinning, and vulnerability scanning of upstream packages;
`infrastructure-misconfiguration` governs the *security and correctness
of the infrastructure resource configuration declared in IaC*
(encryption at rest, network exposure, public accessibility, IAM grants,
audit-log enablement, IaC state-backend hardening, deletion protection,
provider and module version pinning). Where the two meet (IaC provider
and module version pinning is the IaC-native expression of the pinning
principle), `infrastructure-misconfiguration` cross-references
`dependency-management` rather than restating it. It is also distinct
from `supply-chain` (high depth, 12 rules): `supply-chain` governs the
provenance, attestation, signing, and SBOM discipline of the *artifacts
a build produces and consumes*; `infrastructure-misconfiguration` governs
the *declarative configuration of the infrastructure those artifacts run
on*. A signed, attested container image (supply-chain) can still be
deployed into a publicly-exposed, unencrypted, over-permissioned
environment (infrastructure-misconfiguration); the two concerns guard
different failure surfaces. Concern-boundary documentation is authored
in all three catalogs at authoring time.

The `supply-chain` concern shares substantial adjacency with the
`dependency-management` concern (low depth, 5 rules). The two concerns
are kept structurally distinct: `dependency-management` governs
upstream-package selection, pinning, and vulnerability scanning
against advisory databases; `supply-chain` governs artifact provenance,
attestation, signing, build-environment integrity, and SBOM
discipline. Concern-boundary documentation is authored in both
catalogs at authoring time.

The `agentic-systems` concern is introduced as a high-depth concern by
M5 amendment (2026-06-02) and is kept structurally distinct from
`responsible-ai`, with which it shares the AI subject matter but not the
failure surface. `responsible-ai` governs the *properties of a model or
AI system and its societal impact*: fairness, transparency and
disclosure, data governance for training and evaluation, explainability,
human review and contestability of automated decisions, evaluation
before deployment, model provenance, and AI record-keeping, anchored to
the NIST AI RMF and the EU AI Act. `agentic-systems` governs the
*security of an autonomous control loop that takes actions*: goal
integrity under adversarial input, tool-use authorization and least
privilege, autonomy and action bounds, human-in-the-loop gating of
consequential actions, delegation-chain accountability across multi-agent
systems, agent-memory integrity, and the auditing of agent decisions,
anchored to the OWASP Agentic Security Initiative Top 10, the OWASP
Agentic Skills Top 10, and MAESTRO. The seam is system-property versus
control-loop-security: whether a model decision is fair, explained, and
contestable is a `responsible-ai` question, while whether an agent can be
steered into calling a tool it should not, exceed its authority, or act
without a required human gate is an `agentic-systems` question. The two
concerns share the human-oversight subject and cross-reference at it
rather than restating: `responsible-ai` owns the oversight and
contestability of a *decision or output*, `agentic-systems` owns the
human gate on a consequential *action*. Concern-boundary documentation is
authored in both catalogs at authoring time. The OWASP Agentic Skills Top
10 threat catalog and its mapping, also authored in M5, bind to the
`agentic-systems` concern rules.

### Medium depth (6-10 rules)

Concerns with established practices but less density, or concerns
where substrate opinionation has narrower scope.

Concerns at this depth:

- `code-organization`
- `observability`
- `reliability`
- `testing-strategy`
- `privacy`
- `secrets-management`
- `monitoring-alerting`
- `data-classification`
- `performance-caching`

### Low depth (3-6 rules)

Concerns where best practice is narrow, substrate value-add is
limited, or the consumer-side variation is wide enough that few rules
apply universally.

Concerns at this depth:

- `dependency-management`
- `cost-model-selection`
- `feature-flags`
- `configuration-management`
- `backup-recovery`
- `documentation`

### Concerns not yet classified

Concerns that emerge after this document is authored are classified
when first scoped for authoring. The classification is recorded in
this document via an amendment per Charter Article IX or via this
document's own minor version increments.

### Depth is not a quality measure

A low-depth concern is not inferior to a high-depth concern. Cost
model selection at five rules can be more important to a specific
consumer than authentication at fifteen rules. Depth reflects
intrinsic complexity, not importance.

A high-depth concern with sloppy rules is worse than a low-depth
concern with sharp rules. Quality always supersedes depth.

## Substrate size estimation

This section is non-normative. It exists to set expectations about
the substrate's eventual size for maintenance planning.

Realistic substrate size at maturity:

- Tier 1 concerns (16 planned): 16 × ~9 rules average = ~140 rules
- Tier 1+2 concerns (31 plausible): 31 × ~9 rules average = ~280 rules
- Long-term universe (40 max): 40 × ~9 rules average = ~360 rules

Plus design pattern catalogs (~80 rules across SOLID, GoF, Clean
Code, Fowler smells), plus threat catalogs (~40 rules across OWASP
LLM Top 10, OWASP Agentic ASI, MITRE ATLAS, STRIDE), plus compliance
catalog imports (which are not authored by the substrate and do not
count toward the substrate's maintenance burden).

For comparison:

- NIST SP 800-53: 1200+ controls maintained by a NIST team
- OWASP ASVS 5.0: 280+ requirements maintained by a community
  working group
- CWE: 900+ weaknesses maintained by MITRE

The substrate at 250-360 substrate-authored rules is comparable to
OWASP ASVS in size and sustainable for a small maintainer group with
quarterly review cadence for standards tracking and annual review
cadence for substrate-native content.

## How AI agents consult this document

This section is non-normative guidance for AI agents traversing the
substrate.

When an AI agent encounters a proposal for new substrate content, it
consults this document to verify:

- The proposed content matches a tier (Tier 1, Tier 2, or Tier 3)
- The proposed content does not fall under "categorically outside"
- The proposed content follows the five author rules
- The proposed depth matches the concern's classification (or
  triggers a depth-classification amendment)

If any check fails, the AI agent flags the proposal for substrate
maintainer review before proceeding. The AI agent does not
unilaterally accept or reject; the human substrate maintainer
decides per Charter Article III Section 3.2.

## Cross-references

- `../CHARTER.md` Article VII (what the substrate provides; this
  document operationalizes Article VII Section 7.1 and 7.2)
- `../CHARTER.md` Article II (authoring discipline; this document
  operationalizes the five substrate-author rules)
- `../spec/principles.md` (P1-P12 philosophical foundation)
- `../spec/architecture-rationale.md` (design rationale; this document
  is the normative companion)
- `../spec/consumer-scaffold.md` (consumer scaffold contract;
  unifies manifest-format.md, consultation-evidence.md, and
  consumption-contract.md with normative additions for agent
  prompt injection patterns and CI workflow integration; M3
  Session 1 addition)
- `../catalogs/concerns/README.md` (concern catalog orientation;
  references this document for depth guidance)
- `../catalogs/README.md` (catalog kinds overview)
- `../profiles/README.md` (profile orientation)
- `../tooling/toolchain/README.md` (tool binding model: registry, selection, gates)

## Versioning

This document is versioned with the commons. Changes follow Charter
Article VIII versioning discipline.

Current document version: **0.1.0** (matches commons VERSION)

Changes to the five author rules, the categorically-outside list, or
the depth tier definitions are material and trigger minor version
increments at minimum. Adding new concerns to depth classifications,
clarifying language, or adding examples is non-breaking.

Material changes to substrate scope require Charter amendment per
Article IX in addition to this document's update.

## Closing

This document is the substrate's answer to the question "how do we
keep this from growing into something it shouldn't be?" The five
rules and the depth guidance are the answer. Authors consult them
before authoring. Reviewers verify them before merging. AI agents
respect them before proposing.

The substrate's value comes from being focused. A substrate that
tries to be everything ends up being nothing in particular. The
substrate that describes well and stops at the boundary is the
substrate worth consulting.
