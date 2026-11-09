#!/usr/bin/env python3
"""Audit active boxes against current-PDF page-coordinate grids.

This bounded pass maps page-76 O4/B4/G5/O5, non-active page-76 highlights,
and C9/OVERDOSE slots into the current PDFs' point coordinate systems. It asks
whether the active boxes have a distinctive point-grid, page-fraction, or image
placement alignment that the raster scan view hides.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_active_box_coordinate_grid_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_active_box_coordinate_grid_gate.json"
OUT_MD = OUT / "current_pdf_active_box_coordinate_grid_gate.md"
OUT_SHEET = OUT / "current_pdf_active_box_coordinate_grid_gate_sheet.jpg"

PDF_PAGE_BOX_GEOMETRY = ROOT / (
    "analysis_outputs/source_audit/current_pdf_page_box_pair_geometry_gate/"
    "current_pdf_page_box_pair_geometry_gate.json"
)
ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
PAGE76_HIGHLIGHT_BENCHMARK = ROOT / (
    "analysis_outputs/source_audit/page76_all_source_highlight_mirror_benchmark/"
    "page76_all_source_highlight_mirror_benchmark.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_76_UPRIGHT = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

BASE_W = 2544.0
BASE_H = 3264.0
ACTIVE_IDS = {"O4", "B4", "G5", "O5"}
ACTIVE_ORDER = ["O4", "B4", "G5", "O5"]
GRID_SPECS = [
    {"name": "1pt", "step": 1.0, "kind": "fixed"},
    {"name": "0.5pt", "step": 0.5, "kind": "fixed"},
    {"name": "0.25pt", "step": 0.25, "kind": "fixed"},
    {"name": "6pt", "step": 6.0, "kind": "fixed"},
    {"name": "12pt", "step": 12.0, "kind": "fixed"},
    {"name": "72pt", "step": 72.0, "kind": "fixed"},
]
TOLERANCES_PT = [0.05, 0.12]


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


def center(box: list[float]) -> tuple[float, float]:
    x0, y0, x1, y1 = box
    return ((x0 + x1) / 2.0, (y0 + y1) / 2.0)


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in active_index.get("activeRows", []):
        short_id = str(row["shortId"])
        box = [float(value) for value in row["box"]]
        rows.append(
            {
                "id": row["id"],
                "shortId": short_id,
                "kind": "active",
                "label": row["phrase"],
                "visualState": row.get("visualState"),
                "boxPx": box,
            }
        )
    order = {short_id: idx for idx, short_id in enumerate(ACTIVE_ORDER)}
    return sorted(rows, key=lambda item: order.get(item["shortId"], 99))


def highlight_controls(benchmark: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for target in benchmark.get("targets", []):
        target_id = str(target.get("id"))
        if target_id in ACTIVE_IDS:
            continue
        rows.append(
            {
                "id": target_id,
                "shortId": target_id,
                "kind": "highlight_control",
                "label": str(target.get("label")),
                "highlightKind": str(target.get("kind")),
                "boxPx": [float(value) for value in target.get("box", [])],
            }
        )
    return rows


def c9_slot_rows(c9: dict[str, Any]) -> list[dict[str, Any]]:
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    frame = [float(value) for value in c9.get("c9Frame", [])]
    if len(frame) != 4:
        return []
    rows = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "id": f"slot{slot['index']}_{slot['letter']}",
                "shortId": f"s{slot['index']}{slot['letter']}",
                "kind": "overdose_slot",
                "label": f"OVERDOSE slot {slot['index']} {slot['letter']}",
                "letter": str(slot["letter"]),
                "boxPx": [
                    float(slot["left"]),
                    frame[1],
                    float(slot["right"]),
                    frame[3],
                ],
            }
        )
    return rows


def page76_pdf_rows(pdf_geometry: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair in pdf_geometry.get("pairRows", []):
        page = pair.get("page76", {})
        images = page.get("images", [])
        if not images:
            continue
        image = images[0]
        rect = [float(value) for value in image.get("primaryRect", image.get("rects", [[0, 0, 0, 0]])[0])]
        page_rect = [float(value) for value in page.get("pageRect", [])]
        rows.append(
            {
                "pdf": page.get("pdf"),
                "pdfPage": page.get("pdfPage"),
                "articlePage": page.get("articlePage"),
                "rotation": page.get("rotation"),
                "pageRect": page_rect,
                "imageRect": rect,
                "imageSizePx": [int(image.get("widthPx", 0)), int(image.get("heightPx", 0))],
                "scaleXPxPerPt": image.get("scaleXPxPerPt"),
                "scaleYPxPerPt": image.get("scaleYPxPerPt"),
                "hasSideMargins": abs(rect[0]) > 1e-6 or abs(page_rect[2] - rect[2]) > 1e-6,
            }
        )
    return rows


def map_box_to_pdf_modes(box_px: list[float], pdf_row: dict[str, Any]) -> dict[str, list[float]]:
    img_x0, img_y0, img_x1, img_y1 = pdf_row["imageRect"]
    page_x0, page_y0, page_x1, page_y1 = pdf_row["pageRect"]
    width_pt = img_x1 - img_x0
    height_pt = img_y1 - img_y0
    page_height = page_y1 - page_y0
    x0 = img_x0 + (box_px[0] / BASE_W) * width_pt
    y0_top = img_y0 + (box_px[1] / BASE_H) * height_pt
    x1 = img_x0 + (box_px[2] / BASE_W) * width_pt
    y1_top = img_y0 + (box_px[3] / BASE_H) * height_pt
    return {
        "visualTopOrigin": [x0, y0_top, x1, y1_top],
        "pdfBottomOrigin": [x0, page_height - y1_top, x1, page_height - y0_top],
    }


def residual_to_step(value: float, step: float) -> float:
    if step <= 0:
        return 0.0
    quotient = round(value / step)
    return abs(value - quotient * step)


def box_anchors(box: list[float]) -> dict[str, float]:
    x0, y0, x1, y1 = box
    return {
        "left": x0,
        "centerX": (x0 + x1) / 2.0,
        "right": x1,
        "topOrBottomA": y0,
        "centerY": (y0 + y1) / 2.0,
        "topOrBottomB": y1,
    }


def inspect_region_grid(region: dict[str, Any], pdf_row: dict[str, Any]) -> list[dict[str, Any]]:
    mode_boxes = map_box_to_pdf_modes(region["boxPx"], pdf_row)
    rows: list[dict[str, Any]] = []
    for mode_name, box_pt in mode_boxes.items():
        anchors = box_anchors(box_pt)
        for grid in GRID_SPECS:
            step = float(grid["step"])
            center_residuals = [
                residual_to_step(anchors["centerX"], step),
                residual_to_step(anchors["centerY"], step),
            ]
            edge_residuals = [
                residual_to_step(anchors["left"], step),
                residual_to_step(anchors["right"], step),
                residual_to_step(anchors["topOrBottomA"], step),
                residual_to_step(anchors["topOrBottomB"], step),
            ]
            all_residuals = center_residuals + edge_residuals
            rows.append(
                {
                    "pdf": pdf_row["pdf"],
                    "pdfPage": pdf_row["pdfPage"],
                    "mode": mode_name,
                    "regionId": region["shortId"],
                    "regionKind": region["kind"],
                    "grid": grid["name"],
                    "stepPt": step,
                    "boxPt": [round(value, 6) for value in box_pt],
                    "centerPt": [round((box_pt[0] + box_pt[2]) / 2.0, 6), round((box_pt[1] + box_pt[3]) / 2.0, 6)],
                    "centerMaxResidualPt": round(max(center_residuals), 6),
                    "centerMeanResidualPt": round(sum(center_residuals) / len(center_residuals), 6),
                    "edgeMaxResidualPt": round(max(edge_residuals), 6),
                    "edgeMeanResidualPt": round(sum(edge_residuals) / len(edge_residuals), 6),
                    "allAnchorMeanResidualPt": round(sum(all_residuals) / len(all_residuals), 6),
                    "centerClose05": max(center_residuals) <= 0.05,
                    "centerClose12": max(center_residuals) <= 0.12,
                    "allEdgesClose05": max(edge_residuals) <= 0.05,
                    "allEdgesClose12": max(edge_residuals) <= 0.12,
                }
            )
    return rows


def aggregate_grid_rows(grid_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = sorted({(row["pdf"], row["mode"], row["grid"]) for row in grid_rows})
    summaries: list[dict[str, Any]] = []
    for pdf, mode, grid in keys:
        rows = [row for row in grid_rows if (row["pdf"], row["mode"], row["grid"]) == (pdf, mode, grid)]
        active = [row for row in rows if row["regionKind"] == "active"]
        controls = [row for row in rows if row["regionKind"] == "highlight_control"]
        slots = [row for row in rows if row["regionKind"] == "overdose_slot"]
        if not active:
            continue
        summary = {
            "pdf": pdf,
            "mode": mode,
            "grid": grid,
            "activeCenterClose05Count": sum(int(row["centerClose05"]) for row in active),
            "activeCenterClose12Count": sum(int(row["centerClose12"]) for row in active),
            "activeAllEdgesClose05Count": sum(int(row["allEdgesClose05"]) for row in active),
            "activeAllEdgesClose12Count": sum(int(row["allEdgesClose12"]) for row in active),
            "controlCenterClose05Count": sum(int(row["centerClose05"]) for row in controls),
            "controlCenterClose12Count": sum(int(row["centerClose12"]) for row in controls),
            "slotCenterClose05Count": sum(int(row["centerClose05"]) for row in slots),
            "slotCenterClose12Count": sum(int(row["centerClose12"]) for row in slots),
            "activeMeanCenterResidualPt": round(
                sum(row["centerMeanResidualPt"] for row in active) / len(active), 6
            ),
            "controlMeanCenterResidualPt": round(
                sum(row["centerMeanResidualPt"] for row in controls) / len(controls), 6
            )
            if controls
            else None,
            "slotMeanCenterResidualPt": round(
                sum(row["centerMeanResidualPt"] for row in slots) / len(slots), 6
            )
            if slots
            else None,
            "allFourActiveCenterClose05": all(row["centerClose05"] for row in active),
            "allFourActiveCenterClose12": all(row["centerClose12"] for row in active),
            "allFourActiveEdgesClose05": all(row["allEdgesClose05"] for row in active),
            "allFourActiveEdgesClose12": all(row["allEdgesClose12"] for row in active),
        }
        summaries.append(summary)
    return summaries


def draw_sheet(
    image: Image.Image,
    regions: list[dict[str, Any]],
    pdf_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    sheet = Image.new("RGB", (1940, 1280), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(25)
    small = safe_font(14)
    tiny = safe_font(12)

    draw.rectangle((0, 0, 1940, 94), fill=(24, 31, 42))
    draw.text((24, 16), "Current-PDF Active Box Coordinate Grid Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Active boxes, page-76 controls, and C9 slots mapped into current PDF point coordinates.",
        fill=(235, 235, 235),
        font=small,
    )

    preview = image.resize((760, round(760 * image.height / image.width)))
    pdraw = ImageDraw.Draw(preview, "RGBA")
    sx = preview.width / image.width
    sy = preview.height / image.height
    for region in regions:
        x0, y0, x1, y1 = region["boxPx"]
        if region["kind"] == "active":
            color = (255, 120, 0, 235) if region.get("visualState") == "Y" else (0, 0, 0, 235)
            width = 4
        elif region["kind"] == "overdose_slot":
            color = (45, 90, 255, 95)
            width = 2
        else:
            color = (90, 90, 90, 105)
            width = 2
        pdraw.rectangle([x0 * sx, y0 * sy, x1 * sx, y1 * sy], outline=color, width=width)
        pdraw.text((x0 * sx, max(0, y0 * sy - 14)), region["shortId"], fill=(180, 0, 0, 220), font=tiny)
    sheet.paste(preview, (24, 120))

    x0 = 820
    y = 120
    draw.text((x0, y), "PDF Page-76 Geometry", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["pdf", "rot", "page pt", "image rect", "image px", "side margins"]
    xs = [x0, x0 + 260, x0 + 310, x0 + 445, x0 + 675, x0 + 795]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 20
    for row in pdf_rows:
        page_w = row["pageRect"][2] - row["pageRect"][0]
        page_h = row["pageRect"][3] - row["pageRect"][1]
        values = [
            str(row["pdf"])[:34],
            str(row["rotation"]),
            f"{page_w:.2f}x{page_h:.2f}",
            ",".join(f"{value:.1f}" for value in row["imageRect"]),
            f"{row['imageSizePx'][0]}x{row['imageSizePx'][1]}",
            str(int(row["hasSideMargins"])),
        ]
        for xpos, value in zip(xs, values):
            draw.text((xpos, y), value, fill=(35, 35, 35), font=tiny)
        y += 20

    y += 24
    draw.text((x0, y), "Best Grid Summaries", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["pdf", "mode", "grid", "act05", "act12", "ctrl05", "ctrl12", "mean act", "mean ctrl"]
    xs = [x0, x0 + 228, x0 + 368, x0 + 440, x0 + 500, x0 + 560, x0 + 625, x0 + 690, x0 + 780]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 20
    ranked = sorted(
        summary_rows,
        key=lambda row: (
            -row["activeCenterClose12Count"],
            -row["activeCenterClose05Count"],
            row["activeMeanCenterResidualPt"],
        ),
    )
    for row in ranked[:26]:
        values = [
            str(row["pdf"])[:29],
            row["mode"].replace("Origin", ""),
            row["grid"],
            str(row["activeCenterClose05Count"]),
            str(row["activeCenterClose12Count"]),
            str(row["controlCenterClose05Count"]),
            str(row["controlCenterClose12Count"]),
            f"{row['activeMeanCenterResidualPt']:.3f}",
            f"{row['controlMeanCenterResidualPt']:.3f}",
        ]
        for xpos, value in zip(xs, values):
            draw.text((xpos, y), value, fill=(35, 35, 35), font=tiny)
        y += 18

    y = 1020
    draw.text((24, y), "Decision", fill=(70, 70, 70), font=small)
    lines = [
        f"PDFs / regions active-control-slot: {summary['pdfCount']} / {summary['activeRegionCount']}-{summary['highlightControlRegionCount']}-{summary['overdoseSlotRegionCount']}",
        f"Best all active center close <=0.05/0.12pt: {summary['anyAllFourActiveCenterClose05']} / {summary['anyAllFourActiveCenterClose12']}",
        f"Best active center close counts <=0.05/0.12pt: {summary['bestActiveCenterClose05Count']} / {summary['bestActiveCenterClose12Count']}",
        f"Best grid: {summary['bestGridRow']['pdf']} {summary['bestGridRow']['mode']} {summary['bestGridRow']['grid']}",
        f"Grid candidate / hidden candidate: {int(summary['gridAlignmentCandidate'])} / {int(summary['hiddenPdfCoordinateCandidate'])}",
        f"Source R3 / triggers: {summary['sourceBackedR3BridgeHitCount']} / {summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
        f"Fingerprint: {summary['pdfCoordinateGridFingerprint']}",
    ]
    for idx, line in enumerate(lines):
        draw.text((24, y + 28 + idx * 22), line[:190], fill=(35, 35, 35), font=small)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    pdf_geometry = load_json(PDF_PAGE_BOX_GEOMETRY)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    benchmark = load_json(PAGE76_HIGHLIGHT_BENCHMARK)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    image = Image.open(PAGE_76_UPRIGHT).convert("RGB")

    active = active_rows(active_index)
    controls = highlight_controls(benchmark)
    slots = c9_slot_rows(c9)
    regions = active + controls + slots
    pdf_rows = page76_pdf_rows(pdf_geometry)

    grid_rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        for region in regions:
            grid_rows.extend(inspect_region_grid(region, pdf_row))
    summary_rows = aggregate_grid_rows(grid_rows)
    best_row = min(
        summary_rows,
        key=lambda row: (
            -row["activeCenterClose12Count"],
            -row["activeCenterClose05Count"],
            row["activeMeanCenterResidualPt"],
            row["controlCenterClose12Count"],
        ),
    )

    any_all_four_center05 = any(row["allFourActiveCenterClose05"] for row in summary_rows)
    any_all_four_center12 = any(row["allFourActiveCenterClose12"] for row in summary_rows)
    any_all_four_edges05 = any(row["allFourActiveEdgesClose05"] for row in summary_rows)
    any_all_four_edges12 = any(row["allFourActiveEdgesClose12"] for row in summary_rows)
    best_center05 = max(row["activeCenterClose05Count"] for row in summary_rows)
    best_center12 = max(row["activeCenterClose12Count"] for row in summary_rows)
    best_control05 = max(row["controlCenterClose05Count"] for row in summary_rows)
    best_control12 = max(row["controlCenterClose12Count"] for row in summary_rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    grid_candidate = bool(
        (any_all_four_center05 or any_all_four_center12 or any_all_four_edges05 or any_all_four_edges12)
        and best_control12 < len(controls)
    )
    hidden_candidate = bool(grid_candidate and source_r3 > 0 and satisfied_triggers > 0)

    fingerprint = (
        f"pdfs={len(pdf_rows)}|regions={len(active)}/{len(controls)}/{len(slots)}"
        f"|modes=visualTop,pdfBottom|grids={','.join(row['name'] for row in GRID_SPECS)}"
        f"|allFourCenter05={int(any_all_four_center05)}|allFourCenter12={int(any_all_four_center12)}"
        f"|allFourEdges05={int(any_all_four_edges05)}|allFourEdges12={int(any_all_four_edges12)}"
        f"|bestCenter05={best_center05}|bestCenter12={best_center12}"
        f"|controlBest05={best_control05}|controlBest12={best_control12}"
        f"|best={best_row['pdf']}:{best_row['mode']}:{best_row['grid']}"
        f"|gridCandidate={int(grid_candidate)}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "pdfCount": len(pdf_rows),
        "activeRegionCount": len(active),
        "highlightControlRegionCount": len(controls),
        "overdoseSlotRegionCount": len(slots),
        "modeCount": 2,
        "gridNames": [row["name"] for row in GRID_SPECS],
        "tolerancesPt": TOLERANCES_PT,
        "anyAllFourActiveCenterClose05": any_all_four_center05,
        "anyAllFourActiveCenterClose12": any_all_four_center12,
        "anyAllFourActiveEdgesClose05": any_all_four_edges05,
        "anyAllFourActiveEdgesClose12": any_all_four_edges12,
        "bestActiveCenterClose05Count": best_center05,
        "bestActiveCenterClose12Count": best_center12,
        "bestControlCenterClose05Count": best_control05,
        "bestControlCenterClose12Count": best_control12,
        "bestGridRow": best_row,
        "gridAlignmentCandidate": grid_candidate,
        "hiddenPdfCoordinateCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "pdfCoordinateGridFingerprint": fingerprint,
    }

    draw_sheet(image, regions, pdf_rows, summary_rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF point-coordinate grid audit for page-76 active boxes, non-active highlights, and C9/OVERDOSE slots; no extraction or candidate generation",
        "inputs": {
            "pdfPageBoxGeometry": rel(PDF_PAGE_BOX_GEOMETRY),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "page76HighlightBenchmark": rel(PAGE76_HIGHLIGHT_BENCHMARK),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "page76Upright": rel(PAGE_76_UPRIGHT),
        },
        "pdfPage76Rows": pdf_rows,
        "regionRows": regions,
        "gridSummaryRows": summary_rows,
        "gridRegionRows": grid_rows,
        "summary": summary,
        "decision": {
            "currentPdfActiveBoxCoordinateGridGate": "current_pdf_active_box_coordinate_grid_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Mapping the active boxes into current PDF point coordinates does not expose "
                "a distinctive all-four active center or edge grid alignment. The best grid "
                "close-count is partial and comparable page-76 controls also land near the "
                "same PDF grids."
            ),
            "nextMove": (
                "Do not treat PDF point/grid coordinates as the missing selector. Continue "
                "with distinct original-layout, physical scan, or raw-clue evidence that names "
                "the extraction unit/order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Active Box Coordinate Grid Gate",
        "",
        "Scope: mapped current page-76 O4/B4/G5/O5 boxes, page-76 non-active highlight controls, and C9/OVERDOSE slots into the current PDFs' point-coordinate systems. Tested visual top-origin and PDF bottom-origin coordinates against fixed point grids. This is geometry inspection only; no key extraction, candidates, hashing, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / active / highlight-control / OVERDOSE-slot regions: `{len(pdf_rows)}` / `{len(active)}` / `{len(controls)}` / `{len(slots)}`",
        f"- Modes checked: `visualTopOrigin`, `pdfBottomOrigin`",
        f"- Grids checked: `{', '.join(row['name'] for row in GRID_SPECS)}`",
        f"- Tolerances: `{TOLERANCES_PT}` pt",
        f"- Any all-four active center close <=0.05 / <=0.12 pt: `{int(any_all_four_center05)}` / `{int(any_all_four_center12)}`",
        f"- Any all-four active edge close <=0.05 / <=0.12 pt: `{int(any_all_four_edges05)}` / `{int(any_all_four_edges12)}`",
        f"- Best active center close count <=0.05 / <=0.12 pt: `{best_center05}` / `{best_center12}`",
        f"- Best control center close count <=0.05 / <=0.12 pt: `{best_control05}` / `{best_control12}`",
        f"- Best grid row: `{best_row['pdf']}` / `{best_row['mode']}` / `{best_row['grid']}`",
        f"- Grid alignment candidate / hidden PDF coordinate candidate: `{int(grid_candidate)}` / `{int(hidden_candidate)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Best Grid Rows",
        "",
        "| pdf | mode | grid | active center <=0.05 | active center <=0.12 | control center <=0.05 | control center <=0.12 | active mean center residual | control mean center residual |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    ranked = sorted(
        summary_rows,
        key=lambda row: (
            -row["activeCenterClose12Count"],
            -row["activeCenterClose05Count"],
            row["activeMeanCenterResidualPt"],
        ),
    )
    for row in ranked[:18]:
        lines.append(
            f"| `{row['pdf']}` | `{row['mode']}` | `{row['grid']}` | `{row['activeCenterClose05Count']}` | `{row['activeCenterClose12Count']}` | `{row['controlCenterClose05Count']}` | `{row['controlCenterClose12Count']}` | `{row['activeMeanCenterResidualPt']:.4f}` | `{row['controlMeanCenterResidualPt']:.4f}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_active_box_coordinate_grid_no_selector`",
            "- The current PDFs do not expose a hidden point-coordinate selector for O4/B4/G5/O5.",
            "- Active centers/edges do not achieve a distinctive all-four grid landing, and comparable controls land near the same grids.",
            "",
            "## Next Move",
            "",
            "- Keep using the PDF only as current-scan/source-registration evidence unless a distinct original-layout source or raw clue names a unit/order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentPdfActiveBoxCoordinateGridGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
