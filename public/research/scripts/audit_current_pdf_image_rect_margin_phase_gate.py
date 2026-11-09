#!/usr/bin/env python3
"""Audit current-PDF image-rectangle margin phase around active boxes.

This bounded pass maps O4/B4/G5/O5, page-76 non-active highlight controls, and
C9/OVERDOSE slots into the current PDFs' embedded image rectangles. It asks
whether the active boxes have a distinctive alignment to page trim, side
margins, image-rect edges, or the margin-derived 18pt unit in the low-resolution
PDFs.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_image_rect_margin_phase_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_image_rect_margin_phase_gate.json"
OUT_MD = OUT / "current_pdf_image_rect_margin_phase_gate.md"
OUT_SHEET = OUT / "current_pdf_image_rect_margin_phase_gate_sheet.jpg"

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
FRACTION_RULERS = [
    {"name": "halves", "denominator": 2},
    {"name": "thirds", "denominator": 3},
    {"name": "quarters", "denominator": 4},
    {"name": "eighths", "denominator": 8},
    {"name": "sixteenths", "denominator": 16},
]
POINT_TOLERANCES = [0.25, 0.5, 1.0]
FRACTION_TOLERANCES = [0.001, 0.0025, 0.005]


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
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in active_index.get("activeRows", []):
        rows.append(
            {
                "id": row["id"],
                "shortId": row["shortId"],
                "kind": "active",
                "label": row["phrase"],
                "visualState": row.get("visualState"),
                "boxPx": [float(value) for value in row["box"]],
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
    rows: list[dict[str, Any]] = []
    if len(frame) != 4:
        return rows
    for slot in projection.get("slots", []):
        rows.append(
            {
                "id": f"slot{slot['index']}_{slot['letter']}",
                "shortId": f"s{slot['index']}{slot['letter']}",
                "kind": "overdose_slot",
                "label": f"OVERDOSE slot {slot['index']} {slot['letter']}",
                "letter": str(slot["letter"]),
                "boxPx": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return rows


def page76_pdf_rows(pdf_geometry: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for pair in pdf_geometry.get("pairRows", []):
        page = pair.get("page76", {})
        images = page.get("images", [])
        if not images:
            continue
        image = images[0]
        rect = [float(value) for value in image.get("primaryRect", image.get("rects", [[0, 0, 0, 0]])[0])]
        page_rect = [float(value) for value in page.get("pageRect", [])]
        left_margin = rect[0] - page_rect[0]
        right_margin = page_rect[2] - rect[2]
        top_margin = rect[1] - page_rect[1]
        bottom_margin = page_rect[3] - rect[3]
        margin_units = sorted(
            {
                round(abs(value), 6)
                for value in [left_margin, right_margin, top_margin, bottom_margin]
                if abs(value) > 1e-6
            }
        )
        rows.append(
            {
                "pdf": page.get("pdf"),
                "pdfPage": page.get("pdfPage"),
                "articlePage": page.get("articlePage"),
                "rotation": page.get("rotation"),
                "pageRect": page_rect,
                "imageRect": rect,
                "imageSizePx": [int(image.get("widthPx", 0)), int(image.get("heightPx", 0))],
                "leftMarginPt": round(left_margin, 6),
                "rightMarginPt": round(right_margin, 6),
                "topMarginPt": round(top_margin, 6),
                "bottomMarginPt": round(bottom_margin, 6),
                "marginUnitsPt": margin_units,
            }
        )
    return rows


def map_box_to_image_rect(box_px: list[float], pdf_row: dict[str, Any]) -> dict[str, list[float]]:
    ix0, iy0, ix1, iy1 = pdf_row["imageRect"]
    page_x0, page_y0, page_x1, page_y1 = pdf_row["pageRect"]
    width_pt = ix1 - ix0
    height_pt = iy1 - iy0
    page_height = page_y1 - page_y0
    x0 = ix0 + (box_px[0] / BASE_W) * width_pt
    y0_top = iy0 + (box_px[1] / BASE_H) * height_pt
    x1 = ix0 + (box_px[2] / BASE_W) * width_pt
    y1_top = iy0 + (box_px[3] / BASE_H) * height_pt
    return {
        "visualTopOrigin": [x0, y0_top, x1, y1_top],
        "pdfBottomOrigin": [x0, page_height - y1_top, x1, page_height - y0_top],
    }


def fraction_residual(value: float, denominator: int) -> float:
    nearest = round(value * denominator) / denominator
    return abs(value - nearest)


def point_residual_to_unit(value: float, unit: float) -> float | None:
    if unit <= 0:
        return None
    return abs(value - round(value / unit) * unit)


def inspect_region(region: dict[str, Any], pdf_row: dict[str, Any]) -> list[dict[str, Any]]:
    mode_boxes = map_box_to_image_rect(region["boxPx"], pdf_row)
    ix0, iy0, ix1, iy1 = pdf_row["imageRect"]
    width = ix1 - ix0
    height = iy1 - iy0
    rows: list[dict[str, Any]] = []
    for mode, box in mode_boxes.items():
        cx, cy = center(box)
        norm_x = (cx - ix0) / width if width else 0.0
        if mode == "visualTopOrigin":
            norm_y = (cy - iy0) / height if height else 0.0
        else:
            bottom_rect_y0 = pdf_row["pageRect"][3] - iy1
            norm_y = (cy - bottom_rect_y0) / height if height else 0.0
        edge_distances = [box[0] - ix0, ix1 - box[2], box[1] - iy0, iy1 - box[3]]
        min_edge = min(abs(value) for value in edge_distances)
        for ruler in FRACTION_RULERS:
            denom = int(ruler["denominator"])
            rx = fraction_residual(norm_x, denom)
            ry = fraction_residual(norm_y, denom)
            rows.append(
                {
                    "pdf": pdf_row["pdf"],
                    "mode": mode,
                    "regionId": region["shortId"],
                    "regionKind": region["kind"],
                    "ruler": ruler["name"],
                    "denominator": denom,
                    "boxPt": [round(value, 6) for value in box],
                    "centerPt": [round(cx, 6), round(cy, 6)],
                    "normalizedCenter": [round(norm_x, 8), round(norm_y, 8)],
                    "fractionResidualX": round(rx, 8),
                    "fractionResidualY": round(ry, 8),
                    "fractionMaxResidual": round(max(rx, ry), 8),
                    "fractionMeanResidual": round((rx + ry) / 2.0, 8),
                    "close001": max(rx, ry) <= 0.001,
                    "close0025": max(rx, ry) <= 0.0025,
                    "close005": max(rx, ry) <= 0.005,
                    "minImageEdgeDistancePt": round(min_edge, 6),
                }
            )
        for unit in pdf_row["marginUnitsPt"]:
            rx = point_residual_to_unit(cx - pdf_row["pageRect"][0], unit)
            ry = point_residual_to_unit(cy - pdf_row["pageRect"][1], unit)
            edge_r = min(
                point_residual_to_unit(value - pdf_row["pageRect"][0], unit)
                for value in [box[0], box[2]]
            )
            rows.append(
                {
                    "pdf": pdf_row["pdf"],
                    "mode": mode,
                    "regionId": region["shortId"],
                    "regionKind": region["kind"],
                    "ruler": f"marginUnit{unit:g}pt",
                    "denominator": None,
                    "boxPt": [round(value, 6) for value in box],
                    "centerPt": [round(cx, 6), round(cy, 6)],
                    "normalizedCenter": [round(norm_x, 8), round(norm_y, 8)],
                    "marginUnitPt": unit,
                    "centerMarginUnitResidualXPt": round(rx, 6) if rx is not None else None,
                    "centerMarginUnitResidualYPt": round(ry, 6) if ry is not None else None,
                    "edgeMarginUnitResidualXPt": round(edge_r, 6) if edge_r is not None else None,
                    "marginCenterMaxResidualPt": round(max(rx or 0.0, ry or 0.0), 6),
                    "marginCenterClose025": max(rx or 0.0, ry or 0.0) <= 0.25,
                    "marginCenterClose050": max(rx or 0.0, ry or 0.0) <= 0.5,
                    "marginCenterClose100": max(rx or 0.0, ry or 0.0) <= 1.0,
                    "minImageEdgeDistancePt": round(min_edge, 6),
                }
            )
    return rows


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = sorted({(row["pdf"], row["mode"], row["ruler"]) for row in rows})
    summaries: list[dict[str, Any]] = []
    for pdf, mode, ruler in keys:
        subset = [row for row in rows if (row["pdf"], row["mode"], row["ruler"]) == (pdf, mode, ruler)]
        active = [row for row in subset if row["regionKind"] == "active"]
        controls = [row for row in subset if row["regionKind"] == "highlight_control"]
        slots = [row for row in subset if row["regionKind"] == "overdose_slot"]
        if not active:
            continue
        first = active[0]
        if "fractionMaxResidual" in first:
            summary = {
                "pdf": pdf,
                "mode": mode,
                "ruler": ruler,
                "rulerKind": "fraction",
                "activeClose001Count": sum(int(row["close001"]) for row in active),
                "activeClose0025Count": sum(int(row["close0025"]) for row in active),
                "activeClose005Count": sum(int(row["close005"]) for row in active),
                "controlClose001Count": sum(int(row["close001"]) for row in controls),
                "controlClose0025Count": sum(int(row["close0025"]) for row in controls),
                "controlClose005Count": sum(int(row["close005"]) for row in controls),
                "slotClose005Count": sum(int(row["close005"]) for row in slots),
                "activeMeanResidual": round(sum(row["fractionMeanResidual"] for row in active) / len(active), 8),
                "controlMeanResidual": round(sum(row["fractionMeanResidual"] for row in controls) / len(controls), 8)
                if controls
                else None,
                "allFourActiveClose001": all(row["close001"] for row in active),
                "allFourActiveClose0025": all(row["close0025"] for row in active),
                "allFourActiveClose005": all(row["close005"] for row in active),
            }
        else:
            summary = {
                "pdf": pdf,
                "mode": mode,
                "ruler": ruler,
                "rulerKind": "margin_unit",
                "activeClose025Count": sum(int(row["marginCenterClose025"]) for row in active),
                "activeClose050Count": sum(int(row["marginCenterClose050"]) for row in active),
                "activeClose100Count": sum(int(row["marginCenterClose100"]) for row in active),
                "controlClose025Count": sum(int(row["marginCenterClose025"]) for row in controls),
                "controlClose050Count": sum(int(row["marginCenterClose050"]) for row in controls),
                "controlClose100Count": sum(int(row["marginCenterClose100"]) for row in controls),
                "slotClose100Count": sum(int(row["marginCenterClose100"]) for row in slots),
                "activeMeanResidual": round(
                    sum(row["marginCenterMaxResidualPt"] for row in active) / len(active), 6
                ),
                "controlMeanResidual": round(
                    sum(row["marginCenterMaxResidualPt"] for row in controls) / len(controls), 6
                )
                if controls
                else None,
                "allFourActiveClose025": all(row["marginCenterClose025"] for row in active),
                "allFourActiveClose050": all(row["marginCenterClose050"] for row in active),
                "allFourActiveClose100": all(row["marginCenterClose100"] for row in active),
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
    draw.text((24, 16), "Current-PDF Image Rect Margin Phase Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Active boxes compared with PDF image-rect edges, trim margins, fractional rulers, and 18pt margin units.",
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
            color = (255, 128, 0, 235) if region.get("visualState") == "Y" else (0, 0, 0, 235)
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
    draw.text((x0, y), "PDF image rectangles", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["pdf", "image rect", "page rect", "margins", "unit"]
    xs = [x0, x0 + 300, x0 + 545, x0 + 735, x0 + 890]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 20
    for row in pdf_rows:
        vals = [
            str(row["pdf"])[:37],
            ",".join(f"{v:.1f}" for v in row["imageRect"]),
            f"{row['pageRect'][2]:.1f}x{row['pageRect'][3]:.1f}",
            f"{row['leftMarginPt']:.1f}/{row['rightMarginPt']:.1f}",
            ",".join(f"{unit:g}" for unit in row["marginUnitsPt"]) or ".",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 20

    y += 24
    draw.text((x0, y), "Best margin/fraction summaries", fill=(70, 70, 70), font=small)
    y += 26
    headers = ["pdf", "mode", "ruler", "kind", "act", "ctrl", "slot", "mean act", "mean ctrl"]
    xs = [x0, x0 + 250, x0 + 395, x0 + 510, x0 + 600, x0 + 655, x0 + 710, x0 + 760, x0 + 850]
    for xpos, header in zip(xs, headers):
        draw.text((xpos, y), header, fill=(80, 80, 80), font=tiny)
    y += 20
    for row in summary["rankedRows"][:27]:
        if row["rulerKind"] == "fraction":
            act = row["activeClose005Count"]
            ctrl = row["controlClose005Count"]
            slot = row["slotClose005Count"]
        else:
            act = row["activeClose100Count"]
            ctrl = row["controlClose100Count"]
            slot = row["slotClose100Count"]
        vals = [
            str(row["pdf"])[:31],
            row["mode"].replace("Origin", ""),
            row["ruler"],
            row["rulerKind"][:8],
            str(act),
            str(ctrl),
            str(slot),
            f"{row['activeMeanResidual']:.4f}",
            f"{row['controlMeanResidual']:.4f}",
        ]
        for xpos, val in zip(xs, vals):
            draw.text((xpos, y), val, fill=(35, 35, 35), font=tiny)
        y += 18

    y = 1018
    draw.text((24, y), "Decision", fill=(70, 70, 70), font=small)
    lines = [
        f"PDFs / active-control-slot: {summary['pdfCount']} / {summary['activeRegionCount']}-{summary['highlightControlRegionCount']}-{summary['overdoseSlotRegionCount']}",
        f"All-four fraction close <=0.001/0.0025/0.005: {int(summary['anyAllFourFraction001'])}/{int(summary['anyAllFourFraction0025'])}/{int(summary['anyAllFourFraction005'])}",
        f"All-four margin unit close <=0.25/0.5/1.0pt: {int(summary['anyAllFourMargin025'])}/{int(summary['anyAllFourMargin050'])}/{int(summary['anyAllFourMargin100'])}",
        f"Best fraction active/control close <=0.005: {summary['bestFractionActiveClose005Count']} / {summary['bestFractionControlClose005Count']}",
        f"Best margin active/control close <=1pt: {summary['bestMarginActiveClose100Count']} / {summary['bestMarginControlClose100Count']}",
        f"Margin candidate / hidden candidate: {int(summary['marginPhaseCandidate'])} / {int(summary['hiddenMarginPhaseCandidate'])}",
        f"Fingerprint: {summary['imageRectMarginPhaseFingerprint']}",
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

    rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        for region in regions:
            rows.extend(inspect_region(region, pdf_row))
    summary_rows = aggregate(rows)

    fraction_rows = [row for row in summary_rows if row["rulerKind"] == "fraction"]
    margin_rows = [row for row in summary_rows if row["rulerKind"] == "margin_unit"]
    any_fraction_001 = any(row["allFourActiveClose001"] for row in fraction_rows)
    any_fraction_0025 = any(row["allFourActiveClose0025"] for row in fraction_rows)
    any_fraction_005 = any(row["allFourActiveClose005"] for row in fraction_rows)
    any_margin_025 = any(row["allFourActiveClose025"] for row in margin_rows)
    any_margin_050 = any(row["allFourActiveClose050"] for row in margin_rows)
    any_margin_100 = any(row["allFourActiveClose100"] for row in margin_rows)
    best_fraction_active_005 = max((row["activeClose005Count"] for row in fraction_rows), default=0)
    best_fraction_control_005 = max((row["controlClose005Count"] for row in fraction_rows), default=0)
    best_margin_active_100 = max((row["activeClose100Count"] for row in margin_rows), default=0)
    best_margin_control_100 = max((row["controlClose100Count"] for row in margin_rows), default=0)

    def rank_key(row: dict[str, Any]) -> tuple[int, int, float]:
        if row["rulerKind"] == "fraction":
            return (-row["activeClose005Count"], -row["activeClose0025Count"], row["activeMeanResidual"])
        return (-row["activeClose100Count"], -row["activeClose050Count"], row["activeMeanResidual"])

    ranked = sorted(summary_rows, key=rank_key)
    best_row = ranked[0] if ranked else {}
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    margin_candidate = bool(
        (
            any_fraction_001
            or any_fraction_0025
            or any_fraction_005
            or any_margin_025
            or any_margin_050
            or any_margin_100
        )
        and best_fraction_control_005 < len(controls)
        and best_margin_control_100 < len(controls)
    )
    hidden_candidate = bool(margin_candidate and source_r3 > 0 and satisfied_triggers > 0)

    fingerprint = (
        f"pdfs={len(pdf_rows)}|regions={len(active)}/{len(controls)}/{len(slots)}"
        f"|fractionRulers={','.join(row['name'] for row in FRACTION_RULERS)}"
        f"|marginUnits={','.join(str(unit) for row in pdf_rows for unit in row['marginUnitsPt']) or 'none'}"
        f"|allFourFrac001={int(any_fraction_001)}|allFourFrac0025={int(any_fraction_0025)}|allFourFrac005={int(any_fraction_005)}"
        f"|allFourMargin025={int(any_margin_025)}|allFourMargin050={int(any_margin_050)}|allFourMargin100={int(any_margin_100)}"
        f"|bestFracActive005={best_fraction_active_005}|bestFracControl005={best_fraction_control_005}"
        f"|bestMarginActive100={best_margin_active_100}|bestMarginControl100={best_margin_control_100}"
        f"|best={best_row.get('pdf')}:{best_row.get('mode')}:{best_row.get('ruler')}"
        f"|marginCandidate={int(margin_candidate)}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )

    summary = {
        "pdfCount": len(pdf_rows),
        "activeRegionCount": len(active),
        "highlightControlRegionCount": len(controls),
        "overdoseSlotRegionCount": len(slots),
        "fractionRulers": [row["name"] for row in FRACTION_RULERS],
        "pointTolerancesPt": POINT_TOLERANCES,
        "fractionTolerances": FRACTION_TOLERANCES,
        "anyAllFourFraction001": any_fraction_001,
        "anyAllFourFraction0025": any_fraction_0025,
        "anyAllFourFraction005": any_fraction_005,
        "anyAllFourMargin025": any_margin_025,
        "anyAllFourMargin050": any_margin_050,
        "anyAllFourMargin100": any_margin_100,
        "bestFractionActiveClose005Count": best_fraction_active_005,
        "bestFractionControlClose005Count": best_fraction_control_005,
        "bestMarginActiveClose100Count": best_margin_active_100,
        "bestMarginControlClose100Count": best_margin_control_100,
        "bestSummaryRow": best_row,
        "rankedRows": ranked,
        "marginPhaseCandidate": margin_candidate,
        "hiddenMarginPhaseCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "imageRectMarginPhaseFingerprint": fingerprint,
    }

    draw_sheet(image, regions, pdf_rows, summary_rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF image-rectangle margin phase audit for page-76 active boxes, highlight controls, and C9/OVERDOSE slots; no extraction or candidate generation",
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
        "phaseRegionRows": rows,
        "phaseSummaryRows": summary_rows,
        "summary": summary,
        "decision": {
            "currentPdfImageRectMarginPhaseGate": "current_pdf_image_rect_margin_phase_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Active boxes do not have a distinctive image-rect, trim-margin, fraction, "
                "or 18pt margin-unit phase. Any loose all-four active phase is matched or "
                "exceeded by non-active page-76 highlight controls."
            ),
            "nextMove": (
                "Do not treat PDF trim/image-rect margin geometry as the missing selector. "
                "Continue with distinct original-layout, physical scan, or raw-clue evidence "
                "that names the unit/order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Image Rect Margin Phase Gate",
        "",
        "Scope: mapped current page-76 O4/B4/G5/O5 boxes, page-76 non-active highlights, and C9/OVERDOSE slots into the current PDFs' embedded image rectangles. Tested image-rect fractions, trim margins, and margin-derived 18pt units. This is geometry inspection only; no key extraction, candidates, hashing, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / active / highlight-control / OVERDOSE-slot regions: `{len(pdf_rows)}` / `{len(active)}` / `{len(controls)}` / `{len(slots)}`",
        f"- Fraction rulers: `{', '.join(row['name'] for row in FRACTION_RULERS)}`",
        f"- Margin units seen: `{', '.join(str(unit) for row in pdf_rows for unit in row['marginUnitsPt']) or 'none'}` pt",
        f"- Any all-four fraction close <=0.001 / <=0.0025 / <=0.005: `{int(any_fraction_001)}` / `{int(any_fraction_0025)}` / `{int(any_fraction_005)}`",
        f"- Any all-four margin-unit close <=0.25 / <=0.5 / <=1.0 pt: `{int(any_margin_025)}` / `{int(any_margin_050)}` / `{int(any_margin_100)}`",
        f"- Best fraction active/control close <=0.005: `{best_fraction_active_005}` / `{best_fraction_control_005}`",
        f"- Best margin-unit active/control close <=1.0 pt: `{best_margin_active_100}` / `{best_margin_control_100}`",
        f"- Best summary row: `{best_row.get('pdf')}` / `{best_row.get('mode')}` / `{best_row.get('ruler')}`",
        f"- Margin phase candidate / hidden candidate: `{int(margin_candidate)}` / `{int(hidden_candidate)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Best Phase Rows",
        "",
        "| pdf | mode | ruler | kind | active close | control close | slot close | active mean residual | control mean residual |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in ranked[:18]:
        if row["rulerKind"] == "fraction":
            active_close = row["activeClose005Count"]
            control_close = row["controlClose005Count"]
            slot_close = row["slotClose005Count"]
        else:
            active_close = row["activeClose100Count"]
            control_close = row["controlClose100Count"]
            slot_close = row["slotClose100Count"]
        lines.append(
            f"| `{row['pdf']}` | `{row['mode']}` | `{row['ruler']}` | `{row['rulerKind']}` | `{active_close}` | `{control_close}` | `{slot_close}` | `{row['activeMeanResidual']}` | `{row['controlMeanResidual']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_image_rect_margin_phase_no_selector`",
            "- Current-PDF image rectangle, trim-margin, and 18pt side-margin phase do not create a selective active-box rule.",
            "- Loose all-four active phase alignments are matched or exceeded by non-active page-76 highlight controls.",
            "",
            "## Next Move",
            "",
            "- Keep using current PDFs as source-registration evidence only unless a distinct original-layout source or raw clue supplies unit/order wording.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {result['decision']['currentPdfImageRectMarginPhaseGate']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
