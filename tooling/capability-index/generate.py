#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
generate.py - the capability-index generator.

Builds a machine map of what already exists in a codebase: the declared
dependencies and the exported symbols, by file. The discovery agent and the
duplication gate read this to refute a faked "I checked, nothing exists" with an
independent artifact. The third Phase B module of the SPS rewire, built standalone
and unit-tested before any wiring.

It is a tool, not a hook; you run it on demand and read or store its index. It
never blocks.

Honesty about method, recorded per entry:
- Python exports are extracted with the stdlib ast module (precise: top-level
  defs and classes, honoring __all__ when present).
- JavaScript and TypeScript exports are extracted with a regex heuristic, a
  surface scan, not a compiler. It surfaces named exports well enough to refute a
  faked reuse claim; it is not a guarantee of completeness, and each such entry is
  labeled method "regex-heuristic" so the reader knows.
- Dependencies come from the dependency files found in the tree: package.json
  (stdlib json), requirements.txt and go.mod (line parse), and pyproject.toml,
  Cargo.toml, and .mise.toml (tomllib, Python 3.11+). When tomllib is unavailable
  the toml files are skipped and noted, so the tool still runs on 3.9 and 3.10.

Dependencies: Python stdlib only. tomllib (3.11+) is used if present and skipped
gracefully if not.

Usage:
    python3 tooling/capability-index/generate.py <root> [--out index.json]
    python3 tooling/capability-index/generate.py . --out .capability-index.json

Exit code is always 0.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None  # type: ignore

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "target", "vendor",
    "governance-commons",
}

EXPORT_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}


# ---------- Python exports (precise, via ast) ----------


