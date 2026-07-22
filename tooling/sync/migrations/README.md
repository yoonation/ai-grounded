<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# Sync migrations

Executable steps for consumer changes a file copy cannot express (a
structured rewrite inside a consumer-owned file, a rename with content
transform, a one-time cleanup). The sync tool runs each `NNN-name.py` here
once per consumer, oldest first, during `pull`, and records the applied set
in the consumer's `.template-sync/state.json`.

Contract per migration:

- Filename `NNN-short-name.py`, zero-padded ordinal, immutable once shipped.
- Defines `apply(consumer_root, template_root)` taking two `pathlib.Path`
  arguments and returning a short status string.
- Idempotent: running twice must be a no-op the second time. The runner
  guards with state, but a restored or hand-edited state file must not make
  a rerun destructive.
- Consumer-writes only; the template is read-only input.

None are shipped yet; the directory establishes the mechanism.
