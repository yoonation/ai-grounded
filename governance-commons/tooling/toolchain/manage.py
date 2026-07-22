# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Toolchain registry manager and auditor.

The L1 tool registry (toolchain/registry.yaml) is the single source of tool
definitions; the selection map (toolchain/selection.yaml) maps capabilities to
registry ids. This tool maintains and audits them.

Commands:
  audit             Walk the registry and report per tool: source liveness
                    (git ls-remote), license open-source status, supersession
                    target existence, plus selection-to-registry integrity and
                    ecosystem-by-capability coverage. Read-only.
  add               Add a tool. Verifies the source is live and the license is
                    open-source (or requires the paid exception) before writing.
  update            Change fields on an existing tool; re-verifies source liveness.

Liveness uses `git ls-remote`, not the rate-limited GitHub REST API.

Run:
  uv run governance-commons/tooling/toolchain/manage.py audit
  uv run governance-commons/tooling/toolchain/manage.py add --id ID --source URL \
      --ecosystems python --gate-types lint --license MIT [--status active] \
      [--description TEXT] [--package-manager uv] [--recommended-stage pre-commit]
  uv run governance-commons/tooling/toolchain/manage.py update --id ID [--license ...] [...]
"""
import sys
import argparse
import pathlib
import subprocess
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]      # governance-commons/
TOOLCHAIN = ROOT / "toolchain"
REGISTRY = TOOLCHAIN / "registry.yaml"
SELECTION = TOOLCHAIN / "selection.yaml"

GATE_TYPES = {
    "format", "lint", "type-check", "test", "dep-vuln", "dep-pinning", "sast",
    "secrets", "iac-scan", "schema-validate", "license-scan", "provenance-verify",
}

# Open-source license identifiers accepted without a paid exception.
OSS_LICENSES = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC", "MPL-2.0",
    "LGPL-2.1", "LGPL-3.0", "GPL-2.0", "GPL-3.0", "AGPL-3.0", "EPL-2.0",
    "Unlicense", "CC0-1.0", "0BSD", "Zlib", "Artistic-2.0",
}


def load(path):
    if not path.exists():
        return {}
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def dump(path, data):
    with open(path, "w") as fh:
        yaml.safe_dump(data, fh, sort_keys=True, default_flow_style=False)


def source_alive(url):
    try:
        r = subprocess.run(
            ["git", "ls-remote", "--exit-code", url, "HEAD"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
        )
        return r.returncode == 0
    except Exception:
        return None       # could not determine (offline, timeout)


def license_ok(entry):
    lic = entry.get("license", "")
    if lic in OSS_LICENSES:
        return True
    # paid exception: no OSS tool exists for this capability
    if entry.get("paid") is True and entry.get("no-oss-alternative") is True and entry.get("justification"):
        return True
    # override-only exception: an OSS default exists; this non-OSS tool is a deliberate, candidate-only override
    if entry.get("oss-alternative") and entry.get("justification") and entry.get("status") == "candidate":
        return True
    return False


def cmd_audit(args):
    registry = load(REGISTRY)
    selection = load(SELECTION)
    problems = 0
    notes = 0

    print(f"registry: {len(registry)} tool(s)")
    for tid in sorted(registry):
        e = registry[tid] or {}
        msgs = []
        # liveness
        if not args.no_network:
            alive = source_alive(e.get("source", ""))
            if alive is False:
                msgs.append("SOURCE DEAD")
                problems += 1
            elif alive is None:
                msgs.append("source unverified (offline)")
        # license
        if not license_ok(e):
            msgs.append(f"license '{e.get('license')}' not open-source and no recorded paid exception")
            problems += 1
        # status / supersession
        st = e.get("status", "")
        if isinstance(st, str) and st.startswith("superseded-by:"):
            tgt = st.split(":", 1)[1]
            if tgt not in registry:
                msgs.append(f"superseded-by target '{tgt}' not in registry")
                problems += 1
            else:
                msgs.append(f"superseded by {tgt}")
                notes += 1
        elif st in ("deprecated", "archived"):
            msgs.append(st)
            notes += 1
        elif st == "candidate":
            alt = e.get("oss-alternative")
            msgs.append(f"candidate (override-only{', OSS default ' + alt if alt else ''})")
            notes += 1
        flag = "  ".join(msgs) if msgs else "ok"
        print(f"  {tid:18} {flag}")

    # selection -> registry integrity
    print("selection integrity:")
    sel_caps_by_eco = {}
    for eco, caps in selection.items():
        sel_caps_by_eco[eco] = set((caps or {}).keys())
        for cap, tids in (caps or {}).items():
            if cap not in GATE_TYPES:
                print(f"  {eco}.{cap}: not a known gate-type")
                problems += 1
            for tid in (tids or []):
                if tid not in registry:
                    print(f"  {eco}.{cap}: '{tid}' not in registry")
                    problems += 1
                elif registry[tid].get("status") != "active":
                    print(f"  {eco}.{cap}: '{tid}' status '{registry[tid].get('status')}', must be active")
                    problems += 1
    if problems == 0:
        print("  ok")

    # coverage: capabilities present per ecosystem
    print("coverage by ecosystem:")
    for eco in sorted(selection):
        present = sorted(sel_caps_by_eco.get(eco, set()))
        print(f"  {eco:12} {', '.join(present) if present else '(none)'}")

    print(f"\nsummary: {problems} problem(s), {notes} advisory note(s)")
    if args.strict and problems:
        return 1
    return 0


def cmd_add(args):
    registry = load(REGISTRY)
    if args.id in registry:
        print(f"error: '{args.id}' already in registry (use update)")
        return 1
    entry = {
        "description": args.description or args.id,
        "source": args.source,
        "ecosystems": args.ecosystems,
        "gate-types": args.gate_types,
        "license": args.license,
        "status": args.status,
    }
    if args.package_manager:
        entry["package-manager"] = args.package_manager
    if args.recommended_stage:
        entry["recommended-stage"] = args.recommended_stage
    if args.paid:
        entry["paid"] = True
        entry["no-oss-alternative"] = True
        entry["justification"] = args.justification or ""

    bad = [g for g in args.gate_types if g not in GATE_TYPES]
    if bad:
        print(f"error: unknown gate-type(s): {bad}")
        return 1
    if not license_ok(entry):
        print(f"error: license '{args.license}' is not open-source; pass --paid --justification TEXT if no OSS alternative exists")
        return 1
    alive = source_alive(args.source)
    if alive is False:
        print(f"error: source not reachable: {args.source}")
        return 1
    if alive is None:
        print("error: could not verify source liveness (offline); not writing")
        return 1

    registry[args.id] = entry
    dump(REGISTRY, registry)
    print(f"added '{args.id}' (source verified live, license accepted)")
    return 0


def cmd_update(args):
    registry = load(REGISTRY)
    if args.id not in registry:
        print(f"error: '{args.id}' not in registry (use add)")
        return 1
    entry = registry[args.id]
    for field, val in (
        ("description", args.description), ("source", args.source),
        ("license", args.license), ("status", args.status),
        ("package-manager", args.package_manager),
        ("recommended-stage", args.recommended_stage),
    ):
        if val is not None:
            entry[field] = val
    if args.ecosystems:
        entry["ecosystems"] = args.ecosystems
    if args.gate_types:
        entry["gate-types"] = args.gate_types
    if not license_ok(entry):
        print(f"error: resulting license '{entry.get('license')}' is not open-source and no paid exception recorded")
        return 1
    alive = source_alive(entry["source"])
    if alive is False:
        print(f"error: source not reachable: {entry['source']}")
        return 1
    if alive is None:
        print("error: could not verify source liveness (offline); not writing")
        return 1
    dump(REGISTRY, registry)
    print(f"updated '{args.id}' (source re-verified live)")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Toolchain registry manager and auditor")
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("audit")
    a.add_argument("--no-network", action="store_true", help="skip liveness checks")
    a.add_argument("--strict", action="store_true", help="exit nonzero on problems")
    a.set_defaults(func=cmd_audit)

    def common(p):
        p.add_argument("--id", required=True)
        p.add_argument("--source")
        p.add_argument("--ecosystems", nargs="+")
        p.add_argument("--gate-types", dest="gate_types", nargs="+")
        p.add_argument("--license")
        p.add_argument("--status", default=None)
        p.add_argument("--description")
        p.add_argument("--package-manager", dest="package_manager")
        p.add_argument("--recommended-stage", dest="recommended_stage")
        p.add_argument("--paid", action="store_true")
        p.add_argument("--justification")

    ad = sub.add_parser("add")
    common(ad)
    ad.set_defaults(func=cmd_add, status="active")

    up = sub.add_parser("update")
    common(up)
    up.set_defaults(func=cmd_update)

    args = ap.parse_args()
    if not getattr(args, "func", None):
        ap.print_help()
        return 2
    # add requires the core fields
    if args.cmd == "add":
        missing = [f for f in ("source", "ecosystems", "gate_types", "license") if not getattr(args, f)]
        if missing:
            print(f"error: add requires --{', --'.join(m.replace('_','-') for m in missing)}")
            return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
