<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.no-hardcoded-config no hardcoded configuration (anti-patterns)

Substrate-original anti-pattern examples for configuration-management.no-hardcoded-config. Environment-varying
values are inlined as literals in business logic, coupling environment changes
to code changes.

## Python: production hostname and timeout inlined in a constructor

```python
# client.py: the endpoint and timeout are hardcoded
client = HttpClient(
    base_url="https://payments.prod.internal:8443",  # environment-varying literal
    timeout=2.5,                                       # environment-tuned literal
)
```

Why this is flagged: the production endpoint can only change through a code
change, review, build, and deploy. When the dependency moves or the timeout
proves wrong under load, the fix is a code change under incident pressure.
The remediation is to externalize both values to the configuration source and
read them through the configuration module.
