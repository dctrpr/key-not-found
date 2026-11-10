#!/usr/bin/env python3
"""Independent verification of registered G02 source metadata.

``--self-test`` uses finite synthetics. ``--verify`` checks a registered corpus
and compares the ordered metadata records using an independent implementation.

Partition construction: every mask edge that falls inside the closed guard
domain becomes an endpoint cell. Each intervening open band has an exact
rational midpoint representative. Cartesian products cover all cells, including
zero-area edge/point cells; predicates are constant on each open cell. Source
membership is always evaluated in ORIGINAL source boxes at (width-x, y).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


COLORS = ("orange", "black")
COLOR_STATES = {None: 0, "orange": 1, "black": 2}
CLASS_NAMES = frozenset(
    ("same-color", "opposite-color", "source-only", "target-only", "neither")
)
PAIRS = ((76, 77), (77, 76), (78, 79), (79, 78))
SELECTORS = ("same-color", "opposite-color", "source-only", "target-only")
MEMBERSHIP_STATES = ("must", "optional", "out", "unresolved")
RAW_SOURCE_PINS = {
    "sources/printed-lines.json": "c3b03304e932e52cebeea665dc52c9e78f40badf42a43d661140e2c4647b1ebe",
    "sources/word-geometry-20261110.json": "e3348d0d60d3097b05d0afdb0a1fccf66409274408af9ae7a9369c37fe596e9f",
    "analysis_outputs/3d_article_map/article_3d_map_data.json": "22c2285a6cd53f6bdda7bdd284d556c52ff55dea0a55cd1b549acbb81443eac3",
    "analysis_outputs/continuation_20261109/inverted_duplex/inverted_duplex.json": "4d6d029bf5f7e90acfa1d456bc94e790913c7865b923c9367212c219867742f3",
}
SOURCE_FILES = (
    *RAW_SOURCE_PINS,
    "analysis_outputs/continuation_20261110/batch20/G02/RESULT.json",
    "analysis_outputs/continuation_20261110/batch20/GEOMETRY_PROTOCOL.json",
)
CODE_FILES = (
    "scripts/g02_joint_source_audit.py",
    "scripts/verify_g02_joint_source_audit.py",
    "scripts/batch20_geometry.py",
)
DEFINITION = {
    "id": "g02-joint-color-source-audit",
    "pairs": [list(pair) for pair in PAIRS],
    "selectors": list(SELECTORS),
    "sourcePopulation": "All original G02 target lexical word objects, preserving row/token order and IDs.",
    "geometry": "Owning load_geometry and point_rotate helpers; no OCR, image operation, fitting or repair.",
    "guard": "max(12, frozen centerUncertaintyPx)",
    "numericDomain": "Freeze owning finite float centers/guards/mask coordinates as exact binary rationals. Evaluate the closed square without clipping, rounding or added tolerance.",
    "sourcePredicate": "a <= 2544-x < c and b <= y < d in original source rectangles.",
    "targetPredicate": "a <= x < c and b <= y < d in original target rectangles.",
    "coupling": "Source and target colors are evaluated at the same displaced point.",
    "partition": "All rectangle edge coordinates, reflected source x edges, square endpoints, and one midpoint of every open interval; all Cartesian endpoint/interior cells.",
    "overlap": "Any cell with both colors on either side makes the whole word unresolved. No color or zero state is guessed.",
    "compatibility": "Compare nominal exact-rational colors with original float predicates; compare every original guard-unambiguous class with the full new class set. Any disagreement leaves the word unresolved.",
    "membership": "must if every classifiable cell selects the word; optional if some do; out if none do; unresolved if any overlap or compatibility disagreement occurs.",
    "pathCounts": "2^optional per selector is only an independent-word assignment upper bound; null for any unresolved word. No strings or paths are generated.",
    "maximumCanonicalRows": 142,
    "canonicalTokens": 1258,
    "canonicalLexicalWords": 1243,
    "targetWordPositionsByPair": [263, 274, 226, 199],
    "maximumTotalPartitionPoints": 200000,
    "newCipherOutputs": 0,
    "keyChecks": 0,
    "derivations": 0,
    "historyQueries": 0,
    "walletActions": 0,
    "negativeResultClaimed": False,
}
ACTIVITY = {
    "newImages": 0,
    "newOCR": 0,
    "newGeometryFit": 0,
    "newCipherOutputs": 0,
    "keyChecks": 0,
    "derivations": 0,
    "historyQueries": 0,
    "walletActions": 0,
}
PRIMARY_CONTROLS = {
    "passed": True,
    "truthTableCases": 9,
    "endpointUnionOverlapEmptyAndCouplingControls": 9,
    "sameClassDifferentNominalColorsControl": True,
    "unsafeOutputPathControlsRejected": 3,
    "safePrivatePathControlAccepted": True,
    "invalidCoordinatesRejected": 4,
    "targetInputsRead": False,
    "newCipherOutputs": 0,
    "keyChecks": 0,
    "networkRequests": 0,
}
PRIMARY_LIMITS = [
    "The exact joint enclosure is new arithmetic, not byte-identical old within() execution.",
    "Centers, rectangles and guards remain investigator-defined, uncalibrated assumptions.",
    "Independent per-word assignment counts overapproximate physical correlations; they are not counts of independent hypotheses or measured likelihoods.",
    "Only metadata membership/feasibility was audited. No candidate text, plaintext paths, crypto or puzzle exclusion was generated.",
]


class VerificationError(ValueError):
    """A safe, descriptive verification failure without source values."""


def _require(condition, message):
    if not condition:
        raise VerificationError(message)


def _digest(buffer):
    return hashlib.sha256(buffer).hexdigest()


def _same_json(left, right):
    # Serialization distinguishes booleans, integers, floats, and signed zero.
    options = {"sort_keys": True, "allow_nan": False, "separators": (",", ":")}
    return json.dumps(left, **options) == json.dumps(right, **options)


def _utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _exact(value):
    """Freeze an integer, finite binary float, or Fraction without rounding."""
    if isinstance(value, bool):
        raise TypeError("Boolean geometry is not permitted")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Geometry must be finite")
        return Fraction.from_float(value)
    raise TypeError("Geometry must use int, float, or Fraction values")


def _rectangles(masks):
    if not isinstance(masks, Mapping):
        raise TypeError("Masks must be a mapping")
    result = {}
    for color in COLORS:
        raw_rectangles = masks.get(color, ())
        if isinstance(raw_rectangles, (str, bytes)) or not isinstance(
            raw_rectangles, Sequence
        ):
            raise TypeError("A mask color must contain a rectangle sequence")
        rectangles = []
        for raw in raw_rectangles:
            if isinstance(raw, (str, bytes)) or not isinstance(raw, Sequence):
                raise TypeError("A rectangle must be a numeric sequence")
            if len(raw) != 4:
                raise ValueError("A rectangle needs four coordinates")
            # Degenerate/reversed rectangles are permitted and denote the empty
            # set under the unchanged a<=x<c, b<=y<d predicate.
            rectangles.append(tuple(_exact(v) for v in raw))
        result[color] = tuple(rectangles)
    return result


def _bands(lower, upper, boundaries):
    """Return representatives of endpoint singletons and intervening opens."""
    points = sorted({lower, upper, *(v for v in boundaries if lower <= v <= upper)})
    representatives = []
    for i, point in enumerate(points):
        representatives.append(point)
        if i + 1 < len(points):
            representatives.append((point + points[i + 1]) / 2)
    return representatives


def _color_at(x, y, masks):
    """Return one color/None, plus a flag for an unresolved two-color overlap."""
    present = []
    for color in COLORS:
        if any(a <= x < c and b <= y < d for a, b, c, d in masks[color]):
            present.append(color)
    if len(present) > 1:
        return None, True
    return (present[0] if present else None), False


def _joint_at(x, y, source_masks, target_masks, width):
    source_color, source_overlap = _color_at(width - x, y, source_masks)
    target_color, target_overlap = _color_at(x, y, target_masks)
    if source_overlap or target_overlap:
        return None, None
    pair = (COLOR_STATES[source_color], COLOR_STATES[target_color])
    if source_color is None:
        return ("neither" if target_color is None else "target-only"), pair
    if target_color is None:
        return "source-only", pair
    return (
        "same-color" if source_color == target_color else "opposite-color"
    ), pair


def independent_classify_joint(
    center, guard, source_masks, target_masks, width=2544
):
    """Classify every exact cell in the closed, unclipped joint guard domain.

    The result lists classes and joint color states across all classifiable
    cells. Color states are 0 for none, 1 for orange, and 2 for black. The
    nominal class and color pair are None at a two-color overlap at the center.
    Cells evaluated includes all partition cells. Any overlap invalidates
    certification of the whole word and leaves its path count null.

    No position is clipped to the page or rounded. A reflected source box has
    asymmetric x endpoints: a<=width-x<c. No naive half-open reflected box is
    constructed for membership evaluation.
    """
    if isinstance(center, (str, bytes)) or not isinstance(center, Sequence):
        raise TypeError("Center must be a numeric pair")
    if len(center) != 2:
        raise ValueError("Center must have two coordinates")
    cx, cy = (_exact(v) for v in center)
    radius, page_width = _exact(guard), _exact(width)
    if radius < 0:
        raise ValueError("Guard must be nonnegative")
    if page_width <= 0:
        raise ValueError("Page width must be positive")
    source, target = _rectangles(source_masks), _rectangles(target_masks)
    x_edges, y_edges = [], []
    for color in COLORS:
        for a, b, c, d in source[color]:
            x_edges.extend((page_width - a, page_width - c))
            y_edges.extend((b, d))
        for a, b, c, d in target[color]:
            x_edges.extend((a, c))
            y_edges.extend((b, d))
    xs = _bands(cx - radius, cx + radius, x_edges)
    ys = _bands(cy - radius, cy + radius, y_edges)
    classes, states, overlap_observed = set(), set(), False
    for x, y in itertools.product(xs, ys):
        category, state = _joint_at(x, y, source, target, page_width)
        if state is None:
            overlap_observed = True
        else:
            classes.add(category)
            states.add(state)
    nominal, nominal_colors = _joint_at(cx, cy, source, target, page_width)
    return {
        "classes": sorted(classes),
        "jointColorStates": [list(state) for state in sorted(states)],
        "overlapObserved": overlap_observed,
        "cellsEvaluated": len(xs) * len(ys),
        "nominalClass": nominal,
        "nominalColors": list(nominal_colors) if nominal_colors is not None else None,
    }


def classify_joint(center, guard, source_masks, target_masks, width=2544):
    """Public-contract spelling for the independent numeric-only kernel."""
    return independent_classify_joint(
        center, guard, source_masks, target_masks, width
    )


def _integer_half_grid_oracle(center, guard, source_masks, target_masks, width):
    """Independent exhaustive oracle for INTEGER-coordinate synthetic inputs.

    Doubled-integer arithmetic evaluates every half-grid point in the closed
    domain. Integer mask/domain edges ensure this visits every endpoint and at
    least one interior point of each nonempty geometric band. This oracle does
    not call the partition builder, exact conversion, or point classifiers.
    """
    values = [*center, guard, width]
    for side in (source_masks, target_masks):
        for color in COLORS:
            values.extend(v for rect in side[color] for v in rect)
    if not all(type(v) is int for v in values):
        raise TypeError("Half-grid oracle accepts integer synthetics only")

    def at(xx, yy):
        source_x = 2 * width - xx
        source_o = any(
            2 * a <= source_x < 2 * c and 2 * b <= yy < 2 * d
            for a, b, c, d in source_masks["orange"]
        )
        source_b = any(
            2 * a <= source_x < 2 * c and 2 * b <= yy < 2 * d
            for a, b, c, d in source_masks["black"]
        )
        target_o = any(
            2 * a <= xx < 2 * c and 2 * b <= yy < 2 * d
            for a, b, c, d in target_masks["orange"]
        )
        target_b = any(
            2 * a <= xx < 2 * c and 2 * b <= yy < 2 * d
            for a, b, c, d in target_masks["black"]
        )
        if (source_o and source_b) or (target_o and target_b):
            return None, None
        state = (int(source_o) + 2 * int(source_b),
                 int(target_o) + 2 * int(target_b))
        truth = {
            (0, 0): "neither",
            (0, 1): "target-only", (0, 2): "target-only",
            (1, 0): "source-only", (2, 0): "source-only",
            (1, 1): "same-color", (2, 2): "same-color",
            (1, 2): "opposite-color", (2, 1): "opposite-color",
        }
        return truth[state], state

    classes, states, overlap_observed = set(), set(), False
    for xx in range(2 * (center[0] - guard), 2 * (center[0] + guard) + 1):
        for yy in range(2 * (center[1] - guard), 2 * (center[1] + guard) + 1):
            category, state = at(xx, yy)
            if state is None:
                overlap_observed = True
            else:
                classes.add(category)
                states.add(state)
    nominal, nominal_colors = at(2 * center[0], 2 * center[1])
    return {
        "classes": sorted(classes),
        "jointColorStates": [list(state) for state in sorted(states)],
        "overlapObserved": overlap_observed,
        "nominalClass": nominal,
        "nominalColors": list(nominal_colors) if nominal_colors is not None else None,
    }


def _masks(orange=(), black=()):
    return {"orange": list(orange), "black": list(black)}


def self_test():
    """Run only finite synthetic controls; no target reads or target checks."""
    _require(__debug__, "Synthetic controls require assertions enabled")
    comparisons = 0

    def compare(center, guard, source, target, width):
        nonlocal comparisons
        actual = independent_classify_joint(center, guard, source, target, width)
        expected = _integer_half_grid_oracle(center, guard, source, target, width)
        for key in ("classes", "jointColorStates", "overlapObserved", "nominalClass", "nominalColors"):
            assert actual[key] == expected[key], (key, actual, expected)
        assert actual["cellsEvaluated"] >= 1
        assert set(actual["classes"]) <= CLASS_NAMES
        comparisons += 1
        return actual

    empty = _masks()
    result = compare([0, 0], 0, empty, empty, 4)
    assert result == {"classes": ["neither"], "jointColorStates": [[0, 0]],
                      "overlapObserved": False, "cellsEvaluated": 1,
                      "nominalClass": "neither", "nominalColors": [0, 0]}
    assert compare([-3, 7], 2, empty, empty, 4)["cellsEvaluated"] == 9

    # All nine classifiable side-state pairs have an independently stated truth
    # table, including both equal colors and both unequal-color directions.
    cover = [[-10, -10, 10, 10]]
    states = [_masks(), _masks(orange=cover), _masks(black=cover)]
    truth_rows = [
        ["neither", "target-only", "target-only"],
        ["source-only", "same-color", "opposite-color"],
        ["source-only", "opposite-color", "same-color"],
    ]
    for i, j in itertools.product(range(3), repeat=2):
        result = compare([2, 2], 1, states[i], states[j], 4)
        assert result["classes"] == [truth_rows[i][j]]
        assert result["nominalClass"] == truth_rows[i][j]
        assert not result["overlapObserved"]

    # Original-source half-open predicate reflects to (width-c, width-a].
    one = _masks(orange=[[1, 0, 3, 2]])
    assert compare([1, 1], 0, one, empty, 4)["nominalClass"] == "neither"
    assert compare([3, 1], 0, one, empty, 4)["nominalClass"] == "source-only"
    assert compare([1, 1], 0, empty, one, 4)["nominalClass"] == "target-only"
    assert compare([3, 1], 0, empty, one, 4)["nominalClass"] == "neither"
    result = compare([2, 1], 1, one, one, 4)
    assert result["classes"] == ["neither", "same-color", "source-only", "target-only"]
    assert result["cellsEvaluated"] == 9
    assert compare([2, 2], 0, one, one, 4)["nominalClass"] == "neither"

    # Same-color overlaps are unions, not a two-color conflict. Adjacent colors
    # have no overlapping half-open cells, including at the shared endpoint.
    union = _masks(orange=[[0, 0, 3, 4], [2, 0, 4, 4]])
    adjacent = _masks(orange=[[0, 0, 2, 4]], black=[[2, 0, 4, 4]])
    assert not compare([2, 2], 2, union, union, 4)["overlapObserved"]
    assert not compare([2, 2], 2, adjacent, adjacent, 4)["overlapObserved"]
    conflict = _masks(orange=[[0, 0, 3, 4]], black=[[2, 0, 4, 4]])
    for source, target in ((conflict, empty), (empty, conflict), (conflict, conflict)):
        assert compare([2, 2], 2, source, target, 4)["overlapObserved"]
    full_conflict = _masks(orange=cover, black=cover)
    result = compare([2, 2], 1, full_conflict, full_conflict, 4)
    assert result["classes"] == [] and result["nominalClass"] is None
    assert result["overlapObserved"]

    # Multiple overlapping rectangles on BOTH sides; certification remains
    # invalid if any cell conflicts, even if the nominal center is classifiable.
    multi_source = _masks(orange=[[0, -1, 3, 4], [1, 0, 4, 3]],
                          black=[[2, 1, 5, 5], [4, -1, 6, 2]])
    multi_target = _masks(orange=[[-1, 0, 2, 5], [1, 2, 4, 4]],
                          black=[[1, -1, 5, 2], [3, 1, 6, 5]])
    assert compare([2, 2], 3, multi_source, multi_target, 6)["overlapObserved"]
    off_center = _masks(orange=[[0, 0, 4, 4]], black=[[3, 0, 4, 4]])
    result = compare([1, 1], 3, empty, off_center, 6)
    assert result["nominalClass"] == "target-only" and result["overlapObserved"]

    # Exhaustively assign one of four integer rectangles (or no rectangle) to
    # each of the four side/color slots. Every case is checked on all half-grid
    # positions in the closed synthetic domain, not just a sample of cells.
    palette = [None, [0, 0, 2, 2], [1, 0, 3, 2], [0, 1, 2, 3], [2, -1, 4, 3]]
    for so, sb, to, tb in itertools.product(palette, repeat=4):
        source = _masks([] if so is None else [so], [] if sb is None else [sb])
        target = _masks([] if to is None else [to], [] if tb is None else [tb])
        compare([1, 1], 2, source, target, 4)

    # No page clipping: both predicates can select points outside [0,width].
    outside_source = _masks(orange=[[5, -2, 7, 2]])
    outside_target = _masks(black=[[-3, -2, -1, 2]])
    assert compare([-2, 0], 0, outside_source, outside_target, 4)["nominalClass"] == "opposite-color"

    # Freeze each binary float BEFORE subtraction. Decimal reinterpretation or
    # a float-rounded reflected boundary would disagree with this exact case.
    binary_case = independent_classify_joint(
        [0.1, 0.0], 0.0, _masks(orange=[[0.2, -1, 0.4, 1]]), empty, 0.3
    )
    assert Fraction.from_float(0.3) - Fraction.from_float(0.1) < Fraction.from_float(0.2)
    assert binary_case["classes"] == ["neither"]
    assert binary_case["cellsEvaluated"] == 1
    side_colors = _masks(orange=[[-1, -1, 0.9, 1]], black=[[0.9, -1, 2, 1]])
    exact_color = independent_classify_joint([0.1, 0.0], 0, side_colors, empty, 1)
    old_class, old_color = _joint_at(0.1, 0.0, side_colors, empty, 1)
    assert exact_color["nominalClass"] == old_class == "source-only"
    assert exact_color["nominalColors"] == [1, 0] and old_color == (2, 0)
    assert _exact(0.1) == Fraction.from_float(0.1)
    assert independent_classify_joint([Fraction(1, 3), 0], 0, empty, empty)["nominalClass"] == "neither"

    for bad in (float("nan"), float("inf"), float("-inf")):
        try:
            independent_classify_joint([bad, 0], 1, empty, empty)
        except ValueError:
            pass
        else:
            raise AssertionError("Nonfinite geometry was accepted")
    try:
        independent_classify_joint([0, 0], -1, empty, empty)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative guard was accepted")

    _source_metadata_control()
    return {
        "passed": True,
        "independentHalfGridComparisons": comparisons,
        "exhaustivePaletteCases": 625,
        "truthTablePairs": 9,
        "exactBinaryFloatControl": True,
        "sourceMetadataControl": True,
        "targetInputsRead": False,
        "targetExecution": False,
        "textConstructed": False,
        "networkQueries": 0,
        "keyOrFormatChecks": 0,
    }


def _ordered_geometry(canonical_rows, geometry_rows):
    """Validate exact lexical identity/order, then retain geometry metadata."""
    geometry_by_id = {row["id"]: row for row in geometry_rows}
    _require(len(geometry_by_id) == len(geometry_rows), "Duplicate frozen geometry row IDs")
    _require(len({row["id"] for row in canonical_rows}) == len(canonical_rows),
             "Duplicate canonical row IDs")
    ordered_rows, token_count = [], 0
    for row in canonical_rows:
        frozen = geometry_by_id.get(row["id"])
        _require(frozen is not None and frozen.get("status") == "complete",
                 "Missing or incomplete frozen lexical geometry")
        canonical_tokens = row["text"].split()
        token_count += len(canonical_tokens)
        lexical_tokens = [token for token in canonical_tokens if any(c.isalnum() for c in token)]
        words = [word for word in frozen.get("words", [])
                 if any(c.isalnum() for c in word.get("text", ""))]
        _require(len(lexical_tokens) == len(words), "Frozen lexical token count differs")
        metadata = []
        for token, word in zip(lexical_tokens, words):
            _require(word.get("text") == token, "Frozen lexical identity or order differs")
            box = word.get("box")
            _require(isinstance(box, list) and len(box) == 4,
                     "Missing or malformed frozen word box")
            left, top, right, bottom = box
            _require(0 <= left < right <= 2544 and 0 <= top < bottom <= 3264,
                     "Frozen word box lies outside the owning coordinate bounds")
            _require(word.get("verified") is True, "Frozen word geometry is unverified")
            metadata.append((word["id"], box, word.get("centerUncertaintyPx", 12)))
        rotation = frozen.get("rotationCCWDegrees", row["locator"].get("rotate_ccw_degrees", 0))
        ordered_rows.append((row["id"], row["page"], rotation, metadata))
    return ordered_rows, token_count


def _page_masks(model_pages, inverted_boxes):
    masks = {}
    for page in model_pages:
        number = page["page"]
        if not 75 <= number <= 79:
            continue
        orange = []
        for highlight in page["highlights"]:
            if number == 79 and int(highlight["id"].rsplit("_", 1)[1]) >= 6:
                continue
            orange.append(highlight["box"])
        masks[number] = {"orange": orange, "black": inverted_boxes.get(str(number), [])}
        # Validate while retaining the original ints/floats for legacy predicates.
        for boxes in _rectangles(masks[number]).values():
            _require(all(a < c and b < d for a, b, c, d in boxes), "Frozen mask rectangle is empty")
    return masks


def _upright_center(box, rotation):
    # Keep each binary64 operation in the owner's evaluation order. A
    # mathematically equivalent reassociation can change a boundary predicate.
    left, top, right, bottom = box
    x = (left + right) / 2
    y = (top + bottom) / 2
    angle = math.radians(-rotation)
    dx = x - 2544 / 2
    dy = y - 3264 / 2
    cosine, sine = math.cos(angle), math.sin(angle)
    return (2544 / 2 + cosine * dx + sine * dy,
            3264 / 2 - sine * dx + cosine * dy)


def _legacy_side_unknown(x, y, masks, guard):
    _, overlap = _color_at(x, y, masks)
    return overlap or any(
        left - guard <= x < right + guard
        and top - guard <= y < bottom + guard
        and min(abs(x - left), abs(x - right), abs(y - top), abs(y - bottom)) <= guard
        for color in COLORS
        for left, top, right, bottom in masks[color]
    )


def _word_record(source, target, row_id, ordinal, word, rotation, masks):
    word_id, box, uncertainty = word
    x, y = _upright_center(box, rotation)
    guard = max(12, float(uncertainty))
    exact = independent_classify_joint((x, y), guard, masks[source], masks[target])
    old_class, old_pair = _joint_at(x, y, masks[source], masks[target], 2544)
    old_colors = list(old_pair) if old_pair is not None else None
    old_unknown = (_legacy_side_unknown(2544 - x, y, masks[source], guard)
                   or _legacy_side_unknown(x, y, masks[target], guard))
    color_disagreement = exact["nominalColors"] != old_colors
    stable_disagreement = not old_unknown and (
        exact["classes"] != [old_class] or exact["overlapObserved"]
    )
    unresolved = exact["overlapObserved"] or color_disagreement or stable_disagreement
    membership = {}
    for selector in SELECTORS:
        if unresolved:
            state = "unresolved"
        elif exact["classes"] == [selector]:
            state = "must"
        elif selector in exact["classes"]:
            state = "optional"
        else:
            state = "out"
        membership[selector] = state
    return {
        "source": source,
        "target": target,
        "rowId": row_id,
        "wordId": word_id,
        "wordOrdinalInRow": ordinal,
        "centerUprightFloat": [x, y],
        "guardPxFloat": guard,
        **exact,
        "oldFloatClass": old_class,
        "oldFloatColors": old_colors,
        "oldGuardUnknown": old_unknown,
        "nominalFloatCompatibilityDisagreement": color_disagreement,
        "oldStableClassDisagreement": stable_disagreement,
        "selectorMembership": membership,
    }


def _selector_counts(records):
    summary = {}
    for selector in SELECTORS:
        counts = dict.fromkeys(MEMBERSHIP_STATES, 0)
        for record in records:
            counts[record["selectorMembership"][selector]] += 1
        counts["independentAssignmentUpperBound"] = (
            None if counts["unresolved"] else str(1 << counts["optional"])
        )
        summary[selector] = counts
    return summary


def _source_metadata_control():
    canonical = [{"id": "synthetic-row", "page": 77, "text": "alpha — beta",
                  "locator": {"rotate_ccw_degrees": 0}}]
    geometry = [{"id": "synthetic-row", "status": "complete", "words": [
        {"id": "synthetic-first", "text": "alpha", "box": [100, 100, 110, 110], "verified": True},
        {"text": "—"},
        {"id": "synthetic-second", "text": "beta", "box": [112, 100, 122, 110], "verified": True},
    ]}]
    rows, tokens = _ordered_geometry(canonical, geometry)
    assert tokens == 3 and [word[0] for word in rows[0][3]] == ["synthetic-first", "synthetic-second"]
    mask_pages = [{"page": 76, "highlights": []}, {"page": 77, "highlights": [
        {"id": "synthetic_1", "box": [50, 50, 150, 150]}]}, {"page": 79, "highlights": [
        {"id": "synthetic_5", "box": [1, 1, 2, 2]},
        {"id": "synthetic_6", "box": [2, 2, 3, 3]},
    ]}]
    masks = _page_masks(mask_pages, {})
    assert masks[79]["orange"] == [[1, 1, 2, 2]]
    first = _word_record(76, 77, rows[0][0], 1, rows[0][3][0], rows[0][2], masks)
    assert first["centerUprightFloat"] == [105.0, 105.0]
    assert first["oldFloatColors"] == first["nominalColors"] == [0, 1]
    assert first["selectorMembership"]["target-only"] == "must"
    masks[77]["black"] = [[110, 100, 120, 120]]
    disputed = _word_record(76, 77, rows[0][0], 1, rows[0][3][0], rows[0][2], masks)
    assert disputed["overlapObserved"] and disputed["nominalColors"] == [0, 1]
    assert _selector_counts([first, disputed])["target-only"] == {
        "must": 1, "optional": 0, "out": 0, "unresolved": 1,
        "independentAssignmentUpperBound": None,
    }
    geometry[0]["words"][0]["text"] = "beta"
    try:
        _ordered_geometry(canonical, geometry)
    except VerificationError:
        pass
    else:
        raise AssertionError("Mismatched lexical source order was accepted")


def _outside_fresh_directory(path, corpus):
    raw = path.expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    normalized = Path(os.path.abspath(raw))
    resolved = raw.resolve()
    site = corpus.parent.parent.resolve()
    paths = [raw, normalized, resolved, *(parent.resolve() for parent in raw.parents)]
    _require(all(candidate != site and site not in candidate.parents
                 and "public" not in (part.lower() for part in candidate.parts)
                 for candidate in paths), "Output must be outside Site and public routes")
    _require(not raw.exists() and not raw.is_symlink(), "Output directory must be fresh")
    _require(resolved.parent.is_dir(), "Private output parent must already exist")
    return resolved


def _verified_inputs(corpus, protocol_path, registration_commit):
    _require(re.fullmatch(r"[a-f0-9]{40}", registration_commit) is not None,
             "Invalid registration commit identity")
    protocol_bytes = protocol_path.read_bytes()
    protocol_sha = _digest(protocol_bytes)
    protocol = json.loads(protocol_bytes)
    _require(_same_json(protocol["definition"], DEFINITION), "Registered audit definition differs")
    source_pins, code_pins = protocol["sourceHashes"], protocol["scriptHashes"]
    _require(set(source_pins) == set(SOURCE_FILES) and set(code_pins) == set(CODE_FILES),
             "Protocol does not pin the declared source and code files")
    _require(all(source_pins[name] == expected for name, expected in RAW_SOURCE_PINS.items()),
             "Registered raw source pins differ from the owning G02 pins")
    receipt_bytes = (protocol_path.parent / "REGISTRATION.json").read_bytes()
    receipt = json.loads(receipt_bytes)
    _require(receipt["registrationCommit"] == registration_commit
             and receipt["protocolSha256"] == protocol_sha
             and receipt["remoteHeadMatches"] is True,
             "Verified public registration receipt does not match")
    for name in CODE_FILES:
        _require(_digest((corpus / name).read_bytes()) == code_pins[name],
                 f"Registered code bytes differ for {name}")
    _require(_digest(Path(__file__).read_bytes()) == code_pins[CODE_FILES[1]],
             "Executing verifier bytes differ from registration")
    raw_sources = []
    for name in SOURCE_FILES:
        buffer = (corpus / name).read_bytes()
        _require(_digest(buffer) == source_pins[name], f"Registered source bytes differ for {name}")
        if name in RAW_SOURCE_PINS:
            raw_sources.append(json.loads(buffer))
    return raw_sources, protocol, protocol_sha, _digest(receipt_bytes)


def _compare_word_records(actual, expected):
    _require(isinstance(actual, list) and len(actual) == len(expected),
             "Primary word record population differs")
    for ordinal, (given, rebuilt) in enumerate(zip(actual, expected), 1):
        _require(isinstance(given, dict) and set(given) == set(rebuilt),
                 f"Primary word record field set differs at ordered record {ordinal}")
        for field, value in rebuilt.items():
            _require(_same_json(given[field], value),
                     f"Primary metadata differs at ordered record {ordinal}, field {field}")


def _validate_primary_result(actual, expected):
    volatile = {"startedAtUTC", "completedAtUTC"}
    _require(set(actual) == set(expected) | volatile, "Primary result field set differs")
    for field, value in expected.items():
        _require(_same_json(actual[field], value), f"Primary aggregate or provenance differs for {field}")
    times = [actual["startedAtUTC"], actual["completedAtUTC"]]
    _require(all(isinstance(t, str) and t.endswith("Z") for t in times), "Primary timestamps must be UTC")
    began, ended = (datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times)
    _require(began <= ended, "Primary timestamp chronology differs")


def verify(corpus, protocol_path, registration_commit, primary_inventory, primary_result, out):
    started = _utc()
    controls = self_test()
    corpus = corpus.resolve()
    output = _outside_fresh_directory(out, corpus)
    raw, protocol, protocol_sha, receipt_sha = _verified_inputs(
        corpus, protocol_path.resolve(), registration_commit
    )
    canonical, geometry, model, inverted = raw
    ordered_rows, token_count = _ordered_geometry(canonical["rows"], geometry["rows"])
    lexical_count = sum(len(words) for _, _, _, words in ordered_rows)
    _require((len(ordered_rows), token_count, lexical_count) == (142, 1258, 1243),
             "Canonical population is outside the registered scope")
    masks = _page_masks(model["pages"], inverted["boxes"])

    records, pairs, total_cells = [], [], 0
    for source, target in PAIRS:
        pair_records = []
        for row_id, page, rotation, words in ordered_rows:
            if page != target:
                continue
            for ordinal, word in enumerate(words, 1):
                record = _word_record(source, target, row_id, ordinal, word, rotation, masks)
                total_cells += record["cellsEvaluated"]
                _require(total_cells <= DEFINITION["maximumTotalPartitionPoints"],
                         "Registered partition point cap exceeded")
                pair_records.append(record)
        records.extend(pair_records)
        pairs.append({
            "source": source,
            "target": target,
            "wordPositions": len(pair_records),
            "legacyFlaggedWordOccurrences": sum(r["oldGuardUnknown"] for r in pair_records),
            "overlapWords": sum(r["overlapObserved"] for r in pair_records),
            "nominalCompatibilityDisagreements": sum(r["nominalFloatCompatibilityDisagreement"] for r in pair_records),
            "oldStableClassDisagreements": sum(r["oldStableClassDisagreement"] for r in pair_records),
            "selectors": _selector_counts(pair_records),
        })
    _require(len({record["wordId"] for record in records}) == len(records),
             "Reconstructed target word IDs are not unique")
    _require([pair["wordPositions"] for pair in pairs] == DEFINITION["targetWordPositionsByPair"],
             "Target word population differs from registration")
    legacy_counts = [pair["legacyFlaggedWordOccurrences"] for pair in pairs]
    _require(legacy_counts == [20, 25, 23, 29], "Legacy uncertainty counts differ from the saved run")
    global_selectors = _selector_counts(records)
    counts = {
        "canonicalRows": len(ordered_rows),
        "canonicalTokens": token_count,
        "canonicalLexicalWords": lexical_count,
        "directedPairs": len(pairs),
        "targetWordPositions": len(records),
        "legacyFlaggedWordOccurrences": sum(legacy_counts),
        "partitionPointsEvaluated": total_cells,
    }

    inventory_bytes = primary_inventory.read_bytes()
    result_bytes = primary_result.read_bytes()
    inventory_sha, result_sha = _digest(inventory_bytes), _digest(result_bytes)
    inventory, result = json.loads(inventory_bytes), json.loads(result_bytes)
    inventory_fields = {"version": 1, "auditId": DEFINITION["id"],
                        "sourceHashes": protocol["sourceHashes"], "definition": DEFINITION}
    _require(set(inventory) == set(inventory_fields) | {"wordRecords"},
             "Primary inventory field set differs")
    for field, value in inventory_fields.items():
        _require(_same_json(inventory[field], value), f"Primary inventory provenance differs for {field}")
    _compare_word_records(inventory["wordRecords"], records)
    result_fields = {
        "version": 1,
        "testId": DEFINITION["id"],
        "caseStatus": "unsolved",
        "registrationCommit": registration_commit,
        "protocolSha256": protocol_sha,
        "sourceHashes": protocol["sourceHashes"],
        "scriptHashes": protocol["scriptHashes"],
        "sourceModelComplete": all(c["unresolved"] == 0 for c in global_selectors.values()),
        "negativeResultClaimed": False,
        "newCipherOutputsGenerated": False,
        "counts": counts,
        "pairs": pairs,
        "globalSelectors": global_selectors,
        "inventory": {"file": "MEMBERSHIP.json", "sha256": inventory_sha},
        "controls": PRIMARY_CONTROLS,
        "activity": ACTIVITY,
        "limits": PRIMARY_LIMITS,
    }
    _validate_primary_result(result, result_fields)
    report = {
        "version": 1,
        "testId": DEFINITION["id"],
        "verificationPassed": True,
        "startedAtUTC": started,
        "completedAtUTC": _utc(),
        "registrationCommit": registration_commit,
        "protocolSha256": protocol_sha,
        "registrationReceiptSha256": receipt_sha,
        "sourceHashes": protocol["sourceHashes"],
        "scriptHashes": protocol["scriptHashes"],
        "primaryInventorySha256": inventory_sha,
        "primaryResultSha256": result_sha,
        "allOrderedMetadataFieldsMatch": True,
        "sourceModelComplete": result_fields["sourceModelComplete"],
        "counts": counts,
        "pairs": pairs,
        "globalSelectors": global_selectors,
        "controls": controls,
        "activity": ACTIVITY,
    }
    output.mkdir(mode=0o700)
    output.chmod(0o700)
    result_path = output / "INDEPENDENT_VERIFICATION.json"
    with os.fdopen(os.open(result_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as file:
        os.fchmod(file.fileno(), 0o600)
        json.dump(report, file, indent=2, allow_nan=False)
        file.write("\n")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true", help="synthetic controls only")
    mode.add_argument("--verify", action="store_true", help="verify the registered source metadata")
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--registration-commit")
    parser.add_argument("--primary-inventory", type=Path)
    parser.add_argument("--primary-result", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    values = (args.corpus, args.protocol, args.registration_commit,
              args.primary_inventory, args.primary_result, args.out)
    if args.self_test:
        if any(value is not None for value in values):
            parser.error("Self-test accepts no target inputs")
        print(json.dumps(self_test(), sort_keys=True))
        return
    if not all(values):
        parser.error("Verification requires explicit corpus, protocol, registration, primary artifacts, and output")
    try:
        report = verify(*values)
    except VerificationError as error:
        parser.exit(1, f"Verification failed: {error}\n")
    except (OSError, KeyError, TypeError, ValueError):
        parser.exit(1, "Verification failed while reading declared files or validating metadata\n")
    print(json.dumps({"verificationPassed": report["verificationPassed"],
                      "counts": report["counts"], "activity": report["activity"]}, sort_keys=True))


if __name__ == "__main__":
    main()
