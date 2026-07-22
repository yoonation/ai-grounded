<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Incident Response Playbooks

Markdown procedures for common AI failure modes. Each playbook
follows a consistent structure so responders can navigate quickly
under time pressure.

## When to use these

These playbooks are reference material for the moment an incident
occurs. Common triggers:

- Hook fires unexpectedly (PreToolUse, PostToolUse blocks)
- Audit log shows unexpected actor patterns
- Drift detection reports spec/code divergence
- Cost telemetry shows anomalous spend
- User reports unexpected AI behavior
- Compliance auditor surfaces a finding

For each scenario, the relevant playbook walks through:

1. **Recognition** — how to confirm this is the incident type
2. **Immediate containment** — first 5-15 minute actions
3. **Investigation** — diagnostic steps to understand scope
4. **Remediation** — fix the immediate issue
5. **Hardening** — prevent recurrence
6. **Compliance evidence** — what to record for audit

## Playbook structure

Every playbook in this directory follows this template:

    # Playbook: <Scenario Name>
    
    **ID**: <unique-id>
    **Severity**: critical | high | medium | low
    **Related catalogs**: <OWASP-LLM-XX, ASI-XX, MITRE-XX>
    **Compliance relevance**: <SOC2-CC-X, EU-AI-ACT-Art-X, NIST-AI-RMF-Y>
    **Last reviewed**: YYYY-MM-DD
    **Maintainer**: <github-handle>
    
    ## Recognition
    
    Symptoms that indicate this scenario:
    - ...
    
    Definitive confirmation:
    - ...
    
    Not this scenario if:
    - ...
    
    ## Immediate Containment (0-15 minutes)
    
    Stop-the-bleeding actions in priority order.
    
    1. ...
    2. ...
    
    ## Investigation (15-60 minutes)
    
    Diagnostic steps to understand scope and root cause.
    
    1. ...
    
    Questions to answer:
    - ...
    
    ## Remediation (varies)
    
    Steps to fix the immediate issue.
    
    1. ...
    
    Verification:
    - ...
    
    ## Hardening (post-incident)
    
    Changes to prevent recurrence. Document these as ADRs in the
    consuming framework.
    
    1. ...
    
    ## Compliance Evidence
    
    Artifacts to capture for audit trail:
    
    - Audit log entries from `<time_range>`
    - Provenance attestations for any rebuilt artifacts
    - ADRs documenting hardening changes
    - Communication records for required notifications
    
    Required notifications:
    - <jurisdictions, regulators, customers, internal stakeholders>
    
    ## References
    
    - <relevant catalog entries>
    - <prior incident reports if anonymized references available>
    - <upstream documentation>

## Authoring principles

Playbooks are read under time pressure. Optimize for fast
navigation, not comprehensive prose:

- **Lead with action**: imperative verbs, numbered steps
- **Specific commands**: actual shell commands, not "investigate logs"
- **Concrete thresholds**: "if cost > $50/hour" not "if cost is high"
- **Time-boxed steps**: indicate expected duration
- **Failure modes documented**: "if step 3 doesn't work, see X"

Avoid:

- **Narrative paragraphs**: scannable lists win
- **Generic advice**: "follow incident response best practices"
- **Cross-references without context**: link to specifics, not directory roots
- **Tool-specific assumptions**: prefer vendor-neutral commands; note when not possible

## Playbook index

| ID | Scenario | Severity |
|---|---|---|
| [prompt-injection-detected.md](./prompt-injection-detected.md) | Confirmed prompt injection attempt | high |
| [model-output-leaking-pii.md](./model-output-leaking-pii.md) | LLM output contains PII | high |
| [runaway-agent-loop.md](./runaway-agent-loop.md) | Unbounded resource consumption | high |
| [compromised-mcp-server.md](./compromised-mcp-server.md) | Malicious or compromised MCP tool | critical |
| [audit-log-tampering-suspected.md](./audit-log-tampering-suspected.md) | Hash chain integrity broken | critical |
| [unauthorized-agent-action.md](./unauthorized-agent-action.md) | Cedar deny but action occurred | high |
| [model-version-rollback.md](./model-version-rollback.md) | Rolling back to known-good model | medium |
| [credential-leak-in-prompt.md](./credential-leak-in-prompt.md) | Credentials in LLM prompt or log | high |

## Maintenance

Each playbook has a `Last reviewed` field. Quarterly review (per
[../MAINTENANCE.md](../MAINTENANCE.md)) confirms playbooks are
still accurate. Update procedures when:

- The relevant threat taxonomy changes (catalog updates)
- New tools enter the framework that change the response steps
- Real incidents reveal gaps in the documented procedure

When updating after a real incident, include a revision note
(date + brief description) in the playbook's header. Anonymize
incident details if specifics would expose sensitive information.

## Playbooks vs runbooks

Distinction worth noting:

- **Playbook**: how to respond to an unexpected incident
- **Runbook**: how to perform a routine operation

Playbooks live here. Runbooks (like the OSCAL UPDATE_RUNBOOK)
live with the system they operate on.

## When no playbook fits

If you're responding to an incident and no playbook fits the
scenario well enough:

1. Don't force-fit an existing playbook — wrong steps cause harm
2. Apply general principles: contain → investigate → remediate → harden
3. Document what you did as you do it
4. After the incident, write the missing playbook for the next
   responder (likely future-you)

The playbook gap itself is an incident-response finding worth
reporting.
