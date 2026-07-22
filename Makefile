# Governance Commons tasks. Uses uv (PEP 723 inline deps); Nix-friendly.
PY := uv run

.PHONY: gc-validate gc-assemble gc-check gc-toolchain-audit gc-generate-floor
gc-validate:
	$(PY) governance-commons/tooling/assemble/validate.py

gc-assemble:
	$(PY) governance-commons/tooling/assemble/assemble.py

gc-toolchain-audit:
	$(PY) governance-commons/tooling/toolchain/manage.py audit

gc-generate-floor:
	$(PY) governance-commons/tooling/floor-generator/generate.py --stack python typescript terraform alerting --out governance-commons/tooling/floor-generator/example-output

gc-check: gc-validate gc-assemble
