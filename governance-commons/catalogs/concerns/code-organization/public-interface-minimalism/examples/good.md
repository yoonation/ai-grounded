<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.public-interface-minimalism public interface minimalism (good pattern)

Substrate-original illustration. A module exposes one factory function
and a result type as its contract and keeps helpers and state private,
declaring the surface explicitly.

## Python: an explicit, minimal public surface

```python
# rate_limiter/__init__.py
from ._limiter import RateLimiter, Decision

__all__ = ["RateLimiter", "Decision"]


# rate_limiter/_limiter.py  (underscore: module-internal file)
class Decision:
    def __init__(self, allowed: bool, retry_after: float):
        self.allowed = allowed
        self.retry_after = retry_after

class RateLimiter:
    def __init__(self, rate, burst):
        self._tokens = burst          # private state
        self._rate = rate
    def check(self) -> Decision:
        return self._refill_and_decide()
    def _refill_and_decide(self) -> Decision:   # private helper
        ...
```

Why this passes: __all__ declares the contract (RateLimiter, Decision)
in one obvious place; the token-bucket internals (_tokens, _rate,
_refill_and_decide) are private and free to change; the public method
check() returns a public type (Decision), leaking no internals. Adding to
the contract requires editing __all__, a visible, reviewable act.
