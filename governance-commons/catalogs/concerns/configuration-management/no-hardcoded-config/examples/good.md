<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: configuration-management.no-hardcoded-config no hardcoded configuration (good patterns)

Substrate-original good-pattern examples for configuration-management.no-hardcoded-config. Environment-varying
values are read from a configuration source through a typed accessor, not
inlined at the call site.

## Python: endpoints and timeouts read from a typed config module

```python
# config.py: the designated configuration module
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Config:
    payments_base_url: str
    http_timeout_seconds: float

def load_config() -> Config:
    return Config(
        payments_base_url=require("PAYMENTS_BASE_URL"),
        http_timeout_seconds=float(require("HTTP_TIMEOUT_SECONDS")),
    )

def require(key: str) -> str:
    value = os.environ.get(key)
    if value is None or value == "":
        raise KeyError(f"required configuration missing: {key}")
    return value
```

```python
# client.py: business logic reads through the config, no literals
client = HttpClient(base_url=cfg.payments_base_url, timeout=cfg.http_timeout_seconds)
```
