<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->


# Playbook: Compromised MCP Server

**ID**: compromised-mcp-server
**Severity**: critical
**Related catalogs**: OWASP LLM03 (Supply Chain), LLM06 (Excessive Agency), ASI02 (Tool Misuse), MITRE ATLAS AML.T0053
**Compliance relevance**: SOC2 CC9.2 (Vendor Risk), NIST AI RMF MAP-4.1, EU AI Act Art 15
**Last reviewed**: 2026-05-12
**Maintainer**: <set-during-init>

## Recognition

Symptoms that indicate this scenario:

- MCP server responses contain injection patterns (see prompt-injection
  playbook for patterns)
- MCP server returns data that shouldn't be in scope for the tool
- MCP server makes unexpected outbound connections (verifiable via
  network monitoring)
- MCP server requests elevated permissions on update
- MCP server's signature verification fails
- Maintainer of MCP server account compromised (reported by upstream)
- Sudden behavior change in MCP server after a routine update
- Audit log shows MCP responses triggering downstream agent actions
  the user didn't request

Definitive confirmation:

- Network traces show MCP server contacting unexpected endpoints
- Hash of installed MCP server binary doesn't match published hash
- Maintainer publishes a security advisory
- Code review of MCP server source reveals malicious patterns

Not this scenario if:

- MCP server is broken (returning errors, malformed responses) but
  not malicious — that's a vendor support issue
- A specific tool call failed but other calls work — likely API
  issue, not compromise
- The user disabled the server expecting it not to work — operator
  error

## Immediate Containment (0-15 minutes)

This is a critical-severity scenario. Speed matters because:
1. A compromised MCP server may be exfiltrating data
2. Other concurrent sessions may be affected
3. The compromise may spread if not isolated

1. **Disconnect the MCP server.** Remove from active connections
   across all sessions, immediately. Don't wait to investigate.

       # Claude Code: edit .mcp.json to remove the server entry
       # Or: claude mcp disable <server-name>
       # Restart the framework to apply

2. **Block at network layer.** If you control egress, block the
   MCP server's domain and any endpoints it's known to contact.

       # Quick block in /etc/hosts (Linux/macOS)
       echo "0.0.0.0 mcp-server.example.com" | sudo tee -a /etc/hosts

3. **Identify all systems running this MCP server.** If shared
   team-wide, notify everyone immediately to disconnect.

4. **Snapshot the audit log.** Preserve evidence of what the MCP
   server has been doing.

       cp ~/.local/state/<framework>/audit.jsonl \
          ./incident-$(date +%Y%m%d-%H%M%S)-audit.jsonl

5. **Inventory affected sessions.** All sessions that connected to
   this MCP server since last known-good state.

       jq 'select(.event_type=="mcp_call") | .session_id' \
          ./incident-*.jsonl | sort -u

6. **Rotate any credentials the server had access to.** If the MCP
   server stored API tokens, OAuth credentials, or other secrets,
   assume they're compromised. Rotate.

## Investigation (15-60 minutes)

1. **Determine the compromise vector.**

   - **Supply chain attack**: malicious code introduced upstream
     (npm/PyPI compromise, GitHub account takeover, build pipeline
     compromise)
   - **Live exploitation**: server was legitimate but is being
     actively exploited (vulnerable dependency, exposed admin
     interface)
   - **Insider**: compromise by maintainer's own action (rare;
     check maintainer's public statements)
   - **Accidental**: well-intentioned change introduced data leakage
     or injection (not malicious but still requires response)

2. **Scope assessment.** What did the MCP server have access to?

   - File system paths the server could read/write
   - Credentials the server held
   - Other services the server could call
   - Data the server transmitted

3. **Forensic analysis.** Capture and analyze:

   - The MCP server's response history from audit log
   - Network connections initiated by the server (if logged)
   - Any local file changes made by the server
   - Any external API calls the server triggered

4. **Look for indicators of compromise** in agent sessions that
   used the server:

   - Agents that took actions outside their normal scope
   - Outputs containing data from outside the user's working
     directory
   - Tool calls to endpoints the user didn't authorize

Questions to answer:

