<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: documentation.decisions-and-operations decisions and operations (anti-pattern)

Substrate-original anti-pattern example for documentation.decisions-and-operations. The knowledge a team
needs lives only with individuals.

## What "documentation" looks like here (illustrative)

```text
- Why integer cents? "Ask Dana, she decided it in a thread somewhere."
- What changed in 2.0.0? "Check the commits, there's no changelog."
- How do we bring the service up? "Pair with someone who knows."
- Settlement queue alert fired at 3am? "Page Dana; there's no runbook."
```

Nothing is recorded: the decision rationale, the release changes, the setup
steps, and the incident response all depend on a specific person being
available. Onboarding is slow, settled debates reopen, and incidents run
long. Record the decision as an ADR, maintain a changelog, and write the
setup guide and runbook.
