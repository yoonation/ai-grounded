<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Prerequisites

This document enumerates the tools and runtimes required to use this
template. Versions reflect what the template was developed and tested
against. Install in the order shown; later steps may depend on earlier
ones.

## Operating system

| OS | Status |
|---|---|
| macOS (Apple Silicon) | Tested and primary development target |
| macOS (Intel) | Should work but untested |
| Linux (Ubuntu 22.04+, Debian 12+) | Should work; minor path differences |
| Windows (native) | Not supported; use WSL2 |
| Windows (WSL2 with Ubuntu 22.04+) | Should work |

If you are on macOS, see the macOS install path below. If you are on
Linux, see the Linux install path. The required tools are the same; only
the package manager commands differ.

## Required tools

### Tier 1: Foundation

Tools that must be installed before anything else can work.

| Tool | Minimum version | Used for | Required |
|---|---|---|---|
| git | 2.39 | Version control | Yes |
| zsh or bash | any modern | Shell | Yes |
| curl | any modern | Downloads | Yes |
| jq | 1.6 | Event log queries; loop-closure hook | Yes |

### Tier 2: Runtime managers

The template uses two complementary managers. Both must be installed.

| Tool | Minimum version | Used for |
|---|---|---|
| **uv** | 0.5 | Python CLI tools (spec-kit, checkov, pre-commit) |
| **mise** | 2025.x | Runtime versions (Python, Node, Terraform) pinned per project |

Why both:

- `uv` installs Python CLI tools globally in isolated environments
  (`~/.local/share/uv/tools/<tool>/venv/`) and symlinks the binary into
  `~/.local/bin/`. Spec-kit specifically requires installation via uv
  from its git source, because the PyPI package is stale (see SETUP.md).
- `mise` pins runtimes per project via `.mise.toml`. Running
  `mise install` in a cloned project produces the exact Python, Node,
  and Terraform versions the project was developed against.

Do not use `mise`'s `pipx:` backend for spec-kit. It will pull a stale
PyPI version that fails to initialize against current spec-kit releases.
Use `uv tool install` from git for spec-kit specifically.

### Tier 3: AI tooling

| Tool | Minimum version | Required |
|---|---|---|
| Claude Code | latest | Yes (the agents live in `.claude/agents/`) |
| Claude.ai Pro or Max subscription, OR Console API account | active | Yes (for Claude Code authentication) |

The twelve specialized sub-agents and the spec-kit skills are
Claude-Code-specific. Other AI tools (Cursor, Cline, etc.) can still
read `AGENTS.md` and follow the spec-driven workflow manually, but they
won't have access to the agents.

### Tier 4: Python tools (installed via uv)

These are installed via `uv tool install`, not via mise or pip.

| Tool | Used for |
|---|---|
| specify-cli (spec-kit) | The spec-driven workflow CLI |
| checkov | Infrastructure-as-code security scanning |
| pre-commit | Git hook framework |

See SETUP.md for the specific install commands. The spec-kit install
has a gotcha: it must be installed from git, not PyPI.

**Minimum spec-kit version: 0.8.11.** Older versions lack the preset
system the framework relies on, and 0.8.11 also fixed a constitution-
clobber bug that older versions had. The framework will not bootstrap
cleanly against pre-0.8.11 spec-kit.

### Tier 5: Optional but recommended

| Tool | Used for | Recommended for |
|---|---|---|
| 1Password CLI (`op`) | Credentials in scripts without env files | Anyone storing secrets in 1Password |
| Cryptomator | Vault for sensitive source documents | Anyone handling PII |
| Lima + nerdctl | Container runtime (Docker alternative) | Container work without Docker Desktop |
| trivy | Container/dependency vulnerability scanning | Security work |
| trufflehog | Secrets scanning | Pre-commit + CI |
| Obsidian | Knowledge management (Zettelkasten) | Long-term study and design notes |

## Install paths

### macOS install path

This is the path the template was developed against, using nix-darwin
for system-level tools.

```bash
# 1. Determinate Systems Nix installer (one-time, if not already installed)
curl --proto '=https' --tlsv1.2 -sSf -L \
  https://install.determinate.systems/nix | sh -s -- install

# 2. Install nix-darwin (one-time)
nix run nix-darwin/master#darwin-rebuild -- switch --flake ~/.config/nix-darwin

# 3. Use nix-darwin to declare your CLI tools
#    Edit ~/.config/nix-darwin/modules/home.nix to add:
#      home.packages = with pkgs; [
#        git curl jq
#        uv mise
#        nodejs_22
#        # plus other CLI tools you want declared
#      ];
#    Then rebuild:
darwin-rebuild switch --flake ~/.config/nix-darwin

# 4. Verify the foundation tools
git --version
jq --version
uv --version
mise --version
```

If you don't use Nix, the Homebrew path works:

```bash
# Foundation
brew install git curl jq

# Runtime managers
brew install uv mise

# Verify
git --version && jq --version && uv --version && mise --version
```

Then install Claude Code (native installer recommended over brew or npm
because the native installer auto-updates):

