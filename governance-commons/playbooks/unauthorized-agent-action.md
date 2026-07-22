<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Unauthorized Agent Action

**ID**: unauthorized-agent-action
**Severity**: high
**Related catalogs**: OWASP LLM06 (Excessive Agency), ASI06 (Rogue Agents), ASI07 (Cross-Agent Privilege Escalation)
**Compliance relevance**: EU AI Act Art 14 (Human Oversight), SOC2 CC6.3, NIST AI RMF GOVERN-1.4
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- Cedar policy denied an action but the action was performed anyway
  (PEP bypass or misconfiguration)
- Agent took an action outside its configured capabilities
- Audit log shows actions with `outcome: success` for actions that
  should have been blocked
- File modifications by agent in paths the policy should have
  prevented
- External effects (API calls, emails) sent without expected
  approval token
- User reports "the AI did X without asking" where X should have
  required approval

Definitive confirmation:

- Audit log has both a `policy_evaluated` event with `decision: deny`
  AND a subsequent `tool_invocation` event for the same target
- Cedar PEP logs show the policy returned deny
- The action's effect is observable (file changed, API called, etc.)

Not this scenario if:

- The action was allowed by some other policy you didn't expect to
  match (policy misconfiguration, not bypass — different fix)
- The action looks unauthorized but isn't actually denied by any
  policy (gap in policy coverage, not violation)
- The user gave explicit approval but the approval token wasn't
  recorded (audit log gap, not bypass)

## Immediate Containment (0-15 minutes)

1. **Stop the agent.** If the agent is still active, stop the
   session. The fact that an authorization bypass occurred means
   the agent may continue performing unauthorized actions.

2. **Snapshot the audit log.** Preserve evidence of both the deny
   decision and the subsequent action.

       cp ~/.local/state/<framework>/audit.jsonl \
          ./incident-$(date +%Y%m%d-%H%M%S)-audit.jsonl

3. **Identify all unauthorized actions in this session.** Search for
   the pattern of deny-followed-by-success:

       jq -s 'group_by(.session_id) | .[]
              | sort_by(.ts)
              | reduce .[] as $e ({}; ...)' \
          ./incident-*.jsonl

   Or simpler: find tool_invocations following a deny within the
   same session within a short window.

4. **Reverse observable effects.** For each unauthorized action:
   - File modifications → revert
   - External API calls → contact recipient to disregard
   - Sent emails → send correction
   - Created resources → delete

5. **Disable the affected agent or sub-agent role.** Until root
   cause is found, prevent the configuration that allowed bypass
   from running again.

## Investigation (30-180 minutes)

This investigation is critical because the bypass could be:

