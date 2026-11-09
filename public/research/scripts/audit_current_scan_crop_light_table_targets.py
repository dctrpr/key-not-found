#!/usr/bin/env python3
"""Crop-level held-to-light inspection around page-76 active targets.

This pass takes the current scan/PDF page images as source material and zooms
the held-to-light simulator into the O4/B4/G5/O5 boxes. It compares the valid
75->76 same-leaf view against the strongest non-physical 79->76 visual
registration benchmark. It is visual/source geometry only: no key derivation,
hashing, seed/WIF/address checks, OCR-to-key extraction, or broad candidate
generation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_crop_light_table_targets"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_crop_light_table_targets.json"
OUT_MD = OUT / "current_scan_crop_light_table_targets.md"
OUT_SHEET = OUT / "current_scan_crop_light_table_targets_sheet.jpg"
OUT_HTML = OUT / "index.html"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAD_X = 180
PAD_Y = 120


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def normalize_pdf_page(page: int) -> Image.Image:
    """Return PDF-extracted page image in readable/upright coordinates."""
    source = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(
        ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean
    )
    return source.rotate(180) if rot_diff < same_diff else source


def feature_channels(img: Image.Image) -> dict[str, np.ndarray]:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    feature = dark | orange | grey
    return {"feature": feature, "dark": dark, "orange": orange, "grey": grey}


def shift_mask(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(mask)
    h, w = mask.shape
    src_x0 = max(0, -dx)
    src_x1 = min(w, w - dx)
    dst_x0 = max(0, dx)
    dst_x1 = min(w, w + dx)
    src_y0 = max(0, -dy)
    src_y1 = min(h, h - dy)
    dst_y0 = max(0, dy)
    dst_y1 = min(h, h + dy)
    if src_x1 > src_x0 and src_y1 > src_y0:
        out[dst_y0:dst_y1, dst_x0:dst_x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def shift_channels(channels: dict[str, np.ndarray], dx: int, dy: int) -> dict[str, np.ndarray]:
    return {name: shift_mask(np.fliplr(mask), dx, dy) for name, mask in channels.items()}


def transform_source_image(img: Image.Image, dx: int, dy: int) -> Image.Image:
    flipped = ImageOps.mirror(img)
    canvas = Image.new("RGB", img.size, "white")
    canvas.paste(flipped, (dx, dy))
    return canvas


def crop_rect(box: list[float], size: tuple[int, int]) -> tuple[int, int, int, int]:
    w, h = size
    x0, y0, x1, y1 = box
    return (
        max(0, round(x0 - PAD_X)),
        max(0, round(y0 - PAD_Y)),
        min(w, round(x1 + PAD_X)),
        min(h, round(y1 + PAD_Y)),
    )


def box_slice(box: list[float]) -> tuple[slice, slice]:
    x0, y0, x1, y1 = [round(v) for v in box]
    return slice(y0, y1), slice(x0, x1)


def mask_stats(source_mask: np.ndarray, target_mask: np.ndarray, box: list[float]) -> dict:
    y_slice, x_slice = box_slice(box)
    src = source_mask[y_slice, x_slice]
    tgt = target_mask[y_slice, x_slice]
    inter = np.logical_and(src, tgt).sum()
    union = np.logical_or(src, tgt).sum()
    src_total = src.sum()
    tgt_total = tgt.sum()
    area = src.size
    return {
        "sourceCoverage": float(src.mean()) if area else 0.0,
        "targetCoverage": float(tgt.mean()) if area else 0.0,
        "intersectionOverBox": float(inter / area) if area else 0.0,
        "intersectionOverTargetInk": float(inter / tgt_total) if tgt_total else 0.0,
        "intersectionOverSourceInk": float(inter / src_total) if src_total else 0.0,
        "jaccard": float(inter / union) if union else 0.0,
    }


def crop_mask_stats(source_mask: np.ndarray, target_mask: np.ndarray, rect: tuple[int, int, int, int]) -> dict:
    x0, y0, x1, y1 = rect
    src = source_mask[y0:y1, x0:x1]
    tgt = target_mask[y0:y1, x0:x1]
    inter = np.logical_and(src, tgt).sum()
    union = np.logical_or(src, tgt).sum()
    return {
        "sourceCoverage": float(src.mean()) if src.size else 0.0,
        "targetCoverage": float(tgt.mean()) if tgt.size else 0.0,
        "jaccard": float(inter / union) if union else 0.0,
    }


def dominant_source_signal(channels: dict[str, np.ndarray], box: list[float]) -> dict:
    y_slice, x_slice = box_slice(box)
    feature = channels["feature"][y_slice, x_slice]
    feature_total = int(feature.sum())
    if feature_total == 0:
        return {
            "dominantSignal": "none",
            "sourceFeaturePixelCount": 0,
            "orangeShareOfSourceFeatures": 0.0,
            "darkShareOfSourceFeatures": 0.0,
            "greyShareOfSourceFeatures": 0.0,
        }
    shares = {
        "orange": float(np.logical_and(channels["orange"][y_slice, x_slice], feature).sum() / feature_total),
        "dark": float(np.logical_and(channels["dark"][y_slice, x_slice], feature).sum() / feature_total),
        "grey": float(np.logical_and(channels["grey"][y_slice, x_slice], feature).sum() / feature_total),
    }
    dominant = max(shares, key=shares.get)
    return {
        "dominantSignal": dominant,
        "sourceFeaturePixelCount": feature_total,
        "orangeShareOfSourceFeatures": shares["orange"],
        "darkShareOfSourceFeatures": shares["dark"],
        "greyShareOfSourceFeatures": shares["grey"],
    }


def draw_crop_panel(
    target: Image.Image,
    source: Image.Image,
    target_mask: np.ndarray,
    source_mask: np.ndarray,
    row: dict,
    scenario_id: str,
    out_path: Path,
) -> None:
    rect = crop_rect(row["box"], target.size)
    x0, y0, x1, y1 = rect
    target_crop = target.crop(rect)
    source_crop = source.crop(rect)
    blend = Image.blend(target_crop, source_crop, 0.42)

    src_overlay = blend.copy().convert("RGBA")
    overlay = Image.new("RGBA", src_overlay.size, (0, 0, 0, 0))
    overlay_arr = np.asarray(overlay).copy()
    local_source = source_mask[y0:y1, x0:x1]
    local_target = target_mask[y0:y1, x0:x1]
    overlay_arr[local_source] = [0, 128, 255, 92]
    overlay_arr[np.logical_and(local_source, local_target)] = [255, 0, 0, 135]
    src_overlay = Image.alpha_composite(src_overlay, Image.fromarray(overlay_arr, "RGBA")).convert("RGB")

    panels = [target_crop, source_crop, blend, src_overlay]
    labels = ["page 76 target crop", "mirrored source crop", "light-table blend", "source/target ink overlay"]
    target_w = 320
    resized = []
    for panel in panels:
        h = round(target_w * panel.height / panel.width)
        resized.append(panel.resize((target_w, h)))
    panel_h = max(img.height for img in resized)
    canvas = Image.new("RGB", (target_w * 4, panel_h + 84), "white")
    draw = ImageDraw.Draw(canvas, "RGBA")
    try:
        font = ImageFont.truetype("Arial.ttf", 14)
        bold = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
        bold = ImageFont.load_default()
    for idx, img in enumerate(resized):
        px = idx * target_w
        canvas.paste(img, (px, 42))
        draw.text((px + 8, 18), labels[idx], fill=(35, 38, 45), font=font)
        bx0 = round((row["box"][0] - x0) * target_w / (x1 - x0))
        by0 = round((row["box"][1] - y0) * img.height / (y1 - y0)) + 42
        bx1 = round((row["box"][2] - x0) * target_w / (x1 - x0))
        by1 = round((row["box"][3] - y0) * img.height / (y1 - y0)) + 42
        draw.rectangle((px + bx0, by0, px + bx1, by1), outline=(255, 0, 0, 230), width=3)
    draw.rectangle((0, 0, canvas.width, 36), fill=(22, 28, 38, 230))
    draw.text(
        (12, 10),
        f"{scenario_id} / {row['shortId']} {row['phrase']}",
        fill=(255, 255, 255),
        font=bold,
    )
    canvas.save(out_path, quality=92)


def draw_summary_sheet(rows: list[dict], crop_paths: list[Path], summary: dict) -> None:
    width, height = 1840, 1280
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 27)
        header_font = ImageFont.truetype("Arial.ttf", 18)
        small = ImageFont.truetype("Arial.ttf", 14)
        tiny = ImageFont.truetype("Arial.ttf", 11)
    except OSError:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()

    draw.rectangle((0, 0, width, 96), fill=(24, 30, 40))
    draw.text((24, 18), "Crop-Level Held-To-Light Target Inspection", fill="white", font=title_font)
    draw.text(
        (24, 56),
        "O4/B4/G5/O5 crop panels compare valid 75->76 leaf and non-physical 79->76 benchmark.",
        fill=(235, 235, 235),
        font=small,
    )

    y = 118
    cards = [
        ("scenarios", summary["scenarioCount"]),
        ("target rows", summary["targetRowCount"]),
        ("all-four >=25%", summary["allFourAt25ScenarioCount"]),
        ("all-four >=50%", summary["allFourAt50ScenarioCount"]),
        ("best scenario", summary["bestMeanCoverageScenario"]),
        ("R3/triggers", f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"),
    ]
    x = 24
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 280, y + 72), radius=6, fill=(246, 248, 250), outline=(208, 215, 222))
        draw.text((x + 12, y + 10), str(label), fill=(80, 86, 96), font=tiny)
        draw.text((x + 12, y + 34), str(value), fill=(22, 26, 34), font=header_font)
        x += 298

    y = 218
    draw.text((24, y), "Scenario Coverage", fill=(22, 26, 34), font=header_font)
    y += 28
    headers = ["scenario", "topology", "dx/dy", "O4", "B4", "G5", "O5", ">=.25", ">=.50", "mean", "decision"]
    xs = [24, 260, 512, 600, 670, 740, 810, 880, 948, 1016, 1088]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(75, 82, 94), font=tiny)
    y += 20
    for row in rows:
        cov = row["coverageByTarget"]
        values = [
            row["scenarioId"],
            row["topology"],
            f"{row['dx']},{row['dy']}",
            f"{cov['O4']:.3f}",
            f"{cov['B4']:.3f}",
            f"{cov['G5']:.3f}",
            f"{cov['O5']:.3f}",
            row["activeBoxCountAt25"],
            row["activeBoxCountAt50"],
            f"{row['meanActiveCoverage']:.3f}",
            row["scenarioDecision"],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value), fill=(38, 42, 50), font=tiny)
        y += 18

    y = 380
    draw.text((24, y), "Crop panels", fill=(22, 26, 34), font=header_font)
    x = 24
    y += 30
    thumb_w = 430
    for idx, path in enumerate(crop_paths[:8]):
        img = Image.open(path).convert("RGB")
        img = img.resize((thumb_w, round(thumb_w * img.height / img.width)))
        sheet.paste(img, (x, y))
        x += thumb_w + 24
        if x + thumb_w > width:
            x = 24
            y += img.height + 30
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    held = load_json(HELD_TO_LIGHT)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = [
        {
            "shortId": row["shortId"],
            "id": row["id"],
            "phrase": row["phrase"],
            "box": row["box"],
            "centerSlotLetter": row.get("centerSlotLetter"),
            "spanSlotLetters": row.get("spanSlotLetters"),
            "visualState": row.get("visualState"),
            "color": row.get("color"),
        }
        for row in active.get("activeRows", [])
    ]
    active_rows.sort(key=lambda row: ["O4", "B4", "G5", "O5"].index(row["shortId"]))

    pages = {page: normalize_pdf_page(page) for page in [75, 76, 79]}
    target = pages[76]
    target_channels = feature_channels(target)
    source_channels = {page: feature_channels(pages[page]) for page in [75, 79]}

    held_rows = {
        (row["pairId"], row["mode"]): row
        for row in held.get("rows", [])
        if row.get("targetPage") == 76
    }
    scenario_specs = [
        {
            "scenarioId": "valid_75_to_76_natural",
            "sourcePage": 75,
            "pairId": "same_leaf_75_to_76",
            "mode": "natural_hflip",
            "topology": "valid same leaf",
        },
        {
            "scenarioId": "valid_75_to_76_forced_best",
            "sourcePage": 75,
            "pairId": "same_leaf_75_to_76",
            "mode": "best_page76_active_boxes",
            "topology": "valid same leaf, forced boundary shift",
        },
        {
            "scenarioId": "benchmark_79_to_76_natural",
            "sourcePage": 79,
            "pairId": "nonphysical_79_to_76",
            "mode": "natural_hflip",
            "topology": "non-physical benchmark",
        },
        {
            "scenarioId": "benchmark_79_to_76_best",
            "sourcePage": 79,
            "pairId": "nonphysical_79_to_76",
            "mode": "best_global_feature",
            "topology": "non-physical benchmark",
        },
    ]

    scenario_rows = []
    target_rows = []
    crop_paths = []
    for spec in scenario_specs:
        held_row = held_rows[(spec["pairId"], spec["mode"])]
        dx, dy = int(held_row["dx"]), int(held_row["dy"])
        transformed_source = transform_source_image(pages[spec["sourcePage"]], dx, dy)
        transformed_channels = shift_channels(source_channels[spec["sourcePage"]], dx, dy)
        coverage_by_target = {}
        jaccard_by_target = {}
        crop_jaccard_by_target = {}
        target_decisions = []
        for row in active_rows:
            rect = crop_rect(row["box"], target.size)
            box_stats = mask_stats(
                transformed_channels["feature"],
                target_channels["feature"],
                row["box"],
            )
            crop_stats = crop_mask_stats(
                transformed_channels["feature"],
                target_channels["feature"],
                rect,
            )
            signal = dominant_source_signal(transformed_channels, row["box"])
            image_path = OUT / f"{spec['scenarioId']}_{row['shortId']}.jpg"
            draw_crop_panel(
                target,
                transformed_source,
                target_channels["feature"],
                transformed_channels["feature"],
                row,
                spec["scenarioId"],
                image_path,
            )
            crop_paths.append(image_path)
            coverage_by_target[row["shortId"]] = box_stats["sourceCoverage"]
            jaccard_by_target[row["shortId"]] = box_stats["jaccard"]
            crop_jaccard_by_target[row["shortId"]] = crop_stats["jaccard"]
            if box_stats["sourceCoverage"] >= 0.50:
                target_decision = "heavy source ink"
            elif box_stats["sourceCoverage"] >= 0.25:
                target_decision = "partial source ink"
            elif box_stats["sourceCoverage"] >= 0.10:
                target_decision = "weak source ink"
            else:
                target_decision = "no meaningful source ink"
            target_decisions.append(target_decision)
            target_rows.append(
                {
                    "scenarioId": spec["scenarioId"],
                    "target": row["shortId"],
                    "phrase": row["phrase"],
                    "centerSlotLetter": row["centerSlotLetter"],
                    "spanSlotLetters": row["spanSlotLetters"],
                    "visualState": row["visualState"],
                    "color": row["color"],
                    "boxStats": box_stats,
                    "cropStats": crop_stats,
                    "sourceSignal": signal,
                    "targetDecision": target_decision,
                    "image": rel(image_path),
                }
            )

        active_count_10 = sum(1 for v in coverage_by_target.values() if v >= 0.10)
        active_count_25 = sum(1 for v in coverage_by_target.values() if v >= 0.25)
        active_count_50 = sum(1 for v in coverage_by_target.values() if v >= 0.50)
        orange_mean = (coverage_by_target["O4"] + coverage_by_target["O5"]) / 2
        black_mean = (coverage_by_target["B4"] + coverage_by_target["G5"]) / 2
        mean_active = sum(coverage_by_target.values()) / len(coverage_by_target)
        if active_count_25 == 4:
            scenario_decision = "would need source rule"
        elif active_count_50 >= 2 and "nonphysical" in spec["topology"]:
            scenario_decision = "non-physical partial visual benchmark"
        elif active_count_50 == 1:
            scenario_decision = "single-target ink concentration"
        else:
            scenario_decision = "no active quartet crop selector"
        scenario_rows.append(
            {
                "scenarioId": spec["scenarioId"],
                "sourcePage": spec["sourcePage"],
                "pairId": spec["pairId"],
                "mode": spec["mode"],
                "topology": spec["topology"],
                "dx": dx,
                "dy": dy,
                "coverageByTarget": coverage_by_target,
                "boxJaccardByTarget": jaccard_by_target,
                "cropJaccardByTarget": crop_jaccard_by_target,
                "activeBoxCountAt10": active_count_10,
                "activeBoxCountAt25": active_count_25,
                "activeBoxCountAt50": active_count_50,
                "orangeTargetMeanCoverage": orange_mean,
                "blackTargetMeanCoverage": black_mean,
                "meanActiveCoverage": mean_active,
                "scenarioDecision": scenario_decision,
            }
        )

    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0
    best_mean = max(scenario_rows, key=lambda row: row["meanActiveCoverage"])
    best_50 = max(scenario_rows, key=lambda row: row["activeBoxCountAt50"])
    summary = {
        "scenarioCount": len(scenario_rows),
        "targetRowCount": len(target_rows),
        "allFourAt10ScenarioCount": sum(1 for row in scenario_rows if row["activeBoxCountAt10"] == 4),
        "allFourAt25ScenarioCount": sum(1 for row in scenario_rows if row["activeBoxCountAt25"] == 4),
        "allFourAt50ScenarioCount": sum(1 for row in scenario_rows if row["activeBoxCountAt50"] == 4),
        "bestMeanCoverageScenario": best_mean["scenarioId"],
        "bestMeanCoverage": best_mean["meanActiveCoverage"],
        "bestAt50Scenario": best_50["scenarioId"],
        "bestAt50Count": best_50["activeBoxCountAt50"],
        "validNaturalCoverageCsv": ",".join(
            f"{best:.4f}"
            for best in scenario_rows[0]["coverageByTarget"].values()
        ),
        "validForcedCoverageCsv": ",".join(
            f"{best:.4f}"
            for best in scenario_rows[1]["coverageByTarget"].values()
        ),
        "benchmark79BestCoverageCsv": ",".join(
            f"{best:.4f}"
            for best in scenario_rows[3]["coverageByTarget"].values()
        ),
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
    }
    summary["cropLightTableFingerprint"] = (
        f"scenarios={summary['scenarioCount']}|targets={summary['targetRowCount']}|"
        f"all10={summary['allFourAt10ScenarioCount']}|all25={summary['allFourAt25ScenarioCount']}|"
        f"all50={summary['allFourAt50ScenarioCount']}|bestMean={summary['bestMeanCoverageScenario']}:"
        f"{summary['bestMeanCoverage']:.4f}|best50={summary['bestAt50Scenario']}:{summary['bestAt50Count']}|"
        f"validNat={summary['validNaturalCoverageCsv']}|validForced={summary['validForcedCoverageCsv']}|"
        f"bench79={summary['benchmark79BestCoverageCsv']}|sourceR3={source_r3}|"
        f"triggers={triggers}/{trigger_count}|selectors=0"
    )

    draw_summary_sheet(scenario_rows, crop_paths, summary)

    html_cards = [
        {
            "label": f"{row['scenarioId']} / {row['target']}",
            "src": Path(row["image"]).name,
            "coverage": row["boxStats"]["sourceCoverage"],
            "jaccard": row["boxStats"]["jaccard"],
            "decision": row["targetDecision"],
        }
        for row in target_rows
    ]
    html = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Crop Light Table Targets</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#10131a;color:#eee}
header{padding:16px 22px;background:#202838}
main{display:grid;grid-template-columns:330px 1fr;gap:18px;padding:18px}
button{display:block;width:100%;margin:4px 0;padding:8px;border:0;background:#303a4f;color:#fff;text-align:left;cursor:pointer}
button:hover{background:#44536f} img{max-width:100%;height:auto;border:1px solid #333}
.meta{font-size:13px;color:#ccc}
</style></head>
<body><header><h1>Crop Light Table Targets</h1><div>O4/B4/G5/O5 crop panels from current scan/PDF held-to-light transforms.</div></header>
<main><section id="buttons"></section><section><h2 id="label"></h2><img id="view"><p id="meta" class="meta"></p></section></main>
<script>
const cards=__CARDS__;
const buttons=document.getElementById('buttons'), view=document.getElementById('view'), label=document.getElementById('label'), meta=document.getElementById('meta');
function show(i){const c=cards[i];view.src=c.src;label.textContent=c.label;meta.textContent=`coverage=${c.coverage.toFixed(4)}; jaccard=${c.jaccard.toFixed(4)}; ${c.decision}`;}
cards.forEach((c,i)=>{const b=document.createElement('button');b.textContent=c.label;b.onclick=()=>show(i);buttons.appendChild(b);});
show(0);
</script></body></html>
""".replace("__CARDS__", json.dumps(html_cards))
    OUT_HTML.write_text(html, encoding="utf-8")

    decision = {
        "currentScanCropLightTableTargets": "crop_light_table_no_active_quartet_selector",
        "selectorUnlocked": False,
        "reason": (
            "At crop level, the valid 75->76 leaf does not cover all four O4/B4/G5/O5 targets, "
            "even with the forced boundary shift. The strongest 79->76 overlay is still non-physical "
            "and concentrates source ink mainly on O4/O5 rather than the full active quartet."
        ),
        "nextMove": (
            "Use the crop panels for manual visual review, but do not extract from them. The next bounded "
            "pass should test whether actual OVERDOSE glyph rectangles projected into these crop windows "
            "change the result, because current light-table ink alone does not supply the missing source-backed unit/order rule."
        ),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "crop-level held-to-light target inspection; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "scenarios": scenario_rows,
        "targetRows": target_rows,
        "summary": summary,
        "decision": decision,
        "sheet": rel(OUT_SHEET),
        "html": rel(OUT_HTML),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current Scan Crop Light-Table Targets",
        "",
        "Scope: zoomed the current held-to-light simulation into the active page-76 O4/B4/G5/O5 boxes. Compared the physically valid 75->76 same-leaf view against the strongest non-physical 79->76 visual-registration benchmark. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- HTML crop viewer: `{rel(OUT_HTML)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Scenarios / target crop rows: `{summary['scenarioCount']}` / `{summary['targetRowCount']}`",
        f"- All-four active target coverage at >=10% / >=25% / >=50%: `{summary['allFourAt10ScenarioCount']}` / `{summary['allFourAt25ScenarioCount']}` / `{summary['allFourAt50ScenarioCount']}`",
        f"- Best mean active coverage: `{summary['bestMeanCoverageScenario']}` at `{summary['bestMeanCoverage']:.4f}`",
        f"- Best >=50% target count: `{summary['bestAt50Scenario']}` with `{summary['bestAt50Count']}/4` targets",
        f"- Valid natural 75->76 O4/B4/G5/O5 source coverage: `{summary['validNaturalCoverageCsv']}`",
        f"- Valid forced 75->76 O4/B4/G5/O5 source coverage: `{summary['validForcedCoverageCsv']}`",
        f"- Benchmark 79->76 best O4/B4/G5/O5 source coverage: `{summary['benchmark79BestCoverageCsv']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{triggers}/{trigger_count}`",
        f"- Fingerprint: `{summary['cropLightTableFingerprint']}`",
        "",
        "## Scenario Rows",
        "",
        "| scenario | topology | dx | dy | O4 | B4 | G5 | O5 | >=.25 | >=.50 | decision |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in scenario_rows:
        cov = row["coverageByTarget"]
        lines.append(
            f"| `{row['scenarioId']}` | {row['topology']} | {row['dx']} | {row['dy']} | "
            f"{cov['O4']:.4f} | {cov['B4']:.4f} | {cov['G5']:.4f} | {cov['O5']:.4f} | "
            f"{row['activeBoxCountAt25']} | {row['activeBoxCountAt50']} | {row['scenarioDecision']} |"
        )

    lines.extend(
        [
            "",
            "## Target Crop Rows",
            "",
            "| scenario | target | source coverage | box jaccard | crop jaccard | dominant source signal | image |",
            "|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in target_rows:
        lines.append(
            f"| `{row['scenarioId']}` | `{row['target']}` | {row['boxStats']['sourceCoverage']:.4f} | "
            f"{row['boxStats']['jaccard']:.4f} | {row['cropStats']['jaccard']:.4f} | "
            f"{row['sourceSignal']['dominantSignal']} | `{row['image']}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision['currentScanCropLightTableTargets']}`",
            f"- {decision['reason']}",
            f"- {decision['nextMove']}",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
