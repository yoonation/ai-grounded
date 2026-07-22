<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.public-interface-minimalism public interface minimalism (anti-pattern)

Substrate-original illustration. A module exports every symbol it
defines, with no explicit surface, so callers reach into its internals
and the module loses the freedom to change them.

## Python: implicit, leaking surface

```python
# rate_limiter.py   (no __all__; everything is importable)
class RateLimiter:
    def __init__(self, rate, burst):
        self.tokens = burst           # public by default
        self.rate = rate
    def check(self):
        self.refill()
        ...
    def refill(self):                 # meant to be internal, but exported
        ...

# elsewhere in the codebase:
from rate_limiter import RateLimiter
limiter = RateLimiter(10, 20)
limiter.tokens -= 1        # caller mutates internal state directly
limiter.refill()           # caller drives an internal step
```

Why this is a finding: with no declared surface, tokens and refill become
de-facto public the moment a caller touches them. Now the token-bucket
representation cannot change without breaking callers, and there is no
single place that states what the module promises. The test-template
scenario "no internal referenced externally" fails on limiter.tokens and
limiter.refill().

Remediation: declare __all__, move the file behind a package with an
internal module, mark state and refill private, and expose only the
intended contract as in the good-pattern example.
