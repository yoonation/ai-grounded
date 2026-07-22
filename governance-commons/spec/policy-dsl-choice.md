<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Policy DSL Choice

Records the choice of Cedar as the policy expression language for
this commons, with full reasoning and the conditions under which the
choice should be revisited.

## Decision

**Cedar v4.x** is the policy DSL.

Policy files in this commons (under `policies/`) are written in
Cedar. Consuming frameworks wrap Cedar evaluation in a
Strategy-pattern interface so the underlying engine can be swapped
without changing consumer code.

## Why Cedar

### Properties Cedar provides

- **Strong typing** - Policy errors caught at compile time, not
 runtime. Misspelled attribute names fail loudly; in Rego they
 silently return `undefined`.
- **Designed for authorization** - Native concepts of principal,
 action, resource, context match the shape of governance policies.
- **Verifiable** - Cedar's authorizer is amenable to automated
 reasoning. Tools like the Cedar CLI can prove policy properties
 (e.g., "no two policies contradict") at static analysis time.
- **Simpler than Rego** - Smaller surface area, more focused. For
 engineers not already invested in OPA, the learning curve is
 smaller.
- **Performant** - Sub-millisecond evaluation latency in the
 reference implementation. Important for runtime use; useful even
 at build time.

### Alignment with future runtime framework

The planned runtime governance framework will consume the Microsoft
Agent Governance Toolkit (or an equivalent), which uses Cedar.

Choosing Cedar for build-time creates natural cross-framework
consistency: the same policies can be reasoned about in both
contexts, and policy primitives in this commons (`policies/`) are
directly consumable by both frameworks.

If we'd chosen a different DSL for build-time, every shared policy
would need translation, and that translation is itself a source of
divergence.

## Alternatives evaluated

### OPA / Rego

**Open Policy Agent** with the Rego policy language.

Pros:
- Larger ecosystem and community than Cedar
- More mature tooling (Conftest, Gatekeeper, etc.)
- CNCF Graduated project (institutional stability)
- Widely adopted in cloud-native and Kubernetes contexts

Cons:
- Dynamic typing surface errors at runtime not compile time
- Steeper learning curve (logic programming roots, not familiar to
 most engineers)
- Less amenable to formal analysis than Cedar
- Larger runtime footprint than Cedar's reference implementation

OPA/Rego is the documented fallback if Cedar adoption stalls.

### Custom DSL or schema-based policies (CUE, JSON Schema with logic)

Pros:
- No DSL learning curve if using existing schema knowledge
- Tight integration with existing tooling

Cons:
- Reinvents wheels poorly - none of these are designed for
 authorization specifically
- Worse cross-framework portability than either Cedar or Rego
- Audit credibility lower than established DSLs

Rejected on "don't invent your own DSL" grounds.

### AWS IAM policy language

Pros:
- Universally known
- Native AWS integration

Cons:
- AWS-specific semantics leak in (resource ARNs, AWS condition keys)
- Not designed for AI agent governance scenarios
- Cannot express the conditions our policies need

Rejected on portability and fit grounds.

### XACML

Pros:
- Standardized (OASIS)
- Mature

Cons:
- XML-based (verbose, hard to review in PRs)
- Limited modern tooling
- Largely abandoned by industry in favor of Cedar/Rego

Rejected.

## When to revisit

This decision should be re-evaluated if any of these trigger
conditions occur:

### Strong triggers (re-evaluate immediately)

- **Cedar project stalls or is abandoned** - defined as: no releases
 in 18 months, primary maintainers depart, AWS deprioritizes
- **Microsoft Agent Governance Toolkit abandons Cedar** - the
 alignment argument disappears
- **Regulatory body mandates a specific DSL** - happens occasionally
 with NIST or sector regulators
- **A major consumer of this commons cannot use Cedar** - e.g.,
 legal restrictions, license incompatibility

### Weak triggers (review during quarterly maintenance)

- OPA/Rego adds first-class agent-policy primitives that Cedar lacks
- Cedar adoption fails to grow beyond current consumers in 12 months
- A new DSL emerges that's strictly better for AI governance specifically

## Migration plan if Cedar is replaced

If a future review concludes Cedar should be replaced:

1. Document the new decision in this file as an amendment
2. Bump commons VERSION to a major version (breaking change)
3. Migrate policy files in `policies/` to new DSL
4. Provide a transformation script for old policy logs in audit
  trails (to preserve historical context)
5. Update Strategy-pattern wrapper in consuming frameworks to use
  new engine
6. Run policy correctness tests against both old and new DSL during
  transition period
7. Archive old `policies/` directory as `policies-cedar-legacy/`
  rather than delete; auditors may still need to verify historical
  decisions

The Strategy pattern in consumers makes the migration tractable.
Consumer code that calls `evaluate_policy(actor, action, resource,
context)` doesn't change; only the wrapper implementation does.

## Anti-patterns

These behaviors compromise the policy layer:

- **Mixing DSLs** - Cedar for some policies, Rego for others "because
 this one is easier in Rego." Pick one DSL per commons version.
 Migration is a deliberate event, not a per-policy choice.
- **Inlining policy logic in hooks** - defeats the purpose of having
 a DSL. If a check uses policy semantics, it goes in a Cedar policy;
 if it's just deterministic enforcement, it's a hook.
- **Embedding business logic in policies** - policies authorize;
 they don't compute business logic. A policy can deny a fund
 transfer; it doesn't calculate the fund balance.
- **Versionless policies** - every policy file MUST declare a
 version. Versionless policies cannot be reasoned about over time.

## Cedar resources

- Cedar policy language docs: https://docs.cedarpolicy.com
- Cedar GitHub: https://github.com/cedar-policy/cedar
- Cedar in Microsoft Agent Governance Toolkit:
 https://github.com/microsoft/agent-governance-toolkit

## Decision history

  2026-05-11: Initial decision to adopt Cedar (commons v0.1.0)
        Maintainer: <github-handle>
        Reasoning: see above
        Alternatives considered: OPA/Rego, custom DSL, AWS IAM, XACML
        Next review: 2027-02-11 (or trigger condition)
