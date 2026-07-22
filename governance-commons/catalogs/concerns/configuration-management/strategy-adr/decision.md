---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: configuration-management.strategy-adr
title: "Configuration-Management Strategy Policy"
lifecycle-status: stable
commons-version: "0.8.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-04"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M6 close consolidation (2026-06-06) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M6 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-06. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent following the cost-model-selection-policy.madr.md precedent; first decision framework authored in Milestone 6; exercises the established MADR pattern for the configuration-management concern. SPDX header placed as YAML comments inside frontmatter per Section 10 settled decision 15. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft. Substrate-author review required for stable promotion at the M6 close."
authoritative-sources:
  - "https://12factor.net/config"
  - "https://12factor.net/dev-prod-parity"
  - "https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"
  - "https://owasp.org/www-project-application-security-verification-standard/"
  - "https://csrc.nist.gov/projects/risk-management/about-rmf/configuration-management"
  - "https://adr.github.io/madr/"
---

# Configuration-Management Strategy Policy

This decision framework provides the substrate's analysis of the
configuration-management strategy decisions a consumer must make.
Consumers reference this framework when authoring their own ADR
documenting how their services source, layer, validate, and govern
configuration. The substrate-recommended location for the consumer's ADR
is `/docs/decisions/ADR-XXX-configuration-management-strategy.md`.

The framework is referenced by substrate rule configuration-management.strategy-adr, which
requires the consumer to have an explicit, recorded configuration
strategy. Consumers satisfy configuration-management.strategy-adr by authoring an ADR that adapts
the analysis here to their context.

The lower-layer configuration rules enforce the consequences of this
strategy: configuration-management.no-hardcoded-config requires environment-varying values to be
externalized, configuration-management.no-swallowing-default requires required reads not to swallow
absence, configuration-management.startup-validation requires startup validation, and configuration-management.layering-and-parity
requires explicit layering, parity, and the secret-reference boundary.
This framework is the place where the consumer decides the surface those
rules then police.

## Context

Configuration-management strategy is a set of interlocking decisions. The
source model determines where values come from; precedence determines how
sources combine; validation determines when mistakes surface; parity
determines whether environments stay consistent; the secrets boundary
determines what is configuration versus a credential reference; the
static-versus-dynamic split determines what is fixed at deploy versus
changeable at runtime (the boundary with the forthcoming feature-flags
concern); and change control and ownership determine how the surface is
governed over time. The decisions are coupled: a file-only source model
implies a different precedence and validation story than an
environment-plus-service model.

The substrate cannot make these decisions for the consumer because they
depend on the consumer's deployment model, operational maturity, and risk
posture. The substrate provides recommended defaults that suit the common
case and documents the trade-offs so the consumer can deviate
deliberately.

## Decision Drivers

- Reproducibility: the same build should run in any environment by varying
  inputs, not by changing code.
- Early failure: configuration mistakes should surface at deploy time with
  a named cause, not at an arbitrary later request.
- Predictability: the effective source of any value should be knowable
  from a written precedence rule.
- Parity: environments should differ only in the values that must differ.
- Boundary integrity: secrets stay in secrets-management; dynamic toggles
  stay in feature-flags; configuration-management owns the substrate they
  rest on.
- Operability: the chosen approach should be simple to reason about under
  incident pressure.

## Considered Options

### Source model

Option A, environment-only (Twelve-Factor strict): all configuration in
environment variables. Simple, container-native, but awkward for
structured or large configuration and offers no place for non-secret
defaults.

Option B, file-plus-environment: a base configuration file carries
structured defaults; environment variables override per deploy. Balances
structure with deploy-time variation.

Option C, configuration service: a central service serves configuration,
enabling dynamic reconfiguration at the cost of a runtime dependency and
its own availability and change-control surface.

Substrate-recommended default: Option B for most services (environment for
deploy-varying values, a base file for structured defaults), escalating to
Option C only where dynamic reconfiguration without redeploy is a genuine
requirement, in which case the dynamic values are governed as feature-flags
or service-config with their own change control.

