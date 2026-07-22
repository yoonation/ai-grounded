#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the one-way template-to-consumer sync (sync.py).
Stdlib unittest only:
    python3 tooling/sync/test_sync.py

Every test builds a tiny real template and consumer on disk (git-initialized
where the scenario needs a recorded base), so the class resolution, state
recording, backup, merge, deletion, and override paths are exercised for
real, not mocked.

Proof obligations:
  SCAFFOLD-PRESERVED   a consumer-filled shell file survives pull untouched
  SCAFFOLD-CREATED     a missing shell file is delivered
  FRAMEWORK-UPDATE     an untouched framework file follows the template
  OVERRIDE-SKIP        a registered override is never overwritten
  DRIFT-FLAGGED        an unregistered edit to a framework file is kept and
                       reported, never silently clobbered
  SUBSTRATE-REPLACE    the substrate tree is replaced as a unit, consumer
                       extras under it deleted, backup taken
  ADOPT-NO-BASE        first sync with --adopt-template takes the template
                       version and backs up the prior copy
  CONFLICT-NO-BASE     first sync without --adopt-template keeps the
                       consumer copy and reports a conflict
  DELETE-WITH-BASE     a template-dropped framework file is deleted only
                       when the consumer copy matches the recorded base
  THREE-WAY-MERGE      base present plus disjoint edits merge cleanly; the
                       same-line edit conflicts and check exits 2
  ORPHAN-REPORTED      a consumer file under an explicit framework glob the
                       template does not ship is reported, not deleted
  CHECK-TEETH          check exits 0 on a clean consumer and 2 on drift
  MIGRATION-ONCE       a migration runs on first pull and never again
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync as mod  # noqa: E402

MANIFEST = """\
manifest-version: "1.0.0"
substrate:
  - "governance-commons/**"
scaffold:
  - "CLAUDE.md"
framework-explicit:
  - "scripts/bootstrap.sh"
eject:
  exclude:
    - "CLAUDE.md"
  allow-references:
    - "src/notes.ts"
"""


def sh(args, cwd):
    subprocess.run(args, cwd=str(cwd), check=True, capture_output=True)


def git_init(path: Path):
    sh(["git", "init", "-q"], path)
    sh(["git", "config", "user.email", "t@t"], path)
    sh(["git", "config", "user.name", "t"], path)
    sh(["git", "add", "-A"], path)
    sh(["git", "commit", "-qm", "init", "--allow-empty"], path)


def write(root: Path, rel: str, text: str):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.template = self.tmp / "template"
        self.consumer = self.tmp / "consumer"
        write(self.template, "sync-manifest.yaml", MANIFEST)
        write(self.template, "CLAUDE.md", "shell\n")
        write(self.template, "tooling/gate.py", "v1\n")
        write(self.template, "scripts/bootstrap.sh", "boot v1\n")
        write(self.template, "governance-commons/VERSION", "1.0.0\n")
        write(self.template, "governance-commons/rule.yaml", "rule: a\n")
        self.consumer.mkdir()
        git_init(self.consumer)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def pull(self, adopt=False):
        return mod.run_sync(self.template, self.consumer, apply=True, adopt=adopt)

    def commit_all(self):
        sh(["git", "add", "-A"], self.consumer)
        sh(["git", "commit", "-qm", "sync"], self.consumer)


