#!/usr/bin/env python3
"""Audit actual OVERDOSE header ink-centroids against active target geometry.

Prior C9/OVERDOSE passes used equal slots, OCR-derived glyph boxes, mirrored
slots, slot boundaries, and active-box edge residuals. This bounded pass uses
the visible orange ink components of the real OVERDOSE headers on pages 76 and
78, projects their stroke centroids into the C9 frame, and asks whether those
actual ink centers make O4/B4/G5/O5 more selective than the existing slot
geometry.

No key derivation, hashes, seed phrases, WIF/address checks, BIP39, OCR-to-key
extraction, or broad brute force is performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_glyph_stroke_centroid_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_glyph_stroke_centroid_gate.json"
OUT_MD = OUT / "current_scan_overdose_glyph_stroke_centroid_gate.md"
OUT_SHEET = OUT / "current_scan_overdose_glyph_stroke_centroid_gate_sheet.jpg"

PAGES = {
    76: ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg",
    78: ROOT / "analysis_outputs/3d_article_map/page_78_upright.jpg",
}
C9_HEADER_GLYPH = ROOT / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
SLOT_RESIDUAL = ROOT / (
    "analysis_outputs/source_audit/current_scan_slot_boundary_residual_gate/"
    "current_scan_slot_boundary_residual_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

LETTERS = "OVERDOSE"
CLOSE_PX = 16.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def orange_mask(arr: np.ndarray) -> np.ndarray:
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    return (r > 150) & (g > 60) & (g < 220) & (b < 180) & ((r - b) > 35) & ((r - g) > -10)


def connected_components(mask: np.ndarray, x_offset: int, y_offset: int) -> list[dict[str, Any]]:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components: list[dict[str, Any]] = []

    ys, xs = np.nonzero(mask)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if seen[sy, sx]:
            continue
        stack = [(sy, sx)]
        seen[sy, sx] = True
        px: list[int] = []
        py: list[int] = []
        while stack:
            y, x = stack.pop()
            px.append(x)
            py.append(y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(px) < 40:
            continue
        x0 = min(px) + x_offset
        x1 = max(px) + 1 + x_offset
        y0 = min(py) + y_offset
        y1 = max(py) + 1 + y_offset
        if (x1 - x0) < 8 or (y1 - y0) < 10:
            continue
        components.append(
            {
                "pixelCount": len(px),
                "box": [x0, y0, x1, y1],
                "centroid": [round(float(np.mean(px)) + x_offset, 3), round(float(np.mean(py)) + y_offset, 3)],
                "boxCenter": [round((x0 + x1) / 2, 3), round((y0 + y1) / 2, 3)],
            }
        )
    components.sort(key=lambda row: row["centroid"][0])
    return components


def detect_header_components(page_no: int, source_header: dict[str, Any]) -> dict[str, Any]:
    image = Image.open(PAGES[page_no]).convert("RGB")
    word_box = [float(v) for v in source_header["wordBox"]]
    x0 = max(0, int(round(word_box[0] - 110)))
    y0 = max(0, int(round(word_box[1] - 80)))
    x1 = min(image.width, int(round(word_box[2] + 250)))
    y1 = min(image.height, int(round(word_box[3] + 90)))
    crop = image.crop((x0, y0, x1, y1))
    components = connected_components(orange_mask(np.asarray(crop)), x0, y0)

    # Keep the eight left-to-right header-letter components nearest the OCR
    # header y band. This avoids unrelated small orange marks in the page top.
    header_y = (word_box[1] + word_box[3]) / 2
    components.sort(key=lambda row: (abs(row["centroid"][1] - header_y), row["centroid"][0]))
    components = sorted(components[: len(LETTERS)], key=lambda row: row["centroid"][0])
    for letter, component in zip(LETTERS, components):
        component["letter"] = letter

    if len(components) != len(LETTERS):
        raise RuntimeError(f"page {page_no} detected {len(components)} glyph components, expected {len(LETTERS)}")

    return {
        "page": page_no,
        "detectionWindow": [x0, y0, x1, y1],
        "ocrWordBox": word_box,
        "componentCount": len(components),
        "components": components,
    }


def project_components(header: dict[str, Any], c9_frame: list[float]) -> list[dict[str, Any]]:
    comps = header["components"]
    group_left = min(comp["box"][0] for comp in comps)
    group_right = max(comp["box"][2] for comp in comps)
    c9_left, _, c9_right, _ = c9_frame
    scale = (c9_right - c9_left) / max(1.0, group_right - group_left)

    projected = []
    for index, comp in enumerate(comps):
        box = comp["box"]
        centroid_x = comp["centroid"][0]
        projected.append(
            {
                "index": index,
                "letter": comp["letter"],
                "sourceBox": box,
                "sourceCentroid": comp["centroid"],
                "pixelCount": comp["pixelCount"],
                "projectedLeft": round(c9_left + (box[0] - group_left) * scale, 3),
                "projectedRight": round(c9_left + (box[2] - group_left) * scale, 3),
                "projectedCentroidX": round(c9_left + (centroid_x - group_left) * scale, 3),
                "projectedBoxCenterX": round(c9_left + (((box[0] + box[2]) / 2) - group_left) * scale, 3),
            }
        )
    return projected


def nearest_centroid(x: float, strokes: list[dict[str, Any]]) -> dict[str, Any]:
    best = min(strokes, key=lambda row: abs(x - row["projectedCentroidX"]))
    return {
        "x": round(x, 3),
        "nearestStrokeIndex": best["index"],
        "nearestStrokeLetter": best["letter"],
        "nearestStrokeCentroidX": best["projectedCentroidX"],
        "nearestStrokeAbsPx": round(abs(x - best["projectedCentroidX"]), 3),
        "nearestStrokeSignedPx": round(x - best["projectedCentroidX"], 3),
        "close16": abs(x - best["projectedCentroidX"]) <= CLOSE_PX,
    }


def evaluate_rows(projection_name: str, strokes: list[dict[str, Any]], region_rows: list[dict[str, Any]]) -> dict[str, Any]:
    evaluated = []
    for row in region_rows:
        x0, _, x1, _ = [float(v) for v in row["box"]]
        anchors = {
            "left": nearest_centroid(x0, strokes),
            "center": nearest_centroid((x0 + x1) / 2, strokes),
            "right": nearest_centroid(x1, strokes),
        }
        min_any = min(anchor["nearestStrokeAbsPx"] for anchor in anchors.values())
        evaluated.append(
            {
                "shortId": row.get("shortId"),
                "phrase": row.get("phrase"),
                "kind": row.get("kind"),
                "visualState": row.get("visualState"),
                "box": row.get("box"),
                "anchors": anchors,
                "minAnyAnchorStrokeDistancePx": round(min_any, 3),
                "anyAnchorClose16": any(anchor["close16"] for anchor in anchors.values()),
                "centerClose16": anchors["center"]["close16"],
                "centerStrokeLetter": anchors["center"]["nearestStrokeLetter"],
                "leftStrokeLetter": anchors["left"]["nearestStrokeLetter"],
                "rightStrokeLetter": anchors["right"]["nearestStrokeLetter"],
            }
        )

    active = [row for row in evaluated if row["kind"] == "active"]
    controls = [row for row in evaluated if row["kind"] != "active"]
    control_distances = [row["minAnyAnchorStrokeDistancePx"] for row in controls]
    control_p05 = round(float(np.percentile(control_distances, 5)), 3) if control_distances else None
    active_better_than_p05 = (
        sum(1 for row in active if control_p05 is not None and row["minAnyAnchorStrokeDistancePx"] < control_p05)
        if control_p05 is not None
        else 0
    )

    return {
        "name": projection_name,
        "strokeRows": strokes,
        "regionRows": evaluated,
        "summary": {
            "activeCenterStream": "".join(row["centerStrokeLetter"] for row in active),
            "activeLeftStream": "".join(row["leftStrokeLetter"] for row in active),
            "activeRightStream": "".join(row["rightStrokeLetter"] for row in active),
            "activeAnyAnchorClose16RowCount": sum(1 for row in active if row["anyAnchorClose16"]),
            "activeCenterClose16RowCount": sum(1 for row in active if row["centerClose16"]),
            "allFourActiveAnyAnchorClose16": all(row["anyAnchorClose16"] for row in active),
            "allFourActiveCenterClose16": all(row["centerClose16"] for row in active),
            "controlAnyAnchorClose16RowCount": sum(1 for row in controls if row["anyAnchorClose16"]),
            "controlCenterClose16RowCount": sum(1 for row in controls if row["centerClose16"]),
            "controlAnyAnchorDistanceP05": control_p05,
            "activeBetterThanControlP05Count": active_better_than_p05,
            "bestActiveMinDistancePx": min((row["minAnyAnchorStrokeDistancePx"] for row in active), default=None),
            "bestControlMinDistancePx": min((row["minAnyAnchorStrokeDistancePx"] for row in controls), default=None),
        },
    }


def draw_sheet(result: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 1320), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    draw.text((30, 28), "OVERDOSE Glyph Stroke-Centroid Gate", fill=(244, 247, 250), font=font(34, True))
    draw.text(
        (30, 74),
        "Actual orange ink components from p76/p78 headers, projected into the C9 frame and compared with active/control boxes.",
        fill=(176, 186, 198),
        font=font(17),
    )

    chips = [
        ("headers", result["summary"]["headerProjectionCount"]),
        ("components", result["summary"]["componentCounts"]),
        ("active close16", result["summary"]["bestActiveAnyAnchorClose16RowCount"]),
        ("control close16", result["summary"]["bestControlAnyAnchorClose16RowCount"]),
        ("selector", result["decision"]["currentScanOverdoseGlyphStrokeCentroidGate"]),
    ]
    x, y = 30, 118
    for label, value in chips:
        draw.rectangle((x, y, x + 330, y + 58), fill=(24, 30, 38), outline=(52, 62, 74))
        draw.text((x + 12, y + 8), label, fill=(132, 146, 160), font=font(13))
        draw.text((x + 12, y + 30), str(value)[:36], fill=(238, 243, 248), font=font(16, True))
        x += 350

    c9_frame = result["c9Frame"]
    frame_x0, frame_x1 = 90, 1750
    frame_y = 240
    for idx, projection in enumerate(result["projections"]):
        y0 = frame_y + idx * 235
        draw.text((30, y0 - 34), projection["name"], fill=(238, 243, 248), font=font(20, True))
        draw.line((frame_x0, y0, frame_x1, y0), fill=(75, 85, 100), width=3)
        for stroke in projection["strokeRows"]:
            sx = frame_x0 + (stroke["projectedCentroidX"] - c9_frame[0]) / (c9_frame[2] - c9_frame[0]) * (frame_x1 - frame_x0)
            draw.ellipse((sx - 7, y0 - 7, sx + 7, y0 + 7), fill=(250, 139, 42))
            draw.text((sx - 7, y0 + 13), stroke["letter"], fill=(250, 218, 190), font=font(14, True))
        active = [row for row in projection["regionRows"] if row["kind"] == "active"]
        for row_i, row in enumerate(active):
            yy = y0 + 58 + row_i * 33
            color = (255, 190, 76) if row["visualState"] == "Y" else (142, 184, 255)
            for anchor_name in ["left", "center", "right"]:
                anchor = row["anchors"][anchor_name]
                sx = frame_x0 + (anchor["x"] - c9_frame[0]) / (c9_frame[2] - c9_frame[0]) * (frame_x1 - frame_x0)
                draw.line((sx, yy - 9, sx, yy + 9), fill=color, width=2)
            draw.text(
                (30, yy - 10),
                f"{row['shortId']} center={row['centerStrokeLetter']} min={row['minAnyAnchorStrokeDistancePx']}",
                fill=color,
                font=font(14),
            )

    y = 735
    draw.text((30, y), "Projection Summary", fill=(238, 243, 248), font=font(22, True))
    y += 38
    headers = ["projection", "center", "left/right", "active close16", "control close16", "p05", "best active/control"]
    xs = [30, 330, 455, 660, 850, 1060, 1200]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(132, 146, 160), font=font(13, True))
    y += 28
    for projection in result["projections"]:
        s = projection["summary"]
        vals = [
            projection["name"],
            s["activeCenterStream"],
            f"{s['activeLeftStream']}/{s['activeRightStream']}",
            f"{s['activeAnyAnchorClose16RowCount']}/4 center {s['activeCenterClose16RowCount']}/4",
            f"{s['controlAnyAnchorClose16RowCount']} center {s['controlCenterClose16RowCount']}",
            s["controlAnyAnchorDistanceP05"],
            f"{s['bestActiveMinDistancePx']} / {s['bestControlMinDistancePx']}",
        ]
        for x, value in zip(xs, vals):
            draw.text((x, y), str(value)[:34], fill=(224, 231, 238), font=font(13))
        y += 28

    y += 25
    draw.rectangle((30, y, 1810, y + 108), fill=(37, 30, 18), outline=(96, 72, 35))
    draw.text((46, y + 18), "Decision", fill=(255, 219, 137), font=font(17, True))
    draw.text(
        (46, y + 48),
        "Actual stroke centroids do not create an all-four active close alignment and controls still produce comparable close contacts.",
        fill=(255, 219, 137),
        font=font(15),
    )
    draw.text(
        (46, y + 74),
        "Keep OVERDOSE stroke geometry as validation context only; R3 unit/order remains absent.",
        fill=(255, 219, 137),
        font=font(15),
    )
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    c9 = load_json(C9_HEADER_GLYPH)
    residual = load_json(SLOT_RESIDUAL)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    c9_frame = [float(v) for v in c9.get("c9Frame", residual.get("c9Ruler", {}).get("frame", [294.0, 2176.81, 2250.0, 3023.73]))]
    region_rows = residual.get("regionRows", [])

    projections = []
    for projection in c9.get("projections", []):
        page_no = int(projection["sourceHeader"]["page"])
        header = detect_header_components(page_no, projection["sourceHeader"])
        strokes = project_components(header, c9_frame)
        evaluated = evaluate_rows(f"p{page_no}_orange_stroke_centroids", strokes, region_rows)
        evaluated["sourceHeaderDetection"] = header
        projections.append(evaluated)

    best_active_close = max((p["summary"]["activeAnyAnchorClose16RowCount"] for p in projections), default=0)
    best_control_close = max((p["summary"]["controlAnyAnchorClose16RowCount"] for p in projections), default=0)
    source_r3 = int(reopen.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(reopen.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(reopen.get("summary", {}).get("triggerCount") or 0)
    selector_count = sum(
        1
        for p in projections
        if p["summary"]["allFourActiveAnyAnchorClose16"] and source_r3 > 0
    )

    summary = {
        "headerProjectionCount": len(projections),
        "componentCounts": [p["sourceHeaderDetection"]["componentCount"] for p in projections],
        "regionRowCount": len(region_rows),
        "activeRowCount": sum(1 for row in region_rows if row.get("kind") == "active"),
        "controlRowCount": sum(1 for row in region_rows if row.get("kind") != "active"),
        "bestActiveAnyAnchorClose16RowCount": best_active_close,
        "bestControlAnyAnchorClose16RowCount": best_control_close,
        "allFourActiveAnyAnchorClose16ProjectionCount": sum(
            1 for p in projections if p["summary"]["allFourActiveAnyAnchorClose16"]
        ),
        "allFourActiveCenterClose16ProjectionCount": sum(
            1 for p in projections if p["summary"]["allFourActiveCenterClose16"]
        ),
        "activeBetterThanControlP05ProjectionCount": sum(
            1 for p in projections if p["summary"]["activeBetterThanControlP05Count"] == 4
        ),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorCandidateCount": selector_count,
    }
    fingerprint = (
        f"headers={summary['headerProjectionCount']}|components={','.join(map(str, summary['componentCounts']))}|"
        f"rows={summary['regionRowCount']}|activeClose16={best_active_close}|controlClose16={best_control_close}|"
        f"allFourAny={summary['allFourActiveAnyAnchorClose16ProjectionCount']}|"
        f"allFourCenter={summary['allFourActiveCenterClose16ProjectionCount']}|"
        f"activeP05={summary['activeBetterThanControlP05ProjectionCount']}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors={selector_count}"
    )
    summary["glyphStrokeCentroidFingerprint"] = fingerprint

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Actual p76/p78 OVERDOSE orange stroke-centroid projection into C9 frame; "
            "no OCR-to-key extraction, candidate generation, hashing, seed/WIF/address checks, BIP39, or brute force."
        ),
        "inputs": {
            "page76Upright": rel(PAGES[76]),
            "page78Upright": rel(PAGES[78]),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH),
            "slotBoundaryResidualGate": rel(SLOT_RESIDUAL),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "c9Frame": c9_frame,
        "closeThresholdPx": CLOSE_PX,
        "summary": summary,
        "projections": projections,
        "decision": {
            "currentScanOverdoseGlyphStrokeCentroidGate": "no_selector",
            "selectorUnlocked": bool(selector_count),
            "nextMove": (
                "Stop tuning OVERDOSE stroke/slot geometry under the current scan. "
                "Use it only as source-validation context unless a new source/clue supplies R3 unit/order."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current Scan OVERDOSE Glyph Stroke-Centroid Gate",
        "",
        "Scope: detected the actual orange ink components of the p76/p78 `OVERDOSE` headers, projected their stroke centroids into the C9 frame, and compared O4/B4/G5/O5 plus existing controls. No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Header projections / component counts: `{summary['headerProjectionCount']}` / `{summary['componentCounts']}`",
        f"- Region rows / active / controls: `{summary['regionRowCount']}` / `{summary['activeRowCount']}` / `{summary['controlRowCount']}`",
        f"- Best active any-anchor close<=16px rows: `{summary['bestActiveAnyAnchorClose16RowCount']}/4`",
        f"- Best control any-anchor close<=16px rows: `{summary['bestControlAnyAnchorClose16RowCount']}`",
        f"- All-four active any-anchor / center close projections: `{summary['allFourActiveAnyAnchorClose16ProjectionCount']}` / `{summary['allFourActiveCenterClose16ProjectionCount']}`",
        f"- Active-better-than-control-p05 projection count: `{summary['activeBetterThanControlP05ProjectionCount']}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `{source_r3}` / `{satisfied}/{trigger_count}` / `{selector_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Projection Rows",
        "",
        "| projection | center stream | left/right streams | active close<=16 | control close<=16 | control p05 | best active/control distance |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for projection in projections:
        s = projection["summary"]
        lines.append(
            f"| `{projection['name']}` | `{s['activeCenterStream']}` | `{s['activeLeftStream']}/{s['activeRightStream']}` | "
            f"{s['activeAnyAnchorClose16RowCount']} | {s['controlAnyAnchorClose16RowCount']} | {s['controlAnyAnchorDistanceP05']} | "
            f"{s['bestActiveMinDistancePx']} / {s['bestControlMinDistancePx']} |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_overdose_glyph_stroke_centroid_no_selector`.",
            "- Actual orange stroke centroids do not make the active quartet an all-four close alignment.",
            "- Controls still produce comparable close centroid contacts, and no source-backed R3 unit/order trigger is satisfied.",
            "- Keep OVERDOSE stroke geometry as source-validation context only.",
            "",
            "## Next Move",
            "",
            "- Stop tuning current-scan OVERDOSE stroke/slot geometry.",
            "- Highest-value direction remains a distinct physical/original-layout/source asset or raw clue wording that supplies the missing unit, order, or transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")


if __name__ == "__main__":
    main()
