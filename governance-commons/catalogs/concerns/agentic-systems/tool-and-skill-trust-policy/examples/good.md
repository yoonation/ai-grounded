<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.tool-and-skill-trust-policy tool and skill trust policy (good pattern)

Substrate-original illustration. A recorded policy ADR (excerpt).

```markdown
# ADR-034: Tool and skill trust policy for the automation agent

Admitted set: an explicit allow-list of first-party tools, each with a declared
  scope (agentic-systems.tool-authorization-scope) and call-time authorization (agentic-systems.tool-use-authorization).
Vetting gate: a tool is admitted only after source and provenance review
  (supply-chain signature verification for distributed artifacts), scope
  review, and a behavior review.
Third-party / dynamic skills: not loaded dynamically at runtime; a third-party
  skill is vendored, pinned, signature-verified, and passes the vetting gate
  before admission.
Revocation: a skill found untrustworthy is removed from the allow-list and its
  in-flight uses halted.
```

## Why this satisfies the rule

The ADR sets an explicit admitted set, a vetting gate covering provenance, scope,
and behavior, an explicit stance against unvetted dynamic loading, and a
revocation path, cross-referencing supply-chain for artifact provenance and the
per-tool scope and authorization rules. The OWASP Agentic Skills Top 10 threats
map to this decision.
