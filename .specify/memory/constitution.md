# Project Constitution

This constitution establishes the immutable principles that govern all
development work in this project. It is the highest-precedence document
in the spec-driven workflow. Specifications, plans, tasks, and code all
defer to the constitution.

This constitution is read by every spec-kit phase
(`/speckit-constitution`, `/speckit-specify`, `/speckit-plan`,
`/speckit-tasks`, `/speckit-implement`, `/speckit-analyze`,
`/speckit-clarify`) and by every agent in `.claude/agents/`. Any
deviation from these principles requires an ADR
(`docs/decisions/ADR-NNN-*.md`) with explicit reasoning.

This document does not duplicate the principles in
`governance-commons/spec/principles.md`. That document defines the
philosophical principles of the governance framework itself (P1-P12).
This document defines the **operational** rules for how work happens
in this specific project.

## Nature of this document

This constitution is to ADRs what a written constitution is to case
law. The constitution states principles. ADRs interpret principles for
specific situations. Together they form the rule set; neither stands
alone.

The constitution covers what is stable: how work happens, what defaults
protect production, what discipline applies to AI-assisted code, what
loop-closure requires. ADRs cover what is contextual: which database
this feature uses, which threat is accepted given the cost of
mitigation, why a given anti-pattern is justified for a specific case.

When an article seems to conflict with reality, exactly one of three
resolutions applies: (a) the situation is foreseen and an ADR records
the principled exception, (b) the situation reveals a gap in the
constitution that warrants an amendment per Article VII, or (c) the
situation reveals work that should not proceed in its current form. The
wrong resolution is to silently bypass the principle.

The Foundational traditions section near the end of this document names
the engineering bodies of work each Article draws from. When AI agents
or human contributors implement work governed by this constitution,
those traditions are the operational vocabulary for translating
principles into stack-specific practice.

## Article I: Spec Discipline

### Section 1.1 - Specs are the source of truth

Specifications, not code, are the primary artifact. Code is generated
from specs and verified against them. When code and spec diverge, the
spec is canonical; code is updated to match or the spec is updated
with an ADR explaining the change.

### Section 1.2 - No implementation without a spec

Every feature, every non-trivial change, begins with a spec. The spec
captures intent, constraints, and acceptance criteria before any code
is written.

Exceptions, all requiring no spec:

- Single-line fixes (typos, dependency bumps, formatting)
- Exploratory spikes explicitly marked as throwaway
- Operational hotfixes (with retroactive spec + ADR within 48 hours)

### Section 1.3 - Specs precede planning

`/speckit-specify` runs first. `/speckit-plan` only runs after a spec
exists and has been clarified via `/speckit-clarify`. Skipping
clarification requires an explicit reason in the plan.

### Section 1.4 - All artifacts version-controlled

Specs, plans, tasks, ADRs, threat models, challenge documents,
review documents, evaluation sets, and event logs all live in the
repository under version control. Nothing lives only in chat history
or local notes.

## Article II: Engineering Standards

### Section 2.1 - Exact version pinning everywhere

No `latest` Docker tags. No floating dependency versions. No "use the
default" runtime. Every dependency, runtime, container image, and
build tool has an exact version. Pin Kubernetes versions, Terraform
versions, Python versions, Node versions explicitly.

Rationale: reproducibility. The same spec at commit X must produce
the same artifact six months later.

### Section 2.2 - ADRs are pre-build gates, not post-build documentation

Architectural decisions are recorded as ADRs **before** implementation,
not after. An ADR captures:

1. Context (the situation requiring a decision)
2. Decision (what was decided)
3. Consequences (what becomes harder or impossible)
4. Alternatives Considered (what was rejected and why)

ADRs live at `docs/decisions/ADR-NNN-short-title.md`.

### Section 2.3 - Defaults that protect production

Code defaults must be safe for production:

- Errors fail closed, not open
- Timeouts on every external call
- Input validation at every system boundary (expanded in Section 5.6)
- Logging excludes sensitive data (per Section 2.6)
- Configuration is explicit, not inferred
- Behavior under partial failure is defined
- Resource ownership is explicit: RAII in C++, try-with-resources in
  Java, `using` in C#, `with` in Python, `defer` in Go, scope-bound
  lifetimes in Rust, IDisposable patterns generally. No leaked file
  handles, sockets, locks, transactions, allocations, or goroutines.
- Memory safety is the default. Languages or constructs that permit
  unsafe memory access (C, C++, `unsafe` Rust, `unsafe` C#, JNI, FFI
  boundaries, manual pointer arithmetic) require explicit justification
  per unsafe region and are reviewed by security-reviewer.

### Section 2.4 - Test discipline