- When did the compromise begin? (last known-good version)
- What data could have been exfiltrated?
- Are other MCP servers from the same source also at risk?
- Is this a targeted attack or opportunistic supply chain hit?
- What credentials need rotation?

## Remediation (varies)

1. **Wait for upstream advisory.** Don't reinstall until upstream
   publishes a clean version or confirms the issue. Reinstalling
   the same version recreates the problem.

2. **Remove all artifacts.** Delete the MCP server installation
   entirely, including caches:

       # Filesystem locations vary by platform
       rm -rf ~/.local/share/<mcp-server>
       rm -rf ~/.cache/<mcp-server>
       rm -rf ~/.config/<mcp-server>

       # If installed via package manager
       npm uninstall -g <mcp-server-package>
       # or
       pip uninstall <mcp-server-package>

3. **Audit local state.** Look for files the MCP server may have
   modified or planted:

       # Files created/modified during the suspect time window
       find ~/.local ~/.config -newer ./last-known-good-date \
            -type f 2>/dev/null

4. **Rotate all credentials.** Comprehensive rotation of:
   - API tokens the MCP server accessed
   - SSH keys (if compromise included system access)
   - OAuth refresh tokens
   - Database credentials
   - Cloud provider credentials

5. **Find a replacement** if the MCP server is essential. Look for
   alternatives, vetted forks, or in-house implementation.

6. **Verify replacement** before reconnecting:
   - Check published signature against installed binary
   - Review source if open-source
   - Verify maintainer authenticity
   - Pin to specific version (no auto-update)

Verification:

- New MCP server's behavior matches expected scope
- Audit log shows clean call patterns
- Network monitoring confirms no unexpected connections
- Rotated credentials work; old credentials revoked

## Hardening (post-incident)

1. **MCP server allowlist.** Maintain a vetted list of approved
   MCP servers. Anything not on the list requires explicit
   approval to connect.

2. **Signature verification.** Verify MCP server signatures before
   each connection. Cosign/Sigstore where supported; otherwise
   maintained hash list.

3. **Network egress monitoring.** Capture outbound connections
   per MCP server. Anomalies trigger alerts.

4. **Sandbox MCP servers.** Run each MCP server in an isolated
   environment with minimum filesystem access:

       # Example: Lima/nerdctl container
       limactl start --name=mcp-sandbox
       nerdctl run --rm -v /specific/path:/data:ro <mcp-server>

5. **Pin MCP server versions.** No auto-update for production
   workflows. Updates require:
   - Review of release notes
   - Signature verification of new version
   - Testing in isolated environment first

6. **Audit log MCP responses.** Capture MCP server responses (with
   appropriate redaction per audit-envelope.md). Enables forensic
   analysis if compromise discovered later.

7. **Supply chain provenance.** Track which MCP servers are
   installed, from what source, at what version. SBOM-like
   inventory. Generate provenance attestations for builds.

## Compliance Evidence

Artifacts to capture:

- Compromised MCP server binary/source (preserve indefinitely)
- Network traces showing malicious activity
- Audit log entries from compromise window
- Affected sessions list
- Credential rotation log (timestamps, credentials rotated)
- Communication with upstream maintainer (if applicable)
- ADRs documenting allowlist and signature verification adoption

Required notifications:

- **Internal security team**: yes, critical incident
- **Affected colleagues**: if MCP server was shared team-wide
- **Customer notification**: if customer data may have been
  exfiltrated, per applicable breach notification laws
- **Upstream maintainer**: report the compromise (if not already
  known)
- **Vulnerability databases**: consider CVE filing if you discovered
  the compromise (especially for in-house identified issues)
- **EU AI Act Article 73 serious incident**: if MCP server affected
  a high-risk AI system

## References

- OWASP LLM03: https://genai.owasp.org/llmrisk/llm03-supply-chain/
- MITRE ATLAS AML.T0053: https://atlas.mitre.org/techniques/AML.T0053
- MCP specification: https://modelcontextprotocol.io
- Sigstore: https://www.sigstore.dev
- SLSA framework: https://slsa.dev
- Related playbooks:
  [prompt-injection-detected.md](./prompt-injection-detected.md),
  [unauthorized-agent-action.md](./unauthorized-agent-action.md)

## Revision history

    2026-05-12: Initial playbook authored.
