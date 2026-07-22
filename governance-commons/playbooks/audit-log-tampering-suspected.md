<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Audit Log Tampering Suspected

**ID**: audit-log-tampering-suspected
**Severity**: critical
**Related catalogs**: OWASP ASI08 (Inadequate Audit Trails), STRIDE-T (Tampering), STRIDE-R (Repudiation)
**Compliance relevance**: EU AI Act Art 12, SOC2 CC7.2, NIST AI RMF MEASURE-1.3, GDPR Art 32
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- Hash chain verification fails: prev_hash mismatch
- Audit log entries missing for time periods when activity should
  exist
- Audit log shows gaps in event_id sequencing (ULIDs out of order
  beyond clock-skew tolerance)
- Audit log file size shrank without rotation
- Audit log file modification timestamp is newer than the latest
  recorded event
- Backup audit log differs from local audit log
- File permissions on audit log changed unexpectedly

Definitive confirmation:

- Hash chain verification script reports specific mismatch with
  location
- Backup comparison shows missing or modified entries
- File-integrity monitoring tool reports unauthorized modification
- Multiple independent verification methods agree

Not this scenario if:

- Log rotation just happened and old entries moved to archive
- A clock skew issue produced out-of-order entries (entry_ids
  still sequential within ~5 seconds is normal)
- Manual audit during a legitimate workflow (legitimate admins
  testing the verification) — coordinate first to avoid false alarms

## Immediate Containment (0-15 minutes)

This is one of the most serious incident types because:
1. The integrity of all future audit evidence may be in question
2. Required compliance reporting depends on trustworthy logs
3. The tampering may be an active attack still in progress

1. **Stop writing to the local audit log.** Switch to a temporary
   write target if needed. Prevent further potential tampering
   from masking the original event.

       # Pause framework processes
       # Make the audit log immutable temporarily
       chattr +i ~/.local/state/<framework>/audit.jsonl  # Linux
       # macOS equivalent: chflags uchg <file>

2. **Preserve everything.** Hash and snapshot the current state:

       sha256sum ~/.local/state/<framework>/audit.jsonl > \
           ./incident-$(date +%Y%m%d-%H%M%S)-audit-hash.txt
       cp -p ~/.local/state/<framework>/audit.jsonl \
           ./incident-audit-snapshot.jsonl

3. **Compare against backups.** If hash-chained audit logs are
   shipped to an immutable backup (Backblaze B2, S3 Object Lock,
   etc.), retrieve the latest backup and compare.

       diff <(jq -c . ./incident-audit-snapshot.jsonl) \
            <(jq -c . ./backup-audit.jsonl) > ./incident-diff.txt

4. **Identify the user/process with write access.** Who or what
   could have modified the log?

       ls -la ~/.local/state/<framework>/
       # Check recent shell history
       fc -l 1 | tail -50

5. **Notify security team immediately.** Audit log tampering is
   in the "report regardless of confirmation status" tier of
   incidents.

## Investigation (15-180 minutes)

1. **Verify the hash chain across the entire log.**

       python3 - <<'EOF'
       import hashlib, json, sys
       prev_hash = "sha256:" + "0" * 64
       with open("audit.jsonl") as f:
           for line_num, line in enumerate(f, 1):
               entry = json.loads(line)
               if entry["prev_hash"] != prev_hash:
                   print(f"Line {line_num}: prev_hash mismatch")
                   print(f"  Expected: {prev_hash}")
                   print(f"  Got:      {entry['prev_hash']}")
                   sys.exit(1)
               # Recompute this_hash
               this_hash_field = entry.pop("this_hash")
               canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
               computed = "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()
               if this_hash_field != computed:
                   print(f"Line {line_num}: this_hash mismatch")
                   sys.exit(1)
               prev_hash = this_hash_field
           print("Hash chain verified")
       EOF

2. **Identify the tampering window.** The hash chain mismatch
   pinpoints where verification first fails. Everything before is
   trustworthy; everything from that point is suspect.

3. **Determine what was modified.** Compare against backup:
   - Entries deleted (present in backup, missing locally)
   - Entries modified (different content)
   - Entries added (present locally, missing in backup)

