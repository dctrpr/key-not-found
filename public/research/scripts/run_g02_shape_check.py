#!/usr/bin/env python3
"""Check literal shape reachability for the frozen G02 stencil languages."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True

from g02_reading_model import (
    MODES, ORDERS, SELECTORS, layers, load_model, private_dir, project,
    require, verify_inputs, write_private,
)

DICTIONARY = "scripts/batch20_support/english.txt"
SCRIPT = "scripts/run_g02_shape_check.py"
WORK_LIMIT = 2_000_000
FLAT_LIMIT = 256
FORM_ALIASES = {
    "words-spaced": ["words-spaced/exact"],
    "words-joined": ["words-spaced/compacted"],
    "initials": ["initials/exact", "initials/compacted"],
    "finals": ["finals/exact", "finals/compacted"],
}


def check_registration(research, protocol_path, commit, pinned):
    checkout = research.parent.parent
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "Expected full registration commit")
    protocol_rel = protocol_path.relative_to(research).as_posix()
    for rel, expected in {**pinned, protocol_rel: protocol_path.read_bytes()}.items():
        committed = subprocess.check_output(
            ["git", "-C", str(checkout), "show", f"{commit}:public/research/{rel}"])
        require(committed == expected, f"Registered blob differs: {rel}")


def concrete_strings(choices, mode, reverse):
    for path in product(*choices):
        words = [token for token in path if token is not None]
        yield project(words[::-1] if reverse else words, mode)


def run(research, protocol_path, commit, out):
    started = datetime.now(timezone.utc)
    protocol, pinned = verify_inputs(research, protocol_path)
    require(protocol["testId"] == "g02-stencil-literal-shape-reachability", "Wrong protocol")
    require(protocol["maximumWorkUnitsPerDescriptor"] == WORK_LIMIT and
            protocol["maximumFlatAssignmentsPerDescriptor"] == FLAT_LIMIT, "Changed limits")
    require(SCRIPT in protocol["scriptHashes"], "Unpinned runner")
    check_registration(research, protocol_path, commit, pinned)
    dictionary = pinned[DICTIONARY].decode("ascii").splitlines()
    require(len(dictionary) == len(set(dictionary)) == 2048, "Dictionary changed")
    from g02_shape_reachability import Budget, _flat_presence, reading_graph, shape_presence
    import batch20_common as common

    model = load_model(pinned)
    descriptors = []
    counts = Counter()
    scope_counts = {}
    for scope, selector, order, mode in product(model, SELECTORS, ORDERS, MODES):
        choices = layers(model[scope], selector)
        optional = sum(len(layer) == 2 for layer in choices)
        assignments = 2 ** optional
        reverse = order == "reverse"
        graph = reading_graph(choices, mode, reverse)
        shape = shape_presence(graph, dictionary, Budget(WORK_LIMIT))
        flat_agreement = None
        if assignments <= FLAT_LIMIT and shape["complete"]:
            flat = _flat_presence(concrete_strings(choices, mode, reverse), dictionary, common)
            require(flat == shape["presence"], "Flat cross-check disagrees")
            flat_agreement = True
        descriptor = {
            "id": f"{scope}/{selector}/{order}/{mode}", "scope": scope,
            "selector": selector, "order": order, "mode": mode, "aliases": FORM_ALIASES[mode],
            "optionalPositions": optional, "assignmentBound": str(assignments),
            "nodes": graph["nodes"], "flatAgreement": flat_agreement, **shape,
        }
        descriptors.append(descriptor)
        if shape["complete"]:
            present = [kind if isinstance(value, bool) else f"{kind}{length}"
                       for kind, value in shape["presence"].items()
                       for length, found in ([(None, value)] if isinstance(value, bool) else value.items())
                       if found]
            counts.update(present)
            bucket = scope_counts.setdefault(scope, Counter())
            bucket.update(present)
    require(len(descriptors) == 160, "Descriptor population changed")
    require(sum(len(d["aliases"]) for d in descriptors) == 240, "Alias population changed")
    result = {
        "version": 1, "testId": protocol["testId"], "caseStatus": "unsolved",
        "startedAtUTC": started.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "completedAtUTC": datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "registrationCommit": commit, "protocolSha256": sha256(protocol_path.read_bytes()).hexdigest(),
        "counts": {
            "descriptors": len(descriptors),
            "completedDescriptors": sum(d["complete"] for d in descriptors),
            "cappedDescriptors": sum(not d["complete"] for d in descriptors),
            "flatCrossCheckedDescriptors": sum(d["flatAgreement"] is True for d in descriptors),
            "aliases": sum(len(d["aliases"]) for d in descriptors),
        },
        "shapePresentDescriptorCounts": dict(counts),
        "shapePresentByScope": {scope: dict(values) for scope, values in scope_counts.items()},
        "descriptors": descriptors,
        "activity": {"checksums": 0, "derivations": 0, "historyQueries": 0, "walletActions": 0},
    }
    write_private(private_dir(out, research) / "RESULT.json", result)
    print(json.dumps({key: result[key] for key in ("counts", "shapePresentDescriptorCounts", "shapePresentByScope")}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--registration-commit", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.research.resolve(), args.protocol.resolve(), args.registration_commit, args.out)


if __name__ == "__main__":
    main()
