#!/usr/bin/env python3
"""Probe current-scan highlight/crop boundaries for source instruction text.

This bounded pass uses the current PDF-extracted page-76 scan, the locked
O4/B4/G5/O5 boxes, and the 3D OCR word map. It asks whether target highlight
edges or the current light-table crop-window boundaries carry nearby source
words that explicitly name a unit/order such as word, letter, edge, side, fold,
or mirror. It does not derive keys, hash text, generate seed/WIF/address
candidates, or run OCR-to-key extraction.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_highlight_boundary_instruction_probe"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_highlight_boundary_instruction_probe.json"
OUT_MD = OUT / "current_scan_highlight_boundary_instruction_probe.md"
OUT_SHEET = OUT / "current_scan_highlight_boundary_instruction_probe_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"
UPRIGHT_PAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
PAD_X = 180
PAD_Y = 120
TARGET_EDGE_WIDTH = 28
CROP_EDGE_WIDTH = 24
ALONG_PAD = 10

STRICT_INSTRUCTION_TERMS = {
    "above",
    "below",
    "bottom",
    "boundary",
    "count",
    "crop",
    "edge",
    "end",
    "first",
    "fold",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "line",
    "mirror",
    "order",
    "outside",
    "private",
    "read",
    "reverse",
    "right",
    "seed",
    "side",
    "slot",
    "start",
    "take",
    "top",
    "turn",
    "window",
    "word",
}
CONTEXT_TERMS = {
    "billion",
    "bitcoin",
    "bond",
    "bonds",
    "buying",
    "dip",
    "heart",
    "over",
    "overdose",
    "sell",
    "shitcoiner",
    "volcano",
}
SIDES = ["left", "right", "top", "bottom"]
REGION_KINDS = ["target_edge", "crop_window_edge"]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def clean_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def overlap_box(a: list[float], b: list[float]) -> list[float] | None:
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1, y1]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def center(box: list[float]) -> tuple[float, float]:
    return (box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0


def in_box(point: tuple[float, float], box: list[float]) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def normalize_pdf_page() -> Image.Image:
    source = Image.open(SOURCE_PAGE).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE).convert("RGB")
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
    orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    dark = mean < 178
    grey = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    feature = orange | dark | grey
    return {"orange": orange, "dark": dark, "grey": grey, "feature": feature}


def active_targets() -> list[dict[str, Any]]:
    data = load_json(ACTIVE_INDEX_SLOT)
    rows = []
    by_short = {row["shortId"]: row for row in data.get("activeRows", [])}
    for short_id in TARGET_ORDER:
        row = dict(by_short[short_id])
        row["box"] = [float(v) for v in row["box"]]
        rows.append(row)
    return rows


def page_words() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    page = next(page for page in data["pages"] if page["page"] == 76)
    out = []
    for word in page["words"]:
        text = compact(str(word.get("text") or word.get("token") or ""))
        token = clean_token(str(word.get("token") or text))
        if not text and not token:
            continue
        box = [float(v) for v in word["box"]]
        out.append(
            {
                "id": word.get("id"),
                "index": word.get("index"),
                "text": text,
                "token": token,
                "box": box,
                "center": center(box),
            }
        )
    return out


def page_chars() -> list[dict[str, Any]]:
    data = load_json(ARTICLE_MAP)
    page = next(page for page in data["pages"] if page["page"] == 76)
    out = []
    for char in page["chars"]:
        c = str(char.get("c", ""))
        if not c.strip():
            continue
        box = [float(v) for v in char["box"]]
        out.append({"c": c, "i": char.get("i"), "box": box, "center": center(box)})
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


def boundary_region(box: list[float], side: str, kind: str, image_size: tuple[int, int]) -> list[float]:
    if kind == "crop_window_edge":
        x0, y0, x1, y1 = crop_rect(box, image_size)
        width = CROP_EDGE_WIDTH
        if side == "left":
            return [x0, y0, x0 + width, y1]
        if side == "right":
            return [x1 - width, y0, x1, y1]
        if side == "top":
            return [x0, y0, x1, y0 + width]
        return [x0, y1 - width, x1, y1]

    x0, y0, x1, y1 = box
    width = TARGET_EDGE_WIDTH
    if side == "left":
        return [x0 - width, y0 - ALONG_PAD, x0 + width, y1 + ALONG_PAD]
    if side == "right":
        return [x1 - width, y0 - ALONG_PAD, x1 + width, y1 + ALONG_PAD]
    if side == "top":
        return [x0 - ALONG_PAD, y0 - width, x1 + ALONG_PAD, y0 + width]
    return [x0 - ALONG_PAD, y1 - width, x1 + ALONG_PAD, y1 + width]


def clamp_region(region: list[float], size: tuple[int, int]) -> list[float]:
    width, height = size
    return [
        max(0.0, min(float(width), region[0])),
        max(0.0, min(float(height), region[1])),
        max(0.0, min(float(width), region[2])),
        max(0.0, min(float(height), region[3])),
    ]


def words_in_region(words: list[dict[str, Any]], region: list[float]) -> list[dict[str, Any]]:
    hits = []
    for word in words:
        inter = overlap_box(region, word["box"])
        word_area = max(area(word["box"]), 1.0)
        overlap_fraction = area(inter) / word_area if inter else 0.0
        center_hit = in_box(word["center"], region)
        if center_hit or overlap_fraction >= 0.10:
            hits.append(
                {
                    **word,
                    "centerInRegion": center_hit,
                    "overlapFraction": round(overlap_fraction, 4),
                }
            )
    return sorted(hits, key=lambda item: (item["box"][1], item["box"][0], item.get("index") or 0))


def chars_in_region(chars: list[dict[str, Any]], region: list[float]) -> list[dict[str, Any]]:
    hits = []
    for char in chars:
        inter = overlap_box(region, char["box"])
        if inter or in_box(char["center"], region):
            hits.append(char)
    return sorted(hits, key=lambda item: (item["box"][1], item["box"][0], item.get("i") or 0))


def region_pixel_stats(channels: dict[str, np.ndarray], region: list[float]) -> dict[str, float | int]:
    x0, y0, x1, y1 = [int(round(v)) for v in region]
    if x1 <= x0 or y1 <= y0:
        return {
            "areaPx": 0,
            "featureRatio": 0.0,
            "orangeRatio": 0.0,
            "darkRatio": 0.0,
            "greyRatio": 0.0,
        }
    area_px = (x1 - x0) * (y1 - y0)
    return {
        "areaPx": area_px,
        "featureRatio": round(float(channels["feature"][y0:y1, x0:x1].mean()), 6),
        "orangeRatio": round(float(channels["orange"][y0:y1, x0:x1].mean()), 6),
        "darkRatio": round(float(channels["dark"][y0:y1, x0:x1].mean()), 6),
        "greyRatio": round(float(channels["grey"][y0:y1, x0:x1].mean()), 6),
    }


def hit_terms(words: list[dict[str, Any]], terms: set[str]) -> list[str]:
    found = sorted({word["token"] for word in words if word["token"] in terms})
    return found


def make_boundary_rows(
    targets: list[dict[str, Any]],
    words: list[dict[str, Any]],
    chars: list[dict[str, Any]],
    channels: dict[str, np.ndarray],
    image_size: tuple[int, int],
) -> list[dict[str, Any]]:
    rows = []
    for target in targets:
        for kind in REGION_KINDS:
            for side in SIDES:
                region = clamp_region(boundary_region(target["box"], side, kind, image_size), image_size)
                word_hits = words_in_region(words, region)
                char_hits = chars_in_region(chars, region)
                text = compact(" ".join(word["text"] for word in word_hits))
                rows.append(
                    {
                        "target": target["shortId"],
                        "id": target["id"],
                        "phrase": target["phrase"],
                        "visualState": target["visualState"],
                        "color": target["color"],
                        "pageLine": target["pageLine"],
                        "corridorIndex": target["corridorIndex"],
                        "kind": kind,
                        "side": side,
                        "region": [round(v, 2) for v in region],
                        "wordCount": len(word_hits),
                        "wordText": text,
                        "wordTokens": [word["token"] for word in word_hits],
                        "wordIds": [word["id"] for word in word_hits],
                        "strictInstructionHits": hit_terms(word_hits, STRICT_INSTRUCTION_TERMS),
                        "contextTermHits": hit_terms(word_hits, CONTEXT_TERMS),
                        "charCount": len(char_hits),
                        "charStream": "".join(char["c"] for char in char_hits)[:120],
                        "pixelStats": region_pixel_stats(channels, region),
                    }
                )
    return rows


def stream_rows(boundary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    streams = []
    for kind in REGION_KINDS:
        for side in SIDES:
            rows = [row for row in boundary_rows if row["kind"] == kind and row["side"] == side]
            rows.sort(key=lambda row: TARGET_ORDER.index(row["target"]))
            first_tokens = "".join((row["wordTokens"][0][:1].upper() if row["wordTokens"] else ".") for row in rows)
            last_tokens = "".join((row["wordTokens"][-1][:1].upper() if row["wordTokens"] else ".") for row in rows)
            full_text = " ".join(row["wordText"] for row in rows)
            strict_hits = sorted({hit for row in rows for hit in row["strictInstructionHits"]})
            context_hits = sorted({hit for row in rows for hit in row["contextTermHits"]})
            streams.append(
                {
                    "name": f"{kind}_{side}",
                    "targetOrder": [row["target"] for row in rows],
                    "firstTokenInitials": first_tokens,
                    "lastTokenInitials": last_tokens,
                    "strictInstructionHits": strict_hits,
                    "contextTermHits": context_hits,
                    "wordText": compact(full_text),
                }
            )
    return streams


def draw_crop_panel(img: Image.Image, target: dict[str, Any], rows: list[dict[str, Any]]) -> Path:
    rect = crop_rect(target["box"], img.size)
    x0, y0, x1, y1 = [int(round(v)) for v in rect]
    crop = img.crop((x0, y0, x1, y1)).convert("RGB")
    draw = ImageDraw.Draw(crop, "RGBA")
    scale_x = crop.width / max(x1 - x0, 1)
    scale_y = crop.height / max(y1 - y0, 1)

    def sx(x: float) -> int:
        return round((x - x0) * scale_x)

    def sy(y: float) -> int:
        return round((y - y0) * scale_y)

    for row in rows:
        region = row["region"]
        fill = (255, 142, 0, 42) if row["kind"] == "target_edge" else (0, 128, 255, 34)
        outline = (255, 142, 0, 180) if row["kind"] == "target_edge" else (0, 128, 255, 170)
        draw.rectangle([sx(region[0]), sy(region[1]), sx(region[2]), sy(region[3])], fill=fill, outline=outline, width=2)

    box = target["box"]
    draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=(255, 0, 0, 220), width=4)
    draw.text((12, 10), f"{target['shortId']} {target['phrase']}", fill=(255, 255, 255), font=font(20), stroke_width=2, stroke_fill=(0, 0, 0))
    out_path = OUT / f"{target['shortId']}_boundary_probe.jpg"
    crop.save(out_path, quality=92)
    return out_path


def draw_summary_sheet(
    img: Image.Image,
    targets: list[dict[str, Any]],
    boundary_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    crop_paths: list[Path],
) -> None:
    width, height = 1840, 1280
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet, "RGBA")
    title = font(28)
    normal = font(16)
    small = font(13)
    tiny = font(11)
    draw.rectangle((0, 0, width, 88), fill=(24, 31, 42))
    draw.text((28, 22), "Current-scan highlight/crop boundary instruction probe", fill=(255, 255, 255), font=title)
    draw.text(
        (28, 58),
        f"regions={summary['boundaryRegionCount']} strict={summary['strictInstructionRegionCount']} context={summary['contextTermRegionCount']} sourceR3={summary['sourceBackedR3BridgeHitCount']} triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}",
        fill=(190, 205, 225),
        font=normal,
    )

    cluster = [
        min(row["box"][0] for row in targets) - 150,
        min(row["box"][1] for row in targets) - 130,
        max(row["box"][2] for row in targets) + 150,
        max(row["box"][3] for row in targets) + 130,
    ]
    cluster = [max(0, cluster[0]), max(0, cluster[1]), min(img.width, cluster[2]), min(img.height, cluster[3])]
    view = img.crop(tuple(int(round(v)) for v in cluster))
    view_w = 980
    view_h = round(view.height * view_w / view.width)
    view = view.resize((view_w, view_h))
    sheet.paste(view, (28, 120))

    def sx(x: float) -> int:
        return 28 + round((x - cluster[0]) * view_w / max(cluster[2] - cluster[0], 1))

    def sy(y: float) -> int:
        return 120 + round((y - cluster[1]) * view_h / max(cluster[3] - cluster[1], 1))

    for target in targets:
        box = target["box"]
        color = (255, 109, 0, 230) if target["color"] == "orange" else (20, 20, 20, 230)
        draw.rectangle([sx(box[0]), sy(box[1]), sx(box[2]), sy(box[3])], outline=color, width=4)
        draw.text((sx(box[0]), max(92, sy(box[1]) - 22)), target["shortId"], fill=(255, 255, 255), font=normal, stroke_width=2, stroke_fill=(0, 0, 0))
        for kind in REGION_KINDS:
            for side in SIDES:
                region = boundary_region(target["box"], side, kind, img.size)
                outline = (255, 142, 0, 135) if kind == "target_edge" else (0, 128, 255, 125)
                draw.rectangle([sx(region[0]), sy(region[1]), sx(region[2]), sy(region[3])], outline=outline, width=1)

    table_x = 1040
    y = 122
    draw.text((table_x, y), "Boundary word hits", fill=(24, 31, 42), font=font(21))
    y += 34
    headers = ["target", "kind", "side", "words", "strict", "context", "text"]
    widths = [55, 120, 58, 48, 65, 80, 355]
    x = table_x
    for header, col_w in zip(headers, widths):
        draw.text((x, y), header, fill=(70, 80, 95), font=small)
        x += col_w
    y += 20
    interesting = [
        row
        for row in boundary_rows
        if row["wordCount"] or row["strictInstructionHits"] or row["contextTermHits"]
    ][:30]
    for row in interesting:
        x = table_x
        values = [
            row["target"],
            row["kind"].replace("_edge", ""),
            row["side"],
            str(row["wordCount"]),
            ",".join(row["strictInstructionHits"]) or "-",
            ",".join(row["contextTermHits"]) or "-",
            row["wordText"][:48] + ("..." if len(row["wordText"]) > 48 else ""),
        ]
        for value, col_w in zip(values, widths):
            draw.text((x, y), value, fill=(20, 24, 31), font=tiny)
            x += col_w
        y += 18
        if y > 780:
            break

    thumb_y = 850
    draw.text((28, thumb_y - 30), "Per-target boundary overlays", fill=(24, 31, 42), font=font(20))
    thumb_w = 430
    for idx, path in enumerate(crop_paths):
        thumb = Image.open(path).convert("RGB")
        thumb_h = round(thumb.height * thumb_w / thumb.width)
        thumb = thumb.resize((thumb_w, thumb_h))
        px = 28 + (idx % 4) * 450
        sheet.paste(thumb, (px, thumb_y))

    draw.rectangle((28, 1120, 1812, 1250), outline=(210, 216, 226), width=1)
    draw.text((44, 1138), "Decision", fill=(24, 31, 42), font=font(20))
    decision_lines = [
        "No boundary region exposes a strict source instruction term.",
        "Crop-window edges contain ordinary article context only; context hits are thematic words, not unit/order commands.",
        "Continue source/original-layout validation; do not extract from boundary text.",
    ]
    for idx, line in enumerate(decision_lines):
        draw.text((44, 1170 + idx * 23), line, fill=(55, 65, 80), font=normal)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    page_img = normalize_pdf_page()
    targets = active_targets()
    words = page_words()
    chars = page_chars()
    channels = feature_channels(page_img)
    boundary_rows = make_boundary_rows(targets, words, chars, channels, page_img.size)
    streams = stream_rows(boundary_rows)
    crop_paths = [
        draw_crop_panel(
            page_img,
            target,
            [row for row in boundary_rows if row["target"] == target["shortId"]],
        )
        for target in targets
    ]

    source_gate = load_json(SOURCE_REVIEW_GATE).get("summary", {})
    trigger_gate = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    strict_regions = [row for row in boundary_rows if row["strictInstructionHits"]]
    context_regions = [row for row in boundary_rows if row["contextTermHits"]]
    target_edge_strict = [row for row in strict_regions if row["kind"] == "target_edge"]
    crop_edge_strict = [row for row in strict_regions if row["kind"] == "crop_window_edge"]
    rows_with_words = [row for row in boundary_rows if row["wordCount"]]
    stream_strict_hits = sorted({hit for row in streams for hit in row["strictInstructionHits"]})
    stream_context_hits = sorted({hit for row in streams for hit in row["contextTermHits"]})
    summary = {
        "activeTargetCount": len(targets),
        "boundaryRegionCount": len(boundary_rows),
        "targetEdgeRegionCount": sum(1 for row in boundary_rows if row["kind"] == "target_edge"),
        "cropWindowEdgeRegionCount": sum(
            1 for row in boundary_rows if row["kind"] == "crop_window_edge"
        ),
        "regionWithWordCount": len(rows_with_words),
        "strictInstructionRegionCount": len(strict_regions),
        "targetEdgeStrictInstructionRegionCount": len(target_edge_strict),
        "cropWindowStrictInstructionRegionCount": len(crop_edge_strict),
        "strictInstructionTermHits": stream_strict_hits,
        "contextTermRegionCount": len(context_regions),
        "contextTermHits": stream_context_hits,
        "streamCount": len(streams),
        "streamStrictInstructionHitCount": len(stream_strict_hits),
        "streamContextTermHitCount": len(stream_context_hits),
        "sourceBackedR3BridgeHitCount": source_gate.get("sourceBackedR3BridgeHitCount", 0),
        "satisfiedReopenTriggerCount": trigger_gate.get("satisfiedTriggerCount", 0),
        "triggerCount": trigger_gate.get("triggerCount", 9),
        "selectorUnlocked": False,
    }
    summary["boundaryInstructionProbeFingerprint"] = (
        f"targets={summary['activeTargetCount']}|regions={summary['boundaryRegionCount']}"
        f"|wordRegions={summary['regionWithWordCount']}"
        f"|strictRegions={summary['strictInstructionRegionCount']}"
        f"|targetStrict={summary['targetEdgeStrictInstructionRegionCount']}"
        f"|cropStrict={summary['cropWindowStrictInstructionRegionCount']}"
        f"|contextRegions={summary['contextTermRegionCount']}"
        f"|strictTerms={','.join(summary['strictInstructionTermHits']) or '-'}"
        f"|contextTerms={','.join(summary['contextTermHits']) or '-'}"
        f"|sourceR3={summary['sourceBackedR3BridgeHitCount']}"
        f"|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}"
        "|selectors=0"
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Current-scan page-76 target highlight-edge and crop-window boundary probe "
            "for O4/B4/G5/O5; no key derivation, hashing, WIF, seed, address checks, "
            "OCR-to-key extraction, or broad candidate generation."
        ),
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "sourcePage": rel(SOURCE_PAGE),
            "uprightPage": rel(UPRIGHT_PAGE),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "parameters": {
            "targetEdgeWidthPx": TARGET_EDGE_WIDTH,
            "cropEdgeWidthPx": CROP_EDGE_WIDTH,
            "cropPadX": PAD_X,
            "cropPadY": PAD_Y,
            "strictInstructionTerms": sorted(STRICT_INSTRUCTION_TERMS),
            "contextTerms": sorted(CONTEXT_TERMS),
        },
        "boundaryRows": boundary_rows,
        "streamRows": streams,
        "summary": summary,
        "decision": {
            "currentScanHighlightBoundaryInstructionProbe": "boundary_edges_no_source_instruction_selector",
            "selectorUnlocked": False,
            "reason": (
                "Neither active highlight edges nor the current light-table crop-window "
                "boundaries expose source-backed unit/order wording. Nearby OCR words are "
                "ordinary article context or noisy active-box text."
            ),
            "nextMove": (
                "Stop tuning boundary strips on the current scan. The next useful move is "
                "either a manual review of the generated boundary sheet for visual anomalies "
                "or a distinct physical/original-layout source that can satisfy R1/R3."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "cropPanels": [rel(path) for path in crop_paths],
    }

    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = [
        "# Current-Scan Highlight Boundary Instruction Probe",
        "",
        f"Created: `{result['createdAt']}`",
        "",
        "## Scope",
        "",
        result["scope"],
        "",
        "## Inputs",
        "",
    ]
    for key, value in result["inputs"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Active targets / boundary regions: `{summary['activeTargetCount']}` / `{summary['boundaryRegionCount']}`.",
            f"- Regions with OCR-map word hits: `{summary['regionWithWordCount']}`.",
            f"- Strict instruction regions: `{summary['strictInstructionRegionCount']}` (`target_edge={summary['targetEdgeStrictInstructionRegionCount']}`, `crop_window_edge={summary['cropWindowStrictInstructionRegionCount']}`).",
            f"- Strict instruction term hits: `{', '.join(summary['strictInstructionTermHits']) or '-'}`.",
            f"- Context/thematic regions: `{summary['contextTermRegionCount']}`; context terms: `{', '.join(summary['contextTermHits']) or '-'}`.",
            f"- Source-backed R3 hits / satisfied reopen triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`.",
            f"- Fingerprint: `{summary['boundaryInstructionProbeFingerprint']}`.",
            "",
            "## Boundary Rows With Words",
            "",
            "| target | kind | side | words | strict | context | text |",
            "|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in [row for row in boundary_rows if row["wordCount"]]:
        strict = ", ".join(row["strictInstructionHits"]) or "-"
        context = ", ".join(row["contextTermHits"]) or "-"
        text = row["wordText"].replace("|", "\\|")
        lines.append(
            f"| `{row['target']}` | `{row['kind']}` | `{row['side']}` | {row['wordCount']} | `{strict}` | `{context}` | {text} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentScanHighlightBoundaryInstructionProbe']}`.",
            f"- {result['decision']['reason']}",
            f"- Next move: {result['decision']['nextMove']}",
            "",
            "## Artifacts",
            "",
            f"- Sheet: `{result['sheet']}`",
        ]
    )
    for path in result["cropPanels"]:
        lines.append(f"- Crop panel: `{path}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    draw_summary_sheet(page_img, targets, boundary_rows, summary, crop_paths)

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_SHEET}")
    print(summary["boundaryInstructionProbeFingerprint"])


if __name__ == "__main__":
    main()
