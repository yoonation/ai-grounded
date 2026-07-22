# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "jsonschema"]
# ///
"""
Substrate validator.

Checks the authored granular form of governance-commons before assembly:
  - every concern.yaml and rule.yaml validates against its JSON schema
  - rule folder name matches the slug half of the rule id
  - rule id is single-home (no id authored in two folders)
  - required artifact is present per layer
      mechanical  -> binding.yaml
      semantic    -> checklist.md
      judgmental  -> decision.md
  - rule.characteristic matches its concern.characteristic (warn only)
  - profiles, threat catalogs, and mappings validate against their schemas

Severity of failures is governed by authoring-mode.yaml:
  solo      -> problems are warnings; exit 0
  published -> problems are errors;   exit 1

Run:  uv run governance-commons/tooling/assemble/validate.py
"""
import sys
import pathlib
import yaml
import json
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[2]          # governance-commons/
CONCERNS = ROOT / "catalogs" / "concerns"
SCHEMAS = ROOT / "schemas"
MODE_FILE = ROOT / "authoring-mode.yaml"
TOOLCHAIN = ROOT / "toolchain"                              # L1 registry + selection (born in Stage 1)
PROFILES = ROOT / "profiles"
THREATS = ROOT / "catalogs" / "threats"
MAPPINGS = ROOT / "mappings"
DESIGNPATTERNS = ROOT / "catalogs" / "design-patterns"

GATE_TYPES = {
    "format", "lint", "type-check", "test", "dep-vuln", "dep-pinning", "sast",
    "secrets", "iac-scan", "schema-validate", "license-scan", "provenance-verify",
}

REQUIRED_ARTIFACT = {
    "mechanical": "binding.yaml",
    "semantic": "checklist.md",
    "judgmental": "decision.md",
}


def load_yaml(p):
    with open(p) as fh:
        return yaml.load(fh, Loader=_StrDates)


class _StrDates(yaml.SafeLoader):
    """SafeLoader that leaves ISO date/timestamp scalars as strings.

    Several substrate schemas type date fields as 'string'. PyYAML would
    otherwise deserialize an unquoted ISO date to datetime.date and fail
    schema validation. Reading them as strings matches both the authored
    intent and the behaviour of the retired check-jsonschema validators.
    """


