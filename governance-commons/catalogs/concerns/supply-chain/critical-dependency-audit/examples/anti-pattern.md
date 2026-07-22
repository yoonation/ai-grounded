<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.critical-dependency-audit undifferentiated dependency list

Substrate-rejected patterns.

## Anti-pattern A: no inventory

The consumer has no `docs/dependency-inventory.md` or substrate-
acceptable equivalent. Production dependencies exist only in
lockfiles, with no criticality classification.

When supply-chain.critical-dependency-audit review asks "what is the audit cadence for
this dependency?", the answer is "we don't have one" because
the dependency was never classified.

## Anti-pattern B: flat list, no tiers

```markdown
# Dependencies

- httpx
- cryptography
- python-dateutil
- colorlog
- express
```

All dependencies are listed but not classified. The audit cadence
implied by the substrate is one-size-fits-all; the consumer
either audits every dependency quarterly (operational burden)
or audits nothing on a cadence (defeats the rule).

## Anti-pattern C: tiers exist but stale

```markdown
## Tier-1
| Dependency | Last Audit |
|------------|------------|
| express | 2023-04-15 |
```

Audit last performed three years ago. Substrate-recommended
quarterly cadence for tier-1 means the next audit was due in
2023-07; nine quarterly audits have been missed. The inventory
exists but is non-operational.

## Anti-pattern D: classification without rationale

```markdown
## Tier-3 (Commodity)
- cryptography
- httpx
```

Cryptography and HTTP libraries are on the hot path; classifying
them as tier-3 misapplies the supply-chain.critical-dependency-audit criteria. Audit
records would not surface signal drift on these dependencies
because the cadence is annual rather than quarterly.

## Why these patterns fail

Critical-dependency discipline operationalizes the substrate's
"dependencies are not free" stance. Each anti-pattern degrades
the discipline: absence (A, B) makes audit cadence undefined;
staleness (C) makes the cadence non-operational; misclassification
(D) routes critical dependencies to a slow cadence where drift
goes unsurfaced.