4. **Identify the actor.** Common sources of tampering:
   - **Accidental**: a script with bad jq expression overwrote the
     log; a backup-restore operation copied an older version
   - **Misguided**: a developer "cleaning up logs" removed entries
     they thought were noise
   - **Compromised principal**: an attacker with write access tried
     to hide their tracks
   - **System-level**: filesystem corruption (verify checksums of
     other files)

5. **Determine downstream impact.** What decisions were made based
   on the tampered logs? Are any compliance artifacts derived from
   the affected period?

Questions to answer:

- What entries are different/missing/added?
- When did the tampering occur (timestamp of file modification)?
- Who or what process had write access at that time?
- Was the tampering successful in hiding evidence of other actions?
- What downstream artifacts depended on the affected log entries?

## Remediation (varies)

1. **Restore from trusted backup if possible.** The immutable
   backup should be authoritative. Replace the local log.

       cp ./backup-audit.jsonl ~/.local/state/<framework>/audit.jsonl

2. **Document the discrepancy.** The tampered version vs. backup
   version difference is itself an audit-relevant event. Record
   the full diff in a separate evidence file.

3. **If no clean backup exists**, the audit trail integrity for
   the affected period is permanently compromised. This must be:
   - Documented in incident records
   - Disclosed to affected compliance frameworks (auditors)
   - Treated as material when assessing the period's compliance
     evidence

4. **Investigate and remediate the access path.** How did the
   actor have write access? Common fixes:
   - Audit log file should be append-only at filesystem level
   - Audit log should be shipped to write-once backup within
     seconds of write
   - Audit log writer should be the only process with write
     permission (chown/chmod restrictions)

5. **Address any masked events.** If the tampering was hiding
   other malicious activity, separate incident response procedures
   apply to those events.

Verification:

- Hash chain verifies cleanly post-restore
- File permissions prevent unauthorized write
- Backup pipeline is functioning
- Test: attempt unauthorized modification, confirm it fails

## Hardening (post-incident)

1. **Append-only filesystem permissions.** Make audit log files
   append-only using OS features:

       # Linux: chattr +a
       chattr +a ~/.local/state/<framework>/audit.jsonl

       # macOS: lacks append-only at filesystem level; use
       # immutable backups with frequent shipping instead

2. **Real-time backup to immutable storage.** Each audit event
   ships to a write-once backend within seconds of creation:
   - AWS S3 Object Lock (compliance mode)
   - Azure Blob Storage immutability
   - Backblaze B2 with retention lock
   - Cloud audit log services with tamper-evident storage

3. **Periodic verification.** Hash chain verification runs:
   - On every framework startup
   - Hourly during active sessions
   - Before each /audit-export run
   - Nightly as scheduled task

4. **Cryptographic signing.** Upgrade from hash-chaining alone to
   asymmetric signatures for higher-stakes deployments. Each entry
   signed with system private key; verification with public key.

5. **Separation of duties.** The principal writing audit logs is
   different from any principal that processes them. Same process
   writing and reading concentrates tampering risk.

6. **Anomaly detection.** Alert on:
   - Audit log file size decrease
   - Modification timestamp changing without new entries
   - Gaps in event_id sequence beyond clock-skew tolerance
   - Process accessing audit log that isn't on the writer allowlist

## Compliance Evidence

Artifacts to capture:

- Tampered audit log snapshot (with hash)
- Backup audit log snapshot (with hash)
- Full diff showing exact discrepancy
- Hash chain verification report
- File access logs (who accessed when)
- ADRs documenting hardening changes
- Communication with auditors/regulators

Required notifications:

- **Internal security team**: yes, critical
- **Internal compliance team**: yes, may affect audit evidence
- **External auditors**: typically yes if the affected period is
  within current audit scope; consult internal audit/compliance
  function for specifics
- **Regulatory body**: depends on jurisdiction and severity. EU AI
  Act Article 73 applies for high-risk AI systems. Financial
  regulators may have specific tampering reporting requirements.
- **Customer notification**: if customer data audit trails were
  affected and contractual SLAs reference audit evidence
- **Cyber-insurance carrier**: incident may be covered; report per
  policy

## References

- Threat catalogs: STRIDE-T (Tampering), OWASP ASI08
- Audit envelope spec: [spec/audit-envelope.md](../spec/audit-envelope.md)
- Hash chain verification methodology: see the inline script above
- Higher-assurance alternative: Asqav (ML-DSA-65 signing)

## Revision history

    2026-05-12: Initial playbook authored.
