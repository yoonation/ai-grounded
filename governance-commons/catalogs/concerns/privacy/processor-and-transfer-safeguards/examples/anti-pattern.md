<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Example: privacy.processor-and-transfer-safeguards processor agreement and transfer mechanism recorded (anti-pattern)

Substrate-original illustration.

```yaml
# A processor receives personal data with no agreement and an unassessed transfer.
processors:
  - name: analytics-vendor
    dpa: none                   # no data-processing agreement
    region: us                  # EU personal data sent here, no transfer mechanism
```

## Why this violates the rule

Personal data is handed to a processor with no data-processing agreement and
flows across a border purely because the vendor is hosted there, with no
recognized transfer mechanism identified or assessed. The processor has latitude
to reuse the data and the transfer rests on nothing. Binding the processor by a
DPA to instruction-only use and resting the transfer on a recognized mechanism is
the fix.
