<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.dependency-vetting dependency vetting bypassed

Substrate-rejected patterns.

## Anti-pattern A: dependency added without vetting

```diff
# requirements.txt change with no accompanying vetting artifact
+ some-new-lib==1.2.3
```

The lockfile change is committed; no `docs/dependency-vetting/`
artifact is added. The CI gate fails because the vetting-artifact
gate detects the new dependency.

## Anti-pattern B: vetting artifact with placeholders

```markdown
# Vetting: <to-be-filled>

**Adoption date:** TBD
**Approver:** TBD
**Tier classification:** TBD

## Identity

- Package name: some-new-lib
- (TODO: fill in remaining fields)
```

The artifact exists but is empty. The L2 review checklist surfaces
the placeholders as findings; merge is blocked until the artifact
is substantively filled.

## Anti-pattern C: vetting artifact references non-existent ADR

```markdown
## Cross-references

- supply-chain.supply-chain-integrity-strategy ADR: docs/decisions/ADR-XXX-supply-chain.md  # does not exist
- supply-chain.vulnerability-disclosure-response runbook: docs/runbooks/missing.md  # does not exist
```

Broken cross-references defeat the audit-trail purpose of the
vetting artifact. The substrate-recommended automation checks
that cross-references resolve to actual files.

## Anti-pattern D: vetting performed but adoption rationale missing

```markdown
# Vetting: pypi-foo-1.0.0

## Architectural fit

We needed a foo library.

(no alternatives considered, no exit strategy)
```

The vetting form is technically present but does not address
supply-chain.dependency-vetting's architectural-fit question. The rationale is
necessary to surface drift: when the dependency is later
revisited, the original problem and alternatives are the
substrate-required basis for re-vetting decisions.

## Why these patterns fail

The vetting artifact's value is in the audit trail it creates.
Each anti-pattern degrades the audit-trail value: absence (A)
defeats the trail entirely; placeholders (B) and broken
references (C) defeat the audit's reviewability; missing
rationale (D) defeats the audit's longitudinal value when
re-vetting time comes.
