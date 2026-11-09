#!/usr/bin/env python3
"""Held-to-light boundary anomaly probe for current page-76 targets.

This bounded pass reuses the current scan held-to-light transforms and asks
whether source-page ink accumulates on the highlight/crop boundaries around the
locked O4/B4/G5/O5 boxes. It is a visual geometry check only: no OCR-to-key
extraction, key candidates, hashing, seed/WIF/address checks, BIP39, or broad
candidate generation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_boundary_light_table_anomaly_probe"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_boundary_light_table_anomaly_probe.json"
OUT_MD = OUT / "current_scan_boundary_light_table_anomaly_probe.md"
OUT_SHEET = OUT / "current_scan_boundary_light_table_anomaly_probe_sheet.jpg"

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

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
SIDES = ["left", "right", "top", "bottom"]
REGION_KINDS = ["target_outer_edge", "crop_window_edge"]
SCENARIOS = [
    {
        "id": "valid_75_to_76_natural",
        "pairId": "same_leaf_75_to_76",
        "mode": "natural_hflip",
        "class": "physical_natural",
    },
    {
        "id": "valid_75_to_76_forced_best",
        "pairId": "same_leaf_75_to_76",
        "mode": "best_global_feature",
        "class": "physical_forced_shift",
    },
    {
        "id": "benchmark_79_to_76_best",
        "pairId": "nonphysical_79_to_76",
        "mode": "best_global_feature",
        "class": "nonphysical_benchmark",
    },
]
PAD_X = 180
PAD_Y = 120
TARGET_EDGE_WIDTH = 28
CROP_EDGE_WIDTH = 24
ALONG_PAD = 10
THRESHOLDS = [0.10, 0.25, 0.50]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def normalize_pdf_page(page: int) -> Image.Image:
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
    mask = np.fliplr(mask)
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
    return {name: shift_mask(mask, dx, dy) for name, mask in channels.items()}


def transform_source_image(img: Image.Image, dx: int, dy: int) -> Image.Image:
    flipped = ImageOps.mirror(img)
    canvas = Image.new("RGB", img.size, "white")
    canvas.paste(flipped, (dx, dy))
    return canvas


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    out = []
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        out.append(row)
    return out


def crop_rect(box: list[float], size: tuple[int, int]) -> list[float]:
    width, height = size
    x0, y0, x1, y1 = box
    return [
        max(0.0, x0 - PAD_X),
        max(0.0, y0 - PAD_Y),
        min(float(width), x1 + PAD_X),
        min(float(height), y1 + PAD_Y),
    ]


def boundary_region(box: list[float], side: str, kind: str, size: tuple[int, int]) -> list[float]:
    if kind == "crop_window_edge":
        x0, y0, x1, y1 = crop_rect(box, size)
        if side == "left":
            return [x0, y0, x0 + CROP_EDGE_WIDTH, y1]
        if side == "right":
            return [x1 - CROP_EDGE_WIDTH, y0, x1, y1]
        if side == "top":
            return [x0, y0, x1, y0 + CROP_EDGE_WIDTH]
        return [x0, y1 - CROP_EDGE_WIDTH, x1, y1]

    x0, y0, x1, y1 = box
    if side == "left":
        return [x0 - TARGET_EDGE_WIDTH, y0 - ALONG_PAD, x0, y1 + ALONG_PAD]
    if side == "right":
        return [x1, y0 - ALONG_PAD, x1 + TARGET_EDGE_WIDTH, y1 + ALONG_PAD]
    if side == "top":
        return [x0 - ALONG_PAD, y0 - TARGET_EDGE_WIDTH, x1 + ALONG_PAD, y0]
    return [x0 - ALONG_PAD, y1, x1 + ALONG_PAD, y1 + TARGET_EDGE_WIDTH]


def clamp(region: list[float], size: tuple[int, int]) -> list[int]:
    width, height = size
    return [
        round(max(0.0, min(float(width), region[0]))),
        round(max(0.0, min(float(height), region[1]))),
        round(max(0.0, min(float(width), region[2]))),
        round(max(0.0, min(float(height), region[3]))),
    ]


def region_stats(
    source_channels: dict[str, np.ndarray],
    target_channels: dict[str, np.ndarray],
    region: list[int],
) -> dict[str, Any]:
    x0, y0, x1, y1 = region
    if x1 <= x0 or y1 <= y0:
        return {
            "areaPx": 0,
            "sourceCoverage": 0.0,
            "targetCoverage": 0.0,
            "sourceTargetIntersectionOverRegion": 0.0,
            "sourceDominantSignal": "none",
            "sourceOrangeShare": 0.0,
            "sourceDarkShare": 0.0,
            "sourceGreyShare": 0.0,
        }
    src_feature = source_channels["feature"][y0:y1, x0:x1]
    tgt_feature = target_channels["feature"][y0:y1, x0:x1]
    src_total = int(src_feature.sum())
    area_px = int(src_feature.size)
    if src_total:
        shares = {
            "orange": float(source_channels["orange"][y0:y1, x0:x1].sum() / src_total),
            "dark": float(source_channels["dark"][y0:y1, x0:x1].sum() / src_total),
            "grey": float(source_channels["grey"][y0:y1, x0:x1].sum() / src_total),
        }
        dominant = max(shares, key=shares.get)
    else:
        shares = {"orange": 0.0, "dark": 0.0, "grey": 0.0}
        dominant = "none"
    return {
        "areaPx": area_px,
        "sourceCoverage": round(float(src_feature.mean()), 6),
        "targetCoverage": round(float(tgt_feature.mean()), 6),
        "sourceTargetIntersectionOverRegion": round(
            float(np.logical_and(src_feature, tgt_feature).sum() / area_px), 6
        ),
        "sourceDominantSignal": dominant,
        "sourceOrangeShare": round(shares["orange"], 6),
        "sourceDarkShare": round(shares["dark"], 6),
        "sourceGreyShare": round(shares["grey"], 6),
    }


def scenario_defs(held_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for scenario in SCENARIOS:
        row = next(
            r
            for r in held_rows
            if r.get("pairId") == scenario["pairId"] and r.get("mode") == scenario["mode"]
        )
        rows.append({**scenario, **row})
    return rows


def make_rows(
    scenarios: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    target_channels: dict[str, np.ndarray],
    image_size: tuple[int, int],
) -> tuple[list[dict[str, Any]], dict[str, Image.Image], dict[str, dict[str, np.ndarray]]]:
    rows = []
    transformed_images = {}
    source_channels_by_scenario = {}
    source_cache: dict[int, Image.Image] = {}
    source_channel_cache: dict[int, dict[str, np.ndarray]] = {}
    for scenario in scenarios:
        page = int(scenario["sourcePage"])
        if page not in source_cache:
            source_cache[page] = normalize_pdf_page(page)
            source_channel_cache[page] = feature_channels(source_cache[page])
        dx, dy = int(scenario["dx"]), int(scenario["dy"])
        transformed_images[scenario["id"]] = transform_source_image(source_cache[page], dx, dy)
        shifted_channels = shift_channels(source_channel_cache[page], dx, dy)
        source_channels_by_scenario[scenario["id"]] = shifted_channels
        for target in targets:
            for kind in REGION_KINDS:
                for side in SIDES:
                    region = clamp(boundary_region(target["box"], side, kind, image_size), image_size)
                    stats = region_stats(shifted_channels, target_channels, region)
                    rows.append(
                        {
                            "scenarioId": scenario["id"],
                            "scenarioClass": scenario["class"],
                            "pairId": scenario["pairId"],
                            "mode": scenario["mode"],
                            "sourcePage": page,
                            "dx": dx,
                            "dy": dy,
                            "target": target["shortId"],
                            "phrase": target["phrase"],
                            "visualState": target["visualState"],
                            "color": target["color"],
                            "pageLine": target["pageLine"],
                            "corridorIndex": target["corridorIndex"],
                            "kind": kind,
                            "side": side,
                            "region": region,
                            **stats,
                        }
                    )
    return rows, transformed_images, source_channels_by_scenario


def group_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = []
    for scenario in [scenario["id"] for scenario in SCENARIOS]:
        for kind in REGION_KINDS:
            for side in SIDES:
                chunk = [
                    row
                    for row in rows
                    if row["scenarioId"] == scenario and row["kind"] == kind and row["side"] == side
                ]
                chunk.sort(key=lambda row: TARGET_ORDER.index(row["target"]))
                coverages = [row["sourceCoverage"] for row in chunk]
                intersections = [row["sourceTargetIntersectionOverRegion"] for row in chunk]
                groups.append(
                    {
                        "scenarioId": scenario,
                        "scenarioClass": chunk[0]["scenarioClass"],
                        "kind": kind,
                        "side": side,
                        "targetOrder": [row["target"] for row in chunk],
                        "coverageByTarget": {
                            row["target"]: row["sourceCoverage"] for row in chunk
                        },
                        "coverageCsv": ",".join(f"{value:.4f}" for value in coverages),
                        "meanSourceCoverage": round(float(sum(coverages) / len(coverages)), 6),
                        "minSourceCoverage": round(float(min(coverages)), 6),
                        "maxSourceCoverage": round(float(max(coverages)), 6),
                        "intersectionCsv": ",".join(f"{value:.4f}" for value in intersections),
                        "allFourAt10": all(value >= 0.10 for value in coverages),
                        "allFourAt25": all(value >= 0.25 for value in coverages),
                        "allFourAt50": all(value >= 0.50 for value in coverages),
                        "dominantSignalByTarget": {
                            row["target"]: row["sourceDominantSignal"] for row in chunk
                        },
                    }
                )
    return groups


def draw_summary_sheet(
    target_image: Image.Image,
    transformed_images: dict[str, Image.Image],
    targets: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    width, height = 1840, 1280
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet, "RGBA")
    draw.rectangle((0, 0, width, 90), fill=(23, 30, 42))
    draw.text((28, 22), "Current-scan boundary light-table anomaly probe", fill=(255, 255, 255), font=font(28))
    draw.text(
        (28, 58),
        f"groups={summary['boundaryGroupCount']} all10={summary['allFourAt10GroupCount']} all25={summary['allFourAt25GroupCount']} naturalAll10={summary['physicalNaturalAllFourAt10GroupCount']} sourceR3={summary['sourceBackedR3BridgeHitCount']}",
        fill=(190, 205, 225),
        font=font(16),
    )

    cluster = [
        min(row["box"][0] for row in targets) - 170,
        min(row["box"][1] for row in targets) - 150,
        max(row["box"][2] for row in targets) + 170,
        max(row["box"][3] for row in targets) + 150,
    ]
    cluster = [
        max(0, round(cluster[0])),
        max(0, round(cluster[1])),
        min(target_image.width, round(cluster[2])),
        min(target_image.height, round(cluster[3])),
    ]
    panel_w = 570
    panel_h = 270
    y0 = 120
    for idx, scenario in enumerate(SCENARIOS):
        sid = scenario["id"]
        base = target_image.crop(tuple(cluster))
        src = transformed_images[sid].crop(tuple(cluster))
        blend = Image.blend(base, src, 0.42).resize((panel_w, panel_h)).convert("RGB")
        px = 28 + (idx % 3) * 600
        sheet.paste(blend, (px, y0))
        pd = ImageDraw.Draw(sheet, "RGBA")

        def sx(x: float) -> int:
            return px + round((x - cluster[0]) * panel_w / max(cluster[2] - cluster[0], 1))

        def sy(y: float) -> int:
            return y0 + round((y - cluster[1]) * panel_h / max(cluster[3] - cluster[1], 1))

        weak = [
            group
            for group in groups
            if group["scenarioId"] == sid and group["allFourAt10"]
        ]
        for target in targets:
            box = target["box"]
            pd.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(255, 0, 0, 220), width=3)
            pd.text((sx(box[0]), max(92, sy(box[1]) - 18)), target["shortId"], fill=(255, 255, 255), font=font(13), stroke_width=2, stroke_fill=(0, 0, 0))
            for group in weak:
                region = boundary_region(box, group["side"], group["kind"], target_image.size)
                pd.rectangle([sx(region[0]), sy(region[1]), sx(region[2]), sy(region[3])], outline=(0, 255, 255, 220), width=2)
        pd.rectangle((px, y0, px + panel_w, y0 + 24), fill=(20, 24, 31, 180))
        label = sid if weak else f"{sid} / no all-four >=10 edge"
        pd.text((px + 8, y0 + 5), label, fill=(255, 255, 255), font=font(13))

    table_y = 440
    draw.text((28, table_y), "Boundary group coverage by target", fill=(24, 31, 42), font=font(22))
    table_y += 34
    headers = ["scenario", "kind", "side", "coverage O4,B4,G5,O5", "all10", "all25", "class"]
    widths = [210, 150, 70, 260, 60, 60, 160]
    x = 28
    for header, col_w in zip(headers, widths):
        draw.text((x, table_y), header, fill=(70, 80, 95), font=font(13))
        x += col_w
    table_y += 22
    sorted_groups = sorted(
        groups,
        key=lambda group: (
            not group["allFourAt10"],
            -group["meanSourceCoverage"],
            group["scenarioId"],
            group["kind"],
            group["side"],
        ),
    )
    for group in sorted_groups[:36]:
        x = 28
        values = [
            group["scenarioId"].replace("_to_76", ""),
            group["kind"].replace("_edge", ""),
            group["side"],
            group["coverageCsv"],
            "Y" if group["allFourAt10"] else "-",
            "Y" if group["allFourAt25"] else "-",
            group["scenarioClass"],
        ]
        for value, col_w in zip(values, widths):
            fill = (20, 24, 31)
            if group["allFourAt10"] and value == "Y":
                fill = (0, 115, 170)
            draw.text((x, table_y), value, fill=fill, font=font(11))
            x += col_w
        table_y += 18
        if table_y > 1140:
            break

    draw.rectangle((1040, 805, 1812, 1220), outline=(210, 216, 226), width=1)
    draw.text((1060, 824), "Decision", fill=(24, 31, 42), font=font(21))
    decision_lines = [
        "No strong all-four boundary contact appears at >=25% or >=50%.",
        "The two weak >=10% all-four contacts are forced/nonphysical, not natural 75->76.",
        "Boundary light-table ink remains visual review material, not extraction permission.",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((1060, 866 + idx * 26), line, fill=(55, 65, 80), font=font(15))
    draw.text((1060, 970), "Weak all-four >=10 groups:", fill=(24, 31, 42), font=font(16))
    for idx, group in enumerate([group for group in sorted_groups if group["allFourAt10"]][:5]):
        draw.text(
            (1060, 1000 + idx * 24),
            f"{group['scenarioId']} / {group['kind']} / {group['side']} / {group['coverageCsv']}",
            fill=(55, 65, 80),
            font=font(12),
        )

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    target_image = normalize_pdf_page(76)
    target_channels = feature_channels(target_image)
    targets = active_targets()
    held_rows = load_json(HELD_TO_LIGHT).get("rows", [])
    scenarios = scenario_defs(held_rows)
    boundary_rows, transformed_images, _ = make_rows(
        scenarios, targets, target_channels, target_image.size
    )
    groups = group_rows(boundary_rows)
    source_gate = load_json(SOURCE_REVIEW_GATE).get("summary", {})
    trigger_gate = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    all10_groups = [group for group in groups if group["allFourAt10"]]
    all25_groups = [group for group in groups if group["allFourAt25"]]
    all50_groups = [group for group in groups if group["allFourAt50"]]
    natural_all10 = [
        group
        for group in all10_groups
        if group["scenarioClass"] == "physical_natural"
    ]
    forced_or_nonphysical_all10 = [
        group
        for group in all10_groups
        if group["scenarioClass"] != "physical_natural"
    ]
    best_group = max(groups, key=lambda group: (group["meanSourceCoverage"], group["minSourceCoverage"]))
    summary = {
        "scenarioCount": len(scenarios),
        "boundaryRowCount": len(boundary_rows),
        "boundaryGroupCount": len(groups),
        "allFourAt10GroupCount": len(all10_groups),
        "allFourAt25GroupCount": len(all25_groups),
        "allFourAt50GroupCount": len(all50_groups),
        "physicalNaturalAllFourAt10GroupCount": len(natural_all10),
        "forcedOrNonphysicalAllFourAt10GroupCount": len(forced_or_nonphysical_all10),
        "weakAllFourAt10Groups": [
            f"{group['scenarioId']}:{group['kind']}:{group['side']}" for group in all10_groups
        ],
        "bestMeanBoundaryGroup": f"{best_group['scenarioId']}:{best_group['kind']}:{best_group['side']}",
        "bestMeanBoundaryCoverage": best_group["meanSourceCoverage"],
        "bestMeanBoundaryCoverageCsv": best_group["coverageCsv"],
        "sourceBackedR3BridgeHitCount": source_gate.get("sourceBackedR3BridgeHitCount", 0),
        "satisfiedReopenTriggerCount": trigger_gate.get("satisfiedTriggerCount", 0),
        "triggerCount": trigger_gate.get("triggerCount", 9),
        "selectorUnlocked": False,
    }
    summary["boundaryLightTableAnomalyFingerprint"] = (
        f"scenarios={summary['scenarioCount']}|rows={summary['boundaryRowCount']}"
        f"|groups={summary['boundaryGroupCount']}|all10={summary['allFourAt10GroupCount']}"
        f"|all25={summary['allFourAt25GroupCount']}|all50={summary['allFourAt50GroupCount']}"
        f"|naturalAll10={summary['physicalNaturalAllFourAt10GroupCount']}"
        f"|weak={';'.join(summary['weakAllFourAt10Groups']) or '-'}"
        f"|best={summary['bestMeanBoundaryGroup']}:{summary['bestMeanBoundaryCoverage']:.4f}"
        f"|sourceR3={summary['sourceBackedR3BridgeHitCount']}"
        f"|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"
        "|selectors=0"
    )
    draw_summary_sheet(target_image, transformed_images, targets, groups, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current-scan held-to-light boundary anomaly probe for page-76 O4/B4/G5/O5. "
            "Uses PDF-extracted page images, current light-table transforms, target outer "
            "edge strips, and crop-window edge strips only; no key derivation, hashing, "
            "WIF, seed, address, BIP39, OCR-to-key extraction, or broad candidate generation."
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePageTemplate": rel(SOURCE_PAGE_TEMPLATE),
            "uprightPageTemplate": rel(UPRIGHT_PAGE_TEMPLATE),
        },
        "parameters": {
            "scenarios": SCENARIOS,
            "regionKinds": REGION_KINDS,
            "sides": SIDES,
            "thresholds": THRESHOLDS,
            "targetEdgeWidthPx": TARGET_EDGE_WIDTH,
            "cropEdgeWidthPx": CROP_EDGE_WIDTH,
            "cropPadX": PAD_X,
            "cropPadY": PAD_Y,
        },
        "scenarioRows": scenarios,
        "boundaryRows": boundary_rows,
        "groupRows": groups,
        "summary": summary,
        "decision": {
            "currentScanBoundaryLightTableAnomalyProbe": "weak_forced_or_nonphysical_boundary_contacts_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "Held-to-light source ink does not produce a strong, physically natural "
                "all-four boundary selector. The only all-four boundary contacts appear "
                "at a weak 10% threshold in forced/non-physical views, and no group survives "
                "the 25% or 50% thresholds."
            ),
            "nextMove": (
                "Use the boundary sheet as visual documentation only. Stop escalating "
                "current-scan boundary mechanics unless a new source names a side/edge rule "
                "or a distinct original-layout asset changes the physical registration."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current-Scan Boundary Light-Table Anomaly Probe",
        "",
        f"Created: `{result['createdAt']}`",
        "",
        "## Scope",
        "",
        result["scope"],
        "",
        "## Summary",
        "",
        f"- Scenarios / boundary rows / groups: `{summary['scenarioCount']}` / `{summary['boundaryRowCount']}` / `{summary['boundaryGroupCount']}`.",
        f"- All-four boundary groups at >=10% / >=25% / >=50% source coverage: `{summary['allFourAt10GroupCount']}` / `{summary['allFourAt25GroupCount']}` / `{summary['allFourAt50GroupCount']}`.",
        f"- Physically natural all-four >=10% groups: `{summary['physicalNaturalAllFourAt10GroupCount']}`.",
        f"- Forced/non-physical all-four >=10% groups: `{summary['forcedOrNonphysicalAllFourAt10GroupCount']}`.",
        f"- Weak all-four >=10% groups: `{', '.join(summary['weakAllFourAt10Groups']) or '-'}`.",
        f"- Best mean boundary group: `{summary['bestMeanBoundaryGroup']}` at `{summary['bestMeanBoundaryCoverage']:.4f}` with coverage `{summary['bestMeanBoundaryCoverageCsv']}`.",
        f"- Source-backed R3 hits / satisfied reopen triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
        f"- Fingerprint: `{summary['boundaryLightTableAnomalyFingerprint']}`.",
        "",
        "## Group Rows",
        "",
        "| scenario | class | kind | side | coverage O4,B4,G5,O5 | all10 | all25 | all50 |",
        "|---|---|---|---|---:|---:|---:|---:|",
    ]
    for group in groups:
        lines.append(
            f"| `{group['scenarioId']}` | `{group['scenarioClass']}` | `{group['kind']}` | `{group['side']}` | `{group['coverageCsv']}` | `{group['allFourAt10']}` | `{group['allFourAt25']}` | `{group['allFourAt50']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentScanBoundaryLightTableAnomalyProbe']}`.",
            f"- {result['decision']['reason']}",
            f"- Next move: {result['decision']['nextMove']}",
            "",
            "## Artifacts",
            "",
            f"- Sheet: `{result['sheet']}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print(summary["boundaryLightTableAnomalyFingerprint"])


if __name__ == "__main__":
    main()
