<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: code-organization.module-boundary-cohesion module-boundary cohesion (anti-pattern)

Substrate-original illustration. A utils module accretes unrelated
helpers united only by not belonging anywhere else, and the whole
codebase imports it. It cannot be described without listing its contents.

## Package layout: a grab-bag utils module

```
utils.py
    def format_currency(amount): ...      # presentation concern
    def retry(fn, times): ...             # control-flow concern
    def parse_iso_date(s): ...            # parsing concern
    def send_slack_alert(msg): ...        # infrastructure concern
    def slugify(title): ...               # text concern
    def tax_rate_for(region): ...         # domain pricing concern
```

Why this is a finding: there is no single reason this module changes; it
changes whenever any unrelated concern changes. "What is utils
responsible for?" can only be answered with a list joined by "and"
(review question 1 fails). Because everything imports utils, its fan-in
is the highest in the codebase, making it a coupling hotspot (question 4)
and, worse, tax_rate_for is a domain rule hiding in a junk drawer.

Remediation: move each helper to the module that owns its responsibility
(format_currency to a presentation module, tax_rate_for into pricing),
and give genuinely cross-cutting helpers (retry) a named module that
states the capability rather than the catch-all name.
