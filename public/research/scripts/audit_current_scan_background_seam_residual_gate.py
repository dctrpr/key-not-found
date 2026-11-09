#!/usr/bin/env python3
"""Audit current-scan background seam/gutter residuals on page 76.

This bounded pass ignores foreground text/highlight ink and looks only for broad
background luminance transitions that could be scan seams, crop/gutter lines, or
lighting folds. It then checks whether those structural background lines align
with O4/B4/G5/O5 boxes or the projected OVERDOSE frame/slots.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_background_seam_residual_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_background_seam_residual_gate.json"
OUT_MD = OUT / "current_scan_background_seam_residual_gate.md"
OUT_SHEET = OUT / "current_scan_background_seam_residual_gate_sheet.jpg"

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
PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAGES = [75, 76, 78, 79]
ACTIVE_IDS = {"O4", "B4", "G5", "O5"}
THRESHOLDS = [4, 8, 16, 32]
UNIQUE_LINE_TOLERANCE = 16
PEAK_MIN_GAP = 18
MAX_PEAKS = 24
STRUCTURAL_Z = 3.5
MIN_BACKGROUND_COVERAGE = 0.35
MIN_BACKGROUND_SUPPORT = 0.012
EDGE_EXCLUSION = 64


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def robust_z(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return np.array([], dtype=np.float32)
    med = float(np.median(values))
    mad = float(np.median(np.abs(values - med)))
    scale = 1.4826 * mad if mad > 1e-9 else float(np.std(values))
    if scale <= 1e-9:
        return np.zeros_like(values, dtype=np.float32)
    return ((values - med) / scale).astype(np.float32)


def smooth(values: np.ndarray, width: int = 7) -> np.ndarray:
    if width <= 1:
        return values
    kernel = np.ones(width, dtype=np.float32) / float(width)
    return np.convolve(values, kernel, mode="same")


def luma_and_background(image: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    luma = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    saturation = arr.max(axis=2) - arr.min(axis=2)
    # Keep paper/background and broad lighting only. Drop black text, orange
    # highlight ink, and saturated colored regions before seam profiling.
    background = (luma >= 178.0) & (saturation <= 42.0)
    return luma.astype(np.float32), background


def nonmax_peaks(rows: list[dict[str, Any]], min_gap: int, limit: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: (item["structural"], item["zScore"], item["support"]), reverse=True):
        coord = int(row["coord"])
        if any(abs(coord - int(other["coord"])) < min_gap for other in selected):
            continue
        selected.append(row)
        if len(selected) >= limit:
            break
    return sorted(selected, key=lambda item: item["coord"])


def profile_axis(luma: np.ndarray, background: np.ndarray, axis: str) -> dict[str, Any]:
    if axis == "vertical":
        grad = np.abs(luma[:, 1:] - luma[:, :-1])
        bg_pair = background[:, 1:] & background[:, :-1]
        length = grad.shape[1]
        size_other = grad.shape[0]
    else:
        grad = np.abs(luma[1:, :] - luma[:-1, :])
        bg_pair = background[1:, :] & background[:-1, :]
        length = grad.shape[0]
        size_other = grad.shape[1]

    covered = bg_pair.sum(axis=0 if axis == "vertical" else 1).astype(np.float32)
    coverage = covered / float(size_other)
    masked_sum = (grad * bg_pair).sum(axis=0 if axis == "vertical" else 1)
    mean_bg_gradient = np.divide(
        masked_sum,
        np.maximum(covered, 1.0),
        out=np.zeros_like(masked_sum, dtype=np.float32),
        where=covered > 0,
    ).astype(np.float32)
    valid_values = grad[bg_pair]
    if valid_values.size:
        gradient_threshold = max(4.0, float(np.percentile(valid_values, 98.5)))
    else:
        gradient_threshold = 4.0
    support = (((grad >= gradient_threshold) & bg_pair).sum(axis=0 if axis == "vertical" else 1) / float(size_other)).astype(
        np.float32
    )

    interior = np.zeros(length, dtype=bool)
    interior[EDGE_EXCLUSION : max(EDGE_EXCLUSION, length - EDGE_EXCLUSION)] = True
    usable = interior & (coverage >= MIN_BACKGROUND_COVERAGE)
    z_full = np.zeros(length, dtype=np.float32)
    if np.any(usable):
        z_full[usable] = robust_z(smooth(mean_bg_gradient[usable], 7))

    peak_rows: list[dict[str, Any]] = []
    for coord in range(length):
        structural = bool(
            usable[coord]
            and z_full[coord] >= STRUCTURAL_Z
            and support[coord] >= MIN_BACKGROUND_SUPPORT
        )
        if structural or z_full[coord] >= 2.0:
            peak_rows.append(
                {
                    "axis": axis,
                    "coord": coord,
                    "meanBackgroundGradient": round(float(mean_bg_gradient[coord]), 6),
                    "coverage": round(float(coverage[coord]), 6),
                    "support": round(float(support[coord]), 6),
                    "zScore": round(float(z_full[coord]), 6),
                    "structural": structural,
                }
            )

    peaks = nonmax_peaks(peak_rows, PEAK_MIN_GAP, MAX_PEAKS)
    structural = [row for row in peaks if row["structural"]]
    return {
        "axis": axis,
        "length": length,
        "gradientThreshold": round(float(gradient_threshold), 6),
        "peakRows": peaks,
        "structuralRows": structural,
        "structuralCoords": [int(row["coord"]) for row in structural],
        "peakCount": len(peaks),
        "structuralCount": len(structural),
        "maxZScore": round(float(max([row["zScore"] for row in peaks], default=0.0)), 6),
        "maxSupport": round(float(max([row["support"] for row in peaks], default=0.0)), 6),
    }


def page_seams(page: int) -> dict[str, Any]:
    path = Path(str(PAGE_TEMPLATE).format(page=page))
    image = Image.open(path).convert("RGB")
    luma, background = luma_and_background(image)
    vertical = profile_axis(luma, background, "vertical")
    horizontal = profile_axis(luma, background, "horizontal")
    return {
        "page": page,
        "image": rel(path),
        "size": list(image.size),
        "backgroundShare": round(float(background.mean()), 6),
        "vertical": vertical,
        "horizontal": horizontal,
    }


def unique_coords(page_rows: list[dict[str, Any]], page: int, axis: str) -> list[int]:
    current = next(row for row in page_rows if row["page"] == page)[axis]["structuralCoords"]
    others: list[int] = []
    for row in page_rows:
        if row["page"] != page:
            others.extend(row[axis]["structuralCoords"])
    unique: list[int] = []
    for coord in current:
        if not any(abs(coord - other) <= UNIQUE_LINE_TOLERANCE for other in others):
            unique.append(int(coord))
    return unique


def active_rows(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    order = ["O4", "B4", "G5", "O5"]
    rows = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") not in ACTIVE_IDS:
            continue
        rows.append(
            {
                "shortId": row["shortId"],
                "phrase": row["phrase"],
                "kind": "active",
                "visualState": row["visualState"],
                "box": [float(value) for value in row["box"]],
            }
        )
    return sorted(rows, key=lambda item: order.index(item["shortId"]))


def highlight_controls(benchmark: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in benchmark.get("targets", []):
        target_id = str(row.get("id"))
        if target_id in ACTIVE_IDS:
            continue
        rows.append(
            {
                "shortId": f"hl_{target_id}",
                "phrase": str(row.get("label", "")),
                "kind": "highlight_control",
                "visualState": str(row.get("kind", "")),
                "box": [float(value) for value in row.get("box", [])],
            }
        )
    return rows


def overdose_slot_rows(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(value) for value in c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])]
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "shortId": f"slot{slot['index']}_{slot['letter']}",
                "phrase": f"OVERDOSE slot {slot['letter']}",
                "kind": "overdose_slot",
                "visualState": "N",
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return rows


def nearest(coord: float, candidates: list[int]) -> dict[str, Any]:
    if not candidates:
        return {"coord": None, "absPx": None, "signedPx": None}
    distances = [abs(coord - value) for value in candidates]
    index = int(np.argmin(distances))
    chosen = float(candidates[index])
    return {
        "coord": int(chosen),
        "absPx": round(float(distances[index]), 6),
        "signedPx": round(float(coord - chosen), 6),
    }


def inspect_box(row: dict[str, Any], vertical_lines: list[int], horizontal_lines: list[int]) -> dict[str, Any]:
    x0, y0, x1, y1 = [float(value) for value in row["box"]]
    x_anchors = {"left": x0, "center": (x0 + x1) / 2.0, "right": x1}
    y_anchors = {"top": y0, "center": (y0 + y1) / 2.0, "bottom": y1}
    x_rows = {name: nearest(value, vertical_lines) for name, value in x_anchors.items()}
    y_rows = {name: nearest(value, horizontal_lines) for name, value in y_anchors.items()}

    def close_any(anchor_rows: dict[str, Any], threshold: int) -> bool:
        return any(
            item["absPx"] is not None and float(item["absPx"]) <= threshold
            for item in anchor_rows.values()
        )

    return {
        "shortId": row["shortId"],
        "phrase": row["phrase"],
        "kind": row["kind"],
        "visualState": row["visualState"],
        "box": [round(value, 3) for value in [x0, y0, x1, y1]],
        "xAnchors": x_rows,
        "yAnchors": y_rows,
        "closeX": {str(threshold): close_any(x_rows, threshold) for threshold in THRESHOLDS},
        "closeY": {str(threshold): close_any(y_rows, threshold) for threshold in THRESHOLDS},
    }


def shared_line_count(rows: list[dict[str, Any]], axis_key: str, threshold: int) -> int:
    line_hits: dict[int, set[str]] = {}
    for row in rows:
        anchors = row["xAnchors"] if axis_key == "x" else row["yAnchors"]
        for anchor in anchors.values():
            if anchor["coord"] is None or anchor["absPx"] is None:
                continue
            if float(anchor["absPx"]) <= threshold:
                line_hits.setdefault(int(anchor["coord"]), set()).add(row["shortId"])
    return max((len(values) for values in line_hits.values()), default=0)


def make_sheet(
    page76: dict[str, Any],
    unique_vertical: list[int],
    unique_horizontal: list[int],
    rows: list[dict[str, Any]],
) -> None:
    image = Image.open(ROOT / page76["image"]).convert("RGB")
    scale = 0.32
    canvas = image.resize((int(image.width * scale), int(image.height * scale)))
    draw = ImageDraw.Draw(canvas)
    font = safe_font(18)
    small = safe_font(14)

    for x in unique_vertical:
        sx = int(round(x * scale))
        draw.line([(sx, 0), (sx, canvas.height)], fill=(0, 180, 255), width=2)
        draw.text((sx + 3, 8), f"x{x}", fill=(0, 90, 150), font=small)
    for y in unique_horizontal:
        sy = int(round(y * scale))
        draw.line([(0, sy), (canvas.width, sy)], fill=(255, 0, 160), width=2)
        draw.text((8, sy + 3), f"y{y}", fill=(150, 0, 90), font=small)

    colors = {
        "active": (255, 210, 0),
        "highlight_control": (95, 170, 255),
        "overdose_slot": (160, 255, 160),
    }
    for row in rows:
        x0, y0, x1, y1 = row["box"]
        color = colors.get(row["kind"], (255, 255, 255))
        box = [int(round(value * scale)) for value in [x0, y0, x1, y1]]
        width = 4 if row["kind"] == "active" else 2
        draw.rectangle(box, outline=color, width=width)
        if row["kind"] == "active":
            draw.text((box[0], max(0, box[1] - 20)), row["shortId"], fill=color, font=font)

    footer_h = 92
    out = Image.new("RGB", (canvas.width, canvas.height + footer_h), (245, 245, 242))
    out.paste(canvas, (0, 0))
    footer = ImageDraw.Draw(out)
    footer.text(
        (16, canvas.height + 12),
        "Background-only seam/gutter residual gate. Cyan=page-76-unique vertical seams, magenta=unique horizontal seams.",
        fill=(30, 30, 30),
        font=font,
    )
    footer.text(
        (16, canvas.height + 46),
        "Yellow boxes are O4/B4/G5/O5. Controls and OVERDOSE slots are included only for alignment comparison.",
        fill=(70, 70, 70),
        font=small,
    )
    out.save(OUT_SHEET, quality=92)


def summarize(
    page_rows: list[dict[str, Any]],
    unique_vertical: list[int],
    unique_horizontal: list[int],
    inspected_rows: list[dict[str, Any]],
    triggers: dict[str, Any],
) -> dict[str, Any]:
    active = [row for row in inspected_rows if row["kind"] == "active"]
    controls = [row for row in inspected_rows if row["kind"] == "highlight_control"]
    slots = [row for row in inspected_rows if row["kind"] == "overdose_slot"]

    def count_close(rows: list[dict[str, Any]], axis: str, threshold: int) -> int:
        key = "closeX" if axis == "x" else "closeY"
        return sum(1 for row in rows if row[key][str(threshold)])

    all_four_x16 = count_close(active, "x", 16) == 4 and bool(unique_vertical)
    all_four_y16 = count_close(active, "y", 16) == 4 and bool(unique_horizontal)
    all_four_x32 = count_close(active, "x", 32) == 4 and bool(unique_vertical)
    all_four_y32 = count_close(active, "y", 32) == 4 and bool(unique_horizontal)
    shared_x16 = shared_line_count(active, "x", 16)
    shared_y16 = shared_line_count(active, "y", 16)

    source_r3 = int(triggers.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(triggers.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(triggers.get("summary", {}).get("triggerCount") or 0)
    seam_candidate = bool(
        source_r3 > 0
        and (
            all_four_x16
            or all_four_y16
            or shared_x16 == 4
            or shared_y16 == 4
        )
    )
    hidden_candidate = bool(
        (
            all_four_x16
            or all_four_y16
            or shared_x16 == 4
            or shared_y16 == 4
        )
        and source_r3 > 0
        and satisfied > 0
    )

    page76 = next(row for row in page_rows if row["page"] == 76)
    fingerprint = (
        f"pages={len(page_rows)}|p76V={page76['vertical']['structuralCount']}|"
        f"p76H={page76['horizontal']['structuralCount']}|uniqV={len(unique_vertical)}|"
        f"uniqH={len(unique_horizontal)}|activeX16={count_close(active, 'x', 16)}|"
        f"activeY16={count_close(active, 'y', 16)}|allX16={int(all_four_x16)}|"
        f"allY16={int(all_four_y16)}|sharedX16={shared_x16}|sharedY16={shared_y16}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors={int(seam_candidate)}"
    )
    return {
        "pageCount": len(page_rows),
        "activeBoxCount": len(active),
        "highlightControlBoxCount": len(controls),
        "overdoseSlotBoxCount": len(slots),
        "page76StructuralVerticalCount": page76["vertical"]["structuralCount"],
        "page76StructuralHorizontalCount": page76["horizontal"]["structuralCount"],
        "page76UniqueVerticalCount": len(unique_vertical),
        "page76UniqueHorizontalCount": len(unique_horizontal),
        "page76UniqueVerticalCoords": unique_vertical,
        "page76UniqueHorizontalCoords": unique_horizontal,
        "activeCloseX16Count": count_close(active, "x", 16),
        "activeCloseY16Count": count_close(active, "y", 16),
        "activeCloseX32Count": count_close(active, "x", 32),
        "activeCloseY32Count": count_close(active, "y", 32),
        "controlCloseX16Count": count_close(controls, "x", 16),
        "controlCloseY16Count": count_close(controls, "y", 16),
        "overdoseSlotCloseX16Count": count_close(slots, "x", 16),
        "overdoseSlotCloseY16Count": count_close(slots, "y", 16),
        "allFourActiveCloseX16": all_four_x16,
        "allFourActiveCloseY16": all_four_y16,
        "allFourActiveCloseX32": all_four_x32,
        "allFourActiveCloseY32": all_four_y32,
        "sharedActiveVerticalLineHitCount16": shared_x16,
        "sharedActiveHorizontalLineHitCount16": shared_y16,
        "seamResidualCandidate": seam_candidate,
        "hiddenBackgroundSeamCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "backgroundSeamResidualFingerprint": fingerprint,
    }


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    page76 = next(row for row in result["pageRows"] if row["page"] == 76)
    lines = [
        "# Current Scan Background Seam Residual Gate",
        "",
        "Scope: background-only seam/gutter scan of current page rasters. Foreground text/highlight ink is masked out before looking for broad luminance transitions. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Pages checked: `{summary['pageCount']}`",
        f"- Page-76 structural vertical/horizontal seam lines: `{summary['page76StructuralVerticalCount']}` / `{summary['page76StructuralHorizontalCount']}`",
        f"- Page-76 unique structural vertical/horizontal lines: `{summary['page76UniqueVerticalCount']}` / `{summary['page76UniqueHorizontalCount']}`",
        f"- Active boxes close to unique structural x/y lines at <=16px: `{summary['activeCloseX16Count']}` / `{summary['activeCloseY16Count']}`",
        f"- All-four active close to unique structural x/y lines at <=16px: `{int(summary['allFourActiveCloseX16'])}` / `{int(summary['allFourActiveCloseY16'])}`",
        f"- Shared active vertical/horizontal line hits at <=16px: `{summary['sharedActiveVerticalLineHitCount16']}` / `{summary['sharedActiveHorizontalLineHitCount16']}`",
        f"- Controls close to unique structural x/y lines at <=16px: `{summary['controlCloseX16Count']}` / `{summary['controlCloseY16Count']}`",
        f"- OVERDOSE slots close to unique structural x/y lines at <=16px: `{summary['overdoseSlotCloseX16Count']}` / `{summary['overdoseSlotCloseY16Count']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['backgroundSeamResidualFingerprint']}`",
        "",
        "## Page-76 Background Profile",
        "",
        f"- Background share: `{page76['backgroundShare']}`",
        f"- Vertical profile threshold / max z / max support: `{page76['vertical']['gradientThreshold']}` / `{page76['vertical']['maxZScore']}` / `{page76['vertical']['maxSupport']}`",
        f"- Horizontal profile threshold / max z / max support: `{page76['horizontal']['gradientThreshold']}` / `{page76['horizontal']['maxZScore']}` / `{page76['horizontal']['maxSupport']}`",
        f"- Unique vertical coords: `{','.join(map(str, summary['page76UniqueVerticalCoords'])) or 'none'}`",
        f"- Unique horizontal coords: `{','.join(map(str, summary['page76UniqueHorizontalCoords'])) or 'none'}`",
        "",
        "## Active Rows",
        "",
        "| id | phrase | close x16 | close y16 | nearest x anchors | nearest y anchors |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in [item for item in result["inspectedRows"] if item["kind"] == "active"]:
        x_desc = "; ".join(
            f"{name}:{anchor['coord']}:{anchor['absPx']}"
            for name, anchor in row["xAnchors"].items()
        )
        y_desc = "; ".join(
            f"{name}:{anchor['coord']}:{anchor['absPx']}"
            for name, anchor in row["yAnchors"].items()
        )
        lines.append(
            f"| `{row['shortId']}` | `{row['phrase']}` | `{int(row['closeX']['16'])}` | `{int(row['closeY']['16'])}` | `{x_desc}` | `{y_desc}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`.",
            f"- Reason: {result['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    benchmark = load_json(PAGE76_HIGHLIGHT_BENCHMARK)
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    triggers = load_json(REOPEN_TRIGGER_MATRIX)

    page_rows = [page_seams(page) for page in PAGES]
    unique_vertical = unique_coords(page_rows, 76, "vertical")
    unique_horizontal = unique_coords(page_rows, 76, "horizontal")

    boxes = active_rows(active_index) + highlight_controls(benchmark) + overdose_slot_rows(c9)
    inspected = [inspect_box(row, unique_vertical, unique_horizontal) for row in boxes]
    summary = summarize(page_rows, unique_vertical, unique_horizontal, inspected, triggers)

    decision = "background_seam_residual_not_a_selector"
    reason = (
        "Background-only structural seam lines do not produce an all-four active alignment, "
        "do not supply a shared vertical/horizontal line carrier, and still have no source-backed R3 trigger."
    )
    next_move = (
        "Keep page-76 background seam/gutter residuals closed. Reopen only if a new physical/original-layout "
        "source changes page-background seams or raw clue wording explicitly names a seam, gutter, trim, fold, or crop-line read."
    )
    if summary["hiddenBackgroundSeamCandidate"]:
        decision = "background_seam_residual_requires_source_review"
        reason = "A source-backed all-active seam condition appeared; review the source packet before any extraction."
        next_move = "Inspect the source-backed seam evidence manually against the future-source intake gate."

    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "current-scan page background seam/gutter residual audit; no extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "page76HighlightBenchmark": rel(PAGE76_HIGHLIGHT_BENCHMARK),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "pages": [rel(Path(str(PAGE_TEMPLATE).format(page=page))) for page in PAGES],
        },
        "pageRows": page_rows,
        "inspectedRows": inspected,
        "summary": summary,
        "decision": decision,
        "reason": reason,
        "nextMove": next_move,
        "sheet": rel(OUT_SHEET),
    }
    make_sheet(next(row for row in page_rows if row["page"] == 76), unique_vertical, unique_horizontal, inspected)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(summary["backgroundSeamResidualFingerprint"])


if __name__ == "__main__":
    main()
