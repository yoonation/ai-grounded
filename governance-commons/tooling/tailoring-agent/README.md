<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# tailoring-agent

An AI-assisted workflow that helps a consumer produce a tailored profile:
starting from `production-grade-baseline` or an industry-tilt profile, it
proposes selection and severity adjustments fitted to the consumer's context
and emits a candidate profile for human approval.

This directory is a forward-looking skeleton. It documents intent and the
hard boundary; it ships no agent and no runtime. It is the one tooling entry
explicitly marked future.

## Why this is a skeleton only

Two boundaries keep this README-only:

1. The substrate is description, not implementation (Charter Article VII,
   discipline rule 11). A running agent is a maintained product and belongs
   in a consumer's environment, not in the substrate. The substrate's
   contribution is the content the agent would reason over: the profiles, the
   profile-resolver contract, the catalogs, and the tailoring semantics in
   Charter Article V.
2. AI proposes, humans approve (Charter Article III, rule 12). A tailoring
   agent may draft a candidate tailored profile; it may not approve or commit
   one. Any profile the workflow produces is a draft for human review, exactly
   as substrate content itself is authored.

## Intended contract (when built, consumer-side)

- Input: a base profile (baseline or an industry tilt), the resolved
  effective profile (see `../profile-resolver/`), and the consumer's stated
  context (stack, regulatory regime, risk posture).
- Behavior: propose `include`/`exclude` and `profile-severity-override`
  adjustments with a rationale per change, grounded in the substrate's
  catalogs and the Article V tailoring rules.
- Output: a candidate tailored profile (a profile-of-a-profile importing the
  chosen base), presented for human approval. Never auto-applied.

## Status

Skeleton, README-only, explicitly future. No implementation ships with the
substrate by design. The buildable, in-substrate pieces it would rely on
(profiles, profile-resolver, the Article V tailoring semantics) exist or are
themselves skeletons; the agent itself is consumer-side and out of scope for
the substrate.

## Cross-references

- `../profile-resolver/` (the effective-profile input)
- `../../profiles/` (the base profiles to tailor from)
- `../../CHARTER.md` Article III (AI proposes, humans approve), Article V
  (profiles and tailoring), Article VII (consumer-agnostic tooling)
