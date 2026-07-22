<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Project Fit

This document explains which kinds of projects benefit most from the
framework today, which benefit partially, and which are better off
not using it. It also describes the roadmap for where the framework
intends to grow.

The framework's value comes from spec-driven workflow, specialized
multi-agent review, constitutional pre-build gates, threat catalogs,
compliance specifications, ADR discipline, and cost tracking. These
are powerful for production-grade work and overhead for exploratory
work. Honest fit matters because adopting the framework when it's
the wrong choice produces adoption theater — documents that exist
but aren't consulted, agents invoked but not respected.

## Where the framework's value compounds

The framework helps most when all four of these conditions hold:

1. **The project is production-grade.** Real users depend on it. Or
   real money runs through it. Or real data is at stake. The cost of
   shipping something broken is meaningful.

2. **Security or compliance is real.** The work touches authentication,
   authorization, regulated data (PII, PHI, financial, classified+),
   external interfaces, or AI agent capabilities. Threats deserve
   structured analysis, not vibes.

3. **Architectural decisions outlive the writer.** Other engineers
   will read this code in two years. Decisions need to be defensible
   without the original author present. ADRs become first-class
   artifacts.

4. **Getting it wrong is expensive.** Outages, breaches, compliance
   violations, performance failures at scale, or unrecoverable data
   loss are real risks. Pre-build review pays for itself.

When three or four of these hold, the framework's overhead is paid
back by reduced rework and clearer audit trails. When two or fewer
hold, the overhead is likely net negative.

## Honest current fit

The ratings below reflect what the framework supports **today**, not
what it aspires to support. The roadmap section explains where the
gaps are and how each aspirational category gets to Strong over time.

