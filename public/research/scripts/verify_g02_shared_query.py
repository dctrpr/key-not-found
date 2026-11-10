#!/usr/bin/env python3
"""Independent exact offset sweep for paired G02 source selection masks."""

from __future__ import annotations

import argparse
from bisect import bisect_left, bisect_right
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
import math
import os
from pathlib import Path
import random
import re
import subprocess


TEST_ID = "g02-shared-query-sensitivity"
PROTOCOL_PATH = "analysis_outputs/continuation_20261110/g02_shared_query/PROTOCOL.json"
SCRIPT_PATH = "scripts/verify_g02_shared_query.py"
AUDIT = "analysis_outputs/continuation_20261110/g02_joint_color_audit/"
MEMBERSHIP = AUDIT + "MEMBERSHIP.json"
SOURCE_RESULT = AUDIT + "RESULT.json"
SOURCE_REPLAY = AUDIT + "INDEPENDENT_VERIFICATION.json"
SOURCE_REGISTRATION = AUDIT + "REGISTRATION.json"
MAP = "analysis_outputs/3d_article_map/article_3d_map_data.json"
DUPLEX = "analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json"
SHAPE_RESULT = "analysis_outputs/continuation_20261110/g02_shape_reachability/RESULT.json"
REQUIRED_SOURCES = {
    MEMBERSHIP, SOURCE_RESULT, SOURCE_REPLAY, SOURCE_REGISTRATION, MAP, DUPLEX, SHAPE_RESULT,
    "sources/printed-lines.json", "sources/word-geometry-20261110.json",
    "scripts/batch20_support/english.txt",
}
PARAMETERS = {
    "guardPx": 12,
    "widthPx": 2544,
    "maximumLeafCells": 100_000,
    "maximumVariableEvaluations": 5_000_000,
    "maximumProjectedCharacters": 5_000_000,
    "maximumIndependentLeafCells": 500_000,
    "maximumIndependentPairedMasks": 50_000,
}
LEAVES = ((76, 77), (78, 79))
PAIR_COUNTS = (263, 274, 226, 199)
SELECTORS = ("same-color", "opposite-color", "source-only", "target-only")
COLORS = ("orange", "black")
STATES = tuple(product(range(3), repeat=2))
TRUTH = {
    (0, 0): "neither", (0, 1): "target-only", (0, 2): "target-only",
    (1, 0): "source-only", (2, 0): "source-only",
    (1, 1): "same-color", (2, 2): "same-color",
    (1, 2): "opposite-color", (2, 1): "opposite-color",
}


class VerificationError(ValueError):
    """A failed verification with a safe diagnostic."""


class Inconclusive(VerificationError):
    """An overlap or resource cap prevents completeness."""


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def exact(value):
    """Freeze the existing int or binary64 value as a rational."""
    require(not isinstance(value, bool) and isinstance(value, (int, float, Fraction)),
            "Non-numeric coordinate")
    require(not isinstance(value, float) or math.isfinite(value), "Nonfinite coordinate")
    return Fraction(value)


def _frozen_rectangles(masks):
    frozen = {}
    for page, entries in masks.items():
        require(set(entries) == set(COLORS), "Unexpected color channels")
        frozen[page] = {}
        for color in COLORS:
            boxes = []
            for rectangle in entries[color]:
                require(len(rectangle) == 4, "Malformed mask rectangle")
                a, b, c, d = map(exact, rectangle)
                require(a < c and b < d, "Empty mask rectangle")
                boxes.append((a, b, c, d))
            frozen[page][color] = boxes
    return frozen


def _pull_axis(lower, upper, origin, sign):
    """Pull a half-open face interval back through origin + sign * t."""
    if sign == 1:
        return lower - origin, upper - origin, True, False
    return origin - upper, origin - lower, False, True


def _intersects(interval, radius):
    lo, hi, lo_closed, hi_closed = interval
    return ((lo < radius or (lo == radius and lo_closed))
            and (hi > -radius or (hi == -radius and hi_closed)))


def _atoms(cuts):
    points = sorted(cuts)
    reps = [points[0]]
    for left, right in zip(points, points[1:]):
        reps.extend(((left + right) / 2, right))
    return reps


def _span(interval, atoms):
    lo, hi, lo_closed, hi_closed = interval
    start = bisect_left(atoms, lo) if lo_closed else bisect_right(atoms, lo)
    stop = bisect_right(atoms, hi) if hi_closed else bisect_left(atoms, hi)
    return start, stop


