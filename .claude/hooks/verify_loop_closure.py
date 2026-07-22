#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
verify_loop_closure.py: pre-commit closure enforcement.

Mechanical airbag for the framework's loop closure mechanism. Reads
events.jsonl in the active feature directory and blocks the commit if
any P1 or P2 item from upstream agents lacks valid closure evidence.

Closure rules:
- P1 items require a closure-claimed, closure-verified, or overridden
  event NOT superseded by a later closure-rejected event.
- P2 items require the same OR a deferred event with matching entry
  in deferrals.md.
- P3 items have no closure requirement (informational only).
- A closure-rejected event blocks the item unless superseded by a
  later closure-verified or overridden event. A bare closure-claimed
  after a rejection does NOT clear it (the claim must be re-verified).

Backward compatibility:
- Events written before Phase 2.5.4 may have items_raised as string
  arrays (no priority). These are treated as P1 conservatively.

Cross-tool compatibility:
- Both closure-claimed (user self-attestation) and closure-verified
  (closure-auditor confirmation) count as closure evidence. This
  supports non-Claude AI tool users who don't have closure-auditor.

Emergency override:
- Setting SKIP_LOOP_VERIFY=1 in the environment bypasses the check
  entirely and exits 0, but ONLY when SKIP_LOOP_VERIFY_REASON is also
  set to a non-empty reason. The bypass is the one hard control an
  agent invokes itself, and a self-invoked bypass with no recorded
  reason normalizes into a silent default (OBS-001 / IMP-15). Requiring
  a per-use reason recorded at the moment of use is the disk-truth shape
  applied to the escape hatch: a bypass with no recorded justification
  is a declaration, not a justification, so it is refused. This does not
  block legitimate use (a reason can always be supplied); it makes the
  bypass impossible to apply silently-by-default. Intended for rare
  emergencies (hotfixes, broken framework state). The bypass and its
  reason log loudly to stderr so they are auditable in CI logs. Document
  the reason in your commit message as well when you use it.

Usage:
    Configure as pre-commit hook (see hook setup section in
    .claude/docs/agent-coordination.md). Exits 0 to allow commit,
    non-zero to block.

Dependencies: Python 3.9+ stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from _feature import staged_feature_dirs


# ---------- Types ----------


@dataclass
class Item:
    """A pending-resolution item raised by an upstream agent."""
    item_id: str
    priority: str  # P1 | P2 | P3
    source_agent: str
    source_invocation_id: str
    raised_ts: str


@dataclass
class ClosureActivity:
    """All closure-related events for a single item, in chronological order."""
    events: list[dict] = field(default_factory=list)


@dataclass
class Verdict:
    """Final determination for a single item after walking its activity."""
    item: Item
    status: str  # closed | rejected | unverified | unaddressed | deferred_complete | deferred_incomplete
    detail: str
    blocks_commit: bool
    was_deferred: bool = False


# ---------- Events parsing ----------


def read_events(events_path: Path) -> list[dict]:
    """Read events.jsonl into a list of dicts, skipping malformed lines."""
    if not events_path.exists():
        return []

    events: list[dict] = []
    with events_path.open("r") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                event["_line_no"] = line_no
                events.append(event)
            except json.JSONDecodeError as exc:
                print(
                    f"Warning: events.jsonl line {line_no} is malformed JSON: {exc}",
                    file=sys.stderr,
                )
                continue

    return events