Tests verify the spec, not the implementation. A test that passes
only because it mirrors the implementation's quirks does not satisfy
this requirement.

Every feature has:

- Unit tests for individual components
- Integration tests for interactions
- Contract tests at every service-to-service boundary
- At least one negative-path test for every happy path

Tests are written close to (or before) the code they verify, in the
Red-Green-Refactor cycle. Tests are deterministic; flaky tests are
either fixed within one sprint, quarantined with an open issue, or
deleted. There is no third "skip and ignore" state.

Test data is realistic but never includes real PII, real production
credentials, or real customer records.

### Section 2.5 - Anti-pattern resistance

The following are forbidden without an ADR. The list is non-exhaustive
and stack-neutral; language-family-specific anti-patterns extend this
list in `governance-commons/playbooks/` (e.g., Java inheritance depth,
JavaScript loose equality, C++ raw owning pointers, Terraform
duplicate-state-key resources, React unnecessary effect chains).

- Hidden mutable state shared across module or process boundaries
- "God" units of any kind: god objects, god functions, god files, god
  Terraform modules, god Kubernetes manifests, god configuration files
- Magic numbers and magic strings; use named constants or configuration
- Silent failures that do not log, surface, or signal upward
- Catch-all error handlers that neither re-raise nor structured-log;
  applies equally to exception-based languages (try/catch) and to
  result-based languages (errors as values, Result types, Either types)
- Premature abstraction (rule of three; abstract on the third
  occurrence, not the second)
- Premature optimization without profiler or measurement data
- Globals and shared singletons, except for genuinely-singular system
  resources

Forbidden absolutely, **no ADR override**:

- **Hardcoded secrets, credentials, tokens, certificates, or signing
  keys** in source, configuration files, container images, build
  caches, or test fixtures. See Section 2.6.
- **Hardcoded environment-specific values** (endpoints, regions,
  account IDs, file system paths) inside application code.
  Configuration flows from outside the artifact, per
  `governance-commons/spec/principles.md` P1 (Contracts not
  installations).

