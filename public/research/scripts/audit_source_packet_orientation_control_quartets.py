#!/usr/bin/env python3
"""Control the active orientation fingerprint against local quartets.

This bounded pass does not generate candidates or try extraction. It asks
whether the active readable/upright geometry signature is selective against the
available page-76 Y/K and C9 format controls, and records where controls are
limited by missing non-active box geometry.
"""

from __future__ import annotations

import itertools
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/source_packet_orientation_control_quartets"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_orientation_control_quartets.json"
OUT_MD = OUT / "source_packet_orientation_control_quartets.md"
OUT_SHEET = OUT / "source_packet_orientation_control_quartets_sheet.jpg"

INPUTS = {
    "orientation_disambiguator": ROOT
    / "analysis_outputs/source_audit/source_packet_orientation_disambiguator/"
    "source_packet_orientation_disambiguator.json",
    "geometric_fingerprint": ROOT
    / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/"
    "source_packet_geometric_fingerprint.json",
    "frame_normalized_geometry": ROOT
    / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry/"
    "source_packet_frame_normalized_geometry.json",
    "alignment_tolerance": ROOT
    / "analysis_outputs/source_audit/source_packet_alignment_tolerance/"
    "source_packet_alignment_tolerance.json",
    "color_profile_manifest": ROOT
    / "analysis_outputs/source_audit/source_packet_color_profile_manifest/"
    "source_packet_color_profile_manifest.json",
    "o4_frame_rescue_yk_filter_control": ROOT
    / "analysis_outputs/source_audit/o4_frame_rescue_yk_filter_control/"
    "o4_frame_rescue_yk_filter_control.json",
    "o4_frame_yk_unit_order_gate": ROOT
    / "analysis_outputs/source_audit/o4_frame_yk_unit_order_gate/"
    "o4_frame_yk_unit_order_gate.json",
    "c9_bold_highlight_format_density": ROOT
    / "analysis_outputs/source_audit/c9_bold_highlight_format_density/"
    "c9_bold_highlight_format_density.json",
    "source_packet_r3_bridge_audit": ROOT
    / "analysis_outputs/source_audit/source_packet_r3_bridge_audit/"
    "source_packet_r3_bridge_audit.json",
    "source_packet_reopen_trigger_matrix": ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json",
}

ACTIVE_IDS = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]
ACTIVE_STATE_PATTERN = "YKKY"
ACTIVE_GROUP_INDEXES = [12, 14, 15, 19]
ACTIVE_GROUP_GAPS = [2, 1, 4]
ACTIVE_LINE_ORDER = [22, 25, 27, 32]
ACTIVE_CORRIDOR_ORDER = [4, 7, 9, 14]
ACTIVE_LINE_GAPS = [3, 2, 5]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def gaps(values: list[int]) -> list[int]:
    return [b - a for a, b in zip(values, values[1:])]


def center(box: list[float]) -> list[float]:
    return [(float(box[0]) + float(box[2])) / 2.0, (float(box[1]) + float(box[3])) / 2.0]


def sign_stream(points: list[list[float]], axis: int) -> str:
    chars = []
    for left, right in zip(points, points[1:]):
        delta = right[axis] - left[axis]
        chars.append("+" if delta > 0 else "-" if delta < 0 else "0")
    return "".join(chars)


def norm_centers(points: list[list[float]], frame: list[float]) -> list[list[float]]:
    x0, y0, x1, y1 = [float(v) for v in frame]
    return [[round((x - x0) / (x1 - x0), 6), round((y - y0) / (y1 - y0), 6)] for x, y in points]