def extract_items(events: list[dict]) -> list[Item]:
    """
    Walk events and produce a list of all P1/P2/P3 items raised.

    Handles both new format (items_raised as array of objects) and
    legacy format (items_raised as array of strings; treated as P1).
    """
    items: list[Item] = []

    for event in events:
        if event.get("event") != "completed":
            continue

        items_raised = event.get("items_raised")
        if not items_raised:
            continue

        agent = event.get("agent", "unknown")
        invocation_id = event.get("invocation_id", "unknown")
        ts = event.get("ts", "unknown")

        for raised in items_raised:
            if isinstance(raised, str):
                # Legacy format: pre-Phase-2.5.4 events have item IDs
                # as bare strings without priority annotations.
                # Conservative default: treat as P1 (must close).
                items.append(
                    Item(
                        item_id=raised,
                        priority="P1",
                        source_agent=agent,
                        source_invocation_id=invocation_id,
                        raised_ts=ts,
                    )
                )
            elif isinstance(raised, dict):
                item_id = raised.get("id")
                priority = raised.get("priority", "P1")
                if not item_id:
                    continue
                if priority not in ("P1", "P2", "P3"):
                    print(
                        f"Warning: invalid priority {priority!r} for item "
                        f"{item_id} in event {invocation_id}; "
                        f"treating as P1 conservatively",
                        file=sys.stderr,
                    )
                    priority = "P1"
                items.append(
                    Item(
                        item_id=item_id,
                        priority=priority,
                        source_agent=agent,
                        source_invocation_id=invocation_id,
                        raised_ts=ts,
                    )
                )

    return items


def index_closure_activity(events: list[dict]) -> dict[str, ClosureActivity]:
    """
    Build a map of item_id -> ClosureActivity from closure-related events.

    Closure events: closure-claimed, closure-verified, closure-rejected,
    overridden, deferred.
    """
    closure_events = {
        "closure-claimed",
        "closure-verified",
        "closure-rejected",
        "overridden",
        "deferred",
    }

    activity: dict[str, ClosureActivity] = defaultdict(ClosureActivity)

    for event in events:
        event_type = event.get("event")
        if event_type not in closure_events:
            continue

        # Item ID can live in two places depending on event type:
        # - closure_evidence.item_id for closure events with evidence
        # - item_id at root for deferred events (no closure_evidence)
        item_id = None
        closure_evidence = event.get("closure_evidence")
        if isinstance(closure_evidence, dict):
            item_id = closure_evidence.get("item_id")
        if not item_id:
            item_id = event.get("item_id")

        if not item_id:
            continue

        activity[item_id].events.append(event)

    # Sort each item's events chronologically
    for item_id, act in activity.items():
        act.events.sort(key=lambda e: e.get("ts", ""))

    return dict(activity)


# ---------- Deferral verification ----------


def verify_deferral_documented(feature_dir: Path, item_id: str) -> bool:
    """
    Check that deferrals.md exists and documents the item.

    An item is considered documented if EITHER form is present:

    - Form 1 (one entry per item): a markdown heading whose text
      contains the item ID, e.g. ``## T-RS-008``.
    - Form 2 (grouped deferral): a structured ``Source items:`` or
      ``**Source items**:`` line that lists the item ID among others,
      e.g. ``**Source items**: SE-005, T-RS-008, PROD-011``. This is
      the shape closure-auditor emits for consolidated items, where a
      single deferral entry covers several IDs that appear in the
      Source-items line rather than in the heading.

    Without Form 2, grouped deferrals whose covered IDs live only in a
    body line failed silently (the deferred event looked undocumented
    and blocked the commit). The label match is case-insensitive; the
    item ID is matched case-sensitively with word boundaries.
    """
    deferrals_path = feature_dir / "deferrals.md"
    if not deferrals_path.exists():
        return False

    content = deferrals_path.read_text()

    # Form 1: item ID in a markdown heading (## ... ITEM-ID ...)
    heading_pattern = re.compile(
        rf"^#{{1,6}}\s.*\b{re.escape(item_id)}\b", re.MULTILINE
    )
    if heading_pattern.search(content):
        return True

    # Form 2: item ID on a structured "Source items:" line. Tolerates
    # an optional leading bold marker (** ... **) and any colon/bold
    # placement; requires the item ID later on the same line.
    source_items_pattern = re.compile(
        rf"^\s*\*{{0,2}}(?i:source items)\b.*\b{re.escape(item_id)}\b",
        re.MULTILINE,
    )
    return bool(source_items_pattern.search(content))


# ---------- Disk-truth read evidence (Capability 3) ----------


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


