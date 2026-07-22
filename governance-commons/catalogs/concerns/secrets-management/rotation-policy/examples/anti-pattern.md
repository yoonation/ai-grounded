<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Example: secrets-management.rotation-policy rotation policy (anti-patterns)

Substrate-original anti-pattern examples for secrets-management.rotation-policy.
These patterns illustrate violations and should NOT be used.

## Anti-pattern A: "Never rotated" credentials

```text
# Findings from a credential audit:
- prod/db/password: last rotation never (created 2019-03-14)
- prod/stripe/api-key: last rotation never (created 2020-07-22)
- prod/oauth-client-secret: last rotation never (created 2018-11-01)
```

Why this violates secrets-management.rotation-policy: credentials that have
never rotated represent a years-long exposure window. The
attack surface includes every former contributor and every
log line written across the credential's lifetime. The
substrate-recommended cadence varies by class (see the
review checklist), but "never" fails every class.

## Anti-pattern B: Calendar-based manual rotation that slips

```text
# Team calendar 2025:
- Q1: rotate API keys (DONE)
- Q2: rotate API keys (skipped due to launch)
- Q3: rotate API keys (skipped due to incident response)
- Q4: rotate API keys (skipped due to year-end freeze)
```

Why this violates secrets-management.rotation-policy: manual cadence is the
first thing that slips when operational pressure is high.
The substrate-recommended pattern is automation; where
automation is not available (some third-party APIs do not
support API-driven rotation), the manual schedule has a
named owner who is on the hook regardless of competing
priorities.

## Anti-pattern C: Rotation requires service restart

```text
# Application reads credential at startup; cached forever.
# Rotation procedure:
1. Update secret in platform
2. Trigger rolling restart of all application replicas
3. Wait for all replicas to come back
4. Verify
```

Why this violates secrets-management.rotation-policy: rotation that requires
service restart is rotation that gets deferred indefinitely
in any organization with deployment freezes. The
substrate-recommended pattern is in-application refresh
via TTL or per-session retrieval, not restart.

## Anti-pattern D: Rotation creates new credential but never revokes old

```python
# DO NOT DO THIS
def rotate_api_key(credential_name: str):
    new_key = api_provider.create_key(name=credential_name + "-v2")
    secrets_platform.set(credential_name, new_key)
    # Old key is never revoked
```

Why this violates secrets-management.rotation-policy: the old credential
remains valid and can be used by anyone who captured it
during its exposure window. Substrate-recommended pattern
is to revoke the old credential after the dual-key window,
not let it accumulate.

## Anti-pattern E: Same credential rotated in dev, staging, and production simultaneously

```yaml
# CI workflow that rotates all environments at once
- name: Rotate credentials
  run: |
    rotate-credentials --env dev,staging,prod \
                       --secret api-key
```

Why this violates secrets-management.rotation-policy (in spirit): cross-
environment rotation removes the staging gate. If the
rotation procedure has a bug, all environments hit the
bug simultaneously. Substrate-recommended pattern: rotate
non-production first; observe; rotate production
separately.

## Anti-pattern F: Rotation not audited

```text
# Rotation script writes to a transient log file that
# is not collected anywhere. After the script completes,
# there is no evidence the rotation happened beyond the
# new credential's existence.
```

Why this violates secrets-management.rotation-policy: without audit evidence,
periodic review cannot confirm the cadence was met. A
"rotation" that has no trace is indistinguishable from
no rotation. Substrate-recommended pattern: emit audit
events to the security log aggregator.

## Anti-pattern G: Inventory does not match reality

```yaml
# /security/rotation-inventory.yaml says:
prod/api-key:
  cadence-days: 90
  last-rotated: 2024-12-15  # 6 months ago

# Reality (from platform audit log):
# Last rotation: 2024-08-01 (10 months ago)
```

Why this violates secrets-management.rotation-policy: the inventory drift
means the documented cadence is fiction. Periodic review
exists in name only. Substrate-recommended pattern:
generate the inventory from the platform's audit log,
not by hand.

## Anti-pattern H: No compromise-triggered procedure

```text
# Incident: a contractor's laptop was lost with cached
# Vault tokens.
# Response: rotation discussion in a Slack thread,
# decisions made ad-hoc, no consistent procedure followed.
# Two relevant tokens are not rotated because they were
# missed.
```

Why this violates secrets-management.rotation-policy: improvised response
misses credentials and fails to document. The substrate-
recommended pattern is a runbook that enumerates the
credential classes and the rotation order; the procedure
is exercised in tabletops so it works when needed.

## Cross-reference

- Good patterns: examples/secrets-management/rotation-policy-good.md
- Substrate rule: secrets-management.rotation-policy
- Review checklist: checklist.md
