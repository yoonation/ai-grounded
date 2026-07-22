---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.secrets-management.least-privilege-access-least-privilege-access"
title: "secrets-management.least-privilege-access review checklist: least-privilege secret access"
substrate-rule: "secrets-management.least-privilege-access"
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
  - "Code changes that grant a workload, service, or human new access to a secret"
  - "Code changes that touch IAM policies, vault policies, or RBAC for the secrets platform"
  - "New workload deployment requesting access to existing secrets"
  - "Periodic access review (substrate-recommended quarterly)"
---

# secrets-management.least-privilege-access review checklist: least-privilege secret access

## How to use this binding

Reviewers answer every question below when reviewing access-
granting changes or during periodic access review. The questions
apply to both human access (engineers, support, on-call) and
workload access (services, jobs, CI pipelines).

## Review questions

### 1. Scope: is the access scoped to specific secrets rather than blanket policies?

A workload that needs one database password should not have read
on all secrets in the namespace.

What good looks like: per-secret policy grants; resource paths
in the policy enumerate exact secret names; wildcard scopes are
narrow and documented (e.g., a logging shipper that needs every
secret-X-encryption-key has wildcard but only over that
namespace).

What needs follow-up: blanket grants to all secrets in a
namespace where only specific secrets are needed; wildcard
scopes broader than necessary; grants on the secrets platform's
admin path to non-administrator workloads.

### 2. Operations: are read-only operations distinguished from write or rotate?

A workload that consumes a secret needs read; only the rotation
job needs write or rotate. The grant should reflect the
difference.

What good looks like: separate policies for read, write, and
rotate; consumer workloads have read only; the rotation tooling
has rotate; humans rarely have write on production secrets
outside of break-glass scenarios.

What needs follow-up: all grants include write because the
default policy template includes it; rotation jobs and consumer
workloads share the same policy; developer access to staging is
write-by-default when read would suffice.

### 3. Identity: does each access path correspond to a distinct workload identity?

When two workloads share an identity, security operations cannot
tell which workload accessed a secret. Granting access to a
shared identity defeats audit.

What good looks like: each workload (service, job, CI pipeline)
has its own identity; the identity grants are individually
configured; audit logs identify the specific workload.

What needs follow-up: many workloads share a single service
account because it has the right grants; a "platform" identity
covers everyone; the same identity covers production and non-
production workloads.

### 4. Human access: who has access and under what conditions?

Human access to production secrets should be exception-based,
time-bounded, and audited. Standing access for engineers is the
substrate-discouraged pattern.

What good looks like: no standing human access to production
secrets; break-glass procedure exists, is time-bounded, and is
recorded; emergency access requires multi-party approval; review
of human access happens on a documented cadence.

What needs follow-up: engineers have permanent access to
production secrets "in case they need to debug"; break-glass
procedure exists but is the routine path; access reviews are
overdue or have never happened.

### 5. Just-in-time access: where the platform supports it, is just-in-time access used?

Modern platforms (HashiCorp Vault dynamic secrets, AWS IAM
Identity Center temporary access, Teleport, Boundary) issue
short-lived credentials on demand. Just-in-time is the substrate-
recommended pattern for human and high-risk workload access.

What good looks like: human production access via just-in-time
provisioning that issues a credential for a bounded duration;
database access via Vault dynamic secrets that produce per-
session credentials; standing credentials minimized.

What needs follow-up: long-lived standing credentials for human
access; just-in-time capability exists in the platform but is not
configured; the just-in-time path exists but the bounded duration
is impractically long (multiple days).

### 6. Boundary services: are credentials issued by a boundary service rather than embedded in workloads?

Workloads should authenticate to boundary services (databases,
APIs) via tokens issued by the secrets platform, not via
credentials embedded in the workload's configuration.

What good looks like: workload requests a database credential at
startup or per-session; the secrets platform issues a per-workload
or per-session credential; the database authenticates the
credential and applies the workload's role permissions.

What needs follow-up: every workload gets the same database
credential; database credentials are baked into deployment
manifests; the database has a single application user that all
workloads share.

### 7. Cross-environment policy enforcement: do production grants stay in production?

Policy templates that span environments (a single Terraform
module that deploys to all environments) need explicit
environment scoping or they create cross-environment grants.

What good looks like: policies are environment-specific by
construction (separate Terraform workspaces or state files per
environment); a grant in staging cannot accidentally apply to
production; environment promotion is explicit.

What needs follow-up: a single Terraform state covers all
environments and a misconfigured variable could grant production
access to a staging workload; policies are templated but
environment selection happens at apply time without strong
guards.

### 8. Access review evidence: is there evidence the access list is reviewed?

Standing access drifts. The protection against drift is
periodic review.

What good looks like: the secrets platform's access logs are
reviewed on a cadence (substrate-recommended quarterly); the
review produces an artifact (signed-off report, ticket, ADR
amendment); access that has not been used in a defined window
is revoked.

What needs follow-up: no documented review cadence; reviews
happen but produce no artifact; the review is a perfunctory
sign-off without genuine evaluation.

## Reviewer attestation

```
secrets-management.least-privilege-access review checklist: complete
- Scope: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Operations: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Identity: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Human access: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Just-in-time access: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Boundary services: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Cross-environment policy: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Access review evidence: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

## Cross-reference

- Substrate rule: secrets-management.least-privilege-access in catalogs/concerns/secrets-management.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/secrets-management/least-privilege-access-good.md
- Anti-patterns: examples/secrets-management/least-privilege-access-anti-pattern.md
