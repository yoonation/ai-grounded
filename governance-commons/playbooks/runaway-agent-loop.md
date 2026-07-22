<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Runaway Agent Loop

**ID**: runaway-agent-loop
**Severity**: high
**Related catalogs**: OWASP LLM10 (Unbounded Consumption), ASI10 (Resource Exhaustion), ASI05 (Cascading Failures)
**Compliance relevance**: SOC2 A1.1 (Availability), NIST AI RMF MANAGE-2.4
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- Agent has been running far beyond expected duration
- Token consumption rate has spiked above normal baselines
- Cost telemetry shows sudden expense increase
- Multi-agent system has agents waiting on each other in a cycle
- Tool invocations repeat without progress toward task completion
- LLM API responses show "max iterations" or "stop reason: length"
- User reports "the AI seems stuck" or "it keeps trying the same thing"

Definitive confirmation:

- Audit log shows >50 consecutive tool invocations with no
  user-visible progress
- Same tool called with similar parameters repeatedly
- Agent's session duration exceeds task-appropriate threshold
  (varies by task; trivial fix > 5 min, simple feature > 30 min,
  complex feature > 2 hours likely indicates a loop)
- Cost telemetry shows session-level cost exceeded budget threshold

Not this scenario if:

- The agent is doing legitimate exploratory work (research, large
  codebase analysis) — verify by looking at output progress, not
  just call count
- The user is intentionally running an open-ended task (still
  warrants cost monitoring but not loop intervention)
- The agent is processing a genuinely large input (analyzing
  hundreds of files) — verify by examining what the tool calls
  are doing

## Immediate Containment (0-5 minutes)

This scenario has the highest cost-per-minute of any in this
directory. Containment must be fast.

1. **Stop the agent immediately.** Don't investigate first; the
   cost meter is running.

       # Claude Code: Ctrl+C in the terminal
       # Cursor: stop button in UI
       # CI: cancel the job
       # Production agent: trigger circuit breaker

2. **Verify the agent stopped.** Check that no further tool
   invocations are recorded in the audit log. If the agent is
   in a remote process that didn't respect Ctrl+C, kill the
   process or pod.

       # Check audit log after stopping
       tail -n 5 ~/.local/state/<framework>/audit.jsonl

3. **Snapshot the session for analysis.** Save the full conversation
   and audit log before they rotate.

       cp ~/.local/state/<framework>/conversation-<id>.jsonl \
          ./incident-$(date +%Y%m%d-%H%M%S)-conversation.jsonl

4. **Note current spend.** Capture the cost-to-date for this
   session so you can quantify the incident.

       jq '.tokens.input + .tokens.output' \
          ./incident-*.jsonl | awk '{sum+=$1} END {print sum}'

## Investigation (15-60 minutes)

1. **Identify the loop pattern.** What was the agent doing
   repeatedly?

       # Group tool calls by tool name and parameters hash
       jq -r '.subject.tool_name + ":" + (.subject | tostring | @sh)' \
          ./incident-*.jsonl | sort | uniq -c | sort -rn | head -20

2. **Find the trigger.** What input or condition caused the loop?
   Common patterns:

   - **Recursive task decomposition without base case**: agent
     broke a task into sub-tasks; each sub-task broke into more
     sub-tasks; never terminated
   - **Verification loop with broken predicate**: agent tries to
     verify a condition that never returns true (e.g., "wait until
     all tests pass" when one test is permanently failing)
   - **Tool failure retry loop**: agent retries a failing tool
     indefinitely (e.g., expired API token, syntax error in
     parameters)
   - **Multi-agent deadlock**: agent A waits for agent B, B waits
     for A, neither makes progress
   - **Context window saturation**: agent re-reads the same content
     repeatedly because earlier reads scrolled out of context

3. **Calculate the cost.** Sum tokens consumed during the loop.

       jq 'select(.session_id=="<id>") | .tokens.input + .tokens.output' \
          ./audit.jsonl | awk '{sum+=$1} END {printf "Total tokens: %d\n", sum}'

4. **Determine if other systems were affected.** Did the loop
   include external effects (API calls, emails, file writes)?
   Cleanup required.

Questions to answer:

- What was the loop pattern (recursive, verification, retry)?
- What triggered the loop?
- What was the total cost?
- Were external systems modified during the loop?
- Could other concurrent sessions hit the same trigger?

## Remediation (varies)

1. **Resolve the trigger.** Depends on root cause:

   - Recursive decomposition: add explicit depth limits, or
     specify the task scope more concretely in the prompt
   - Verification loop: fix the underlying condition (e.g., fix
     the failing test) or add max-iteration cap to the verification
   - Retry loop: fix the failing tool (rotate credentials,
     correct parameters), then add retry caps
   - Multi-agent deadlock: redesign the coordination protocol
     to break circular dependencies
   - Context saturation: increase context window, use semantic
     compression, or break the task into smaller sessions

2. **Reverse any unintended side effects.** Were files written
   that shouldn't have been? Were external calls made that need
   to be reversed?

3. **Cost reconciliation.** If the loop incurred significant
   unexpected cost, file an internal expense report. If it hit
   a budget cap that affected other users, communicate.

Verification:

- Re-run the same trigger with the fix; confirm the loop doesn't
  recur
- Check that resource consumption returns to baseline
- Confirm any side effects are reversed

## Hardening (post-incident)

1. **Hard iteration caps.** Every agent must have a max-iterations
   parameter at the framework level. Recommended default: 50
   iterations per session for build-time agents, 25 for sub-agents.

2. **Token budget per session.** Set per-session token budgets
   that hard-stop the agent when exceeded. Recommend
   tier-by-task-complexity:
   - Quick fixes: 50K tokens
   - Standard features: 250K tokens
   - Complex features: 1M tokens
   - Research/analysis: 2M tokens

3. **Cost telemetry monitoring.** Real-time cost telemetry per
   session. Alert when session cost exceeds threshold (e.g., $5
   for build-time, varies for runtime).

4. **Progress detection.** Heuristic: if the last 10 tool
   invocations are identical or near-identical (parameter hash
   similarity > 0.9), suspect a loop. Pause and prompt user.

5. **Circuit breakers in multi-agent systems.** Each inter-agent
   call carries a "depth" counter that increments per hop. If
   depth exceeds threshold (e.g., 5), break the chain.

6. **Cost-amplification testing.** Red-team test: can a small
   user input cause large agent activity? Look for patterns that
   amplify and add guards.

## Compliance Evidence

Artifacts to capture:

- Audit log entries showing the loop
- Token consumption summary
- Cost incurred
- Root cause analysis
- Hardening ADRs

Required notifications:

- **Internal cost team**: if the incident incurred material spend
  (>$500 or per organizational threshold)
- **Customer notification**: typically not required unless the
  loop affected service availability (SOC 2 A1.1 implications)
- **Service-level commitments**: if availability commitments were
  breached due to the loop's resource consumption affecting other
  users

## References

- OWASP LLM10: https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/
- Threat catalogs:
  [catalogs/threats/owasp-llm-top10.yaml](../catalogs/threats/owasp-llm-top10.yaml),
  [catalogs/threats/owasp-agentic-asi-2026.yaml](../catalogs/threats/owasp-agentic-asi-2026.yaml)
- Audit envelope `tokens` field:
  [spec/audit-envelope.md](../spec/audit-envelope.md)

## Revision history

    2026-05-12: Initial playbook authored.
