<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Model Version Rollback

**ID**: model-version-rollback
**Severity**: medium
**Related catalogs**: OWASP LLM04 (Data and Model Poisoning), MITRE ATLAS AML.T0059 (Erode ML Model Integrity)
**Compliance relevance**: NIST AI RMF MANAGE-2.4 (deactivate AI systems), EU AI Act Art 20 (Corrective actions), SOC2 CC8.1 (Change Management)
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Scenarios that trigger this playbook:

- New model version released and adopted in framework
- After adoption, quality regression observed:
  - Increased hallucinations
  - More frequent policy violations
  - Reduced task completion rate
  - Changed reasoning patterns affecting downstream tooling
- New model version has reported safety issues (provider advisory)
- New model version's terms of service changed unacceptably (e.g.,
  retention policy changed)
- New model behaves in ways incompatible with existing prompts

Definitive confirmation:

- Side-by-side comparison shows new version performs worse on
  representative tasks
- Provider publishes deprecation notice or safety advisory
- Quantitative metrics (evaluations) show regression
- User feedback consistent across multiple sessions

Not this scenario if:

- Single bad session that may be ordinary LLM variance (non-determinism
  is normal; re-run with the same prompt and see if it varies)
- Apparent regression is actually a feature change documented in
  release notes (read the release notes)
- The issue is in prompt construction, not model capability
  (test the same prompts on old version to confirm regression)

## Immediate Containment (0-30 minutes)

Rollback scenarios have less time pressure than security incidents
but still warrant prompt action since the bad version is causing
ongoing low-quality work.

1. **Identify the impacted version.** Confirm exactly which model
   string corresponds to the issue:
   - `claude-opus-4-7` vs `claude-opus-4-6`
   - `gpt-4o-2024-11-20` vs `gpt-4o-2024-08-06`
   - etc.

2. **Identify the rollback target.** Last known-good version that:
   - Is still available from the provider
   - Has acceptable terms of service
   - Performs well on representative tasks

3. **Update configuration to use rollback target.**

       # Framework-specific config; for Anthropic API:
       # in CLAUDE.md or settings.json, set model to known-good version

       # For mise-managed CLI tools:
       # mise.toml updates pin to previous version

4. **Verify the rollback took effect.** Run a test session and
   confirm the model string in audit logs matches the rollback
   target.

       jq '.actor.id' ~/.local/state/<framework>/audit.jsonl | tail -5

5. **Communicate with users** if shared environment. "Rolling back
   to <version> due to <reason>; details in incident #N."

## Investigation (30-180 minutes)

1. **Characterize the regression.** What specifically is worse?
   Use representative tasks to quantify:
   - Task completion rate (% completed correctly)
   - Hallucination rate (% outputs with factual errors)
   - Policy compliance (% sessions with policy violations)
   - User satisfaction (qualitative)

2. **Document the regression evidence.** Save:
   - Example sessions showing the regression
   - Side-by-side comparison with prior version on same prompts
   - Evaluation suite results (if you maintain one)

3. **Determine if a temporary or permanent rollback.** Is this
   regression likely to be fixed by the provider in a patch
   release? Or is this a fundamental change requiring longer-term
   alternative?

4. **Check for shared impact.** If the model is widely used
   beyond your framework, look for community discussion of the
   same regression. Confirms it's not specific to your usage.

Questions to answer:

- What is the specific regression?
- What's the rollback target?
- Is rollback temporary or permanent?
- Are there terms-of-service implications to using the older
  version (e.g., older models sometimes have less favorable
  retention defaults)?
- What downstream artifacts produced during the bad version's
  use need re-verification?

## Remediation (varies)

1. **Pin model version in config.** No auto-upgrades. The framework
   defaults to a specific model version that you've validated.

       # Concrete example for CLAUDE.md or framework config:
       # Model: claude-opus-4-6 (rolled back from 4-7 due to <reason>)

2. **Update build provenance.** If you generate SLSA provenance,
   the model version is part of the build environment. Update
   provenance generation to record the rolled-back version.

3. **Re-validate recent artifacts.** Work produced under the bad
   version may have quality issues. Identify and review:
   - Code committed during the bad-version window
   - Documents generated during the window
   - Decisions made based on AI outputs during the window

4. **Test that the rollback works for representative tasks.**
   Run a sampling of common workflows against the rolled-back
   version. Confirm they complete successfully.

5. **Plan for re-adoption.** When can the new version be
   reconsidered?
   - Patch release from provider addressing the issue
   - Sufficient time has passed for community confirmation of fix
   - Re-evaluation against your representative tasks shows parity
     or improvement

Verification:

- Audit log shows rolled-back model in use
- Representative tasks complete successfully
- Provenance attestations record the rolled-back version
- No new sessions using the bad version (CI enforcement)

## Hardening (post-incident)

1. **Model version pinning by default.** Configuration should
   always specify exact model versions; never "latest". This
   prevents future surprises from auto-upgrades.

2. **Evaluation suite.** Maintain a small but representative
   evaluation suite that you can run against any model version
   to validate before adoption:
   - 20-30 prompts covering common workflows
   - Expected behaviors documented
   - Automated comparison runner

3. **Provider-version monitoring.** Track when providers release
   new versions and when they deprecate old ones. Plan adoption
   testing before deprecation date.

4. **Staged rollout for model changes.** New model versions
   adopted by:
   - Personal use for 1-2 weeks
   - Team-shared use after positive personal experience
   - Production-adjacent CI workflows last

5. **Rollback rehearsal.** Periodically (annually?) practice the
   rollback procedure with a deliberate temporary switch. Catches
   any process gaps before they matter.

6. **Provenance includes model version.** Build provenance
   attestations should always include the model version used for
   AI-assisted work. Enables forensic analysis if model issues
   discovered later.

## Compliance Evidence

Artifacts to capture:

- Evidence of regression (test results, sample sessions)
- Configuration change record (the rollback config commit)
- List of artifacts produced during the bad-version window
- Re-validation results for affected artifacts
- ADR documenting the version pinning policy
- Communication records (user notification, internal advisory)

Required notifications:

- **Internal stakeholders**: yes, affected teams
- **Customer notification**: only if AI outputs affected customer
  deliverables and required re-validation
- **EU AI Act Article 20**: corrective action requirement applies
  if affected system is high-risk; document the rollback as a
  corrective action
- **SOC 2**: change management evidence; document as a controlled
  change

## When NOT to roll back

Sometimes the right answer is forward, not back:

- New version has critical security fixes; rolling back exposes you
  to fixed vulnerabilities
- Old version is deprecated and will be retired soon anyway
- The "regression" is actually a behavior change you can adapt to
  with prompt updates
- Rolling back loses important features your workflows now depend on

In these cases, document the decision not to roll back, and instead
work forward to adapt to the new version.

## References

- Threat catalogs: OWASP LLM04, MITRE ATLAS AML.T0059
- Principles: P12 (Honest acknowledgment of non-determinism)
- Architecture rationale: includes provider-version pinning

## Revision history

    2026-05-12: Initial playbook authored.
