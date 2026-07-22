<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Substrate-coverage matrix (reference template)

This file is a substrate-published reference template demonstrating
the consumer-side substrate-coverage matrix artifact. A
substrate-coverage matrix is the consumer-authored mapping of "this
feature's in-scope substrate rules" to "this feature's implementation
tasks and review obligations." It is the bridge between
`governance-manifest.yaml` (which declares the consumer's
consultation contract) and the consumer's working artifacts (specs,
plans, ADRs, code reviews).

**Substrate-internal location**: this file lives inside the
substrate at
`governance-commons/reference/templates/substrate-coverage-matrix.md`.
The substrate publishes it; consumers do not modify it in place. To
integrate, consumers copy this file out of the substrate into their
own per-feature workspace at a location such as
`/specs/<feature>/substrate-coverage.md` and adapt the rule list and
implementation-task entries to the feature under construction.

The substrate's contract is on the matrix structure and the
substrate rule reference format. The substrate does not constrain
consumer prose or task tracking conventions. The consumer freely
extends the template with project-specific columns (assignee, due
date, link to PR, etc.).

## Why this artifact exists

The consumer scaffold contract specified in
`governance-commons/spec/consumer-scaffold.md` defines five
obligations consumers satisfy to integrate Governance Commons
end-to-end. The substrate-coverage matrix operationalizes the work
between Obligation 1 (a complete manifest declaring what gets
consulted) and Obligation 4 (consultation evidence emission) for a
specific feature.

The matrix answers four questions for each feature:

1. Which substrate rules are in scope for this feature given the
   manifest's catalog selection and the feature's nature?
2. For each in-scope rule, what is the consumer's implementation
   task that satisfies the rule?
3. For each task, what evidence demonstrates satisfaction at code
   review and at the post-implementation consultation checkpoint?
4. Which substrate L3 decision frameworks require a consumer ADR
   for this feature?

Without the matrix, consumers either treat each substrate
consultation as a fresh pass through the entire catalog set (slow
and discouraging) or implicitly select rules to consult (drift-
prone, no audit trail). With the matrix, the consumer's
consultation events generated at each manifest checkpoint reference
specific matrix rows; closure verification confirms every row is
addressed before merge.

## How to use this template

The substrate-recommended workflow is four steps per feature:

1. **Read the feature spec.** Identify the systems and code paths
   the feature touches (request handler, data layer, authentication
   boundary, telemetry surface, etc.).
2. **Walk the manifest's `consults` selections.** For each
   checkpoint in the consumer's `governance-manifest.yaml`, list
   the catalogs and rules that apply to this feature's scope. Not
   every rule in every catalog applies to every feature; the
   matrix is the place to record the selection rationale.
3. **Fill the matrix template below** with the selected rules. For
   each row, the consumer specifies the implementation task,
   evidence, and any L3 ADR that the rule triggers.
4. **Reference the matrix from consultation events.** Each
   substrate consultation event the consumer's agents emit at a
   manifest checkpoint cites the matrix row (or rows) it
   addresses. Closure verification at the consumer's CI gate
   confirms every matrix row is referenced by at least one
   consultation event before merge.

The matrix is a living artifact within the feature's lifetime; it
is updated when the feature's scope changes during design or when
new substrate rules become in-scope (e.g., a new threat-modeling
finding adds an authorization rule that was not initially in
scope).

## Matrix structure

The matrix has three sections: a feature header, a per-rule table,
and a per-L3 ADR list. Each section's purpose is documented inline.

### Section 1: Feature header

Identifies the feature and pins the substrate context.

```yaml
feature:
  name: <feature-name>
  spec-location: <path-to-feature-spec>
  owner: <engineer-or-team>
  manifest-location: <path-to-governance-manifest.yaml>
  substrate-commons-version: <semver>
  substrate-profile: <profile-name>
  matrix-authored-date: <YYYY-MM-DD>
  matrix-last-updated: <YYYY-MM-DD>
```

The `substrate-commons-version` field anchors the matrix to a
specific substrate release; substrate evolution between matrix
authoring and feature completion is the consumer's responsibility
to reconcile (Charter Article VII compatibility-with-consumers
governs substrate-side change discipline).

### Section 2: Per-rule matrix

Each row covers one substrate rule that is in scope for the
feature. The substrate-recommended columns are:

