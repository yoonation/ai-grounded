<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: authentication.authentication-strategy authentication strategy MADR (forbidden)

Three patterns of substrate-non-compliant authentication strategy
decisions. Do not produce MADRs that look like these.

## Anti-pattern A: No MADR at all

The application begins implementing authentication directly. The
team picks password-based auth because it is familiar; they add
MFA "if time permits"; they add rate limiting in response to the
first credential-stuffing incident; they add breach corpus
screening after a security audit findings.

No decision document exists. Each substrate rule is implemented
reactively as gaps are discovered.

Why this violates authentication.authentication-strategy:
- The substrate's pre-build gate was not satisfied
- Strategy choice was implicit (default to passwords) rather
  than deliberate
- The reactive implementation pattern guarantees gaps because
  there is no inventory of what rules apply
- Periodic review has nothing to review against

This is the most common failure mode and the one the substrate
rule exists to prevent.

## Anti-pattern B: MADR exists but is content-free

```markdown
# ADR-007: Authentication

## Status
Accepted

## Context
We need authentication.

## Decision
We will use passwords with MFA.

## Consequences
Users will need to remember a password and use an authenticator app.
```

Why this violates authentication.authentication-strategy:
- Context section is two words and gives no information
- No decision drivers
- No considered options
- No substrate alignment statement
- Consequences are user-facing only; no inventory of substrate
  rules in scope
- No pros and cons analysis
- No review schedule

A reviewer applying the substrate's review checklist marks every
question FOLLOW-UP. The MADR is not accepted; implementation work
cannot proceed.

## Anti-pattern C: MADR is post-hoc rationalization

The application has already implemented password + MFA. After
the substrate is adopted, someone is tasked with "writing the
ADR to match what we have". The resulting MADR documents the
existing choice but skips the analysis.

```markdown
# ADR-007: Authentication Strategy

## Status
Accepted

## Context
ExampleApp authenticates users for [...descriptive text about
the application...]

## Decision
We use passwords with mandatory MFA (TOTP).

## Considered Options
1. Passwords with MFA (chosen)

## Substrate alignment
Aligned.

## Consequences
- Users need a password and authenticator
- Customer support handles password reset requests
- We rotate session cookies on login

## Decision review schedule
As needed.
```

Why this violates authentication.authentication-strategy:
- "Considered options" lists only the chosen option
- No comparative analysis (substrate-recommended passkeys
  alternative was never seriously considered)
- "Substrate alignment: Aligned" is unsupported (password+MFA is
  substrate-acceptable but not substrate-preferred for greenfield
  consumer applications; the MADR does not address the deviation)
- Decision drivers are absent
- Substrate-rule inventory in Consequences is incomplete (no
  mention of authentication.password-hashing password hashing, authentication.password-policy password
  policy, authentication.mfa-enrollment MFA enrollment, etc.)
- Review schedule "as needed" is not a schedule

Reviewer applies the checklist: most questions FOLLOW-UP. The
MADR must be amended with the missing analysis before the
substrate considers the decision documented.

## Anti-pattern D: MADR exists but documented decision does not match running implementation

The application's MADR documents passkey-primary with federated
recovery. The running implementation only has the password path;
passkey implementation was deferred and forgotten.

Why this violates authentication.authentication-strategy:
- The MADR is stale; the running implementation has diverged from
  the documented decision
- This is the same as Anti-pattern A in practice (no authoritative
  decision document) but worse because the existence of a stale
  MADR creates false confidence

Remediation: either update the implementation to match the MADR
or supersede the MADR with a new ADR documenting the actual
decision. Substrate does not accept silent drift.

## Anti-pattern E: MADR deviates from substrate without justification

```markdown
# ADR-007: Authentication Strategy

## Decision
We will use SMS one-time codes as the primary authentication
factor.

## Substrate alignment
Deviation.
```

Why this violates authentication.authentication-strategy:
- SMS as primary factor deviates from substrate guidance (SMS is
  substrate-acceptable only as fallback for MFA, not as primary
  factor, due to SIM-swap risk)
- The MADR acknowledges the deviation but does not justify it
- A reviewer applying the checklist marks "Substrate alignment
  explicit: FOLLOW-UP" because deviation requires reasoning

The substrate does not require the consumer to pick substrate-
preferred options. It requires deviations to be explicit AND
reasoned. "Deviation" without explanation is not sufficient.

## Common failure mode across all anti-patterns

The team views the MADR as paperwork to complete rather than as
the architectural decision itself. The MADR is treated as
documentation of a decision made elsewhere (in chat, in
hallway conversations, by default), rather than as the locus
of the decision.

The substrate's L3 rule design exists precisely to prevent this
failure mode. The MADR IS the decision. If the MADR is
content-free, the decision is content-free. The pre-build gate
is the mechanism that forces the decision to happen in the MADR
rather than in unrecorded conversations.

## Cross-reference

- Substrate rule: authentication.authentication-strategy in catalogs/concerns/authentication.oscal.yaml
- Decision framework binding: decision.md
- Review binding: checklist.md
- Good example: examples/authentication/authentication-strategy-good.md