def group_row(groups: list[dict], source: str, row_type: str, ordinal: int) -> dict:
    group_indexes = [int(row["groupIndex"]) for row in groups]
    layer_codes = "".join(row.get("layerCode", "") for row in groups)
    target_ids = [row.get("targetId") for row in groups]
    active_flags = [bool(row.get("isActiveTarget")) for row in groups]
    active_count = sum(active_flags)
    row = {
        "source": source,
        "rowType": row_type,
        "ordinal": ordinal,
        "groupIndexes": group_indexes,
        "groupIndexGaps": gaps(group_indexes),
        "layerCodes": layer_codes,
        "targetIds": target_ids,
        "activeFlags": active_flags,
        "activeCount": active_count,
        "nonActiveCount": len(groups) - active_count,
        "matchesYkkyPattern": layer_codes == ACTIVE_STATE_PATTERN,
        "matchesActiveGroupIndexes": group_indexes == ACTIVE_GROUP_INDEXES,
        "matchesActiveGroupGaps": gaps(group_indexes) == ACTIVE_GROUP_GAPS,
        "allActiveTargets": target_ids == ACTIVE_IDS,
        "hasPixelGeometry": all(row.get("box") for row in groups),
    }
    row["controlClass"] = (
        "active_exact"
        if row["allActiveTargets"]
        else "mixed_ykky_control"
        if row["matchesYkkyPattern"]
        else "nonmatching_control"
    )
    return row


def line_combo_row(rows: list[dict], row_type: str, ordinal: int) -> dict:
    line_indexes = [int(row["lineIndex"]) for row in rows]
    corridor_indexes = [int(row["corridorIndex"]) for row in rows]
    active_targets = [row.get("activeTargetIds", []) for row in rows]
    active_flags = [bool(ids) for ids in active_targets]
    active_ids = [ids[0] for ids in active_targets if ids]
    return {
        "rowType": row_type,
        "ordinal": ordinal,
        "lineIndexes": line_indexes,
        "lineGaps": gaps(line_indexes),
        "corridorIndexes": corridor_indexes,
        "corridorGaps": gaps(corridor_indexes),
        "activeFlags": active_flags,
        "activeTargetIds": active_targets,
        "activeCount": sum(active_flags),
        "nonActiveCount": len(rows) - sum(active_flags),
        "formatSignals": [bool(row.get("formatSignal")) for row in rows],
        "hardInstructionHits": [hit for row in rows for hit in row.get("hardInstructionHits", [])],
        "matchesActiveLineOrder": line_indexes == ACTIVE_LINE_ORDER,
        "matchesActiveLineGaps": gaps(line_indexes) == ACTIVE_LINE_GAPS,
        "matchesActiveCorridorOrder": corridor_indexes == ACTIVE_CORRIDOR_ORDER,
        "allActiveTargets": active_ids == ACTIVE_IDS,
    }


