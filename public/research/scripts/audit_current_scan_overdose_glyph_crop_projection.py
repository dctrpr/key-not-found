#!/usr/bin/env python3
"""Project actual OVERDOSE glyph slots into current scan light-table crops.

This bounded pass combines three already-locked surfaces:
- current PDF/scan page images normalized into readable/upright coordinates;
- the current held-to-light transforms; and
- actual measured OVERDOSE header glyph boundaries scaled into the C9 frame.

It asks whether source ink inside O4/B4/G5/O5 becomes more selective when the
target boxes are subdivided by real OVERDOSE glyph rectangles. It does not run
OCR-to-key extraction, hashing, seed/WIF/address checks, BIP39 checks, or broad
candidate generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_glyph_crop_projection"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_glyph_crop_projection.json"
OUT_MD = OUT / "current_scan_overdose_glyph_crop_projection.md"
OUT_SHEET = OUT / "current_scan_overdose_glyph_crop_projection_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
HELD_TO_LIGHT = ROOT / (
    "analysis_outputs/source_audit/current_scan_held_to_light_simulator/"
    "current_scan_held_to_light_simulator.json"
)
C9_HEADER_GLYPH = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/"
    "c9_header_glyph_slot_gate.json"
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

LETTERS = "OVERDOSE"
TARGET_ORDER = ["O4", "B4", "G5", "O5"]
STRICT_INSTRUCTION_TERMS = [
    "take",
    "read",
    "word",
    "letter",
    "line",
    "first",
    "last",
    "key",
    "seed",
    "private",
    "mirror",
    "fold",
]
LAYOUT_TERMS = ["OVER", "DOSE", "OVERDOSE"]
THRESHOLDS = [0.10, 0.25, 0.50]
PAD_X = 180
PAD_Y = 120


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def compact(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text).upper()


def term_hits(stream: str, terms: list[str]) -> list[str]:
    cstream = compact(stream)
    return [term for term in terms if compact(term) in cstream]


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


def slot_box(target_box: list[float], slot: dict) -> tuple[int, int, int, int] | None:
    left = max(float(target_box[0]), float(slot["left"]))
    right = min(float(target_box[2]), float(slot["right"]))
    top = float(target_box[1])
    bottom = float(target_box[3])
    if right <= left or bottom <= top:
        return None
    return round(left), round(top), round(right), round(bottom)


def slot_stats(
    target_box: list[float],
    slot: dict,
    source_feature: np.ndarray,
    target_feature: np.ndarray,
) -> dict:
    region = slot_box(target_box, slot)
    if not region:
        return {
            "index": slot["index"],
            "letter": slot["letter"],
            "area": 0,
            "sourceCoverage": 0.0,
            "targetCoverage": 0.0,
            "intersectionOverSlotArea": 0.0,
            "jaccard": 0.0,
        }
    x0, y0, x1, y1 = region
    src = source_feature[y0:y1, x0:x1]
    tgt = target_feature[y0:y1, x0:x1]
    inter = np.logical_and(src, tgt).sum()
    union = np.logical_or(src, tgt).sum()
    return {
        "index": slot["index"],
        "letter": slot["letter"],
        "area": int(src.size),
        "sourceCoverage": float(src.mean()) if src.size else 0.0,
        "targetCoverage": float(tgt.mean()) if tgt.size else 0.0,
        "intersectionOverSlotArea": float(inter / src.size) if src.size else 0.0,
        "jaccard": float(inter / union) if union else 0.0,
    }


def glyph_letters_for_threshold(slot_rows: list[dict], threshold: float) -> str:
    return "".join(row["letter"] for row in slot_rows if row["sourceCoverage"] >= threshold)


def dominant_slot(slot_rows: list[dict], threshold: float = 0.10) -> dict:
    candidates = [row for row in slot_rows if row["area"] > 0]
    if not candidates:
        return {"letter": ".", "index": None, "sourceCoverage": 0.0}
    best = max(candidates, key=lambda row: (row["sourceCoverage"], row["intersectionOverSlotArea"]))
    if best["sourceCoverage"] < threshold:
        return {"letter": ".", "index": best["index"], "sourceCoverage": best["sourceCoverage"]}
    return {"letter": best["letter"], "index": best["index"], "sourceCoverage": best["sourceCoverage"]}


def make_stream_record(name: str, rows: list[dict], field: str) -> dict:
    raw = "".join(row[field] for row in rows)
    compact_stream = raw.replace(".", "")
    return {
        "name": name,
        "rawStream": raw,
        "stream": compact_stream,
        "targetOrder": [row["target"] for row in rows],
        "layoutTermHits": term_hits(compact_stream, LAYOUT_TERMS),
        "strictInstructionHits": term_hits(compact_stream, STRICT_INSTRUCTION_TERMS),
    }


def draw_crop_panel(
    target: Image.Image,
    transformed_source: Image.Image,
    target_feature: np.ndarray,
    source_feature: np.ndarray,
    row: dict,
    slots: list[dict],
    scenario_id: str,
    out_path: Path,
) -> None:
    rect = crop_rect(row["box"], target.size)
    x0, y0, x1, y1 = rect
    target_crop = target.crop(rect)
    source_crop = transformed_source.crop(rect)
    blend = Image.blend(target_crop, source_crop, 0.42).convert("RGBA")
    overlay = Image.new("RGBA", blend.size, (0, 0, 0, 0))
    overlay_arr = np.asarray(overlay).copy()
    local_src = source_feature[y0:y1, x0:x1]
    local_tgt = target_feature[y0:y1, x0:x1]
    overlay_arr[local_src] = [0, 128, 255, 90]
    overlay_arr[np.logical_and(local_src, local_tgt)] = [255, 0, 0, 132]
    blend = Image.alpha_composite(blend, Image.fromarray(overlay_arr, "RGBA")).convert("RGB")

    target_w = 700
    resized = blend.resize((target_w, round(target_w * blend.height / blend.width)))
    canvas = Image.new("RGB", (target_w, resized.height + 72), "white")
    canvas.paste(resized, (0, 72))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 0, canvas.width, 60), fill=(23, 30, 41, 235))
    draw.text(
        (12, 10),
        f"{scenario_id} / {row['target']} {row['phrase']}",
        fill=(255, 255, 255),
        font=font(16),
    )
    draw.text(
        (12, 36),
        f"dominant {row['dominant10Letter']} ({row['dominant10Coverage']:.3f}); >=10 slots {row['slots10Letters'] or '-'}",
        fill=(220, 228, 238),
        font=font(13),
    )

    def sx(x: float) -> float:
        return (x - x0) * target_w / (x1 - x0)

    def sy(y: float) -> float:
        return 72 + (y - y0) * resized.height / (y1 - y0)

    colors = [
        (255, 190, 80),
        (246, 130, 90),
        (120, 190, 255),
        (150, 220, 150),
        (220, 160, 255),
        (255, 220, 120),
        (110, 210, 230),
        (245, 160, 170),
    ]
    for slot, color in zip(slots, colors):
        left = max(float(slot["left"]), x0)
        right = min(float(slot["right"]), x1)
        if right <= left:
            continue
        draw.rectangle((sx(left), 72, sx(right), canvas.height - 1), outline=color + (190,), width=2)
        draw.text((sx(left) + 4, 76), slot["letter"], fill=color + (255,), font=font(12))
    bx0, by0, bx1, by1 = row["box"]
    draw.rectangle((sx(bx0), sy(by0), sx(bx1), sy(by1)), outline=(255, 0, 0, 240), width=3)
    canvas.save(out_path, quality=92)


def draw_sheet(scenario_rows: list[dict], target_rows: list[dict], summary: dict, crop_paths: list[Path]) -> None:
    width, height = 1840, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title_font = font(27)
    header_font = font(18)
    small = font(13)
    tiny = font(11)
    draw.rectangle((0, 0, width, 96), fill=(24, 30, 40))
    draw.text((24, 18), "Current Scan OVERDOSE Glyph Crop Projection", fill="white", font=title_font)
    draw.text(
        (24, 56),
        "Actual OVERDOSE glyph slots projected into O4/B4/G5/O5 held-to-light crop windows.",
        fill=(235, 235, 235),
        font=small,
    )
    y = 118
    cards = [
        ("scenario/projection rows", summary["scenarioProjectionCount"]),
        ("target rows", summary["targetGlyphRowCount"]),
        ("all-four dom>=10", summary["allFourDominant10ScenarioProjectionCount"]),
        ("all-four slot>=25", summary["allFourTouched25ScenarioProjectionCount"]),
        ("layout hit streams", summary["layoutHitStreamCount"]),
        ("R3/triggers", f"{summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"),
    ]
    x = 24
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 280, y + 72), radius=6, fill=(246, 248, 250), outline=(208, 215, 222))
        draw.text((x + 12, y + 10), label, fill=(80, 86, 96), font=tiny)
        draw.text((x + 12, y + 34), str(value), fill=(22, 26, 34), font=header_font)
        x += 298

    y = 222
    draw.text((24, y), "Scenario/projection streams", fill=(22, 26, 34), font=header_font)
    y += 28
    headers = ["scenario", "projection", "dom line", "dom x", "black >=10", ">=25 all?", "layout", "decision"]
    xs = [24, 310, 470, 570, 670, 790, 890, 1010]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(75, 82, 94), font=tiny)
    y += 20
    for row in scenario_rows:
        vals = [
            row["scenarioId"],
            row["glyphProjection"],
            row["dominant10LineStream"],
            row["dominant10XStream"],
            row["blackSlots10XStream"],
            row["allFourTouched25"],
            row["layoutTermHitStreamCount"],
            row["scenarioDecision"],
        ]
        for tx, val in zip(xs, vals):
            draw.text((tx, y), str(val), fill=(38, 42, 50), font=tiny)
        y += 18
        if y > 610:
            break

    y = 642
    draw.text((24, y), "Representative p76-glyph crop panels", fill=(22, 26, 34), font=header_font)
    y += 30
    x = 24
    thumb_w = 430
    for path in crop_paths[:8]:
        img = Image.open(path).convert("RGB")
        img = img.resize((thumb_w, round(thumb_w * img.height / img.width)))
        sheet.paste(img, (x, y))
        x += thumb_w + 24
        if x + thumb_w > width:
            x = 24
            y += img.height + 28
        if y > height - 260:
            break
    sheet.save(OUT_SHEET, quality=92)


def build() -> dict:
    active = load_json(ACTIVE_INDEX_SLOT)
    held = load_json(HELD_TO_LIGHT)
    glyph = load_json(C9_HEADER_GLYPH)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)

    active_rows = []
    for row in active.get("activeRows", []):
        active_rows.append(
            {
                "target": row["shortId"],
                "id": row["id"],
                "phrase": row["phrase"],
                "box": [float(v) for v in row["box"]],
                "visualState": row["visualState"],
                "color": row["color"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "centerX": row["centerX"],
            }
        )
    active_rows.sort(key=lambda row: TARGET_ORDER.index(row["target"]))

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
        ("valid_75_to_76_natural", 75, "same_leaf_75_to_76", "natural_hflip", "valid same leaf"),
        ("valid_75_to_76_forced_best", 75, "same_leaf_75_to_76", "best_page76_active_boxes", "valid same leaf, forced boundary shift"),
        ("benchmark_79_to_76_natural", 79, "nonphysical_79_to_76", "natural_hflip", "non-physical benchmark"),
        ("benchmark_79_to_76_best", 79, "nonphysical_79_to_76", "best_global_feature", "non-physical benchmark"),
    ]

    projections = [
        {
            "name": projection["name"],
            "slots": projection["slots"],
            "maxAbsEdgeDeltaVsEqualSlotPx": projection.get("maxAbsEdgeDeltaVsEqualSlotPx"),
        }
        for projection in glyph.get("projections", [])
    ]

    scenario_rows: list[dict] = []
    target_rows: list[dict] = []
    stream_rows: list[dict] = []
    crop_paths: list[Path] = []
    for scenario_id, source_page, pair_id, mode, topology in scenario_specs:
        held_row = held_rows[(pair_id, mode)]
        dx, dy = int(held_row["dx"]), int(held_row["dy"])
        transformed_source = transform_source_image(pages[source_page], dx, dy)
        transformed_channels = shift_channels(source_channels[source_page], dx, dy)
        for projection in projections:
            projected_rows = []
            for base in active_rows:
                slot_rows = [
                    slot_stats(
                        base["box"],
                        slot,
                        transformed_channels["feature"],
                        target_channels["feature"],
                    )
                    for slot in projection["slots"]
                ]
                dom10 = dominant_slot(slot_rows, 0.10)
                dom25 = dominant_slot(slot_rows, 0.25)
                row = {
                    **base,
                    "scenarioId": scenario_id,
                    "sourcePage": source_page,
                    "pairId": pair_id,
                    "mode": mode,
                    "topology": topology,
                    "dx": dx,
                    "dy": dy,
                    "glyphProjection": projection["name"],
                    "slotRows": slot_rows,
                    "dominant10Letter": dom10["letter"],
                    "dominant10SlotIndex": dom10["index"],
                    "dominant10Coverage": dom10["sourceCoverage"],
                    "dominant25Letter": dom25["letter"],
                    "dominant25SlotIndex": dom25["index"],
                    "dominant25Coverage": dom25["sourceCoverage"],
                    "slots10Letters": glyph_letters_for_threshold(slot_rows, 0.10),
                    "slots25Letters": glyph_letters_for_threshold(slot_rows, 0.25),
                    "slots50Letters": glyph_letters_for_threshold(slot_rows, 0.50),
                    "maxSlotSourceCoverage": max((slot["sourceCoverage"] for slot in slot_rows), default=0.0),
                }
                if projection["name"] == "p76_header_glyph":
                    image_path = OUT / f"{scenario_id}_{base['target']}_p76_glyph_slots.jpg"
                    draw_crop_panel(
                        target,
                        transformed_source,
                        target_channels["feature"],
                        transformed_channels["feature"],
                        row,
                        projection["slots"],
                        scenario_id,
                        image_path,
                    )
                    row["image"] = rel(image_path)
                    crop_paths.append(image_path)
                projected_rows.append(row)
                target_rows.append(row)

            line_order = sorted(projected_rows, key=lambda row: TARGET_ORDER.index(row["target"]))
            x_order = sorted(projected_rows, key=lambda row: row["centerX"])
            black_x = [row for row in x_order if row["visualState"] == "K"]
            orange_x = [row for row in x_order if row["visualState"] == "Y"]
            stream_specs = [
                ("dominant10_line", line_order, "dominant10Letter"),
                ("dominant10_x", x_order, "dominant10Letter"),
                ("dominant25_line", line_order, "dominant25Letter"),
                ("slots10_line", line_order, "slots10Letters"),
                ("slots10_x", x_order, "slots10Letters"),
                ("black_slots10_x", black_x, "slots10Letters"),
                ("orange_slots10_x", orange_x, "slots10Letters"),
                ("slots25_line", line_order, "slots25Letters"),
                ("black_slots25_x", black_x, "slots25Letters"),
            ]
            scenario_streams = [
                make_stream_record(f"{scenario_id}_{projection['name']}_{label}", rows, field)
                for label, rows, field in stream_specs
            ]
            stream_rows.extend(scenario_streams)
            all_four_dom10 = all(row["dominant10Letter"] != "." for row in line_order)
            all_four_touch25 = all(bool(row["slots25Letters"]) for row in line_order)
            all_four_touch50 = all(bool(row["slots50Letters"]) for row in line_order)
            layout_count = sum(1 for stream in scenario_streams if stream["layoutTermHits"])
            strict_count = sum(len(stream["strictInstructionHits"]) for stream in scenario_streams)
            black_slots10 = next(
                stream["stream"] for stream in scenario_streams if stream["name"].endswith("black_slots10_x")
            )
            if all_four_touch25:
                decision = "would need source rule"
            elif "nonphysical" in topology and layout_count:
                decision = "non-physical glyph/source-ink layout fragment"
            elif all_four_dom10:
                decision = "weak all-target glyph coverage"
            else:
                decision = "no active quartet glyph-ink selector"
            scenario_rows.append(
                {
                    "scenarioId": scenario_id,
                    "sourcePage": source_page,
                    "pairId": pair_id,
                    "mode": mode,
                    "topology": topology,
                    "dx": dx,
                    "dy": dy,
                    "glyphProjection": projection["name"],
                    "dominant10LineStream": next(
                        stream["rawStream"] for stream in scenario_streams if stream["name"].endswith("dominant10_line")
                    ),
                    "dominant10XStream": next(
                        stream["rawStream"] for stream in scenario_streams if stream["name"].endswith("dominant10_x")
                    ),
                    "dominant25LineStream": next(
                        stream["rawStream"] for stream in scenario_streams if stream["name"].endswith("dominant25_line")
                    ),
                    "slots10LineStream": next(
                        stream["stream"] for stream in scenario_streams if stream["name"].endswith("slots10_line")
                    ),
                    "slots10XStream": next(
                        stream["stream"] for stream in scenario_streams if stream["name"].endswith("slots10_x")
                    ),
                    "blackSlots10XStream": black_slots10,
                    "allFourDominant10": all_four_dom10,
                    "allFourTouched25": all_four_touch25,
                    "allFourTouched50": all_four_touch50,
                    "layoutTermHitStreamCount": layout_count,
                    "strictInstructionHitCount": strict_count,
                    "scenarioDecision": decision,
                }
            )

    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0
    layout_hit_streams = [row for row in stream_rows if row["layoutTermHits"]]
    strict_hit_streams = [row for row in stream_rows if row["strictInstructionHits"]]
    valid_nat = next(
        row
        for row in scenario_rows
        if row["scenarioId"] == "valid_75_to_76_natural" and row["glyphProjection"] == "p76_header_glyph"
    )
    valid_forced = next(
        row
        for row in scenario_rows
        if row["scenarioId"] == "valid_75_to_76_forced_best" and row["glyphProjection"] == "p76_header_glyph"
    )
    bench_best = next(
        row
        for row in scenario_rows
        if row["scenarioId"] == "benchmark_79_to_76_best" and row["glyphProjection"] == "p76_header_glyph"
    )
    summary = {
        "glyphProjectionCount": len(projections),
        "scenarioProjectionCount": len(scenario_rows),
        "targetGlyphRowCount": len(target_rows),
        "streamCount": len(stream_rows),
        "allFourDominant10ScenarioProjectionCount": sum(1 for row in scenario_rows if row["allFourDominant10"]),
        "allFourTouched25ScenarioProjectionCount": sum(1 for row in scenario_rows if row["allFourTouched25"]),
        "allFourTouched50ScenarioProjectionCount": sum(1 for row in scenario_rows if row["allFourTouched50"]),
        "layoutHitStreamCount": len(layout_hit_streams),
        "strictInstructionHitCount": sum(len(row["strictInstructionHits"]) for row in stream_rows),
        "validNaturalDominant10LineStream": valid_nat["dominant10LineStream"],
        "validForcedDominant10LineStream": valid_forced["dominant10LineStream"],
        "benchmark79BestDominant10LineStream": bench_best["dominant10LineStream"],
        "validNaturalBlackSlots10XStream": valid_nat["blackSlots10XStream"],
        "validForcedBlackSlots10XStream": valid_forced["blackSlots10XStream"],
        "benchmark79BestBlackSlots10XStream": bench_best["blackSlots10XStream"],
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
    }
    summary["glyphCropProjectionFingerprint"] = (
        f"glyphs={summary['glyphProjectionCount']}|scenarioProj={summary['scenarioProjectionCount']}|"
        f"targets={summary['targetGlyphRowCount']}|allDom10={summary['allFourDominant10ScenarioProjectionCount']}|"
        f"all25={summary['allFourTouched25ScenarioProjectionCount']}|all50={summary['allFourTouched50ScenarioProjectionCount']}|"
        f"layoutStreams={summary['layoutHitStreamCount']}|strict={summary['strictInstructionHitCount']}|"
        f"validNat={summary['validNaturalDominant10LineStream']}|validForced={summary['validForcedDominant10LineStream']}|"
        f"bench79={summary['benchmark79BestDominant10LineStream']}|black10={summary['validNaturalBlackSlots10XStream']}/"
        f"{summary['validForcedBlackSlots10XStream']}/{summary['benchmark79BestBlackSlots10XStream']}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors=0"
    )
    draw_sheet(scenario_rows, target_rows, summary, crop_paths)
    return {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current scan held-to-light OVERDOSE glyph crop projection; no extraction or candidate generation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "heldToLightSimulator": rel(HELD_TO_LIGHT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "scenarioRows": scenario_rows,
        "targetRows": target_rows,
        "streamRows": stream_rows,
        "summary": summary,
        "decision": {
            "currentScanOverdoseGlyphCropProjection": "glyph_crop_projection_no_active_quartet_selector",
            "selectorUnlocked": False,
            "reason": (
                "Actual OVERDOSE glyph slots do not turn the current held-to-light crop windows into a source-backed selector. "
                "The valid 75->76 natural case still lacks a complete active quartet; any layout fragments are weak, forced, or non-physical and still lack R3 unit/order wording."
            ),
            "nextMove": (
                "Use this as the glyph-aware stop-check for the current scan. The next bounded move is not another slot permutation; "
                "inspect whether page-76 highlight edges or crop-window boundaries supply a source-backed instruction term, or wait for distinct source/original-layout material."
            ),
        },
        "sheet": rel(OUT_SHEET),
    }


def write_report(result: dict) -> None:
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = result["summary"]
    lines = [
        "# Current Scan OVERDOSE Glyph Crop Projection",
        "",
        "Scope: projected actual measured OVERDOSE header glyph slots into the current scan held-to-light crop windows for O4/B4/G5/O5. This checks glyph geometry plus source ink, not key material. No OCR-to-key extraction, hashes, WIF, seed phrase, address, BIP39, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Glyph projections / scenario-projection rows / target rows: `{summary['glyphProjectionCount']}` / `{summary['scenarioProjectionCount']}` / `{summary['targetGlyphRowCount']}`",
        f"- All-four dominant >=10% / touched >=25% / touched >=50%: `{summary['allFourDominant10ScenarioProjectionCount']}` / `{summary['allFourTouched25ScenarioProjectionCount']}` / `{summary['allFourTouched50ScenarioProjectionCount']}`",
        f"- Layout-hit streams / strict instruction hits: `{summary['layoutHitStreamCount']}` / `{summary['strictInstructionHitCount']}`",
        f"- Valid natural 75->76 dominant line stream: `{summary['validNaturalDominant10LineStream']}`",
        f"- Valid forced 75->76 dominant line stream: `{summary['validForcedDominant10LineStream']}`",
        f"- Benchmark 79->76 best dominant line stream: `{summary['benchmark79BestDominant10LineStream']}`",
        f"- Valid natural / forced / benchmark black >=10% x streams: `{summary['validNaturalBlackSlots10XStream']}` / `{summary['validForcedBlackSlots10XStream']}` / `{summary['benchmark79BestBlackSlots10XStream']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['glyphCropProjectionFingerprint']}`",
        "",
        "## Scenario Rows",
        "",
        "| scenario | projection | dx | dy | dominant line | dominant x | black >=10 x | all dom >=10 | all >=25 | layout streams | decision |",
        "|---|---|---:|---:|---|---|---|---:|---:|---:|---|",
    ]
    for row in result["scenarioRows"]:
        lines.append(
            f"| `{row['scenarioId']}` | `{row['glyphProjection']}` | {row['dx']} | {row['dy']} | "
            f"`{row['dominant10LineStream']}` | `{row['dominant10XStream']}` | `{row['blackSlots10XStream']}` | "
            f"{int(row['allFourDominant10'])} | {int(row['allFourTouched25'])} | {row['layoutTermHitStreamCount']} | {row['scenarioDecision']} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentScanOverdoseGlyphCropProjection']}`",
            "- Do not promote actual OVERDOSE glyph rectangles inside the current light-table crop windows as an extraction selector.",
            "- The glyph-aware pass does not create a physically valid all-four O4/B4/G5/O5 selector at meaningful thresholds.",
            "- Any remaining layout fragments are still controlled by prior OVERDOSE/p75 results or depend on forced/non-physical registration, and no source-backed unit/order wording appears.",
            f"- Next move: {result['decision']['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = build()
    write_report(result)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
