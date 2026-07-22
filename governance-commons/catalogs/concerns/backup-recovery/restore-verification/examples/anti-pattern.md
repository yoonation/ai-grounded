<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: backup-recovery.restore-verification restore verification (anti-pattern)

Substrate-original anti-pattern example for backup-recovery.restore-verification. The backup job
succeeds and the restore is never exercised, so recoverability is assumed.

## Backup-only job, no restore test (illustrative)

```bash
#!/usr/bin/env bash
set -euo pipefail

# the backup runs and reports success
backup_store orders --to s3://backups/orders/

# ...and that is the end of it: no restore is ever performed,
# no integrity check, no time measurement, no isolated target.
echo "backup ok"
```

The dashboard is green and the copy may be unrestorable: an unreadable
format, a missing dependency, silent corruption, a scope that quietly dropped
a table, or expired restore credentials would all go undetected until a real
incident. Add a scheduled restore test that restores into an isolated target
and verifies the result.