### Layering and precedence

Option A, implicit (load order): precedence is whatever the code happens to
do. Rejected; it is the unpredictability the rule exists to prevent.

Option B, explicit documented order: a written precedence (for example
defaults, then base file, then environment-specific file, then environment
variables, then explicit overrides) the loader implements exactly.

Substrate-recommended default: Option B, with the order recorded in the ADR
and matched by the implementation, verified by the configuration-management.layering-and-parity test.

### Validation approach

Option A, none or lazy: values are read and trusted at first use. Rejected;
it defers failure past the point of diagnosis.

Option B, startup validation gate: presence, type, and constraints checked
at boot, failing fast with an aggregated named error (configuration-management.startup-validation).

Substrate-recommended default: Option B, run in every environment so parity
is exercised.

### Environment parity

Option A, per-environment hand maintenance: each environment is edited
independently. Rejected; it is the source of the missing-in-production key.

Option B, shared required-key schema or manifest enforced across
environments, with environment-specific overrides carrying only differing
values.

Substrate-recommended default: Option B, verified by the configuration-management.layering-and-parity
parity test.

### Secrets boundary

Option A, secrets in configuration: convenient, and the recurring source of
committed credentials. Rejected.

Option B, secrets by reference: configuration carries references resolved at
runtime; handling is owned by secrets-management.

Substrate-recommended default: Option B without exception; the
configuration surface stays safe to commit.

### Static-versus-dynamic split (feature-flags boundary)

Option A, everything static at deploy: simplest; cannot change behavior
without a redeploy.

Option B, dynamic where justified: values that must change without redeploy
are modeled as feature-flags (behavioral toggles) or configuration-service
values, each with its own change control; everything else is static
configuration.

Substrate-recommended default: Option B, with the boundary recorded so that
when the feature-flags concern is adopted the hand-off is already drawn.
The default bias is static unless a concrete need for runtime change exists.

### Change control and ownership

Option A, ad hoc: configuration changes flow without review or audit.
Rejected for production-affecting values.

Option B, reviewed and audited: configuration changes are reviewed
proportionate to blast radius and are auditable; the surface has a named
owner and a review cadence.

Substrate-recommended default: Option B, with the owner and cadence recorded
in the ADR.

## Decision Outcome

The substrate-recommended strategy for the common case: a file-plus-
environment source model; an explicit documented precedence; a startup
validation gate run in every environment; a shared required-key schema for
parity; secrets by reference only; a static-by-default surface with dynamic
values escalated to feature-flags or a configuration service; and reviewed,
audited, owned change control. Consumers deviate deliberately and record the
deviation and its rationale in their ADR.

## Substrate Alignment

This framework is the L3 companion to the configuration-management catalog.
It draws boundaries to two sibling concerns rather than absorbing them: the
secrets boundary defers all credential handling to secrets-management, and
the static-versus-dynamic split defers flag lifecycle to the forthcoming
feature-flags concern (Milestone 6 Session 2). When feature-flags is
authored, the hand-off recorded here is finalized in both catalogs. The
provisioning of any configuration store remains
infrastructure-misconfiguration.

## Consequences

Positive: a coherent configuration surface inheritable across services;
configuration mistakes that fail fast and name their cause; environments
that drift only where intended; a secrets boundary that resists erosion.

Negative or cost: the startup gate and parity enforcement are upfront work;
the explicit precedence and shared schema impose a small discipline tax that
pays back at the first averted missing-in-production incident.

## References

See the authoritative-sources frontmatter: The Twelve-Factor App (Config
and Dev/prod parity), OWASP Top 10 A05:2021, OWASP ASVS Configuration
requirements, NIST SP 800-53 Configuration Management family, and the MADR
format.

## Decision Review Schedule

The consumer's ADR is reviewed at substrate adoption, at the introduction of
a new source model or a configuration service, at the introduction of
dynamic reconfiguration, at the authoring of the feature-flags boundary, and
on a substrate-recommended annual cadence.
