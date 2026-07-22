<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.startup-validation startup validation (good patterns)

Substrate-original good-pattern example for configuration-management.startup-validation. Configuration is
validated at boot; the workload refuses to start on missing or invalid
required configuration and aggregates failures into one named error.

## Python: a startup gate that aggregates and fails fast

```python
def validate_config(env: dict) -> None:
    errors = []
    for key in ("DB_HOST", "PAYMENTS_BASE_URL", "HTTP_TIMEOUT_SECONDS"):
        if not env.get(key):
            errors.append(f"missing required key: {key}")
    timeout = env.get("HTTP_TIMEOUT_SECONDS")
    if timeout and not _is_positive_number(timeout):
        errors.append("HTTP_TIMEOUT_SECONDS must be a positive number")
    if errors:
        raise SystemExit("configuration invalid:\n  " + "\n  ".join(errors))

# called in the bootstrap path before the listener binds, in every environment
validate_config(os.environ)
```