@dataclass
class ReadCheck:
    """Result of validating a closure-verified event's disk-read evidence."""
    ok: bool
    detail: str


def _sha256_file(path: Path) -> str:
    """Stream a file through SHA-256 and return the hex digest."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_read_evidence(event: dict, repo_root: Path) -> ReadCheck:
    """
    Disk-truth gate: a closure-verified must carry machine-checkable read
    evidence, and the gate independently re-reads it.

    Requires closure_evidence.read = {path, sha256}. The gate confirms the
    read block is present and well-formed, that path resolves to an existing
    non-empty file on disk, and that sha256 is a 64-hex digest. It then
    recomputes the digest from disk and FAILS CLOSED on a mismatch (ADR-002).
    SHA-256 preimage resistance makes a MATCHING recorded digest cryptographic
    proof that a real hashing tool ran over these exact bytes; a mismatch
    means either the digest was composed rather than computed (the feature
    007 fabrication episode) or the file was edited after the audit. Both
    invalidate the verification: the honest remediation for a post-audit edit
    is a superseding closure-verified event carrying a freshly computed
    digest (the verdict logic takes the latest event), or re-running the
    closure audit after cosmetic passes such as lint and formatting.

    A closure-verified lacking valid read evidence is auto-rejected. A claim
    of a match with no recorded read of the artifact is a declaration, not
    evidence. This is the single class that caused the most expensive misses
    in feature 003 (prose-only verifications that no one re-read).

    Scope: this binds closure-verified only. closure-claimed (cross-tool
    self-attestation) and overridden (ADR acceptance) are unchanged.
    """
    closure_evidence = event.get("closure_evidence")
    if not isinstance(closure_evidence, dict):
        return ReadCheck(
            False,
            "closure-verified has no closure_evidence block to carry a disk read",
        )

    read = closure_evidence.get("read")
    if not isinstance(read, dict):
        return ReadCheck(
            False,
            "closure-verified carries no closure_evidence.read {path, sha256}; "
            "a verification with no recorded artifact read is a declaration, "
            "not evidence",
        )

    path_str = read.get("path")
    sha = read.get("sha256")

    if not isinstance(path_str, str) or not path_str.strip():
        return ReadCheck(False, "closure_evidence.read.path is missing or not a string")

    if not isinstance(sha, str) or not SHA256_RE.match(sha):
        return ReadCheck(
            False,
            f"closure_evidence.read.sha256 is not a 64-hex digest (got {sha!r})",
        )

    candidate = Path(path_str)
    if not candidate.is_absolute():
        candidate = repo_root / candidate

    if not candidate.exists() or not candidate.is_file():
        return ReadCheck(
            False,
            f"closure_evidence.read.path does not resolve to a file on disk: {path_str}",
        )

    if candidate.stat().st_size == 0:
        return ReadCheck(
            False,
            f"closure_evidence.read.path is an empty file, no artifact to verify: {path_str}",
        )

    # Fail closed on recorded-versus-disk mismatch (ADR-002): a mismatch is
    # either a digest that was never computed by a tool (fabricated evidence)
    # or a file edited after the audit. Both invalidate the verification.
    try:
        current = _sha256_file(candidate)
    except OSError as exc:
        return ReadCheck(
            False,
            f"could not recompute the digest for {path_str} ({exc}); "
            f"unverifiable evidence fails closed",
        )
    if current.lower() != sha.lower():
        return ReadCheck(
            False,
            f"{path_str} recorded digest {sha[:12]}... does not match disk "
            f"{current[:12]}.... Either the digest was not produced by a real "
            f"hash of this file (fabricated evidence) or the file changed "
            f"after the audit. Remediation: recompute with "
            f"'shasum -a 256 {path_str}' and emit a superseding "
            f"closure-verified event with the fresh digest, or re-run the "
            f"closure audit; run audits after lint/format passes so cosmetic "
            f"edits do not stale fresh evidence",
        )

    return ReadCheck(True, f"disk read present, digest matches disk ({path_str})")


# ---------- Verdict logic ----------


def determine_verdict(
    item: Item, activity: ClosureActivity, feature_dir: Path, repo_root: Path
) -> Verdict:
    """
    Walk an item's closure activity and produce a final verdict.

    Rules:
    - Latest closure-rejected blocks the item until superseded by a
      later closure-verified.
    - closure-claimed, closure-verified, and overridden all count as
      valid closures (for cross-tool support).
    - deferred is valid for P2 only AND requires deferrals.md entry.
    - P3 items don't block regardless of activity.
    """
    if item.priority == "P3":
        return Verdict(
            item=item,
            status="closed",
            detail="P3 informational; no closure required",
            blocks_commit=False,
        )

    if not activity.events:
        return Verdict(
            item=item,
            status="unaddressed",
            detail="No closure activity found",
            blocks_commit=True,
        )

    # Determine whether an unsuperseded rejection is active. Per the
    # closure rules, a closure-rejected blocks the item until a LATER
    # closure-verified or overridden supersedes it. A bare
    # closure-claimed does NOT clear a prior rejection (the claim must be
    # re-verified). Walk chronologically (events are pre-sorted by ts).
    rejection_active = False
    rejecting_event = None
    for ev in activity.events:
        et = ev.get("event")
        if et == "closure-rejected":
            rejection_active = True
            rejecting_event = ev
        elif et in ("closure-verified", "overridden"):
            rejection_active = False

    if rejection_active:
        rej = rejecting_event or activity.events[-1]
        return Verdict(
            item=item,
            status="rejected",
            detail=(
                f"closure-rejected at line {rej.get('_line_no', '?')} not "
                f"superseded by a later closure-verified or overridden: "
                f"{rej.get('rejection_rationale', '(no rationale provided)')}. "
                f"A bare closure-claimed does not clear a rejection."
            ),
            blocks_commit=True,
        )

    # No active rejection. Decide on the latest event (original
    # latest-wins semantics for the non-rejection cases). The latest
    # event cannot be an unsuperseded closure-rejected here.
    latest = activity.events[-1]
    latest_type = latest.get("event")

    if latest_type == "closure-verified":
        # Disk-truth gate: the verification transition that clears an item
        # must carry an independent read of the artifact it verified. A
        # closure-verified with no valid read block is auto-rejected.
        check = verify_read_evidence(latest, repo_root)
        if not check.ok:
            return Verdict(
                item=item,
                status="unverified",
                detail=(
                    f"closure-verified at line {latest.get('_line_no', '?')} "
                    f"lacks valid disk-read evidence: {check.detail}"
                ),
                blocks_commit=True,
            )
        return Verdict(
            item=item,
            status="closed",
            detail=(
                f"closure-verified at line {latest.get('_line_no', '?')}; "
                f"{check.detail}"
            ),
            blocks_commit=False,
            # F19: a closure-verified that supersedes a rejection ON A
            # DEFERRED item is a verified deferral, not a fresh close. Flag
            # it so the tally bins it as Deferred, not Closed. Display only;
            # blocking behavior is unchanged.
            was_deferred=any(
                e.get("event") == "deferred" for e in activity.events
            ),
        )

    if latest_type in ("closure-claimed", "overridden"):
        return Verdict(
            item=item,
            status="closed",
            detail=(
                f"{latest_type} at line {latest.get('_line_no', '?')}; "
                f"type: {latest.get('closure_evidence', {}).get('type', 'unknown')}"
            ),
            blocks_commit=False,
        )

    if latest_type == "deferred":
        if item.priority == "P1":
            return Verdict(
                item=item,
                status="rejected",
                detail=(
                    f"P1 item cannot be deferred (deferred event at line "
                    f"{latest.get('_line_no', '?')}). Close in code, "
                    f"override via ADR, or re-classify priority."
                ),
                blocks_commit=True,
            )
        # P2: verify deferrals.md has matching entry
        if verify_deferral_documented(feature_dir, item.item_id):
            return Verdict(
                item=item,
                status="deferred_complete",
                detail="Deferred with rationale in deferrals.md",
                blocks_commit=False,
            )
        return Verdict(
            item=item,
            status="deferred_incomplete",
            detail=(
                f"deferred event present at line {latest.get('_line_no', '?')} "
                f"but no rationale entry for {item.item_id} in deferrals.md"
            ),
            blocks_commit=True,
        )

    # Unknown event type at end of activity
    return Verdict(
        item=item,
        status="unaddressed",
        detail=f"Unknown closure activity ending with {latest_type!r}",
        blocks_commit=True,
    )


# ---------- Reporting ----------


def report(verdicts: list[Verdict], feature_name: str = "") -> int:
    """
    Print a human-readable report. Return exit code (0 if commit OK,
    non-zero if blocked).
    """
    blockers = [v for v in verdicts if v.blocks_commit]
    closed = [
        v
        for v in verdicts
        if not v.blocks_commit and v.status == "closed" and not v.was_deferred
    ]
    deferred = [
        v
        for v in verdicts
        if not v.blocks_commit
        and (v.status == "deferred_complete" or v.was_deferred)
    ]

    p1_count = sum(1 for v in verdicts if v.item.priority == "P1")
    p2_count = sum(1 for v in verdicts if v.item.priority == "P2")
    p3_count = sum(1 for v in verdicts if v.item.priority == "P3")

    print("=" * 70)
    label = "verify_loop_closure.py: pre-commit closure check"
    if feature_name:
        label += f" [{feature_name}]"
    print(label)
    print("=" * 70)
    print(f"Items audited: P1={p1_count}, P2={p2_count}, P3={p3_count}")
    print(f"Closed: {len(closed)} | Deferred (P2): {len(deferred)} | "
          f"Blocking: {len(blockers)}")


    if not blockers:
        print()
        print("All required closures present. Commit allowed.")
        return 0

    print()
    print(f"BLOCKED: {len(blockers)} required closure(s) missing or rejected.")
    print()

    by_status: dict[str, list[Verdict]] = defaultdict(list)
    for v in blockers:
        by_status[v.status].append(v)

    if "unaddressed" in by_status:
        print("--- Unaddressed items ---")
        for v in by_status["unaddressed"]:
            print(
                f"  [{v.item.priority}] {v.item.item_id} "
                f"(from {v.item.source_agent}): {v.detail}"
            )
        print()

    if "rejected" in by_status:
        print("--- Rejected closures (closure-rejected not superseded) ---")
        for v in by_status["rejected"]:
            print(
                f"  [{v.item.priority}] {v.item.item_id} "
                f"(from {v.item.source_agent}): {v.detail}"
            )
        print()

    if "unverified" in by_status:
        print("--- Unverified closures (closure-verified with no disk-read evidence) ---")
        for v in by_status["unverified"]:
            print(
                f"  [{v.item.priority}] {v.item.item_id} "
                f"(from {v.item.source_agent}): {v.detail}"
            )
        print()

    if "deferred_incomplete" in by_status:
        print("--- Incomplete deferrals (event present but deferrals.md entry missing) ---")
        for v in by_status["deferred_incomplete"]:
            print(
                f"  [{v.item.priority}] {v.item.item_id} "
                f"(from {v.item.source_agent}): {v.detail}"
            )
        print()

    print("To resolve:")
    print("  - For unaddressed items: address in code (write closure-claimed event),")
    print("    override via ADR (write overridden event), or for P2 only,")
    print("    defer with rationale entry in deferrals.md (write deferred event).")
    print("  - For rejected closures: fix the underlying issue and RE-VERIFY")
    print("    (write a closure-verified event; a bare closure-claimed will NOT")
    print("    clear a rejection), OR override via ADR with explicit rationale.")
    print("  - For incomplete deferrals: add the rationale entry to deferrals.md.")
    print("  - For unverified closures: the closure-verified must carry a")
    print("    closure_evidence.read {path, sha256} for an artifact that exists")
    print("    on disk. Re-run @closure-auditor so it records the read it made;")
    print("    a verification with no recorded read is rejected.")
    print()
    print("Run `@closure-auditor` to verify after addressing.")
    print("=" * 70)
    return 1


# ---------- Main ----------


def main() -> int:
    if os.environ.get("SKIP_LOOP_VERIFY") == "1":
        # Emergency escape hatch. Documented in SETUP.md troubleshooting.
        # The bypass should be rare and explained in the commit message.
        # Loud stderr output ensures the bypass is auditable in CI logs
        # and terminal scrollback.
        #
        # OBS-001 / IMP-15: the bypass is the one hard control an agent
        # invokes itself, so a self-invoked bypass with no recorded reason
        # normalizes into a silent default. A reason recorded at the moment
        # of use is the disk-truth shape applied to the escape hatch: a
        # bypass with no recorded justification is a declaration, not a
        # justification, so it is refused. This does not block legitimate
        # use (a reason can always be supplied); it makes the bypass
        # impossible to apply silently-by-default.
        reason = (os.environ.get("SKIP_LOOP_VERIFY_REASON") or "").strip()
        if not reason:
            print(
                "=" * 70,
                file=sys.stderr,
            )
            print(
                "BLOCKED: SKIP_LOOP_VERIFY=1 set without SKIP_LOOP_VERIFY_REASON.",
                file=sys.stderr,
            )
            print(
                "         The bypass requires a per-use reason recorded at the",
                file=sys.stderr,
            )
            print(
                "         moment of use, so it cannot be applied silently. Re-run",
                file=sys.stderr,
            )
            print(
                "         with a reason, for example:",
                file=sys.stderr,
            )
            print(
                "           SKIP_LOOP_VERIFY=1 \\",
                file=sys.stderr,
            )
            print(
                "           SKIP_LOOP_VERIFY_REASON='checkpoint snapshot; items intentionally open' \\",
                file=sys.stderr,
            )
            print(
                "           git commit ...",
                file=sys.stderr,
            )
            print(
                "=" * 70,
                file=sys.stderr,
            )
            return 1
        print(
            "=" * 70,
            file=sys.stderr,
        )
        print(
            "WARNING: SKIP_LOOP_VERIFY=1 set; bypassing loop closure check.",
            file=sys.stderr,
        )
        print(
            "         Reason: " + reason,
            file=sys.stderr,
        )
        print(
            "         This bypass should be rare and documented in the commit",
            file=sys.stderr,
        )
        print(
            "         message. Use `git log -1 --format=%B` to inspect.",
            file=sys.stderr,
        )
        print(
            "=" * 70,
            file=sys.stderr,
        )
        return 0

    repo_root = Path.cwd()
    feature_dirs = staged_feature_dirs(repo_root)
    if not feature_dirs:
        # No feature directory found. Either no spec-driven work in
        # this commit, or framework not in use. Don't block.
        return 0

    overall = 0
    for feature_dir in feature_dirs:
        overall = check_feature(feature_dir, repo_root) or overall
    return overall


def check_feature(feature_dir: Path, repo_root: Path) -> int:
    """Run the closure audit for one feature directory; return its exit code."""
    events_path = feature_dir / "events.jsonl"
    events = read_events(events_path)

    if not events:
        # No events. Either feature just started or framework hasn't
        # been used for this feature yet. Don't block.
        print(
            f"verify_loop_closure.py: no events.jsonl in {feature_dir}; "
            f"skipping closure check.",
            file=sys.stderr,
        )
        return 0

    items = extract_items(events)
    if not items:
        # Events exist but no pending-resolution items raised
        return 0

    activity = index_closure_activity(events)

    verdicts: list[Verdict] = []
    for item in items:
        item_activity = activity.get(item.item_id, ClosureActivity())
        verdicts.append(
            determine_verdict(item, item_activity, feature_dir, repo_root)
        )

    return report(verdicts, feature_dir.name)


if __name__ == "__main__":
    sys.exit(main())