**Composition is preferred to inheritance.** This applies to OOP
class hierarchies (Java, C#, Kotlin, Python, C++), to UI component
design (React function components and hooks, Vue composition API,
SwiftUI, Flutter widget composition), and to module composition in
functional and declarative stacks. The Gang of Four's "favor object
composition over class inheritance" generalizes beyond OOP.

### Section 2.6 - Secrets management

Secrets are anything that grants access: passwords, API tokens, OAuth
client secrets, JWT signing keys, database credentials, encryption
keys, certificate private keys, publish tokens (npm, PyPI, Maven,
crates.io, container registries), webhook signing secrets, third-party
service credentials. All are treated the same.

- No secrets in source control, ever, including git history. A
  pre-commit secret scanner is required (gitleaks, trufflehog,
  detect-secrets, or equivalent), configured to block commits.
- No secrets in container or VM images, including intermediate build
  layers.
- No secrets in logs, error messages, stack traces, distributed traces,
  metrics labels, or telemetry payloads.
- No secrets in environment variables on developer machines; secrets
  flow from a vault (1Password CLI, AWS Secrets Manager, HashiCorp
  Vault, Azure Key Vault, GCP Secret Manager, k8s External Secrets)
  into runtime contexts only.
- Secrets in transit travel over authenticated, encrypted channels
  per Section 5.5.
- On suspected exposure: rotate immediately, audit access logs, write
  an ADR capturing what was exposed, how, and what changed to prevent
  recurrence. Speed of rotation is the primary metric; thorough root
  cause analysis can follow.
- Service-to-service authentication prefers workload identity (IAM
  roles, k8s service accounts with OIDC, mTLS, SPIFFE/SPIRE) over
  static credentials, where the platform supports it.

Per P1 (Contracts not installations), the framework specifies that
secrets must be present and protected; it does not mandate a specific
vault. The choice is environment-level, recorded in the feature's
spec.

### Section 2.7 - Static analysis and reproducible builds

**Static analysis runs in CI and blocks merge** on findings of
declared severity. Tools are stack-appropriate; the obligation is
universal.

- Linters and formatters for every language in the project (eslint,
  prettier, ruff, black, gofmt, golangci-lint, ktlint, detekt, clippy,
  rustfmt, clang-tidy, clang-format, csharpier, dotnet-format,
  rubocop, phpcs/phpstan, checkstyle/spotbugs, stylelint, hadolint)
- Type checkers where the language supports them (mypy, tsc strict
  mode, Kotlin null-safety, C# nullable reference types, Rust's
  borrow checker, C++ compiled with `-Wall -Wextra -Werror`)
- Security scanners (semgrep, bandit, gosec, brakeman, sonarqube,
  or equivalent)
- Infrastructure-as-code scanners (Checkov, tfsec, trivy, kube-linter,
  kubescape) for any project containing Terraform, CloudFormation,
  Helm charts, Kubernetes manifests, Pulumi, or Dockerfiles
- Dependency vulnerability scanners per Section 5.7

Findings are either fixed, suppressed with a documented reason in the
config, or trigger an ADR. A "we'll fix it later" backlog is not a
suppression.

**Builds are reproducible**:

- All dependency lockfiles committed (`package-lock.json`, `yarn.lock`,
  `pnpm-lock.yaml`, `Cargo.lock`, `go.sum`, `Gemfile.lock`,
  `poetry.lock`, `composer.lock`, `.terraform.lock.hcl`, Maven
  dependency lock plugin output, etc.)
- Production container images pinned by digest (`sha256:...`), not by
  mutable tag, at the deployment manifest level.
- Build environment captured: CI image version, OS, toolchain
  versions.
- Build outputs are deterministic to the extent the toolchain
  permits: no embedded timestamps, hostnames, or random ordering
  unless required by the artifact format. Where embedded metadata
  is unavoidable, document it.

## Article III: AI-Assisted Work

### Section 3.1 - AI is an assistant, not an author

AI-assisted code requires human review before merge. AI output is
treated as a strong starting point, not a finished product.

### Section 3.2 - Attribution

Every commit involving AI-assisted code is attributable. The audit
log records the agent, the model, the session, and the human
principal who approved the work. This attribution is preserved in
provenance attestations (SLSA v1.0 + in-toto, per
`governance-commons/attestation/`).

### Section 3.3 - Agent boundaries

Sub-agents operate within their explicitly-granted capabilities. They
cannot escalate privileges by spawning other agents with capabilities
they themselves lack (enforced by
`governance-commons/policies/cross-agent-handoff.cedar`).

### Section 3.4 - Loop closure is mandatory

When one agent raises challenges, threats, or concerns against an
artifact, those items must be either resolved or explicitly overridden
with an ADR before downstream work proceeds. Specifically:

- `staff-engineer` raises challenges → `code-reviewer` verifies resolution
- `threat-modeler` identifies threats → `security-reviewer` verifies mitigations
- `performance-reviewer` flags resource concerns → `test-architect` produces tests proving the safeguard works
- `production-readiness` flags operability gaps → `code-reviewer` verifies closure

Ignoring an agent's output without an ADR is forbidden.

### Section 3.5 - Cost discipline

Every agent invocation reports its cost (tokens + estimated USD).
Cost reports accumulate in `specs/NNN-feature/events.jsonl`.
The framework is provider-agnostic; pricing data lives in
`governance-commons/lib-context/ai-model-pricing.yaml` and supports
multiple providers (Anthropic, OpenAI, Google, Meta, etc.).

### Section 3.6 - Evaluations and adversarial testing

Any feature that ships AI capability requires evaluations before
production deployment and adversarial testing proportional to the
capability's reach.

**Evaluations**:

- Each AI capability defines a measurable evaluation set before
  implementation begins. The eval set captures the capability's
  intent the way unit tests capture function behavior.
- Evaluations are versioned, run automatically against the model
  configuration of record, and baseline against the prior-shipped
  version. Regressions block deployment.
- Evaluations include refusal behavior: the capability should refuse
  what it is supposed to refuse, with the wording captured in eval
  fixtures.
- Where the capability operates autonomously, evaluations cover the
  decision space the agent has authority over: which actions it
  takes, which tools it invokes, which artifacts it writes.
- Production drift is monitored: a sample of real interactions is
  scored against the eval criteria, with alerting on regression.

**Adversarial testing**:

- For capabilities that touch external interfaces, untrusted input,
  or sensitive data, adversarial inputs are added to the eval set
  before launch. Coverage includes prompt injection, jailbreak
  attempts, malformed inputs, and inputs designed to extract training
  data or system prompts.
- For capabilities with high-stakes autonomy (writes to production,
  takes externally-visible actions, makes governance decisions),
  red-teaming is conducted by humans or by separate agents acting
  adversarially. Findings flow through the same priority system as
  threat-modeler findings (Section 3.4 loop closure).
- Instruction-hierarchy violations (e.g., user input attempting to
  override system instructions) are tested explicitly.

The eval set, the adversarial fixtures, and the run history are
artifacts under version control like any other spec deliverable
(Section 1.4).

This section is informed by Anthropic's Responsible Scaling Policy
(ASL-3 deployment standards, Risk Reports, affirmative-case-for-safety
framing), OpenAI's Model Spec (instruction hierarchy, decision rubrics
for irreversible actions), Andrew Ng's evaluation discipline (single-
number metrics, error analysis as iterative practice), Andrej
Karpathy's training recipe (verify the data, overfit a small batch,
baseline before claiming improvement), and Ian Goodfellow's
adversarial-examples lineage.

