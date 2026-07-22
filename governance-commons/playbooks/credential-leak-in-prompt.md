<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Credential Leak in Prompt or Log

**ID**: credential-leak-in-prompt
**Severity**: high
**Related catalogs**: OWASP LLM02 (Sensitive Information Disclosure), LLM07 (System Prompt Leakage), MITRE ATLAS AML.T0055 (Unsecured Credentials)
**Compliance relevance**: SOC2 CC6.1 (Logical Access), NIST AI RMF MEASURE-2.10 (Privacy Risk), GDPR Art 32
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- A credential (API key, OAuth token, password, private key) appears
  in:
  - A prompt sent to an LLM provider
  - An audit log entry
  - A conversation transcript saved to disk
  - A backup file
  - A commit message or code comment
- Credential scanner (gitleaks, trufflehog) flags content in agent-
  related files
- Provider sends a security alert about credential exposure (some
  providers scan for and warn about leaked credentials)
- User reports "I just realized the prompt I sent included my API key"

Definitive confirmation:

- Pattern-match confirms a real credential (not a placeholder or
  example):
  - AWS keys: `AKIA[0-9A-Z]{16}` followed by 40-char secret
  - GitHub tokens: `ghp_[a-zA-Z0-9]{36}` or `github_pat_*`
  - OpenAI/Anthropic API keys: `sk-*` patterns
  - Generic high-entropy strings matching credential heuristics
- Provider validation: testing the credential confirms it works
  (treat as compromised even before validating)

Not this scenario if:

- The match is a placeholder, example, or test value (e.g.,
  `sk-XXXXXXXX`)
- The match is in test fixtures or documentation deliberately
  showing format
- The credential is for a sandboxed test environment with no
  production access (lower severity but still address)

## Immediate Containment (0-15 minutes)

Treat every potentially-leaked credential as compromised until
proven otherwise. The cost of unnecessary rotation is small; the
cost of using a leaked credential is unbounded.

1. **Rotate the credential immediately.** Don't wait to investigate
   exposure scope. Generate a new credential, invalidate the old.

       # Examples per provider:
       # AWS: aws iam delete-access-key --access-key-id <key>
       # GitHub: settings → developer settings → tokens → revoke
       # OpenAI/Anthropic: provider dashboard → API keys → revoke
       # 1Password: revoke and regenerate the secret

2. **Identify what the credential could access.** Inventory the
   permissions the credential had. This drives scope of potential
   damage.

3. **Identify the leak surfaces.** Where could the credential have
   gone?

   - Prompts sent to LLM providers (covered by provider retention
     policy; check enterprise tier vs default)
   - Local audit logs and conversation transcripts
   - Backups (especially if backed up to cloud storage)
   - Shared CI logs (especially public projects)
   - Commit history (especially if pushed to remote)
   - Browser history if the credential was pasted into a web UI

4. **Snapshot affected files for evidence preservation.**

       # Audit log
       cp ~/.local/state/<framework>/audit.jsonl \
          ./incident-$(date +%Y%m%d-%H%M%S)-audit.jsonl

       # Recent conversations
       cp -r ~/.local/state/<framework>/conversations/ \
          ./incident-conversations/

5. **Check provider's credential leak detection.** Some providers
   (GitHub, Anthropic, OpenAI) actively scan for leaked credentials
   and may have already detected this. Check their security alerts.

## Investigation (30-120 minutes)

1. **Determine the leak vector.** How did the credential end up in
   the prompt or log?

   - **User pasted it directly**: educate; not a system issue
   - **Tool returned it in response**: tool needs to filter
     credentials from output
   - **Environment variable leaked through tool call**: tool should
     never echo env vars
   - **Configuration file read by AI**: should have been classified
     and blocked by no-credential-paths policy
   - **System prompt included credential**: never put credentials in
     system prompts; fix the prompt

2. **Determine exposure scope.** Where could the credential have
   gone?

   - Provider retention: how long does the LLM provider retain prompt
     data?
   - Audit log retention: how long until rotation/deletion?
   - Backup propagation: are audit logs and conversations included
     in backups that go to cloud storage?

3. **Check for use of the credential between leak and rotation.**
   If the credential was used during the leak window, was the
   usage legitimate (you used it) or suspicious (potential attacker
   testing access)?

       # AWS: check CloudTrail for the access-key-id
       # GitHub: check Personal Audit Log
       # Any service: check access logs by API key

4. **Determine downstream cleanup needs.**

   - Audit log: scrub or rotate?
   - Backups: identify which include the leak, replace with
     scrubbed versions
   - Code commits: if the credential is in git history, rewrite
     history with git-filter-repo or BFG Repo-Cleaner
   - Provider data: request deletion per provider's data deletion
     API (varies by provider and tier)

