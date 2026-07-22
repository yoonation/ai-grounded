#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
Unit tests for the capability-index generator (generate.py).

Stdlib unittest only. Run:
    python3 -m unittest tooling.capability-index.test_generate
or from the directory:
    python3 -m unittest test_generate
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate  # noqa: E402


class PythonExports(unittest.TestCase):
    def test_top_level_defs_and_classes(self):
        src = "def alpha():\n    pass\n\nclass Beta:\n    pass\n\ndef _hidden():\n    pass\n"
        symbols, method = generate.extract_python_exports(src)
        self.assertEqual(symbols, ["Beta", "alpha"])
        self.assertEqual(method, "ast")

    def test_dunder_all_is_authoritative(self):
        src = "__all__ = ['only_this']\n\ndef only_this():\n    pass\n\ndef also_public():\n    pass\n"
        symbols, method = generate.extract_python_exports(src)
        self.assertEqual(symbols, ["only_this"])
        self.assertEqual(method, "ast-dunder-all")

    def test_syntax_error(self):
        symbols, method = generate.extract_python_exports("def broken(:\n")
        self.assertEqual(symbols, [])
        self.assertEqual(method, "ast-parse-error")


class JsTsExports(unittest.TestCase):
    def test_named_and_brace_exports(self):
        src = (
            "export function rank(x) {}\n"
            "export const THRESHOLD = 2;\n"
            "export class Store {}\n"
            "function helper() {}\n"
            "export { helper as exposed };\n"
            "exports.legacyName = 1;\n"
        )
        symbols, method = generate.extract_js_ts_exports(src)
        self.assertEqual(method, "regex-heuristic")
        for name in ["rank", "THRESHOLD", "Store", "exposed", "legacyName"]:
            self.assertIn(name, symbols)
        self.assertNotIn("helper", symbols)


class Dependencies(unittest.TestCase):
    def test_package_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "package.json"
            p.write_text(json.dumps({
                "dependencies": {"zod": "3.0.0"},
                "devDependencies": {"typescript": "5.0.0"},
            }), encoding="utf-8")
            self.assertEqual(generate.deps_from_package_json(p), ["typescript", "zod"])

    def test_requirements(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "requirements.txt"
            p.write_text("# comment\nrequests==2.31.0\nflask>=3.0\n-e .\n", encoding="utf-8")
            self.assertEqual(generate.deps_from_requirements(p), ["flask", "requests"])

    def test_pyproject_if_tomllib(self):
        if generate.tomllib is None:
            self.skipTest("tomllib unavailable (Python < 3.11)")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "pyproject.toml"
            p.write_text('[project]\ndependencies = ["httpx>=0.27", "pydantic"]\n', encoding="utf-8")
            self.assertEqual(generate.deps_from_pyproject(p), ["httpx", "pydantic"])


class BuildIndex(unittest.TestCase):
    def _make_tree(self, base: Path):
        (base / "src").mkdir(parents=True)
        (base / "src" / "util.py").write_text("def helper():\n    pass\nclass Thing:\n    pass\n", encoding="utf-8")
        (base / "src" / "api.ts").write_text("export function go() {}\nexport const N = 1;\n", encoding="utf-8")
        (base / "package.json").write_text(json.dumps({"dependencies": {"zod": "3.0.0"}}), encoding="utf-8")
        # noise that must be skipped
        (base / "node_modules").mkdir()
        (base / "node_modules" / "junk.js").write_text("export function shouldNotAppear() {}\n", encoding="utf-8")

    def test_index_contents(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            self._make_tree(base)
            idx = generate.build_index(base)
        self.assertIn("npm", idx["dependencies"])
        self.assertIn("zod", idx["dependencies"]["npm"])
        py = idx["exports"]["src/util.py"]
        self.assertEqual(py["language"], "python")
        self.assertEqual(py["symbols"], ["Thing", "helper"])
        ts = idx["exports"]["src/api.ts"]
        self.assertEqual(ts["method"], "regex-heuristic")
        self.assertIn("go", ts["symbols"])

    def test_skip_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            self._make_tree(base)
            idx = generate.build_index(base)
        for relpath in idx["exports"]:
            self.assertNotIn("node_modules", relpath)
        all_symbols = [s for v in idx["exports"].values() for s in v["symbols"]]
        self.assertNotIn("shouldNotAppear", all_symbols)


class ShippedFixture(unittest.TestCase):
    def test_sample_project(self):
        root = Path(os.path.dirname(os.path.abspath(__file__))) / "fixtures" / "sample-project"
        if not root.exists():
            self.skipTest("shipped fixture not present")
        idx = generate.build_index(root)
        self.assertIn("zod", idx["dependencies"].get("npm", []))
        self.assertIn("typescript", idx["dependencies"].get("npm", []))
        py = idx["exports"].get("src/scorer.py")
        self.assertIsNotNone(py)
        self.assertEqual(py["symbols"], ["Calibration", "score_candidate"])
        self.assertNotIn("_private_helper", py["symbols"])
        ts = idx["exports"].get("src/api.ts")
        self.assertIsNotNone(ts)
        for name in ["rankCandidates", "DEFAULT_THRESHOLD", "CandidateStore", "exposedHelper"]:
            self.assertIn(name, ts["symbols"])


if __name__ == "__main__":
    unittest.main()
