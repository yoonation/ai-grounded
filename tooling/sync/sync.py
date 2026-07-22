#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
sync.py - one-way template-to-consumer synchronization.

Direction is strictly one way: the template is read-only input, the consumer
is the only tree this tool writes. Ownership per path comes from the
template's sync-manifest.yaml (substrate, scaffold, framework); the
consumer's .template-sync/overrides.yml register names template-owned paths
the consumer has deliberately taken over, which the tool then skips.

Per-file decision, framework class, using the recorded base (the template
commit recorded in .template-sync/state.json at the last sync plus the
sha256 of each blob as delivered):

  template unchanged since base                       -> skip
  consumer file identical to template                 -> record, skip
  consumer untouched since base, template changed     -> overwrite (backup)
  consumer changed, template unchanged since base     -> keep consumer,
                                                         report DRIFT
  both changed, base blob retrievable from template
  git history                                         -> git merge-file
                                                         three-way; conflict
                                                         markers reported
  no base (first sync)                                -> report CONFLICT and
                                                         keep consumer, or
                                                         overwrite with
                                                         --adopt-template
                                                         (backup first)

Scaffold files are created when missing and never overwritten. The
substrate tree is replaced as a unit whenever it differs, consumer extras
under it deleted, the prior tree backed up. Deletions of framework files
the template dropped are applied only when the consumer copy still matches
the recorded base. Every overwrite and deletion lands a copy under
.template-sync/backup/<timestamp>/ first.

Migrations: executable steps in tooling/sync/migrations/NNN-*.py (template
side) run once each during pull, oldest first, recorded in state. Each must
define apply(consumer_root, template_root) and be idempotent.

Commands:
  status  report what pull would do; writes nothing; exit 0
  check   CI gate; exit 2 when the consumer has drifted from the template
          (framework mismatch, missing scaffold, substrate mismatch, or
          leftover conflict markers); exit 0 when clean
  pull    apply the sync; refuses on a dirty consumer git tree unless
          --allow-dirty
  verify-manifest  template-side self-check: every template file resolves
          to exactly one class and every configured glob matches something

The --template value may be either a local path or a Git URL. A URL (https,
http, git@, or ssh scheme) is cloned into a temporary directory for the run
and removed afterward; a path is used in place. When --template is omitted,
the DEFAULT_TEMPLATE constant near the top of this file is used, so a bare
`pull` with your remote set there needs no arguments. An explicit --template
always overrides the default (use a local path for a one-off offline sync).
The clone is unshallowed on purpose: three-way merges read the last-synced
base blob from template git history, which a shallow clone cannot guarantee.

YAML loading uses PyYAML when importable and otherwise falls back to a
minimal parser sufficient for sync-manifest.yaml and overrides.yml (string
scalars, one nesting level, dash lists). Run with plain python3 or
`uv run --with pyyaml python3` for full YAML.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

STATE_DIR = ".template-sync"
STATE_FILE = "state.json"
OVERRIDES_FILE = "overrides.yml"
BACKUP_DIR = "backup"
MANIFEST_NAME = "sync-manifest.yaml"

# ----------------------------------------------------------------------
# Operator configuration: set these once, then run with no --template.
# ----------------------------------------------------------------------
#
# DEFAULT_TEMPLATE is used whenever --template is not passed on the command
# line. Set it to either a local checkout path or a Git URL. A Git URL is
# cloned fresh for each run into a temporary directory and removed after;
# a local path is used in place with no copying. An explicit --template on
# the command line always overrides this value.
#
# Examples:
#   DEFAULT_TEMPLATE = "https://github.com/yoonation/ai-grounded.git"
#   DEFAULT_TEMPLATE = "git@github.com:yoonation/ai-grounded.git"
#   DEFAULT_TEMPLATE = "~/lab/ai-grounded"
DEFAULT_TEMPLATE = "https://github.com/yoonation/ai-grounded.git"

# DEFAULT_REF is the branch, tag, or commit checked out after a URL clone
# (ignored for a local path, which is read at its current HEAD). Empty
# string means the remote default branch. Pin a tag here for reproducible
# release-based syncs, for example "v1.4.0".
DEFAULT_REF = ""