## Article IV: Production Readiness

### Section 4.1 - Environment topology awareness

The framework distinguishes four default environments: `local`,
`integration`, `staging`, and `prod`. Additional environments
(`perf`, `chaos`, `security`) may be added as YAML configuration.

Each environment differs across dimensions documented by the
`production-readiness` agent: data, scale, latency, dependencies,
authn/authz, secrets, observability, recoverability, rate limits,
cost controls, feature flags.

Code must be reviewed against this matrix before reaching production.

### Section 4.2 - Production configuration verification

Before any deployment to `prod`, the following are explicitly
verified:

- Production environment variables documented and present
- Production secrets sourced from vault/KMS per Section 2.6, not env
  files
- Production tokens scoped to least privilege per Section 5.1
- Rate limits configured on every external dependency
- Timeouts configured on every external call per Section 2.3
- Production logging level is appropriate (Section 4.3)
- Replica/instance count sized for load per Section 4.7
- Database connection pools sized for replicas
- Feature flag defaults are correct
- Cost controls active (billing alarms, hard caps); align with the
  AWS Well-Architected Cost Optimization pillar or equivalent
  cloud-provider discipline
- Backup configuration verified and restore tested in last 90 days

### Section 4.3 - Observability is non-optional

Every production code path emits:

- Structured logs with correlation IDs at decision points
- Metrics at appropriate cardinality (no high-cardinality user IDs
  in labels)
- Traces spanning operation boundaries
- Audit envelope events at governance decision points

Each production service defines Service Level Indicators (SLIs),
Service Level Objectives (SLOs), and an error budget. The error
budget governs release cadence: when the budget is exhausted,
feature work pauses until reliability is restored.

### Section 4.4 - Failure is expected

The 8 fallacies of distributed computing are not assumptions. Every
external call assumes:

- The network is unreliable
- Latency is non-zero
- Bandwidth is finite
- The network is not secure
- Topology will change
- There are multiple administrators
- Transport costs are non-zero
- The network is not homogeneous

Code that violates any of these requires an ADR justifying the
assumption. Werner Vogels' "everything fails, all the time" is the
operational corollary.

### Section 4.5 - Idempotency by default

Operations that mutate state must be safe to retry. Idempotency is a
design property, not a runtime accident.

- HTTP mutations follow REST semantics: `PUT` and `DELETE` are
  idempotent by contract; `POST` carries an idempotency key when the
  operation has external side effects (payment, account creation,
  notification dispatch).
- Message consumers handle duplicate delivery. At-least-once is the
  delivery guarantee; exactly-once is the application property the
  consumer engineers.
- Database migrations are forward-only and idempotent in application:
  re-running a migration on an up-to-date schema is a no-op, not a
  failure.
- Deployment pipelines are re-runnable. A failed deploy plus a
  re-run produces the same final state as a successful single
  deploy.
- Infrastructure-as-code is idempotent by construction: Terraform
  `plan`/`apply` cycles, Pulumi previews, Kubernetes controller
  reconciliation loops, Ansible playbooks with check mode.

When retry-safety is not achievable, document the operation as
"at-most-once" with the failure-handling path explicit, and route it
through a human approval step rather than automatic retry.

### Section 4.6 - Backward compatibility and migration discipline

Public surfaces have a versioning scheme and a deprecation policy.
"Public" means: APIs consumed by other services, libraries published
to a registry, database schemas read by other applications, message
formats consumed by other producers or consumers, Terraform module
input variables, container image tags consumed by other repositories.

**Versioning**:

- Semantic versioning (MAJOR.MINOR.PATCH) for libraries and APIs
  where semver applies.
- Calendar versioning where semver does not (data formats, dataset
  versions, model versions).
- Additive changes are MINOR or PATCH; backward-incompatible changes
  are MAJOR.
- Breaking changes require an ADR documenting the migration plan,
  the deprecation window, and the consumer-notification path.

**Migration**:

- Database schema changes use expand-then-contract patterns where
  zero-downtime matters: add the new shape, dual-write, backfill,
  switch reads, drop the old shape.
- API breaking changes ship behind a new path or version; old paths
  remain for the deprecation window with deprecation headers.
- Library breaking changes ship with codemods or migration guides
  where mechanical translation is feasible.

