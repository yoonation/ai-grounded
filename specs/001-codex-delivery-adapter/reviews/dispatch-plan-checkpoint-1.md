# C1 Dispatch Plan: Codex Local Delivery Adapter

> Advisory-isolation warning: the parent Codex session is operating with a
> workspace-write sandbox, which supersedes the C1 reviewers' ordinary
> read-only default. Reviewers are therefore advisory-only; the main session
> is the sole writer of this artifact and `events.jsonl`.

## Plan-gate result

`PASS: approved plan present and covers the dial floor`

## Deterministic dispatcher output

```json
{
  "checkpoint": "C1",
  "routing_decision_event": {
    "agent": "dispatcher",
    "assignments": [
      {"agent": "staff-engineer", "catalogs": ["agent-security", "code-organization", "documentation"]},
      {"agent": "threat-modeler", "catalogs": ["agent-security", "input-validation"]},
      {"agent": "performance-reviewer", "catalogs": []},
      {"agent": "production-readiness", "catalogs": []}
    ],
    "checkpoint": "C1",
    "event": "routing-decision",
    "plan_ref": "feature-concerns.yaml",
    "profile": "production-grade-baseline",
    "routing": "plan"
  },
  "waves": [
    {
      "agents": [
        {"agent": "staff-engineer", "catalogs": ["agent-security", "code-organization", "documentation"]},
        {"agent": "threat-modeler", "catalogs": ["agent-security", "input-validation"]},
        {"agent": "performance-reviewer", "catalogs": []},
        {"agent": "production-readiness", "catalogs": []}
      ],
      "mode": "parallel",
      "wave": "Wave 1"
    }
  ]
}
```
