<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.decisions-and-operations decisions and operations (good pattern)

Substrate-original good-pattern example for documentation.decisions-and-operations. Significant
decisions, consumer-visible changes, and operational knowledge are recorded
and discoverable.

## A decision record (illustrative)

```markdown
# ADR-017: Use integer cents for all monetary amounts

Status: Accepted   Date: 2026-05-02
Context: floating-point dollars produced rounding errors in settlement.
Decision: represent all monetary amounts as integer cents end to end.
Consequences: API bodies and storage change; migration ADR-018 follows.
```

## A changelog entry and a runbook pointer (illustrative)

```markdown
## [2.0.0] - 2026-05-10
### Changed
- Monetary amounts are now integer cents (see ADR-017). Breaking for clients
  sending decimal dollars.

# Runbook: settlement backlog
If the settlement queue depth alert fires, see docs/runbooks/settlement.md
for the drain procedure and the dashboard link.
```

The reasoning, the change history, and the operational response are written
down where a reader will find them, so the team acts without the original
author present.