| Column | Purpose |
|---|---|
| `Rule ID` | The substrate rule identifier (`authentication.password-hashing`, `input-validation.type-narrowing-at-boundary`, etc.). |
| `Layer` | L1 mechanical / L2 semantic / L3 judgmental. |
| `Catalog` | The concern catalog the rule lives in. |
| `In-scope rationale` | Why this rule applies to this feature. One sentence. |
| `Implementation task` | What the engineer does to satisfy the rule. |
| `Evidence at review` | What the reviewer or agent looks for to confirm satisfaction. |
| `Status` | `planned` / `in-progress` / `satisfied` / `n/a-with-justification`. |
| `Consultation event ref` | The event ID or timestamp of the consultation that referenced this row. |

Consumers add columns as needed (PR link, deferred-to-ticket, etc.)
without changing the row structure the substrate cares about.

### Section 3: Per-L3 ADR list

L3 rules trigger consumer ADRs that document trade-off decisions.
Each in-scope L3 rule produces one ADR (occasionally two, when one
L3 decision feeds another like authentication.authentication-strategy → authentication.mfa-factor-selection). The
list section records:

| Column | Purpose |
|---|---|
| `L3 Rule ID` | The substrate rule that requires the ADR. |
| `Decision framework MADR` | The substrate-published `decision-frameworks/<name>.madr.md` consulted. |
| `Consumer ADR location` | Where the consumer's ADR lives (`/docs/decisions/ADR-XXX-*.md`). |
| `Status` | `drafted` / `under-review` / `accepted` / `superseded`. |
| `Pre-build gate cleared` | Yes/No; ADR acceptance is the pre-build gate per the substrate consultation pattern. |

## Worked example: a feature touching authentication and input validation

The following worked example illustrates a substrate-coverage matrix
for a small feature ("password reset via emailed one-time token").
The example is purely illustrative; consumers adapt the details to
their own features.

### Section 1: Feature header (example)

```yaml
feature:
  name: password-reset-via-email-otp
  spec-location: /specs/password-reset/spec.md
  owner: identity-team
  manifest-location: /governance-manifest.yaml
  substrate-commons-version: 0.5.0
  substrate-profile: production-grade-baseline
  matrix-authored-date: 2026-06-01
  matrix-last-updated: 2026-06-15
```

### Section 2: Per-rule matrix (example)

| Rule ID | Layer | Catalog | In-scope rationale | Implementation task | Evidence at review | Status | Consultation event ref |
|---|---|---|---|---|---|---|---|
| `authentication.password-hashing` | L1 | authentication | Feature stores recovery-token hash if implementation chooses persisted token (vs. signed token). | Use Argon2id via the team's `crypto.HashToken()` wrapper; never store raw token. | Semgrep run finds no MD5/SHA1/SHA256 usage on token storage path. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-authentication.password-hashing |
| `authentication.no-credentials-in-urls` | L1 | authentication | Reset link is a URL with embedded token. | Construct reset URL with token in body of POST after user clicks link, never in GET query string. | Semgrep run finds no credentials-in-URL in router definitions. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-authentication.no-credentials-in-urls |
| `authentication.timing-safe-comparison` | L1 | authentication | Token comparison happens at validation time. | Use `crypto/subtle.ConstantTimeCompare` (Go) when comparing stored hash to candidate. | Semgrep run finds no `==` or `bytes.Equal` on token bytes. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-authentication.timing-safe-comparison |
| `authentication.rate-limiting` | L2 | authentication | Feature creates a new password setting flow. | Enforce password-strength policy on the reset confirmation step using shared `policy.EnforcePassword()`. | Review-checklist `authentication.rate-limiting-password-strength-policy.md` walked at PR; satisfied. | satisfied | ev-2026-06-15T09:14:33Z-post-implementation-authentication.rate-limiting |
| `authentication.mfa-enrollment` | L2 | authentication | Reset flow is a sensitive account-modification action. | Send notification email to user's existing primary email on reset request and on successful reset. | Review-checklist `authentication.mfa-enrollment-account-change-notification.md` walked. | satisfied | ev-2026-06-15T09:14:33Z-post-implementation-authentication.mfa-enrollment |
| `input-validation.parameterized-queries` | L1 | input-validation | Token-validation handler reads from request body and queries the user table. | Use parameterized query for token lookup; ORM enforces this. | Semgrep run finds no string concatenation in SQL on this path. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-input-validation.parameterized-queries |
| `input-validation.schema-validation-at-boundary` | L2 | input-validation | Reset confirmation accepts a free-text new password. | Validate at boundary: length 8-128 chars, no NUL, no whitespace-only. | Review-checklist `input-validation.schema-validation-at-boundary-validation-at-boundary.md` walked. | satisfied | ev-2026-06-15T09:14:33Z-post-implementation-input-validation.schema-validation-at-boundary |
| `logging.no-sensitive-data-in-logs` | L1 | logging | Reset flow logs success and failure events for audit. | Use `log.SafeFields(...)` helper that scrubs PII before emission. | Semgrep run finds no raw email/token in log calls on reset path. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-logging.no-sensitive-data-in-logs |
| `observability.no-sensitive-data-in-telemetry` | L1 | observability | Reset success/failure produces metrics. | Use the `metrics.RecordAuthEvent()` wrapper that strips identifiers from labels. | Semgrep run finds no PII metric labels. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-observability.no-sensitive-data-in-telemetry |
| `error-handling.no-stack-trace-in-response` | L1 | error-handling | Reset flow returns errors to clients. | All error responses use the `errors.UserSafe()` wrapper that excludes stack traces. | Semgrep run finds no raw exception in HTTP response on reset path. | satisfied | ev-2026-06-14T15:22:01Z-pre-commit-error-handling.no-stack-trace-in-response |
| `testing-strategy.critical-path-coverage` | L2 | testing-strategy | Critical-path coverage required; reset is on the authentication critical path. | Integration tests cover happy path, expired-token, replayed-token, wrong-user-token, throttled-request. | Review-checklist `testing-strategy.critical-path-coverage-critical-path-coverage.md` walked; 5 integration tests passing. | satisfied | ev-2026-06-15T09:14:33Z-post-implementation-testing-strategy.critical-path-coverage |
| `authentication.authentication-strategy` | L3 | authentication | New authentication-adjacent flow triggers strategy review. | Author ADR for password-reset strategy (token vs. magic link vs. delegated). | ADR `/docs/decisions/ADR-024-password-reset-strategy.md` accepted at pre-build gate. | accepted | ev-2026-06-05T10:00:00Z-post-spec-authentication.authentication-strategy |

