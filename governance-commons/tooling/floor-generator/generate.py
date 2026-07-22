# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Floor generator (Stage 5).

Reads the rich L1 layer (registry, selection, and the capability-bound bindings)
and emits the lean runtime floor a project actually runs:

  - .pre-commit-config.yaml   local hooks for pre-commit-stage gates
  - governance-ci.yml         a GitHub Actions workflow for ci-stage gates
  - REVIEW-CHECKLIST.md       the L2 review manifest (semantic rules + checklists)

For a given project stack (the active ecosystems), each mechanical rule's gate is
resolved to concrete tools through selection (or a direct tool reference), then
tools are grouped into hooks and steps. This first cut is unpinned: hooks invoke
tools through the project's own runner (uv, npx, system) rather than pinned
upstream hook revisions. A later pinning pass can lift revisions and the
invocation table into the registry.

Run:
  uv run governance-commons/tooling/floor-generator/generate.py \
      --stack python typescript terraform alerting --out OUTDIR
"""
import argparse
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]      # governance-commons/
CONCERNS = ROOT / "catalogs" / "concerns"
REGISTRY = ROOT / "toolchain" / "registry.yaml"
SELECTION = ROOT / "toolchain" / "selection.yaml"

# The one piece of tool knowledge not yet in the registry: how each tool is
# invoked. The pinning pass can move this into registry entries. stage is the
# default lane; a tool may still be emitted into CI as well.
INVOCATIONS = {
    "ruff":         {"stage": "pre-commit", "hooks": [("ruff-check", "uv run ruff check", "lint"), ("ruff-format", "uv run ruff format --check", "format")], "ci": "uv run ruff check && uv run ruff format --check"},
    "mypy":         {"stage": "pre-commit", "hooks": [("mypy", "uv run mypy .", "type-check")], "ci": "uv run mypy ."},
    "pytest":       {"stage": "ci", "ci": "uv run pytest"},
    "bandit":       {"stage": "pre-commit", "hooks": [("bandit", "uv run bandit -q -r . -c pyproject.toml", "sast")], "ci": "uv run bandit -q -r ."},
    "eslint":       {"stage": "pre-commit", "hooks": [("eslint", "npx --no-install eslint .", "lint")], "ci": "npx eslint ."},
    "prettier":     {"stage": "pre-commit", "hooks": [("prettier", "npx --no-install prettier --check .", "format")], "ci": "npx prettier --check ."},
    "typescript":   {"stage": "ci", "ci": "npx tsc --noEmit"},
    "vitest":       {"stage": "ci", "ci": "npx vitest run"},
    "opentofu":     {"stage": "pre-commit", "hooks": [("tofu-fmt", "tofu fmt -check -recursive", "format"), ("tofu-validate", "tofu validate", "schema-validate")], "ci": "tofu fmt -check -recursive && tofu validate"},
    "tflint":       {"stage": "pre-commit", "hooks": [("tflint", "tflint", "lint")], "ci": "tflint"},
    "trivy":        {"stage": "ci", "ci": "trivy config ."},
    "gitleaks":     {"stage": "pre-commit", "hooks": [("gitleaks", "gitleaks protect --staged --redact", "secrets")], "ci": "gitleaks detect --redact"},
    "opengrep":     {"stage": "ci", "ci": "opengrep scan --config auto ."},
    "osv-scanner":  {"stage": "ci", "ci": "osv-scanner scan ."},
    "uv":           {"stage": "ci", "ci": "uv lock --check"},
    "npm":          {"stage": "ci", "ci": "npm ci"},
    "cosign":       {"stage": "deploy", "ci": "cosign verify --certificate-identity-regexp '.*' <artifact>  # deploy-time; consumer sets allowed-signers policy"},
    "slsa-verifier":{"stage": "deploy", "ci": "slsa-verifier verify-artifact <artifact> --source-uri <repo>  # deploy-time"},
    "amtool":       {"stage": "ci", "ci": "amtool check-config <alerting-config>"},
    "tsc":          {"stage": "ci", "ci": "npx tsc --noEmit"},
}


def load(p):
    with open(p) as fh:
        return yaml.safe_load(fh) or {}


def resolve(gate, direct, stack, selection):
    if direct:
        return [direct]
    tools = []
    for eco in list(stack) + ["any"]:
        for t in (selection.get(eco, {}) or {}).get(gate, []):
            if t not in tools:
                tools.append(t)
    return tools


def main():
    ap = argparse.ArgumentParser(description="Generate the lean runtime floor from the rich L1 layer")
    ap.add_argument("--stack", nargs="+", default=["python", "typescript"], help="active project ecosystems")
    ap.add_argument("--out", default=".", help="output directory")
    args = ap.parse_args()

    registry = load(REGISTRY)
    selection = load(SELECTION)
    pinned = {t: (registry.get(t) or {}).get("pinned-version") for t in registry}
    stack = args.stack
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # tool -> set of rule ids it enforces; and L2 rules for the review manifest
    tool_rules = {}            # tool_id -> [rule_id, ...]
    unresolved = []            # (rule_id, gate) with no tool for this stack
    l2 = []                    # (concern, rule_id, checklist_path)

    for concern_dir in sorted(CONCERNS.iterdir()):
        if not concern_dir.is_dir():
            continue
        for rdir in sorted(concern_dir.iterdir()):
            rule_f = rdir / "rule.yaml"
            if not rule_f.exists():
                continue
            rule = load(rule_f)
            rid = rule.get("id", rdir.name)
            layer = rule.get("layer")
            if layer == "mechanical":
                b = rdir / "binding.yaml"
                if not b.exists():
                    continue
                binding = load(b)
                gate = binding.get("gate")
                direct = binding.get("tool")
                tools = resolve(gate, direct, stack, selection)
                if not tools:
                    unresolved.append((rid, gate))
                for t in tools:
                    tool_rules.setdefault(t, []).append(rid)
            elif layer == "semantic":
                cl = rdir / "checklist.md"
                if cl.exists():
                    l2.append((concern_dir.name, rid, str(cl.relative_to(ROOT.parent))))

    needed = sorted(tool_rules)

    # ---- .pre-commit-config.yaml ----
    pc_hooks = []
    for t in needed:
        inv = INVOCATIONS.get(t)
        if not inv or inv.get("stage") != "pre-commit":
            continue
        for hook_id, entry, cap in inv.get("hooks", []):
            ver = pinned.get(t)
            pc_hooks.append({
                "id": hook_id,
                "name": f"{hook_id} ({cap})" + (f" [pinned {t} {ver}]" if ver else ""),
                "entry": entry,
                "language": "system",
                "pass_filenames": False,
            })
    pc = {"repos": [{"repo": "local", "hooks": pc_hooks}]}
    pc_header = (
        "# Generated by the governance-commons floor generator (Stage 5, unpinned cut).\n"
        f"# Stack: {', '.join(stack)}. Do not edit by hand; regenerate from the L1 layer.\n"
        "# Local hooks invoke tools through the project runner; a pinning pass will\n"
        "# switch to pinned upstream hook revisions.\n"
    )
    (out / ".pre-commit-config.yaml").write_text(pc_header + yaml.safe_dump(pc, sort_keys=False))

    # ---- GitHub Actions workflow ----
    ci_steps = [{"name": "Checkout", "uses": "actions/checkout@v4"}]
    pin_lines = [f"{t}=={pinned[t]}" for t in needed if pinned.get(t)]
    if pin_lines:
        ci_steps.append({
            "name": "Pinned tool versions (from registry; install these exact versions)",
            "run": "echo 'pinned: " + " ".join(pin_lines) + "'",
        })
    for t in needed:
        inv = INVOCATIONS.get(t)
        if not inv:
            continue
        if inv.get("stage") in ("ci", "pre-commit"):
            cmd = inv.get("ci")
            if cmd:
                ver = pinned.get(t)
                ci_steps.append({"name": f"{t}" + (f" ({ver})" if ver else ""), "run": cmd})
    deploy = [t for t in needed if INVOCATIONS.get(t, {}).get("stage") == "deploy"]
    wf = {
        "name": "governance-floor",
        "on": {"pull_request": {}, "push": {"branches": ["main"]}},
        "jobs": {
            "governance": {
                "runs-on": "ubuntu-latest",
                "steps": ci_steps,
            }
        },
    }
    wf_header = (
        "# Generated by the governance-commons floor generator (Stage 5, unpinned cut).\n"
        f"# Stack: {', '.join(stack)}. Regenerate from the L1 layer; do not edit by hand.\n"
    )
    if deploy:
        wf_header += "# Deploy-time provenance gates (run in your deploy pipeline, not here): " + ", ".join(deploy) + ".\n"
    (out / "governance-ci.yml").write_text(wf_header + yaml.safe_dump(wf, sort_keys=False))

    # ---- L2 review manifest ----
    lines = ["# Review checklist manifest (L2)", "",
             "These rules are enforced by human or AI review, not by a gate. Each links",
             "to its checklist. Wire them into your pull-request template or review bot.", ""]
    by_concern = {}
    for concern, rid, path in l2:
        by_concern.setdefault(concern, []).append((rid, path))
    for concern in sorted(by_concern):
        lines.append(f"## {concern}")
        for rid, path in sorted(by_concern[concern]):
            lines.append(f"- {rid}  ({path})")
        lines.append("")
    (out / "REVIEW-CHECKLIST.md").write_text("\n".join(lines))

    # ---- summary to stdout ----
    print(f"stack: {', '.join(stack)}")
    print(f"pre-commit hooks: {len(pc_hooks)}  |  ci steps: {len(ci_steps) - 1}  |  L2 review rules: {len(l2)}")
    print("tools engaged:")
    for t in needed:
        stg = INVOCATIONS.get(t, {}).get("stage", "?")
        print(f"  {t:14} [{stg}]  enforces {len(tool_rules[t])} rule(s)")
    if unresolved:
        print(f"\nNOT enforced for this stack ({len(unresolved)} rule(s); their ecosystem is absent):")
        seen = set()
        for rid, gate in unresolved:
            key = gate
            if key not in seen:
                seen.add(key)
            print(f"  {rid}  (gate {gate})")
    print(f"\nwrote: {out/'.pre-commit-config.yaml'}, {out/'governance-ci.yml'}, {out/'REVIEW-CHECKLIST.md'}")


if __name__ == "__main__":
    main()