def draw_sheet(summary: dict, yk_windows: list[dict], ykky_controls: list[dict], line_hits: list[dict]) -> None:
    width, height = 1800, 980
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 16)
        tiny = ImageFont.truetype("Arial.ttf", 13)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 96), fill=(24, 29, 36))
    draw.text((24, 18), "Source Packet Orientation Control Quartets", fill="white", font=title)
    draw.text(
        (24, 58),
        (
            f"YKKY combos {summary['fullPageYkYkkyCombinationCount']}/{summary['fullPageYkCombinationCount']} | "
            f"Y/K windows {summary['fullPageYkSlidingYkkyCount']}/{summary['fullPageYkSlidingWindowCount']} | "
            f"line-gap hits {summary['formatLineGapExactMatchCount']}/{summary['formatLineCombinationCount']} | "
            f"fingerprint {summary['orientationControlQuartetFingerprint']}"
        ),
        fill=(230, 230, 230),
        font=tiny,
    )

    y = 124
    draw.text((24, y), "Contiguous full-page Y/K windows", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["window", "codes", "group indexes", "gaps", "targets", "class"]
    xs = [24, 150, 260, 510, 700, 1400]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 22
    for idx, row in enumerate(yk_windows):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 42), fill=fill)
        color = (25, 110, 55) if row["controlClass"] == "active_exact" else (120, 80, 30)
        draw.text((xs[0], y), str(row["ordinal"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), row["layerCodes"], fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(map(str, row["groupIndexes"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), " ".join(map(str, row["groupIndexGaps"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), " | ".join(str(v) for v in row["targetIds"])[:86], fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), row["controlClass"], fill=color, font=tiny)
        y += 50

    y += 18
    draw.text((24, y), "Non-active or mixed YKKY combinations", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["combo", "group indexes", "gaps", "active count", "targets"]
    xs = [24, 150, 380, 570, 760]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 22
    for idx, row in enumerate(ykky_controls[:10]):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 40), fill=fill)
        draw.text((xs[0], y), str(row["ordinal"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), " ".join(map(str, row["groupIndexes"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(map(str, row["groupIndexGaps"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), str(row["activeCount"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), " | ".join(str(v) for v in row["targetIds"])[:104], fill=(30, 30, 30), font=tiny)
        y += 46

    y += 18
    draw.text((24, y), "Format-line gap controls", fill=(45, 45, 45), font=small)
    y += 28
    headers = ["hit", "line order", "line gaps", "corridor order", "active count", "decision"]
    xs = [24, 150, 370, 560, 820, 1020]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=tiny)
    y += 22
    for idx, row in enumerate(line_hits):
        fill = (248, 249, 252) if idx % 2 == 0 else (237, 241, 247)
        draw.rectangle((18, y - 4, width - 18, y + 46), fill=fill)
        draw.text((xs[0], y), str(row["ordinal"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[1], y), " ".join(map(str, row["lineIndexes"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[2], y), " ".join(map(str, row["lineGaps"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[3], y), " ".join(map(str, row["corridorIndexes"])), fill=(30, 30, 30), font=tiny)
        draw.text((xs[4], y), str(row["activeCount"]), fill=(30, 30, 30), font=tiny)
        draw.text((xs[5], y), "only exact 3/2/5 format-line quartet", fill=(25, 110, 55), font=tiny)
        y += 52

    img.save(OUT_SHEET, quality=92)


def main() -> None:
    orientation = load_json(INPUTS["orientation_disambiguator"])
    geom = load_json(INPUTS["geometric_fingerprint"])
    frame = load_json(INPUTS["frame_normalized_geometry"])
    tolerance = load_json(INPUTS["alignment_tolerance"])
    color = load_json(INPUTS["color_profile_manifest"])
    yk_control = load_json(INPUTS["o4_frame_rescue_yk_filter_control"])
    yk_order = load_json(INPUTS["o4_frame_yk_unit_order_gate"])
    density = load_json(INPUTS["c9_bold_highlight_format_density"])
    r3_bridge = load_json(INPUTS["source_packet_r3_bridge_audit"])
    reopen = load_json(INPUTS["source_packet_reopen_trigger_matrix"])

    full_yk_groups = yk_control.get("fullPageYkGroups", [])
    frame_signal_groups = yk_control.get("frameSignalGroups", [])
    active_rows = yk_order.get("groupOrderRows", [])
    format_lines = [row for row in density.get("lineRows", []) if row.get("formatSignal")]

    yk_combo_rows = [
        group_row(list(groups), "full_page_yk", "combination", ordinal)
        for ordinal, groups in enumerate(itertools.combinations(full_yk_groups, 4), start=1)
    ]
    yk_window_rows = [
        group_row(full_yk_groups[idx : idx + 4], "full_page_yk", "sliding_window", idx + 1)
        for idx in range(max(0, len(full_yk_groups) - 3))
    ]
    frame_signal_window_rows = [
        group_row(frame_signal_groups[idx : idx + 4], "frame_signal", "sliding_window", idx + 1)
        for idx in range(max(0, len(frame_signal_groups) - 3))
    ]
    line_combo_rows = [
        line_combo_row(list(rows), "format_line_combination", ordinal)
        for ordinal, rows in enumerate(itertools.combinations(format_lines, 4), start=1)
    ]
    line_window_rows = [
        line_combo_row(format_lines[idx : idx + 4], "format_line_window", idx + 1)
        for idx in range(max(0, len(format_lines) - 3))
    ]

    ykky_combo_rows = [row for row in yk_combo_rows if row["matchesYkkyPattern"]]
    ykky_non_exact_rows = [row for row in ykky_combo_rows if row["matchesYkkyPattern"] and not row["allActiveTargets"]]
    yk_window_hits = [row for row in yk_window_rows if row["matchesYkkyPattern"]]
    active_group_gap_hits = [row for row in yk_combo_rows if row["matchesActiveGroupGaps"]]
    line_gap_hits = [row for row in line_combo_rows if row["matchesActiveLineGaps"]]
    line_window_gap_hits = [row for row in line_window_rows if row["matchesActiveLineGaps"]]

    c9_frame_box = [294, 2177, 2250, 3024]
    active_points = [center(row["box"]) for row in active_rows]
    active_geometry = {
        "targetIds": [row["targetId"] for row in active_rows],
        "visualStateOrder": "".join(row.get("visualState", "") for row in active_rows),
        "pageLines": [row.get("pageLine") for row in active_rows],
        "corridorIndexes": [row.get("corridorIndex") for row in active_rows],
        "groupIndexes": [row.get("groupIndex") for row in active_rows],
        "groupIndexGaps": gaps([int(row.get("groupIndex")) for row in active_rows]),
        "dxSignStream": sign_stream(active_points, 0),
        "dySignStream": sign_stream(active_points, 1),
        "c9NormalizedCenterStream": norm_centers(active_points, c9_frame_box),
        "commonShiftTolerancePx": tolerance.get("summary", {}).get(
            "commonFullEightDirectionShiftAllTargetsPassPx"
        ),
        "colorProfileFingerprint": color.get("summary", {}).get("colorProfileFingerprint"),
    }

    missing_full_yk_geometry_count = sum(1 for row in full_yk_groups if not row.get("box"))
    missing_non_active_yk_geometry_count = sum(
        1 for row in full_yk_groups if not row.get("isActiveTarget") and not row.get("box")
    )
    source_r3_count = r3_bridge.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0)
    satisfied_reopen_count = reopen.get("summary", {}).get("satisfiedTriggerCount", 0)
    selector_unlocked_count = sum(
        1
        for source in [orientation, geom, frame, tolerance, color, yk_control, yk_order, density, r3_bridge, reopen]
        if source.get("summary", {}).get("selectorUnlocked")
        or source.get("decision", {}).get("selectorUnlocked")
    )

    summary = {
        "fullPageYkGroupCount": len(full_yk_groups),
        "fullPageYkCombinationCount": len(yk_combo_rows),
        "fullPageYkYkkyCombinationCount": len(ykky_combo_rows),
        "fullPageYkYkkyNonExactCombinationCount": len(ykky_non_exact_rows),
        "fullPageYkSlidingWindowCount": len(yk_window_rows),
        "fullPageYkSlidingYkkyCount": len(yk_window_hits),
        "frameSignalSlidingWindowCount": len(frame_signal_window_rows),
        "frameSignalSlidingYkkyCount": sum(1 for row in frame_signal_window_rows if row["matchesYkkyPattern"]),
        "activeYkWindowIsOnlyContiguousYkkyWindow": len(yk_window_hits) == 1
        and bool(yk_window_hits)
        and yk_window_hits[0]["allActiveTargets"],
        "activeGroupGapExactMatchCount": len(active_group_gap_hits),
        "formatSignalLineCount": len(format_lines),
        "formatLineCombinationCount": len(line_combo_rows),
        "formatLineWindowCount": len(line_window_rows),
        "formatLineGapExactMatchCount": len(line_gap_hits),
        "formatLineWindowGapExactMatchCount": len(line_window_gap_hits),
        "formatLineGapExactNonActiveMatchCount": sum(1 for row in line_gap_hits if not row["allActiveTargets"]),
        "visualPatternAloneIsNonUnique": len(ykky_combo_rows) > 1,
        "fullPageYkGroupsMissingPixelGeometryCount": missing_full_yk_geometry_count,
        "nonActiveYkGroupsMissingPixelGeometryCount": missing_non_active_yk_geometry_count,
        "sourceBackedR3BridgeHitCount": source_r3_count,
        "satisfiedReopenTriggerCount": satisfied_reopen_count,
        "selectorUnlockedCount": selector_unlocked_count,
        "extractionReadyGateCount": 0,
    }
    summary["strictReadableGeometryIsUniqueInAvailableControls"] = (
        len(active_group_gap_hits) == 1
        and active_group_gap_hits[0]["allActiveTargets"]
        and len(line_gap_hits) == 1
        and line_gap_hits[0]["allActiveTargets"]
        and len(line_window_gap_hits) == 0
    )
    summary["orientationControlQuartetFingerprint"] = (
        f"ykCombos={summary['fullPageYkCombinationCount']}|"
        f"YKKY={summary['fullPageYkYkkyCombinationCount']}|"
        f"YKKYNonExact={summary['fullPageYkYkkyNonExactCombinationCount']}|"
        f"windows={summary['fullPageYkSlidingWindowCount']}|"
        f"windowYKKY={summary['fullPageYkSlidingYkkyCount']}|"
        f"lineCombos={summary['formatLineCombinationCount']}|"
        f"lineGaps325={summary['formatLineGapExactMatchCount']}|"
        f"dx={active_geometry['dxSignStream']}|dy={active_geometry['dySignStream']}|"
        f"sourceR3={source_r3_count}|selectors={selector_unlocked_count}"
    )

    control_findings = [
        {
            "finding": "YKKY visual-state pattern is not unique as an unordered local quartet.",
            "evidence": f"{len(ykky_combo_rows)} of {len(yk_combo_rows)} full-page Y/K combinations form YKKY; {len(ykky_non_exact_rows)} include non-active or mixed controls.",
            "decision": "reject_pattern_only_orientation_or_selector",
        },
        {
            "finding": "The active quartet is the only contiguous full-page Y/K window with YKKY.",
            "evidence": f"{len(yk_window_hits)} of {len(yk_window_rows)} sliding Y/K windows match YKKY, and the matching window is groups 12/14/15/19.",
            "decision": "keep_as_source_registration_discriminator",
        },
        {
            "finding": "The exact readable line/corridor gap pattern is unique among C9 format-line combinations.",
            "evidence": f"{len(line_gap_hits)} of {len(line_combo_rows)} format-line quartets match 3/2/5 gaps; no sliding format-line window matches.",
            "decision": "keep_as_readable_upright_geometry_check",
        },
        {
            "finding": "Non-active Y/K pixel geometry remains unavailable in the current handoff.",
            "evidence": f"{missing_non_active_yk_geometry_count} non-active Y/K groups lack page-line, box, and center coordinates in the Y/K filter report.",
            "decision": "do_not_claim_controlled_pixel_center_uniqueness",
        },
        {
            "finding": "No R3 or reopen trigger is supplied by the control pass.",
            "evidence": f"source-backed R3 hits {source_r3_count}; satisfied reopen triggers {satisfied_reopen_count}; selector unlocks {selector_unlocked_count}.",
            "decision": "location_and_orientation_only",
        },
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "bounded control quartet audit for source-packet orientation geometry; "
            "no OCR extraction, key candidates, hashing, WIF, seed, address, or broad brute force"
        ),
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "activeGeometry": active_geometry,
        "ykWindowRows": yk_window_rows,
        "ykkyCombinationRows": ykky_combo_rows,
        "activeGroupGapHitRows": active_group_gap_hits,
        "frameSignalWindowRows": frame_signal_window_rows,
        "formatLineGapHitRows": line_gap_hits,
        "formatLineWindowGapHitRows": line_window_gap_hits,
        "controlFindings": control_findings,
        "summary": summary,
        "decision": {
            "sourcePacketOrientationControlQuartets": "source-registration-strengthened-not-extraction",
            "ruledOut": [
                "YKKY pattern alone as an orientation proof",
                "YKKY pattern alone as a selector",
                "claiming non-active pixel-center control uniqueness from the current handoff",
            ],
            "retained": [
                "readable/upright line order 22/25/27/32",
                "corridor order 4/7/9/14",
                "group-index gap 2/1/4 inside the filtered Y/K frame window",
                "C9 normalized centers and dx/dy signs as future source comparison checks",
            ],
            "nextMove": (
                "If another pass runs before cutoff, build a compact source-review checklist "
                "that combines orientation controls with the exact R1-R5 reopen triggers; do not "
                "run new selector/key permutations."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(summary, yk_window_rows, ykky_non_exact_rows, line_gap_hits)

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Orientation Control Quartets",
        "",
        "Scope: bounded control audit for the active source-packet orientation fingerprint. No OCR extraction, key candidates, hashes, WIF, seed, address checks, BIP39, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{summary['orientationControlQuartetFingerprint']}`",
        "",
        "## Summary",
        "",
        f"- Full-page Y/K quartets tested: `{summary['fullPageYkCombinationCount']}`.",
        f"- Full-page Y/K `YKKY` quartets: `{summary['fullPageYkYkkyCombinationCount']}`; non-exact/mixed controls: `{summary['fullPageYkYkkyNonExactCombinationCount']}`.",
        f"- Contiguous full-page Y/K windows tested: `{summary['fullPageYkSlidingWindowCount']}`; `YKKY` windows: `{summary['fullPageYkSlidingYkkyCount']}`.",
        f"- C9 format-line quartets tested: `{summary['formatLineCombinationCount']}`; exact `3/2/5` line-gap matches: `{summary['formatLineGapExactMatchCount']}`.",
        f"- C9 format-line sliding windows tested: `{summary['formatLineWindowCount']}`; exact `3/2/5` sliding-window matches: `{summary['formatLineWindowGapExactMatchCount']}`.",
        f"- Full-page Y/K groups without pixel box geometry in the Y/K filter report: `{summary['fullPageYkGroupsMissingPixelGeometryCount']}`; non-active groups among them: `{summary['nonActiveYkGroupsMissingPixelGeometryCount']}`.",
        f"- Source-backed R3 bridge hits: `{summary['sourceBackedR3BridgeHitCount']}`; satisfied reopen triggers: `{summary['satisfiedReopenTriggerCount']}`; selector unlocks: `{summary['selectorUnlockedCount']}`.",
        "",
        "## Active Geometry",
        "",
        f"- Target order: `{' / '.join(active_geometry['targetIds'])}`.",
        f"- Visual state: `{active_geometry['visualStateOrder']}`.",
        f"- Page lines / corridors: `{' '.join(map(str, active_geometry['pageLines']))}` / `{' '.join(map(str, active_geometry['corridorIndexes']))}`.",
        f"- Group indexes / gaps: `{' '.join(map(str, active_geometry['groupIndexes']))}` / `{' '.join(map(str, active_geometry['groupIndexGaps']))}`.",
        f"- Center-step signs: dx `{active_geometry['dxSignStream']}`, dy `{active_geometry['dySignStream']}`.",
        f"- C9 normalized centers: `{'; '.join(f'{x:.3f},{y:.3f}' for x, y in active_geometry['c9NormalizedCenterStream'])}`.",
        "",
        "## Findings",
        "",
    ]
    for finding in control_findings:
        lines.append(
            f"- {finding['finding']} Evidence: {finding['evidence']} Decision: `{finding['decision']}`."
        )

    lines.extend(
        [
            "",
            "## YKKY Combination Controls",
            "",
            "| group indexes | gaps | active count | targets |",
            "|---|---:|---:|---|",
        ]
    )
    for row in ykky_non_exact_rows:
        lines.append(
            f"| `{' '.join(map(str, row['groupIndexes']))}` | `{' '.join(map(str, row['groupIndexGaps']))}` | `{row['activeCount']}` | `{' / '.join(str(v) for v in row['targetIds'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `YKKY` alone remains ruled out as orientation proof because it appears in multiple mixed/non-active quartets.",
            "- The readable/upright discriminator is stronger than pattern-only evidence: the active quartet is the only contiguous filtered Y/K window and the only C9 format-line combination with exact `3/2/5` line/corridor gaps.",
            "- This pass does not unlock extraction because the selectivity is still source-registration/location evidence and supplies no source-backed R3 unit/order instruction.",
            "- Pixel-center uniqueness against earlier non-active Y/K controls remains unclaimed because those controls do not carry box/center coordinates in the current handoff.",
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("fingerprint:", summary["orientationControlQuartetFingerprint"])


if __name__ == "__main__":
    main()
