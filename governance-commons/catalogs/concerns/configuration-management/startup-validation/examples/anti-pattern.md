<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.startup-validation startup validation (anti-patterns)

Substrate-original anti-pattern example for configuration-management.startup-validation. Configuration is
read lazily at first use with no startup gate, so the workload boots and
degrades at request time.

## Python: lazy read at first use, no startup check

```python
def handle_request(req):
    # first request that needs the value discovers it is missing
    base_url = os.environ["PAYMENTS_BASE_URL"]  # KeyError in production traffic
    ...
```

Why this is flagged: there is no validation in the bootstrap path. A missing
or malformed required value is not discovered until a request happens to
exercise the path, turning a deploy-time error into a production incident.
