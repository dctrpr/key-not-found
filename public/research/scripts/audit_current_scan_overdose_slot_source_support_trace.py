#!/usr/bin/env python3
"""Trace source-supported OVERDOSE slots back to page-75 source bands.

The light-table self-signal partition showed that the active boxes are
target-only dominated, while several projected OVERDOSE slot controls carry
stronger mirrored page-75 source support. This bounded pass checks whether
those source-supported slots form a usable OVERDOSE mechanic or simply reflect
ordinary page-75 text columns under the valid 75 -> 76 horizontal mirror.

No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address
checks, BIP39 checks, or broad brute force is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_overdose_slot_source_support_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_overdose_slot_source_support_trace.json"
OUT_MD = OUT / "current_scan_overdose_slot_source_support_trace.md"
OUT_SHEET = OUT / "current_scan_overdose_slot_source_support_trace_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
C9_HEADER_GLYPH_SLOT_GATE = ROOT / (
    "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
)
SELF_SIGNAL_PARTITION = ROOT / (
    "analysis_outputs/source_audit/current_scan_light_table_self_signal_partition_gate/"
    "current_scan_light_table_self_signal_partition_gate.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

SOURCE_INK_LUMA_THRESHOLD = 238.0
TARGET_INK_LUMA_THRESHOLD = 238.0
AVERAGE_ALPHA = 0.70
HIGH_SOURCE_SHARE_THRESHOLD = 0.50

STRICT_INSTRUCTION_TERMS = {
    "above",
    "below",
    "bold",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "edges",
    "first",
    "fold",
    "folded",
    "font",
    "highlight",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "letters",
    "line",
    "lines",
    "mirror",
    "mirrored",
    "order",
    "outside",
    "read",
    "reads",
    "reverse",
    "right",
    "side",
    "slot",
    "take",
    "takes",
    "top",
    "window",
    "word",
    "words",
}
ACTION_ORDER_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "edges",
    "first",
    "fold",
    "folded",
    "inside",
    "key",
    "last",
    "left",
    "mirror",
    "mirrored",
    "order",
    "outside",
    "read",
    "reads",
    "reverse",
    "right",
    "side",
    "take",
    "takes",
    "top",
    "window",
}
CONTEXT_TERMS = {
    "bitcoin",
    "bitcoins",
    "bond",
    "bonds",
    "bukele",
    "dip",
    "heart",
    "imf",
    "overdose",
    "salvador",
    "sell",
    "shitcoiner",
    "volcano",
    "volcanoes",
}


def rel(path: Path | str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return str(p.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
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


def normalize_page(page: int) -> Image.Image:
    source_path = Path(str(SOURCE_PAGE_TEMPLATE).format(page=page))
    upright_path = Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=page))
    if source_path.exists():
        source = Image.open(source_path).convert("RGB")
        upright = Image.open(upright_path).convert("RGB")
        sample_size = (318, 408)
        source_sample = source.resize(sample_size)
        upright_sample = upright.resize(sample_size)
        same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
        rot_diff = sum(
            ImageStat.Stat(
                ImageChops.difference(source_sample.rotate(180), upright_sample)
            ).mean
        )
        return source.rotate(180) if rot_diff < same_diff else source
    return Image.open(upright_path).convert("RGB")


def luma(arr: np.ndarray) -> np.ndarray:
    return 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]


def average_blend(target_arr: np.ndarray, source_arr: np.ndarray) -> np.ndarray:
    return np.clip(
        (1.0 - AVERAGE_ALPHA) * target_arr.astype(np.float32)
        + AVERAGE_ALPHA * source_arr.astype(np.float32),
        0,
        255,
    ).astype(np.uint8)


def crop_arr(arr: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return arr[y0:y1, x0:x1, :]


def crop_bool(mask: np.ndarray, box: list[float]) -> np.ndarray:
    h, w = mask.shape[:2]
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, min(w, x0))
    x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0))
    y1 = max(0, min(h, y1))
    return mask[y0:y1, x0:x1]


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def box_area(box: list[float] | None) -> float:
    if box is None:
        return 0.0
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0


def overlap_box(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def page_words(page_no: int) -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    for page in data.get("pages", []):
        if int(page.get("page", -1)) != page_no:
            continue
        words: list[dict[str, Any]] = []
        for word in page.get("words", []):
            text = compact(str(word.get("text") or word.get("token") or ""))
            token = clean_token(str(word.get("token") or text))
            if not text and not token:
                continue
            box = [float(v) for v in word["box"]]
            words.append(
                {
                    "id": word.get("id"),
                    "index": word.get("index"),
                    "text": text,
                    "token": token,
                    "box": box,
                    "center": center(box),
                }
            )
        return words
    return []


def words_in_region(words: list[dict[str, Any]], region: list[float]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for word in words:
        inter = overlap_box(region, word["box"])
        word_area = max(box_area(word["box"]), 1.0)
        overlap_fraction = box_area(inter) / word_area if inter else 0.0
        center_hit = in_box(word["center"], region)
        if center_hit or overlap_fraction >= 0.10:
            hits.append(
                {
                    **word,
                    "centerInRegion": center_hit,
                    "overlapFraction": round(overlap_fraction, 4),
                    "strictInstruction": word["token"] in STRICT_INSTRUCTION_TERMS,
                    "contextTerm": word["token"] in CONTEXT_TERMS,
                }
            )
    return sorted(hits, key=lambda item: (item["box"][1], item["box"][0], item.get("index") or 0))


def word_row_count(words: list[dict[str, Any]]) -> int:
    centers = sorted((word["box"][1] + word["box"][3]) / 2.0 for word in words)
    if not centers:
        return 0
    rows = [centers[0]]
    for cy in centers[1:]:
        if abs(cy - rows[-1]) > 22:
            rows.append(cy)
        else:
            rows[-1] = (rows[-1] + cy) / 2.0
    return len(rows)


def source_box_from_target_box(
    target_box: list[float], width: int, height: int, dx: int = 0, dy: int = 0
) -> list[float]:
    tx0, ty0, tx1, ty1 = [float(v) for v in target_box]
    sx0 = width - (tx1 - dx)
    sx1 = width - (tx0 - dx)
    sy0 = ty0 - dy
    sy1 = ty1 - dy
    return [max(0.0, sx0), max(0.0, sy0), min(float(width), sx1), min(float(height), sy1)]


def source_feature_stats(source_arr: np.ndarray, source_box: list[float]) -> dict[str, Any]:
    crop = crop_arr(source_arr, source_box)
    if crop.size == 0:
        return {
            "sourceFeatureCoverage": 0.0,
            "sourceDarkCoverage": 0.0,
            "sourceOrangeCoverage": 0.0,
            "sourceGreyCoverage": 0.0,
            "dominantSourceSignal": "none",
        }
    r = crop[:, :, 0].astype(np.int16)
    g = crop[:, :, 1].astype(np.int16)
    b = crop[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3.0
    dark = mean < 178
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    feature = dark | orange | grey
    totals = {
        "dark": int(dark.sum()),
        "orange": int(orange.sum()),
        "grey": int(grey.sum()),
    }
    dominant = max(totals, key=totals.get) if int(feature.sum()) else "none"
    return {
        "sourceFeatureCoverage": round(float(feature.mean()), 6),
        "sourceDarkCoverage": round(float(dark.mean()), 6),
        "sourceOrangeCoverage": round(float(orange.mean()), 6),
        "sourceGreyCoverage": round(float(grey.mean()), 6),
        "dominantSourceSignal": dominant,
    }


def overdose_slot_boxes(c9: dict[str, Any]) -> list[dict[str, Any]]:
    frame = [float(v) for v in c9.get("c9Frame", [294.0, 2176.81, 2250.0, 3023.73])]
    projection = next(
        (item for item in c9.get("projections", []) if item.get("name") == "p76_header_glyph"),
        {},
    )
    rows: list[dict[str, Any]] = []
    for slot in projection.get("slots", []):
        rows.append(
            {
                "slotIndex": int(slot["index"]),
                "slotLetter": str(slot["letter"]),
                "targetBox": [float(slot["left"]), frame[1], float(slot["right"]), frame[3]],
                "sourceGlyphBox": slot.get("sourceGlyphBox"),
            }
        )
    return rows


def measure_slot(
    slot: dict[str, Any],
    target_arr: np.ndarray,
    mirrored_source_arr: np.ndarray,
    source_arr: np.ndarray,
    source_ink_mask: np.ndarray,
    target_ink_mask: np.ndarray,
    page75_words: list[dict[str, Any]],
    prior_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    target_box = slot["targetBox"]
    target_crop = crop_arr(target_arr, target_box)
    source_crop = crop_arr(mirrored_source_arr, target_box)
    blend_crop = average_blend(target_crop, source_crop)
    source_ink = crop_bool(source_ink_mask, target_box)
    target_ink = crop_bool(target_ink_mask, target_box)
    delta = np.abs(luma(target_crop) - luma(blend_crop))
    total_delta = float(delta.sum())
    source_supported_delta = float(delta[source_ink].sum()) if source_ink.any() else 0.0
    target_only = target_ink & ~source_ink
    target_only_delta = float(delta[target_only].sum()) if target_only.any() else 0.0
    source_box = source_box_from_target_box(target_box, target_arr.shape[1], target_arr.shape[0])
    words = words_in_region(page75_words, source_box)
    strict_hits = sorted({word["token"] for word in words if word["strictInstruction"]})
    action_order_hits = sorted({token for token in strict_hits if token in ACTION_ORDER_TERMS})
    unit_only_hits = sorted({token for token in strict_hits if token not in ACTION_ORDER_TERMS})
    context_hits = sorted({word["token"] for word in words if word["contextTerm"]})
    prior_key = f"{slot['slotLetter']}{slot['slotIndex']}"
    prior = prior_rows.get(prior_key, {})
    source_share = round(source_supported_delta / total_delta, 6) if total_delta else 0.0
    target_share = round(target_only_delta / total_delta, 6) if total_delta else 0.0
    return {
        **slot,
        "slotId": prior_key,
        "sourceBox": [round(v, 2) for v in source_box],
        "averageDelta": round(float(delta.mean()), 6) if delta.size else 0.0,
        "sourceInkRatio": round(float(source_ink.mean()), 6) if source_ink.size else 0.0,
        "targetInkRatio": round(float(target_ink.mean()), 6) if target_ink.size else 0.0,
        "sourceSupportedDeltaShare": source_share,
        "targetOnlyDeltaShare": target_share,
        "sourceSupportedDeltaMean": round(float((delta * source_ink).mean()), 6) if delta.size else 0.0,
        "sourceOnlyDeltaShare": round(
            float(delta[source_ink & ~target_ink].sum()) / total_delta, 6
        )
        if total_delta and (source_ink & ~target_ink).any()
        else 0.0,
        "sourceSupportedDominant": source_share >= HIGH_SOURCE_SHARE_THRESHOLD,
        "priorPartitionSourceSupportedDeltaShare": prior.get("sourceSupportedDeltaShare"),
        "priorPartitionSourceSupportedDeltaMean": prior.get("sourceSupportedDeltaMean"),
        "sourceWordCount": len(words),
        "sourceWordRowCount": word_row_count(words),
        "sourceTextPreview": compact(" ".join(word["text"] for word in words))[:220],
        "sourceWords": words[:80],
        "strictInstructionHits": strict_hits,
        "strictInstructionHitCount": len(strict_hits),
        "actionOrderInstructionHits": action_order_hits,
        "actionOrderInstructionHitCount": len(action_order_hits),
        "unitOnlyInstructionHits": unit_only_hits,
        "unitOnlyInstructionHitCount": len(unit_only_hits),
        "contextTermHits": context_hits,
        "contextTermHitCount": len(context_hits),
        **source_feature_stats(source_arr, source_box),
    }


def high_runs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for row in rows:
        if row["sourceSupportedDominant"]:
            current.append(row)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return [
        {
            "slotIds": [row["slotId"] for row in run],
            "letters": "".join(row["slotLetter"] for row in run),
            "startIndex": run[0]["slotIndex"],
            "endIndex": run[-1]["slotIndex"],
            "length": len(run),
            "strictInstructionHitCount": sum(row["strictInstructionHitCount"] for row in run),
            "actionOrderInstructionHitCount": sum(row["actionOrderInstructionHitCount"] for row in run),
            "unitOnlyInstructionHitCount": sum(row["unitOnlyInstructionHitCount"] for row in run),
            "contextTermHitCount": sum(row["contextTermHitCount"] for row in run),
            "sourceWordCount": sum(row["sourceWordCount"] for row in run),
            "sourceWordRowCount": sum(row["sourceWordRowCount"] for row in run),
            "sourceTextPreview": " | ".join(row["sourceTextPreview"] for row in run if row["sourceTextPreview"])[:300],
        }
        for run in runs
    ]


def draw_sheet(target_img: Image.Image, source_img: Image.Image, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 1320), (248, 248, 244))
    draw = ImageDraw.Draw(sheet, "RGBA")
    draw.rectangle((0, 0, 1840, 92), fill=(28, 32, 39))
    draw.text((24, 16), "OVERDOSE Slot Source-Support Trace", fill="white", font=font(26, True))
    draw.text((24, 52), summary["fingerprint"], fill=(230, 230, 230), font=font(12))

    crop_w, crop_h = 430, 185
    for idx, row in enumerate(rows):
        px = 24 + (idx % 4) * 452
        py = 120 + (idx // 4) * 255
        source_box = row["sourceBox"]
        pad_x, pad_y = 36, 28
        crop_box = [
            max(0, round(source_box[0] - pad_x)),
            max(0, round(source_box[1] - pad_y)),
            min(source_img.width, round(source_box[2] + pad_x)),
            min(source_img.height, round(source_box[3] + pad_y)),
        ]
        crop = source_img.crop(tuple(crop_box)).resize((crop_w, crop_h), Image.Resampling.LANCZOS)
        sheet.paste(crop, (px, py))

        def sx(x: float) -> int:
            return px + round((x - crop_box[0]) * crop_w / max(crop_box[2] - crop_box[0], 1))

        def sy(y: float) -> int:
            return py + round((y - crop_box[1]) * crop_h / max(crop_box[3] - crop_box[1], 1))

        draw.rectangle(
            [sx(source_box[0]), sy(source_box[1]), sx(source_box[2]), sy(source_box[3])],
            outline=(255, 95, 0, 240) if row["sourceSupportedDominant"] else (40, 105, 225, 210),
            width=3,
        )
        draw.rectangle((px, py, px + crop_w, py + 28), fill=(20, 24, 31, 185))
        draw.text(
            (px + 8, py + 7),
            f"{row['slotId']} source share={row['sourceSupportedDeltaShare']:.3f} words={row['sourceWordCount']} strict={row['strictInstructionHitCount']}",
            fill="white",
            font=font(12),
        )
        preview = row["sourceTextPreview"][:72] + ("..." if len(row["sourceTextPreview"]) > 72 else "")
        draw.text((px, py + crop_h + 8), preview or "(no source OCR word hit)", fill=(42, 48, 58), font=font(12))
        draw.text(
            (px, py + crop_h + 27),
            f"mapped x={source_box[0]:.0f}-{source_box[2]:.0f} rows={row['sourceWordRowCount']} context={','.join(row['contextTermHits']) or '-'}",
            fill=(78, 84, 95),
            font=font(11),
        )

    y = 666
    draw.text((24, y), "Slot Trace", fill=(30, 30, 30), font=font(18, True))
    y += 30
    headers = ["slot", "src share", "target share", "src x", "words", "rows", "strict", "context", "source text"]
    xs = [24, 88, 178, 274, 375, 432, 486, 568, 710]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(70, 70, 70), font=font(11))
    y += 20
    for row in rows:
        values = [
            row["slotId"],
            f"{row['sourceSupportedDeltaShare']:.3f}",
            f"{row['targetOnlyDeltaShare']:.3f}",
            f"{row['sourceBox'][0]:.0f}-{row['sourceBox'][2]:.0f}",
            str(row["sourceWordCount"]),
            str(row["sourceWordRowCount"]),
            ",".join(row["strictInstructionHits"]) or "-",
            ",".join(row["contextTermHits"]) or "-",
            row["sourceTextPreview"][:92],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value), fill=(25, 25, 25), font=font(11))
        y += 20

    y += 26
    draw.rectangle((24, y, 1816, y + 148), outline=(210, 216, 226), width=1)
    draw.text((44, y + 18), "Decision", fill=(24, 31, 42), font=font(18, True))
    decision_lines = [
        f"High source-supported slots: {summary['highSourceSupportedSlotIdsCsv'] or '-'}; runs: {summary['highSourceSupportedRunsCsv'] or '-'}.",
        f"High-slot action/order instruction hits: {summary['highSlotActionOrderInstructionHitCount']}; source-backed R3/triggers: {summary['sourceBackedR3BridgeHitCount']}/{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}.",
        "The high slots map to ordinary page-75 lower text bands, not to a source-side unit/order instruction.",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((44, y + 54 + idx * 25), line, fill=(55, 65, 80), font=font(14))
    sheet.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current Scan OVERDOSE Slot Source-Support Trace",
        "",
        "Scope: valid page `75 -> 76` horizontal-mirror light-table geometry only. Each projected OVERDOSE slot was mapped back to its page-75 source band, then checked for source words, instruction terms, and context terms. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Slots traced: `{summary['slotCount']}`",
        f"- High source-supported slots: `{summary['highSourceSupportedSlotCount']}` (`{summary['highSourceSupportedSlotIdsCsv'] or '-'}`)",
        f"- High source-supported runs: `{summary['highSourceSupportedRunsCsv'] or '-'}`",
        f"- Source word hits / rows: `{summary['totalSourceWordHits']}` / `{summary['totalSourceWordRows']}`",
        f"- Instruction-like hits / high-slot action-order hits: `{summary['totalStrictInstructionHits']}` / `{summary['highSlotActionOrderInstructionHitCount']}`",
        f"- Unit-only terms: `{', '.join(summary['unitOnlyInstructionHits']) or '-'}`",
        f"- Context hits: `{summary['totalContextTermHits']}` (`{', '.join(summary['contextTermHits']) or '-'}`)",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['fingerprint']}`",
        "",
        "## Slot Rows",
        "",
        "| slot | source-supported share | target-only share | source x band | words | rows | instruction-like | action/order | context | source text preview |",
        "|---|---:|---:|---|---:|---:|---|---|---|---|",
    ]
    for row in result["slotRows"]:
        text = row["sourceTextPreview"].replace("|", "\\|")
        lines.append(
            f"| `{row['slotId']}` | `{row['sourceSupportedDeltaShare']}` | `{row['targetOnlyDeltaShare']}` | "
            f"`{row['sourceBox'][0]:.0f}-{row['sourceBox'][2]:.0f}` | {row['sourceWordCount']} | "
            f"{row['sourceWordRowCount']} | `{', '.join(row['strictInstructionHits']) or '-'}` | "
            f"`{', '.join(row['actionOrderInstructionHits']) or '-'}` | "
            f"`{', '.join(row['contextTermHits']) or '-'}` | {text} |"
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
    c9 = load_json(C9_HEADER_GLYPH_SLOT_GATE)
    self_signal = load_json(SELF_SIGNAL_PARTITION)
    triggers = load_json(REOPEN_TRIGGER_MATRIX)
    target_img = normalize_page(76)
    source_img = normalize_page(75)
    mirrored_source = ImageOps.mirror(source_img)

    target_arr = np.asarray(target_img.convert("RGB"))
    mirrored_source_arr = np.asarray(mirrored_source.convert("RGB"))
    source_arr = np.asarray(source_img.convert("RGB"))
    source_ink_mask = luma(mirrored_source_arr) < SOURCE_INK_LUMA_THRESHOLD
    target_ink_mask = luma(target_arr) < TARGET_INK_LUMA_THRESHOLD
    page75_words = page_words(75)
    prior_rows = {
        f"{row.get('slotLetter')}{row.get('slotIndex')}": row
        for row in self_signal.get("rows", [])
        if row.get("kind") == "overdose_slot"
    }

    slot_rows = [
        measure_slot(
            slot,
            target_arr,
            mirrored_source_arr,
            source_arr,
            source_ink_mask,
            target_ink_mask,
            page75_words,
            prior_rows,
        )
        for slot in overdose_slot_boxes(c9)
    ]
    slot_rows.sort(key=lambda row: row["slotIndex"])
    runs = high_runs(slot_rows)
    high_slots = [row for row in slot_rows if row["sourceSupportedDominant"]]
    high_slot_ids = [row["slotId"] for row in high_slots]
    source_r3 = int(triggers.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(triggers.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(triggers.get("summary", {}).get("triggerCount") or 0)
    high_strict_hits = sum(row["strictInstructionHitCount"] for row in high_slots)
    high_action_order_hits = sum(row["actionOrderInstructionHitCount"] for row in high_slots)
    total_strict_hits = sum(row["strictInstructionHitCount"] for row in slot_rows)
    total_action_order_hits = sum(row["actionOrderInstructionHitCount"] for row in slot_rows)
    total_context_hits = sum(row["contextTermHitCount"] for row in slot_rows)
    context_terms = sorted({term for row in slot_rows for term in row["contextTermHits"]})
    unit_only_terms = sorted({term for row in slot_rows for term in row["unitOnlyInstructionHits"]})
    high_run_csv = ",".join(f"{run['letters']}@{run['startIndex']}-{run['endIndex']}" for run in runs)
    selector = bool(source_r3 and high_slots and high_action_order_hits)
    decision = (
        "overdose_slot_source_support_is_page75_text_band_no_selector"
        if not selector
        else "overdose_slot_source_support_requires_manual_review"
    )
    reason = (
        "The high source-supported OVERDOSE slots form a contiguous OSE run, but their mirrored source bands contain ordinary page-75 prose/context, not a source-backed unit/order instruction."
        if not selector
        else "A high source-supported slot also has source-backed instruction evidence; review manually before any extraction."
    )
    next_move = (
        "Treat these OVERDOSE slots as a useful source-support control, not as an extraction selector; stop varying light-table blend/slot opacity unless a new source or clue names unit, transform, and read order."
        if not selector
        else "Inspect high-slot source bands against source-reopen requirements before continuing."
    )
    fingerprint = (
        f"slots={len(slot_rows)}|highSrc={len(high_slots)}|highRun={high_run_csv or '-'}|"
        f"highSlots={','.join(high_slot_ids) or '-'}|words={sum(row['sourceWordCount'] for row in slot_rows)}|"
        f"wordRows={sum(row['sourceWordRowCount'] for row in slot_rows)}|instructionLike={total_strict_hits}|"
        f"actionOrder={total_action_order_hits}|highActionOrder={high_action_order_hits}|"
        f"unitOnly={','.join(unit_only_terms) or '-'}|context={total_context_hits}|"
        f"sourceR3={source_r3}|triggers={satisfied}/{trigger_count}|selectors={int(selector)}"
    )
    summary = {
        "slotCount": len(slot_rows),
        "highSourceSupportedSlotCount": len(high_slots),
        "highSourceSupportedSlotIds": high_slot_ids,
        "highSourceSupportedSlotIdsCsv": ",".join(high_slot_ids),
        "highSourceSupportedRuns": runs,
        "highSourceSupportedRunsCsv": high_run_csv,
        "totalSourceWordHits": sum(row["sourceWordCount"] for row in slot_rows),
        "totalSourceWordRows": sum(row["sourceWordRowCount"] for row in slot_rows),
        "medianSourceWordRowsPerSlot": median([row["sourceWordRowCount"] for row in slot_rows])
        if slot_rows
        else 0,
        "totalStrictInstructionHits": total_strict_hits,
        "highSlotStrictInstructionHitCount": high_strict_hits,
        "totalActionOrderInstructionHits": total_action_order_hits,
        "highSlotActionOrderInstructionHitCount": high_action_order_hits,
        "unitOnlyInstructionHits": unit_only_terms,
        "totalContextTermHits": total_context_hits,
        "contextTermHits": context_terms,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "selectorUnlocked": selector,
        "fingerprint": fingerprint,
    }
    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "valid 75->76 OVERDOSE slot source-support trace; no extraction, candidates, hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "c9HeaderGlyphSlotGate": rel(C9_HEADER_GLYPH_SLOT_GATE),
            "selfSignalPartition": rel(SELF_SIGNAL_PARTITION),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "sourcePage": rel(Path(str(SOURCE_PAGE_TEMPLATE).format(page=75))),
            "targetPage": rel(Path(str(UPRIGHT_PAGE_TEMPLATE).format(page=76))),
            "alpha": AVERAGE_ALPHA,
            "sourceInkLumaThreshold": SOURCE_INK_LUMA_THRESHOLD,
            "targetInkLumaThreshold": TARGET_INK_LUMA_THRESHOLD,
        },
        "summary": summary,
        "slotRows": slot_rows,
        "decision": decision,
        "reason": reason,
        "nextMove": next_move,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(target_img, source_img, slot_rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)
    print(decision)


if __name__ == "__main__":
    main()
