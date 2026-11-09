#!/usr/bin/env python3
"""Trace valid same-leaf projected source line bands over active targets.

This bounded pass keeps the physically valid page 75 -> page 76 held-to-light
model and projects page-75 OCR line bands through the mirrored leaf transform
onto page 76. It asks whether whole source text lines, rather than individual
word boxes, line up with O4/B4/G5/O5 target bands in a way that supplies
instruction, unit, context, or order language. No candidate derivation,
hashing, seed/WIF/address checks, or broad search is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_line_band_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_line_band_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_line_band_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_line_band_trace_sheet.jpg"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
ARTICLE_MAP = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

TARGET_ORDER = ["O4", "B4", "G5", "O5"]
MODES = [
    ("valid_75_to_76_natural", 0, 0),
    ("valid_75_to_76_small_jitter_best", -80, -20),
]
LINE_Y_THRESHOLD = 31.0
TARGET_PAD_X = 28
TARGET_PAD_Y = 52
PANEL_PAD_X = 260
PANEL_PAD_Y = 180

STRICT_TERMS = {
    "read",
    "reads",
    "reading",
    "take",
    "takes",
    "taking",
    "use",
    "using",
    "select",
    "extract",
    "decode",
    "encoded",
    "cipher",
    "key",
    "private",
    "seed",
    "line",
    "lines",
    "word",
    "words",
    "phrase",
    "phrases",
    "letter",
    "letters",
    "edge",
    "edges",
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "fold",
    "folded",
    "mirror",
    "mirrored",
    "reverse",
    "order",
    "slot",
    "slots",
    "index",
    "indexes",
    "font",
    "bold",
    "highlight",
    "overdose",
}
CONTEXT_TERMS = {
    "bitcoin",
    "bitcoins",
    "satoshi",
    "salvador",
    "bukele",
    "imf",
    "volcano",
    "volcanoes",
    "bond",
    "bonds",
    "shitcoiner",
    "shitcoiners",
    "heart",
    "dip",
    "sell",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def norm_token(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


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
    source = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean)
    return source.rotate(180) if rot_diff < same_diff else source


def box_union(boxes: list[list[float]]) -> list[float]:
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    ]


def center_y(box: list[float]) -> float:
    return (box[1] + box[3]) / 2


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection_area(a: list[float], b: list[float]) -> float:
    if not boxes_intersect(a, b):
        return 0.0
    return (min(a[2], b[2]) - max(a[0], b[0])) * (min(a[3], b[3]) - max(a[1], b[1]))


def padded_box(box: list[float], size: tuple[int, int], pad_x: int, pad_y: int) -> list[float]:
    w, h = size
    return [
        max(0.0, box[0] - pad_x),
        max(0.0, box[1] - pad_y),
        min(float(w), box[2] + pad_x),
        min(float(h), box[3] + pad_y),
    ]


def line_groups(words: list[dict]) -> list[dict]:
    normalized = [word for word in words if norm_token(word.get("text", ""))]
    normalized.sort(key=lambda word: (center_y(word["box"]), word["box"][0]))
    groups: list[list[dict]] = []
    for word in normalized:
        if not groups:
            groups.append([word])
            continue
        current_y = sum(center_y(item["box"]) for item in groups[-1]) / len(groups[-1])
        if abs(center_y(word["box"]) - current_y) <= LINE_Y_THRESHOLD:
            groups[-1].append(word)
        else:
            groups.append([word])

    lines = []
    for idx, group in enumerate(groups):
        group.sort(key=lambda word: word["box"][0])
        tokens = [norm_token(word.get("text", "")) for word in group if norm_token(word.get("text", ""))]
        box = box_union([word["box"] for word in group])
        lines.append(
            {
                "lineIndex": idx,
                "box": box,
                "center": [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2],
                "text": " ".join(word.get("text", "") for word in group),
                "tokens": tokens,
                "words": [
                    {
                        "id": word.get("id"),
                        "index": word.get("index"),
                        "text": word.get("text", ""),
                        "token": norm_token(word.get("text", "")),
                        "box": word.get("box"),
                    }
                    for word in group
                ],
            }
        )
    return lines


def transform_line_to_target(line: dict, page_width: int, dx: int, dy: int) -> dict:
    x0, y0, x1, y1 = line["box"]
    target_box = [page_width - x1 + dx, y0 + dy, page_width - x0 + dx, y1 + dy]
    words = []
    for word in line["words"]:
        wx0, wy0, wx1, wy1 = word["box"]
        words.append(
            {
                **word,
                "targetBox": [page_width - wx1 + dx, wy0 + dy, page_width - wx0 + dx, wy1 + dy],
            }
        )
    tokens = line["tokens"]
    return {
        "lineIndex": line["lineIndex"],
        "sourceBox": line["box"],
        "targetBox": target_box,
        "sourceText": line["text"],
        "tokens": tokens,
        "strictInstructionTerms": sorted({token for token in tokens if token in STRICT_TERMS}),
        "contextTerms": sorted({token for token in tokens if token in CONTEXT_TERMS}),
        "words": words,
    }


def line_terms(lines: list[dict], key: str) -> list[str]:
    terms: set[str] = set()
    for line in lines:
        terms.update(line.get(key, []))
    return sorted(terms)


def target_terms(lines: list[dict], term_set: set[str]) -> list[str]:
    terms: set[str] = set()
    for line in lines:
        terms.update(token for token in line.get("tokens", []) if token in term_set)
    return sorted(terms)


def draw_panel(
    target_img: Image.Image,
    active_row: dict,
    mode: str,
    dx: int,
    dy: int,
    target_lines: list[dict],
    source_lines: list[dict],
    out_path: Path,
) -> None:
    crop = padded_box(active_row["box"], target_img.size, PANEL_PAD_X, PANEL_PAD_Y)
    crop_i = [round(v) for v in crop]
    image = target_img.crop(tuple(crop_i)).convert("RGB")
    target_w = 760
    resized = image.resize((target_w, round(target_w * image.height / image.width)))
    canvas = Image.new("RGB", (target_w, resized.height + 98), "white")
    canvas.paste(resized, (0, 98))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 0, canvas.width, 82), fill=(25, 31, 42, 235))
    source_preview = " / ".join(line["sourceText"][:52] for line in source_lines[:2]) or "-"
    target_preview = " / ".join(line["text"][:40] for line in target_lines[:2]) or "-"
    draw.text(
        (12, 10),
        f"{mode.replace('valid_75_to_76_', '')} / {active_row['shortId']} dx={dx} dy={dy}",
        fill="white",
        font=font(16),
    )
    draw.text((12, 38), f"target: {target_preview}", fill=(225, 232, 242), font=font(11))
    draw.text((12, 57), f"source: {source_preview}", fill=(225, 232, 242), font=font(11))

    def sx(value: float) -> float:
        return (value - crop[0]) * target_w / (crop[2] - crop[0])

    def sy(value: float) -> float:
        return 98 + (value - crop[1]) * resized.height / (crop[3] - crop[1])

    ax0, ay0, ax1, ay1 = active_row["box"]
    draw.rectangle((sx(ax0), sy(ay0), sx(ax1), sy(ay1)), outline=(255, 0, 0, 235), width=3)
    for line in target_lines:
        x0, y0, x1, y1 = line["box"]
        draw.rectangle((sx(x0), sy(y0), sx(x1), sy(y1)), outline=(255, 128, 0, 220), width=2)
    for line in source_lines:
        x0, y0, x1, y1 = line["targetBox"]
        color = (0, 105, 255, 210)
        if line["strictInstructionTerms"]:
            color = (255, 0, 0, 240)
        draw.rectangle((sx(x0), sy(y0), sx(x1), sy(y1)), outline=color, width=2)

    draw.rectangle((514, 52, 528, 66), fill=(255, 128, 0, 165))
    draw.text((534, 50), "p76 line", fill=(238, 241, 246), font=font(11))
    draw.rectangle((606, 52, 620, 66), fill=(0, 105, 255, 165))
    draw.text((626, 50), "p75 projected", fill=(238, 241, 246), font=font(11))
    canvas.save(out_path, quality=92)


def draw_sheet(result: dict, panel_paths: list[Path]) -> None:
    width, height = 1840, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Valid Leaf Line-Band Trace", fill="white", font=font(26))
    draw.text(
        (24, 56),
        "Projected page-75 OCR lines over O4/B4/G5/O5 bands under the valid page 75 -> page 76 leaf.",
        fill=(235, 235, 235),
        font=font(14),
    )
    cards = [
        ("rows", result["summary"]["traceRowCount"]),
        ("source rows", result["summary"]["sourceLineRows"]),
        ("source lines", result["summary"]["totalSourceLineHits"]),
        ("overlap rows", result["summary"]["lineOverlapRows"]),
        ("strict/context", f"{result['summary']['totalStrictInstructionHits']}/{result['summary']['totalContextTermHits']}"),
        ("R3/triggers", f"{result['summary']['sourceBackedR3BridgeHitCount']}/{result['summary']['satisfiedReopenTriggerCount']}/{result['summary']['triggerCount']}"),
    ]
    x, y = 24, 118
    for label, value in cards:
        draw.rounded_rectangle((x, y, x + 278, y + 70), radius=6, fill=(246, 248, 250), outline=(208, 215, 222))
        draw.text((x + 12, y + 10), label, fill=(80, 86, 96), font=font(11))
        draw.text((x + 12, y + 34), str(value), fill=(22, 26, 34), font=font(18))
        x += 296
    x, y = 24, 216
    for path in panel_paths[:8]:
        img = Image.open(path).convert("RGB").resize((430, 250))
        sheet.paste(img, (x, y))
        x += 448
        if x + 430 > width:
            x = 24
            y += 292
    y = 850
    headers = ["mode", "target", "source lines", "overlap", "strict", "context", "source text"]
    xs = [24, 220, 292, 382, 460, 526, 610]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=font(11))
    y += 22
    for row in result["traceRows"][:12]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            str(row["sourceLineHitCount"]),
            str(row["sourceTargetLineOverlapCount"]),
            str(row["strictInstructionHitCount"]),
            str(row["contextTermHitCount"]),
            row["sourceTextPreview"][:92],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value), fill=(35, 35, 35), font=font(11))
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    article = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    target_img = normalize_page(76)
    page_width = target_img.width

    page75_words: list[dict] = []
    page76_words: list[dict] = []
    for page in article.get("pages", []):
        if page.get("page") == 75:
            page75_words = page.get("words", [])
        if page.get("page") == 76:
            page76_words = page.get("words", [])
    page75_lines = line_groups(page75_words)
    page76_lines = line_groups(page76_words)
    active_rows = [
        {
            "shortId": row["shortId"],
            "phrase": row["phrase"],
            "box": row["box"],
        }
        for row in active.get("activeRows", [])
        if row.get("shortId") in TARGET_ORDER
    ]
    active_rows = sorted(active_rows, key=lambda row: TARGET_ORDER.index(row["shortId"]))

    trace_rows = []
    panel_paths: list[Path] = []
    for mode, dx, dy in MODES:
        projected_source_lines = [
            transform_line_to_target(line, page_width, dx, dy) for line in page75_lines
        ]
        for active_row in active_rows:
            target_band = padded_box(active_row["box"], target_img.size, TARGET_PAD_X, TARGET_PAD_Y)
            target_lines = [line for line in page76_lines if boxes_intersect(line["box"], target_band)]
            source_lines = [
                line for line in projected_source_lines if boxes_intersect(line["targetBox"], target_band)
            ]
            overlap_count = 0
            overlap_area = 0.0
            for source_line in source_lines:
                for target_line in target_lines:
                    area = intersection_area(source_line["targetBox"], target_line["box"])
                    if area > 0:
                        overlap_count += 1
                        overlap_area += area
            strict_terms = line_terms(source_lines, "strictInstructionTerms")
            context_terms = line_terms(source_lines, "contextTerms")
            target_context_terms = target_terms(target_lines, CONTEXT_TERMS)
            row = {
                "mode": mode,
                "dx": dx,
                "dy": dy,
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                "targetLineHitCount": len(target_lines),
                "sourceLineHitCount": len(source_lines),
                "sourceTargetLineOverlapCount": overlap_count,
                "sourceTargetLineOverlapArea": overlap_area,
                "strictInstructionHitCount": len(strict_terms),
                "contextTermHitCount": len(context_terms),
                "targetContextTermHitCount": len(target_context_terms),
                "strictInstructionTerms": strict_terms,
                "contextTerms": context_terms,
                "targetContextTerms": target_context_terms,
                "targetTextPreview": " / ".join(line["text"] for line in target_lines),
                "sourceTextPreview": " / ".join(line["sourceText"] for line in source_lines),
                "targetLines": target_lines[:10],
                "sourceLines": source_lines[:10],
            }
            panel_path = OUT / f"{mode}_{active_row['shortId']}_line_band.jpg"
            draw_panel(
                target_img,
                active_row,
                mode,
                dx,
                dy,
                target_lines,
                source_lines,
                panel_path,
            )
            row["panel"] = rel(panel_path)
            trace_rows.append(row)
            panel_paths.append(panel_path)

    satisfied_triggers = sum(1 for row in reopen.get("triggerRows", []) if row.get("triggerSatisfiedNow"))
    trigger_count = len(reopen.get("triggerRows", []))
    source_backed_r3 = 0
    selector_unlocks = 0
    summary = {
        "traceRowCount": len(trace_rows),
        "sourceLineRows": sum(1 for row in trace_rows if row["sourceLineHitCount"]),
        "targetLineRows": sum(1 for row in trace_rows if row["targetLineHitCount"]),
        "lineOverlapRows": sum(1 for row in trace_rows if row["sourceTargetLineOverlapCount"]),
        "totalSourceLineHits": sum(row["sourceLineHitCount"] for row in trace_rows),
        "totalTargetLineHits": sum(row["targetLineHitCount"] for row in trace_rows),
        "totalSourceTargetLineOverlaps": sum(row["sourceTargetLineOverlapCount"] for row in trace_rows),
        "strictInstructionRows": sum(1 for row in trace_rows if row["strictInstructionHitCount"]),
        "contextTermRows": sum(1 for row in trace_rows if row["contextTermHitCount"]),
        "totalStrictInstructionHits": sum(row["strictInstructionHitCount"] for row in trace_rows),
        "totalContextTermHits": sum(row["contextTermHitCount"] for row in trace_rows),
        "sourceBackedR3BridgeHitCount": source_backed_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlockCount": selector_unlocks,
    }
    fingerprint = (
        f"modes={len(MODES)}|targets={len(active_rows) * len(MODES)}|"
        f"sourceRows={summary['sourceLineRows']}|overlapRows={summary['lineOverlapRows']}|"
        f"sourceLines={summary['totalSourceLineHits']}|targetLines={summary['totalTargetLineHits']}|"
        f"overlaps={summary['totalSourceTargetLineOverlaps']}|strictRows={summary['strictInstructionRows']}|"
        f"contextRows={summary['contextTermRows']}|strict={summary['totalStrictInstructionHits']}|"
        f"context={summary['totalContextTermHits']}|sourceR3={source_backed_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page 75 -> page 76 source line-band trace around O4/B4/G5/O5; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": "valid_leaf_line_band_trace_no_instruction_source",
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Do not extract from valid-leaf projected source line bands; require source/clue wording that names transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Line-Band Trace",
        "",
        "Scope: projected page-75 OCR line bands through the physically valid page 75 -> page 76 held-to-light transform, then checked whether they line up with O4/B4/G5/O5 target bands as instruction, unit, context, or order language. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Rows / source-line rows / line-overlap rows: `{summary['traceRowCount']}` / `{summary['sourceLineRows']}` / `{summary['lineOverlapRows']}`",
        f"- Source lines / target lines / source-target overlaps: `{summary['totalSourceLineHits']}` / `{summary['totalTargetLineHits']}` / `{summary['totalSourceTargetLineOverlaps']}`",
        f"- Strict instruction rows / context rows: `{summary['strictInstructionRows']}` / `{summary['contextTermRows']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_backed_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Target Rows",
        "",
        "| mode | target | target text | source text | overlaps | strict | context | panel |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in trace_rows:
        lines.append(
            "| `{mode}` | `{target}` | {target_text} | {source_text} | {overlaps} | {strict} | {context} | `{panel}` |".format(
                mode=row["mode"],
                target=row["target"],
                target_text=row["targetTextPreview"].replace("|", "/")[:85] or "",
                source_text=row["sourceTextPreview"].replace("|", "/")[:110] or "",
                overlaps=row["sourceTargetLineOverlapCount"],
                strict=row["strictInstructionHitCount"],
                context=row["contextTermHitCount"],
                panel=row["panel"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `valid_leaf_line_band_trace_no_instruction_source`",
            "- Projected source line bands that reach the active target bands are ordinary page-75 prose and do not supply source-backed instruction, unit, or order wording.",
            "- Line-band overlaps do not satisfy any source-backed R3 or reopen trigger.",
            "- Keep this as the line-level held-to-light stop-check for the current valid leaf.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