# Scheme prefixes that mark a --template value as a Git URL rather than a
# local path.
URL_PREFIXES = ("https://", "http://", "git@", "ssh://", "file://")
# A file counts as conflicted only when it carries both an ours and a
# theirs marker line; a bare run of equals signs is a legitimate text
# separator (NOTICE, changelogs) and must not trip the gate.
CONFLICT_OURS = "<" * 7
CONFLICT_THEIRS = ">" * 7

# Path segments the walker never treats as content in either tree, at any
# depth; "dist" is ignored only at the top level (build output) because
# nested dist directories (governance-commons/dist) are real content.
IGNORED_SEGMENTS = {".git", "node_modules", ".venv", "__pycache__", STATE_DIR}
IGNORED_TOP = {"dist"}


# ----------------------------------------------------------------------
# Minimal YAML subset loader (fallback when PyYAML is absent)
# ----------------------------------------------------------------------

def _mini_yaml(text: str):
    root: dict = {}
    stack = [(0, root)]
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        stripped = raw.split("#", 1)[0].rstrip() if not raw.lstrip().startswith("- ") else raw.rstrip()
        if raw.lstrip().startswith("#") or not stripped.strip():
            continue
        indent = len(raw) - len(raw.lstrip())
        while stack and indent < stack[-1][0]:
            stack.pop()
        container = stack[-1][1]
        body = stripped.strip()
        if body.startswith("- "):
            item = body[2:].strip()
            if len(item) >= 2 and item[0] == item[-1] and item[0] in "\"'":
                item = item[1:-1]
            if isinstance(container, list):
                container.append(item)
            continue
        if ":" in body:
            key, _, val = body.partition(":")
            key = key.strip().strip('"')
            val = val.strip()
            if val == "":
                # Look ahead: dash list or nested map
                nxt = i
                while nxt < len(lines) and (not lines[nxt].strip() or lines[nxt].lstrip().startswith("#")):
                    nxt += 1
                child: object
                if nxt < len(lines) and lines[nxt].lstrip().startswith("- "):
                    child = []
                else:
                    child = {}
                if isinstance(container, dict):
                    container[key] = child
                stack.append((indent + 1, child))
            else:
                if isinstance(container, dict):
                    container[key] = val.strip('"').strip("'")
    return root


def load_yaml(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        return _mini_yaml(text)


# ----------------------------------------------------------------------
# Manifest and overrides
# ----------------------------------------------------------------------

class Manifest:
    def __init__(self, data: dict):
        self.substrate = list(data.get("substrate") or [])
        self.scaffold = list(data.get("scaffold") or [])
        self.framework_explicit = list(data.get("framework-explicit") or [])
        eject = data.get("eject") or {}
        self.eject_exclude = list(eject.get("exclude") or [])
        self.eject_allow_refs = list(eject.get("allow-references") or [])

    @staticmethod
    def _match(path: str, globs) -> bool:
        for g in globs:
            if fnmatch.fnmatch(path, g):
                return True
            # "dir/**" should also match files at any depth below dir
            if g.endswith("/**") and (path == g[:-3] or path.startswith(g[:-3] + "/")):
                return True
        return False

    def class_of(self, rel: str) -> str:
        if self._match(rel, self.substrate):
            return "substrate"
        if self._match(rel, self.scaffold):
            return "scaffold"
        return "framework"

    def framework_glob_hit(self, rel: str) -> bool:
        return self._match(rel, self.framework_explicit)


def load_manifest(template: Path) -> Manifest:
    p = template / MANIFEST_NAME
    if not p.is_file():
        sys.exit(f"sync: {MANIFEST_NAME} not found in template at {template}")
    return Manifest(load_yaml(p))


def load_overrides(consumer: Path):
    p = consumer / STATE_DIR / OVERRIDES_FILE
    if not p.is_file():
        return []
    data = load_yaml(p)
    out = []
    for entry in data.get("overrides") or []:
        if isinstance(entry, dict):
            val = str(entry.get("path", "")).strip()
        else:
            val = str(entry).strip()
            if val.startswith("path:"):
                val = val.partition(":")[2].strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
        out.append(val)
    return [o for o in out if o]


def overridden(rel: str, overrides) -> bool:
    return Manifest._match(rel, overrides)


# ----------------------------------------------------------------------
# State, hashing, git helpers
# ----------------------------------------------------------------------

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha256(path.read_bytes())


def load_state(consumer: Path) -> dict:
    p = consumer / STATE_DIR / STATE_FILE
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"template_ref": None, "files": {}, "migrations": []}