def extract_python_exports(text: str):
    """Top-level functions and classes; honor __all__ when present.

    Returns a sorted list of exported symbol names. If __all__ is defined as a
    literal list or tuple of strings, that is authoritative. Otherwise, top-level
    public defs and classes (names not starting with underscore).
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [], "ast-parse-error"
    dunder_all = None
    names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        literal = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                literal.append(elt.value)
                        dunder_all = literal
    if dunder_all is not None:
        return sorted(set(dunder_all)), "ast-dunder-all"
    return sorted(set(names)), "ast"


# ---------- JS/TS exports (heuristic, via regex) ----------

_RE_EXPORT_DECL = re.compile(
    r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|var)\s+([A-Za-z_$][\w$]*)",
    re.MULTILINE,
)
_RE_EXPORT_BRACE = re.compile(r"export\s*\{([^}]*)\}")
_RE_EXPORTS_DOT = re.compile(r"(?:module\.)?exports\.([A-Za-z_$][\w$]*)\s*=")


def extract_js_ts_exports(text: str):
    """Heuristic surface scan for named exports. Not a parser; labeled as such."""
    names = set(_RE_EXPORT_DECL.findall(text))
    for brace in _RE_EXPORT_BRACE.findall(text):
        for part in brace.split(","):
            token = part.strip()
            if not token:
                continue
            # handle "a as b": the exported name is what follows "as"
            if " as " in token:
                token = token.split(" as ")[-1].strip()
            token = token.lstrip("*").strip()
            if re.match(r"^[A-Za-z_$][\w$]*$", token):
                names.add(token)
    names.update(_RE_EXPORTS_DOT.findall(text))
    return sorted(names), "regex-heuristic"


def extract_exports(path: Path):
    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if suffix == ".py":
        symbols, method = extract_python_exports(text)
        language = "python"
    else:
        symbols, method = extract_js_ts_exports(text)
        language = "typescript" if suffix in (".ts", ".tsx") else "javascript"
    return {"language": language, "method": method, "symbols": symbols}


# ---------- Dependency parsers ----------


def deps_from_package_json(path: Path):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    out = []
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        block = data.get(key)
        if isinstance(block, dict):
            out.extend(block.keys())
    return sorted(set(out))


def deps_from_requirements(path: Path):
    out = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            name = re.split(r"[<>=!~;\[ ]", line, 1)[0].strip()
            if name:
                out.append(name)
    except OSError:
        return []
    return sorted(set(out))


def deps_from_go_mod(path: Path):
    out = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    in_block = False
    for line in lines:
        s = line.strip()
        if s.startswith("require ("):
            in_block = True
            continue
        if in_block and s == ")":
            in_block = False
            continue
        if in_block and s:
            out.append(s.split()[0])
        elif s.startswith("require ") and "(" not in s:
            parts = s.split()
            if len(parts) >= 2:
                out.append(parts[1])
    return sorted(set(out))


def _toml_load(path: Path):
    if tomllib is None:
        return None
    try:
        with path.open("rb") as handle:
            return tomllib.load(handle)
    except (OSError, ValueError):
        return None


def deps_from_pyproject(path: Path):
    data = _toml_load(path)
    if data is None:
        return []
    out = []
    project = data.get("project", {})
    for dep in project.get("dependencies", []) or []:
        if isinstance(dep, str):
            out.append(re.split(r"[<>=!~;\[ ]", dep, 1)[0].strip())
    poetry = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    if isinstance(poetry, dict):
        out.extend(k for k in poetry.keys() if k.lower() != "python")
    return sorted(set(n for n in out if n))


def deps_from_cargo(path: Path):
    data = _toml_load(path)
    if data is None:
        return []
    out = []
    for key in ("dependencies", "dev-dependencies", "build-dependencies"):
        block = data.get(key)
        if isinstance(block, dict):
            out.extend(block.keys())
    return sorted(set(out))


def deps_from_mise(path: Path):
    data = _toml_load(path)
    if data is None:
        return []
    tools = data.get("tools")
    if isinstance(tools, dict):
        return sorted(tools.keys())
    return []


DEP_FILES = {
    "package.json": ("npm", deps_from_package_json),
    "requirements.txt": ("python", deps_from_requirements),
    "pyproject.toml": ("python", deps_from_pyproject),
    "go.mod": ("go", deps_from_go_mod),
    "Cargo.toml": ("rust", deps_from_cargo),
    ".mise.toml": ("mise-tools", deps_from_mise),
}


# ---------- Index assembly ----------


def build_index(root: Path) -> dict:
    root = root.resolve()
    dependencies: dict = {}
    exports: dict = {}
    skipped_toml = []
    files_scanned = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            rel = str(path.relative_to(root))
            if name in DEP_FILES:
                bucket, parser = DEP_FILES[name]
                if name.endswith(".toml") and tomllib is None:
                    skipped_toml.append(rel)
                    continue
                found = parser(path)
                if found:
                    dependencies.setdefault(bucket, [])
                    dependencies[bucket] = sorted(set(dependencies[bucket] + found))
            if path.suffix.lower() in EXPORT_EXTENSIONS:
                result = extract_exports(path)
                files_scanned += 1
                if result and result["symbols"]:
                    exports[rel] = result

    symbols_total = sum(len(v["symbols"]) for v in exports.values())
    deps_total = sum(len(v) for v in dependencies.values())
    return {
        "generated_from": str(root),
        "dependencies": dependencies,
        "exports": exports,
        "summary": {
            "files_scanned": files_scanned,
            "files_with_exports": len(exports),
            "symbols_total": symbols_total,
            "dependencies_total": deps_total,
            "skipped_toml_no_tomllib": skipped_toml,
            "note": "python exports are precise (ast); js/ts exports are a regex heuristic",
        },
    }


# ---------- CLI ----------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Capability-index generator: map declared dependencies and exported symbols. Advisory; never blocks.",
    )
    parser.add_argument("root", help="root directory to scan")
    parser.add_argument("--out", default=None, help="write the index JSON to this path instead of stdout")
    args = parser.parse_args(argv)

    index = build_index(Path(args.root))
    payload = json.dumps(index, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
        sys.stdout.write("wrote {0} ({1} files with exports, {2} symbols, {3} dependencies)\n".format(
            args.out, index["summary"]["files_with_exports"],
            index["summary"]["symbols_total"], index["summary"]["dependencies_total"]))
    else:
        sys.stdout.write(payload + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