The spirit here is Fowler's *Refactoring* and *Patterns of Enterprise
Application Architecture*: backward compatibility is achieved by
making each step a refactoring, never a rewrite.

### Section 4.7 - Resource limits and capacity planning

Every workload has explicit resource limits. Unbounded growth is
forbidden without an ADR.

- Containers declare CPU/memory requests and limits. Kubernetes pods
  without both fail admission.
- Lambda / Cloud Functions / Cloud Run instances declare memory and
  timeout.
- JVM workloads set explicit heap sizes (`-Xms` / `-Xmx`); .NET
  workloads set explicit GC and memory limits where the runtime
  allows.
- Connection pools, thread pools, request queues, and retry queues
  are bounded, with overflow behavior defined (reject, shed, queue
  with timeout).
- Log volume is monitored; logs that grow unboundedly require
  rotation, sampling, or aggregation.
- Cost ceilings are configured with billing alarms and, where the
  provider supports it, hard caps.

Capacity planning is documented at three time horizons in the
production-readiness review: launch, 6 months out, 24 months out.
Each horizon names the dimension expected to be the bottleneck
(throughput, storage, concurrency, cost) and the response plan
(scale-up, scale-out, archival, sharding, model swap).

## Article V: Security Posture

### Section 5.1 - Least privilege everywhere

- AI agents have minimum capabilities to complete their task
- Service accounts have minimum permissions to complete their job
- Production credentials are scoped narrowly
- Cross-service trust is explicit, not implicit

### Section 5.2 - Threats are modeled before implementation

For any feature touching authentication, authorization, data
classified Confidential or higher, external interfaces, or AI
agent capabilities, a threat model
(`specs/NNN-feature/reviews/threat-model.md`) is produced by the
`threat-modeler` agent before `/speckit-tasks` runs.

### Section 5.3 - Data classification respected

Data classifications from `governance-commons/spec/data-classification.md`
are honored:

- Public, Internal: AI may read
- Confidential: AI reads with session-level approval
- Restricted: AI reads with file-specific approval + MFA
- Regulated: AI never reads, period

### Section 5.4 - Compliance configuration is verified

Compliance requirements (GDPR, HIPAA, SOC 2, EU AI Act, etc.) are
verified by the `security-reviewer` agent against the OSCAL controls
in `governance-commons/catalogs/compliance/`.

### Section 5.5 - Encryption is the default

- All network communication is encrypted in transit: TLS 1.2 minimum,
  TLS 1.3 preferred. No plaintext HTTP between services, even on
  trusted networks (Zero Trust applies internally as well as
  externally).
- All persistent data is encrypted at rest: database storage, object
  storage, backups, message queue contents, Terraform state, container
  registries, secret stores, log archives, build caches.
- Key management is explicit and uses managed KMS or HSM where
  available (AWS KMS, GCP Cloud KMS, Azure Key Vault, HashiCorp Vault
  Transit, sealed-secrets for Kubernetes, age for asymmetric file
  encryption). No plaintext keys on disk; no keys in source control;
  no keys in environment variables on developer machines.
- No custom cryptography. Use vetted libraries (libsodium/NaCl, AWS
  Encryption SDK, language standard-library crypto, Google Tink).
  Custom crypto requires an ADR, security-reviewer approval, and
  external review.
- Certificate expiry is monitored; renewal is automated where the
  certificate authority supports it (Let's Encrypt, ACME, AWS
  Certificate Manager, cert-manager for Kubernetes).
- Keys are rotated on a defined cadence and immediately upon
  suspected compromise.

### Section 5.6 - Input validation and output encoding

Validation at boundaries (Section 2.3) is the first half of safe
data handling. The second half is encoding outputs for the
destination context:

- **HTML output**: escape per the HTML grammar position (element
  body, attribute value, script body, style body, URL context). Use
  the framework's templating layer; do not concatenate strings into
  HTML.
- **SQL**: parameterized queries only; never string concatenation
  with user input. ORMs satisfy this when used correctly.
- **Shell**: never pass user input through `system()` / `exec()` /
  `subprocess.shell=True` without quoting; prefer argument arrays.
- **JSON, XML, YAML, TOML, Protobuf**: use the language's standard
  serializer/deserializer; do not hand-write parsing of user input.
- **URL components**: URL-encode query parameters and path segments;
  never trust that "the framework handles it" without verifying.
- **Log output**: structured fields, not interpolated strings, so log
  consumers can rely on field types and untrusted input cannot break
  the log format.
- LDAP filter injection, XPath injection, command-line argument
  injection, template injection (Jinja2/Mustache/ERB with user-
  controlled template strings), deserialization of untrusted input:
  all forbidden without explicit security-reviewer approval.

