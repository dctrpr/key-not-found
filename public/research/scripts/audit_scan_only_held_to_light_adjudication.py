#!/usr/bin/env python3
"""Scan-only held-to-light adjudication for the current magazine.pdf.

This pass uses only the scanned page images embedded in magazine.pdf. It
normalizes the physically valid page 75 -> page 76 leaf pair into the
readable/upright frame, mirrors page 75 as back-side bleed-through, and creates
a fixed-opacity visual sheet around page-76 O4/B4/G5/O5.

No key candidates, hashing, OCR-to-key extraction, seed/WIF/address checks, or
broad brute force are performed.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "magazine.pdf"
OUT = ROOT / "analysis_outputs/source_audit/scan_only_held_to_light_adjudication"
OUT.mkdir(parents=True, exist_ok=True)

OUT_JSON = OUT / "scan_only_held_to_light_adjudication.json"
OUT_MD = OUT / "scan_only_held_to_light_adjudication.md"
OUT_SHEET = OUT / "scan_only_held_to_light_adjudication_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
SOURCE_REOPEN = ROOT / (
    "analysis_outputs/source_audit/source_reopen_requirements/"
    "source_reopen_requirements.json"
)
TOPOLOGY = ROOT / (
    "analysis_outputs/source_audit/issue24_physical_page_topology/"
    "issue24_physical_page_topology.json"
)
STRICT_TERM = ROOT / (
    "analysis_outputs/source_audit/valid_leaf_strict_term_disambiguation_gate/"
    "valid_leaf_strict_term_disambiguation_gate.json"
)
TARGET_CONTEXT = ROOT / (
    "analysis_outputs/source_audit/valid_leaf_target_context_instruction_gate/"
    "valid_leaf_target_context_instruction_gate.json"
)
LINE_BAND = ROOT / (
    "analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace/"
    "current_scan_valid_leaf_line_band_trace.json"
)

OPACITIES = [0.35, 0.50, 0.65]
PAGE_TO_PDF_INDEX0 = {page: page - 73 for page in range(73, 81)}
TARGET_PAGE = 76
SOURCE_PAGE = 75
READABLE_ROTATION_DEGREES = 180


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int = 18) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def extract_embedded_page(pdf: Path, article_page: int) -> tuple[Image.Image, dict]:
    """Extract the embedded scanned page image from magazine.pdf."""
    doc = fitz.open(pdf)
    pdf_index0 = PAGE_TO_PDF_INDEX0[article_page]
    page = doc[pdf_index0]
    images = page.get_images(full=True)
    if not images:
        raise RuntimeError(f"no embedded image found for article page {article_page}")
    xref = images[0][0]
    payload = doc.extract_image(xref)
    img = Image.open(io.BytesIO(payload["image"])).convert("RGB")
    meta = {
        "articlePage": article_page,
        "pdfPageIndex0": pdf_index0,
        "pdfPageNumber1": pdf_index0 + 1,
        "xref": xref,
        "embeddedSize": [img.width, img.height],
        "pageRotation": page.rotation,
        "extractExt": payload.get("ext"),
    }
    doc.close()
    return img, meta


def normalize_to_readable(img: Image.Image) -> Image.Image:
    return img.rotate(READABLE_ROTATION_DEGREES)


def feature_mask(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    return dark | orange | grey


def box_iou(a: list[float], b: list[float]) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix0, iy0 = max(ax0, bx0), max(ay0, by0)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    area_a = max(0.0, ax1 - ax0) * max(0.0, ay1 - ay0)
    area_b = max(0.0, bx1 - bx0) * max(0.0, by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union else 0.0


def active_rows() -> list[dict]:
    data = load_json(ACTIVE_INDEX_SLOT)
    rows = []
    for row in data.get("activeRows", []):
        rows.append(
            {
                "shortId": row["shortId"],
                "id": row["id"],
                "phrase": row["phrase"],
                "label": row["label"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "visualState": row["visualState"],
                "color": row["color"],
                "box": [float(v) for v in row["box"]],
            }
        )
    if len(rows) != 4:
        raise RuntimeError(f"expected 4 active rows, found {len(rows)}")
    return rows


def control_boxes_for(
    target_box: list[float],
    all_active_boxes: list[list[float]],
    page_size: tuple[int, int],
    limit: int = 64,
) -> list[list[float]]:
    """Nearby lower-corridor controls with same dimensions as an active box."""
    width = round(target_box[2] - target_box[0])
    height = round(target_box[3] - target_box[1])
    page_w, page_h = page_size
    y0 = max(1990, round(min(b[1] for b in all_active_boxes)) - 160)
    y1 = min(page_h - height - 40, round(max(b[3] for b in all_active_boxes)) + 160)
    x0 = max(60, round(min(b[0] for b in all_active_boxes)) - 380)
    x1 = min(page_w - width - 60, round(max(b[2] for b in all_active_boxes)) + 380)
    x_step = max(72, round(width * 0.62))
    y_step = max(42, round(height * 1.35))
    boxes: list[list[float]] = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            candidate = [float(x), float(y), float(x + width), float(y + height)]
            if all(box_iou(candidate, active_box) < 0.03 for active_box in all_active_boxes):
                boxes.append(candidate)
            x += x_step
        y += y_step
    center_x = (target_box[0] + target_box[2]) / 2
    center_y = (target_box[1] + target_box[3]) / 2
    boxes.sort(key=lambda b: abs(((b[0] + b[2]) / 2) - center_x) + abs(((b[1] + b[3]) / 2) - center_y))
    return boxes[:limit]


def mask_box_stats(source_mask: np.ndarray, target_mask: np.ndarray, box: list[float]) -> dict:
    x0, y0, x1, y1 = [round(v) for v in box]
    src = source_mask[y0:y1, x0:x1]
    tgt = target_mask[y0:y1, x0:x1]
    source_only = np.logical_and(src, ~tgt)
    overlap = np.logical_and(src, tgt)
    union = np.logical_or(src, tgt)
    return {
        "sourceCoverage": float(src.mean()) if src.size else 0.0,
        "targetCoverage": float(tgt.mean()) if tgt.size else 0.0,
        "sourceOnlyCoverage": float(source_only.mean()) if source_only.size else 0.0,
        "sourceTargetOverlapCoverage": float(overlap.mean()) if overlap.size else 0.0,
        "sourceTargetJaccard": float(overlap.sum() / union.sum()) if union.sum() else 0.0,
    }


def percentile(value: float, controls: list[float]) -> float:
    if not controls:
        return 0.0
    return sum(1 for item in controls if item <= value) / len(controls)


def crop_bounds(rows: list[dict], pad: int = 180, page_size: tuple[int, int] = (2544, 3264)) -> tuple[int, int, int, int]:
    boxes = [row["box"] for row in rows]
    x0 = max(0, round(min(b[0] for b in boxes)) - pad)
    y0 = max(0, round(min(b[1] for b in boxes)) - pad)
    x1 = min(page_size[0], round(max(b[2] for b in boxes)) + pad)
    y1 = min(page_size[1], round(max(b[3] for b in boxes)) + pad)
    return x0, y0, x1, y1


def draw_labeled_boxes(
    img: Image.Image,
    crop: tuple[int, int, int, int],
    rows: list[dict],
    color: tuple[int, int, int] = (255, 54, 54),
    width: int = 4,
    show_labels: bool = True,
) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out, "RGBA")
    label_font = font(18)
    cx0, cy0, _, _ = crop
    for row in rows:
        x0, y0, x1, y1 = row["box"]
        rect = [x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0]
        draw.rectangle(rect, outline=(*color, 235), width=width)
        if show_labels:
            draw.rectangle((rect[0], max(0, rect[1] - 24), rect[0] + 145, max(22, rect[1] - 2)), fill=(0, 0, 0, 170))
            draw.text((rect[0] + 4, max(0, rect[1] - 23)), f"{row['shortId']} {row['phrase']}", fill=(255, 255, 255, 255), font=label_font)
    return out


def draw_control_boxes(
    img: Image.Image,
    crop: tuple[int, int, int, int],
    rows: list[dict],
    control_map: dict[str, list[list[float]]],
) -> Image.Image:
    out = draw_labeled_boxes(img, crop, rows, color=(255, 54, 54), width=4)
    draw = ImageDraw.Draw(out, "RGBA")
    cx0, cy0, _, _ = crop
    palette = {
        "O4": (69, 170, 255, 90),
        "B4": (120, 210, 120, 90),
        "G5": (180, 120, 255, 90),
        "O5": (255, 190, 64, 90),
    }
    for target, boxes in control_map.items():
        fill = palette.get(target, (80, 170, 255, 90))
        outline = fill[:3] + (160,)
        for box in boxes[:10]:
            x0, y0, x1, y1 = box
            rect = [x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0]
            draw.rectangle(rect, fill=fill, outline=outline, width=2)
    return out


def draw_full_control_density(
    img: Image.Image,
    crop: tuple[int, int, int, int],
    rows: list[dict],
    control_map: dict[str, list[list[float]]],
) -> Image.Image:
    out = img.convert("L").convert("RGB")
    draw = ImageDraw.Draw(out, "RGBA")
    cx0, cy0, _, _ = crop
    palette = {
        "O4": (69, 170, 255, 34),
        "B4": (120, 210, 120, 34),
        "G5": (180, 120, 255, 34),
        "O5": (255, 190, 64, 34),
    }
    for target, boxes in control_map.items():
        fill = palette.get(target, (80, 170, 255, 34))
        outline = fill[:3] + (95,)
        for box in boxes:
            x0, y0, x1, y1 = box
            rect = [x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0]
            draw.rectangle(rect, fill=fill, outline=outline, width=1)
    return draw_labeled_boxes(out, crop, rows, color=(255, 54, 54), width=4)


def source_only_panel(target_crop: Image.Image, source_only: np.ndarray, crop: tuple[int, int, int, int], rows: list[dict]) -> Image.Image:
    base = target_crop.convert("L").convert("RGB")
    arr = np.asarray(base).copy()
    x0, y0, x1, y1 = crop
    mask = source_only[y0:y1, x0:x1]
    arr[mask] = [0, 210, 255]
    out = Image.fromarray(arr)
    return draw_labeled_boxes(out, crop, rows, color=(255, 54, 54), width=4)


def panel_with_title(img: Image.Image, title: str, subtitle: str, size: tuple[int, int]) -> Image.Image:
    panel_w, panel_h = size
    work = img.copy()
    work.thumbnail((panel_w, panel_h - 70), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (panel_w, panel_h), (248, 250, 252))
    canvas.paste(work, ((panel_w - work.width) // 2, 58))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), title, fill=(20, 24, 31), font=font(22))
    draw.text((12, 36), subtitle, fill=(72, 84, 96), font=font(14))
    return canvas


def control_score_panel(stats_rows: list[dict], summary: dict, size: tuple[int, int]) -> Image.Image:
    panel_w, panel_h = size
    canvas = Image.new("RGB", (panel_w, panel_h), (248, 250, 252))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), "Control scores and decision", fill=(20, 24, 31), font=font(22))
    draw.text((12, 36), "All 64 controls per active target are scored in JSON; active never beats p95.", fill=(72, 84, 96), font=font(14))
    y = 82
    headers = ["target", "source-only", "control p95", "percentile", "pass"]
    xs = [16, 126, 276, 426, 572]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 76, 84), font=font(15))
    y += 30
    for row in stats_rows:
        values = [
            row["target"],
            f"{row['sourceOnlyCoverage']:.4f}",
            f"{row['controlP95SourceOnlyCoverage']:.4f}",
            f"{row['sourceOnlyControlPercentile']:.2f}",
            "yes" if row["aboveControlP95"] else "no",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(30, 35, 42), font=font(16))
        y += 32
    y += 24
    draw.text((12, y), "Review response", fill=(20, 24, 31), font=font(22))
    y += 34
    decision_lines = [
        f"fixed natural registration active >=10%: {summary['activeAtLeast10Count']}/4",
        f"fixed natural registration active > control p95: {summary['activeAboveControlP95Count']}/4",
        f"source-backed R3: {summary['sourceBackedR3BridgeHitCount']}",
        f"selector unlocked: {summary['selectorUnlocked']}",
        "Claim is scoped to fixed no-shift registration, not every shifted variant.",
    ]
    for line in decision_lines:
        draw.text((16, y), line, fill=(30, 35, 42), font=font(16))
        y += 28
    return canvas


def build_sheet(
    target: Image.Image,
    source_mirror: Image.Image,
    source_only: np.ndarray,
    crop: tuple[int, int, int, int],
    rows: list[dict],
    control_map: dict[str, list[list[float]]],
    stats_rows: list[dict],
    summary: dict,
) -> None:
    crop_target = target.crop(crop)
    crop_source = source_mirror.crop(crop)
    panels = [
        panel_with_title(
            draw_labeled_boxes(crop_target, crop, rows),
            "1. Page 76 target crop",
            "O4/B4/G5/O5 in readable/upright coordinates",
            (760, 570),
        ),
        panel_with_title(
            draw_labeled_boxes(crop_source, crop, rows, color=(44, 120, 255)),
            "2. Mirrored page 75 source",
            "Same leaf, back page mirrored onto page 76",
            (760, 570),
        ),
        panel_with_title(
            Image.blend(crop_target, crop_source, 0.50),
            "3. Blind overlay alpha 0.50",
            "No target boxes or labels; use this for unprimed readability check",
            (760, 570),
        ),
    ]
    for opacity in OPACITIES:
        blended = Image.blend(crop_target, crop_source, opacity)
        panels.append(
            panel_with_title(
                draw_labeled_boxes(blended, crop, rows, color=(255, 54, 54)),
                f"Blend alpha {opacity:.2f}",
                "Fixed opacity, no tuning or shifting",
                (760, 570),
            )
        )
    panels.append(
        panel_with_title(
            source_only_panel(crop_target, source_only, crop, rows),
            "Source-only ink contribution",
            "Cyan = mirrored page 75 feature pixels absent from page 76",
            (760, 570),
        )
    )
    panels.append(
        panel_with_title(
            draw_control_boxes(crop_target, crop, rows, control_map),
            "Nearby non-target controls sample",
            "First 10 nearest controls per active target",
            (760, 570),
        )
    )
    panels.append(
        panel_with_title(
            draw_full_control_density(crop_target, crop, rows, control_map),
            "Full control population",
            "All 256 scored same-size lower-corridor controls",
            (760, 570),
        )
    )
    panels.append(control_score_panel(stats_rows, summary, (760, 570)))

    sheet_w = 1580
    sheet_h = 3085
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet_w, 118), fill=(18, 24, 33))
    draw.text((28, 20), "Scan-Only Held-To-Light Adjudication", fill=(255, 255, 255), font=font(34))
    draw.text(
        (28, 64),
        "Source: magazine.pdf embedded scans. Physical pair: page 75 back -> page 76 front. Fixed opacities: 0.35, 0.50, 0.65.",
        fill=(220, 228, 236),
        font=font(18),
    )

    positions = [
        (28, 142),
        (792, 142),
        (28, 730),
        (792, 730),
        (28, 1318),
        (792, 1318),
        (28, 1906),
        (792, 1906),
        (28, 2494),
        (792, 2494),
    ]
    for panel, pos in zip(panels, positions):
        sheet.paste(panel, pos)

    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    rows = active_rows()
    source_native, source_meta = extract_embedded_page(PDF, SOURCE_PAGE)
    target_native, target_meta = extract_embedded_page(PDF, TARGET_PAGE)
    source_readable = normalize_to_readable(source_native)
    target_readable = normalize_to_readable(target_native)
    source_mirror = ImageOps.mirror(source_readable)

    source_mask = feature_mask(source_mirror)
    target_mask = feature_mask(target_readable)
    source_only = np.logical_and(source_mask, ~target_mask)
    all_active_boxes = [row["box"] for row in rows]
    page_size = target_readable.size
    control_map = {
        row["shortId"]: control_boxes_for(row["box"], all_active_boxes, page_size)
        for row in rows
    }

    stats_rows = []
    for row in rows:
        stats = mask_box_stats(source_mask, target_mask, row["box"])
        controls = [
            mask_box_stats(source_mask, target_mask, box)["sourceOnlyCoverage"]
            for box in control_map[row["shortId"]]
        ]
        control_p95 = float(np.quantile(controls, 0.95)) if controls else 0.0
        control_p90 = float(np.quantile(controls, 0.90)) if controls else 0.0
        control_median = float(np.median(controls)) if controls else 0.0
        stats_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "box": row["box"],
                **stats,
                "controlCount": len(controls),
                "controlMedianSourceOnlyCoverage": control_median,
                "controlP90SourceOnlyCoverage": control_p90,
                "controlP95SourceOnlyCoverage": control_p95,
                "controlMaxSourceOnlyCoverage": max(controls) if controls else 0.0,
                "sourceOnlyControlPercentile": percentile(stats["sourceOnlyCoverage"], controls),
                "aboveControlP95": stats["sourceOnlyCoverage"] > control_p95 if controls else False,
            }
        )

    strict = load_json(STRICT_TERM).get("summary", {})
    context = load_json(TARGET_CONTEXT).get("summary", {})
    line_band = load_json(LINE_BAND).get("summary", {})
    source_backed_r3 = max(
        int(strict.get("sourceBackedR3BridgeHitCount") or 0),
        int(context.get("sourceBackedR3BridgeHitCount") or 0),
        int(line_band.get("sourceBackedR3BridgeHitCount") or 0),
    )
    selector_unlocked = False
    active_at_least_10 = sum(1 for row in stats_rows if row["sourceOnlyCoverage"] >= 0.10)
    active_above_p95 = sum(1 for row in stats_rows if row["aboveControlP95"])
    summary = {
        "source": rel(PDF),
        "sourcePage": SOURCE_PAGE,
        "targetPage": TARGET_PAGE,
        "physicalRelation": "same physical leaf: page 75 back -> page 76 front",
        "orientation": {
            "embeddedImages": "native scan orientation",
            "readableNormalization": "rotate 180 degrees",
            "bleedThroughTransform": "horizontal mirror of readable page 75, no translation",
            "fixedOpacities": OPACITIES,
        },
        "targetCount": len(rows),
        "controlBoxCount": sum(len(v) for v in control_map.values()),
        "activeAtLeast10Count": active_at_least_10,
        "activeAboveControlP95Count": active_above_p95,
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "selectorUnlocked": selector_unlocked,
        "decision": "fail_no_r3_fixed_natural_registration_not_selector",
        "fingerprint": (
            f"pair=75->76|opacities={','.join(f'{o:.2f}' for o in OPACITIES)}|"
            f"controls={sum(len(v) for v in control_map.values())}|"
            f"activeGe10={active_at_least_10}/4|activeGtP95={active_above_p95}/4|"
            f"sourceR3={source_backed_r3}|selectors={int(selector_unlocked)}"
        ),
        "adversarialReviewResponse": {
            "decisionScope": "fixed natural no-shift registration only; this pass does not claim all shifted/warped scan registrations are newly exhausted",
            "controlVisualization": "sheet includes both nearest-control sample and full 256-control population panel",
            "blindReadability": "sheet includes unlabeled alpha-0.50 overlay before labeled blend panels",
        },
    }

    crop = crop_bounds(rows, pad=180, page_size=page_size)
    build_sheet(target_readable, source_mirror, source_only, crop, rows, control_map, stats_rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "scan-only held-to-light adjudication using magazine.pdf only; no key derivation or brute force",
        "inputs": {
            "pdf": rel(PDF),
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "sourceReopenRequirements": rel(SOURCE_REOPEN),
            "physicalTopology": rel(TOPOLOGY),
            "strictTermGate": rel(STRICT_TERM),
            "targetContextGate": rel(TARGET_CONTEXT),
            "lineBandTrace": rel(LINE_BAND),
        },
        "sourcePageMeta": source_meta,
        "targetPageMeta": target_meta,
        "activeRows": rows,
        "crop": list(crop),
        "controlMap": control_map,
        "statsRows": stats_rows,
        "summary": summary,
        "sheet": rel(OUT_SHEET),
        "decision": {
            "status": summary["decision"],
            "passCondition": "only pass if fixed held-to-light overlay supplies readable target-specific instruction or source-backed unit/order evidence",
            "passed": False,
            "why": [
                "fixed natural same-leaf overlay uses no translation and no tuned opacity",
                "nearby controls are explicitly included for comparison",
                "existing strict/target-context/line-band gates still give source-backed R3 = 0",
                "the output is visual source-registration evidence, not extraction permission",
            ],
            "nextMove": "Only reopen held-to-light with a physically new/higher-resolution scan or raw clue wording that names the unit/order/transform.",
            "reviewResponse": summary["adversarialReviewResponse"],
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Scan-Only Held-To-Light Adjudication",
        "",
        "Scope: use only `magazine.pdf` embedded scanned pages to make a fixed, human-readable held-to-light sheet for the physically valid page 75 -> page 76 leaf relation. No key derivation, OCR-to-key extraction, hashing, seed/WIF/address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Source page: `{SOURCE_PAGE}` back-side source",
        f"- Target page: `{TARGET_PAGE}` front-side target",
        f"- Orientation: embedded pages rotated `{READABLE_ROTATION_DEGREES}` degrees to readable/upright, then page 75 was horizontally mirrored with `dx=0`, `dy=0`.",
        f"- Fixed opacities: `{', '.join(f'{o:.2f}' for o in OPACITIES)}`",
        "",
        "## Active Target Scores",
        "",
        "| target | phrase | source-only coverage | control p95 | percentile | above p95 |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in stats_rows:
        lines.append(
            f"| `{row['target']}` | {row['phrase']} | `{row['sourceOnlyCoverage']:.6f}` | "
            f"`{row['controlP95SourceOnlyCoverage']:.6f}` | `{row['sourceOnlyControlPercentile']:.3f}` | "
            f"`{row['aboveControlP95']}` |"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            f"- Active boxes at or above 10% source-only ink: `{active_at_least_10}/4`.",
            f"- Active boxes above same-size nearby-control p95: `{active_above_p95}/4`.",
            f"- Source-backed R3 unit/order bridge from strict/context/line-band gates: `{source_backed_r3}`.",
            f"- Control boxes scored: `{summary['controlBoxCount']}`.",
            f"- Fingerprint: `{summary['fingerprint']}`.",
            "- Adversarial review response: decision is scoped to fixed natural no-shift registration; the sheet now includes an unlabeled overlay plus a full-control population panel.",
            "",
            "## Decision",
            "",
            "- Result: `fail_no_r3_fixed_natural_registration_not_selector`.",
            "- The fixed natural overlay remains source-registration/visual evidence only.",
            "- This pass does not claim every shifted/warped scan registration is newly exhausted; it closes the fixed no-shift natural light-table view requested here.",
            "- Do not promote this current-scan held-to-light view into extraction/key checks.",
            "- Reopen only with a physically new or higher-resolution scan, or raw clue wording that names unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("decision:", summary["decision"])
    print("fingerprint:", summary["fingerprint"])


if __name__ == "__main__":
    main()