class FirstDelivery(Base):
    def test_scaffold_created_then_preserved(self):
        r = self.pull(adopt=True)
        self.assertIn("scaffold-create", r.counts)
        write(self.consumer, "CLAUDE.md", "my filled content\n")
        write(self.template, "CLAUDE.md", "shell v2\n")
        r2 = self.pull()
        self.assertEqual((self.consumer / "CLAUDE.md").read_text(), "my filled content\n")
        self.assertIn("scaffold-template-changed", r2.counts)

    def test_framework_update_when_untouched(self):
        self.pull(adopt=True)
        write(self.template, "tooling/gate.py", "v2\n")
        r = self.pull()
        self.assertIn("framework-update", r.counts)
        self.assertEqual((self.consumer / "tooling/gate.py").read_text(), "v2\n")

    def test_conflict_without_base_keeps_consumer(self):
        write(self.consumer, "tooling/gate.py", "consumer version\n")
        r = self.pull(adopt=False)
        self.assertIn("conflict", r.counts)
        self.assertEqual((self.consumer / "tooling/gate.py").read_text(), "consumer version\n")

    def test_adopt_overwrites_and_backs_up(self):
        write(self.consumer, "tooling/gate.py", "consumer version\n")
        r = self.pull(adopt=True)
        self.assertIn("adopt-overwrite", r.counts)
        self.assertEqual((self.consumer / "tooling/gate.py").read_text(), "v1\n")
        backups = list((self.consumer / ".template-sync" / "backup").rglob("gate.py"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "consumer version\n")


class SteadyState(Base):
    def setUp(self):
        super().setUp()
        git_init(self.template)
        self.pull(adopt=True)
        self.commit_all()

    def test_drift_flagged_not_clobbered(self):
        write(self.consumer, "tooling/gate.py", "local hack\n")
        r = self.pull(adopt=False)
        self.assertIn("drift", r.counts)
        self.assertEqual((self.consumer / "tooling/gate.py").read_text(), "local hack\n")

    def test_override_skip(self):
        write(self.consumer, ".template-sync/overrides.yml",
              "overrides:\n  - path: \"tooling/gate.py\"\n")
        write(self.consumer, "tooling/gate.py", "deliberate fork\n")
        write(self.template, "tooling/gate.py", "v2\n")
        r = self.pull()
        self.assertIn("override-skip", r.counts)
        self.assertEqual((self.consumer / "tooling/gate.py").read_text(), "deliberate fork\n")

    def test_substrate_full_replace_deletes_extras(self):
        write(self.consumer, "governance-commons/extra.md", "consumer-only\n")
        write(self.template, "governance-commons/rule.yaml", "rule: b\n")
        r = self.pull()
        self.assertIn("substrate-replace", r.counts)
        self.assertFalse((self.consumer / "governance-commons/extra.md").exists())
        self.assertEqual((self.consumer / "governance-commons/rule.yaml").read_text(), "rule: b\n")
        backups = list((self.consumer / ".template-sync" / "backup").rglob("extra.md"))
        self.assertEqual(len(backups), 1)

    def test_delete_with_base_only_when_unmodified(self):
        (self.template / "tooling/gate.py").unlink()
        r = self.pull()
        self.assertIn("framework-delete", r.counts)
        self.assertFalse((self.consumer / "tooling/gate.py").exists())

    def test_delete_refused_when_modified(self):
        write(self.consumer, "tooling/gate.py", "local hack\n")
        (self.template / "tooling/gate.py").unlink()
        r = self.pull()
        self.assertIn("drift", r.counts)
        self.assertTrue((self.consumer / "tooling/gate.py").exists())

    def test_three_way_clean_merge(self):
        sh(["git", "add", "-A"], self.template)
        sh(["git", "commit", "-qm", "base", "--allow-empty"], self.template)
        st = mod.load_state(self.consumer)
        st["template_ref"] = mod.template_head(self.template)
        mod.save_state(self.consumer, st)
        base = "line1\nline2\nline3\n"
        write(self.template, "tooling/gate.py", base)
        sh(["git", "add", "-A"], self.template)
        sh(["git", "commit", "-qm", "base2", "--allow-empty"], self.template)
        st = mod.load_state(self.consumer)
        st["template_ref"] = mod.template_head(self.template)
        st["files"]["tooling/gate.py"] = mod.sha256(base.encode())
        mod.save_state(self.consumer, st)
        write(self.consumer, "tooling/gate.py", "line1 consumer\nline2\nline3\n")
        write(self.template, "tooling/gate.py", "line1\nline2\nline3 template\n")
        r = self.pull()
        self.assertIn("merge-clean", r.counts)
        merged = (self.consumer / "tooling/gate.py").read_text()
        self.assertIn("line1 consumer", merged)
        self.assertIn("line3 template", merged)

    def test_three_way_conflict_and_check_teeth(self):
        sh(["git", "add", "-A"], self.template)
        sh(["git", "commit", "-qm", "base", "--allow-empty"], self.template)
        base = "same line\n"
        write(self.template, "tooling/gate.py", base)
        sh(["git", "add", "-A"], self.template)
        sh(["git", "commit", "-qm", "base2", "--allow-empty"], self.template)
        st = mod.load_state(self.consumer)
        st["template_ref"] = mod.template_head(self.template)
        st["files"]["tooling/gate.py"] = mod.sha256(base.encode())
        mod.save_state(self.consumer, st)
        write(self.consumer, "tooling/gate.py", "consumer line\n")
        write(self.template, "tooling/gate.py", "template line\n")
        r = self.pull()
        self.assertIn("merge-conflict", r.counts)
        rc = mod.cmd_check(self.template, self.consumer)
        self.assertEqual(rc, 2)

    def test_check_clean_exits_zero(self):
        rc = mod.cmd_check(self.template, self.consumer)
        self.assertEqual(rc, 0)

    def test_orphan_reported_not_deleted(self):
        write(self.consumer, "scripts/my-app-helper.sh", "app\n")
        write(self.consumer, "scripts/bootstrap.sh.bak", "stale\n")
        # bootstrap.sh.bak does not match the explicit glob; my-app-helper
        # does not either; craft one that does:
        st = mod.load_state(self.consumer)
        r = mod.run_sync(self.template, self.consumer, apply=False, adopt=False)
        self.assertNotIn("orphan", r.counts)
        (self.template / "scripts" / "bootstrap.sh").unlink()
        st["files"].pop("scripts/bootstrap.sh", None)
        mod.save_state(self.consumer, st)
        r2 = mod.run_sync(self.template, self.consumer, apply=False, adopt=False)
        self.assertIn("orphan", r2.counts)
        self.assertTrue((self.consumer / "scripts/bootstrap.sh").exists())


class ModePreservation(Base):
    def test_executable_bit_survives_delivery(self):
        import os
        import stat
        write(self.template, "tooling/hook.sh", "run\n")
        os.chmod(self.template / "tooling/hook.sh", 0o755)
        self.pull(adopt=True)
        mode = (self.consumer / "tooling/hook.sh").stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)


