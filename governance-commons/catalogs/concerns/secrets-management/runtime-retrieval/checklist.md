---
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
binding-id: "review-checklists.secrets-management.runtime-retrieval-runtime-retrieval"
title: "secrets-management.runtime-retrieval review checklist: runtime secret retrieval from a dedicated secrets management platform"
substrate-rule: "secrets-management.runtime-retrieval"
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
  - "Code changes that add a new external service integration requiring a credential"
  - "Code changes that touch secret retrieval, credential rotation hooks, or secrets-platform client code"
  - "New service deployment that requires production credentials"
  - "Periodic security self-assessment of secret handling"
---

# secrets-management.runtime-retrieval review checklist: runtime secret retrieval from a dedicated secrets management platform

## How to use this binding

Reviewers answer every question below when reviewing pull requests
that match the review triggers above. Unanswered items block
merge. Answers are recorded in the pull-request review thread;
consumers adapt the format to their tooling.

The checklist is also useful for periodic self-assessment outside
the pull-request flow.

## Review questions

### 1. Retrieval source: where does the secret come from at runtime?

A production secret should be retrieved from a substrate-recognized
secrets management platform (per the consumer's secrets-management.platform-selection ADR),
not from a plain environment variable populated by the deployment
process alone.

What good looks like: the application reads the secret via a
secrets manager client (HashiCorp Vault, AWS Secrets Manager, GCP
Secret Manager, Azure Key Vault, Kubernetes external-secrets
operator, or equivalent); retrieval happens at startup or on first
use; the platform's audit log records the access.

What needs follow-up: secret comes from an environment variable
populated by a static deployment template; secret comes from a
file on disk that was placed there during build; secret hardcoded
or templated at build time.

### 2. Caching and refresh: how does the application handle credential rotation?

When the secrets platform rotates a credential, the application
must pick up the new value within a defined window without manual
intervention.

What good looks like: the application re-reads on a TTL or on
authentication failure; client libraries provided by the platform
handle refresh; the refresh interval is bounded (substrate-
recommended ceiling 1 hour for short-lived secrets, 24 hours for
long-lived).

What needs follow-up: secret read once at startup and never
refreshed; refresh on a multi-day cycle that defeats rotation;
manual restart required to pick up a rotated credential.

### 3. In-memory handling: how is the secret held while in use?

The secret should be held in a typed wrapper that masks under
string conversion (per secrets-management.no-secrets-in-logs redaction discipline) and
that does not survive serialization.

What good looks like: a SecretString or equivalent wrapper class;
__repr__ and __str__ return a redacted placeholder; the wrapper
does not implement __json__ or pickling protocols that would
serialize the value.

What needs follow-up: secret held as a plain string in a long-
lived global; secret passed through structures that serialize
(error reports, telemetry payloads); secret stored in an object
attribute that gets logged elsewhere.

### 4. Boundary discipline: does the secret cross only the boundaries it must?

A secret retrieved for use in component A should not be passed to
component B that does not need it.

What good looks like: the retrieval point is close to the use
site; helper functions receive opaque tokens that they pass through
to the platform client rather than receiving raw secret values;
inter-service requests do not propagate credentials in headers or
bodies unless required by the protocol.

What needs follow-up: a credential retrieved at application
startup is passed down through many function arguments before
finally being used; a service-to-service call carries the calling
service's database credential rather than its own service-account
token.

### 5. Failure modes: how does the application behave when the secrets platform is unavailable?

The platform's availability becomes part of the application's
availability. The behavior on platform failure must be deliberate.

What good looks like: cached value continues to work within the
cache TTL; fail-closed posture for new operations that need a
fresh secret; explicit health-check status that surfaces the
platform-unreachable state; operational runbook documents the
response.

What needs follow-up: application crashes on first retrieval
failure with no graceful degradation; application falls back to a
default-or-empty value that succeeds (silently degraded auth);
platform unreachable causes silent data loss.

### 6. Identity used to retrieve: which identity authenticates to the secrets platform?

Workload identity (IAM role, Kubernetes service account, machine
identity) is the substrate-recommended path. A static credential
that itself authenticates to the secrets platform is a chicken-
and-egg failure pattern.

What good looks like: the workload assumes an IRSA role, a GCP
service account via workload identity federation, a Kubernetes
service account via projected token, or an Azure managed identity.
The platform validates the workload identity directly; no static
credential is shipped to the workload.

What needs follow-up: a static API key is shipped to the
workload to authenticate to the secrets platform; the same
static key is shared across many workloads; the bootstrap
credential is itself never rotated.

### 7. Per-environment isolation: are non-production secrets distinct from production?

A development credential should not work in production and vice
versa. Cross-environment secret reuse is a common path for staging
incidents to spill into production.

What good looks like: each environment (dev, staging, production)
has a distinct namespace or vault in the secrets platform; the
workload identity per environment only sees its own namespace;
local development uses developer-issued credentials that are
short-lived.

What needs follow-up: a single secret used across all
environments; production credentials accessible from developer
workstations; staging deploys against the production secret
store with read-only permissions that nevertheless allow secret
exfiltration.

### 8. Telemetry and audit: are retrievals visible?

Secret retrievals are operationally important events. They should
be visible to security operations.

What good looks like: the secrets platform emits an audit event
for every retrieval (which identity, which secret, when); audit
events flow to the security log aggregator; alerts fire on
unusual patterns (retrieval volume spike, retrieval from an
unexpected identity).

What needs follow-up: platform audit logs not enabled; audit logs
collected but not analyzed; no alerting on anomalous patterns.

## Reviewer attestation

When all eight questions have been answered with "what good
looks like" outcomes, the reviewer records attestation in the
pull-request review:

```
secrets-management.runtime-retrieval review checklist: complete
- Retrieval source: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Caching and refresh: PASS / FOLLOW-UP / EXEMPT-with-rationale
- In-memory handling: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Boundary discipline: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Failure modes: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Identity used to retrieve: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Per-environment isolation: PASS / FOLLOW-UP / EXEMPT-with-rationale
- Telemetry and audit: PASS / FOLLOW-UP / EXEMPT-with-rationale
```

FOLLOW-UP items block merge until resolved. EXEMPT items require
documented rationale in the pull-request thread.

## Cross-reference

- Substrate rule: secrets-management.runtime-retrieval in catalogs/concerns/secrets-management.oscal.yaml
- Test binding: test-template.md
- Good examples: examples/secrets-management/runtime-retrieval-good.md
- Anti-patterns: examples/secrets-management/runtime-retrieval-anti-pattern.md
- Related: secrets-management.platform-selection (platform selection decision)