- A bug in the PEP code (policy was evaluated but result ignored)
- A configuration error (PEP isn't intercepting the right code path)
- A logic error in the Cedar policy (deny was actually allow due to
  unintended condition)
- A genuine attack on the policy infrastructure

1. **Reproduce the bypass.** Run the same agent configuration with
   the same inputs in an isolated environment. Confirm the bypass
   is reproducible.

2. **Trace the PEP code path.** What code was supposed to enforce
   the deny decision? Was that code:
   - Called? (verify with tracing/breakpoints)
   - Given the correct request context?
   - Receiving the deny response?
   - Acting on the deny by blocking the operation?

3. **Verify policy evaluation.** Run Cedar's `cedar authorize`
   command with the exact request that should have been denied:

       cedar authorize \
            --schema schema.cedarschema \
            --policies <combined-policies>.cedar \
            --request-json suspect-request.json

   If Cedar returns Deny but the action occurred, the PEP isn't
   honoring decisions. If Cedar returns Allow, the policy doesn't
   say what you thought.

4. **Check policy composition order.** Cedar evaluates all
   matching policies; `forbid` always wins over `permit`. Is there
   a buggy `permit` policy overshadowing the intended `forbid`?

5. **Audit recent policy changes.** Did anyone modify policies
   recently that could have introduced this? `git log` on the
   policies directory.

Questions to answer:

- Was Cedar's decision correct (matched expectation)?
- Did the PEP receive Cedar's decision correctly?
- Did the PEP act on the decision?
- What downstream code performed the unauthorized action?
- How many sessions could have been affected by this bypass?

## Remediation (varies)

The fix depends on which step in the authorization chain failed:

### Cedar policy evaluation error

If the policy was returning Allow when it should return Deny:

1. Fix the policy logic
2. Add test cases that would have caught this (cedar-policy CLI
   has built-in test runner)
3. Deploy fixed policy
4. Re-run failing scenarios to confirm fix

### PEP not calling Cedar

If the policy enforcement point wasn't invoking Cedar at all for
this action:

1. Identify the code path that performed the action
2. Add the missing Cedar evaluation call
3. Verify with integration test that the call happens
4. Deploy fix

### PEP not honoring decision

If Cedar said deny but the PEP let the action through:

1. Trace the bug in PEP code
2. Fix the conditional that should have blocked
3. Add unit test for the deny-honor logic
4. Deploy fix

### Configuration not loading policy

If the policy file wasn't loaded at all:

1. Verify policy file path is correct
2. Verify file permissions allow read
3. Check loading code for silent failures
4. Add startup validation that all expected policies loaded
5. Deploy fix

Verification:

- Re-run the bypass scenario; confirm it now blocks
- All tests in the policy test suite pass
- Audit log shows clean deny-and-block patterns

## Hardening (post-incident)

1. **Fail-closed PEP.** If Cedar evaluation errors or times out,
   the default must be deny. Open-failure is unacceptable for
   security-critical decisions.

2. **PEP test suite.** Comprehensive tests covering:
   - Each policy file's intended denies
   - Each policy file's intended permits
   - Combinations of policies (forbid wins over permit)
   - Edge cases (missing attributes, unusual values)

3. **Policy change review.** Every policy change goes through PR
   review with explicit policy testing. ADR required for policy
   semantic changes.

4. **Continuous policy verification.** Cedar policies validated
   against schema in CI on every commit. Cedar's analyzer can
   prove certain properties (e.g., "no policy permits Delete
   without approval_token").

5. **Defense in depth at lower layers.** Hooks should not be the
   only enforcement. Critical paths (write to credential paths,
   external effects, destructive actions) should have additional
   blocks at lower layers (OS permissions, network egress
   controls).

6. **Audit log assertion.** Audit log should record both the
   policy decision and the action outcome. The check
   `if decision == deny then outcome != success` should be
   verifiable across the log.

       # Quick check: any deny-followed-by-success?
       jq -s 'group_by(.session_id)
              | map(select(any(.event_type == "policy_evaluated"
                               and .policy_decision.decision == "deny")
                          and any(.event_type == "tool_invocation"
                                  and .outcome == "success")))' \
          ./audit.jsonl

## Compliance Evidence

Artifacts to capture:

- Audit log entries showing the bypass
- Reproduction in isolated environment (recorded if possible)
- PEP code analysis
- Cedar policy evaluation results
- ADRs documenting the hardening changes
- Test additions for the failure mode
- Communication records for required notifications

Required notifications:

- **Internal security team**: yes, authorization bypass is high-priority
- **Affected stakeholders**: customers, regulators if data or
  customer-facing actions were affected
- **EU AI Act Article 14**: this directly relates to human oversight
  failure; if the affected system is high-risk, Article 73 reporting
  may apply
- **Internal audit**: incident may affect SOC 2 evidence; engage
  internal audit function

## References

- OWASP LLM06, ASI06, ASI07
- Cedar documentation: https://docs.cedarpolicy.com
- Policy DSL choice: [spec/policy-dsl-choice.md](../spec/policy-dsl-choice.md)
- Policies directory: [policies/](../policies/)

## Revision history

    2026-05-12: Initial playbook authored.
