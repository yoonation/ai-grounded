<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 Myoung Hong -->

# tooling/eject

Exports a consumer's application as a standalone tree with the governance
framework stripped. Never mutates the consumer; the export is a repeatable
build into an output directory, so a fresh standalone cut can follow every
framework or application change.

    uv run --no-project python tooling/eject/eject.py --template ~/lab/ai-grounded --consumer . --out dist/standalone

Ships application files plus consumer-filled scaffold, minus the manifest's
`eject.exclude` globs. Strips everything classified framework or substrate.

Verification (findings exit 2, export left in place for inspection):

1. Reference scan: no exported file may mention a framework path except
   files matching `eject.allow-references` in `sync-manifest.yaml`.
2. Marker scan: no exported file may carry a template-managed marker.
3. Proof gate: printed always, executed with `--run-proof`:
   `pnpm install --frozen-lockfile`, `pnpm run build`,
   `pnpm run typecheck`, `pnpm run test:unit` inside the export. The eject
   is not done until the standalone tree passes its own suite.

## Tests

    python3 tooling/eject/test_eject.py