def _point_state(x, y, masks):
    hits = [number for number, color in enumerate(COLORS, 1)
            if any(a <= x < c and b <= y < d for a, b, c, d in masks[color])]
    return None if len(hits) > 1 else (hits[0] if hits else 0)


def _paired_ids(bitmask, directions):
    first, second = directions
    return [[identifier for index, identifier in enumerate(first) if bitmask & (1 << index)],
            [identifier for index, identifier in enumerate(second, len(first)) if bitmask & (1 << index)]]


def _sweep(rows, x_count, y_count):
    """Yield four source/target orange/black membership bitsets per atom cell."""
    y_events = defaultdict(list)
    for index, (x0, x1, y0, y1, channel, bit) in enumerate(rows):
        y_events[y0].append((index, True))
        y_events[y1].append((index, False))
    active_rows = set()
    for y in range(y_count):
        for index, start in y_events[y]:
            if start:
                active_rows.add(index)
            else:
                active_rows.remove(index)
        x_events = defaultdict(list)
        for index in active_rows:
            x0, x1, _, _, channel, bit = rows[index]
            x_events[x0].append((channel, bit, 1))
            x_events[x1].append((channel, bit, -1))
        current = [0, 0, 0, 0]
        multiplicity = [dict() for _ in current]
        for x in range(x_count):
            for channel, bit, change in x_events[x]:
                counts = multiplicity[channel]
                count = counts.get(bit, 0) + change
                if count:
                    counts[bit] = count
                    current[channel] |= bit
                else:
                    del counts[bit]
                    current[channel] &= ~bit
            yield tuple(current)