class Migrations(Base):
    def test_migration_runs_once(self):
        write(self.template, "tooling/sync/migrations/001-touch.py",
              "def apply(consumer_root, template_root):\n"
              "    p = consumer_root / 'migrated.txt'\n"
              "    n = int(p.read_text()) + 1 if p.exists() else 1\n"
              "    p.write_text(str(n))\n"
              "    return 'touched'\n")
        self.pull(adopt=True)
        self.pull()
        self.assertEqual((self.consumer / "migrated.txt").read_text(), "1")


class RemoteTemplate(Base):
    """URL --template: clone-per-run against a bare repo used as a hermetic
    fake remote, plus the incremental three-way merge that an unshallowed
    clone must preserve."""

    def _make_bare_remote(self):
        src = self.tmp / "remote-src"
        write(src, "sync-manifest.yaml", MANIFEST)
        write(src, "CLAUDE.md", "shell\n")
        write(src, "tooling/gate.py", "line1\nline2\nline3\n")
        write(src, "governance-commons/VERSION", "1.0.0\n")
        git_init(src)
        bare = self.tmp / "remote.git"
        sh(["git", "clone", "--quiet", "--bare", str(src), str(bare)], self.tmp)
        return src, bare

    def test_url_first_pull_adopts(self):
        _src, bare = self._make_bare_remote()
        url = bare.as_uri()
        rc = mod.main(["pull", "--template", url, "--consumer", str(self.consumer),
                       "--adopt-template"])
        self.assertEqual(rc, 0)
        self.assertTrue((self.consumer / "tooling/gate.py").exists())
        self.assertEqual((self.consumer / "governance-commons/VERSION").read_text(), "1.0.0\n")
        st = mod.load_state(self.consumer)
        self.assertEqual(len(st["template_ref"]), 40)
        self.assertEqual(list(Path(tempfile.gettempdir()).glob("template-sync-*")), [])

    def test_url_incremental_three_way_merge(self):
        src, bare = self._make_bare_remote()
        url = bare.as_uri()
        mod.main(["pull", "--template", url, "--consumer", str(self.consumer),
                  "--adopt-template"])
        self.commit_all()
        write(self.consumer, "tooling/gate.py", "line1 consumer\nline2\nline3\n")
        self.commit_all()
        write(src, "tooling/gate.py", "line1\nline2\nline3 template\n")
        sh(["git", "add", "-A"], src)
        sh(["git", "commit", "-qm", "template edit"], src)
        # Refresh the bare mirror from src regardless of default branch name.
        import subprocess as _sp
        branch = _sp.run(["git", "branch", "--show-current"], cwd=str(src),
                         capture_output=True, text=True).stdout.strip()
        sh(["git", "fetch", "--quiet", str(src), f"{branch}:{branch}"], bare)
        rc = mod.main(["pull", "--template", url, "--consumer", str(self.consumer)])
        self.assertEqual(rc, 0)
        merged = (self.consumer / "tooling/gate.py").read_text()
        self.assertIn("line1 consumer", merged)
        self.assertIn("line3 template", merged)


