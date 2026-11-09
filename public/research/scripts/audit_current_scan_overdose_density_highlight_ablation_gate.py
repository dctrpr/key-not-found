#!/usr/bin/env python3
"""Ablate mirrored page-75 highlights behind the OVERDOSE density outliers.

The prior provenance pass showed the three normalized page-76 OVERDOSE slot
outliers overlap mirrored page-75 highlights. This bounded pass removes those
mirrored source-highlight rectangles from the natural 75->76 source mask and
asks whether the outlier status survives.

No OCR-to-key extraction, key candidates, hashes-to-key, seed/WIF/address
checks, BIP39 checks, or broad brute force are run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_density_highlight_ablation_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_density_highlight_ablation_gate.json"
OUT_MD = OUT / "current_scan_overdose_density_highlight_ablation_gate.md"
OUT_SHEET = OUT / "current_scan_overdose_density_highlight_ablation_gate_sheet.jpg"

DENSITY_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_light_table_density_calibration_gate/"
    "current_scan_light_table_density_calibration_gate.json"
)
PROVENANCE_GATE = ROOT / (
    "analysis_outputs/source_audit/current_scan_overdose_density_outlier_provenance_gate/"
    "current_scan_overdose_density_outlier_provenance_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
C9_HEADER_GLYPH_SLOT = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"
PAGE76_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
INK_LUMA_THRESHOLD = 238.0
EPSILON = 1e-9


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


def norm(value: float, denom: float) -> float:
    return value / max(denom, EPSILON)


def mirror_box(box: list[float], width: float) -> list[float]:
    return [width - box[2], box[1], width - box[0], box[3]]


def overdose_slots(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [])]
    slots = []
    for slot in c9.get("projections", [{}])[0].get("slots", []):
        slots.append(
            {
                "slotId": f"slot_{slot['index']}_{slot['letter']}",
                "slotIndex": int(slot["index"]),
                "letter": slot["letter"],
                "box": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
            }
        )
    return slots


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


def highlight_boxes(article: dict[str, Any], ids: set[str] | None = None) -> list[dict[str, Any]]:
    page75 = next(page for page in article["pages"] if int(page["page"]) == 75)
    width = float(page75["width"])
    rows = []
    for highlight in page75.get("highlights", []):
        if ids is not None and highlight["id"] not in ids:
            continue
        rows.append(
            {
                "id": highlight["id"],
                "kind": highlight.get("kind"),
                "sourceBox": [float(v) for v in highlight["box"]],
                "mirroredBox": mirror_box([float(v) for v in highlight["box"]], width),
            }
        )
    return rows


def density_row_for_slot(density: dict[str, Any], slot_id: str, target_page: int) -> dict[str, Any]:
    return next(
        row
        for row in density.get("overdoseSlotRows", [])
        if row["slotId"] == slot_id and int(row["targetPage"]) == target_page
    )


def other_leaf_max(density: dict[str, Any], slot_id: str) -> float:
    return max(
        float(row["inkOverPageDensity"])
        for row in density.get("overdoseSlotRows", [])
        if row["slotId"] == slot_id and int(row["targetPage"]) != 76
    )


def draw_sheet(result: dict[str, Any]) -> None:
    page = Image.open(PAGE76_IMAGE).convert("RGB")
    crop = [210, 2090, 2325, 3065]
    scale = 0.48
    panel = page.crop(crop).resize(
        (int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale))
    )
    margin = 26
    header_h = 130
    table_h = 310
    sheet = Image.new("RGB", (margin * 2 + panel.size[0], header_h + panel.size[1] + table_h), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.size[0], header_h), fill=(24, 31, 42))
    draw.text((margin, 18), "OVERDOSE Source-Highlight Ablation Gate", fill="white", font=font(25))
    draw.text(
        (margin, 54),
        "Tests whether ROS/SOR survives after removing mirrored page-75 highlight boxes from the source mask.",
        fill=(225, 229, 236),
        font=font(13),
    )
    draw.text(
        (margin, 80),
        f"Outlier survivors after source-highlight ablation: {result['summary']['outlierSurvivorCountAfterOutlierHighlightAblation']}/{result['summary']['baselineOutlierSlotCount']}",
        fill=(225, 229, 236),
        font=font(13),
    )
    sheet.paste(panel, (margin, header_h))

    def sx(x: float) -> float:
        return margin + (x - crop[0]) * scale

    def sy(y: float) -> float:
        return header_h + (y - crop[1]) * scale

    for row in result["slotRows"]:
        box = row["box"]
        if row["baselineOutlier"]:
            color = "#ef4444" if row["survivesOutlierHighlightAblation"] else "#16a34a"
            width = 4
        else:
            color = "#64748b"
            width = 1
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=width)
        draw.text((sx(box[0]) + 5, sy(box[1]) + 4), row["letter"], fill=color, font=font(15))

    for hrow in result["outlierSourceHighlights"]:
        box = hrow["mirroredBox"]
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline="#f59e0b", width=2)

    y = header_h + panel.size[1] + 24
    draw.text((margin, y), "Ablation Trace", fill=(30, 34, 40), font=font(15))
    y += 26
    headers = ["slot", "out", "base", "after OH", "drop", "survive", "after all", "non-out ctrl"]
    xs = [margin, margin + 64, margin + 108, margin + 196, margin + 306, margin + 388, margin + 482, margin + 592]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 86, 96), font=font(10))
    y += 18
    for row in result["slotRows"]:
        values = [
            f"{row['slotIndex']}:{row['letter']}",
            str(int(row["baselineOutlier"])),
            f"{row['baselineInkOverPageDensity']:.3f}",
            f"{row['inkOverOriginalPageDensityAfterOutlierHighlightAblation']:.3f}",
            f"{row['outlierHighlightAblationDropPct']:.1f}%",
            str(int(row["survivesOutlierHighlightAblation"])),
            f"{row['inkOverOriginalPageDensityAfterAllHighlightAblation']:.3f}",
            f"{row['inkOverOriginalPageDensityAfterNonOutlierHighlightAblation']:.3f}",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(25, 28, 34), font=font(10))
        y += 21
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    density = load_json(DENSITY_GATE)
    provenance = load_json(PROVENANCE_GATE)
    article = load_json(ARTICLE_MAP)
    c9 = load_json(C9_HEADER_GLYPH_SLOT)
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    outlier_ids = set(provenance.get("summary", {}).get("outlierMirroredSourceHighlightIds", []))

    source = normalize_page(75)
    mirrored = ImageOps.mirror(source)
    base_masks = masks(mirrored)
    original_page_ink = ratio(base_masks["ink"])
    original_page_feature = ratio(base_masks["feature"])
    all_highlights = highlight_boxes(article)
    outlier_highlights = highlight_boxes(article, outlier_ids)
    non_outlier_highlights = [row for row in all_highlights if row["id"] not in outlier_ids]

    variants = {
        "baseline": base_masks,
        "outlier_highlights_ablated": {
            "ink": ablate(base_masks["ink"], [row["mirroredBox"] for row in outlier_highlights]),
            "feature": ablate(base_masks["feature"], [row["mirroredBox"] for row in outlier_highlights]),
        },
        "all_highlights_ablated": {
            "ink": ablate(base_masks["ink"], [row["mirroredBox"] for row in all_highlights]),
            "feature": ablate(base_masks["feature"], [row["mirroredBox"] for row in all_highlights]),
        },
        "non_outlier_highlights_ablated": {
            "ink": ablate(base_masks["ink"], [row["mirroredBox"] for row in non_outlier_highlights]),
            "feature": ablate(base_masks["feature"], [row["mirroredBox"] for row in non_outlier_highlights]),
        },
    }

    slot_rows = []
    for slot in overdose_slots(c9):
        baseline_density_row = density_row_for_slot(density, slot["slotId"], 76)
        baseline_norm = float(baseline_density_row["inkOverPageDensity"])
        other_max = other_leaf_max(density, slot["slotId"])
        baseline_outlier = baseline_norm > other_max
        variant_rows = {}
        for name, mask_set in variants.items():
            ink_ratio = ratio(mask_set["ink"], slot["box"])
            feature_ratio = ratio(mask_set["feature"], slot["box"])
            page_ink = ratio(mask_set["ink"])
            page_feature = ratio(mask_set["feature"])
            variant_rows[name] = {
                "sourceInkRatio": round(ink_ratio, 6),
                "sourceFeatureRatio": round(feature_ratio, 6),
                "inkOverOriginalPageDensity": round(norm(ink_ratio, original_page_ink), 6),
                "featureOverOriginalPageDensity": round(norm(feature_ratio, original_page_feature), 6),
                "inkOverVariantPageDensity": round(norm(ink_ratio, page_ink), 6),
                "featureOverVariantPageDensity": round(norm(feature_ratio, page_feature), 6),
                "variantPageInkDensity": round(page_ink, 6),
                "variantPageFeatureDensity": round(page_feature, 6),
            }
        after_outlier = variant_rows["outlier_highlights_ablated"]["inkOverOriginalPageDensity"]
        after_all = variant_rows["all_highlights_ablated"]["inkOverOriginalPageDensity"]
        after_non_outlier = variant_rows["non_outlier_highlights_ablated"]["inkOverOriginalPageDensity"]
        drop = baseline_norm - after_outlier
        drop_pct = (drop / baseline_norm * 100.0) if baseline_norm else 0.0
        slot_rows.append(
            {
                **slot,
                "box": [round(float(v), 3) for v in slot["box"]],
                "otherLeafInkOverPageDensityMax": round(other_max, 6),
                "baselineInkOverPageDensity": round(baseline_norm, 6),
                "baselineOutlier": baseline_outlier,
                "inkOverOriginalPageDensityAfterOutlierHighlightAblation": round(after_outlier, 6),
                "inkOverOriginalPageDensityAfterAllHighlightAblation": round(after_all, 6),
                "inkOverOriginalPageDensityAfterNonOutlierHighlightAblation": round(after_non_outlier, 6),
                "outlierHighlightAblationDrop": round(drop, 6),
                "outlierHighlightAblationDropPct": round(drop_pct, 3),
                "survivesOutlierHighlightAblation": after_outlier > other_max,
                "survivesAllHighlightAblation": after_all > other_max,
                "controlNonOutlierAblationChangesStatus": (after_non_outlier > other_max) != baseline_outlier,
                "variants": variant_rows,
            }
        )

    baseline_outliers = [row for row in slot_rows if row["baselineOutlier"]]
    survivors_outlier_ablation = [
        row for row in baseline_outliers if row["survivesOutlierHighlightAblation"]
    ]
    survivors_all_ablation = [
        row for row in baseline_outliers if row["survivesAllHighlightAblation"]
    ]
    non_outlier_control_flips = [
        row for row in slot_rows if row["controlNonOutlierAblationChangesStatus"]
    ]
    outlier_letters = "".join(row["letter"] for row in baseline_outliers)
    survivor_letters = "".join(row["letter"] for row in survivors_outlier_ablation)
    mean_drop_pct = (
        float(np.mean([row["outlierHighlightAblationDropPct"] for row in baseline_outliers]))
        if baseline_outliers
        else 0.0
    )
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    hidden_candidate = bool(survivors_outlier_ablation and source_r3 > 0)
    fingerprint = (
        f"slots={len(slot_rows)}|baselineOutliers={len(baseline_outliers)}|letters={outlier_letters or '-'}|"
        f"outlierHighlightIds={','.join(sorted(outlier_ids)) or '-'}|"
        f"surviveOutlierAblation={len(survivors_outlier_ablation)}|surviveLetters={survivor_letters or '-'}|"
        f"surviveAllAblation={len(survivors_all_ablation)}|meanDropPct={mean_drop_pct:.1f}|"
        f"nonOutlierControlFlips={len(non_outlier_control_flips)}|hiddenCandidate={int(hidden_candidate)}|"
        f"sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "slotCount": len(slot_rows),
        "baselineOutlierSlotCount": len(baseline_outliers),
        "baselineOutlierSlotIds": [row["slotId"] for row in baseline_outliers],
        "baselineOutlierLetters": outlier_letters,
        "outlierSourceHighlightIds": sorted(outlier_ids),
        "outlierSurvivorCountAfterOutlierHighlightAblation": len(survivors_outlier_ablation),
        "outlierSurvivorLettersAfterOutlierHighlightAblation": survivor_letters,
        "outlierSurvivorCountAfterAllHighlightAblation": len(survivors_all_ablation),
        "meanOutlierHighlightAblationDropPct": round(mean_drop_pct, 3),
        "nonOutlierHighlightControlFlipCount": len(non_outlier_control_flips),
        "hiddenHighlightAblationCandidate": hidden_candidate,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "highlightAblationFingerprint": fingerprint,
        "priorOutlierProvenanceFingerprint": provenance.get("fingerprint"),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "current-scan OVERDOSE source-highlight ablation gate; tests whether "
            "density-calibrated page-76 slot outliers survive removal of mirrored "
            "page-75 source-highlight rectangles"
        ),
        "inputs": {
            "densityCalibrationGate": rel(DENSITY_GATE),
            "outlierProvenanceGate": rel(PROVENANCE_GATE),
            "articleMap": rel(ARTICLE_MAP),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "sourcePage": 75,
        "targetPage": 76,
        "originalPageInkDensity": round(original_page_ink, 6),
        "originalPageFeatureDensity": round(original_page_feature, 6),
        "outlierSourceHighlights": outlier_highlights,
        "slotRows": slot_rows,
        "summary": summary,
        "decision": {
            "currentScanOverdoseDensityHighlightAblationGate": "current_scan_overdose_density_highlight_ablation_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The normalized OVERDOSE slot outliers do not survive source-highlight "
                "ablation as a source-backed selector; their signal is dependent on "
                "mirrored page-75 highlight regions and still has no R3 unit/order cue."
            ),
            "nextMove": (
                "Keep current-scan OVERDOSE density as provenance noise unless a raw clue "
                "specifically names highlighted source bleed-through, slots, density, or a "
                "reading order."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan OVERDOSE Density Highlight Ablation Gate",
        "",
        "Scope: removes mirrored page-75 source-highlight rectangles from the natural 75->76 held-to-light source mask, then checks whether the density-calibrated OVERDOSE slot outliers survive. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Slot columns checked: `{summary['slotCount']}`",
        f"- Baseline outlier slots / letters: `{', '.join(summary['baselineOutlierSlotIds'])}` / `{summary['baselineOutlierLetters'] or '-'}`",
        f"- Ablated mirrored source highlight ids: `{', '.join(summary['outlierSourceHighlightIds']) or '-'}`",
        f"- Outlier survivors after outlier-highlight ablation: `{summary['outlierSurvivorCountAfterOutlierHighlightAblation']}` / `{summary['baselineOutlierSlotCount']}`",
        f"- Surviving letters after outlier-highlight ablation: `{summary['outlierSurvivorLettersAfterOutlierHighlightAblation'] or '-'}`",
        f"- Outlier survivors after all-highlight ablation: `{summary['outlierSurvivorCountAfterAllHighlightAblation']}` / `{summary['baselineOutlierSlotCount']}`",
        f"- Mean outlier drop after outlier-highlight ablation: `{summary['meanOutlierHighlightAblationDropPct']:.3f}%`",
        f"- Non-outlier highlight-control status flips: `{summary['nonOutlierHighlightControlFlipCount']}`",
        f"- Hidden highlight-ablation candidate: `{int(summary['hiddenHighlightAblationCandidate'])}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Slot Ablation Trace",
        "",
        "| slot | letter | baseline | other max | outlier | after outlier-highlight ablation | drop | survives | after all-highlight ablation | non-outlier highlight control |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in slot_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['slotId']}`",
                    f"`{row['letter']}`",
                    f"{row['baselineInkOverPageDensity']:.6f}",
                    f"{row['otherLeafInkOverPageDensityMax']:.6f}",
                    str(int(row["baselineOutlier"])),
                    f"{row['inkOverOriginalPageDensityAfterOutlierHighlightAblation']:.6f}",
                    f"{row['outlierHighlightAblationDropPct']:.3f}%",
                    str(int(row["survivesOutlierHighlightAblation"])),
                    f"{row['inkOverOriginalPageDensityAfterAllHighlightAblation']:.6f}",
                    f"{row['inkOverOriginalPageDensityAfterNonOutlierHighlightAblation']:.6f}",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_scan_overdose_density_highlight_ablation_no_selector`",
            "- The slot-density signal depends on mirrored page-75 highlight regions and still supplies no source-backed unit/order rule.",
            "- Do not tune `ROS`/`SOR` slot density unless a new clue specifically names source-highlight bleed-through, slots, density, or a reading order.",
            "",
            "## Next Move",
            "",
            "- Continue with physical/original-layout source validation or raw clue wording that names unit/order/transform.",
            "- If staying local-only, move away from OVERDOSE density and inspect a different mechanism such as original-layout source acquisition or a constrained folded-geometry witness.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
