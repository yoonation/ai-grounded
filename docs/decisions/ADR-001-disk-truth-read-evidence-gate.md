<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# ADR-001: Disk-truth read-evidence gate on closure-verified

**Status**: Accepted
**Date**: 2026-06-23
**Decision-maker**: Myoung Hong (maintainer)
**Related artifacts**: `.claude/hooks/verify_loop_closure.py`, `.claude/hooks/test_verify_loop_closure.py`, `.specify/schemas/events.schema.json`, `.claude/agents/closure-auditor.md`, `.specify/memory/constitution.md` Section 6.2, commit `86dc27b`
**Related ADRs**: none (first ADR)

## Context

The feature 003 gate-verification run surfaced roughly fifteen manual
interventions, almost all of one shape: the framework verified
DECLARATIONS while the operator verified ACTUALS. The most expensive
recurring class was a `closure-verified` event whose verdict rested on
prose alone, with no record that the auditor actually read the artifact
it claimed to verify. Concrete instances in 003: TM-010..015 and
PERF-001 were cleared by `closure-verified` events backed by prose-only
reasoning and no re-checkable artifact reference.

Before this decision, `verify_loop_closure.py` accepted a
`closure-verified` on the existence of the event alone (constitution
Section 6.2 enumerated `closure-claimed`, `closure-verified`, or
`overridden` as closure, with no read condition). A green guardrail is
itself a self-report; "self-reports cannot verify their own honesty"
was the run's through-line. The constitution already mandates
provenance attestation for AI-assisted work (Section 3.2) and supply
chain (Section 5.7, SLSA v1.0 plus in-toto), and fail-closed defaults
(Section 2.3). Those principles were not yet applied to closure
verification itself.

## Decision

A `closure-verified` event must carry `closure_evidence.read` with a
`path` and the `sha256` of the artifact the verifier read. At commit
time `verify_loop_closure.py` independently re-reads that path and marks
the item `unverified` (blocking) if the read block is absent, resolves
to no file, points at an empty file, or carries a malformed digest. If
the artifact's current digest differs from the recorded one, the hook
warns without blocking (drift visibility). This binds `closure-verified`
only; `closure-claimed` (cross-tool self-attestation) and `overridden`
(ADR acceptance) are unchanged. `closure_evidence.read` is formalized in
the events schema additively; historical events without it still
validate, and the requirement is enforced by the gate for
`closure-verified` specifically, not by schema validation.

## Rationale

The read block is a lightweight instance of the in-toto verification
predicate pattern the constitution already adopts (Sections 3.2, 5.7):
a verifier records what artifact it checked, by digest, so the claim is
independently re-checkable rather than taken on faith. It applies the
fail-closed default of Section 2.3 to closure verification: a
verification with no readable artifact is rejected, not allowed. The
proof harness uses a gate-falsifier (neutralize the read check, confirm
a test then catches the regression), which is mutation testing, the
discipline whose entire motivation is that coverage is misleading when
statements are covered but their outcome is not asserted upon, the exact
F15/F16/F17 failure family from the run.

Binding `closure-verified` only preserves cross-tool operation: per
`.claude/docs/agent-coordination.md`, Layer 1 (claim) plus Layer 3
(hook) work without Layer 2 (closure-auditor), and `closure-claimed` is
the path non-Claude tools use. Requiring read evidence on
`closure-claimed` would have broken them.

Honest limitation, recorded so it is not overclaimed: the read block is
attestation-shaped, not attestation-strength. It is an unsigned
honesty-ledger entry (recorded digest plus path), not a DSSE-signed
cosign/Rekor attestation. It raises the bar from a prose claim to a
claim with a re-readable, digest-checked artifact reference, which is
proportionate to a cooperating-agent threat model. It does not
cryptographically bind the verifier's identity or prevent a fabricated
digest. If the threat model ever includes a malicious verifier, the
upgrade path is signing, already specified in
`governance-commons/attestation/`.

This ADR is retroactive. The change shipped in commit `86dc27b` ahead of
this record, which was a process gap against Section 2.2 (ADRs are
pre-build gates). This ADR and the accompanying Section 6.2 amendment
reconcile that gap; subsequent gate-behavior changes record the ADR
first.

## Consequences

Positive: a prose-only `closure-verified` that the prior gate allowed
(exit 0) now blocks (exit 1); verification leaves a re-checkable trace;
the closure-auditor's reads become machine-verifiable rather than
honor-system; the discipline composes with the planned `verification`
event and drift instrumentation (ERROR-AND-DRIFT-MODEL.md) and with the
SLSA/in-toto attestation already in the substrate.

Negative / cost: existing `closure-verified` events written before this
amendment carry no read block and will block if their feature is
re-staged. Because the hook scopes to the feature whose files are
staged, fresh features adopt cleanly and old features are not
re-audited unless re-staged; `SKIP_LOOP_VERIFY=1` (documented in the
commit message) covers a legacy re-stage, or the auditor can be re-run
to emit read-bearing events. The auditor must compute one digest per
verified item (negligible). The read is unsigned, so a fabricated
digest is possible under a malicious-verifier threat model (see
Rationale); accepted as out of scope for the current cooperating-agent
model.

## Alternatives Considered

- **Bind the read requirement to `closure-claimed` as well.** Rejected:
  `closure-claimed` is the cross-tool self-attestation path; gating it
  breaks non-Claude tools that lack a closure-auditor (Fork 1 in the
  build discussion).
- **Block on digest drift, not just warn.** Rejected: a file
  legitimately changes between audit and commit; blocking would
  false-positive on valid edits and train operators toward
  `SKIP_LOOP_VERIFY`, the bypass the gate's own design warns against.
- **Full DSSE-signed attestation (cosign/Rekor) for each verification.**
  Rejected for now as disproportionate to the cooperating-agent threat
  model; recorded as the upgrade path if the threat model changes.
- **Leave prose-only verification in place.** Rejected: it is the
  single most expensive recurring failure class from the 003 run
  (TM-010..015, PERF-001), the "green guardrail is a self-report"
  problem the framework exists to close.
