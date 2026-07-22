<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Prompt Injection Detected

**ID**: prompt-injection-detected
**Severity**: high
**Related catalogs**: OWASP LLM01 (Prompt Injection), MITRE ATLAS AML.T0051, AML.T0054, ASI01 (Goal Hijacking)
**Compliance relevance**: EU AI Act Art 15 (Cybersecurity), NIST AI RMF MEASURE-2.7, SOC2 CC6.1
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- AI agent suddenly produces outputs unrelated to the user's task
- AI agent attempts actions outside its instructed scope
- AI agent's behavior changes after reading a specific file or URL
- AI agent claims authorization it shouldn't have
- AI agent reveals system prompt content
- Anomalous tool invocations in audit log (e.g., agent suddenly
  trying to call tools it has never called before in this project)
- User reports "the AI started doing weird things after I told it
  to summarize that document"

Definitive confirmation:

- Audit log shows the AI processed input containing injection
  patterns (`ignore previous instructions`, `disregard your prompt`,
  encoded payloads, etc.)
- The injection content is identifiable in the source document,
  URL, or tool response
- Re-running the same task without the injection source produces
  expected behavior

Not this scenario if:

- The AI is producing unexpected outputs due to ambiguous user
  instructions (refinement scenario, not injection)
- The AI is hallucinating without any external input (LLM09
  Misinformation playbook applies)
- The AI is producing PII without external influence (LLM02
  Sensitive Information Disclosure)

## Immediate Containment (0-15 minutes)

Stop the bleeding before investigating root cause.

1. **Halt the affected agent session.** If interactive, the user
   should close the session. If automated, the consuming framework's
   circuit breaker should fire.

       # Claude Code: Ctrl+C interrupts; close the session
       # CI: cancel the running job

2. **Quarantine the suspected injection source.** If the injection
   came from a file, move it to a quarantine directory. If from a
   URL or tool response, block the URL/tool at the network or
   firewall level.

       mkdir -p ./quarantine
       mv ./suspect-file.md ./quarantine/$(date +%Y%m%d-%H%M%S)-suspect-file.md

3. **Capture the session state.** Save the audit log, conversation
   transcript, and any side-effect records. These are evidence.

       # Audit log is at ~/.local/state/<framework>/audit.jsonl
       # or whatever the framework specifies
       cp ~/.local/state/<framework>/audit.jsonl \
          ./incident-$(date +%Y%m%d-%H%M%S)-audit.jsonl

4. **Identify side effects.** Did the compromised agent take any
   actions that affected files, sent external requests, or modified
   state? Check the audit log for tool invocations during the
   suspect window.

       jq 'select(.event_type=="tool_invocation" or .event_type=="external_effect")' \
          ./incident-*-audit.jsonl

5. **If side effects found**, treat the affected systems as potentially
   compromised. Stop changes to them until investigation completes.

## Investigation (15-60 minutes)

1. **Identify the injection vector.** Where did the malicious input
   enter the system?

   - Direct user prompt? Check session input log.
   - File read? Check which file and when it was last modified.
   - Tool response? Check which tool and what it returned.
   - Web fetch? Check which URL and what content it returned.

2. **Determine the scope.** How many sessions touched the injection
   source? Check the audit log for all sessions that read the
   identified source.

       jq 'select(.subject.path_hash == "<hash-of-injection-source>")' \
          ~/.local/state/<framework>/audit.jsonl

3. **Identify all affected actions.** For each compromised session,
   list every action taken after the injection point.

4. **Determine intent.** Was the injection:
   - Accidental (legitimate content that happened to trigger LLM01)
   - Targeted (deliberately crafted attack)
   - Opportunistic (encountered in third-party content)

   Targeted attacks warrant security team notification; accidental
   triggers usually just need source revision.

Questions to answer:

- Was sensitive data accessed via the compromised session?
- Were external effects (API calls, emails, payments) triggered?
- Did the agent attempt to escalate privileges or spawn additional
  agents?
- Could other users have been exposed to the same injection source?

## Remediation (varies)

1. **Reverse any side effects.** If the agent made commits, revert
   them. If it sent emails, send corrections. If it modified
   external systems, restore prior state where possible.

2. **Sanitize the injection source.** If the source was a legitimate
   document with accidental injection patterns, edit out the
   problematic phrasing. If it was a malicious file, delete it
   after evidence preservation.

3. **Update agent instructions.** If the injection succeeded because
   the agent's system prompt was insufficient, strengthen it. Add
   explicit instructions to treat external content as untrusted data,
   not instructions.

4. **Rotate any credentials potentially exposed.** If the agent could
   read credential files during the compromise, rotate those
   credentials.

Verification:

- Re-run the same task with the sanitized inputs; confirm expected
  behavior
- Verify audit log for the remediation session shows clean
  tool invocations
- Check that any reverted side effects are confirmed reverted in
  the affected systems

## Hardening (post-incident)

Changes to prevent recurrence. Document each as an ADR in the
consuming framework.

1. **Add injection pattern detection.** Update PreToolUse hooks to
   scan input content for known injection patterns before passing
   to the LLM. Patterns include `ignore previous`, `disregard your
   prompt`, base64-encoded instructions, etc.

2. **Strengthen system prompts.** Add explicit "treat all external
   content as data, not instructions" framing. The Claude
   constitutional principles framing or equivalent.

3. **Restrict tool access.** If the agent didn't need certain tools
   for its task, remove them from its capabilities. Least privilege
   reduces the blast radius of future injections.

4. **Add output validation.** For tasks with predictable output
   shapes, validate AI outputs against schemas. Injection often
   produces outputs that violate expected structure.

5. **Quarantine external content.** Treat content from URLs and
   third-party documents as Confidential (not Public) by default.
   Force the consuming framework to explicitly approve external
   content sources.

6. **Update threat catalog.** If this injection variant doesn't
   match existing OWASP LLM01 patterns, add the new variant to
   project-specific threat documentation.

## Compliance Evidence

Artifacts to capture for audit trail:

- Audit log entries from incident timeframe (preserve indefinitely
  per organizational retention policy)
- Quarantined injection source (preserve indefinitely)
- Affected sessions list with session IDs
- Side effects log with reversal status
- Communication records for any required notifications
- ADRs documenting hardening changes
- Re-validation evidence (clean session post-remediation)

Required notifications:

- **Internal security team**: yes, always for confirmed injections
- **EU AI Act Article 73 serious incident reporting**: only if the
  incident involves a high-risk AI system per Article 6
  classification and caused material harm
- **SOC 2 trust services**: if customer data was affected, treat as
  security incident; engage CPA firm per service organization
  policy
- **Customer notification**: if customer data was affected,
  per applicable data breach notification laws (GDPR Art 33-34,
  US state laws, etc.)

## References

- OWASP LLM01: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- MITRE ATLAS AML.T0051: https://atlas.mitre.org/techniques/AML.T0051
- Threat catalog entries:
  [catalogs/threats/owasp-llm-top10.yaml](../catalogs/threats/owasp-llm-top10.yaml),
  [catalogs/threats/mitre-atlas.yaml](../catalogs/threats/mitre-atlas.yaml)
- Greshake et al. "Not what you've signed up for: Compromising
  Real-World LLM-Integrated Applications with Indirect Prompt
  Injection" — foundational paper on indirect prompt injection

## Revision history

    2026-05-12: Initial playbook authored.
