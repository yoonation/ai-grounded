<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: reliability.reliability-strategy reliability strategy (anti-pattern)

Substrate-original illustration: a "strategy" that gestures at reliability
without making any of the sub-decisions, so the L2 rules have nothing to
conform to.

```markdown
# ADR-021: Reliability

## Status
Accepted

## Decision
The orders service will be highly available and resilient. We use retries
and timeouts on external calls and run multiple replicas behind a load
balancer. Health checks are configured. We will monitor the service and
respond to incidents as they arise.
```

Why this fails the rule: nothing is actually decided. There is no
failure-mode catalog (which failures is it built to survive?), no
dependency-criticality classification (so reliability.graceful-degradation has no reference
and everything is implicitly critical), no delivery semantics (so
reliability.idempotency cannot be checked), no failure-domain map (so reliability.failure-isolation has
nothing to verify), and "health checks are configured" says nothing about
what liveness and readiness gate on (so reliability.health-signaling is unmoored). This is
the default-everything-critical posture the rule exists to replace. The
fix is to make each sub-decision explicit, as in the good example.
