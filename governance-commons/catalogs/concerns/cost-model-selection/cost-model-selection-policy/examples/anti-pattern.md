<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: cost-model-selection.cost-model-selection-policy cost model selection policy (anti-patterns)

Substrate-original anti-pattern examples for cost-model-selection.cost-model-selection-policy. Each
shows a common way the L3 ADR rule is violated and explains why
the violation matters.

## Anti-pattern 1: Undocumented cost model ("we'll watch the dashboard")

```
Operator question: "What's payments-api's cost target?"
Team answer:        "We watch the cost dashboard and respond if
                    something looks wrong."
Operator: "Is the target documented anywhere?"
Team:     "Not formally. We'd know if it was getting bad."
```

Why this fails: no ADR exists. The cost-model-selection.cost-anomaly-alerting anomaly alerting
cannot reference a documented target; thresholds are improvised
or copied from other services. The team's response when "something
looks wrong" is itself improvised. New team members inherit no
documented commitment. The substrate's COST-L1 and COST-L2 rules
operate against an unstated target the team carries in their
heads.

The substrate's L3 review fails. Remediation is to author the
ADR retrospectively, documenting the cost model that has been
operating implicitly.

## Anti-pattern 2: Budget without documented response policy

```markdown
# ADR-014 (incomplete): payments-api cost target

## Status: Accepted

## Decision: payments-api monthly budget is $25,000.

## End of ADR.
```

Why this fails: the target is documented but the response policy
is absent. When the budget burns, the team has no documented
guidance; the on-call engineer makes ad-hoc decisions; the
product owner is engaged or not engaged based on whoever
remembers to escalate.

The substrate-recommended pattern is that the response policy is
the load-bearing decision (the over-budget response policy is
why the cost model is a decision rather than a number). The
substrate's L3 review surfaces this as a blocking finding.

## Anti-pattern 3: Cost SLI does not reflect unit economics

```markdown
# ADR-014: payments-api Cost Model

## Decision

Cost SLI: compute spend, storage spend, network spend (broken
out by AWS service category).

Cost SLO targets:
- Compute spend under $15,000/month
- Storage spend under $5,000/month
- Network spend under $5,000/month
```

Why this fails: the SLI choice reflects operator convenience
(provider category breakdown) rather than the consumer's
economic interest. A SaaS provider whose business model is
per-transaction has no business reason to optimize compute-
versus-storage spend separately; the relevant question is
cost per transaction.

The substrate's L3 review confirms cost SLI choice connects
to a unit-economics or business-meaningful dimension. Provider-
category breakdown is acceptable as a supplementary view but
not as the primary SLI for a business with unit-economics
relevance.

## Anti-pattern 4: Trade-off rationale missing or asserted

```markdown
# ADR-014: payments-api Cost Model

## Cost-vs-reliability trade-off

We will balance cost and reliability appropriately.
```

Why this fails: "balance appropriately" is an assertion, not a
rationale. The ADR does not document the consumer's position
at any of the substrate-recognized trade-off boundaries (an
additional 9 of availability; a fault-injection program; a
multi-region active-active topology; a regulated-region
deployment). When the trade-off arises in practice, the team
has no documented position to reference.

The substrate-recommended pattern is concrete trade-off
positions at each boundary the consumer's architecture might
encounter. The good-pattern example shows the shape (rejected
99.99 percent availability with cost calculation; approved
fault-injection with budget; etc.).

## Anti-pattern 5: No cross-reference to related ADRs

```markdown
# ADR-014: payments-api Cost Model

## Decision

[Cost SLIs, targets, budget computation, response policy all
documented]

## Related ADRs

(none referenced)
```

Why this fails: the cost-model ADR does not cross-reference the
observability.slo-policy SLO policy ADR (or its equivalent for the
reliability commitments). The cost-vs-reliability trade-off
discussion cannot reference the reliability commitments because
the link is missing.

The substrate-recommended pattern is explicit cross-reference
to the SLO policy ADR (or substrate-recognized reliability
documentation) and to the dependent COST-L1 and COST-L2 rules
the ADR anchors. The good-pattern example shows the
related-adr frontmatter and the references section.

## Anti-pattern 6: ADR exists but has no review schedule

```markdown
# ADR-014: payments-api Cost Model

## Status

Accepted (2024-08-15).

## Decision review schedule

(absent)
```

Why this fails: an ADR with no review schedule becomes stale as
the consumer's business and infrastructure evolve. The substrate-
recommended discipline is annual full review plus triggered
reviews on substrate-recognized events; absence is a finding.

A more insidious variant: the ADR has a review schedule but the
review date has passed without amendment. The substrate's L3
review checks both the schedule's presence and its currency.

## Anti-pattern 7: ADR is one year stale despite documented review schedule

```markdown
# ADR-014: payments-api Cost Model

## Status

Accepted (2025-01-15). Next review 2026-01-15.

[ADR content has not been amended since 2025-01-15. Today is
2026-05-21.]
```

Why this fails: the ADR is four months past its documented
review date. The consumer's business may have shifted (volume
growth; tenancy model changes; vendor renegotiation); the cost
SLI choice or target may no longer reflect the operative
situation; the response policy may reference roles that no
longer exist.

The substrate-recommended pattern is to enforce review-cadence
adherence as part of the substrate-author's annual M1 review
or via a consumer-side process. A stale ADR is a finding;
remediation is amendment or extension with documented rationale
for the extension.

## Anti-pattern 8: Cost SLO target borrowed from peer service without context

```markdown
# ADR-014: payments-api Cost Model

## Decision

Cost SLO target: $25,000/month.

Rationale: orders-api has a $25,000/month target so we adopted
the same number.
```

Why this fails: target adoption without examination of the
operative context. orders-api may have a different cost shape
(different transaction volume; different unit economics;
different vendor mix); copying its target produces a target
that does not reflect payments-api's business sustainability.

The substrate-recommended pattern is per-service target
derivation from the consumer's unit economics and business
commitments. Peer-service targets are acceptable as a starting
estimate but require justification against the operative
context.

## Anti-pattern 9: ADR documents the target but COST-L2 rules use different numbers

```markdown
# ADR-014: payments-api Cost Model
Cost SLO target: $25,000/month (cost per transaction $0.0024)
```

```yaml
# alerting-rules.yaml
spec:
  service: payments-api
  budget:
    monthly-amount-usd: 30000  # different from ADR target
```

Why this fails: the ADR documents one target; the alerting
configuration enforces a different target. When the budget
burns, the team doesn't know which target is operative.

The substrate-recommended pattern is single source of truth: the
ADR documents the target; the cost-model-selection.cost-anomaly-alerting alerting configuration
derives from the ADR; the cost-model-selection.cost-emission-pipeline pipeline computes against
the ADR's documented method. Divergence is a finding.

## What the consequences look like in operation

A consumer with an inadequate cost-model ADR sees the
consequences across the cost program:

- The COST-L2 rules cannot operate against a documented target;
  alerting and pipeline review are improvised
- New service launches inherit no cost discipline because the
  ADR template does not constrain them
- Budget overruns produce ad-hoc responses; the team
  rediscovers the same trade-offs at every burndown event
- Cost-vs-reliability trade-offs surface in incident reviews
  rather than in proactive architecture decisions
- Pricing decisions operate from estimate rather than from
  documented unit economics
- Audit and finance team requests for cost commitments produce
  inconsistent answers across team members

The substrate's discipline is to require the ADR before the
service exits its initial production soak period and to
maintain it on the substrate-recommended cadence. The ADR is
the anchoring decision that makes the rest of the cost program
coherent.