def save_state(consumer: Path, state: dict) -> None:
    d = consumer / STATE_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / STATE_FILE).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(args, cwd: Path):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def template_head(template: Path):
    r = git(["rev-parse", "HEAD"], template)
    return r.stdout.strip() if r.returncode == 0 else None


def base_blob(template: Path, ref, rel: str):
    if not ref:
        return None
    r = subprocess.run(
        ["git", "show", f"{ref}:{rel}"],
        cwd=str(template), capture_output=True,
    )
    return r.stdout if r.returncode == 0 else None


def consumer_dirty(consumer: Path) -> bool:
    r = git(["status", "--porcelain"], consumer)
    return r.returncode == 0 and bool(r.stdout.strip())


def consumer_origin(consumer: Path):
    """The consumer's origin remote URL, or None if there is no git repo or
    no origin remote."""
    r = git(["remote", "get-url", "origin"], consumer)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _normalize_remote(url: str) -> str:
    """Reduce a git remote URL to a comparable host/path form so https, ssh,
    and scp-style forms of the same repo compare equal. Strips scheme, a
    trailing .git, a leading git@, and a trailing slash."""
    u = url.strip()
    for pre in ("https://", "http://", "ssh://", "git+ssh://", "file://"):
        if u.startswith(pre):
            u = u[len(pre):]
            break
    if u.startswith("git@"):
        u = u[len("git@"):]
    if "@" not in u and ":" in u and "/" not in u.split(":", 1)[0]:
        u = u.replace(":", "/", 1)
    u = u.rstrip("/")
    if u.endswith(".git"):
        u = u[:-len(".git")]
    return u.lower()


def same_git_remote(a: str, b: str) -> bool:
    return _normalize_remote(a) == _normalize_remote(b)


def is_url(spec: str) -> bool:
    return spec.startswith(URL_PREFIXES)


