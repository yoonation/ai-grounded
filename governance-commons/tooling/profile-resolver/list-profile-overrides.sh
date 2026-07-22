#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
#
# list-profile-overrides.sh
#
# Reference implementation of profile-resolver step 3, single-profile scope
# (illustrative; read-only analysis of substrate content; NOT a maintained
# substrate runtime). Lists every control-id a profile alters together with
# the profile-severity-override it sets, as tab-separated lines:
#
#   <control-id>    <profile-severity-override>
#
# Whole-chain flattening (following the parent profile import and merging the
# baseline selection) is documented in README.md and is intentionally not
# implemented here. This script performs no network access.
#
# bash 3.2 compatible. No associative arrays, no mapfile, no process
# substitution. Depends on awk, sed, grep, coreutils.
#
# Usage:
#   ./list-profile-overrides.sh PROFILE_FILE
#   ./list-profile-overrides.sh ../../profiles/financial-services.oscal.yaml

set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: list-profile-overrides.sh PROFILE_FILE" >&2
  exit 2
fi
PROFILE="$1"
if [ ! -f "$PROFILE" ]; then
  echo "profile-resolver: profile not found: $PROFILE" >&2
  exit 1
fi

# Walk the alters block: track the most recent control-id, and when a
# profile-severity-override value appears under it, emit the pair. awk keeps
# the last-seen control-id and prints on the matching override line.
awk '
  /^[[:space:]]*-[[:space:]]*control-id:[[:space:]]*/ {
    cid = $0
    sub(/.*control-id:[[:space:]]*/, "", cid)
    gsub(/"/, "", cid)
    gsub(/[[:space:]]/, "", cid)
    next
  }
  /name:[[:space:]]*profile-severity-override[[:space:]]*$/ { want = 1; next }
  want && /value:[[:space:]]*/ {
    val = $0
    sub(/.*value:[[:space:]]*/, "", val)
    gsub(/"/, "", val)
    gsub(/[[:space:]]/, "", val)
    if (cid != "" && val != "") printf "%s\t%s\n", cid, val
    want = 0
  }
' "$PROFILE"

count="$(grep -c 'name: profile-severity-override' "$PROFILE" || true)"
echo "profile-resolver: $PROFILE declares $count severity override(s)" >&2
