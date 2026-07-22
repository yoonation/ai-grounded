<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.strategy-adr strategy ADR (anti-pattern)

Substrate-original anti-pattern example for configuration-management.strategy-adr. No strategy is
recorded; each service invents its own configuration conventions.

## The absence of a record

```
(no ADR exists)
```

Symptoms that follow: one service reads config from environment, another from
a checked-in file, a third from an undocumented service; precedence differs
per service; some validate at startup and some do not; secrets land in
config files in the services with no recorded boundary. Reviewers have no
written standard to check a service against, so every review relitigates the
basics. The remediation is to author the strategy ADR using the substrate
decision framework as the companion.