def resolve_template(spec: str, ref: str):
    """Return (template_path, cleanup_dir_or_None). A URL is cloned
    unshallowed into a temp dir (checked out at ref when given) so the
    three-way base blob stays retrievable from history; a local path is
    resolved in place. The caller removes cleanup_dir when set."""
    if is_url(spec):
        tmp = Path(tempfile.mkdtemp(prefix="template-sync-"))
        r = subprocess.run(["git", "clone", "--quiet", spec, str(tmp)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            shutil.rmtree(tmp, ignore_errors=True)
            sys.exit(f"sync: git clone failed for {spec}\n{r.stderr.strip()}")
        if ref:
            c = subprocess.run(["git", "-C", str(tmp), "checkout", "--quiet", ref],
                              capture_output=True, text=True)
            if c.returncode != 0:
                shutil.rmtree(tmp, ignore_errors=True)
                sys.exit(f"sync: git checkout {ref} failed for {spec}\n{c.stderr.strip()}")
        return tmp, tmp
    return Path(spec).expanduser().resolve(), None


# ----------------------------------------------------------------------
# Tree walking
# ----------------------------------------------------------------------

def walk(root: Path):
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink():
            continue
        rel = p.relative_to(root).as_posix()
        segs = rel.split("/")
        if segs[0] in IGNORED_TOP or any(s in IGNORED_SEGMENTS for s in segs):
            continue
        files.append(rel)
    return files


def tree_sha(root: Path, files) -> str:
    h = hashlib.sha256()
    for rel in files:
        h.update(rel.encode())
        h.update((root / rel).read_bytes())
    return h.hexdigest()


# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------

class Report:
    def __init__(self):
        self.lines = []
        self.counts: dict = {}

    def add(self, kind: str, msg: str):
        self.counts[kind] = self.counts.get(kind, 0) + 1
        self.lines.append(f"  [{kind}] {msg}")

    def emit(self, header: str):
        print(header)
        for line in self.lines:
            print(line)
        if not self.lines:
            print("  (no differences)")
        summary = ", ".join(f"{k}={v}" for k, v in sorted(self.counts.items()))
        print(f"summary: {summary or 'clean'}")

    def has(self, *kinds) -> bool:
        return any(k in self.counts for k in kinds)


# ----------------------------------------------------------------------
# Core sync
# ----------------------------------------------------------------------

def backup(consumer: Path, rel: str, stamp: str) -> None:
    src = consumer / rel
    if not src.exists():
        return
    dst = consumer / STATE_DIR / BACKUP_DIR / stamp / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_file(consumer: Path, rel: str, data: bytes, mode_from: Path = None) -> None:
    dst = consumer / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    if mode_from is not None and mode_from.exists():
        shutil.copymode(mode_from, dst)


def merge_three_way(base: bytes, ours: Path, theirs: bytes, workdir: Path):
    """git merge-file: ours = consumer, theirs = template. Returns
    (merged_bytes, had_conflicts)."""
    tmp = workdir / STATE_DIR / "merge-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    b = tmp / "base"
    o = tmp / "ours"
    t = tmp / "theirs"
    b.write_bytes(base)
    o.write_bytes(ours.read_bytes())
    t.write_bytes(theirs)
    r = subprocess.run(
        ["git", "merge-file", "-L", "consumer", "-L", "base", "-L", "template",
         "-p", str(o), str(b), str(t)],
        capture_output=True,
    )
    merged = r.stdout
    conflicted = r.returncode > 0
    shutil.rmtree(tmp, ignore_errors=True)
    return merged, conflicted


def run_sync(template: Path, consumer: Path, apply: bool, adopt: bool) -> Report:
    manifest = load_manifest(template)
    overrides = load_overrides(consumer)
    state = load_state(consumer)
    report = Report()
    stamp = time.strftime("%Y%m%d-%H%M%S")

    t_files = walk(template)
    t_set = set(t_files)
    new_files_state: dict = {}

    # --- substrate: whole-tree replace when different -------------------
    sub_t = [f for f in t_files if manifest.class_of(f) == "substrate"]
    sub_roots = sorted({g[:-3] for g in manifest.substrate if g.endswith("/**")})
    sub_c = []
    for root in sub_roots:
        d = consumer / root
        if d.is_dir():
            for p in sorted(d.rglob("*")):
                if not p.is_file() or p.is_symlink():
                    continue
                rel = root + "/" + p.relative_to(d).as_posix()
                if any(s in IGNORED_SEGMENTS for s in rel.split("/")):
                    continue
                sub_c.append(rel)
    sub_t_sha = tree_sha(template, sub_t)
    sub_c_sha = tree_sha(consumer, [f for f in sub_c if (consumer / f).is_file()]) if sub_c else ""
    if sub_t and (sub_t_sha != sub_c_sha):
        report.add("substrate-replace", f"{sub_roots}: consumer tree differs; full replace")
        if apply:
            for rel in sub_c:
                backup(consumer, rel, stamp)
            for root in sub_roots:
                rp = str(root).strip()
                if not rp or rp in (".", "..", "/") or Path(rp).is_absolute() or ".." in Path(rp).parts:
                    report.add("substrate-replace-skip",
                               f"refusing to delete substrate root '{root}': it does not "
                               f"resolve to a safe path under the consumer")
                    continue
                shutil.rmtree(consumer / root, ignore_errors=True)
            for rel in sub_t:
                write_file(consumer, rel, (template / rel).read_bytes(), template / rel)
    for rel in sub_t:
        new_files_state[rel] = file_sha(template / rel)

    # --- scaffold: create if missing, never overwrite -------------------
    for rel in [f for f in t_files if manifest.class_of(f) == "scaffold"]:
        t_hash = file_sha(template / rel)
        c = consumer / rel
        if not c.exists():
            report.add("scaffold-create", rel)
            if apply:
                write_file(consumer, rel, (template / rel).read_bytes(), template / rel)
        elif file_sha(c) != t_hash:
            prior = state["files"].get(rel)
            if prior and prior != t_hash:
                report.add("scaffold-template-changed", f"{rel} (template shell evolved; consumer copy retained)")
            # consumer-filled scaffold: silent, that is the design
        new_files_state[rel] = t_hash

    # --- framework -------------------------------------------------------
    for rel in [f for f in t_files if manifest.class_of(f) == "framework"]:
        t_bytes = (template / rel).read_bytes()
        t_hash = sha256(t_bytes)
        new_files_state[rel] = t_hash
        if overridden(rel, overrides):
            prior = state["files"].get(rel)
            note = " (template side changed since last sync)" if prior and prior != t_hash else ""
            report.add("override-skip", rel + note)
            continue
        c = consumer / rel
        if not c.exists():
            report.add("framework-add", rel)
            if apply:
                write_file(consumer, rel, t_bytes, template / rel)
            continue
        c_hash = file_sha(c)
        if c_hash == t_hash:
            continue
        prior = state["files"].get(rel)
        if prior == c_hash:
            report.add("framework-update", rel)
            if apply:
                backup(consumer, rel, stamp)
                write_file(consumer, rel, t_bytes, template / rel)
        elif prior == t_hash:
            report.add("drift", f"{rel} (consumer modified a template-owned file; register it in "
                                f"{STATE_DIR}/{OVERRIDES_FILE} or revert)")
        else:
            base = base_blob(template, state.get("template_ref"), rel)
            if base is not None:
                merged, conflicted = merge_three_way(base, c, t_bytes, consumer)
                kind = "merge-conflict" if conflicted else "merge-clean"
                report.add(kind, rel)
                if apply:
                    backup(consumer, rel, stamp)
                    write_file(consumer, rel, merged)
            elif adopt:
                report.add("adopt-overwrite", f"{rel} (no base; template adopted, prior copy backed up)")
                if apply:
                    backup(consumer, rel, stamp)
                    write_file(consumer, rel, t_bytes, template / rel)
            else:
                report.add("conflict", f"{rel} (no recorded base; rerun pull with --adopt-template "
                                       f"to take the template version, or register an override)")

    # --- deletions: framework files the template dropped -----------------
    for rel, prior in sorted(state.get("files", {}).items()):
        if rel in t_set:
            continue
        c = consumer / rel
        if not c.exists():
            continue
        cls = manifest.class_of(rel)
        if cls != "framework" or overridden(rel, overrides):
            continue
        if file_sha(c) == prior:
            report.add("framework-delete", rel)
            if apply:
                backup(consumer, rel, stamp)
                c.unlink()
        else:
            report.add("drift", f"{rel} (template deleted this file but the consumer modified it; "
                                f"resolve manually)")

    # --- orphans: consumer files under explicit framework globs ----------
    for rel in walk(consumer):
        if rel in t_set or rel in state.get("files", {}):
            continue
        if manifest.framework_glob_hit(rel) and not overridden(rel, overrides):
            report.add("orphan", f"{rel} (matches a framework glob but the template does not ship it)")

    # --- migrations -------------------------------------------------------
    mig_dir = template / "tooling" / "sync" / "migrations"
    applied = set(state.get("migrations", []))
    for mig in sorted(mig_dir.glob("[0-9]*-*.py")) if mig_dir.is_dir() else []:
        if mig.name in applied:
            continue
        report.add("migration", mig.name)
        if apply:
            ns: dict = {}
            exec(compile(mig.read_text(encoding="utf-8"), str(mig), "exec"), ns)
            msg = ns["apply"](consumer, template)
            if msg:
                print(f"  migration {mig.name}: {msg}")
            applied.add(mig.name)

    if apply:
        state["template_ref"] = template_head(template) or state.get("template_ref")
        state["synced_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        state["files"] = new_files_state
        state["migrations"] = sorted(applied)
        save_state(consumer, state)

    return report


# ----------------------------------------------------------------------
# check and verify-manifest
# ----------------------------------------------------------------------

def conflict_marker_files(consumer: Path):
    hits = []
    for rel in walk(consumer):
        p = consumer / rel
        try:
            head = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        lines = head.splitlines()
        has_ours = any(ln.startswith(CONFLICT_OURS + " ") or ln == CONFLICT_OURS for ln in lines)
        has_theirs = any(ln.startswith(CONFLICT_THEIRS + " ") or ln == CONFLICT_THEIRS for ln in lines)
        if has_ours and has_theirs:
            hits.append(rel)
    return hits


def cmd_check(template: Path, consumer: Path) -> int:
    report = run_sync(template, consumer, apply=False, adopt=False)
    markers = conflict_marker_files(consumer)
    for rel in markers:
        report.add("conflict-marker", rel)
    report.emit(f"sync check: consumer={consumer} template={template}")
    drifted = report.has("substrate-replace", "framework-add", "framework-update",
                         "framework-delete", "scaffold-create", "drift", "conflict",
                         "merge-conflict", "conflict-marker", "migration")
    return 2 if drifted else 0


def cmd_verify_manifest(template: Path) -> int:
    manifest = load_manifest(template)
    files = walk(template)
    ok = True
    for globs, name in ((manifest.substrate, "substrate"),
                        (manifest.scaffold, "scaffold"),
                        (manifest.framework_explicit, "framework-explicit")):
        for g in globs:
            if not any(Manifest._match(f, [g]) for f in files):
                print(f"  [unmatched-glob] {name}: {g}")
                ok = False
    census: dict = {}
    for f in files:
        census[manifest.class_of(f)] = census.get(manifest.class_of(f), 0) + 1
    print("verify-manifest census: " + ", ".join(f"{k}={v}" for k, v in sorted(census.items())))
    print("verify-manifest: " + ("OK" if ok else "FAILED"))
    return 0 if ok else 2


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _run(args, template: Path) -> int:
    consumer = Path(args.consumer).expanduser().resolve()
    if not template.is_dir():
        sys.exit(f"sync: template path {template} is not a directory")
    if not consumer.is_dir():
        sys.exit(f"sync: consumer path {consumer} is not a directory")
    if args.command == "verify-manifest":
        return cmd_verify_manifest(template)
    if template == consumer:
        sys.exit("sync: template and consumer are the same directory")
    # Refuse to sync a repo against itself. The flow runs one way (template
    # to application); running status/pull/check from inside the template has
    # nothing upstream to pull. The same-directory check above catches the
    # local-path case; this catches syncing from a URL that resolves to the
    # consumer's own origin remote, which is what happens when the tool is
    # run inside the template with the remote default pointing at that
    # template's repo. Applications legitimately carry a synced copy of
    # sync-manifest.yaml, so the manifest's presence is not the signal;
    # same-origin is. verify-manifest is exempt above (it is meant to run in
    # a template).
    if getattr(args, "_template_spec_is_url", False):
        origin = consumer_origin(consumer)
        if origin and same_git_remote(origin, getattr(args, "_template_spec", "")):
            sys.exit(
                f"sync: the template URL resolves to this repo's own origin "
                f"({origin}). The flow runs one way (template to application); "
                f"run status/pull/check from an application repo, not the "
                f"template. (Only verify-manifest belongs in the template.)"
            )
    if args.command == "check":
        return cmd_check(template, consumer)
    if args.command == "status":
        report = run_sync(template, consumer, apply=False, adopt=args.adopt_template)
        report.emit(f"sync status (dry run): consumer={consumer} template={template}")
        return 0
    # pull
    if consumer_dirty(consumer) and not args.allow_dirty:
        sys.exit("sync: consumer git tree is dirty; commit or stash first, or pass --allow-dirty")
    report = run_sync(template, consumer, apply=True, adopt=args.adopt_template)
    report.emit(f"sync pull: consumer={consumer} template={template}")
    if report.has("conflict", "merge-conflict"):
        print("sync: conflicts remain; resolve before committing (check blocks on markers).")
        return 2
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="One-way template-to-consumer sync.")
    ap.add_argument("command", choices=["status", "check", "pull", "verify-manifest"])
    ap.add_argument("--template", default=None,
                    help="Template local path or Git URL. Omit to use DEFAULT_TEMPLATE.")
    ap.add_argument("--ref", default=None,
                    help="Branch, tag, or commit to check out after a URL clone. "
                         "Omit to use DEFAULT_REF (empty means the remote default branch). "
                         "Ignored for a local path.")
    ap.add_argument("--consumer", default=".", help="Path to the consumer repo (default: cwd).")
    ap.add_argument("--adopt-template", action="store_true",
                    help="On files with no recorded base, take the template version (backup first).")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="Permit pull on a consumer tree with uncommitted changes.")
    args = ap.parse_args(argv)

    spec = args.template if args.template is not None else DEFAULT_TEMPLATE
    ref = args.ref if args.ref is not None else DEFAULT_REF
    args._template_spec = spec
    args._template_spec_is_url = is_url(spec)
    if is_url(spec):
        print(f"sync: cloning template {spec}" + (f" at {ref}" if ref else "") + " ...")
    template, cleanup = resolve_template(spec, ref)
    try:
        return _run(args, template)
    finally:
        if cleanup is not None:
            shutil.rmtree(cleanup, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
