<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Anti-example: supply-chain.supply-chain-integrity-strategy ADR defers all decisions

Substrate-rejected patterns.

## Anti-pattern A: ADR missing entirely

The consumer has no `ADR-XXX-supply-chain-*.md` file. SUPPLY-L1-*
bindings reference policy files that exist but have no documented
rationale. The audit cannot determine whether the policy
parameters were chosen deliberately or copied from substrate
defaults without analysis.

## Anti-pattern B: ADR with all sections "defer to industry standard"

```markdown
# Supply-Chain Integrity Strategy

## Section 1: Context
We make software.

## Section 2: SLSA Build Level
Industry standard.

## Section 3: Attestation Scope
Whatever is reasonable.

## Section 4: SBOM
Yes, we have SBOM.

## Section 5: Signing
Sigstore.

## Section 6: Transparency log
Default.

## Section 7: Retention
We retain.

## Section 8: Exemptions
Case by case.

## Section 9: Review
When needed.
```

Each section is filled but with substrate-uninformative content.
"Industry standard" does not specify which standard; "we retain"
does not specify how long; "case by case" does not document the
exemption discipline. The review checklist surfaces every
section as a finding.

## Anti-pattern C: regulatory exposure undocumented

```markdown
## Section 1: Context

We ship a product.
```

The consumer is in fact in scope for EU CRA but Section 1 does
not record this. Sections 4 (SBOM) and 7 (retention) make
choices without acknowledging the CRA floor. After 2026-09-11,
the consumer is non-compliant; the ADR cannot prove the consumer
even considered CRA scope.

## Anti-pattern D: ADR-and-operation drift

```markdown
## Section 2: SLSA Build Level
SLSA Build Level 3.
```

ADR claims L3. Operational pipeline:

```yaml
- name: Build
  run: docker build -t api .
# No provenance generation; no slsa-github-generator
```

The pipeline runs at L0 (no provenance). The substrate-recommended
supply-chain.supply-chain-integrity-strategy review checklist flags this in Question 10
(cross-reference consistency). The choice on paper is not the
choice in practice.

## Anti-pattern E: ADR last reviewed years ago

```markdown
**Last reviewed:** 2023-04-15
```

Three years since last review. EU CRA was published in October
2024; CRA in-scope determination is not in the ADR. The annual
review cadence is in arrears by two years.

## Why these patterns fail

The supply-chain.supply-chain-integrity-strategy ADR's value is to make the consumer's choices
deliberate, documented, and reviewable. Each anti-pattern
defeats one of these properties: absence (A) defeats all three;
non-substantive content (B) defeats deliberateness; missing
regulatory analysis (C) defeats reviewability; ADR-operational
drift (D) defeats documentedness as a reliable signal; stale
ADR (E) defeats reviewability over time.
