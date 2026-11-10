#!/usr/bin/env python3
"""Restrict frozen G02 word choices to one shared query offset per leaf."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random
import re
import subprocess
import sys

sys.dont_write_bytecode = True

import batch20_geometry as geometry
from g02_joint_source_audit import category, colors_at, partition_axis, rational, rectangles
from g02_reading_model import (
    MEMBERSHIP, PAIRS, SELECTORS, load_model, private_dir, project, require, verify_inputs,
    write_private,
)
from g02_shape_reachability import BASE58, MINIKEY_LENGTHS, WIF_LENGTHS

TEST_ID = "g02-shared-query-sensitivity"
DIRECTORY = "analysis_outputs/continuation_20261110/"
PROTOCOL = DIRECTORY + "g02_shared_query/PROTOCOL.json"
PREVIOUS = DIRECTORY + "g02_shape_reachability/RESULT.json"
ARTICLE_MAP = "analysis_outputs/3d_article_map/article_3d_map_data.json"
DUPLEX = "analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json"
SCRIPT = "scripts/run_g02_shared_query.py"
MODULES = (
    "batch20_geometry", "g02_joint_source_audit", "g02_reading_model",
    "g02_shape_reachability", "global_mirror_dag",
)
FAMILIES = (("wif", frozenset("5KL"), WIF_LENGTHS),
            ("minikey", frozenset("S"), MINIKEY_LENGTHS))
LIMITS = {
    "guardPx": 12,
    "widthPx": 2544,
    "maximumLeafCells": 100_000,
    "maximumVariableEvaluations": 5_000_000,
    "maximumProjectedCharacters": 5_000_000,
}


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def paired_mask_hash(leaves):
    raw = json.dumps(leaves, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("utf-8")).hexdigest()


def relevant_rectangles(origin, slopes, masks, guard):
    """Cull rectangles disjoint from the closed offset box and collect its breakpoints."""
    x, y = origin
    sx, sy = slopes
    active = {"orange": [], "black": []}
    xs, ys = set(), set()
    for color, boxes in masks.items():
        for a, b, c, d in boxes:
            left, right = sorted((sx * (a - x), sx * (c - x)))
            bottom, top = sorted((sy * (b - y), sy * (d - y)))
            if right < -guard or left > guard or top < -guard or bottom > guard:
                continue
            active[color].append((a, b, c, d))
            xs.update(edge for edge in (left, right) if -guard <= edge <= guard)
            ys.update(edge for edge in (bottom, top) if -guard <= edge <= guard)
    return active, xs, ys


def prepare_word(record, forward, masks, width, guard):
    x, y = map(rational, record["centerUprightFloat"])
    require(rational(record["guardPxFloat"]) >= guard, "Shared query leaves the prior guard")
    previous = frozenset(record["classes"])
    require(previous and not record["overlapObserved"], "Prior color state is unresolved")
    for selector, state in record["selectorMembership"].items():
        expected = "must" if previous == {selector} else "optional" if selector in previous else "out"
        require(state == expected, "Prior class-to-membership mismatch")
    if len(previous) == 1:
        return (record["wordId"], previous, None), set(), set()
    # First direction queries c+F*t. Its reciprocal queries c-t.
    y_slope = 1 if forward else -1
    source, source_xs, source_ys = relevant_rectangles(
        (width - x, y), (1, y_slope), masks[record["source"]], guard)
    target, target_xs, target_ys = relevant_rectangles(
        (x, y), (-1, y_slope), masks[record["target"]], guard)
    probes = x, y, y_slope, source, target
    return (record["wordId"], previous, probes), source_xs | target_xs, source_ys | target_ys


def classify_word(word, dx, dy, width):
    _, previous, probes = word
    if probes is None:
        return next(iter(previous))
    x, y, y_slope, source, target = probes
    query_x, query_y = x - dx, y + y_slope * dy
    a = colors_at(width - query_x, query_y, source)
    b = colors_at(query_x, query_y, target)
    require(len(a) <= 1 and len(b) <= 1, "Overlapping colors at a shared query")
    found = category(a[0] if a else 0, b[0] if b else 0)
    require(found in previous, "Shared query escaped the prior joint classification")
    return found


def leaf_masks(directions, masks, width, guard, max_cells, max_evaluations):
    """Enumerate constant-color cells, including all edge and corner cells."""
    require(len(directions) == 2, "A leaf needs exactly two directions")
    xs, ys = {-guard, guard}, {-guard, guard}
    prepared = []
    for i, records in enumerate(directions):
        words = []
        for record in records:
            word, edges_x, edges_y = prepare_word(record, i == 0, masks, width, guard)
            words.append(word)
            xs.update(edges_x)
            ys.update(edges_y)
        prepared.append(words)
    axis_x, axis_y = partition_axis(xs), partition_axis(ys)
    cells = len(axis_x) * len(axis_y)
    variable = sum(word[2] is not None for words in prepared for word in words)
    evaluations = cells * variable
    require(cells <= max_cells and evaluations <= max_evaluations, "Geometry work cap reached")
    states = {selector: set() for selector in SELECTORS}
    # Classify only variable words at each atom, then reconstruct the immutable order.
    layouts = []
    for words in prepared:
        layouts.append([
            (word, next(iter(word[1])) if word[2] is None else None)
            for word in words
        ])
    for dx, dy in product(axis_x, axis_y):
        directions_at_cell = []
        for layout in layouts:
            selected = {selector: [] for selector in SELECTORS}
            for word, fixed in layout:
                state = fixed if fixed is not None else classify_word(word, dx, dy, width)
                if state in selected:
                    selected[state].append(word[0])
            directions_at_cell.append(selected)
        for selector in SELECTORS:
            states[selector].add(tuple(tuple(direction[selector]) for direction in directions_at_cell))
    paired = {selector: sorted(options) for selector, options in states.items()}
    metadata = {
        "xAtoms": len(axis_x), "yAtoms": len(axis_y), "cellCount": cells,
        "variablePositions": variable, "variableEvaluations": evaluations,
        "distinctPairedMasks": {selector: len(options) for selector, options in paired.items()},
    }
    return paired, metadata


def fragment_statistics(text):
    """Summarize marker-started internal and trailing Base58 runs and the prefix."""
    prefix = 0
    trailing = [0] * len(FAMILIES)
    longest = [0] * len(FAMILIES)
    for index, char in enumerate(text):
        if char not in BASE58:
            trailing = [0] * len(FAMILIES)
            continue
        if index == prefix:
            prefix += 1
        for kind, (_, markers, _) in enumerate(FAMILIES):
            if trailing[kind] or char in markers:
                trailing[kind] += 1
                longest[kind] = max(longest[kind], trailing[kind])
    return prefix, tuple(trailing), tuple(longest)


def combine_statistics(first, second=None):
    """For independent whole-fragment options, count syntax across the seam exactly."""
    left_max = tuple(max(row[2][kind] for row in first) for kind in range(len(FAMILIES)))
    if second is None:
        return left_max
    right_prefix = max(row[0] for row in second)
    result = []
    for kind, maximum in enumerate(left_max):
        left_suffix = max(row[1][kind] for row in first)
        right_max = max(row[2][kind] for row in second)
        spanning = left_suffix + right_prefix if left_suffix else 0
        result.append(max(maximum, right_max, spanning))
    return tuple(result)


def check_shape_languages(prior, leaves, token_by_id, char_limit):
    require(prior["testId"] == "g02-stencil-literal-shape-reachability" and
            len(prior["descriptors"]) == prior["counts"]["completedDescriptors"] == 160,
            "Unexpected prior shape receipt")
    leaf_by_scope = {f"{source}-to-{target}": (f"{min(source, target)}-{max(source, target)}", i % 2)
                     for i, (source, target) in enumerate(PAIRS)}
    result = []
    projected = 0
    for desc in prior["descriptors"]:
        require(desc["complete"] and desc["reason"] is None, "Incomplete prior descriptor")
        presence = desc["presence"]
        require(presence["hex64"] is False and not any(presence["bip39"].values()),
                "Prior result needs another recognizer")
        if not any(value for name, _, _ in FAMILIES for value in presence[name].values()):
            continue
        scope, selector, order, mode = (desc[key] for key in ("scope", "selector", "order", "mode"))
        require(selector in ("source-only", "target-only") and order in ("forward", "reverse") and
                mode in ("words-joined", "initials"), "Unexpected syntax-positive scope")
        scopes = ([(leaf, None) for leaf in leaves] if scope == "global" else [leaf_by_scope[scope]])
        if order == "reverse":
            scopes.reverse()
        fragments = []
        for leaf, direction in scopes:
            options = leaves[leaf][selector]
            masks = {paired[direction] if direction is not None else paired[0] + paired[1]
                     for paired in options}
            stats = []
            for mask in sorted(masks):
                words = [token_by_id[word_id] for word_id in mask]
                text = project(words[::-1] if order == "reverse" else words, mode)
                projected += len(text)
                require(projected <= char_limit, "Projection work cap reached")
                stats.append(fragment_statistics(text))
            fragments.append(stats)
        maxima = combine_statistics(*fragments)
        flags = {name: {str(length): maxima[kind] >= length for length in lengths}
                 for kind, (name, _, lengths) in enumerate(FAMILIES)}
        for name, values in flags.items():
            require(all(not found or presence[name][length] for length, found in values.items()),
                    "Restricted language escaped the prior shape result")
        result.append({
            "id": desc["id"], "distinctMasksByFragment": [len(stats) for stats in fragments],
            "priorPresence": {name: presence[name] for name, _, _ in FAMILIES},
            "sharedQueryPresence": flags,
        })
    require(len(result) == 8, "Prior syntax-positive population changed")
    return result, projected


def registration_inputs(research, protocol, commit):
    require(protocol == research / PROTOCOL, "Unexpected registered protocol path")
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "Supply the full registration commit")
    spec, pinned = verify_inputs(research, protocol)
    require(spec["testId"] == TEST_ID and all(spec[key] == val for key, val in LIMITS.items()),
            "Protocol scope or limits changed")
    executing = {SCRIPT: Path(__file__).resolve()}
    executing.update({f"scripts/{name}.py": Path(sys.modules[name].__file__).resolve()
                      for name in MODULES})
    for rel, imported in executing.items():
        require(rel in spec["scriptHashes"] and imported == research / rel
                and imported.read_bytes() == pinned[rel], f"Unpinned executing code: {rel}")
    checkout = research.parent.parent
    prefix = "public/research/"
    for rel, expected in {**pinned, PROTOCOL: protocol.read_bytes()}.items():
        registered = subprocess.check_output(["git", "-C", str(checkout), "show", f"{commit}:{prefix}{rel}"])
        require(registered == expected, f"Git pin differs: {rel}")
    return pinned


def run(research, protocol, commit, out):
    started = utc()
    pinned = registration_inputs(research, protocol, commit)
    model = load_model(pinned)
    words = {identifier: token for identifier, token, _ in model["global"]}
    records = json.loads(pinned[MEMBERSHIP])["wordRecords"]
    masks = {page: rectangles(boxes) for page, boxes in geometry.get_masks(
        json.loads(pinned[ARTICLE_MAP]), json.loads(pinned[DUPLEX])).items()}
    directions = {(a, b): [r for r in records if (r["source"], r["target"]) == (a, b)]
                  for a, b in PAIRS}
    leaves, summary = {}, {}
    remaining = LIMITS["maximumVariableEvaluations"]
    for low, high in PAIRS[::2]:
        key = f"{low}-{high}"
        paired, metadata = leaf_masks(
            [directions[(low, high)], directions[(high, low)]], masks, Fraction(LIMITS["widthPx"]),
            Fraction(LIMITS["guardPx"]), LIMITS["maximumLeafCells"], remaining,
        )
        leaves[key], summary[key] = paired, metadata
        remaining -= metadata["variableEvaluations"]
    require(sum(leaf["variablePositions"] for leaf in summary.values()) == 97, "Prior flags changed")
    prior = json.loads(pinned[PREVIOUS])
    checks, chars = check_shape_languages(prior, leaves, words, LIMITS["maximumProjectedCharacters"])
    present = Counter(name + length for row in checks
                      for name, flags in row["sharedQueryPresence"].items()
                      for length, found in flags.items() if found)
    retained = sum(any(v for group in row["sharedQueryPresence"].values() for v in group.values())
                   for row in checks)
    result = {
        "version": 1, "testId": TEST_ID, "caseStatus": "unsolved", "sharedQueryComplete": True,
        "conditionalQueryModelOnly": True,
        "physicalDisplacementRangeMeasured": False, "startedAtUTC": started, "completedAtUTC": utc(),
        "registrationCommit": commit, "protocolSha256": sha256(protocol.read_bytes()).hexdigest(),
        "priorShapeResultSha256": sha256(pinned[PREVIOUS]).hexdigest(),
        "pairedMaskSha256": paired_mask_hash(leaves), "leaves": summary,
        "counts": {
            "previousSyntaxPositiveLanguages": len(checks), "syntaxPositiveLanguages": retained,
            "excludedPreviouslyPositiveLanguages": len(checks) - retained,
            "previousSyntaxNegativeLanguages": len(prior["descriptors"]) - len(checks),
            "projectedCharactersProcessed": chars, "physicalDisplacementMeasurements": 0,
        },
        "shapePresentDescriptorCounts": dict(present), "languageChecks": checks,
        "activity": {"checksums": 0, "derivations": 0, "historyQueries": 0, "walletActions": 0},
    }
    write_private(private_dir(out, research) / "RESULT.json", result)
    print(json.dumps({"counts": result["counts"], "leaves": summary,
                      "pairedMaskSha256": result["pairedMaskSha256"]}))


def self_test():
    require(__debug__, "Run synthetic controls with assertions enabled")
    empty = {"orange": [], "black": []}
    box = {"orange": [[8, 0, 9, 1]], "black": []}
    active, x, y = relevant_rectangles((Fraction(8), Fraction(1)), (1, -1),
                                       rectangles(box), Fraction(1))
    assert active == rectangles(box) and x == {0, 1} and y == {0, 1}
    assert colors_at(8, 0, active) == [1] and colors_at(9, 0, active) == []
    assert colors_at(8, 1, active) == []
    def record(source, target, identifier, center, selector):
        classes = ["neither", selector]
        return {"source": source, "target": target, "wordId": identifier,
                "centerUprightFloat": center, "guardPxFloat": 1, "classes": classes,
                "overlapObserved": False,
                "selectorMembership": {s: "optional" if s in classes else "out" for s in SELECTORS}}
    a = record(1, 2, "ab", [2, 1], "source-only")
    b = record(2, 1, "ba", [8, 1], "target-only")
    paired, info = leaf_masks([[a], [b]], {1: rectangles(box), 2: rectangles(empty)},
                              Fraction(10), Fraction(1), 100, 100)
    assert paired["source-only"] == [((), ()), (("ab",), ())]
    assert paired["target-only"] == [((), ()), ((), ("ba",))]
    assert paired["same-color"] == [((), ())] and info["variablePositions"] == 2
    reciprocal_masks = {
        1: rectangles({"orange": [[7, 0, 10, 1]], "black": []}),
        2: rectangles({"orange": [[8, 0, 11, 1]], "black": []}),
    }
    b_source = record(2, 1, "ba", [1, 1], "source-only")
    reciprocal, _ = leaf_masks([[a], [b_source]], reciprocal_masks,
                                Fraction(10), Fraction(1), 100, 100)
    assert reciprocal["source-only"] == [((), ()), ((), ("ba",)), (("ab",), ())]
    try:
        leaf_masks([[a], [b]], {1: rectangles(box), 2: rectangles(empty)},
                   Fraction(10), Fraction(1), 1, 1)
    except ValueError as error:
        assert str(error) == "Geometry work cap reached"
    else:
        raise AssertionError("Geometry work cap was ignored")
    first = ["", "!S" + "a" * 12, "K" + "A" * 50 + "!"]
    second = ["a" * 17 + "!", "0", "5" + "a" * 10]
    assert combine_statistics(list(map(fragment_statistics, first)),
                              list(map(fragment_statistics, second))) == (51, 30)
    assert combine_statistics([fragment_statistics(""), fragment_statistics("a" * 40)],
                              [fragment_statistics("b" * 40)]) == (0, 0)
    assert combine_statistics([fragment_statistics("KS!")], [fragment_statistics("a" * 60)]) == (2, 1)
    assert project(["(Écho)", "Beta."], "initials") == "ÉB"
    assert project(["Beta.", "(Écho)"], "words-joined") == "Beta.(Écho)"
    # Compare max-plus concatenation with direct scans of every synthetic pair.
    # The direct loop starts from each marker, unlike the suffix summary.
    rng = random.Random(20261110)
    def fragment():
        return "".join(rng.choices("ASLK5abc!0()", k=rng.randrange(80)))
    def direct_max(text, markers):
        longest = 0
        for start, char in enumerate(text):
            if char not in markers:
                continue
            end = start + 1
            while end < len(text) and text[end] in BASE58:
                end += 1
            longest = max(longest, end - start)
        return longest
    comparisons = 512
    for _ in range(comparisons):
        left = [fragment() for _ in range(rng.randint(1, 5))]
        right = [fragment() for _ in range(rng.randint(1, 5))]
        expected = tuple(max(direct_max(a + b, markers) for a, b in product(left, right))
                         for _, markers, _ in FAMILIES)
        actual = combine_statistics(list(map(fragment_statistics, left)),
                                    list(map(fragment_statistics, right)))
        assert actual == expected
    print(json.dumps({"syntheticControlsPassed": True, "fragmentProductComparisons": comparisons,
                      "reciprocalCouplingControl": True, "targetEvaluations": 0}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--research", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    require(all((args.research, args.protocol, args.registration_commit, args.out)), "Missing run arguments")
    run(args.research.resolve(), args.protocol.resolve(), args.registration_commit, args.out)


if __name__ == "__main__":
    main()
