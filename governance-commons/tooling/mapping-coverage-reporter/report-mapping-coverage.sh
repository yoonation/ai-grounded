#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
#
# report-mapping-coverage.sh
#
# Reference implementation of mapping-coverage-reporter steps 1 and 2
# (illustrative; read-only analysis of substrate content; NOT a maintained
# substrate runtime). For a single mapping file, reports the relation count,
# distinct source items addressed, distinct target concerns, and explicit
# coverage-gap entry count.
#
# The source-catalog silent-gap diff (step 3) is documented in README.md and
# is intentionally not implemented here. This script performs no network
# access.
#
# bash 3.2 compatible. No associative arrays, no mapfile, no process
# substitution. Depends on grep, sed, sort, coreutils.
#
# Usage:
#   ./report-mapping-coverage.sh MAPPING_FILE
#   ./report-mapping-coverage.sh ../../mappings/owasp-llm-to-concerns.oscal.yaml

set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: report-mapping-coverage.sh MAPPING_FILE" >&2
  exit 2
fi
MAP="$1"
if [ ! -f "$MAP" ]; then
  echo "mapping-coverage-reporter: mapping not found: $MAP" >&2
  exit 1
fi

relations="$(grep -cE '^[[:space:]]*source-rule:' "$MAP" || true)"

sources="$(grep -E '^[[:space:]]*source-rule:' "$MAP" \
  | sed 's/.*source-rule:[[:space:]]*//; s/"//g; s/[[:space:]]//g' \
  | sort -u | wc -l | tr -d '[:space:]')"

concerns="$(grep -E '^[[:space:]]*target-rule:' "$MAP" \
  | sed 's/.*target-rule:[[:space:]]*//; s/"//g; s/\..*//; s/[[:space:]]//g' \
  | sort -u | wc -l | tr -d '[:space:]')"

gaps="$(grep -ciE 'coverage-gap' "$MAP" || true)"

echo "mapping: $(basename "$MAP")"
echo "  relations:               $relations"
echo "  distinct source items:   $sources"
echo "  distinct target concerns:$concerns"
echo "  coverage-gap mentions:   $gaps"
echo "  (silent-gap diff against the source catalog is the documented extension point; see README.md)"