> **L1 enforcement caveat (read before wiring a blocking gate).** The
> substrate's L1 mechanical layer (static-analysis bindings) is
> maturing. A registry-ID audit found that only about 45 of 306 L1
> rule references are verifiably alive in their upstream source of
> truth, and that 23 of 47 L1 bindings have no live upstream reference
> at all (upstream drift: registry rules get renamed, merged, or
> removed). Do not wire the L1 bindings into a blocking CI gate
> assuming every reference resolves. Treat L1 as advisory and
> maturing; lead adoption with the L2 review checklists, the L3
> decision frameworks, and threat-model traceability, which are
> unaffected. This is the single most important limitation to weigh
> when judging fit. The authoritative statement, with the remediation
> plan, is `governance-commons/SUBSTRATE-FIT.md` (section "The L1
> enforcement caveat").

| Project type | Current fit | Notes |
|---|---|---|
| Cloud infrastructure (Terraform, Pulumi, CloudFormation) | **Strong** | Security-relevant, multi-environment, blast radius matters. OSCAL maps directly. ADRs critical for IaC decisions. Lib-context covers Terraform/AWS. |
| AI/ML platforms and agentic systems | **Strong** | Framework's primary target. AI-specific threats (OWASP LLM, MITRE ATLAS), Cedar policies for agent runtime, cost discipline, compliance complexity. Lib-context covers LangChain, LangGraph, Pydantic. |
| Kubernetes operators and platform engineering | **Strong** | Production-grade by definition. RBAC/security model rich. Multi-environment. SLO-aligned. Constitution Article IV environment topology fits cleanly. |
| Backend services at scale (Java/Spring Boot, Go, Rust, Python, .NET) | **Strong** | Threat modeling, performance review, production readiness directly apply. ADRs valuable for architectural decisions. Lib-context covers FastAPI; other backends covered by general agents. |
| Distributed systems (gRPC, event-driven, microservices) | **Strong** | Performance and threat lenses especially valuable. Operational design important. The 8 fallacies of distributed computing are explicitly constraints in constitution Article IV. |
| Security-sensitive applications (auth, payments, healthcare, identity) | **Strong** | All review lenses apply. Compliance catalogs (NIST 800-53, NIST 800-171, NIST SSDF, NIST CSF v2, NIST AI RMF, EU AI Act) directly useful. Cedar policies model fine-grained access control. |
| Data platforms (pipelines, ETL, warehousing, lakehouses) | **Strong** | Privacy review valuable. Performance/scaling matters. Compliance often applies. Schema decisions deserve ADRs. |
| Mobile apps (iOS, Android, React Native, Flutter) | Partial today | Constitution and ADR discipline apply. Generic threat-modeler runs against STRIDE but lacks OWASP MASTG/MASVS catalogs. No mobile-specific lib-context. Performance-reviewer is server-oriented. See Roadmap. |
| Web frontends (React, Vue, Svelte, Angular SPAs) | Partial today | Constitution and ADR discipline apply. Threat-modeler covers XSS/CSRF/auth via OWASP Top 10 mapping but lacks OWASP ASVS Frontend depth. No accessibility catalog. Performance-reviewer doesn't cover Core Web Vitals or bundle analysis. See Roadmap. |
| Libraries and SDKs (public APIs, shared modules) | Partial today | ADR discipline applies fully — libraries outlive their authors. Threat-modeler runs but lacks API versioning/deprecation discipline. No semver enforcement or breaking-change catalog. See Roadmap. |
| CLI tools and developer utilities (non-trivial, shipped to users) | Partial today | Constitution applies. Threat surface usually small. No CLI-specific guidance (argument design, exit code semantics, completion scripts, cross-platform distribution). Most agents over-apply for typical CLI scope. See Roadmap. |
| Game development | Partial | Performance discipline differs (frame-rate constrained, not cost-constrained). Threat modeling rarely applies. Different lifecycle. Use substrate (constitution and ADRs valuable). Not on near-term roadmap. |
| Prototypes and proofs-of-concept | Partial | Framework's pre-build gates can defeat the purpose of exploration. Use Tier 1 substrate (threat catalogs as reference, ADRs for decisions worth remembering); skip the workflow. |
| Personal scripts and one-off automation | Not recommended | Overhead exceeds value. The framework is built for projects that ship to users. |
| Static sites (Jekyll, Hugo, Next.js static export) | Not recommended | Minimal architecture decisions. Most "code" is content. Use markdown and ship. |
| WordPress and PHP CMS sites | Not recommended | Most decisions are configuration, not architecture. Framework's lenses don't fit configuration-driven work. |
| Research code and academic prototypes | Not recommended | Research velocity beats discipline for the exploration phase. Adopt later if the research code transitions to production. |

## Roadmap to Strong fit for partial-fit categories

Mobile apps, web frontends, libraries, and CLI tools are partial fit
today because the framework was built primarily for backend/cloud/AI
work. Each has a concrete path to Strong fit that depends on framework
growth, not document edits.

### Mobile apps

What's missing to earn Strong fit:

- OWASP MASTG (Mobile Application Security Testing Guide) catalog
  added to `governance-commons/catalogs/threats/`
- OWASP MASVS (Mobile App Security Verification Standard) profile
  for the OSCAL catalogs
- Mobile-specific lib-context YAMLs (React Native, Flutter, SwiftUI,
  Jetpack Compose) documenting hallucination-prone APIs
- Mobile-specific playbook in `governance-commons/playbooks/`
  (app-store-rejection, certificate-expiry, signing-key-compromise)
- Performance-reviewer scope expansion: battery profiling, network
  conditions, background execution limits, memory pressure
- Threat-modeler scope expansion: device permissions, deep links,
  biometric auth, secure storage, certificate pinning

When all of these exist, mobile apps move to Strong fit.

### Web frontends

What's missing to earn Strong fit:

- OWASP ASVS (Application Security Verification Standard) Frontend
  profile for the OSCAL catalogs
- WCAG accessibility catalog added to
  `governance-commons/catalogs/` as a standards reference
- Frontend-specific lib-context YAMLs (React, Vue, Svelte, Angular)
- Core Web Vitals performance reference in lib-context (LCP, INP,
  CLS) with budget conventions
- Performance-reviewer scope expansion: bundle size, hydration cost,
  client-side rendering performance, third-party script impact
- Threat-modeler scope expansion: CSP/SRI configuration, prototype
  pollution, supply chain via npm, framework-specific patterns
  (React Server Components security, Next.js middleware)
- New cognitive lens (probably as a scope expansion to code-reviewer
  per the agent-coordination scope discipline principle):
  accessibility review triggered when UI work is in scope

When all of these exist, web frontends move to Strong fit.

### Libraries and SDKs

What's missing to earn Strong fit:

- Semver catalog and breaking-change taxonomy in
  `governance-commons/catalogs/`
- API versioning ADR template variant (deprecation timelines,
  migration paths)
- Lib-author-specific playbook (breaking-change-announcement,
  downstream-consumer-impact-analysis)
- Staff-engineer scope expansion or new lens: API design discipline
  (consistency with platform idioms, surface area discipline,
  deprecation cadence)
- Multi-language binding guidance for libraries with C/C++/Rust
  cores and language wrappers

When all of these exist, libraries and SDKs move to Strong fit.

### CLI tools

What's missing to earn Strong fit:

- CLI design conventions catalog (POSIX argument conventions, exit
  code semantics, completion script generation, terminal capability
  detection)
- Cross-platform distribution playbook (homebrew, scoop, apt, dnf,
  binary releases, code signing per platform)
- Lib-context for common CLI frameworks (Click, Cobra, Clap,
  Commander, Typer)
- Constitution amendment or extension: CLI-specific principles
  (UNIX philosophy alignment, composability with pipes, predictable
  output formats)
- Lighter-weight workflow variant for CLI scope (the current
  spec-kit workflow can be heavy for typical CLI tool features)

When all of these exist, CLI tools move to Strong fit.

## Strong fit: full framework

Projects with **Strong** current fit benefit from the complete framework:

- Spec-driven workflow (`/speckit-specify` → `/speckit-plan` →
  `/speckit-tasks` → `/speckit-implement`)
- All twelve specialized sub-agents invoked per their trigger conditions
- Constitutional pre-build gates with ADR discipline
- Loop closure verification at every workflow checkpoint
- Compliance catalogs and Cedar policies where applicable
- Cost tracking and audit envelopes
- Full SETUP.md path

This is the path the framework was designed for. The overhead is
real but the value compounds across the project's lifetime.

## Partial fit: substrate-only adoption

Projects with **Partial** current fit should adopt only the substrate
from the framework. The full workflow would be overhead, but specific
pieces are still valuable:

- **Threat catalogs** (`governance-commons/catalogs/threats/`) —
  useful as security references even without full threat modeling
- **Incident playbooks** (`governance-commons/playbooks/`) — useful
  for any project that operates in production
- **Constitution** (`.specify/memory/constitution.md`) — adopt
  selectively (e.g., exact version pinning, ADRs for non-trivial
  decisions) without committing to the full workflow
- **ADR discipline** — decisions worth remembering still benefit
  from structured documentation
- **lib-context YAMLs** — useful if the project uses any of the
  listed hallucination-prone libraries

See `docs/RETROFIT.md` for the tier-based adoption strategy. Partial
fit projects should adopt Tier 1 (drop-in substrate) and skip Tier 2
and Tier 3 unless concrete need arises.

If your project is in a category on the roadmap above, you can adopt
the substrate now and gain the full framework as the roadmap items
land.

## Not recommended: skip the framework entirely

Projects in this category are better off without the framework
because the overhead would exceed the value:

- **Personal scripts and one-off automation**: write the script,
  use it, move on. Constitution and ADRs for a 50-line shell script
  is overhead theater.
- **Static sites**: content is the work, not architecture. Use
  markdown and ship.
- **WordPress/CMS sites**: configuration is the work. Framework's
  engineering lenses don't fit.
- **Research code**: exploration phase benefits from minimal friction.
  Adopt the framework when research transitions to production.

The framework is built for projects that ship to users and where
architectural decisions matter. If neither is true, the framework
is the wrong tool.

## Edge cases worth flagging

**Hybrid projects**: a static marketing site with a small backend
API has different fit per part. Apply the framework to the API
(strong fit) and skip it for the static site (not recommended).
Don't force uniform adoption.

**Greenfield vs. existing**: greenfield projects with strong fit are
the cleanest case. Existing projects with strong fit need the
retrofit path (`docs/RETROFIT.md`). Don't conflate them.

**Solo developer projects**: the framework works for solo developers
(this very framework is solo-built). Coordination overhead is lower
but discipline benefit is real. ADRs especially help future-you who
won't remember why past-you made a choice.

**Multi-tool team projects**: per `docs/AI-COMPATIBILITY.md`, the
framework supports mixed AI tool usage. Different developers can
use Claude Code, Cursor, Codex, etc., all operating on the same
substrate. The Strong/Partial/Not-recommended fit doesn't change
based on AI tool choice.

## Honest signals that fit might be wrong

If you're adopting the framework and seeing any of these, the fit
may be off:

- Specs that read as ceremonial — written, never consulted, never
  amended
- Threat models with zero must-mitigate threats (the spec doesn't
  warrant the analysis)
- ADRs that document trivial choices ("we use camelCase for
  variables")
- Loop closure events that fire without anyone reading them
- Frustration that exceeds the perceived value

These are signals to either drop to partial fit or step back and
reassess whether the project belongs in the strong-fit category.

## See also

- `README.md` — framework overview
- `docs/AI-COMPATIBILITY.md` — which AI tools support the framework
- `docs/RETROFIT.md` — adopting the framework on existing projects
- `FUTURE.md` — roadmap items including the partial-fit improvements
- `SETUP.md` — installation procedure for strong-fit projects
- `PREREQUISITES.md` — what you need before adopting