Questions to answer:

- What credential leaked?
- What was its access scope?
- How did it leak (which vector)?
- Where could it have propagated (provider retention, backups,
  history)?
- Was it used between leak and rotation?
- What downstream cleanup is required?

## Remediation (varies)

1. **Confirm rotation completed.** Test that the old credential no
   longer works.

2. **Scrub leaked credential from local files.**

       # Replace credential pattern with <REDACTED> in audit log
       # (do this carefully - audit log is hash-chained; rewriting
       # breaks the chain. See "Audit log integrity" below.)

3. **Request provider data deletion** if your tier supports it.

4. **Rewrite git history** if the credential reached a commit.

       # Use git-filter-repo
       git filter-repo --replace-text expressions.txt
       # where expressions.txt contains:
       # AKIA[A-Z0-9]{16}==><REDACTED>

       # Force-push after coordinating with collaborators
       git push --force-with-lease origin --all

   NOTE: forcing push to public repos doesn't fully erase history;
   the credential should be considered permanently compromised even
   after history rewrite. The rewrite is for hygiene; the rotation
   is the actual mitigation.

5. **Backup remediation.** If credential reached cloud backups:
   - Identify the affected backup snapshots
   - Replace with scrubbed versions
   - Confirm old snapshots are deleted (cloud retention policies
     may need adjustment)

### Audit log integrity

Scrubbing audit log entries breaks the hash chain. Options:

- **Replace with redaction marker, accept broken chain at that
  point.** Document the redaction in incident records. Verification
  scripts skip the broken segment with explicit acknowledgment.
- **Truncate the log at the affected entry.** Preserve everything
  up to the leak; archive the rest separately with redaction.
- **Re-emit the log with redaction applied during emit phase.** Only
  works if you can replay events from a clean source.

Document whichever approach you take in incident records.

Verification:

- Old credential confirmed invalid
- New credential confirmed working in legitimate use
- Audit log shows no further references to old credential
- Backups confirmed clean
- Git history clean (or documented as known-compromised)

## Hardening (post-incident)

1. **Pre-prompt credential scanning.** Add a hook that scans
   prompts for credential patterns before sending to LLM. Block or
   redact.

2. **Pre-output credential scanning.** Add a hook that scans
   LLM outputs and tool responses for credential patterns. Block
   or redact before including in audit log.

3. **System prompt audit.** Periodic review of system prompts to
   confirm no credentials embedded. Automated check in CI.

4. **Environment variable filtering.** Tools that can access env
   vars should be configured to NOT echo specific env var names
   (e.g., never echo `*_KEY`, `*_TOKEN`, `*_PASSWORD`).

5. **No-credential-paths policy.** The Cedar policy in
   [policies/no-credential-paths.cedar](../policies/no-credential-paths.cedar)
   should already block AI from reading credential files. Confirm
   it's loaded and effective.

6. **Audit log redaction.** Verify the audit envelope redaction
   rules are active (see audit-envelope.md). Test by deliberately
   constructing a credential-containing event in isolation;
   confirm it's redacted in the log.

7. **Secret scanning in pre-commit hooks.** Tools like gitleaks
   in pre-commit prevent credentials from reaching git in the
   first place.

       # .pre-commit-config.yaml
       - repo: https://github.com/gitleaks/gitleaks
         rev: v8.18.0
         hooks:
           - id: gitleaks

8. **Provider-side credential scanning.** Enable provider features
   that detect and alert on leaked credentials (GitHub, AWS, etc.).

## Compliance Evidence

Artifacts to capture:

- Audit log entries showing the leak
- Rotation evidence (old credential invalidation, new credential
  creation)
- Provider data deletion requests and confirmations
- Backup remediation evidence
- ADRs documenting hardening
- Usage logs showing whether the credential was used during the
  leak window

Required notifications:

- **Internal security team**: yes, always
- **Affected service teams**: if the credential gave access to
  shared infrastructure
- **Customers**: if customer-affecting credentials (e.g., the
  credential was for a service that processes customer data,
  per applicable breach notification laws)
- **Provider security teams**: if the credential was for a
  third-party service, report per their security disclosure
  policy
- **Internal compliance**: SOC 2 evidence; engage internal audit
  function for documentation

## References

- OWASP LLM02, LLM07; MITRE ATLAS AML.T0055
- Policy: [policies/no-credential-paths.cedar](../policies/no-credential-paths.cedar)
- Audit envelope redaction: [spec/audit-envelope.md](../spec/audit-envelope.md)
- gitleaks: https://github.com/gitleaks/gitleaks
- trufflehog: https://github.com/trufflesecurity/trufflehog
- git-filter-repo: https://github.com/newren/git-filter-repo

## Revision history

    2026-05-12: Initial playbook authored.