def paired_leaf(records, raw_masks, leaf, *, radius=12, width=2544,
                maximum_cells=500_000, maximum_masks=50_000):
    """Independently compute one leaf's exact paired selector masks."""
    radius, width = exact(radius), exact(width)
    require(radius >= 0 and width > 0, "Invalid offset square")
    require(type(maximum_cells) is int and type(maximum_masks) is int
            and maximum_cells >= 0 and maximum_masks >= 0, "Invalid sweep cap")
    lower, higher = leaf
    directions = ((lower, higher), (higher, lower))
    masks = _frozen_rectangles(raw_masks)
    identifiers = ([], [])
    all_ids = set()
    prior_direction = 0
    cuts_x, cuts_y = {-radius, radius}, {-radius, radius}
    rectangles = []
    allowed_states = dict.fromkeys(STATES, 0)
    required = dict.fromkeys(SELECTORS, 0)
    possible = dict.fromkeys(SELECTORS, 0)
    variable_count = 0

    for index, record in enumerate(records):
        direction = (record["source"], record["target"])
        require(direction in directions, "Word record belongs to a different leaf")
        direction_index = directions.index(direction)
        require(direction_index >= prior_direction, "Leaf direction order changed")
        prior_direction = direction_index
        identifier = record["wordId"]
        require(isinstance(identifier, str) and identifier and identifier not in all_ids,
                "Invalid or duplicate frozen word ID")
        all_ids.add(identifier)
        identifiers[direction_index].append(identifier)
        x, y = map(exact, record["centerUprightFloat"])
        require(exact(record["guardPxFloat"]) >= radius, "Shared square exceeds a frozen word guard")
        states = {tuple(state) for state in record["jointColorStates"]}
        require(states and states <= set(STATES), "Invalid frozen joint-color domain")
        bit = 1 << index
        for state in states:
            allowed_states[state] |= bit
        categories = {TRUTH[state] for state in states}
        variable_count += len(categories) > 1
        expected_membership = {}
        for selector in SELECTORS:
            membership = ("must" if categories == {selector} else
                          "optional" if selector in categories else "out")
            expected_membership[selector] = membership
            if membership == "must":
                required[selector] |= bit
            if membership != "out":
                possible[selector] |= bit
        require(record["selectorMembership"] == expected_membership,
                "Frozen selector domain differs from frozen colors")

        source, target = direction
        nominal = (_point_state(width - x, y, masks[source]), _point_state(x, y, masks[target]))
        if None in nominal:
            raise Inconclusive("Color overlap at zero offset")
        require(nominal in states, "Zero offset escapes the frozen joint-color domain")
        if "nominalColors" in record:
            require(list(nominal) == record["nominalColors"], "Zero offset differs from the frozen nominal colors")

        # A→B uses c + F t. B→A uses c - t. The reflected source x
        # reverses each target x sign. Both sides retain the same y sign.
        y_sign = 1 if direction_index == 0 else -1
        for side, (page, x_origin, x_sign) in enumerate(((source, width - x, 1), (target, x, -1))):
            for color_index, color in enumerate(COLORS):
                for a, b, c, d in masks[page][color]:
                    horizontal = _pull_axis(a, c, x_origin, x_sign)
                    vertical = _pull_axis(b, d, y, y_sign)
                    if not (_intersects(horizontal, radius) and _intersects(vertical, radius)):
                        continue
                    cuts_x.update(edge for edge in horizontal[:2] if -radius <= edge <= radius)
                    cuts_y.update(edge for edge in vertical[:2] if -radius <= edge <= radius)
                    rectangles.append((horizontal, vertical, side * 2 + color_index, bit))

    xs, ys = _atoms(cuts_x), _atoms(cuts_y)
    cell_count = len(xs) * len(ys)
    if cell_count > maximum_cells:
        raise Inconclusive("Independent leaf cell cap exceeded")
    sweep_rows = []
    for horizontal, vertical, channel, bit in rectangles:
        x0, x1 = _span(horizontal, xs)
        y0, y1 = _span(vertical, ys)
        require(x0 < x1 and y0 < y1, "Intersecting rectangle lost its atom")
        sweep_rows.append((x0, x1, y0, y1, channel, bit))

    population = (1 << len(records)) - 1
    outcomes = {selector: set() for selector in SELECTORS}
    for source_o, source_b, target_o, target_b in _sweep(sweep_rows, len(xs), len(ys)):
        if source_o & source_b or target_o & target_b:
            raise Inconclusive("A shared offset has a two-color overlap")
        source_any, target_any = source_o | source_b, target_o | target_b
        source_states = (population ^ source_any, source_o, source_b)
        target_states = (population ^ target_any, target_o, target_b)
        for a, b in STATES:
            require(not (source_states[a] & target_states[b] & ~allowed_states[a, b]),
                    "Shared offset escapes a frozen joint-color domain")
        selected = (
            (source_o & target_o) | (source_b & target_b),
            (source_o & target_b) | (source_b & target_o),
            source_any & ~target_any,
            target_any & ~source_any,
        )
        for selector, chosen in zip(SELECTORS, selected):
            require(not (required[selector] & ~chosen) and not (chosen & ~possible[selector]),
                    "Shared offset escapes a frozen selector domain")
            outcomes[selector].add(chosen)
            if len(outcomes[selector]) > maximum_masks:
                raise Inconclusive("Independent paired-mask cap exceeded")

    paired = {selector: sorted(_paired_ids(value, identifiers) for value in outcomes[selector])
              for selector in SELECTORS}
    return paired, {
        "cellCount": cell_count, "xAtoms": len(xs), "yAtoms": len(ys),
        "wordPositions": [len(ids) for ids in identifiers],
        "variablePositions": variable_count,
        "distinctPairedMasks": {selector: len(paired[selector]) for selector in SELECTORS},
    }


