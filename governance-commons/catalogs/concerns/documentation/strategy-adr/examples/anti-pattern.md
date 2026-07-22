<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.strategy-adr documentation strategy ADR (anti-pattern)

Substrate-original anti-pattern example for documentation.strategy-adr. The ADR is vague,
leaves decisions open, and gives the lower-layer rules nothing to enforce.

## ADR excerpt (illustrative)

```markdown
# ADR-022: Docs

Status: Accepted   Owner: (unassigned)

- We value good documentation.
- Document things that are important.
- Keep docs up to date when you can.
- Decisions and changelogs: TBD.
- We will figure out where docs live later.
```

"Good documentation" and "things that are important" are aspirations, not a
standard documentation.public-api-documented or documentation.accuracy-and-sync can check. The decision-record and
changelog conventions are deferred, the location is undecided, and there is
no owner. The result is inconsistent documentation with no enforceable
expectation. Resolve each sub-decision and make the per-surface standard
concrete.