### Section 3: Per-L3 ADR list (example)

| L3 Rule ID | Decision framework MADR | Consumer ADR location | Status | Pre-build gate cleared |
|---|---|---|---|---|
| `authentication.authentication-strategy` | `governance-commons/decision-frameworks/auth-strategy.madr.md` | `/docs/decisions/ADR-024-password-reset-strategy.md` | accepted | Yes (2026-06-05) |

The matrix includes 12 rules total: 8 L1 mechanical, 4 L2 semantic
(actually 3 L2 in the example above; an actual feature may select
more or fewer), and 1 L3 judgmental. The feature's manifest declares
the post-spec-drafting checkpoint produced the matrix; the
pre-commit checkpoint references the L1 matrix rows via Semgrep
findings; the post-implementation checkpoint references the L2
matrix rows via the code-review-agent's consultation events.

## Variations on the template

The substrate intentionally does not specify a single format. Two
common variations consumers adopt:

- **CSV-backed matrix** for teams that prefer a spreadsheet
  workflow. The columns above translate directly to CSV; the
  template's structure is preserved. Closure verification reads the
  CSV at CI time the same way it reads the Markdown table.
- **Issue-tracker-backed matrix** for teams that prefer
  Jira/Linear/GitHub-Issues as the source of truth. The matrix
  becomes a saved query (filter by label `substrate-coverage` and
  feature epic), and the per-row implementation task and evidence
  fields live on the issue. The matrix Markdown file then becomes a
  snapshot or pointer document.

The substrate's contract is on the **information captured**, not
on the **format used**. Consumers select the form that fits their
tooling.

## What this template does NOT specify

- **Workflow automation.** The substrate does not ship the script
  that walks the manifest and produces the initial matrix shell;
  consumers implement this against their own conventions or run the
  threat-modeling-agent (per
  `governance-commons/reference/agents/threat-modeling-agent.md`)
  which produces the initial matrix as part of its
  post-spec-drafting deliverable.
- **Automatic closure detection.** Closure verification consumes
  the matrix at CI gate time; the verification logic itself is
  consumer-side tooling (see the reference CI workflow at
  `governance-commons/reference/workflows/governance-commons-gate.yml`
  Steps 5-8 for the evidence-validation pattern).
- **Cross-feature aggregation.** Multiple features may share an L3
  ADR (e.g., the same authentication-strategy ADR covers password
  reset, registration, and login features). Cross-feature
  aggregation is a consumer-side concern; the substrate-coverage
  matrix is per-feature.

## Maintenance

This reference template is updated when:

- The substrate's consultation contract changes in a way that
  affects the matrix's columns or sections.
- A new substrate rule layer is introduced (the L1/L2/L3 model is
  stable; no expansion expected in the substrate's 1.0 window).
- Consumer feedback identifies a recurring matrix structure that
  the substrate should publish as an alternative template format.

Substrate-author Article VII compatibility-with-consumers
obligation governs the change discipline: material changes
accompany substrate minor version bumps; editorial clarifications
may be made non-versionedly.

End of template.
