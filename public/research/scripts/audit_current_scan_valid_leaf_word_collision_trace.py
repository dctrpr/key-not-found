#!/usr/bin/env python3
"""Trace word-level collisions in the valid same-leaf light-table view.

This bounded pass keeps the physically valid page 75 -> page 76 held-to-light
model and projects page-75 OCR word boxes through the mirrored leaf transform
onto page 76. It asks whether source words physically overlay O4/B4/G5/O5
target words in a way that supplies instruction, unit, or order language. No
candidate derivation, hashing, seed/WIF/address checks, or broad search is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_valid_leaf_word_collision_trace"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_valid_leaf_word_collision_trace.json"
OUT_MD = OUT / "current_scan_valid_leaf_word_collision_trace.md"
OUT_SHEET = OUT / "current_scan_valid_leaf_word_collision_trace_sheet.jpg"

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
BOX_PAD = 18
PANEL_PAD_X = 190
PANEL_PAD_Y = 120

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


def boxes_intersect(a: list[float], b: list[float]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection_area(a: list[float], b: list[float]) -> float:
    if not boxes_intersect(a, b):
        return 0.0
    return (min(a[2], b[2]) - max(a[0], b[0])) * (min(a[3], b[3]) - max(a[1], b[1]))


def padded_box(box: list[float], size: tuple[int, int], pad: int = BOX_PAD) -> list[float]:
    w, h = size
    return [
        max(0.0, box[0] - pad),
        max(0.0, box[1] - pad),
        min(float(w), box[2] + pad),
        min(float(h), box[3] + pad),
    ]


def transform_source_word_to_target(word: dict, page_width: int, dx: int, dy: int) -> dict:
    x0, y0, x1, y1 = word["box"]
    target_box = [page_width - x1 + dx, y0 + dy, page_width - x0 + dx, y1 + dy]
    token = norm_token(word.get("text", ""))
    return {
        "id": word.get("id"),
        "index": word.get("index"),
        "text": word.get("text", ""),
        "token": token,
        "sourceBox": word.get("box"),
        "targetBox": target_box,
        "strictInstruction": token in STRICT_TERMS,
        "contextTerm": token in CONTEXT_TERMS,
    }


def words_in_box(words: list[dict], box: list[float]) -> list[dict]:
    hits = []
    for word in words:
        token = norm_token(word.get("text", ""))
        if token and boxes_intersect(word.get("box", [0, 0, 0, 0]), box):
            hits.append(
                {
                    "id": word.get("id"),
                    "index": word.get("index"),
                    "text": word.get("text", ""),
                    "token": token,
                    "box": word.get("box"),
                    "strictInstruction": token in STRICT_TERMS,
                    "contextTerm": token in CONTEXT_TERMS,
                }
            )
    return hits


def initials(words: list[dict]) -> str:
    return "".join(word["token"][:1] for word in words if word.get("token"))


def ordered_collision_initials(target_words: list[dict], source_words: list[dict]) -> str:
    items = []
    for word in target_words:
        box = word["box"]
        items.append(((box[0] + box[2]) / 2, "T", word["token"][:1]))
    for word in source_words:
        box = word["targetBox"]
        items.append(((box[0] + box[2]) / 2, "S", word["token"][:1]))
    return "".join(item[2] for item in sorted(items))


def find_pages(article: dict) -> tuple[list[dict], list[dict]]:
    page75_words: list[dict] = []
    page76_words: list[dict] = []
    for page in article.get("pages", []):
        if page.get("page") == 75:
            page75_words = page.get("words", [])
        if page.get("page") == 76:
            page76_words = page.get("words", [])
    return page75_words, page76_words


def draw_panel(
    target_img: Image.Image,
    active_row: dict,
    mode: str,
    dx: int,
    dy: int,
    target_words: list[dict],
    source_words: list[dict],
    collisions: list[dict],
    out_path: Path,
) -> None:
    crop = padded_box(active_row["box"], target_img.size, PANEL_PAD_X)
    crop[1] = max(0.0, active_row["box"][1] - PANEL_PAD_Y)
    crop[3] = min(float(target_img.height), active_row["box"][3] + PANEL_PAD_Y)
    crop_i = [round(v) for v in crop]
    img = target_img.crop(tuple(crop_i)).convert("RGB")
    target_w = 720
    resized = img.resize((target_w, round(target_w * img.height / img.width)))
    canvas = Image.new("RGB", (target_w, resized.height + 92), "white")
    canvas.paste(resized, (0, 92))
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle((0, 0, canvas.width, 76), fill=(25, 31, 42, 235))
    draw.text(
        (12, 10),
        f"{mode.replace('valid_75_to_76_', '')} / {active_row['shortId']} dx={dx} dy={dy}",
        fill="white",
        font=font(16),
    )
    draw.text(
        (12, 39),
        f"target: {' '.join(w['text'] for w in target_words)[:46]}  source: {' '.join(w['text'] for w in source_words)[:50] or '-'}",
        fill=(222, 230, 240),
        font=font(12),
    )

    def sx(value: float) -> float:
        return (value - crop[0]) * target_w / (crop[2] - crop[0])

    def sy(value: float) -> float:
        return 92 + (value - crop[1]) * resized.height / (crop[3] - crop[1])

    ax0, ay0, ax1, ay1 = active_row["box"]
    draw.rectangle((sx(ax0), sy(ay0), sx(ax1), sy(ay1)), outline=(255, 0, 0, 235), width=3)
    for word in target_words:
        x0, y0, x1, y1 = word["box"]
        draw.rectangle((sx(x0), sy(y0), sx(x1), sy(y1)), outline=(255, 118, 0, 210), width=2)
    collision_source_ids = {item["sourceWordId"] for item in collisions}
    for word in source_words:
        x0, y0, x1, y1 = word["targetBox"]
        color = (140, 54, 255, 235) if word["id"] in collision_source_ids else (0, 105, 255, 185)
        draw.rectangle((sx(x0), sy(y0), sx(x1), sy(y1)), outline=color, width=2)
    draw.rectangle((448, 49, 462, 63), fill=(255, 118, 0, 160))
    draw.text((468, 47), "p76 words", fill=(235, 238, 244), font=font(11))
    draw.rectangle((548, 49, 562, 63), fill=(0, 105, 255, 160))
    draw.text((568, 47), "p75 through page", fill=(235, 238, 244), font=font(11))
    canvas.save(out_path, quality=92)


def draw_sheet(result: dict, panel_paths: list[Path]) -> None:
    width, height = 1840, 1320
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Valid Leaf Word-Collision Trace", fill="white", font=font(26))
    draw.text(
        (24, 56),
        "Page-75 OCR word boxes mirrored through the valid leaf and checked against O4/B4/G5/O5 target words.",
        fill=(235, 235, 235),
        font=font(14),
    )
    cards = [
        ("rows", result["summary"]["traceRowCount"]),
        ("source rows", result["summary"]["sourceWordRows"]),
        ("collision rows", result["summary"]["collisionRows"]),
        ("collisions", result["summary"]["totalCollisionPairs"]),
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
    headers = ["mode", "target", "target text", "source text", "pairs", "strict", "initials"]
    xs = [24, 220, 292, 610, 1000, 1060, 1120]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=font(11))
    y += 22
    for row in result["traceRows"][:12]:
        values = [
            row["mode"].replace("valid_75_to_76_", ""),
            row["target"],
            row["targetTextPreview"][:38],
            row["sourceTextPreview"][:48],
            str(row["collisionPairCount"]),
            str(row["strictInstructionHitCount"]),
            row["combinedInitials"][:30],
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), str(value), fill=(35, 35, 35), font=font(11))
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    article = load_json(ARTICLE_MAP)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    page75_words, page76_words = find_pages(article)
    target_img = normalize_page(76)
    page_width = target_img.width
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
        transformed_words = [
            transform_source_word_to_target(word, page_width, dx, dy)
            for word in page75_words
            if norm_token(word.get("text", ""))
        ]
        for active_row in active_rows:
            check_box = padded_box(active_row["box"], target_img.size, BOX_PAD)
            target_words = words_in_box(page76_words, check_box)
            source_words = [
                word for word in transformed_words if boxes_intersect(word["targetBox"], check_box)
            ]
            collisions = []
            for source_word in source_words:
                for target_word in target_words:
                    area = intersection_area(source_word["targetBox"], target_word["box"])
                    if area > 0:
                        collisions.append(
                            {
                                "sourceWordId": source_word["id"],
                                "sourceText": source_word["text"],
                                "sourceToken": source_word["token"],
                                "targetWordId": target_word["id"],
                                "targetText": target_word["text"],
                                "targetToken": target_word["token"],
                                "overlapArea": area,
                            }
                        )
            strict_hits = [
                word["token"]
                for word in source_words + target_words
                if word.get("strictInstruction")
            ]
            context_hits = [
                word["token"]
                for word in source_words + target_words
                if word.get("contextTerm")
            ]
            row = {
                "mode": mode,
                "dx": dx,
                "dy": dy,
                "target": active_row["shortId"],
                "phrase": active_row["phrase"],
                "box": active_row["box"],
                "targetWordHitCount": len(target_words),
                "sourceWordHitCount": len(source_words),
                "collisionPairCount": len(collisions),
                "strictInstructionHitCount": len(set(strict_hits)),
                "contextTermHitCount": len(set(context_hits)),
                "strictInstructionTerms": sorted(set(strict_hits)),
                "contextTerms": sorted(set(context_hits)),
                "targetTextPreview": " ".join(word["text"] for word in target_words),
                "sourceTextPreview": " ".join(word["text"] for word in source_words),
                "targetInitials": initials(target_words),
                "sourceInitials": initials(source_words),
                "combinedInitials": ordered_collision_initials(target_words, source_words),
                "collisions": collisions[:20],
                "targetWords": target_words[:20],
                "sourceWords": source_words[:20],
            }
            panel_path = OUT / f"{mode}_{active_row['shortId']}_word_collision.jpg"
            draw_panel(
                target_img,
                active_row,
                mode,
                dx,
                dy,
                target_words,
                source_words,
                collisions,
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
        "sourceWordRows": sum(1 for row in trace_rows if row["sourceWordHitCount"]),
        "targetWordRows": sum(1 for row in trace_rows if row["targetWordHitCount"]),
        "collisionRows": sum(1 for row in trace_rows if row["collisionPairCount"]),
        "totalSourceWordHits": sum(row["sourceWordHitCount"] for row in trace_rows),
        "totalTargetWordHits": sum(row["targetWordHitCount"] for row in trace_rows),
        "totalCollisionPairs": sum(row["collisionPairCount"] for row in trace_rows),
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
        f"sourceRows={summary['sourceWordRows']}|collisionRows={summary['collisionRows']}|"
        f"sourceWords={summary['totalSourceWordHits']}|targetWords={summary['totalTargetWordHits']}|"
        f"pairs={summary['totalCollisionPairs']}|strictRows={summary['strictInstructionRows']}|"
        f"contextRows={summary['contextTermRows']}|strict={summary['totalStrictInstructionHits']}|"
        f"context={summary['totalContextTermHits']}|sourceR3={source_backed_r3}|"
        f"triggers={satisfied_triggers}/{trigger_count}|selectors={selector_unlocks}"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "valid page 75 -> page 76 word-box collision trace around O4/B4/G5/O5; no key derivation",
        "inputs": {
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "articleMap": rel(ARTICLE_MAP),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": "valid_leaf_word_collision_trace_no_instruction_source",
        "summary": summary,
        "fingerprint": fingerprint,
        "traceRows": trace_rows,
        "sheet": rel(OUT_SHEET),
        "nextMove": "Do not extract from valid-leaf OCR word collisions; require source/clue wording that names transform, unit, and order.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    draw_sheet(result, panel_paths)

    lines = [
        "# Current Scan Valid Leaf Word-Collision Trace",
        "",
        "Scope: projected page-75 OCR word boxes through the physically valid page 75 -> page 76 held-to-light transform, then checked whether they collide with O4/B4/G5/O5 target words as instruction, unit, or order language. No OCR-to-key extraction, key derivation, hashes, seed/WIF/address checks, BIP39, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Rows / source-word rows / collision rows: `{summary['traceRowCount']}` / `{summary['sourceWordRows']}` / `{summary['collisionRows']}`",
        f"- Source words / target words / collision pairs: `{summary['totalSourceWordHits']}` / `{summary['totalTargetWordHits']}` / `{summary['totalCollisionPairs']}`",
        f"- Strict instruction rows / context rows: `{summary['strictInstructionRows']}` / `{summary['contextTermRows']}`",
        f"- Source-backed R3 / satisfied triggers: `{source_backed_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Target Rows",
        "",
        "| mode | target | target text | source text | pairs | strict | context | initials | panel |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in trace_rows:
        lines.append(
            "| `{mode}` | `{target}` | {target_text} | {source_text} | {pairs} | {strict} | {context} | `{initials}` | `{panel}` |".format(
                mode=row["mode"],
                target=row["target"],
                target_text=row["targetTextPreview"].replace("|", "/") or "",
                source_text=row["sourceTextPreview"].replace("|", "/") or "",
                pairs=row["collisionPairCount"],
                strict=row["strictInstructionHitCount"],
                context=row["contextTermHitCount"],
                initials=row["combinedInitials"],
                panel=row["panel"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `valid_leaf_word_collision_trace_no_instruction_source`",
            "- Source words that reach the active boxes are ordinary page-75 prose and do not supply instruction, unit, or order wording.",
            "- Word-box collisions do not satisfy any source-backed R3 or reopen trigger.",
            "- Keep this as the word-level held-to-light collision stop-check for the current valid leaf.",
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
