---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
framework-id: feature-flags.strategy-adr
title: "Feature-Flags Strategy Policy"
lifecycle-status: stable
commons-version: "0.8.0"
framework-version: "1.0.0"
author: myoung
authored: "2026-06-04"
reviewer: "myoung-self-attested"
reviewed: "2026-06-06"
entered-status-at: "2026-06-06"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation). Promoted to stable at the M6 close consolidation (2026-06-06) per the Path A precedent. Cooling-off honored: authoring landed in the concern's M6 authoring session on a prior calendar day; attestation lands at the close in a discrete commit on 2026-06-06. Backs the paired L3 catalog rule promoted to stable in the same close."
ai-assistance: "AI drafted from substrate-author intent following the configuration-management-strategy.madr.md precedent; second decision framework authored in Milestone 6; exercises the established MADR pattern for the feature-flags concern. SPDX header placed as YAML comments inside frontmatter per Section 10 settled decision 15. Frontmatter validates clean against decision-framework.schema.json at lifecycle-status draft. Substrate-author review required for stable promotion at the M6 close."
authoritative-sources:
  - "https://openfeature.dev/specification/"
  - "https://martinfowler.com/articles/feature-toggles.html"
  - "https://owasp.org/Top10/A05_2021-Security_Misconfiguration/"
  - "https://adr.github.io/madr/"
---

# Feature-Flags Strategy Policy

This decision framework provides the substrate's analysis of the
feature-flags strategy decisions a consumer must make. Consumers reference
this framework when authoring their own ADR documenting how their services
define, evaluate, roll out, and retire flags. The substrate-recommended
location for the consumer's ADR is
`/docs/decisions/ADR-XXX-feature-flags-strategy.md`.

The framework is referenced by substrate rule feature-flags.strategy-adr, which requires
the consumer to have an explicit, recorded feature-flags strategy.
Consumers satisfy feature-flags.strategy-adr by authoring an ADR that adapts the analysis
here to their context.

The lower-layer feature-flags rules enforce the consequences of this
strategy: feature-flags.fail-static-default requires every evaluation to supply a fail-static
default, feature-flags.no-hardcoded-flag requires a live flag not to be pinned to a constant or
short-circuited, feature-flags.staged-rollout-and-context requires staged rollout through provider
targeting with a clean evaluation context, and feature-flags.lifecycle-and-kill-switch requires flag
lifecycle discipline and a working kill switch. This framework is the place
where the consumer decides the surface those rules then police.

## Context

Feature-flags strategy is a set of interlocking decisions. The management
approach determines where and how flags are evaluated; the taxonomy
determines what kinds of flags exist and the lifecycle each one is held to;
the fail-static convention determines what happens when the provider is
unreachable or the flag is unknown; the evaluation-context schema determines
what data crosses into the targeting decision and where the PII and secret
boundaries sit; the rollout approach determines how a change reaches users;
the kill-switch inventory determines what can be turned off without a
deploy; and change control and ownership determine how the flag surface is
governed over time. The decisions are coupled: a permission-flag taxonomy
implies a fail-closed default, and a staged-rollout approach implies a
stable targeting key the context schema must carry.

The substrate cannot make these decisions for the consumer because they
depend on the consumer's deployment model, provider choice, and risk
posture. The substrate provides recommended defaults that suit the common
case and documents the trade-offs so the consumer can deviate deliberately.

## Decision Drivers

- Safe failure: an unreachable provider or unknown flag should degrade to
  the known-safe path, never to the new or more-permissive one.
- Reversibility: a change behind a flag should be revertible without a
  deploy, so rollout is a risk-reduction tool rather than a one-way door.
- Determinism: the same subject should resolve to the same variant across
  instances and restarts, so behavior is reproducible and debuggable.
- Boundary integrity: secrets stay in secrets-management, static
  configuration stays in configuration-management, and feature-flags owns
  only the dynamic behavioral surface.
- Debt control: flags are liabilities with a lifecycle; the strategy must
  make retirement the default rather than the exception.
- Operability: kill switches must be reachable and tested under incident
  pressure, not discovered to be inert when first needed.

## Considered Options

### Management approach

Option A, in-house flag table: flags read from a configuration source or
database the team builds around. Full control, but the team owns evaluation
semantics, targeting, propagation, and the audit surface.

Option B, managed or open provider behind a standard interface: an
OpenFeature-style SDK over a provider (hosted or self-managed) supplies
evaluation, targeting, and propagation. Less control of internals, but a
single coherent evaluation model and a vendor-neutral interface.

Substrate-recommended default: Option B with server-side evaluation behind a
standard interface, so the provider can be changed without rewriting call
sites, escalating to in-house only where a hard constraint forbids a
provider.

