<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# ADR-002: Fail closed on closure-hash recorded-versus-disk mismatch

**Status**: Accepted
**Date**: 2026-07-05
**Decision-maker**: Myoung Hong (maintainer)
**Related artifacts**: `.claude/hooks/verify_loop_closure.py`, `.claude/hooks/test_verify_loop_closure.py`, `.claude/agents/closure-auditor.md`
**Related ADRs**: ADR-001 (establishes the disk-truth read-evidence gate; this decision supersedes its Tier-1 warn-without-blocking posture for digest mismatches)

## Context

ADR-001 made `closure-verified` events carry machine-checkable read
evidence (`closure_evidence.read = {path, sha256}`) and had the commit
gate independently recompute the digest. Structural failures (missing
read block, unresolvable path, malformed digest, empty file) blocked;
a recorded-versus-disk digest MISMATCH only warned (Tier 1, drift
visibility), on the theory that a file legitimately changes between
audit and commit.

Feature 007's C4 commit episode showed the warn posture is exploitable
by the exact failure the gate exists to prevent: the closure-auditor
emitted LLM-generated digests instead of running the hash tool. The
fabricated digests would have produced only non-blocking warnings; the
catch happened because the operator recomputed hashes by hand. ADR-001
itself cites in-toto attestation and the constitution's fail-closed
default (Section 2.3) as founding principles; in the in-toto model the
functionary records material hashes and the verifier FAILS verification
on a recompute mismatch. A warn posture on the one check that is
cryptographically decisive was an internal inconsistency.

## Decision

The gate fails closed on a recorded-versus-disk digest mismatch and on
an unreadable-file recompute. SHA-256 preimage resistance makes a
MATCHING recorded digest cryptographic proof that a real hashing tool
ran over the committed bytes, so a mismatch always means one of two
invalidating conditions: a digest that was composed rather than
computed (fabrication), or a file edited after the audit (stale
verification). Both reject the closure.

The auditor keeps producing the recorded digest (its instruction now
requires the raw tool output from the current invocation). The
alternative of making the hook the sole digest author with the auditor
citing path only was rejected: it would erase the binding between the
auditor's read and the content, degrading the evidence from "the
auditor verified these bytes" to "this file existed at commit time."
The recorded-by-functionary, recomputed-by-verifier split is the
in-toto model and preserves attestation semantics.

Legitimate post-audit staleness has two honest remediations, both
pre-existing mechanics: emit a superseding `closure-verified` with a
freshly computed digest (the verdict logic takes the latest event), or
re-run the closure audit. Process guidance: run closure audits after
lint and formatting passes so cosmetic edits do not stale fresh
evidence. The documented emergency valve (`SKIP_LOOP_VERIFY=1` with
`SKIP_LOOP_VERIFY_REASON`) remains the last resort and is loudly
logged.

## Consequences

- A fabricated digest can no longer enter the ledger silently; the
  commit blocks with a message naming both possible causes and the
  remediation.
- Post-audit cosmetic edits now block until re-verified instead of
  warning; this is intended friction, ordered around by running audits
  last.
- The Tier-1 drift-warning plumbing (Verdict.warning, the non-blocking
  warnings section of the report) is removed as dead code.
- Regression coverage: a fabrication/stale-mismatch case must block,
  and a superseding fresh-digest event must close
  (`test_fab1_recorded_disk_mismatch_blocks`,
  `test_fab2_superseding_fresh_digest_closes`).
