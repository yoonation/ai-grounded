<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.restore-verification restore verification (good pattern)

Substrate-original good-pattern example for backup-recovery.restore-verification. A scheduled restore
test reconstructs the data into an isolated target, checks integrity, measures
time against the recovery time objective, and alerts on failure.

## Scheduled restore-test job (illustrative)

```bash
#!/usr/bin/env bash
set -euo pipefail

# 1. restore the latest backup into an isolated, non-production target
start=$(date +%s)
restore_into --target isolated-verify --from "$(latest_backup orders)"

# 2. verify completeness and integrity against a known expectation
verify_row_counts --store orders --target isolated-verify
verify_referential_integrity --target isolated-verify
smoke_check --target isolated-verify

# 3. measure restore time against the tier RTO and record/alert
elapsed=$(( $(date +%s) - start ))
record_restore_result --store orders --seconds "$elapsed" --rto 3600
# record_restore_result raises an alert via monitoring-alerting on failure
```

The restore is exercised on a cadence, isolated from production, checked for
correctness, timed against the objective, and its outcome is recorded. The
backup is proven recovery capability, not assumed.