### Flag taxonomy and lifecycle

Option A, untyped flags: every flag is the same kind, with no expected
lifespan. Rejected; it is the source of flag debt the rules exist to
prevent.

Option B, typed taxonomy with per-type lifecycle: release, experiment,
operational kill-switch, and permission flags, each with a defined expected
lifespan (release and experiment flags are short-lived and carry an expiry;
kill-switch and permission flags are long-lived and reviewed on a cadence).

Substrate-recommended default: Option B, with owner, type, and expiry
recorded per flag and enforced by the feature-flags.lifecycle-and-kill-switch inventory reconciliation.

### Fail-static convention

Option A, default chosen ad hoc per call: each developer picks a default.
Rejected; it produces fail-open permission gates by accident.

Option B, convention by type: every flag defaults to its safe path, and
permission and kill-switch flags fail closed by rule; the safe polarity is
recorded with the flag.

Substrate-recommended default: Option B, enforced at the call site by
feature-flags.fail-static-default.

### Evaluation-context schema

Option A, pass whatever targeting might need: the application attaches user
records and lookup tokens. Rejected; it leaks secrets and excess PII into the
evaluation path.

Option B, documented allow-list: a stable targeting key plus a fixed set of
non-secret attributes the targeting rules actually consume, with PII
minimized to those inputs.

Substrate-recommended default: Option B, with the schema recorded and
enforced by feature-flags.staged-rollout-and-context; secret values never enter context (deferred to
secrets-management).

### Rollout approach

Option A, application-side bucketing: the code randomizes or hashes to decide
exposure. Rejected; client-side randomness is nondeterministic and untargetable.

Option B, provider targeting with deterministic bucketing: staged exposure is
expressed as provider targeting rules keyed on a stable identifier, ramped by
cohort and percentage without a deploy.

Substrate-recommended default: Option B, verified by the feature-flags.staged-rollout-and-context test.

### Kill-switch inventory

Option A, no designated kills: disabling a feature means a code change and
deploy. Rejected for anything that must be stoppable under incident pressure.

Option B, designated kill switches: operational kills are typed, owned by
on-call, default to the safe path, listed in an inventory, and exercised in
game-days.

Substrate-recommended default: Option B, verified by the feature-flags.lifecycle-and-kill-switch
kill-switch test.

### Change control and ownership

Option A, ad hoc: flag changes flow without review or audit. Rejected for
production-affecting flags.

Option B, reviewed and audited: flag-state changes are auditable and
reviewed proportionate to blast radius; the flag surface has a named owner
and a review cadence.

Substrate-recommended default: Option B, with owner and cadence recorded in
the ADR.

## Decision Outcome

The substrate-recommended strategy for the common case: a managed or open
provider behind a standard interface with server-side evaluation; a typed
taxonomy with per-type lifecycle and recorded expiry; a fail-static
convention where every flag defaults safe and permission and kill-switch
flags fail closed; a documented evaluation-context allow-list free of secrets
and excess PII; staged rollout through provider targeting with deterministic
bucketing; a designated, owned, tested kill-switch inventory; and reviewed,
audited, owned change control. Consumers deviate deliberately and record the
deviation and its rationale in their ADR.

## Substrate Alignment

This framework is the L3 companion to the feature-flags catalog. It draws
boundaries to two sibling concerns rather than absorbing them. The
static-versus-dynamic boundary with configuration-management is finalized:
static configuration, its source model, layering, precedence, and validation
are owned by configuration-management (configuration-management.no-hardcoded-config, configuration-management.no-swallowing-default,
configuration-management.startup-validation, configuration-management.layering-and-parity, configuration-management.strategy-adr), while a value that must change
behavior at runtime without a redeploy is a feature-flag governed here. The
secret boundary defers all credential handling to secrets-management:
evaluation context carries no secret values. The provisioning of any
flag-management service remains infrastructure-misconfiguration.

## Consequences

Positive: a coherent flag surface inheritable across services; changes that
fail safe and revert without a deploy; deterministic, debuggable rollouts; a
flag inventory that resists debt; kill switches that work when needed.

Negative or cost: the provider interface, the inventory, and the kill-switch
game-days are upfront and ongoing work; the typed taxonomy and context
allow-list impose a small discipline tax that pays back at the first averted
fail-open incident or stale-flag outage.

## References

See the authoritative-sources frontmatter: the OpenFeature specification,
Martin Fowler's Feature Toggles article, OWASP Top 10 A05:2021, and the MADR
format.

## Decision Review Schedule

The consumer's ADR is reviewed at substrate adoption, at the introduction of
a flag-management system or a change of provider, at the introduction of the
first operational kill switch, at the first use of a flag to gate AI or agent
behavior, and on a substrate-recommended annual cadence.
