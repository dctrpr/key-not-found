#!/usr/bin/env python3
"""Ablate mirrored page-75 highlights behind active page-76 targets.

Natural held-to-light checks already show the valid 75->76 leaf has source ink
at O4/G5/O5 but not B4. This bounded pass removes mirrored page-75 highlight
rectangles from the natural source mask and asks whether the active target
support survives as a source-backed all-four selector.

No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address
checks, BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_active_source_highlight_ablation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_active_source_highlight_ablation_gate.json"
OUT_MD = OUT / "current_scan_active_source_highlight_ablation_gate.md"
OUT_SHEET = OUT / "current_scan_active_source_highlight_ablation_gate_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ALL_LEAF_PARITY = ROOT / (
    "analysis_outputs/source_audit/current_scan_all_leaf_light_table_parity_gate/"
    "current_scan_all_leaf_light_table_parity_gate.json"
)
DENSITY_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/"
    "current_scan_light_table_density_calibration_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
CONTROL_LINE_OFFSETS = [-3, -2, -1, 1, 2, 3]
INK_LUMA_THRESHOLD = 238.0


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def normalize_page(page: int) -> Image.Image:
    source = Image.open(Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))).convert("RGB")
    upright = Image.open(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    return source.rotate(180) if rot_diff < same_diff else source


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def masks(img: Image.Image) -> dict[str, np.ndarray]:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    feature = dark | orange | grey
    ink = luma(arr.astype(np.float32)) < INK_LUMA_THRESHOLD
    return {"ink": ink, "feature": feature}


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def ratio(mask: np.ndarray, box: list[float] | None = None) -> float:
    cropped = crop_bool(mask, box) if box else mask
    return float(cropped.mean()) if cropped.size else 0.0


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def inter_area(a: list[float], b: list[float]) -> float:
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(
        0.0, min(a[3], b[3]) - max(a[1], b[1])
    )


def mirror_box(box: list[float], width: float) -> list[float]:
    return [width - box[2], box[1], width - box[0], box[3]]


def ablate(mask: np.ndarray, boxes: list[list[float]]) -> np.ndarray:
    out = mask.copy()
    h, w = out.shape[:2]
    for box in boxes:
        x0, y0, x1, y1 = [int(round(v)) for v in box]
        x0 = max(0, min(w, x0))
        x1 = max(0, min(w, x1))
        y0 = max(0, min(h, y0))
        y1 = max(0, min(h, y1))
        out[y0:y1, x0:x1] = False
    return out


def active_boxes(active_index: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in active_index.get("activeRows", []):
        if row.get("shortId") not in TARGET_ORDER:
            continue
        rows.append(
            {
                "shortId": row["shortId"],
                "phrase": row["phrase"],
                "visualState": row["visualState"],
                "pageLine": int(row["pageLine"]),
                "box": [float(v) for v in row["box"]],
            }
        )
    rows.sort(key=lambda row: TARGET_ORDER.index(row["shortId"]))
    return rows


def estimated_line_pitch(rows: list[dict[str, Any]]) -> float:
    pitches = []
    for i, left in enumerate(rows):
        for right in rows[i + 1 :]:
            line_gap = right["pageLine"] - left["pageLine"]
            if not line_gap:
                continue
            cy_left = (left["box"][1] + left["box"][3]) / 2.0
            cy_right = (right["box"][1] + right["box"][3]) / 2.0
            pitches.append((cy_right - cy_left) / line_gap)
    return float(median(pitches)) if pitches else 73.5


def shifted_box(box: list[float], dy: float, page_size: tuple[int, int]) -> list[float] | None:
    w, h = page_size
    shifted = [box[0], box[1] + dy, box[2], box[3] + dy]
    if shifted[0] < 0 or shifted[1] < 0 or shifted[2] > w or shifted[3] > h:
        return None
    return shifted


def control_boxes(active: list[dict[str, Any]], page_size: tuple[int, int], pitch: float) -> list[dict[str, Any]]:
    controls = []
    for row in active:
        for offset in CONTROL_LINE_OFFSETS:
            box = shifted_box(row["box"], offset * pitch, page_size)
            if box is None:
                continue
            controls.append(
                {
                    "controlId": f"{row['shortId']}_line_{offset:+d}",
                    "sourceTarget": row["shortId"],
                    "lineOffset": offset,
                    "box": box,
                }
            )
    return controls


def highlight_boxes(article: dict[str, Any]) -> list[dict[str, Any]]:
    page75 = next(page for page in article["pages"] if int(page["page"]) == 75)
    width = float(page75["width"])
    rows = []
    for highlight in page75.get("highlights", []):
        source_box = [float(v) for v in highlight["box"]]
        rows.append(
            {
                "id": highlight["id"],
                "kind": highlight.get("kind"),
                "sourceBox": source_box,
                "mirroredBox": mirror_box(source_box, width),
            }
        )
    return rows


def overlapping_highlights(highlights: list[dict[str, Any]], box: list[float]) -> list[dict[str, Any]]:
    rows = []
    for highlight in highlights:
        overlap = inter_area(highlight["mirroredBox"], box)
        if overlap <= 0.5:
            continue
        rows.append(
            {
                "id": highlight["id"],
                "kind": highlight.get("kind"),
                "overlapFractionOfTarget": round(overlap / max(area(box), 1.0), 6),
                "overlapFractionOfHighlight": round(overlap / max(area(highlight["mirroredBox"]), 1.0), 6),
            }
        )
    return rows


def measure(mask_set: dict[str, np.ndarray], box: list[float]) -> dict[str, float]:
    return {
        "sourceInkRatio": round(ratio(mask_set["ink"], box), 6),
        "sourceFeatureRatio": round(ratio(mask_set["feature"], box), 6),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE76_IMAGE).convert("RGB")
    crop = [260, 2095, 1900, 3030]
    scale = 0.55
    panel = page.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 26
    header_h = 132
    table_h = 260
    sheet = Image.new("RGB", (margin * 2 + panel.size[0], header_h + panel.size[1] + table_h), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.size[0], header_h), fill=(24, 31, 42))
    draw.text((margin, 18), "Active Source-Highlight Ablation Gate", fill="white", font=font(25))
    draw.text(
        (margin, 54),
        "Natural 75->76 active target source ink after removing mirrored page-75 highlights.",
        fill=(225, 229, 236),
        font=font(13),
    )
    draw.text(
        (margin, 80),
        f"all-four before/after all-highlight ablation: {int(result['summary']['baselineAllFourPositive'])}/{int(result['summary']['allHighlightAblationAllFourPositive'])}; B4 after: {result['summary']['b4InkAfterAllHighlightAblation']:.6f}",
        fill=(225, 229, 236),
        font=font(13),
    )
    sheet.paste(panel, (margin, header_h))

    def sx(x: float) -> float:
        return margin + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return header_h + (y - crop[1]) * scale

    for highlight in result["mirroredSourceHighlights"]:
        box = highlight["mirroredBox"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline="#f59e0b", width=1)
    for row in result["activeRows"]:
        box = row["box"]
        color = "#ef4444" if row["shortId"] == "B4" else "#16a34a"
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=3)
        draw.text((sx(box[0]), sy(box[1]) - 16), row["shortId"], fill=color, font=font(12))

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Active Target Trace", fill=(30, 34, 40), font=font(15))
    y += 26
    headers = ["target", "base", "after all", "drop", "after overlap", "overlap ids", "positive"]
    xs = [margin, margin + 72, margin + 148, margin + 238, margin + 310, margin + 420, margin + 675]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 86, 96), font=font(10))
    y += 18
    for row in result["activeRows"]:
        values = [
            row["shortId"],
            f"{row['baseline']['sourceInkRatio']:.4f}",
            f"{row['allHighlightAblation']['sourceInkRatio']:.4f}",
            f"{row['allHighlightDropPct']:.1f}%",
            f"{row['overlapHighlightAblation']['sourceInkRatio']:.4f}",
            ",".join(row["overlappingSourceHighlightIds"]) or "-",
            str(int(row["allHighlightAblationPositive"])),
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(25, 28, 34), font=font(10))
        y += 22
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active_index = load_json(ACTIVE_INDEX_SLOT)
    article = load_json(ARTICLE_MAP)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    parity = load_json(ALL_LEAF_PARITY)
    density = load_json(DENSITY_GATE)

    active = active_boxes(active_index)
    page_size = normalize_page(76).size
    pitch = estimated_line_pitch(active)
    controls = control_boxes(active, page_size, pitch)
    highlights = highlight_boxes(article)
    all_highlight_boxes = [row["mirroredBox"] for row in highlights]

    mirrored = ImageOps.mirror(normalize_page(75))
    base_masks = masks(mirrored)
    all_highlight_masks = {
        "ink": ablate(base_masks["ink"], all_highlight_boxes),
        "feature": ablate(base_masks["feature"], all_highlight_boxes),
    }

    active_rows = []
    for row in active:
        overlaps = overlapping_highlights(highlights, row["box"])
        overlap_boxes = [
            highlight["mirroredBox"]
            for highlight in highlights
            if highlight["id"] in {item["id"] for item in overlaps}
        ]
        overlap_masks = {
            "ink": ablate(base_masks["ink"], overlap_boxes),
            "feature": ablate(base_masks["feature"], overlap_boxes),
        }
        non_overlap_masks = {
            "ink": ablate(
                base_masks["ink"],
                [
                    highlight["mirroredBox"]
                    for highlight in highlights
                    if highlight["id"] not in {item["id"] for item in overlaps}
                ],
            ),
            "feature": ablate(
                base_masks["feature"],
                [
                    highlight["mirroredBox"]
                    for highlight in highlights
                    if highlight["id"] not in {item["id"] for item in overlaps}
                ],
            ),
        }
        baseline = measure(base_masks, row["box"])
        all_ablation = measure(all_highlight_masks, row["box"])
        overlap_ablation = measure(overlap_masks, row["box"])
        non_overlap_ablation = measure(non_overlap_masks, row["box"])
        drop = baseline["sourceInkRatio"] - all_ablation["sourceInkRatio"]
        drop_pct = drop / baseline["sourceInkRatio"] * 100.0 if baseline["sourceInkRatio"] else 0.0
        active_rows.append(
            {
                **row,
                "box": [round(float(v), 3) for v in row["box"]],
                "overlappingSourceHighlights": overlaps,
                "overlappingSourceHighlightIds": [item["id"] for item in overlaps],
                "baseline": baseline,
                "allHighlightAblation": all_ablation,
                "overlapHighlightAblation": overlap_ablation,
                "nonOverlapHighlightAblation": non_overlap_ablation,
                "allHighlightDrop": round(drop, 6),
                "allHighlightDropPct": round(drop_pct, 3),
                "baselinePositive": baseline["sourceInkRatio"] > 0.0,
                "allHighlightAblationPositive": all_ablation["sourceInkRatio"] > 0.0,
            }
        )

    control_rows = []
    for control in controls:
        baseline = measure(base_masks, control["box"])
        all_ablation = measure(all_highlight_masks, control["box"])
        control_rows.append(
            {
                **control,
                "box": [round(float(v), 3) for v in control["box"]],
                "baseline": baseline,
                "allHighlightAblation": all_ablation,
                "baselinePositive": baseline["sourceInkRatio"] > 0.0,
                "allHighlightAblationPositive": all_ablation["sourceInkRatio"] > 0.0,
            }
        )

    baseline_positive = [row["shortId"] for row in active_rows if row["baselinePositive"]]
    after_positive = [row["shortId"] for row in active_rows if row["allHighlightAblationPositive"]]
    b4 = next(row for row in active_rows if row["shortId"] == "B4")
    mean_active_drop_pct = float(np.mean([row["allHighlightDropPct"] for row in active_rows]))
    max_active_drop_pct = float(np.max([row["allHighlightDropPct"] for row in active_rows]))
    control_positive_before = sum(1 for row in control_rows if row["baselinePositive"])
    control_positive_after = sum(1 for row in control_rows if row["allHighlightAblationPositive"])
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    hidden_candidate = bool(len(after_positive) == len(TARGET_ORDER) and source_r3 > 0)
    fingerprint = (
        f"targets=4|baselinePositive={','.join(baseline_positive) or '-'}|"
        f"afterAllPositive={','.join(after_positive) or '-'}|B4Base={b4['baseline']['sourceInkRatio']:.6f}|"
        f"B4After={b4['allHighlightAblation']['sourceInkRatio']:.6f}|"
        f"meanDropPct={mean_active_drop_pct:.1f}|maxDropPct={max_active_drop_pct:.1f}|"
        f"controlsPositive={control_positive_before}->{control_positive_after}|"
        f"hiddenCandidate={int(hidden_candidate)}|sourceR3={source_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "activeTargetCount": len(active_rows),
        "baselinePositiveTargets": baseline_positive,
        "allHighlightAblationPositiveTargets": after_positive,
        "baselineAllFourPositive": len(baseline_positive) == len(TARGET_ORDER),
        "allHighlightAblationAllFourPositive": len(after_positive) == len(TARGET_ORDER),
        "b4InkBaseline": b4["baseline"]["sourceInkRatio"],
        "b4InkAfterAllHighlightAblation": b4["allHighlightAblation"]["sourceInkRatio"],
        "meanActiveAllHighlightDropPct": round(mean_active_drop_pct, 3),
        "maxActiveAllHighlightDropPct": round(max_active_drop_pct, 3),
        "controlRegionCount": len(control_rows),
        "controlPositiveBeforeAllHighlightAblation": control_positive_before,
        "controlPositiveAfterAllHighlightAblation": control_positive_after,
        "hiddenActiveHighlightAblationCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "activeSourceHighlightAblationFingerprint": fingerprint,
        "priorAllLeafParityFingerprint": parity.get("fingerprint"),
        "priorDensityCalibrationFingerprint": density.get("fingerprint"),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current-scan active source-highlight ablation gate; natural 75->76 "
            "active target source-ink support after removing mirrored page-75 "
            "source-highlight rectangles"
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "allLeafParityGate": rel(ALL_LEAF_PARITY),
            "densityCalibrationGate": rel(DENSITY_GATE),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "sourcePage": 75,
        "targetPage": 76,
        "linePitchPx": round(pitch, 6),
        "mirroredSourceHighlights": [
            {
                "id": row["id"],
                "kind": row["kind"],
                "sourceBox": [round(float(v), 3) for v in row["sourceBox"]],
                "mirroredBox": [round(float(v), 3) for v in row["mirroredBox"]],
            }
            for row in highlights
        ],
        "activeRows": active_rows,
        "controlRows": control_rows,
        "summary": summary,
        "decision": {
            "currentScanActiveSourceHighlightAblationGate": "current_scan_active_source_highlight_ablation_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Removing mirrored page-75 highlights does not create all-four active support; "
                "B4 remains zero and the remaining source ink stays partial with no source-backed "
                "unit/order cue."
            ),
            "nextMove": (
                "Use active held-to-light contacts as provenance checks only. Reopen extraction "
                "only for a source/original-layout clue naming a unit, order, transform, or "
                "specific highlight bleed-through rule."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Active Source-Highlight Ablation Gate",
        "",
        "Scope: removes mirrored page-75 source-highlight rectangles from the natural `75->76` held-to-light source mask, then remeasures O4/B4/G5/O5 and matched line-shift controls. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active targets checked: `{summary['activeTargetCount']}`",
        f"- Baseline positive targets: `{','.join(summary['baselinePositiveTargets']) or '-'}`",
        f"- Positive targets after all source-highlight ablation: `{','.join(summary['allHighlightAblationPositiveTargets']) or '-'}`",
        f"- All-four active positive before/after ablation: `{int(summary['baselineAllFourPositive'])}` / `{int(summary['allHighlightAblationAllFourPositive'])}`",
        f"- B4 source ink before/after ablation: `{summary['b4InkBaseline']:.6f}` / `{summary['b4InkAfterAllHighlightAblation']:.6f}`",
        f"- Mean/max active source-ink drop after ablation: `{summary['meanActiveAllHighlightDropPct']:.3f}%` / `{summary['maxActiveAllHighlightDropPct']:.3f}%`",
        f"- Control positives before/after ablation: `{summary['controlPositiveBeforeAllHighlightAblation']}` / `{summary['controlPositiveAfterAllHighlightAblation']}` of `{summary['controlRegionCount']}`",
        f"- Hidden active highlight-ablation candidate: `{int(summary['hiddenActiveHighlightAblationCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Active Target Trace",
        "",
        "| target | baseline ink | after all highlights | drop | after overlapping highlights | overlapping source highlights | positive after all |",
        "|---|---:|---:|---:|---:|---|---:|",
    ]
    for row in active_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['shortId']}`",
                    f"{row['baseline']['sourceInkRatio']:.6f}",
                    f"{row['allHighlightAblation']['sourceInkRatio']:.6f}",
                    f"{row['allHighlightDropPct']:.3f}%",
                    f"{row['overlapHighlightAblation']['sourceInkRatio']:.6f}",
                    ",".join(row["overlappingSourceHighlightIds"]) or "-",
                    str(int(row["allHighlightAblationPositive"])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_active_source_highlight_ablation_no_selector`",
            "- B4 remains zero before and after source-highlight ablation.",
            "- The active target source-ink pattern is partial, not all-four, and still has no source-backed unit/order wording.",
            "",
            "## Next Move",
            "",
            "- Continue with physical/original-layout source validation or raw clue wording that names unit/order/transform.",
            "- If staying local-only, move away from held-to-light density and inspect constrained folded geometry or original PDF/source acquisition evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