The OWASP Top 10 (web) and the OWASP API Security Top 10 are the
operational vocabulary for this section. The OWASP Top 10 for
Agentic Applications applies additionally to AI-capable features
(distinct from the OWASP LLM Top 10).

### Section 5.7 - Dependency and supply chain hygiene

The dependencies you take are part of your attack surface.

- Software Bill of Materials (SBOM) is generated for every deployable
  artifact, in SPDX or CycloneDX format, and stored alongside the
  artifact.
- License compatibility is verified before adding a dependency. The
  project's allowed-license list is maintained alongside the build
  configuration; additions require an ADR.
- Dependency vulnerability scanning runs in CI per Section 2.7;
  critical vulnerabilities block deployment.
- Where supported, dependencies are pinned to signed artifacts and
  signatures verified at install (npm provenance, PyPI Trusted
  Publishers, sigstore/cosign for container images, Go module
  checksums, crates.io signatures).
- Unmaintained dependencies (no release in 18+ months, no security
  response) are flagged in the SBOM review; an ADR documents the
  replacement plan or the justification for retaining.
- Build provenance attestations (SLSA v1.0 + in-toto, per
  `governance-commons/attestation/`) are generated for production
  artifacts and verified at deployment.
- Transitive dependencies are reviewed: a `curl` binary in your
  container is your problem regardless of which dependency pulled it
  in.

## Article VI: Governance Loop Closure

### Section 6.1 - Append-only event log per feature

Every feature has `specs/NNN-feature/events.jsonl` recording
all agent invocations, their costs, their outputs, and the resolution
status of items they raised.

### Section 6.2 - Loop verification enforced

A git pre-commit hook (`.claude/hooks/verify-loop-closure.sh`, which
delegates to `.claude/hooks/verify_loop_closure.py`) checks before
every commit that:

- Every P1 item raised by an upstream agent has a matching
  `closure-claimed`, `closure-verified`, or `overridden` event NOT
  superseded by a `closure-rejected` event
- Every P2 item raised by an upstream agent has the same OR a
  `deferred` event with a matching rationale entry in
  `specs/NNN-feature/deferrals.md`
- P3 items are informational; no closure required
- A `closure-verified` event additionally carries disk-read evidence
  (`closure_evidence.read` with a `path` and the `sha256` digest of the
  artifact the verifier read). The hook independently re-reads that
  artifact and rejects a `closure-verified` whose read evidence is
  absent, resolves to no file, is empty, or has a malformed digest; a
  since-changed artifact warns without blocking. A verification with no
  recorded read of the artifact is a declaration, not evidence. This
  binds `closure-verified` only; `closure-claimed` (cross-tool
  self-attestation) and `overridden` (ADR acceptance) are unchanged.
  See `docs/decisions/ADR-001-disk-truth-read-evidence-gate.md`.

Semantic verification (whether a claimed closure actually addresses
the original concern) is performed by the `closure-auditor` sub-agent
at the post-implementation checkpoint and at pre-commit. The hook
is the mechanical enforcement layer; closure-auditor is the
semantic-judgment layer.

The hook honors `SKIP_LOOP_VERIFY=1` as an emergency override only
when paired with a non-empty `SKIP_LOOP_VERIFY_REASON` (rare; the
reason is logged and the commit message documents it).

### Section 6.3 - ADRs document overrides

When an agent's challenge is overridden rather than resolved in code,
the override is documented in an ADR (`docs/decisions/ADR-NNN-*.md`)
explaining what is being accepted and why. The ADR is referenced
from the corresponding `overridden` event in events.jsonl.

P1 items can be overridden via ADR. P2 items can be overridden OR
deferred (with rationale entry in `deferrals.md`). P3 items are
informational and require no action.

## Article VII: Amendments

### Section 7.1 - Constitution changes require process

This constitution can be amended. Amendments require:

1. A spec describing the proposed change
2. An ADR justifying the change
3. Migration plan for affected features (if applicable)
4. Approval from the project principal (you)
5. Update to this document with version increment

### Section 7.2 - Version

Current version: **1.2.0**

Last amended: **2026-06-23** (v1.2.0: Section 6.2 amended to require
disk-read evidence on `closure-verified` events, independently
re-checked by `verify_loop_closure.py`; see ADR-001. Additive normative
refinement of the existing loop-closure rule; `closure-claimed` and
`overridden` are unchanged. Existing `closure-verified` events written
before this amendment carry no read block and will block if their
feature is re-staged; the hook scopes to the staged feature, so fresh
features adopt cleanly, and the SKIP_LOOP_VERIFY override covers a
legacy re-stage.)

