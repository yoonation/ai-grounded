---
name: review
description: Run the framework's post-implementation review (C3 checkpoint) via the dispatcher.
disable-model-invocation: true
---

You are at the **post-implementation checkpoint (C3)** of the framework's four-checkpoint workflow. Run the canonical review path: the dispatcher produces the C3 invocation list from the approved plan, you execute it, then closure-auditor verifies the audit trail.

This slash command is a shortcut for the standard C3 flow documented in `.specify/extensions/workflow/commands/speckit.workflow.post-impl.md`. It does NOT invoke code-reviewer or security-reviewer directly - that bypasses the priority schema, the parallel-group ordering, the closure-signaling protocol, and closure-auditor's audit-trail verification.

## Steps

1. Identify the active feature directory under `specs/NNN-feature/`. If unclear, ask the user.

2. Run the dispatcher for C3, substituting the feature directory:

   ```
   uv run --with pyyaml python3 tooling/dispatch/dispatch.py specs/NNN-feature --checkpoint C3
   ```

3. Save the dispatcher output to `specs/NNN-feature/reviews/dispatch-plan-checkpoint-3.md` and append its `routing_decision_event` to `specs/NNN-feature/events.jsonl` verbatim.

4. Execute the plan:
   - Invoke `@code-reviewer` and `@security-reviewer` (if applicable per the plan) in parallel. Assign a shared `parallel_group_id` to events from this batch.
   - Wait for both to complete. Save each artifact to the path specified in its frontmatter. Append each completion event to events.jsonl.
   - Then invoke `@closure-auditor` as the sequential follow-up.

5. Save closure-auditor's report to `specs/NNN-feature/reviews/closure-audit-report-checkpoint-3.md`. Append its completion event. Then parse its "Recommended events" section and append each JSON line **verbatim** to events.jsonl.

6. Summarize findings in a single report:
   - **Findings from code-reviewer** by priority (P1, P2, P3)
   - **Findings from security-reviewer** by priority (if invoked)
   - **Closure-auditor verdicts**: verified, rejected, unaddressed, incomplete deferrals
   - **What blocks commit**: list each P1/P2 item without valid closure
   - **What looks good**: any agent that returned `informational` status

7. Recommend next actions for blocking items: close in code (and re-signal closure), override via ADR (`@adr-architect` can draft), or defer (P2 only; requires entry in `specs/NNN-feature/deferrals.md`).

If the user wants only a quick lint-style review without the framework's priority schema and closure mechanism (e.g., reviewing a hotfix branch that won't go through specs/), tell them that and invoke `@code-reviewer` directly on the diff. This should be the exception, not the default.