_StrDates.yaml_implicit_resolvers = {
    ch: [(tag, regexp) for (tag, regexp) in resolvers
         if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_schema(name):
    with open(SCHEMAS / name) as fh:
        return json.load(fh)


def mode():
    if MODE_FILE.exists():
        m = load_yaml(MODE_FILE) or {}
        return m.get("mode", "solo")
    return "solo"


def validate_collection(directory, schema_name, pattern, problems):
    """Validate every `pattern` file in `directory` against `schema_name`.

    Returns the count validated. No-op (returns 0) if the directory or the
    schema is absent. Folds in the coverage of the retired shell validators
    (profiles, threats) and closes the previously-unvalidated mappings gap.
    """
    if not directory.exists() or not (SCHEMAS / schema_name).exists():
        return 0
    validator = Draft202012Validator(load_schema(schema_name))
    n = 0
    for f in sorted(directory.glob(pattern)):
        n += 1
        for err in validator.iter_errors(load_yaml(f)):
            problems.append(("error", f"{f.relative_to(ROOT)}: schema: {err.message}"))
    return n


def main():
    problems = []          # (kind, message)
    rule_schema = Draft202012Validator(load_schema("rule.schema.json"))
    concern_schema = Draft202012Validator(load_schema("concern.schema.json"))
    binding_schema = Draft202012Validator(load_schema("binding.schema.json"))

    seen_ids = {}          # id -> folder path (single-home check)
    n_concerns = 0
    n_rules = 0

    # --- L1 toolchain (registry + selection): validated when present, no-op otherwise ---
    registry_data = {}
    selection_data = {}
    selection_caps = set()      # union of capabilities offered by any ecosystem
    reg_path = TOOLCHAIN / "registry.yaml"
    sel_path = TOOLCHAIN / "selection.yaml"

    if reg_path.exists():
        registry_data = load_yaml(reg_path) or {}
        if (SCHEMAS / "registry.schema.json").exists():
            reg_schema = Draft202012Validator(load_schema("registry.schema.json"))
            for err in reg_schema.iter_errors(registry_data):
                problems.append(("error", f"{reg_path.relative_to(ROOT)}: schema: {err.message}"))
        # superseded-by targets must exist
        for tid, entry in registry_data.items():
            st = (entry or {}).get("status", "")
            if isinstance(st, str) and st.startswith("superseded-by:"):
                tgt = st.split(":", 1)[1]
                if tgt not in registry_data:
                    problems.append(("error", f"{reg_path.relative_to(ROOT)}: '{tid}' superseded-by target '{tgt}' not in registry"))

    if sel_path.exists():
        selection_data = load_yaml(sel_path) or {}
        if (SCHEMAS / "selection.schema.json").exists():
            sel_schema = Draft202012Validator(load_schema("selection.schema.json"))
            for err in sel_schema.iter_errors(selection_data):
                problems.append(("error", f"{sel_path.relative_to(ROOT)}: schema: {err.message}"))
        for eco, caps in (selection_data or {}).items():
            for cap, tids in (caps or {}).items():
                selection_caps.add(cap)
                if registry_data:
                    for tid in (tids or []):
                        if tid not in registry_data:
                            problems.append(("error", f"{sel_path.relative_to(ROOT)}: {eco}.{cap}: tool '{tid}' not in registry"))
                        elif registry_data[tid].get("status") != "active":
                            problems.append(("error", f"{sel_path.relative_to(ROOT)}: {eco}.{cap}: tool '{tid}' status '{registry_data[tid].get('status')}', selection requires active"))

    if not CONCERNS.exists():
        print("no catalogs/concerns directory found")
        return 0

    for concern_dir in sorted(p for p in CONCERNS.iterdir() if p.is_dir()):
        concern_yaml = concern_dir / "concern.yaml"
        if not concern_yaml.exists():
            continue                      # not a migrated concern yet; skip
        n_concerns += 1
        concern = load_yaml(concern_yaml) or {}
        for err in concern_schema.iter_errors(concern):
            problems.append(("error", f"{concern_yaml.relative_to(ROOT)}: schema: {err.message}"))
        concern_characteristic = concern.get("characteristic")

        for rule_dir in sorted(p for p in concern_dir.iterdir() if p.is_dir()):
            rule_yaml = rule_dir / "rule.yaml"
            if not rule_yaml.exists():
                continue
            n_rules += 1
            rule = load_yaml(rule_yaml) or {}
            rel = rule_yaml.relative_to(ROOT)

            for err in rule_schema.iter_errors(rule):
                problems.append(("error", f"{rel}: schema: {err.message}"))

            rid = rule.get("id", "")
            # folder-name matches slug half of id
            if "." in rid:
                concern_part, slug_part = rid.split(".", 1)
                if slug_part != rule_dir.name:
                    problems.append(("error", f"{rel}: folder '{rule_dir.name}' does not match id slug '{slug_part}'"))
                if concern_part != concern_dir.name:
                    problems.append(("error", f"{rel}: id concern '{concern_part}' does not match folder '{concern_dir.name}'"))
            # single-home
            if rid in seen_ids:
                problems.append(("error", f"{rel}: id '{rid}' also authored at {seen_ids[rid]} (ids must be single-home)"))
            else:
                seen_ids[rid] = str(rel)
            # required artifact per layer
            layer = rule.get("layer")
            need = REQUIRED_ARTIFACT.get(layer)
            if need and not (rule_dir / need).exists():
                problems.append(("error", f"{rel}: layer '{layer}' requires {need} in the rule folder"))
            # binding.yaml schema validation when present
            bpath = rule_dir / "binding.yaml"
            if bpath.exists():
                binding = load_yaml(bpath) or {}
                for err in binding_schema.iter_errors(binding):
                    problems.append(("error", f"{bpath.relative_to(ROOT)}: schema: {err.message}"))
                if binding.get("rule") and binding["rule"] != rid:
                    problems.append(("error", f"{bpath.relative_to(ROOT)}: binding.rule '{binding.get('rule')}' does not match rule id '{rid}'"))
                # capability-bound referential integrity (only when toolchain data exists)
                if binding.get("binding_status") == "capability-bound" and (reg_path.exists() or sel_path.exists()):
                    direct = binding.get("tool")
                    g = binding.get("gate")
                    if direct:
                        if registry_data and direct not in registry_data:
                            problems.append(("error", f"{bpath.relative_to(ROOT)}: tool '{direct}' not in registry"))
                    elif g and selection_data and g not in selection_caps:
                        problems.append(("error", f"{bpath.relative_to(ROOT)}: gate '{g}' not resolvable through any selection ecosystem"))
            # characteristic alignment (warn)
            if concern_characteristic and rule.get("characteristic") and rule["characteristic"] != concern_characteristic:
                problems.append(("warn", f"{rel}: rule characteristic '{rule['characteristic']}' differs from concern '{concern_characteristic}'"))

    current_mode = mode()

    # --- substrate-authored collections (folded in from the retired shell validators) ---
    n_profiles = validate_collection(PROFILES, "profile.schema.json", "*.oscal.yaml", problems)
    n_threats = validate_collection(THREATS, "threat-catalog.schema.json", "*.yaml", problems)
    n_mappings = validate_collection(MAPPINGS, "mapping.schema.json", "*.oscal.yaml", problems)
    n_patterns = validate_collection(DESIGNPATTERNS, "design-pattern-catalog.schema.json", "*.yaml", problems)

    blocking = [m for k, m in problems if k == "error"]
    warnings = [m for k, m in problems if k == "warn"]

    print(f"mode: {current_mode}")
    print(f"checked {n_concerns} concern(s), {n_rules} rule(s)")
    print(f"        {n_profiles} profile(s), {n_threats} threat catalog(s), {n_mappings} mapping(s)")
    print(f"        {n_patterns} design-pattern catalog(s)")
    if reg_path.exists() or sel_path.exists():
        print(f"toolchain: {len(registry_data)} tool(s), {len(selection_data)} ecosystem(s) in selection")
    for m in warnings:
        print(f"  WARN  {m}")
    for m in blocking:
        print(f"  {'WARN' if current_mode == 'solo' else 'ERROR'}  {m}")

    if not problems:
        print("OK: all checks passed")
        return 0
    if current_mode == "published" and blocking:
        print(f"FAIL: {len(blocking)} error(s) in published mode")
        return 1
    print(f"done: {len(blocking)} issue(s) reported as warnings in solo mode")
    return 0


if __name__ == "__main__":
    sys.exit(main())
