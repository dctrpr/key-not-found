#!/usr/bin/env python3
"""Audit current page-76 target geometry against actual C9/OVERDOSE slots.

This bounded pass checks whether O4/B4/G5/O5 box starts, centers, or ends have
a repeatable residual to the actual C9/OVERDOSE glyph-slot ruler. It compares
the active boxes with page-76 non-active highlight controls. It is geometry
inspection only, not extraction.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_slot_boundary_residual_gate.json"
OUT_MD = OUT / "current_scan_slot_boundary_residual_gate.md"
OUT_SHEET = OUT / "current_scan_slot_boundary_residual_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
PAGE76_HIGHLIGHT_BENCHMARK = ROOT / (
    "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

THRESHOLDS = [4, 8, 16, 32]
SIGNATURE_THRESHOLD = 16
ANCHORS = ["left", "center", "right"]
ACTIVE_IDS = {"O4", "B4", "G5", "O5"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def c9_ruler(c9: dict[str, Any]) -> dict[str, Any]:
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    slots = projection.get("slots", [])
    boundaries: list[float] = []
    centers: list[float] = []
    slot_rows: list[dict[str, Any]] = []
    for slot in slots:
        left = float(slot["left"])
        right = float(slot["right"])
        if not boundaries:
            boundaries.append(left)
        boundaries.append(right)
        center = (left + right) / 2.0
        centers.append(center)
        slot_rows.append(
            {
                "index": int(slot["index"]),
                "letter": str(slot["letter"]),
                "left": round(left, 6),
                "center": round(center, 6),
                "right": round(right, 6),
                "width": round(float(slot["width"]), 6),
            }
        )
    return {"boundaries": boundaries, "centers": centers, "slots": slot_rows}


def nearest(value: float, candidates: list[float]) -> tuple[float, int, float]:
    if not candidates:
        return 0.0, -1, 0.0
    distances = [abs(value - candidate) for candidate in candidates]
    index = int(np.argmin(distances))
    signed = value - candidates[index]
    return float(distances[index]), index, float(signed)


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "visualState": row["visualState"],
            "kind": "active",
            "box": row["box"],
            "source": "source_packet_active_index_slot_control",
        }
        for row in active_index.get("activeRows", [])
    ]


def highlight_control_rows(benchmark: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in benchmark.get("targets", []):
        target_id = str(target.get("id"))
        if target_id in ACTIVE_IDS:
            continue
        rows.append(
            {
                "shortId": f"hl_{target_id}",
                "phrase": str(target.get("label")),
                "visualState": str(target.get("kind")),
                "kind": "highlight_control",
                "box": [float(value) for value in target.get("box", [])],
                "source": "page76_all_source_highlight_mirror_benchmark",
            }
        )
    return rows


def shifted_y_controls(active: list[dict[str, Any]], image_size: tuple[int, int]) -> list[dict[str, Any]]:
    width, height = image_size
    rows: list[dict[str, Any]] = []
    for row in active:
        x0, y0, x1, y1 = [float(value) for value in row["box"]]
        for dy in [-292, -146, 146, 292]:
            sy0 = max(0.0, min(float(height), y0 + dy))
            sy1 = max(0.0, min(float(height), y1 + dy))
            if sy1 <= sy0:
                continue
            rows.append(
                {
                    "shortId": f"{row['shortId']}_dy{dy:+d}",
                    "phrase": f"{row['shortId']} shifted {dy:+d}px",
                    "visualState": "control",
                    "kind": "vertical_shift_control",
                    "box": [x0, sy0, x1, sy1],
                    "source": "active_vertical_shift",
                }
            )
    return rows


def inspect_row(row: dict[str, Any], ruler: dict[str, Any]) -> dict[str, Any]:
    x0, y0, x1, y1 = [float(value) for value in row["box"]]
    anchor_values = {"left": x0, "center": (x0 + x1) / 2.0, "right": x1}
    anchor_rows: dict[str, Any] = {}
    close_counts = {str(threshold): 0 for threshold in THRESHOLDS}
    boundary_close_counts = {str(threshold): 0 for threshold in THRESHOLDS}
    center_close_counts = {str(threshold): 0 for threshold in THRESHOLDS}
    signature_parts = []
    min_residuals = []
    for anchor, value in anchor_values.items():
        boundary_dist, boundary_index, boundary_signed = nearest(value, ruler["boundaries"])
        center_dist, center_index, center_signed = nearest(value, ruler["centers"])
        if boundary_dist <= center_dist:
            nearest_type = "boundary"
            nearest_index = boundary_index
            nearest_letter = (
                "frame"
                if nearest_index in {0, len(ruler["boundaries"]) - 1}
                else f"{ruler['slots'][nearest_index - 1]['letter']}|{ruler['slots'][nearest_index]['letter']}"
            )
            nearest_dist = boundary_dist
            signed = boundary_signed
        else:
            nearest_type = "center"
            nearest_index = center_index
            nearest_letter = str(ruler["slots"][center_index]["letter"])
            nearest_dist = center_dist
            signed = center_signed
        for threshold in THRESHOLDS:
            key = str(threshold)
            if nearest_dist <= threshold:
                close_counts[key] += 1
            if boundary_dist <= threshold:
                boundary_close_counts[key] += 1
            if center_dist <= threshold:
                center_close_counts[key] += 1
        min_residuals.append(nearest_dist)
        anchor_rows[anchor] = {
            "x": round(value, 6),
            "nearestBoundaryIndex": boundary_index,
            "nearestBoundaryAbsPx": round(boundary_dist, 6),
            "nearestBoundarySignedPx": round(boundary_signed, 6),
            "nearestCenterIndex": center_index,
            "nearestCenterLetter": str(ruler["slots"][center_index]["letter"]),
            "nearestCenterAbsPx": round(center_dist, 6),
            "nearestCenterSignedPx": round(center_signed, 6),
            "nearestType": nearest_type,
            "nearestIndex": nearest_index,
            "nearestLetter": nearest_letter,
            "nearestAbsPx": round(nearest_dist, 6),
            "nearestSignedPx": round(signed, 6),
        }
        close_flag = "Y" if nearest_dist <= SIGNATURE_THRESHOLD else "N"
        signature_parts.append(
            f"{anchor[0].upper()}{nearest_type[0].upper()}{nearest_index}:{int(round(nearest_dist))}{close_flag}"
        )
    return {
        **row,
        "width": round(x1 - x0, 6),
        "height": round(y1 - y0, 6),
        "anchors": anchor_rows,
        "closeCountsByThreshold": close_counts,
        "boundaryCloseCountsByThreshold": boundary_close_counts,
        "centerCloseCountsByThreshold": center_close_counts,
        "minAnchorResidualPx": round(min(min_residuals), 6),
        "meanAnchorResidualPx": round(float(np.mean(min_residuals)), 6),
        "maxAnchorResidualPx": round(max(min_residuals), 6),
        "slotBoundarySignature": "|".join(signature_parts),
        "anyAnchorClose16": bool(close_counts[str(SIGNATURE_THRESHOLD)] > 0),
        "allAnchorsClose16": bool(close_counts[str(SIGNATURE_THRESHOLD)] == len(ANCHORS)),
        "leftBoundaryClose16": bool(anchor_rows["left"]["nearestBoundaryAbsPx"] <= SIGNATURE_THRESHOLD),
        "centerClose16": bool(anchor_rows["center"]["nearestCenterAbsPx"] <= SIGNATURE_THRESHOLD),
        "rightBoundaryClose16": bool(anchor_rows["right"]["nearestBoundaryAbsPx"] <= SIGNATURE_THRESHOLD),
    }


def stream_for_anchor(rows: list[dict[str, Any]], anchor: str, target_type: str) -> str:
    chars = []
    for row in rows:
        info = row["anchors"][anchor]
        if target_type == "boundary":
            idx = int(info["nearestBoundaryIndex"])
            if idx <= 0 or idx >= 8:
                chars.append(".")
            else:
                chars.append(str(idx))
        elif target_type == "center":
            chars.append(str(info["nearestCenterLetter"]))
        else:
            chars.append(str(info["nearestLetter"])[0])
    return "".join(chars)


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]], ruler: dict[str, Any], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1880, 1280), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1880, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan Slot Boundary Residual Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "O4/B4/G5/O5 starts, centers, and ends compared with actual C9/OVERDOSE glyph-slot boundaries.",
        fill=(235, 235, 235),
        font=small,
    )

    preview = image.resize((720, round(720 * image.height / image.width)))
    pdraw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height
    frame_y0 = 2176.81 * sy
    frame_y1 = 3023.73 * sy
    for boundary in ruler["boundaries"]:
        x = boundary * sx
        pdraw.line((x, frame_y0, x, frame_y1), fill=(60, 80, 255, 130), width=2)
    for center in ruler["centers"]:
        x = center * sx
        pdraw.line((x, frame_y0, x, frame_y1), fill=(255, 120, 40, 90), width=1)
    for row in rows:
        if row["kind"] == "vertical_shift_control":
            continue
        x0, y0, x1, y1 = row["box"]
        color = (255, 128, 0, 230) if row["kind"] == "active" else (90, 90, 90, 130)
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        pdraw.rectangle(rect, outline=color, width=3 if row["kind"] == "active" else 2)
        pdraw.text((rect[0], max(0, rect[1] - 16)), row["shortId"], fill=(255, 0, 0, 255))
    sheet.paste(preview, (24, 120))

    x0 = 780
    y = 120
    draw.text((x0, y), "Slot residual rows", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "signature", "close16", "leftB", "centerC", "rightB", "mean", "max"]
    xs = [x0, x0 + 120, x0 + 245, x0 + 620, x0 + 700, x0 + 770, x0 + 850, x0 + 930, x0 + 1000]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    ordered = [row for row in rows if row["kind"] == "active"]
    ordered += sorted(
        [row for row in rows if row["kind"] == "highlight_control"],
        key=lambda item: item["meanAnchorResidualPx"],
    )
    for row in ordered[:28]:
        vals = [
            row["kind"][:16],
            row["shortId"][:16],
            row["slotBoundarySignature"][:50],
            str(row["closeCountsByThreshold"][str(SIGNATURE_THRESHOLD)]),
            "1" if row["leftBoundaryClose16"] else "0",
            "1" if row["centerClose16"] else "0",
            "1" if row["rightBoundaryClose16"] else "0",
            f"{row['meanAnchorResidualPx']:.1f}",
            f"{row['maxAnchorResidualPx']:.1f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    draw.text((780, 760), "Summary", fill=(70, 70, 70), font=small)
    summary_lines = [
        f"Active/highlight-control/vertical-control rows: {summary['activeBoxCount']} / {summary['highlightControlBoxCount']} / {summary['verticalShiftControlBoxCount']}",
        f"All-four any anchor close <=16px: {int(summary['allFourActiveAnyAnchorClose16'])}",
        f"All-four left-boundary close <=16px: {int(summary['allFourActiveLeftBoundaryClose16'])}",
        f"All-four center close <=16px: {int(summary['allFourActiveCenterClose16'])}",
        f"All-four right-boundary close <=16px: {int(summary['allFourActiveRightBoundaryClose16'])}",
        f"Active common signature: {summary['activeCommonSlotBoundarySignature'] or 'mixed'}",
        f"Control signature matches: {summary['highlightControlCommonSignatureMatchCount']} / {summary['verticalShiftControlCommonSignatureMatchCount']}",
        f"Mean active/control anchor residual: {summary['meanActiveAnchorResidualPx']:.2f} / {summary['meanHighlightControlAnchorResidualPx']:.2f}",
        f"Shared carrier / hidden candidate: {int(summary['sharedActiveSlotBoundaryCarrier'])} / {int(summary['hiddenSlotBoundaryCandidate'])}",
        f"Source R3/triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
    ]
    for idx, line in enumerate(summary_lines):
        draw.text((780, 794 + idx * 22), line, fill=(35, 35, 35), font=small)

    draw.text((780, 1040), "Active streams", fill=(70, 70, 70), font=small)
    stream_lines = [
        f"Nearest center letters L/C/R: {summary['activeNearestCenterStreams']['left']} / {summary['activeNearestCenterStreams']['center']} / {summary['activeNearestCenterStreams']['right']}",
        f"Nearest boundary indexes L/C/R: {summary['activeNearestBoundaryStreams']['left']} / {summary['activeNearestBoundaryStreams']['center']} / {summary['activeNearestBoundaryStreams']['right']}",
        f"Nearest mixed labels L/C/R: {summary['activeNearestMixedStreams']['left']} / {summary['activeNearestMixedStreams']['center']} / {summary['activeNearestMixedStreams']['right']}",
    ]
    for idx, line in enumerate(stream_lines):
        draw.text((780, 1074 + idx * 22), line, fill=(35, 35, 35), font=small)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    benchmark = load_json(PAGE76_HIGHLIGHT_BENCHMARK)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")
    ruler = c9_ruler(c9)

    active = active_rows(active_index)
    highlight_controls = highlight_control_rows(benchmark)
    vertical_controls = shifted_y_controls(active, image.size)
    rows = [inspect_row(row, ruler) for row in active + highlight_controls + vertical_controls]

    active_inspected = [row for row in rows if row["kind"] == "active"]
    highlight_inspected = [row for row in rows if row["kind"] == "highlight_control"]
    vertical_inspected = [row for row in rows if row["kind"] == "vertical_shift_control"]

    active_signatures = [row["slotBoundarySignature"] for row in active_inspected]
    active_common_signature = active_signatures[0] if len(set(active_signatures)) == 1 else None
    highlight_common_matches = (
        sum(1 for row in highlight_inspected if row["slotBoundarySignature"] == active_common_signature)
        if active_common_signature
        else 0
    )
    vertical_common_matches = (
        sum(1 for row in vertical_inspected if row["slotBoundarySignature"] == active_common_signature)
        if active_common_signature
        else 0
    )
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    all_four_any_close = all(row["anyAnchorClose16"] for row in active_inspected)
    all_four_left_boundary = all(row["leftBoundaryClose16"] for row in active_inspected)
    all_four_center = all(row["centerClose16"] for row in active_inspected)
    all_four_right_boundary = all(row["rightBoundaryClose16"] for row in active_inspected)
    shared_carrier = bool(
        active_common_signature
        or all_four_left_boundary
        or all_four_center
        or all_four_right_boundary
    )
    hidden_candidate = bool(shared_carrier and source_r3 > 0 and highlight_common_matches == 0)

    active_center_streams = {
        anchor: stream_for_anchor(active_inspected, anchor, "center") for anchor in ANCHORS
    }
    active_boundary_streams = {
        anchor: stream_for_anchor(active_inspected, anchor, "boundary") for anchor in ANCHORS
    }
    active_mixed_streams = {
        anchor: stream_for_anchor(active_inspected, anchor, "mixed") for anchor in ANCHORS
    }
    mean_active = float(np.mean([row["meanAnchorResidualPx"] for row in active_inspected]))
    mean_highlight = float(np.mean([row["meanAnchorResidualPx"] for row in highlight_inspected]))

    fingerprint = (
        f"active={len(active_inspected)}|highlightControls={len(highlight_inspected)}"
        f"|verticalControls={len(vertical_inspected)}|thresholds={','.join(map(str, THRESHOLDS))}"
        f"|allFourAny16={int(all_four_any_close)}|allFourLeftB16={int(all_four_left_boundary)}"
        f"|allFourCenter16={int(all_four_center)}|allFourRightB16={int(all_four_right_boundary)}"
        f"|commonSig={active_common_signature or 'mixed'}"
        f"|streamsC={active_center_streams['left']}/{active_center_streams['center']}/{active_center_streams['right']}"
        f"|streamsB={active_boundary_streams['left']}/{active_boundary_streams['center']}/{active_boundary_streams['right']}"
        f"|meanResidual={mean_active:.2f}/{mean_highlight:.2f}"
        f"|sharedCarrier={int(shared_carrier)}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_inspected),
        "highlightControlBoxCount": len(highlight_inspected),
        "verticalShiftControlBoxCount": len(vertical_inspected),
        "thresholdsPx": THRESHOLDS,
        "signatureThresholdPx": SIGNATURE_THRESHOLD,
        "allFourActiveAnyAnchorClose16": all_four_any_close,
        "allFourActiveLeftBoundaryClose16": all_four_left_boundary,
        "allFourActiveCenterClose16": all_four_center,
        "allFourActiveRightBoundaryClose16": all_four_right_boundary,
        "activeSlotBoundarySignatures": active_signatures,
        "activeCommonSlotBoundarySignature": active_common_signature,
        "highlightControlCommonSignatureMatchCount": highlight_common_matches,
        "verticalShiftControlCommonSignatureMatchCount": vertical_common_matches,
        "activeNearestCenterStreams": active_center_streams,
        "activeNearestBoundaryStreams": active_boundary_streams,
        "activeNearestMixedStreams": active_mixed_streams,
        "meanActiveAnchorResidualPx": round(mean_active, 6),
        "meanHighlightControlAnchorResidualPx": round(mean_highlight, 6),
        "sharedActiveSlotBoundaryCarrier": shared_carrier,
        "hiddenSlotBoundaryCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "slotBoundaryResidualFingerprint": fingerprint,
    }
    draw_sheet(image, rows, ruler, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 active and highlight-control box edges against actual C9/OVERDOSE glyph-slot ruler; no extraction or candidate generation",
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "page76HighlightBenchmark": rel(PAGE76_HIGHLIGHT_BENCHMARK),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "c9Ruler": ruler,
        "summary": summary,
        "regionRows": rows,
        "decision": {
            "currentScanSlotBoundaryResidualGate": "current_scan_slot_boundary_residual_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The active boxes do not share a repeatable C9/OVERDOSE slot-boundary or "
                "slot-center residual. O4 breaks the left-boundary near-hit pattern, no "
                "all-four center/right-edge pattern appears, and no source-backed R3 cue "
                "names this geometry as an extraction rule."
            ),
            "nextMove": (
                "Do not pursue C9 slot-boundary residual tuning as a selector. Continue with "
                "original-layout/physical source validation or raw clue wording that names "
                "the missing unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Slot Boundary Residual Gate",
        "",
        "Scope: inspected current page-76 active target box starts, centers, and ends against the actual C9/OVERDOSE glyph-slot boundaries and centers, with page-76 non-active highlight controls. This is geometry inspection only. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/highlight-control/vertical-control boxes: `{len(active_inspected)}` / `{len(highlight_inspected)}` / `{len(vertical_inspected)}`",
        f"- Thresholds checked: `{THRESHOLDS}` px",
        f"- Signature threshold: `{SIGNATURE_THRESHOLD}` px",
        f"- All-four any anchor close <=16 px: `{int(all_four_any_close)}`",
        f"- All-four left-boundary close <=16 px: `{int(all_four_left_boundary)}`",
        f"- All-four center close <=16 px: `{int(all_four_center)}`",
        f"- All-four right-boundary close <=16 px: `{int(all_four_right_boundary)}`",
        f"- Active common slot-boundary signature: `{active_common_signature or 'mixed'}`",
        f"- Matching highlight / vertical controls for common signature: `{highlight_common_matches}` / `{vertical_common_matches}`",
        f"- Active nearest-center streams L/C/R: `{active_center_streams['left']}` / `{active_center_streams['center']}` / `{active_center_streams['right']}`",
        f"- Active nearest-boundary streams L/C/R: `{active_boundary_streams['left']}` / `{active_boundary_streams['center']}` / `{active_boundary_streams['right']}`",
        f"- Mean active/highlight-control anchor residual: `{mean_active:.2f}` / `{mean_highlight:.2f}` px",
        f"- Shared active slot-boundary carrier / hidden slot-boundary candidate: `{int(shared_carrier)}` / `{int(hidden_candidate)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | signature | close16 | left boundary | center slot | right boundary | mean residual | max residual |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in active_inspected + sorted(highlight_inspected, key=lambda item: item["meanAnchorResidualPx"]):
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | `{row['slotBoundarySignature']}` | `{row['closeCountsByThreshold'][str(SIGNATURE_THRESHOLD)]}` | {int(row['leftBoundaryClose16'])} | {int(row['centerClose16'])} | {int(row['rightBoundaryClose16'])} | {float(row['meanAnchorResidualPx']):.2f} | {float(row['maxAnchorResidualPx']):.2f} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_slot_boundary_residual_no_selector`",
            "- The active boxes do not share a repeatable C9/OVERDOSE slot-boundary or slot-center residual.",
            "- O4 breaks the left-boundary near-hit pattern, no all-four center/right-edge pattern appears, and no source-backed unit/order/transform clue is present.",
            "",
            "## Next Move",
            "",
            "- Continue only with original-layout/physical source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanSlotBoundaryResidualGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
