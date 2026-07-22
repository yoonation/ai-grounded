#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for verify_loop_closure.py, the disk-truth read-evidence gate
(Capability 3) plus the F19 deferral-tally fix.

Stdlib unittest only. The directory has a dot, so run the file directly:
    python3 .claude/hooks/test_verify_loop_closure.py

Proof obligations (the forced-failure contract for the capability):
  NEG-1   prose-only closure-verified (no read block)        -> BLOCKS
  NEG-2   read.path points at a file that does not exist      -> BLOCKS
  NEG-3   read.sha256 is not a 64-hex digest                  -> BLOCKS
  NEG-4   read.path resolves but the file is empty            -> BLOCKS
  POS-1   read.path exists, non-empty, valid sha              -> CLOSES
  POS-2a  closure-claimed with no read (cross-tool)           -> CLOSES (unchanged)
  POS-2b  overridden with no read (ADR acceptance)            -> CLOSES (unchanged)
  POS-2c  P2 deferred + deferrals.md entry                    -> deferred_complete
  POS-2d  P3 informational                                    -> not blocking
  DRIFT-1 read.path exists but disk sha != recorded sha       -> CLOSES + warns
  TEETH   bypass verify_read_evidence -> NEG-1 closes          -> proves the read
          check is the load-bearing branch (the gate's own falsifier)
  F19     deferred item later closure-verified                -> tallied Deferred
  E2E     run the real module as a subprocess in a real git
          repo: NEG-1 blocks (exit 1), POS-1 allows (exit 0)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify_loop_closure as mod  # noqa: E402


# ---------- helpers ----------


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def completed_event(item_id, priority="P1", agent="threat-modeler",
                    inv="01INVRAISE", ts="2026-01-01T00:00:00Z"):
    """A `completed` event raising one pending-resolution item."""
    return {
        "ts": ts,
        "event": "completed",
        "agent": agent,
        "invocation_id": inv,
        "items_raised": [{"id": item_id, "priority": priority}],
    }


def closure_event(event, item_id, ts, read=None, type_="code",
                  agent="closure-auditor", inv="01INVCLOSE"):
    ce = {"item_id": item_id, "source_agent": "threat-modeler", "type": type_,
          "location": "src/x.ts:1-2", "summary": "x"}
    if read is not None:
        ce["read"] = read
    return {
        "ts": ts,
        "event": event,
        "agent": agent,
        "invocation_id": inv,
        "closure_evidence": ce,
    }


def deferred_event(item_id, ts, inv="01INVDEFER"):
    return {"ts": ts, "event": "deferred", "agent": "main",
            "invocation_id": inv, "item_id": item_id}


def run_pipeline(events, feature_dir, repo_root):
    """
    Exercise the REAL gate pipeline (extract_items + index_closure_activity +
    determine_verdict) rather than re-implementing verdict logic in the test.
    Returns {item_id: Verdict}.
    """
    # mirror read_events() line numbering so detail strings format
    for i, e in enumerate(events, 1):
        e["_line_no"] = i
    items = mod.extract_items(events)
    activity = mod.index_closure_activity(events)
    verdicts = {}
    for item in items:
        act = activity.get(item.item_id, mod.ClosureActivity())
        verdicts[item.item_id] = mod.determine_verdict(
            item, act, feature_dir, repo_root
        )
    return verdicts


class DiskTruthGate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.feature = self.repo / "specs" / "004-x"
        self.feature.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _real_artifact(self, rel="src/x.ts", body=b"export const x = 1;\n"):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body)
        return rel, _sha256(body)

    # ---- NEG cases: a close without a real read must FAIL ----

    def test_neg1_prose_only_blocks(self):
        events = [
            completed_event("CR-1"),
            closure_event("closure-verified", "CR-1", "2026-01-02T00:00:00Z"),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-1"]
        self.assertTrue(v.blocks_commit)
        self.assertEqual(v.status, "unverified")
        self.assertIn("no recorded artifact read", v.detail.lower()
                      .replace("recorded read", "recorded artifact read")
                      if "recorded read" in v.detail else v.detail.lower())

    def test_neg2_phantom_path_blocks(self):
        events = [
            completed_event("CR-2"),
            closure_event("closure-verified", "CR-2", "2026-01-02T00:00:00Z",
                          read={"path": "src/does-not-exist.ts",
                                "sha256": "a" * 64}),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-2"]
        self.assertTrue(v.blocks_commit)
        self.assertEqual(v.status, "unverified")
        self.assertIn("does not resolve", v.detail)

    def test_neg3_malformed_sha_blocks(self):
        rel, _ = self._real_artifact()
        events = [
            completed_event("CR-3"),
            closure_event("closure-verified", "CR-3", "2026-01-02T00:00:00Z",
                          read={"path": rel, "sha256": "not-a-real-digest"}),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-3"]
        self.assertTrue(v.blocks_commit)
        self.assertEqual(v.status, "unverified")
        self.assertIn("64-hex", v.detail)

    def test_neg4_empty_file_blocks(self):
        rel, sha = self._real_artifact(rel="src/empty.ts", body=b"")
        events = [
            completed_event("CR-4"),
            closure_event("closure-verified", "CR-4", "2026-01-02T00:00:00Z",
                          read={"path": rel, "sha256": sha}),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-4"]
        self.assertTrue(v.blocks_commit)
        self.assertEqual(v.status, "unverified")
        self.assertIn("empty file", v.detail)

    # ---- POS cases: a real read passes; other paths unchanged ----

    def test_pos1_valid_read_closes(self):
        rel, sha = self._real_artifact()
        events = [
            completed_event("CR-5"),
            closure_event("closure-verified", "CR-5", "2026-01-02T00:00:00Z",
                          read={"path": rel, "sha256": sha}),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-5"]
        self.assertFalse(v.blocks_commit)
        self.assertEqual(v.status, "closed")

    def test_pos2a_closure_claimed_unchanged(self):
        # cross-tool self-attestation is NOT gated on a read (Fork 1 scope)
        events = [
            completed_event("CR-6"),
            closure_event("closure-claimed", "CR-6", "2026-01-02T00:00:00Z"),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-6"]
        self.assertFalse(v.blocks_commit)
        self.assertEqual(v.status, "closed")

    def test_pos2b_overridden_unchanged(self):
        events = [
            completed_event("CR-7"),
            closure_event("overridden", "CR-7", "2026-01-02T00:00:00Z"),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-7"]
        self.assertFalse(v.blocks_commit)
        self.assertEqual(v.status, "closed")

    def test_pos2c_p2_deferred_with_doc(self):
        (self.feature / "deferrals.md").write_text("## CR-8\nDeferred to 005.\n")
        events = [
            completed_event("CR-8", priority="P2"),
            deferred_event("CR-8", "2026-01-02T00:00:00Z"),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-8"]
        self.assertFalse(v.blocks_commit)
        self.assertEqual(v.status, "deferred_complete")

    def test_pos2d_p3_not_blocking(self):
        events = [completed_event("CR-9", priority="P3")]
        v = run_pipeline(events, self.feature, self.repo)["CR-9"]
        self.assertFalse(v.blocks_commit)

    # ---- DRIFT: verified an older version -> pass, but warn ----

    def test_fab1_recorded_disk_mismatch_blocks(self):
        # ADR-002: a recorded digest that does not match disk fails closed,
        # whether it was fabricated (never computed by a tool) or staled by a
        # post-audit edit. This is the feature 007 fabrication episode.
        rel, sha = self._real_artifact()
        (self.repo / rel).write_bytes(b"edited after the audit\n")
        events = [
            completed_event("CR-F1"),
            closure_event("closure-verified", "CR-F1", "2026-01-02T00:00:00Z",
                          read={"path": rel, "sha256": sha}),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-F1"]
        self.assertTrue(v.blocks_commit)
        self.assertIn("does not match disk", v.detail)
        self.assertIn("shasum -a 256", v.detail)

    def test_fab2_superseding_fresh_digest_closes(self):
        # The honest remediation: a LATER closure-verified carrying a freshly
        # computed digest supersedes the stale one and closes the item.
        rel, stale_sha = self._real_artifact()
        (self.repo / rel).write_bytes(b"edited after the audit\n")
        fresh_sha = _sha256(b"edited after the audit\n")
        events = [
            completed_event("CR-F2"),
            closure_event("closure-verified", "CR-F2", "2026-01-02T00:00:00Z",
                          read={"path": rel, "sha256": stale_sha}),
            closure_event("closure-verified", "CR-F2", "2026-01-03T00:00:00Z",
                          read={"path": rel, "sha256": fresh_sha},
                          inv="01INVFRESH"),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-F2"]
        self.assertFalse(v.blocks_commit)
        self.assertEqual(v.status, "closed")

    def test_teeth_bypass_makes_neg1_close(self):
        """
        The gate's own falsifier. If verify_read_evidence is neutralized,
        NEG-1 (prose-only) closes again. That proves the read check is
        exactly what flips NEG-1 from closed to blocked, not something
        incidental. This is Capability 1 discipline applied by hand to
        the build of Capability 3.
        """
        events = [
            completed_event("CR-11"),
            closure_event("closure-verified", "CR-11", "2026-01-02T00:00:00Z"),
        ]
        original = mod.verify_read_evidence
        try:
            mod.verify_read_evidence = lambda ev, root: mod.ReadCheck(True, "bypassed")
            v = run_pipeline(events, self.feature, self.repo)["CR-11"]
            self.assertFalse(v.blocks_commit)   # with the check gone, it closes
            self.assertEqual(v.status, "closed")
        finally:
            mod.verify_read_evidence = original
        # and with the check restored, the SAME fixture blocks
        v2 = run_pipeline(events, self.feature, self.repo)["CR-11"]
        self.assertTrue(v2.blocks_commit)
        self.assertEqual(v2.status, "unverified")

    # ---- F19: a verified deferral is tallied Deferred, not Closed ----

    def test_f19_verified_deferral_tally(self):
        (self.feature / "deferrals.md").write_text("## CR-12\nDeferred, residual recorded.\n")
        rel, sha = self._real_artifact(rel="specs/004-x/deferrals.md",
                                       body=(self.feature / "deferrals.md").read_bytes())
        events = [
            completed_event("CR-12", priority="P2"),
            closure_event("closure-rejected", "CR-12", "2026-01-02T00:00:00Z",
                          inv="01REJ"),
            deferred_event("CR-12", "2026-01-02T01:00:00Z"),
            # auditor verifies the deferral by reading deferrals.md, clearing
            # the rejection -> latest event is a closure-verified
            closure_event("closure-verified", "CR-12", "2026-01-02T02:00:00Z",
                          read={"path": rel, "sha256": sha}, inv="01VER"),
        ]
        v = run_pipeline(events, self.feature, self.repo)["CR-12"]
        self.assertFalse(v.blocks_commit)
        self.assertTrue(v.was_deferred)         # F19: re-binned as Deferred
        # confirm report() counts it under Deferred, not Closed
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            mod.report([v])
        out = buf.getvalue()
        self.assertIn("Deferred (P2): 1", out)
        self.assertIn("Closed: 0", out)


@unittest.skipUnless(shutil.which("git"), "git required for the end-to-end test")
class EndToEnd(unittest.TestCase):
    """
    Exercise the REAL artifact: run verify_loop_closure.py as a subprocess in
    a real git repo with a real staged events.jsonl, so find_feature_dir,
    read_events, the verdict walk, and report() all run on the real path.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.feature = self.repo / "specs" / "004-x"
        self.feature.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.repo, check=True)
        self.gate = Path(mod.__file__)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_events(self, events):
        path = self.feature / "events.jsonl"
        path.write_text("\n".join(json.dumps(e) for e in events) + "\n")
        return path

    def _stage(self, *rels):
        subprocess.run(["git", "add", *rels], cwd=self.repo, check=True)

    def _run_gate(self):
        return subprocess.run(
            [sys.executable, str(self.gate)],
            cwd=self.repo, capture_output=True, text=True,
        )

    def test_e2e_prose_only_blocks(self):
        self._write_events([
            completed_event("CR-1"),
            closure_event("closure-verified", "CR-1", "2026-01-02T00:00:00Z"),
        ])
        self._stage("specs/004-x/events.jsonl")
        r = self._run_gate()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("Unverified closures", r.stdout)

    def test_e2e_valid_read_allows(self):
        body = b"export const x = 1;\n"
        (self.repo / "src").mkdir()
        (self.repo / "src" / "x.ts").write_bytes(body)
        self._write_events([
            completed_event("CR-1"),
            closure_event("closure-verified", "CR-1", "2026-01-02T00:00:00Z",
                          read={"path": "src/x.ts", "sha256": _sha256(body)}),
        ])
        self._stage("specs/004-x/events.jsonl", "src/x.ts")
        r = self._run_gate()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Commit allowed", r.stdout)


class Bypass(unittest.TestCase):
    """OBS-001 / IMP-15: the SKIP_LOOP_VERIFY escape hatch requires a per-use reason,
    so it cannot be applied silently-by-default. Exercises the real artifact as a
    subprocess with a controlled environment."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.gate = Path(mod.__file__)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, overrides):
        env = dict(os.environ)
        for k, v in overrides.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
        return subprocess.run(
            [sys.executable, str(self.gate)],
            cwd=self.tmp, capture_output=True, text=True, env=env,
        )

    def test_bypass_without_reason_unset_blocks(self):
        r = self._run({"SKIP_LOOP_VERIFY": "1", "SKIP_LOOP_VERIFY_REASON": None})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("BLOCKED", r.stderr)

    def test_bypass_with_blank_reason_blocks(self):
        r = self._run({"SKIP_LOOP_VERIFY": "1", "SKIP_LOOP_VERIFY_REASON": "   "})
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("BLOCKED", r.stderr)

    def test_bypass_with_reason_passes_and_echoes_it(self):
        r = self._run({"SKIP_LOOP_VERIFY": "1",
                       "SKIP_LOOP_VERIFY_REASON": "checkpoint snapshot; items open"})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Reason: checkpoint snapshot; items open", r.stderr)
        self.assertIn("bypassing loop closure check", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
