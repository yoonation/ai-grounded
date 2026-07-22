<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: agentic-systems.tool-and-skill-trust-policy tool and skill trust policy (anti-pattern)

Substrate-original illustration.

```python
# The agent discovers and loads skills dynamically from an open registry.
for skill_url in registry.list_skills(query):
    skill = download_and_load(skill_url)   # no source check, no vetting
    agent.register(skill)                  # admitted with the agent's authority
```

## Why this violates the rule

The agent loads third-party skills dynamically with no source check, no vetting,
and no revocation path, so a malicious or compromised skill is admitted and runs
with the agent's full authority, subverting every other control from a position
of trust. This is where supply-chain compromise becomes agent compromise. A
recorded policy with an admitted set, a vetting gate, an explicit dynamic-skill
stance, and revocation is the fix.