Previously amended: **2026-05-16** (v1.1.0: added Nature-of-this-document
preamble; Article II Sections 2.6 Secrets management and 2.7 Static
analysis and reproducible builds; Article III Section 3.6 Evaluations
and adversarial testing; Article IV Sections 4.5 Idempotency by
default, 4.6 Backward compatibility and migration discipline, 4.7
Resource limits and capacity planning; Article V Sections 5.5
Encryption is the default, 5.6 Input validation and output encoding,
5.7 Dependency and supply chain hygiene; reframed Section 2.5
Anti-pattern resistance to be language-family-neutral and added
forbidden-absolutely entries; expanded Sections 2.3 and 2.4; added
Foundational traditions section.)

Initial version: **1.0.0** (2026-05-13).

## Application across spec-kit phases

How each spec-kit command honors this constitution:

| Command | Constitution check |
|---|---|
| `/speckit-specify` | Spec must address all relevant Articles (engineering, AI, prod, security) |
| `/speckit-clarify` | Clarifications surface implicit constitutional violations |
| `/speckit-plan` | Plan respects Article II (engineering standards) and Article IV (production) |
| `/speckit-tasks` | Tasks include constitutional verification steps (threat model, ADRs, tests, evals) |
| `/speckit-implement` | Implementation follows all Articles; agents enforce in real time |
| `/speckit-analyze` | Cross-artifact consistency check verifies constitutional alignment |

## Application across agents

How each agent honors this constitution:

| Agent | Primary Articles enforced |
|---|---|
| `code-reviewer` | II, V, VI |
| `security-reviewer` | V (especially 5.3, 5.4, 5.5, 5.6, 5.7), VI |
| `test-architect` | II (especially 2.4), III (3.6 evaluations) |
| `threat-modeler` | V (especially 5.2) |
| `performance-reviewer` | II (2.3), IV (especially 4.4, 4.5, 4.7) |
| `staff-engineer` | All Articles (judgment layer) |
| `production-readiness` | IV (all sections) |

All agents enforce Article III (AI-assisted work) and Article VI
(governance loop closure).

## Foundational traditions

This constitution states principles; implementing them in code is
done in the idioms of specific engineering traditions. AI agents and
human contributors are expected to apply the relevant tradition for
the stack they are working in. The works listed below are the
operational vocabulary, not an exhaustive bibliography. Stack-specific
manifestations are documented in `governance-commons/playbooks/`
(populated incrementally as features in each stack ship).

**Universal software engineering** (applies regardless of stack):

- *Effective Java* (Bloch): API design, immutability, composition
  over inheritance, defensive copying, "design APIs that cannot be
  misused." Connects to Sections 2.3, 2.5.
- *Clean Code* and *Clean Architecture* (Robert C. Martin): SOLID
  principles, function/class size, dependencies-point-inward, Boy
  Scout Rule. Connects to Sections 2.4, 2.5.
- *Test-Driven Development: By Example*, *Extreme Programming
  Explained*, *Tidy First?* (Beck): Red-Green-Refactor,
  tests-as-design-pressure, small reversible changes. Connects to
  Section 2.4.
- *Refactoring*, *Patterns of Enterprise Application Architecture*,
  *Microservices* essays (Fowler): code smells, evolutionary design,
  Strangler Fig migrations, Conway's Law, "make the change easy,
  then make the easy change." Connects to Article I, Sections 2.2,
  4.6.
- *Design Patterns* (Gamma, Helm, Johnson, Vlissides, the Gang of
  Four): creational, structural, behavioral patterns as shared
  vocabulary; "program to an interface, not an implementation."
  Connects to Section 2.5.
- *The Pragmatic Programmer* (Hunt, Thomas): DRY, orthogonality,
  crash-early, programming-by-contract, "sign your work." Connects
  to Sections 2.5, 3.2.

**Language-family idioms**:

- **Java / JVM**: Bloch *Effective Java*; Josh Long Spring Boot
  production patterns (auto-configuration, Actuator, observability
  defaults). Connects to Sections 2.3, 4.2, 4.3.
- **JavaScript / TypeScript**: Crockford *JavaScript: The Good
  Parts* (strict mode, strict equality, avoid implicit globals);
  Kyle Simpson *You Don't Know JS* series (scope, closures, coercion,
  async patterns). Connects to Section 2.7.
- **React**: Dan Abramov and Jordan Walke writing on component
  composition, unidirectional data flow, effects as escape hatches
  not first resort, server vs. client components. Connects to
  Section 2.5 composition preference.
