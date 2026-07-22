<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.multi-agent-trust multi-agent trust (good pattern)

Substrate-original illustration. A recorded model ADR (excerpt).

```markdown
# ADR-033: Multi-agent trust and delegation model for the research system

Agents and roles: Orchestrator (plans); Retriever (read-only search);
  Writer (drafts). No agent has tool authority beyond its role.
Trust and delegation topology: Orchestrator may delegate to Retriever and
  Writer; Retriever and Writer may not delegate to anyone.
Narrowing rule: a delegated grant is always a subset of the delegator's
  (agentic-systems.delegation-authority); Retriever can never receive a write scope.
Accountability: the Orchestrator's request id and identity propagate to every
  sub-agent action in the audit record.
Containment: a sub-agent flagged anomalous is suspended and its in-flight
  delegations halted by the Orchestrator.
```

## Why this satisfies the rule

The ADR maps the agents and roles, states an explicit delegation topology
(who may delegate to whom), encodes the narrowing rule that agentic-systems.delegation-authority
enforces per call, propagates caller identity for accountability, and states how
a compromised sub-agent is contained. The per-call delegation behavior now
operates within a deliberate topology rather than an implicit one.
