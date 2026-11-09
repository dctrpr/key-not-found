#!/usr/bin/env python3
"""Audit current-scan JPEG 8x8 block-grid behavior on page 76.

This bounded pass treats the current page-76 scan/PDF raster as source material
and checks whether active target boxes or projected OVERDOSE slots are marked by
JPEG block-grid phase or block-boundary energy. It is a visual/source artifact
gate, not a steganographic extraction or key search.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_jpeg_block_grid_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_jpeg_block_grid_gate.json"
OUT_MD = OUT / "current_scan_jpeg_block_grid_gate.md"
OUT_SHEET = OUT / "current_scan_jpeg_block_grid_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

BLOCK = 8
EDGE_HIT_TOLERANCE = 1.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def clamp_box(box: list[float], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = box
    return [
        max(0.0, min(float(width), x0)),
        max(0.0, min(float(height), y0)),
        max(0.0, min(float(width), x1)),
        max(0.0, min(float(height), y1)),
    ]


def distance_to_block_edge(value: float) -> float:
    phase = value % BLOCK
    return min(phase, BLOCK - phase)


def box_phase_metrics(box: list[float]) -> dict[str, Any]:
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    distances = {
        "left": distance_to_block_edge(x0),
        "right": distance_to_block_edge(x1),
        "top": distance_to_block_edge(y0),
        "bottom": distance_to_block_edge(y1),
        "centerX": distance_to_block_edge(cx),
        "centerY": distance_to_block_edge(cy),
    }
    return {
        "edgePhase": {
            "left": round(x0 % BLOCK, 6),
            "right": round(x1 % BLOCK, 6),
            "top": round(y0 % BLOCK, 6),
            "bottom": round(y1 % BLOCK, 6),
            "centerX": round(cx % BLOCK, 6),
            "centerY": round(cy % BLOCK, 6),
        },
        "edgeDistanceToBlock": {key: round(value, 6) for key, value in distances.items()},
        "strictEdgeHitCount": sum(
            1
            for key in ["left", "right", "top", "bottom"]
            if distances[key] <= EDGE_HIT_TOLERANCE
        ),
        "centerHitCount": sum(
            1 for key in ["centerX", "centerY"] if distances[key] <= EDGE_HIT_TOLERANCE
        ),
    }


def crop_array(image_arr: np.ndarray, box: list[float]) -> tuple[np.ndarray, int, int]:
    x0, y0, x1, y1 = [round(v) for v in box]
    x0 = max(0, min(image_arr.shape[1], x0))
    x1 = max(0, min(image_arr.shape[1], x1))
    y0 = max(0, min(image_arr.shape[0], y0))
    y1 = max(0, min(image_arr.shape[0], y1))
    return image_arr[y0:y1, x0:x1, :], x0, y0


def block_boundary_metrics(image_arr: np.ndarray, box: list[float]) -> dict[str, Any]:
    crop, x0, y0 = crop_array(image_arr, box)
    if crop.shape[0] < 2 or crop.shape[1] < 2:
        return {
            "verticalBoundaryEnergy": 0.0,
            "verticalNonBoundaryEnergy": 0.0,
            "horizontalBoundaryEnergy": 0.0,
            "horizontalNonBoundaryEnergy": 0.0,
            "boundaryEnergy": 0.0,
            "nonBoundaryEnergy": 0.0,
            "boundaryToNonBoundaryRatio": 0.0,
            "boundaryEnergyDelta": 0.0,
        }

    vertical_diff = np.abs(
        crop[:, 1:, :].astype(np.int16) - crop[:, :-1, :].astype(np.int16)
    ).mean(axis=2)
    vertical_global_x = np.arange(x0 + 1, x0 + crop.shape[1])
    vertical_boundary_mask = (vertical_global_x % BLOCK) == 0

    horizontal_diff = np.abs(
        crop[1:, :, :].astype(np.int16) - crop[:-1, :, :].astype(np.int16)
    ).mean(axis=2)
    horizontal_global_y = np.arange(y0 + 1, y0 + crop.shape[0])
    horizontal_boundary_mask = (horizontal_global_y % BLOCK) == 0

    v_boundary = vertical_diff[:, vertical_boundary_mask].mean() if vertical_boundary_mask.any() else 0.0
    v_non = vertical_diff[:, ~vertical_boundary_mask].mean() if (~vertical_boundary_mask).any() else 0.0
    h_boundary = horizontal_diff[horizontal_boundary_mask, :].mean() if horizontal_boundary_mask.any() else 0.0
    h_non = horizontal_diff[~horizontal_boundary_mask, :].mean() if (~horizontal_boundary_mask).any() else 0.0
    boundary = float(np.mean([v_boundary, h_boundary]))
    non_boundary = float(np.mean([v_non, h_non]))
    return {
        "verticalBoundaryEnergy": round(float(v_boundary), 6),
        "verticalNonBoundaryEnergy": round(float(v_non), 6),
        "horizontalBoundaryEnergy": round(float(h_boundary), 6),
        "horizontalNonBoundaryEnergy": round(float(h_non), 6),
        "boundaryEnergy": round(boundary, 6),
        "nonBoundaryEnergy": round(non_boundary, 6),
        "boundaryToNonBoundaryRatio": round(float(boundary / non_boundary), 6)
        if non_boundary
        else 0.0,
        "boundaryEnergyDelta": round(float(boundary - non_boundary), 6),
    }


def c9_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "shortId": f"slot{slot['index']}_{slot['letter']}",
                "phrase": f"C9 projected OVERDOSE slot {slot['letter']}",
                "kind": "overdose_slot",
                "box": [float(slot["left"]), float(frame[1]), float(slot["right"]), float(frame[3])],
            }
        )
    return rows


def shifted_control_boxes(active_boxes: list[dict[str, Any]], size: tuple[int, int]) -> list[dict[str, Any]]:
    width, height = size
    rows: list[dict[str, Any]] = []
    for box in active_boxes:
        x0, y0, x1, y1 = box["box"]
        for dy in [-292, -146, 146, 292]:
            shifted = clamp_box([x0, y0 + dy, x1, y1 + dy], width, height)
            if shifted[3] > shifted[1] and shifted[2] > shifted[0]:
                rows.append(
                    {
                        "shortId": f"{box['shortId']}_dy{dy:+d}",
                        "phrase": f"{box['shortId']} shifted {dy:+d}px",
                        "kind": "shifted_control",
                        "box": shifted,
                    }
                )
    return rows


def inspect_region(image_arr: np.ndarray, row: dict[str, Any]) -> dict[str, Any]:
    phase = box_phase_metrics(row["box"])
    boundary = block_boundary_metrics(image_arr, row["box"])
    x0, y0, x1, y1 = row["box"]
    return {
        **row,
        "width": round(float(x1 - x0), 6),
        "height": round(float(y1 - y0), 6),
        **phase,
        **boundary,
    }


def draw_sheet(image: Image.Image, rows: list[dict[str, Any]]) -> None:
    sheet = Image.new("RGB", (1840, 1220), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 14)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()
    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current-Scan JPEG Block Grid Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Page 76 active boxes, shifted controls, and C9 OVERDOSE slots checked against 8x8 JPEG block phase/energy.",
        fill=(235, 235, 235),
        font=small,
    )

    preview = image.resize((720, round(720 * image.height / image.width)))
    pdraw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height
    for x in range(0, preview.width, max(1, round(BLOCK * sx))):
        pdraw.line((x, 0, x, preview.height), fill=(255, 255, 255, 25), width=1)
    for y in range(0, preview.height, max(1, round(BLOCK * sy))):
        pdraw.line((0, y, preview.width, y), fill=(255, 255, 255, 25), width=1)
    for row in rows:
        if row["kind"] not in {"active", "overdose_slot"}:
            continue
        x0, y0, x1, y1 = row["box"]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        color = (255, 128, 0, 230) if row["kind"] == "active" else (30, 90, 255, 180)
        pdraw.rectangle(rect, outline=color, width=3)
        pdraw.text((rect[0], max(0, rect[1] - 16)), row["shortId"], fill=(255, 0, 0, 255))
    sheet.paste(preview, (24, 120))

    y = 120
    x0 = 780
    draw.text((x0, y), "Top block-boundary ratios", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["kind", "region", "ratio", "delta", "edgeHits", "phase"]
    xs = [x0, x0 + 110, x0 + 240, x0 + 320, x0 + 410, x0 + 500]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in sorted(rows, key=lambda item: item["boundaryToNonBoundaryRatio"], reverse=True)[:24]:
        vals = [
            row["kind"][:14],
            row["shortId"][:16],
            f"{row['boundaryToNonBoundaryRatio']:.3f}",
            f"{row['boundaryEnergyDelta']:.3f}",
            str(row["strictEdgeHitCount"]),
            f"L{row['edgePhase']['left']:.1f}/T{row['edgePhase']['top']:.1f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")
    image_arr = np.asarray(image)

    active_boxes = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "visualState": row["visualState"],
            "kind": "active",
            "box": row["box"],
        }
        for row in active_index.get("activeRows", [])
    ]
    controls = shifted_control_boxes(active_boxes, image.size)
    slots = c9_slot_boxes(c9)
    rows = [inspect_region(image_arr, row) for row in active_boxes + controls + slots]

    active_rows = [row for row in rows if row["kind"] == "active"]
    control_rows = [row for row in rows if row["kind"] == "shifted_control"]
    slot_rows = [row for row in rows if row["kind"] == "overdose_slot"]

    control_ratio_p95 = float(
        np.percentile([row["boundaryToNonBoundaryRatio"] for row in control_rows], 95)
    ) if control_rows else 0.0
    active_outliers = [
        row["shortId"]
        for row in active_rows
        if row["boundaryToNonBoundaryRatio"] > control_ratio_p95
    ]
    all_four_active_outlier = len(active_outliers) == len(active_rows)
    active_edge_hit_count = sum(row["strictEdgeHitCount"] for row in active_rows)
    control_edge_hit_count = sum(row["strictEdgeHitCount"] for row in control_rows)
    slot_edge_hit_count = sum(row["strictEdgeHitCount"] for row in slot_rows)
    max_active_ratio = max(row["boundaryToNonBoundaryRatio"] for row in active_rows)
    max_control_ratio = max(row["boundaryToNonBoundaryRatio"] for row in control_rows)
    max_slot_ratio = max(row["boundaryToNonBoundaryRatio"] for row in slot_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    fingerprint = (
        f"active={len(active_rows)}|controls={len(control_rows)}|slots={len(slot_rows)}"
        f"|edgeHits={active_edge_hit_count}/{control_edge_hit_count}/{slot_edge_hit_count}"
        f"|activeOutliers={len(active_outliers)}|allFourOutliers={int(all_four_active_outlier)}"
        f"|ratioMax={max_active_ratio:.3f}/{max_control_ratio:.3f}/{max_slot_ratio:.3f}"
        f"|controlP95={control_ratio_p95:.3f}|sourceR3={source_r3}"
        f"|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "activeBoxCount": len(active_rows),
        "shiftedControlBoxCount": len(control_rows),
        "overdoseSlotBoxCount": len(slot_rows),
        "blockSize": BLOCK,
        "edgeHitTolerancePx": EDGE_HIT_TOLERANCE,
        "activeStrictEdgeHitCount": active_edge_hit_count,
        "controlStrictEdgeHitCount": control_edge_hit_count,
        "overdoseSlotStrictEdgeHitCount": slot_edge_hit_count,
        "activeBoundaryRatioOutlierCount": len(active_outliers),
        "activeBoundaryRatioOutlierIds": active_outliers,
        "allFourActiveBoundaryRatioOutlier": all_four_active_outlier,
        "controlBoundaryRatioP95": round(control_ratio_p95, 6),
        "maxActiveBoundaryRatio": max_active_ratio,
        "maxControlBoundaryRatio": max_control_ratio,
        "maxOverdoseSlotBoundaryRatio": max_slot_ratio,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "jpegBlockGridFingerprint": fingerprint,
    }

    draw_sheet(image, rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current page-76 scan JPEG 8x8 block-grid phase and boundary-energy gate; no extraction or candidate generation",
        "inputs": {
            "page76Upright": rel(PAGE_76_UPRIGHT),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "regionRows": rows,
        "decision": {
            "currentScanJpegBlockGridGate": "current_scan_jpeg_block_grid_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Active target boxes and projected OVERDOSE slots do not show a unique "
                "JPEG 8x8 phase or block-boundary-energy carrier against shifted controls. "
                "Any edge/block coincidences are ordinary scan/compression artifacts and "
                "lack source-backed unit/order wording."
            ),
            "nextMove": (
                "Keep JPEG/block structure as a closed current-scan artifact path. Continue "
                "only with distinct physical/original-layout source validation or raw clue "
                "wording that names the extraction unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan JPEG Block Grid Gate",
        "",
        "Scope: inspected page-76 current-scan JPEG 8x8 block-grid phase and block-boundary energy in active target boxes, shifted controls, and projected C9/OVERDOSE slots. This is a visual/source artifact gate, not steganographic extraction. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active/control/OVERDOSE-slot boxes: `{len(active_rows)}` / `{len(control_rows)}` / `{len(slot_rows)}`",
        f"- Block size / edge tolerance: `{BLOCK}` / `{EDGE_HIT_TOLERANCE}` px",
        f"- Active/control/OVERDOSE strict edge hits: `{active_edge_hit_count}` / `{control_edge_hit_count}` / `{slot_edge_hit_count}`",
        f"- Active boundary-ratio outliers above shifted-control p95: `{len(active_outliers)}` (`{','.join(active_outliers)}`)",
        f"- All-four active boundary-ratio outlier: `{int(all_four_active_outlier)}`",
        f"- Max active/control/OVERDOSE boundary ratio: `{max_active_ratio:.3f}` / `{max_control_ratio:.3f}` / `{max_slot_ratio:.3f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Region Rows",
        "",
        "| kind | region | ratio | boundary delta | edge hits | center hits | phase L/T/R/B |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in sorted(rows, key=lambda item: item["boundaryToNonBoundaryRatio"], reverse=True):
        phase = row["edgePhase"]
        lines.append(
            f"| `{row['kind']}` | `{row['shortId']}` | {row['boundaryToNonBoundaryRatio']:.3f} | {row['boundaryEnergyDelta']:.3f} | {row['strictEdgeHitCount']} | {row['centerHitCount']} | `{phase['left']:.1f}/{phase['top']:.1f}/{phase['right']:.1f}/{phase['bottom']:.1f}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_jpeg_block_grid_no_selector`",
            "- Active boxes and projected OVERDOSE slots do not produce a unique 8x8 JPEG block phase or boundary-energy signature against shifted controls.",
            "- Edge/block coincidences are ordinary compression geometry and do not supply source-backed R3 unit/order/transform evidence.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentScanJpegBlockGridGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
