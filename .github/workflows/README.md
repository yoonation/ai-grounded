# GitHub Actions workflows

## `ci.yml`

Runs on every pull request and on pushes to `main`. It mirrors the local
pre-commit gate chain so contributions are checked automatically:

- **tests** — the Python test suites under `tooling/**`, `governance-commons/tooling/**`, and `.claude/hooks/**`
- **validators** — `tooling/gates/describe.py --check --strict` (the gate inventory matches `docs/GATES.md`), plus advisory manifest/schema checks
- **lint** — `ruff` on all Python, `shellcheck` on framework-authored shell
- **secrets** — gitleaks, using `.gitleaks.toml`
- **dco** — every PR commit carries a `Signed-off-by` line (`git commit -s`)

Actions are version-pinned (no `@latest`/`@main`); `renovate.json` keeps them
current and digest-pins them over time.