- **Python**: PEP 8, PEP 20 (Zen of Python, "explicit is better
  than implicit"); Brett Slatkin *Effective Python*; Raymond
  Hettinger's standard-library patterns; Guido van Rossum's design
  philosophy. Connects to Sections 2.3, 2.4.
- **C++**: Stroustrup *The C++ Programming Language* and *A Tour of
  C++*; Scott Meyers *Effective C++* / *Effective Modern C++*;
  Sutter and Alexandrescu *C++ Coding Standards*. RAII, Rule of
  Zero/Three/Five, smart pointers, `const` correctness, avoid
  undefined behavior. Connects to Section 2.3 resource ownership.
- **PHP**: Taylor Otwell's Laravel idioms (service container,
  Eloquent, migrations, queue jobs); Rasmus Lerdorf's pragmatic
  minimalism; PSR standards. Connects to Section 4.6 migration
  discipline.
- **C# / .NET**: Microsoft's .NET runtime team guidance; nullable
  reference types as default. Connects to Section 2.3 memory safety,
  Section 2.7 static analysis.
- **Kotlin**: JetBrains language design (null safety by default,
  data classes, sealed hierarchies). Connects to Section 2.5
  anti-pattern resistance.

**Cloud-native and infrastructure**:

- **Kubernetes**: Kelsey Hightower *Kubernetes Up & Running* (with
  Burns and Beda); Brendan Burns *Designing Distributed Systems*;
  Joe Beda's design notes from Kubernetes' early architecture;
  Craig McLuckie's framing of the immutable-infrastructure thesis.
  Connects to Sections 4.5, 4.7, 5.1.
- **AWS**: Werner Vogels' essays ("Everything fails, all the time";
  "10 lessons from 10 years of Amazon Web Services"); Jeff Barr's
  AWS service introductions; AWS Well-Architected Framework's six
  pillars (Operational Excellence, Security, Reliability, Performance
  Efficiency, Cost Optimization, Sustainability). Connects to
  Articles IV and V overall.
- **Terraform / IaC**: HashiCorp's recommended patterns (remote
  state, state locking, workspace isolation, module composition).
  Connects to Sections 2.1, 4.5.
- **Twelve-Factor App methodology**: already codified in
  `governance-commons/spec/principles.md` P1 (Contracts not
  installations); informs Sections 2.1, 2.6, 4.2.

**AI engineering**:

- **Andrew Ng** *Machine Learning Yearning*: train/dev/test
  discipline, single-number metrics, error analysis as iterative
  practice. Connects to Section 3.6.
- **Andrej Karpathy** "A Recipe for Training Neural Networks",
  *Software 2.0* essay: verify the data, overfit a small batch,
  don't be a hero. Connects to Sections 3.1, 3.6.
- **Geoffrey Hinton**: backpropagation foundations, distillation,
  representation learning. Background to Article III generally.
- **Ian Goodfellow**: GANs and adversarial examples; the lineage
  from adversarial examples to AI red-teaming. Connects to
  Section 3.6.
- **Anthropic Responsible Scaling Policy** (v3.x, current Feb 2026):
  AI Safety Levels, Frontier Safety Roadmaps, Risk Reports with
  external review, affirmative-case-for-safety framing. Connects to
  Sections 3.6, 3.4.
- **OpenAI Model Spec** (CC0, current Dec 2025):
  constitution-vs-case-law analogy (which this document adopts in
  the Nature of this document section); instruction-hierarchy /
  chain-of-command framing; decision rubrics for irreversible
  actions; concrete compliant/non-compliant examples for hard cases.
  Connects to Nature of this document and Section 3.6.

## References

- `governance-commons/spec/principles.md` - philosophical principles (P1-P12)
- `governance-commons/spec/policy-dsl-choice.md` - Cedar policy framework
- `governance-commons/policies/` - enforceable Cedar policies
- `governance-commons/catalogs/threats/` - threat catalogs
- `governance-commons/catalogs/compliance/` - OSCAL compliance catalogs
- `governance-commons/playbooks/` - incident response procedures and
  stack-specific manifestations of constitutional principles
- `governance-commons/attestation/` - provenance attestation specs
- `governance-commons/lib-context/ai-model-pricing.yaml` - cost data
- `docs/decisions/` - ADRs (the "case law" complement to this constitution)
- NIST AI Risk Management Framework
- EU AI Act
- ISO/IEC 42001 (AI management systems)
- SLSA v1.0 supply chain security framework
- OWASP Top 10, OWASP API Security Top 10, OWASP Top 10 for Agentic
  Applications, OWASP LLM Top 10
- AWS Well-Architected Framework (https://aws.amazon.com/architecture/well-architected/)
- Anthropic Responsible Scaling Policy (https://www.anthropic.com/responsible-scaling-policy)
- OpenAI Model Spec (https://model-spec.openai.com)
