#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Myoung Hong
"""
references.py - shared reference-resolution primitive.

Several tools do the same thing: take declarations that name a target, and check
the target actually exists. The consistency gate (IMP-1) checks that a done task's
named file exists on disk. The manifest validator checks that each checkpoint's
referenced constitution article, agent, file, and catalog exists. That is the same
shape repeated, a declared edge (source names target) and a check on whether the
target resolves, so per the constitution's rule-of-three (II.2.5, abstract on the
third occurrence) it is extracted here.

This is reference resolution, not graph validation: it detects dangling edges
(a named target that does not exist). It deliberately does NOT do cycle detection
or traversal, because the artifacts it serves have no such structure; naming it
"graph validation" would overstate it.

`find_dangling` is pure: callers inject the resolvers, so it is testable without
touching disk. A kind with no resolver is returned as `unresolvable` rather than
silently passing, so the caller can decide to skip loudly (e.g. a substrate
catalog layout that is not present) instead of pretending the edge was checked.
Absence of a resolver is never treated as success.
"""

from __future__ import annotations


def find_dangling(edges, resolvers):
    """
    edges: iterable of (source, target, kind).
    resolvers: {kind: callable(target) -> bool}.

    Returns {"dangling": [...], "unresolvable": [...]}, each item
    {"source", "target", "kind"}:
      - dangling: a resolver exists for the kind and returned False (target missing).
      - unresolvable: no resolver for the kind; the caller decides how to surface it
        (typically a loud skip), never a silent pass.
    """
    dangling, unresolvable = [], []
    for source, target, kind in edges:
        fn = resolvers.get(kind)
        if fn is None:
            unresolvable.append({"source": source, "target": target, "kind": kind})
        elif not fn(target):
            dangling.append({"source": source, "target": target, "kind": kind})
    return {"dangling": dangling, "unresolvable": unresolvable}