def paired_digest(leaves):
    return digest(json.dumps(leaves, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def _test_record(source, target, identifier, x, y):
    return {"source": source, "target": target, "wordId": identifier,
            "centerUprightFloat": [x, y], "guardPxFloat": 3,
            "jointColorStates": [list(state) for state in STATES],
            "selectorMembership": dict.fromkeys(SELECTORS, "optional")}


def _half_grid_oracle(records, masks, width, radius):
    """Direct integer/half-integer coordinate oracle for synthetic fixtures."""
    sets = {selector: set() for selector in SELECTORS}

    def hit(x2, y2, boxes):
        return any(2 * a <= x2 < 2 * c and 2 * b <= y2 < 2 * d for a, b, c, d in boxes)

    offsets = range(-2 * radius, 2 * radius + 1)
    for tx2, ty2 in product(offsets, repeat=2):
        current = {selector: ([], []) for selector in SELECTORS}
        for record in records:
            source, target = record["source"], record["target"]
            x, y = record["centerUprightFloat"]
            forward = source < target
            target_x2, y2 = 2 * x - tx2, 2 * y + (ty2 if forward else -ty2)
            source_x2 = 2 * width - target_x2
            so = hit(source_x2, y2, masks[source]["orange"])
            sb = hit(source_x2, y2, masks[source]["black"])
            to = hit(target_x2, y2, masks[target]["orange"])
            tb = hit(target_x2, y2, masks[target]["black"])
            if (so and sb) or (to and tb):
                return None
            category = TRUTH[int(so) + 2 * int(sb), int(to) + 2 * int(tb)]
            if category in current:
                current[category][0 if forward else 1].append(record["wordId"])
        for selector, pair in current.items():
            sets[selector].add(tuple(tuple(ids) for ids in pair))
    return {selector: [[list(a), list(b)] for a, b in sorted(sets[selector])] for selector in SELECTORS}


def self_test():
    require(__debug__, "Synthetic controls require assertions enabled")
    records = [_test_record(1, 2, "first", 5, 1), _test_record(2, 1, "second", 5, 1)]
    masks = {page: {"orange": [[0, 1, 10, 3]], "black": []} for page in (1, 2)}
    paired, stats = paired_leaf(records, masks, (1, 2), radius=1, width=10)
    assert paired == _half_grid_oracle(records, masks, 10, 1)
    assert paired["same-color"] == [[[], ["second"]], [["first"], []], [["first"], ["second"]]]
    assert stats["distinctPairedMasks"]["same-color"] == 3

    # A singleton at the closed guard edge must survive the reversed x bound.
    endpoint = [_test_record(1, 2, "edge", 5, 1)]
    endpoint_masks = {1: {"orange": [], "black": []},
                      2: {"orange": [[6, 0, 7, 2]], "black": []}}
    paired, _ = paired_leaf(endpoint, endpoint_masks, (1, 2), radius=1, width=10)
    assert paired["target-only"] == [[[], []], [["edge"], []]]
    assert paired == _half_grid_oracle(endpoint, endpoint_masks, 10, 1)

    # Fraction arithmetic keeps a binary64 boundary that float subtraction
    # would round onto its neighboring color.
    edge = [_test_record(1, 2, "binary", 0.1, 0.0)]
    binary_masks = {1: {"orange": [[0, -1, 0.9, 1]], "black": [[0.9, -1, 2, 1]]},
                    2: {"orange": [[0, -1, 2, 1]], "black": []}}
    paired, _ = paired_leaf(edge, binary_masks, (1, 2), radius=0, width=1)
    assert paired["same-color"] == [[["binary"], []]]
    assert paired["opposite-color"] == [[[], []]]

    rng = random.Random(20261111)
    palette = [[0, 0, 2, 2], [1, 1, 4, 4], [2, 0, 5, 3], [3, -1, 7, 2]]
    successful = rejected_overlaps = 0
    for _ in range(150):
        toy_masks = {page: {color: rng.sample(palette, rng.randint(0, 2)) for color in COLORS}
                     for page in (1, 2)}
        toy_records = [_test_record(a, b, f"toy{a}-{i}", rng.randrange(1, 6), rng.randrange(0, 4))
                       for a, b in ((1, 2), (2, 1)) for i in range(2)]
        expected = _half_grid_oracle(toy_records, toy_masks, 6, 2)
        try:
            actual, _ = paired_leaf(toy_records, toy_masks, (1, 2), radius=2, width=6)
        except Inconclusive:
            assert expected is None
            rejected_overlaps += 1
        else:
            assert expected is not None and actual == expected
            successful += 1
    assert successful > 0 and rejected_overlaps > 0

    for cap in ({"maximum_cells": 0}, {"maximum_masks": 1}):
        try:
            paired_leaf(records, masks, (1, 2), radius=1, width=10, **cap)
        except Inconclusive:
            pass
        else:
            raise AssertionError("Incomplete sweep accepted as complete")

    narrowed = dict(records[0], jointColorStates=[[0, 0]],
                    selectorMembership=dict.fromkeys(SELECTORS, "out"))
    try:
        paired_leaf([narrowed, records[1]], masks, (1, 2), radius=1, width=10)
    except VerificationError:
        pass
    else:
        raise AssertionError("A position escaped its frozen domain")
    return {"passed": True, "halfGridCases": successful + rejected_overlaps + 2,
            "matchingCompleteMasks": successful + 2, "rejectedOverlapCases": rejected_overlaps,
            "binaryEndpointControl": True, "correlatedPairControl": True,
            "capsFailClosed": True, "targetInputsRead": False, "targetEvaluation": False}


def _mask_pages(model, duplex):
    masks = {}
    for page in model["pages"]:
        number = page["page"]
        if number not in (76, 77, 78, 79):
            continue
        require(number not in masks, "Duplicate source mask page")
        orange = []
        for highlight in page["highlights"]:
            if number == 79 and int(highlight["id"].rsplit("_", 1)[1]) >= 6:
                continue
            orange.append(highlight["box"])
        masks[number] = {"orange": orange, "black": duplex["boxes"].get(str(number), [])}
    require(set(masks) == {76, 77, 78, 79}, "Missing source mask page")
    return masks


def _verified_bytes(research, protocol_path, commit):
    require(re.fullmatch(r"[a-f0-9]{40}", commit) is not None, "Expected full registration commit")
    require(protocol_path == research / PROTOCOL_PATH, "Unexpected registered protocol path")
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    require(protocol["testId"] == TEST_ID, "Wrong protocol identifier")
    require(all(type(protocol.get(name)) is int and protocol[name] == value
                for name, value in PARAMETERS.items()), "Registered model or caps differ")
    sources, scripts = protocol["sourceHashes"], protocol["scriptHashes"]
    require(REQUIRED_SOURCES <= set(sources) and SCRIPT_PATH in scripts,
            "Missing required source or verifier pins")
    require(not set(sources) & set(scripts) and PROTOCOL_PATH not in sources and PROTOCOL_PATH not in scripts,
            "Overlapping protocol pins")
    checkout = research.parent.parent
    require(research == checkout / "public/research", "Unexpected checkout layout")
    pinned = {PROTOCOL_PATH: protocol_bytes}
    for name, expected in {**sources, **scripts}.items():
        require(isinstance(name, str) and all(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", part)
                                              for part in name.split("/")), "Invalid pin path")
        require(isinstance(expected, str) and re.fullmatch(r"[a-f0-9]{64}", expected), "Invalid pin digest")
        file = (research / name).resolve()
        require(file.is_relative_to(research), "Pinned path escapes the research tree")
        content = file.read_bytes()
        require(digest(content) == expected, f"Current file differs from pin: {name}")
        pinned[name] = content
    require(digest(Path(__file__).read_bytes()) == scripts[SCRIPT_PATH], "Executing verifier differs from its pin")
    for name, expected in pinned.items():
        registered = subprocess.check_output(
            ["git", "-C", str(checkout), "show", f"{commit}:public/research/{name}"],
            stderr=subprocess.DEVNULL,
        )
        require(registered == expected, f"Registered blob differs: {name}")
    return protocol, pinned, digest(protocol_bytes)


def _bound_inventory(pinned):
    inventory, source_result, replay, registration = (json.loads(pinned[name]) for name in (
        MEMBERSHIP, SOURCE_RESULT, SOURCE_REPLAY, SOURCE_REGISTRATION
    ))
    membership_sha = digest(pinned[MEMBERSHIP])
    require(source_result["sourceModelComplete"] is True
            and source_result["inventory"]["sha256"] == membership_sha,
            "Prior result does not bind a complete membership inventory")
    require(replay["verificationPassed"] is True and replay["allOrderedMetadataFieldsMatch"] is True
            and replay["primaryInventorySha256"] == membership_sha
            and replay["primaryResultSha256"] == digest(pinned[SOURCE_RESULT])
            and replay["registrationReceiptSha256"] == digest(pinned[SOURCE_REGISTRATION]),
            "Prior independent receipt does not bind the source artifacts")
    require(registration["registrationCommit"] == source_result["registrationCommit"] == replay["registrationCommit"]
            and replay["pairs"] == source_result["pairs"]
            and replay["globalSelectors"] == source_result["globalSelectors"],
            "Prior source verification scope differs")
    directions = [pair for a, b in LEAVES for pair in ((a, b), (b, a))]
    require(inventory["definition"]["pairs"] == [list(pair) for pair in directions]
            and inventory["definition"]["selectors"] == list(SELECTORS), "Frozen source directions differ")
    records = inventory["wordRecords"]
    require(len(records) == sum(PAIR_COUNTS) and len({record["wordId"] for record in records}) == len(records),
            "Frozen word position population differs")
    offset = 0
    groups = []
    for direction, count in zip(directions, PAIR_COUNTS):
        group = records[offset:offset + count]
        require(all((record["source"], record["target"]) == direction and "nominalColors" in record
                    for record in group), "Frozen directed order differs")
        require(min(exact(record["guardPxFloat"]) for record in group) == PARAMETERS["guardPx"],
                "Frozen direction guard minimum differs")
        groups.append(group)
        offset += count
    return {leaf: groups[index * 2] + groups[index * 2 + 1] for index, leaf in enumerate(LEAVES)}


def _private_path(path, research):
    raw = path.expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    resolved = raw.resolve()
    checkout = research.parent.parent
    seen = [raw, Path(os.path.abspath(raw)), resolved, *(parent.resolve() for parent in raw.parents)]
    require(all(not candidate.is_relative_to(checkout)
                and "public" not in {part.lower() for part in candidate.parts} for candidate in seen),
            "Output must be outside Site and public paths")
    require(not raw.exists() and not raw.is_symlink() and resolved.parent.is_dir(),
            "Output must be fresh with an existing private parent")
    return resolved


def verify(research, protocol_path, registration_commit, primary_path, output_path):
    started = utc()
    controls = self_test()
    research = research.resolve()
    output = _private_path(output_path, research)
    protocol, pinned, protocol_sha = _verified_bytes(research, protocol_path.resolve(), registration_commit)
    primary_bytes = primary_path.read_bytes()
    primary = json.loads(primary_bytes)
    require(primary["sharedQueryComplete"] is True and primary["testId"] == TEST_ID
            and primary["registrationCommit"] == registration_commit
            and primary["protocolSha256"] == protocol_sha, "Primary shared-query result is incomplete or unbound")
    grouped = _bound_inventory(pinned)
    masks = _mask_pages(json.loads(pinned[MAP]), json.loads(pinned[DUPLEX]))
    leaves, summaries = {}, {}
    for leaf, records in grouped.items():
        label = f"{leaf[0]}-{leaf[1]}"
        leaves[label], summaries[label] = paired_leaf(
            records, masks, leaf, radius=protocol["guardPx"], width=protocol["widthPx"],
            maximum_cells=protocol["maximumIndependentLeafCells"],
            maximum_masks=protocol["maximumIndependentPairedMasks"],
        )
    paired_sha = paired_digest(leaves)
    require(paired_sha == primary["pairedMaskSha256"], "Complete paired selector mask digests differ")
    require(set(primary["leaves"]) == set(summaries), "Primary leaf set differs")
    for label, summary in summaries.items():
        saved = primary["leaves"][label]
        require(type(saved["cellCount"]) is int and 0 < saved["cellCount"] <= protocol["maximumLeafCells"],
                "Primary leaf cell count exceeds its registered cap")
        require(saved["distinctPairedMasks"] == summary["distinctPairedMasks"],
                "Primary paired mask counts differ")

    receipt = {
        "version": 1, "testId": TEST_ID, "startedAtUTC": started, "completedAtUTC": utc(),
        "registrationCommit": registration_commit, "protocolSha256": protocol_sha,
        "sourceHashes": protocol["sourceHashes"], "scriptHashes": protocol["scriptHashes"],
        "primaryResultSha256": digest(primary_bytes), "pairedMaskSha256": paired_sha,
        "verificationPassed": True, "sharedQueryComplete": True, "completePairedMaskAgreement": True,
        "leaves": summaries, "controls": controls,
        "activity": {"rawReadings": 0, "shapeTests": 0, "checksums": 0, "derivations": 0,
                     "historyQueries": 0, "walletActions": 0, "networkQueries": 0},
        "limits": ["The independent sweep may partition stable regions more finely than the primary.",
                   "The receipt covers paired masks inside the registered conditional shared-query model.",
                   "No projected strings or shape decisions were evaluated by this verifier."],
    }
    output.mkdir(mode=0o700)
    output.chmod(0o700)
    file = output / "INDEPENDENT_VERIFICATION.json"
    with os.fdopen(os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as handle:
        os.fchmod(handle.fileno(), 0o600)
        json.dump(receipt, handle, indent=2, allow_nan=False)
        handle.write("\n")
    return {"verificationPassed": True, "pairedMaskSha256": paired_sha, "leaves": summaries}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--research", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--primary-result", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    target = (args.research, args.protocol, args.registration_commit, args.primary_result, args.out)
    if args.self_test:
        if any(value is not None for value in target):
            parser.error("Self-test accepts no target inputs")
        print(json.dumps(self_test(), sort_keys=True))
        return
    if not all(target):
        parser.error("Supply all registered target arguments or use --self-test")
    try:
        result = verify(*target)
    except Inconclusive as error:
        parser.exit(1, f"Inconclusive: {error}\n")
    except VerificationError as error:
        parser.exit(1, f"Verification failed: {error}\n")
    except (OSError, KeyError, TypeError, ValueError, subprocess.CalledProcessError):
        parser.exit(1, "Verification failed while checking registered files or source metadata\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
