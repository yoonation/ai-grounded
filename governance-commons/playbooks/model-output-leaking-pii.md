<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Model Output Leaking PII

**ID**: model-output-leaking-pii
**Severity**: high
**Related catalogs**: OWASP LLM02 (Sensitive Information Disclosure), LLM07 (System Prompt Leakage), MITRE ATLAS AML.T0057
**Compliance relevance**: GDPR Art 32-34, HIPAA 164.312, EU AI Act Art 10, SOC2 CC6.7, NIST AI RMF MEASURE-2.10
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- AI output contains personal information (names, emails, phone
  numbers, SSNs, account numbers)
- AI output contains internal organization data (employee details,
  pricing, strategic information)
- AI output includes API keys, tokens, or credentials
- AI output reveals system prompt content (configuration, instructions)
- User reports "the AI just told me <person's> phone number" or
  similar
- DLP (data loss prevention) tooling flags AI output

Definitive confirmation:

- The leaked data matches verified PII patterns (regex matches for
  SSN, credit card, email, etc.)
- The leaked content is identifiable to a specific individual or
  organization
- The data was not in the user's original prompt (i.e., the AI
  produced it from training data or context, not echoed it)

Not this scenario if:

- The AI is echoing PII the user provided in their prompt (still
  a concern but different scope — see audit-envelope redaction)
- The AI is hallucinating plausible-but-fake PII (LLM09 Misinformation)
- The "PII" turns out to be public information (public records,
  published author names, etc.)

## Immediate Containment (0-15 minutes)

1. **Stop distribution of the affected output.** If the output was
   sent to a customer, retract if possible. If posted publicly,
   take down. If displayed in a UI, clear/redact.

2. **Quarantine the conversation.** Save the full conversation
   transcript including the prompt that produced the leak.

       cp ~/.local/state/<framework>/conversation-<id>.jsonl \
          ./incident-$(date +%Y%m%d-%H%M%S)-conversation.jsonl

3. **Identify the data source.** Where did the PII come from?
   - Training data of the LLM (uncommon for current models with
     reasonable safety training)
   - RAG corpus that included PII-containing documents
   - Tool response that returned PII the LLM then included
   - System prompt or instructions that included PII
   - Long-context window from prior conversation turns

4. **Pause similar sessions.** If multiple users have similar
   workflows, pause them until the leak source is identified.

5. **Record the event in audit log** if not already automatically
   captured. The audit envelope `event_type: "policy_violation"` or
   similar is appropriate.

## Investigation (15-60 minutes)

1. **Trace the PII to its source.** Search for the leaked content
   in:
   - The RAG corpus (vector store, embedding index)
   - System prompts and configuration files
   - Recent tool responses in the audit log
   - User uploads from earlier in the session

       # Search RAG corpus (adapt to your store)
       grep -r "<leaked-pii-snippet>" ./rag-corpus/

       # Search audit log for tool responses containing the data
       jq 'select(.event_type=="tool_result") | select(.details.response | contains("<snippet>"))' \
          ./audit.jsonl

2. **Determine scope.** How many other documents in the RAG corpus
   contain similar PII? Run PII scanning across the corpus.

       # Use a PII scanner like Presidio (Microsoft) or similar
       presidio analyze --input ./rag-corpus/ --output ./pii-scan-results.json

3. **Identify affected parties.** Which individuals' PII was leaked?
   This drives notification requirements.

4. **Determine retention exposure.** Was the leaked output sent to
   an external LLM provider with a non-zero retention policy?
   Check API agreement terms.

Questions to answer:

- Whose PII was leaked?
- How long has this PII been accessible to the AI?
- Were other sessions exposed to the same PII source?
- Was the leak via training data (provider issue) or context
  (our issue)?
- What jurisdictions apply for notification (GDPR, state breach
  laws)?

## Remediation (varies)

1. **Remove PII from source.** If the source was a RAG corpus
   document, redact or remove. If it was a system prompt, edit it.

2. **Purge from LLM provider caches.** If using an external LLM
   provider, request data deletion per their data deletion API.
   For enterprise tiers with zero retention, this should already
   be automatic.

3. **Add PII redaction at boundaries.** Update input/output pipelines
   to detect and redact PII before sending to or receiving from
   the LLM. Tools: Microsoft Presidio, AWS Macie, Google DLP API.

4. **Sanitize the audit log if needed.** The audit log itself should
   not contain raw PII (per audit-envelope.md redaction rules). If
   it does, that's a separate issue — review and fix the redaction
   logic.

5. **Document the incident** in incident tracking system with
   appropriate access controls.

Verification:

- Re-run a similar prompt against the cleaned RAG corpus or system
  prompt; confirm no PII in output
- Run PII scanner against output of the next 10 sessions to confirm
  no recurrence
- Check audit log redaction is working (no raw PII in audit entries)

## Hardening (post-incident)

Document each as an ADR.

1. **PII scanning in RAG ingestion pipeline.** No document enters
   the RAG corpus without PII scan + redaction first. Tools:
   Presidio, AWS Macie, custom regex.

2. **Output filtering.** Add a post-LLM-call output filter that
   scans for PII patterns and either redacts or blocks the response.
   Add to PostToolUse hook or equivalent.

3. **System prompt audit.** Periodic review of system prompts for
   embedded PII. Use the same scanner used for RAG ingestion.

4. **Provider agreement review.** Confirm LLM provider agreement
   includes zero-retention for any data classified Confidential
   or higher. Upgrade tier if needed.

5. **Trust score adjustment.** Reduce trust score for agents whose
   outputs trigger PII filters; quarantine if repeated violations.

## Compliance Evidence

Artifacts to capture:

- Conversation transcript with leaked output
- Source identification (where the PII came from)
- Scope assessment (how many sessions/users affected)
- Affected-parties list
- Notification records (who was notified, when, what was disclosed)
- Remediation evidence (redacted corpus, updated prompts, new filters)
- Re-validation evidence

Required notifications:

- **GDPR Article 33**: Data Protection Authority notification within
  72 hours of awareness, if EU data subjects affected
- **GDPR Article 34**: Data subject notification if high risk to
  rights and freedoms (varies by case)
- **US state breach notification**: per applicable state law
  (California CPRA, Virginia VCDPA, etc.)
- **HIPAA Breach Notification Rule**: if PHI involved and breach
  affects 500+ individuals, notify HHS, media, individuals; if
  fewer than 500, log internally and notify HHS annually
- **PCI DSS**: if cardholder data, notify card brands and acquirer
- **Customer contractual notifications**: per agreements with
  affected customers
- **SOC 2 audit trail**: log per service organization policy

## References

- OWASP LLM02: https://genai.owasp.org/llmrisk/llm02-sensitive-information-disclosure/
- GDPR Articles 32-34: https://gdpr-info.eu/art-32-gdpr/
- Microsoft Presidio: https://microsoft.github.io/presidio/
- Threat catalog: [catalogs/threats/owasp-llm-top10.yaml](../catalogs/threats/owasp-llm-top10.yaml)
- Audit envelope redaction:
  [spec/audit-envelope.md](../spec/audit-envelope.md)
- Data classification:
  [spec/data-classification.md](../spec/data-classification.md)

## Revision history

    2026-05-12: Initial playbook authored.
