#!/usr/bin/env python3
"""Audit content-box registration as a current-scan held-to-light cue.

This pass follows the page-frame/trim audit. It asks whether the visible
content envelope in the current page rasters can justify a held-to-light
registration correction, and then measures the bounded effect of that
content-box correction on the valid page-75 -> page-76 source-ink landing.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/source_audit/current_scan_content_box_registration_gate"
JSON_OUT = OUT_DIR / "current_scan_content_box_registration_gate.json"
MD_OUT = OUT_DIR / "current_scan_content_box_registration_gate.md"
SHEET_OUT = OUT_DIR / "current_scan_content_box_registration_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
SOURCE_INK_LANDING = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_source_ink_landing_gate/"
    "current_scan_valid_leaf_source_ink_landing_gate.json"
)
JITTER_SOURCE_INK = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_valid_leaf_jitter_source_ink_rescue_gate/"
    "current_scan_valid_leaf_jitter_source_ink_rescue_gate.json"
)
PAGE_FRAME_TRIM = (
    ROOT
    / "analysis_outputs/source_audit/current_scan_page_frame_trim_registration_gate/"
    "current_scan_page_frame_trim_registration_gate.json"
)
REOPEN_TRIGGER_MATRIX = (
    ROOT
    / "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAGES = [75, 76, 78, 79]
VALID_PAIR = (75, 76)
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
PAIR_ROWS = [(75, 76), (78, 79), (76, 75), (79, 78), (75, 78), (76, 79)]

INK_LUMA_THRESHOLD = 238.0
CONTENT_LUMA_THRESHOLD = 244.0
SATURATION_THRESHOLD = 18.0
ROW_SHARE_THRESHOLD = 0.003
COL_SHARE_THRESHOLD = 0.003
SUPPORT_THRESHOLD = 0.05
WEAK_SUPPORT_THRESHOLD = 0.01


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for item in candidates:
        if item and Path(item).exists():
            try:
                return ImageFont.truetype(item, size)
            except OSError:
                pass
    return ImageFont.load_default()


def normalize_page(page: int) -> tuple[Image.Image, str]:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    upright = Image.open(upright_path).convert("RGB")
    if not source_path.exists():
        return upright, "upright_only"
    source = Image.open(source_path).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    if rot_diff < same_diff:
        return source.rotate(180), "source_rot180_to_readable"
    return source, "source_as_readable"


def saturation(arr: np.ndarray) -> np.ndarray:
    return arr.max(axis=2) - arr.min(axis=2)


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def content_mask(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    return (luma(arr) < CONTENT_LUMA_THRESHOLD) | (saturation(arr) > SATURATION_THRESHOLD)


def robust_bbox(
    mask: np.ndarray,
    y0: int,
    y1: int,
    row_threshold: float = ROW_SHARE_THRESHOLD,
    col_threshold: float = COL_SHARE_THRESHOLD,
) -> list[int] | None:
    band = mask[y0:y1, :]
    rows = np.flatnonzero(band.mean(axis=1) > row_threshold)
    cols = np.flatnonzero(band.mean(axis=0) > col_threshold)
    if len(rows) == 0 or len(cols) == 0:
        return None
    return [int(cols.min()), int(rows.min() + y0), int(cols.max() + 1), int(rows.max() + y0 + 1)]


def box_center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def box_width(box: list[float]) -> float:
    return max(0.0, box[2] - box[0])


def box_height(box: list[float]) -> float:
    return max(0.0, box[3] - box[1])


def mirror_box(box: list[int], width: int) -> list[int]:
    return [int(width - box[2]), int(box[1]), int(width - box[0]), int(box[3])]


def summarize_box(page: int, kind: str, image: Image.Image, mask: np.ndarray, box: list[int]) -> dict[str, Any]:
    width, height = image.size
    band_clipped = kind == "lower_half_content" and box[1] == height // 2
    return {
        "page": page,
        "kind": kind,
        "box": box,
        "width": int(box_width(box)),
        "height": int(box_height(box)),
        "center": [round(v, 3) for v in box_center(box)],
        "contentShare": round(float(mask.mean()), 6),
        "touchesCanvasLeft": box[0] <= 40,
        "touchesCanvasTop": box[1] <= 40,
        "touchesCanvasRight": box[2] >= width - 40,
        "touchesCanvasBottom": box[3] >= height - 40,
        "bandBoundaryClipped": band_clipped,
    }


def page_boxes(page: int) -> tuple[Image.Image, dict[str, Any]]:
    image, source_mode = normalize_page(page)
    mask = content_mask(image)
    width, height = image.size
    boxes: dict[str, Any] = {}
    all_box = robust_bbox(mask, 0, height)
    lower_box = robust_bbox(mask, height // 2, height)
    if all_box is None or lower_box is None:
        raise RuntimeError(f"content box detection failed for page {page}")
    boxes["all_content"] = summarize_box(page, "all_content", image, mask, all_box)
    boxes["lower_half_content"] = summarize_box(
        page, "lower_half_content", image, mask, lower_box
    )
    return image, {
        "page": page,
        "sourceMode": source_mode,
        "size": [width, height],
        "boxes": boxes,
    }


def pair_transform(
    source_page: int,
    target_page: int,
    kind: str,
    page_rows: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    source = page_rows[source_page]
    target = page_rows[target_page]
    width = int(source["size"][0])
    source_box = source["boxes"][kind]["box"]
    target_box = target["boxes"][kind]["box"]
    mirrored_source_box = mirror_box(source_box, width)
    source_center = box_center(mirrored_source_box)
    target_center = box_center(target_box)
    dx = target_center[0] - source_center[0]
    dy = target_center[1] - source_center[1]
    sx = box_width(target_box) / box_width(mirrored_source_box) if box_width(mirrored_source_box) else 0.0
    sy = box_height(target_box) / box_height(mirrored_source_box) if box_height(mirrored_source_box) else 0.0
    return {
        "pair": f"{source_page}->{target_page}",
        "sourcePage": source_page,
        "targetPage": target_page,
        "kind": kind,
        "sourceBox": source_box,
        "mirroredSourceBox": mirrored_source_box,
        "targetBox": target_box,
        "dx": round(dx, 3),
        "dy": round(dy, 3),
        "shiftMagnitudePx": round(math.hypot(dx, dy), 3),
        "scaleX": round(sx, 6),
        "scaleY": round(sy, 6),
        "sourceTouchesCanvasOrBand": {
            "left": source["boxes"][kind]["touchesCanvasLeft"],
            "right": source["boxes"][kind]["touchesCanvasRight"],
            "top": source["boxes"][kind]["touchesCanvasTop"],
            "bottom": source["boxes"][kind]["touchesCanvasBottom"],
            "bandBoundary": source["boxes"][kind]["bandBoundaryClipped"],
        },
        "targetTouchesCanvasOrBand": {
            "left": target["boxes"][kind]["touchesCanvasLeft"],
            "right": target["boxes"][kind]["touchesCanvasRight"],
            "top": target["boxes"][kind]["touchesCanvasTop"],
            "bottom": target["boxes"][kind]["touchesCanvasBottom"],
            "bandBoundary": target["boxes"][kind]["bandBoundaryClipped"],
        },
    }


def range_or_zero(values: list[float]) -> float:
    return float(max(values) - min(values)) if values else 0.0


def median_or_zero(values: list[float]) -> float:
    return float(median(values)) if values else 0.0


def shift_stability(pair_rows: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    rows = [row for row in pair_rows if row["kind"] == kind]
    dxs = [float(row["dx"]) for row in rows]
    dys = [float(row["dy"]) for row in rows]
    mags = [float(row["shiftMagnitudePx"]) for row in rows]
    sx = [float(row["scaleX"]) for row in rows]
    sy = [float(row["scaleY"]) for row in rows]
    dx_range = range_or_zero(dxs)
    dy_range = range_or_zero(dys)
    scale_x_range = range_or_zero(sx)
    scale_y_range = range_or_zero(sy)
    stable = bool(dx_range <= 8.0 and dy_range <= 4.0 and scale_x_range <= 0.03 and scale_y_range <= 0.01)
    return {
        "kind": kind,
        "pairCount": len(rows),
        "dxRangePx": round(dx_range, 3),
        "dyRangePx": round(dy_range, 3),
        "shiftMagnitudeRangePx": round(range_or_zero(mags), 3),
        "medianDxPx": round(median_or_zero(dxs), 3),
        "medianDyPx": round(median_or_zero(dys), 3),
        "scaleXRange": round(scale_x_range, 6),
        "scaleYRange": round(scale_y_range, 6),
        "stableByThreshold": stable,
    }


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") in TARGET_ORDER:
            rows.append(
                {
                    "shortId": row["shortId"],
                    "phrase": row["phrase"],
                    "visualState": row["visualState"],
                    "pageLine": int(row["pageLine"]),
                    "box": [float(v) for v in row["box"]],
                }
            )
    rows.sort(key=lambda item: TARGET_ORDER.index(item["shortId"]))
    return rows


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    height, width = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(width, x0))
    x1 = max(0, min(width, x1))
    y0 = max(0, min(height, y0))
    y1 = max(0, min(height, y1))
    return mask[y0:y1, x0:x1]


def shifted_mirrored_source(page: Image.Image, dx: float, dy: float) -> Image.Image:
    mirrored = ImageOps.mirror(page)
    canvas = Image.new("RGB", page.size, "white")
    canvas.paste(mirrored, (int(round(dx)), int(round(dy))))
    return canvas


def measure_source_landing(
    source_page_image: Image.Image,
    active: list[dict[str, Any]],
    mode_id: str,
    dx: float,
    dy: float,
) -> dict[str, Any]:
    source_landing = shifted_mirrored_source(source_page_image, dx, dy)
    source_arr = np.asarray(source_landing.convert("RGB"), dtype=np.float32)
    source_mask = luma(source_arr) < INK_LUMA_THRESHOLD
    target_rows = []
    for row in active:
        region = crop_bool(source_mask, row["box"])
        pixel_count = int(region.size)
        ink_count = int(region.sum())
        ratio = ink_count / pixel_count if pixel_count else 0.0
        target_rows.append(
            {
                "target": row["shortId"],
                "phrase": row["phrase"],
                "visualState": row["visualState"],
                "box": [round(float(v), 3) for v in row["box"]],
                "sourceInkPixelCount": ink_count,
                "pixelCount": pixel_count,
                "sourceInkRatio": round(ratio, 6),
                "weakSourceSupported": ratio >= WEAK_SUPPORT_THRESHOLD,
                "sourceSupported": ratio >= SUPPORT_THRESHOLD,
            }
        )
    supported = [row["target"] for row in target_rows if row["sourceSupported"]]
    weak = [row["target"] for row in target_rows if row["weakSourceSupported"]]
    zero = [row["target"] for row in target_rows if row["sourceInkPixelCount"] == 0]
    return {
        "modeId": mode_id,
        "dx": round(float(dx), 3),
        "dy": round(float(dy), 3),
        "targetRows": target_rows,
        "activeSourceSupportedTargets": supported,
        "weakSourceSupportedTargets": weak,
        "zeroSourceInkTargets": zero,
        "activeSourceSupportedCount": len(supported),
        "weakActiveSourceSupportedCount": len(weak),
        "allFourSourceSupported": len(supported) == 4,
        "allFourWeakSourceSupported": len(weak) == 4,
    }


def load_trigger_summary() -> dict[str, int]:
    data = load_json(REOPEN_TRIGGER_MATRIX)
    summary = data.get("summary", {})
    return {
        "sourceBackedR3BridgeHitCount": int(summary.get("sourceBackedR3BridgeHitCount", 0) or 0),
        "satisfiedReopenTriggerCount": int(
            summary.get("satisfiedReopenTriggerCount", summary.get("satisfiedTriggerCount", 0)) or 0
        ),
        "triggerCount": int(summary.get("triggerCount", 0) or 0),
    }


def draw_sheet(
    images: dict[int, Image.Image],
    page_rows: dict[int, dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    landing_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    sheet = Image.new("RGB", (1960, 1320), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    title = safe_font(32, bold=True)
    header = safe_font(22, bold=True)
    body = safe_font(19)
    small = safe_font(15)

    draw.text((36, 28), "Current Scan Content-Box Registration Gate", fill=(15, 23, 42), font=title)
    y = 82
    for line in [
        f"Decision: {summary['decision']}",
        f"Valid pair: {summary['validPair']} | all shift: {summary['validPairAllContentShift']} | lower shift: {summary['validPairLowerHalfShift']}",
        f"Lower content shift stable: {int(summary['lowerHalfContentShiftStable'])} | content-box candidate: {int(summary['contentBoxRegistrationCandidate'])}",
        f"Best content-box landing: {summary['bestLandingModeId']} with {summary['bestLandingSupportedCount']}/4 supported; B4 remains {summary['b4BestSourceInkRatio']:.4f}",
    ]:
        draw.text((36, y), line, fill=(30, 41, 59), font=body)
        y += 30

    thumb_w, thumb_h = 235, 302
    x = 36
    y = 230
    for page in PAGES:
        image = images[page].copy()
        scale_x = thumb_w / image.size[0]
        scale_y = thumb_h / image.size[1]
        thumb = image.resize((thumb_w, thumb_h))
        overlay = ImageDraw.Draw(thumb)
        all_box = page_rows[page]["boxes"]["all_content"]["box"]
        low_box = page_rows[page]["boxes"]["lower_half_content"]["box"]
        for box, color in [(all_box, (220, 38, 38)), (low_box, (37, 99, 235))]:
            scaled = [
                box[0] * scale_x,
                box[1] * scale_y,
                box[2] * scale_x,
                box[3] * scale_y,
            ]
            overlay.rectangle(scaled, outline=color, width=3)
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_h + 8), f"p{page}: red=all, blue=lower", fill=(30, 41, 59), font=small)
        x += thumb_w + 28

    x0 = 36
    y = 610
    draw.text((x0, y), "Content-Box Pair Transforms", fill=(15, 23, 42), font=header)
    y += 34
    cols = [x0, x0 + 100, x0 + 310, x0 + 405, x0 + 500, x0 + 625, x0 + 730, x0 + 860]
    headers = ["pair", "kind", "dx", "dy", "mag", "scale x", "scale y", "touches edge/band"]
    for cx, label in zip(cols, headers):
        draw.text((cx, y), label, fill=(51, 65, 85), font=small)
    y += 24
    for row in pair_rows:
        touch = row["sourceTouchesCanvasOrBand"]
        target_touch = row["targetTouchesCanvasOrBand"]
        vals = [
            row["pair"],
            row["kind"].replace("_content", "").replace("_", " "),
            f"{row['dx']:.1f}",
            f"{row['dy']:.1f}",
            f"{row['shiftMagnitudePx']:.1f}",
            f"{row['scaleX']:.4f}",
            f"{row['scaleY']:.4f}",
            f"S:{int(any(touch.values()))} T:{int(any(target_touch.values()))}",
        ]
        for cx, val in zip(cols, vals):
            draw.text((cx, y), str(val), fill=(30, 41, 59), font=small)
        y += 22

    x0 = 1120
    y = 230
    draw.text((x0, y), "Source-Ink Landing After Content-Box Shift", fill=(15, 23, 42), font=header)
    y += 34
    cols = [x0, x0 + 160, x0 + 230, x0 + 300, x0 + 370, x0 + 440, x0 + 520, x0 + 610]
    headers = ["mode", "O4", "B4", "G5", "O5", ">=5%", "weak", "zero"]
    for cx, label in zip(cols, headers):
        draw.text((cx, y), label, fill=(51, 65, 85), font=small)
    y += 24
    for landing in landing_rows:
        by_target = {row["target"]: row for row in landing["targetRows"]}
        vals = [
            landing["modeId"],
            f"{by_target['O4']['sourceInkRatio']:.4f}",
            f"{by_target['B4']['sourceInkRatio']:.4f}",
            f"{by_target['G5']['sourceInkRatio']:.4f}",
            f"{by_target['O5']['sourceInkRatio']:.4f}",
            f"{landing['activeSourceSupportedCount']}/4",
            f"{landing['weakActiveSourceSupportedCount']}/4",
            ",".join(landing["zeroSourceInkTargets"]) or "-",
        ]
        for cx, val in zip(cols, vals):
            draw.text((cx, y), str(val)[:20], fill=(30, 41, 59), font=small)
        y += 26

    y += 28
    draw.text((x0, y), "Interpretation", fill=(15, 23, 42), font=header)
    y += 34
    notes = [
        "The all-page content envelope is not stable: vertical shifts vary by page content.",
        "The lower-half envelope has a repeatable x bias, but it is clipped to canvas/band edges.",
        "Applying the lower content-box shift still leaves B4 at zero source ink and no all-four landing.",
        "So content-box normalization is a source-review witness, not a held-to-light selector.",
    ]
    for note in notes:
        draw.text((x0 + 8, y), "- " + note, fill=(30, 41, 59), font=body)
        y += 30

    sheet.save(SHEET_OUT, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current Scan Content-Box Registration Gate",
        "",
        "Scope: tested whether the visible content envelope in the current page rasters can justify changing valid page-75 -> page-76 held-to-light registration. This is a bounded source/geometry pass only; no key extraction, candidates, hashing-to-key, WIF/seed/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Pages checked: `{summary['pagesChecked']}`",
        f"- Valid pair / same canvas: `{summary['validPair']}` / `{int(summary['sameCanvasValidPair'])}`",
        f"- Valid all-content shift dx,dy: `{summary['validPairAllContentShift']}`",
        f"- Valid lower-half shift dx,dy: `{summary['validPairLowerHalfShift']}`",
        f"- All-content shift stable / lower-half shift stable: `{int(summary['allContentShiftStable'])}` / `{int(summary['lowerHalfContentShiftStable'])}`",
        f"- Content-box registration candidate / hidden content-box candidate: `{int(summary['contentBoxRegistrationCandidate'])}` / `{int(summary['hiddenContentBoxCandidate'])}`",
        f"- Best content-box landing: `{summary['bestLandingModeId']}` with `{summary['bestLandingSupportedCount']}/4` source-supported targets",
        f"- Best B4 source-ink ratio: `{summary['b4BestSourceInkRatio']:.6f}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Fingerprint: `{summary['contentBoxRegistrationFingerprint']}`",
        "",
        "## Content Box Rows",
        "",
        "| page | kind | box | width | height | center | edge/band clipped |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    for row in result["contentBoxRows"]:
        clipped = (
            row["touchesCanvasLeft"]
            or row["touchesCanvasTop"]
            or row["touchesCanvasRight"]
            or row["touchesCanvasBottom"]
            or row["bandBoundaryClipped"]
        )
        lines.append(
            f"| `{row['page']}` | `{row['kind']}` | `{row['box']}` | `{row['width']}` | `{row['height']}` | `{row['center']}` | `{int(clipped)}` |"
        )
    lines.extend(
        [
            "",
            "## Pair Transforms",
            "",
            "| pair | kind | dx | dy | magnitude | scale x | scale y | source edge/band | target edge/band |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in result["pairRows"]:
        source_touch = int(any(row["sourceTouchesCanvasOrBand"].values()))
        target_touch = int(any(row["targetTouchesCanvasOrBand"].values()))
        lines.append(
            f"| `{row['pair']}` | `{row['kind']}` | `{row['dx']}` | `{row['dy']}` | `{row['shiftMagnitudePx']}` | `{row['scaleX']}` | `{row['scaleY']}` | `{source_touch}` | `{target_touch}` |"
        )
    lines.extend(
        [
            "",
            "## Source-Ink Landing Rows",
            "",
            "| mode | dx | dy | O4 | B4 | G5 | O5 | supported | weak supported | zero-source targets |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for landing in result["landingRows"]:
        by_target = {row["target"]: row for row in landing["targetRows"]}
        lines.append(
            f"| `{landing['modeId']}` | `{landing['dx']}` | `{landing['dy']}` | "
            f"`{by_target['O4']['sourceInkRatio']:.6f}` | `{by_target['B4']['sourceInkRatio']:.6f}` | "
            f"`{by_target['G5']['sourceInkRatio']:.6f}` | `{by_target['O5']['sourceInkRatio']:.6f}` | "
            f"`{landing['activeSourceSupportedCount']}/4` | `{landing['weakActiveSourceSupportedCount']}/4` | "
            f"`{','.join(landing['zeroSourceInkTargets']) if landing['zeroSourceInkTargets'] else '-'}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{summary['decision']}`",
            "- The all-page content envelope is not a stable registration frame: its vertical shift changes with page content.",
            "- The lower-half envelope has a repeatable roughly 33 px horizontal bias, but it is clipped to canvas and band edges, so it is not an independent physical page-frame cue.",
            "- Applying the lower-half content-box shift does not rescue the valid held-to-light landing: B4 remains at zero source ink, and no mode supports all four active boxes.",
            "- This closes content-envelope normalization as a current-scan held-to-light selector.",
            "",
            "## Next Move",
            "",
            "- Best direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.",
        ]
    )
    MD_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    active_index = load_json(ACTIVE_INDEX_SLOT)
    active = active_boxes(active_index)

    images: dict[int, Image.Image] = {}
    page_rows_by_page: dict[int, dict[str, Any]] = {}
    for page in PAGES:
        image, row = page_boxes(page)
        images[page] = image
        page_rows_by_page[page] = row

    content_box_rows = []
    for page in PAGES:
        for kind in ["all_content", "lower_half_content"]:
            content_box_rows.append(page_rows_by_page[page]["boxes"][kind])

    pair_rows = []
    for source_page, target_page in PAIR_ROWS:
        for kind in ["all_content", "lower_half_content"]:
            pair_rows.append(pair_transform(source_page, target_page, kind, page_rows_by_page))

    valid_all = next(row for row in pair_rows if row["pair"] == "75->76" and row["kind"] == "all_content")
    valid_lower = next(row for row in pair_rows if row["pair"] == "75->76" and row["kind"] == "lower_half_content")
    all_stability = shift_stability(pair_rows, "all_content")
    lower_stability = shift_stability(pair_rows, "lower_half_content")

    source_page = images[75]
    landing_rows = [
        measure_source_landing(source_page, active, "natural_hflip", 0, 0),
        measure_source_landing(
            source_page,
            active,
            "all_content_box_translation",
            float(valid_all["dx"]),
            float(valid_all["dy"]),
        ),
        measure_source_landing(
            source_page,
            active,
            "lower_half_content_box_translation",
            float(valid_lower["dx"]),
            float(valid_lower["dy"]),
        ),
    ]

    best_landing = max(
        landing_rows,
        key=lambda row: (
            row["activeSourceSupportedCount"],
            row["weakActiveSourceSupportedCount"],
            -abs(row["dx"]) - abs(row["dy"]),
        ),
    )
    b4_best = max(
        row["targetRows"][TARGET_ORDER.index("B4")]["sourceInkRatio"] for row in landing_rows
    )
    trigger_summary = load_trigger_summary()
    same_canvas_valid_pair = page_rows_by_page[75]["size"] == page_rows_by_page[76]["size"]
    all_content_shift_stable = bool(all_stability["stableByThreshold"])
    lower_half_shift_stable = bool(lower_stability["stableByThreshold"])
    lower_boxes_clipped = all(
        row["kind"] == "lower_half_content"
        and (
            row["touchesCanvasLeft"]
            or row["touchesCanvasRight"]
            or row["touchesCanvasBottom"]
            or row["bandBoundaryClipped"]
        )
        for row in content_box_rows
        if row["kind"] == "lower_half_content"
    )
    content_box_candidate = bool(
        same_canvas_valid_pair
        and (all_content_shift_stable or lower_half_shift_stable)
        and not lower_boxes_clipped
        and best_landing["allFourSourceSupported"]
    )
    hidden_candidate = False

    fingerprint = (
        f"pages={len(PAGES)}|pair=75->76|sameCanvas={int(same_canvas_valid_pair)}"
        f"|allShift={valid_all['dx']:.1f},{valid_all['dy']:.1f}"
        f"|lowerShift={valid_lower['dx']:.1f},{valid_lower['dy']:.1f}"
        f"|allStable={int(all_content_shift_stable)}|lowerStable={int(lower_half_shift_stable)}"
        f"|natural={landing_rows[0]['activeSourceSupportedCount']}/4:B4={landing_rows[0]['targetRows'][1]['sourceInkRatio']:.4f}"
        f"|allContent={landing_rows[1]['activeSourceSupportedCount']}/4:B4={landing_rows[1]['targetRows'][1]['sourceInkRatio']:.4f}"
        f"|lowerContent={landing_rows[2]['activeSourceSupportedCount']}/4:B4={landing_rows[2]['targetRows'][1]['sourceInkRatio']:.4f}"
        f"|candidate={int(content_box_candidate)}|hiddenCandidate={int(hidden_candidate)}"
        f"|sourceR3={trigger_summary['sourceBackedR3BridgeHitCount']}"
        f"|triggers={trigger_summary['satisfiedReopenTriggerCount']}/{trigger_summary['triggerCount']}"
        "|selectors=0"
    )

    summary = {
        "decision": "current_scan_content_box_registration_no_selector",
        "pageCount": len(PAGES),
        "pagesChecked": PAGES,
        "validPair": "75->76",
        "sameCanvasValidPair": same_canvas_valid_pair,
        "validPairAllContentShift": [valid_all["dx"], valid_all["dy"]],
        "validPairLowerHalfShift": [valid_lower["dx"], valid_lower["dy"]],
        "allContentStability": all_stability,
        "lowerHalfContentStability": lower_stability,
        "allContentShiftStable": all_content_shift_stable,
        "lowerHalfContentShiftStable": lower_half_shift_stable,
        "lowerHalfBoxesClippedToCanvasOrBand": lower_boxes_clipped,
        "contentBoxRegistrationCandidate": content_box_candidate,
        "hiddenContentBoxCandidate": hidden_candidate,
        "landingModeCount": len(landing_rows),
        "bestLandingModeId": best_landing["modeId"],
        "bestLandingSupportedCount": best_landing["activeSourceSupportedCount"],
        "b4BestSourceInkRatio": b4_best,
        "priorHeldToLightFingerprint": load_json(HELD_TO_LIGHT)
        .get("summary", {})
        .get("heldToLightSimulatorFingerprint"),
        "priorSourceInkLandingFingerprint": load_json(SOURCE_INK_LANDING)
        .get("summary", {})
        .get("sourceInkLandingFingerprint"),
        "priorJitterSourceInkFingerprint": load_json(JITTER_SOURCE_INK)
        .get("summary", {})
        .get("jitterSourceInkRescueFingerprint"),
        "priorPageFrameTrimFingerprint": load_json(PAGE_FRAME_TRIM)
        .get("summary", {})
        .get("pageFrameTrimFingerprint"),
        "sourceBackedR3BridgeHitCount": trigger_summary["sourceBackedR3BridgeHitCount"],
        "satisfiedReopenTriggerCount": trigger_summary["satisfiedReopenTriggerCount"],
        "triggerCount": trigger_summary["triggerCount"],
        "contentBoxRegistrationFingerprint": fingerprint,
    }

    result = {
        "createdAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": "current scan content-box registration audit for held-to-light geometry; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT),
            "sourceInkLandingGate": rel(SOURCE_INK_LANDING),
            "jitterSourceInkGate": rel(JITTER_SOURCE_INK),
            "pageFrameTrimGate": rel(PAGE_FRAME_TRIM),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePageTemplate": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))).replace("75", "{page}"),
            "uprightPageTemplate": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=75))).replace("75", "{page}"),
        },
        "contentBoxRows": content_box_rows,
        "pairRows": pair_rows,
        "landingRows": landing_rows,
        "summary": summary,
        "decision": {
            "currentScanContentBoxRegistrationGate": summary["decision"],
            "selectorUnlocked": False,
            "reason": (
                "The all-page content envelope is content-dependent, while the lower-half envelope's "
                "repeatable x shift is clipped to canvas/band edges and does not rescue all four active "
                "targets. B4 remains zero source ink under content-box shifts."
            ),
            "nextMove": (
                "Do not reopen held-to-light with content-box normalization unless a distinct physical or "
                "original-layout source supplies an explicit registration cue."
            ),
        },
        "sheet": rel(SHEET_OUT),
        "fingerprint": fingerprint,
    }

    draw_sheet(images, page_rows_by_page, pair_rows, landing_rows, summary)
    JSON_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(MD_OUT)}")
    print(f"Wrote {rel(JSON_OUT)}")
    print(f"Wrote {rel(SHEET_OUT)}")
    print(f"Decision: {summary['decision']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
