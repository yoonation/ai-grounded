---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.secrets-management.rotation-policy-rotation-policy"
title: "secrets-management.rotation-policy review checklist: secret rotation policy and execution"
substrate-rule: "secrets-management.rotation-policy"
substrate-rule-href: "rule.yaml"
layer: "L2"
lifecycle-status: "stable"
commons-version: "0.2.0"
binding-version: "1.0.0"
author: "myoung"
authored: "2026-05-20"
last-modified: "2026-05-29"
reviewer: "myoung-self-attested"
reviewed: "2026-05-22"
entered-status-at: "2026-05-22"
attestation-mechanism: "Charter Section 2.4.1 (solo-author attestation; parent-inherited per Section 10 settled decision 23). Lifecycle status follows the parent catalog rule; M3 Session 4 L2 binding format refactor is structural and information-preserving and does not constitute a fresh attestation event."
ai-assistance: "AI drafted the original content per the substrate-author's intent at the time of authoring. Refactored from markdown-wrapped-YAML to MADR-pattern YAML-frontmatter + markdown-body at M3 Session 4 (2026-05-29); refactor is information-preserving and does not alter review-question content."
review-triggers:
  - "Code changes that introduce a new credential class"
  - "Code changes that touch credential rotation procedures or schedulers"
  - "Periodic security self-assessment (substrate-recommended quarterly)"
  - "Incident response review identifying a credential compromise"
---

# secrets-management.rotation-policy review checklist: secret rotation policy and execution

## How to use this binding

Reviewers answer every question below when reviewing pull
requests that match the review triggers above, or during the
periodic self-assessment. Unanswered items block merge or
escalate as findings in the self-assessment.

## Review questions

### 1. Coverage: which credential classes have documented rotation?

Every credential in scope for the application should have a
rotation policy documented. The substrate recognizes the
following classes:

- Database credentials (application user accounts)
- API keys to third-party services
- OAuth client secrets
- Encryption keys (data-at-rest, signing, TLS)
- Service-to-service tokens
- Webhook signing secrets
- Machine identities (PKI certificates)

What good looks like: an inventory exists (in the secrets
platform, in an ADR, in a SECURITY.md) listing each credential
class with its rotation cadence and owner.

What needs follow-up: some credential classes have rotation,
others are ad-hoc; no central inventory; inventory exists but is
older than 6 months and out of date.

### 2. Cadence: are the cadences appropriate for each class?

Different credential classes warrant different cadences. The
substrate-recommended starting points (consumers tune by risk):

- Short-lived workload tokens (STS, vault dynamic): minutes to hours
- API keys to high-value third parties: 90 days
- API keys to low-risk third parties: 180 days to 1 year
- Database credentials: 90 days (or dynamic per-session via Vault, Boundary)
- TLS certificates: per CA recommendation, typically 90 days for automation, 1 year for manual
- Signing keys: 1 year minimum, longer with HSM protection
- OAuth client secrets: 1 year, sooner on suspected compromise

What good looks like: cadences within or stricter than the
substrate-recommended ranges; rationale documented for any
deviation.

What needs follow-up: cadences significantly longer than the
ranges with no documented rationale; "never rotated" credentials
for classes that should rotate; multi-year cadences for short-
lived classes.

### 3. Automation: is rotation automated or manual?

Manual rotation is high-effort and error-prone. The substrate
strongly prefers automated rotation where the platform supports
it.

What good looks like: the secrets platform handles rotation via
its native mechanism (Vault database secrets engine, AWS Secrets
Manager rotation Lambda, GCP Secret Manager rotation, Azure Key
Vault rotation policy); the application picks up new values via
the runtime retrieval pattern from secrets-management.runtime-retrieval.

What needs follow-up: rotation is a manual operator task
scheduled on a calendar; rotation requires application restart
and is therefore deferred; rotation procedure exists but has not
been exercised in the last cadence window.

### 4. Coordination: do dependent systems pick up rotated values without service disruption?

Rotation that breaks service is rotation that does not happen.
The procedure must produce zero-downtime rotation for the typical
case.

What good looks like: dual-key window (old credential still
accepted for a TTL after rotation); application picks up new
credential within the dual-key window; rotation events are
correlated with deployment freezes only when truly necessary.

What needs follow-up: rotation requires service restart;
rotation invalidates the old credential immediately with no dual-
key window (impossible to roll forward atomically across replicas);
dependent systems retry failed authentication indefinitely after
rotation.

### 5. Compromise indicators: what triggers an out-of-band rotation?

Beyond the scheduled cadence, certain events should trigger
immediate rotation: detected leak (logs, source code,
ex-employee), platform incident at the secrets platform itself,
suspicious access patterns.

What good looks like: a documented list of compromise indicators;
the incident response playbook references the rotation procedure
by name; the procedure is exercised in tabletop exercises.

What needs follow-up: no documented compromise-triggered rotation
procedure; the procedure exists but has never been exercised;
the procedure assumes a coordinated operator action that may not
be available during an incident.

### 6. Audit trail: is rotation evidenced?

Rotation events should be visible after the fact for compliance
and incident response.

What good looks like: the secrets platform records rotation
events in its audit log; events flow to the security log
aggregator; reviewers can verify the rotation actually happened
when the schedule said it should.

What needs follow-up: no audit trail of rotation; audit logs
exist but are not retained long enough to verify cadence;
rotation logged but with insufficient detail to confirm the new
credential is in use.

### 7. Decommissioning: are old credentials revoked?

Rotation produces a new credential and should produce a revoked
old credential. Neither half of the rotation is complete alone.

What good looks like: revocation is part of the rotation
procedure; revocation happens after the dual-key window expires;
revoked credentials no longer authenticate at the issuing system.

What needs follow-up: rotation creates new credentials but old
credentials remain valid (accumulating credential bloat); the
revocation step is manual and is sometimes skipped; revocation
status is unclear because the issuing system does not have a
revocation list.

### 8. Cross-environment isolation: are non-production rotations isolated from production?

Rotation exercises in dev or staging should not affect
production, and vice versa.

What good looks like: rotation scripts and schedulers operate
within their environment; dev rotation does not rotate
production secrets; the runbook for production rotation is
explicit about the production scope.

What needs follow-up: rotation tooling spans environments
without strict isolation; an operator running rotation in dev
could accidentally rotate production credentials; environment
detection is via naming convention only (fragile).

## Reviewer attestation

```
secrets-management.rotation-policy review checklist: complete
- Coverage: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cadence: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Automation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Coordination: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Compromise indicators: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Audit trail: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Decommissioning: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cross-environment isolation: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge or appear as self-assessment
findings until resolved.

## Cross-reference

- Substrate rule: secrets-management.rotation-policy in catalogs/concerns/secrets-management.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/secrets-management/rotation-policy-good.md
- Anti-patterns: examples/secrets-management/rotation-policy-anti-pattern.md