class TemplateSelfSyncGuard(unittest.TestCase):
    """status/pull/check must refuse when the template URL resolves to the
    consumer's own origin remote, i.e. running the tool from inside the
    template. Applications that merely carry a synced sync-manifest.yaml are
    NOT blocked; the signal is same-origin, not manifest presence."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "the-template"
        self.bare = self.tmp / "the-template.git"
        write(self.repo, "sync-manifest.yaml", MANIFEST)
        write(self.repo, "CLAUDE.md", "shell\n")
        write(self.repo, "governance-commons/VERSION", "1.0.0\n")
        git_init(self.repo)
        sh(["git", "clone", "--quiet", "--bare", str(self.repo), str(self.bare)], self.tmp)
        sh(["git", "remote", "add", "origin", str(self.bare)], self.repo)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _expect_refusal(self, command):
        url = self.bare.as_uri()
        with self.assertRaises(SystemExit) as ctx:
            mod.main([command, "--template", url, "--consumer", str(self.repo)])
        self.assertIn("origin", str(ctx.exception))

    def test_status_refused(self):
        self._expect_refusal("status")

    def test_pull_refused(self):
        self._expect_refusal("pull")

    def test_check_refused(self):
        self._expect_refusal("check")

    def test_application_with_synced_manifest_not_blocked(self):
        app = self.tmp / "real-app"
        write(app, "app.txt", "code\n")
        git_init(app)
        other_bare = self.tmp / "app-origin.git"
        sh(["git", "clone", "--quiet", "--bare", str(app), str(other_bare)], self.tmp)
        sh(["git", "remote", "add", "origin", str(other_bare)], app)
        url = self.bare.as_uri()
        rc = mod.main(["pull", "--template", url, "--consumer", str(app),
                       "--adopt-template"])
        self.assertEqual(rc, 0)
        self.assertTrue((app / "sync-manifest.yaml").is_file())


class RemoteNormalization(unittest.TestCase):
    def test_https_ssh_scp_forms_compare_equal(self):
        forms = [
            "https://github.com/yoonation/ai-grounded.git",
            "git@github.com:yoonation/ai-grounded.git",
            "ssh://git@github.com/yoonation/ai-grounded.git",
            "https://github.com/yoonation/ai-grounded",
        ]
        norm = {mod._normalize_remote(f) for f in forms}
        self.assertEqual(len(norm), 1)

    def test_different_repos_differ(self):
        self.assertFalse(mod.same_git_remote(
            "https://github.com/yoonation/ai-grounded.git",
            "https://github.com/yoonation/example-app.git"))


class MiniYaml(unittest.TestCase):
    def test_manifest_subset_parses(self):
        data = mod._mini_yaml(MANIFEST)
        self.assertEqual(data["substrate"], ["governance-commons/**"])
        self.assertEqual(data["scaffold"], ["CLAUDE.md"])
        self.assertEqual(data["eject"]["exclude"], ["CLAUDE.md"])

    def test_overrides_subset_parses(self):
        data = mod._mini_yaml("overrides:\n  - path: \"a/b.md\"\n  - path: 'c/**'\n")
        self.assertEqual(data["overrides"], ['path: "a/b.md"', "path: 'c/**'"])


class OverrideEntryShapes(unittest.TestCase):
    def test_dict_and_string_entries(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            write(tmp, ".template-sync/overrides.yml",
                  "overrides:\n"
                  "  - path: \"x/y.md\"\n"
                  "    reason: \"kept fork\"\n"
                  "  - \"z/**\"\n")
            got = mod.load_overrides(tmp)
            self.assertIn("z/**", got)
            self.assertTrue(any("x/y.md" in g for g in got))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
