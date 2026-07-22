<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.no-swallowing-default no swallowing default (good patterns)

Substrate-original good-pattern examples for configuration-management.no-swallowing-default. A required value is
read through an accessor that surfaces absence rather than masking it.

## Go: LookupEnv with an explicit presence check

```go
host, ok := os.LookupEnv("DB_HOST")
if !ok || host == "" {
    return fmt.Errorf("required configuration missing: DB_HOST")
}
```

## Python: required accessor raises on absence

```python
db_host = require("DB_HOST")  # raises KeyError if absent or empty
```

The absence becomes a loud, named failure at the read or at the startup
validation gate (configuration-management.startup-validation), not a runtime error at first query.