```bash
curl -fsSL https://claude.ai/install.sh | sh

# Verify
claude --version
```

### Linux install path

For Debian/Ubuntu:

```bash
# Foundation
sudo apt-get update
sudo apt-get install -y git curl jq

# uv (via official installer)
curl -LsSf https://astral.sh/uv/install.sh | sh

# mise (via official installer)
curl https://mise.run | sh
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Verify
git --version && jq --version && uv --version && mise --version

# Claude Code
curl -fsSL https://claude.ai/install.sh | sh
claude --version
```

For Fedora/RHEL substitute `dnf install -y` for `apt-get install -y`.

### Windows install path

Use WSL2 with Ubuntu 22.04 and follow the Linux install path inside
WSL2. The spec-kit scripts and the loop-closure hook require POSIX
shell; native Windows PowerShell support exists but is less
extensively tested in this template.

```powershell
# In Windows PowerShell as Administrator
wsl --install -d Ubuntu-22.04
```

After WSL2 + Ubuntu is set up, follow the Linux instructions above.

## PATH configuration

`uv tool install` places binaries in `~/.local/bin/`. Ensure this is on
your PATH.

### For nix-darwin users

Add to `~/.config/nix-darwin/modules/home.nix`:

```nix
home.sessionPath = [
  "/Users/YOURNAME/.local/bin"
];
```

Then `darwin-rebuild switch --flake ~/.config/nix-darwin`.

### For non-Nix users

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then `source ~/.zshrc` (or open a new terminal).

Verify:

```bash
echo $PATH | tr ':' '\n' | grep "local/bin"
# Expected: a line ending in /.local/bin
```

## Verification

After installing the prerequisites, run this verification block. All
commands should succeed and print a version.

```bash
echo "=== Tier 1: Foundation ==="
git --version
jq --version
curl --version | head -1

echo ""
echo "=== Tier 2: Runtime managers ==="
uv --version
mise --version

echo ""
echo "=== Tier 3: AI tooling ==="
claude --version

echo ""
echo "=== PATH check ==="
echo "$PATH" | tr ':' '\n' | grep "\.local/bin" \
  && echo "PASS: ~/.local/bin is on PATH" \
  || echo "FAIL: ~/.local/bin not on PATH, see PATH configuration above"
```

If everything passes, proceed to SETUP.md to install spec-kit, the
Python tools, and bring up your first project.

## Gotchas (read before SETUP.md)

A short list of things that have bitten template users:

### 1. `ANTHROPIC_API_KEY` in the shell silently bypasses your subscription

If `ANTHROPIC_API_KEY` is set in your shell environment, Claude Code
authenticates with the API key and bills your API account at per-token
rates, **bypassing your Pro/Max subscription entirely**.

```bash
# Check now:
echo $ANTHROPIC_API_KEY
# Should print empty
```

If something prints, either unset it before using Claude Code, or
accept that your subscription is doing nothing.

The clean separation:

- **Claude Code authentication**: subscription, via `claude login` (no env var)
- **API key for project work**: stored in a credentials file, sourced
  only inside specific projects that need it

### 2. `mise`'s `pipx:` backend pulls stale spec-kit from PyPI

Do not install spec-kit via:

```bash
# DON'T DO THIS:
mise use -g pipx:specify-cli@latest
```

The PyPI package `specify-cli` is at v1.0.0 (November 2025) and has
been abandoned in favor of GitHub-only releases. The actual current
version is v0.8.7+ on GitHub. SETUP.md shows the correct install via
`uv tool install --from git+...`.

### 3. `~/.local/bin` not on PATH

`uv tool install` puts binaries here. If PATH isn't configured (see
above), every Python CLI tool will appear "not found" even though it
was installed successfully.

### 4. Em-dashes in markdown flag AI-generated text

If you are evolving this template, prefer regular hyphens over em-dashes
in committed documentation. Em-dashes are a common AI-generation
signature; the template documents prefer human-readable plain hyphens.

### 5. Python 3.11 minimum for spec-kit, 3.12 pinned by this template

Spec-kit requires Python 3.11+. This template pins 3.12 in
`.mise.toml`. Running `mise install` in the project root produces 3.12
automatically. Don't override.

## Reference

| Tool | Project page | Reason for choice |
|---|---|---|
| nix-darwin | https://github.com/LnL7/nix-darwin | Declarative system config |
| Determinate Systems Nix | https://docs.determinate.systems/ | Easier Nix installer |
| uv | https://docs.astral.sh/uv/ | Modern Python tool installer |
| mise | https://mise.jdx.dev/ | Modern runtime version manager |
| Claude Code | https://docs.claude.com/en/docs/claude-code | The CLI this template's agents run in |
| spec-kit | https://github.com/github/spec-kit | The spec-driven workflow CLI |
| jq | https://jqlang.github.io/jq/ | Required by the loop-closure hook |

## Next

Once everything in this document is installed and verified, proceed to
[SETUP.md](SETUP.md) for the project initialization procedure.
