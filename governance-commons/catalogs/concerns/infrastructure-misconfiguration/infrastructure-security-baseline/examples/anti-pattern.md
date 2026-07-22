<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: infrastructure-misconfiguration.infrastructure-security-baseline infrastructure security baseline (anti-patterns)

Substrate-original anti-pattern examples for infrastructure-misconfiguration.infrastructure-security-baseline.

## Anti-pattern 1: No ADR at all

```
$ find docs/decisions -name "*.md" | xargs grep -l "infrastructure security baseline"
(no results)

$ find . -name "*.md" | xargs grep -l "CIS Foundations" 2>/dev/null
(no results)
```

**Why it matters:** The substrate's L1 and L2 rules apply
inconsistently because no strategic shape exists. Every
substrate-author makes ad-hoc baseline decisions; the consumer's
posture is the union of those ad-hoc decisions, which diverge
across teams and over time. Substrate-required: an ADR adapting
the substrate's MADR.

## Anti-pattern 2: ADR exists but does not name a baseline benchmark

```markdown
# ADR-XXX Infrastructure Posture

Status: Accepted

We will follow industry best practices for infrastructure security.

(end of document)
```

**Why it matters:** "Industry best practices" is not a baseline.
Without a named benchmark (CIS, NIST SP 800-53, FedRAMP, etc.)
and pinned version, the consumer cannot demonstrate
conformance to any specific control set. The ADR template
requires Sub-Decision 1 (baseline benchmark) to name a
specific benchmark and version.

## Anti-pattern 3: ADR names baseline but no enforcement model

```markdown
# ADR-XXX Infrastructure Posture

Status: Accepted

We adopt CIS AWS Foundations v3.0.0 as our baseline.

(end of document)
```

**Why it matters:** A baseline without an enforcement model is
aspirational. The benchmark's controls describe outcomes; the
enforcement model is how those outcomes are guaranteed. The
ADR template requires Sub-Decision 2 to select one of Options
A through E.

## Anti-pattern 4: ADR lists exceptions inline without governance

```markdown
# ADR-XXX Infrastructure Posture

We adopt CIS AWS Foundations v3.0.0 with Option B preventive
policy-as-code enforcement.

Exceptions (documented inline, no expiration, no review):
- payments-api bucket allows public-read for the legal-pages
  prefix (Joe says it's fine)
- production EKS public endpoint is okay because we have a
  firewall in front
- the tfstate bucket can be world-readable in dev because it's
  inconvenient otherwise
```

**Why it matters:** Inline, undated, unowned exceptions become
the consumer's actual posture rather than the documented
baseline. Substrate-required: exception governance with
approval authority, registry, expiration, and review cadence
(Sub-Decision 3).

## Anti-pattern 5: ADR is stale; next-review date has lapsed

```markdown
# ADR-007 Infrastructure Security Baseline

Status: Accepted
Date: 2023-01-15
Next review: 2024-01-15  # past

(content from 2023; we have moved from single-cloud to
multi-cloud since, the team has grown 3x, and we have entered
FedRAMP scope)
```

**Why it matters:** A stale ADR creates false confidence: the
posture is documented, but the documentation no longer matches
the consumer's context. Multi-cloud adoption alone requires a
re-evaluation under D2; FedRAMP adoption requires re-evaluation
under D1. Substrate-required: ADR currency check; on-trigger
re-evaluation.

## Anti-pattern 6: ADR claims Option C but only Option D is implemented

```markdown
# ADR-XXX Infrastructure Security Baseline

Sub-Decision 2: Option C hybrid preventive plus detective.

Preventive: planned for Q4. We will integrate Checkov when we
have time.

Detective: AWS Security Hub and Wiz are deployed.
```

**Why it matters:** The ADR claims an enforcement model that
is not actually in place. The L3 review's Question 8
(conformance) catches this gap. The ADR's accuracy is required;
"planned for later" defers conformance indefinitely.

## Anti-pattern 7: ADR conflicts with the IaC's actual posture

```markdown
ADR Sub-Decision 4: Drift detection daily for production.
```

```yaml
# But the actual workflow has been disabled:
# .github/workflows/drift-detect.yml
on:
  workflow_dispatch:  # only manual runs; no schedule
```

**Why it matters:** The ADR is the consumer's strategic
contract; the IaC is the consumer's implementation. When they
diverge, the consumer's actual posture is the IaC. The L3
review's conformance question catches this; the ADR is either
updated to reflect the actual choice (and the implications
acknowledged) or the IaC is brought back into conformance.

## Anti-pattern 8: ADR copies the substrate's MADR verbatim

```markdown
# ADR-XXX Infrastructure Security Baseline

(copy of substrate's MADR with no consumer-specific choices
made; all options presented as "to be decided")
```

**Why it matters:** The substrate's MADR is the analytic
template; the consumer's ADR is supposed to instantiate the
template with consumer-specific choices. A verbatim copy with
unmade decisions is theater. Substrate-required: the ADR
adapts the MADR by selecting options for each sub-decision and
documenting consequences.

## How each anti-pattern is reviewed

The L3 review applies the infrastructure-misconfiguration.infrastructure-security-baseline review-checklist's eight
questions to the consumer's ADR. Anti-patterns 1-4 are caught
at Question 1-4 (presence and content). Anti-pattern 5 is
caught at Question 7 (currency). Anti-patterns 6-7 are caught
at Question 8 (conformance). Anti-pattern 8 is caught at the
checklist's "How to use this binding" guidance about template
instantiation.

Remediation: replace each anti-pattern with the corresponding
good pattern in the paired
`infrastructure-security-baseline-good.md` example.
