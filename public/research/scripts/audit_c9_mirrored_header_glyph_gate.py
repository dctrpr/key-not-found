#!/usr/bin/env python3
"""Test mirrored C9 OVERDOSE header-glyph slot readings.

The previous header-glyph pass showed that real p76/p78 OVERDOSE glyph
boundaries are effectively equal-width C9 slots. This bounded follow-up checks
the mirror variants that the fold/3D hypothesis could imply:

- keep geometry and reverse the header letters;
- mirror active/control boxes across the C9 frame center;
- do both at once.

No OCR, extraction, private-key derivation, hashing, seed/WIF checks, address
checks, or broad candidate generation are performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
C9_SLOT_JSON = ROOT / "analysis_outputs/source_audit/c9_overdose_letter_slot_gate/c9_overdose_letter_slot_gate.json"
C9_GREY_BLACK_JSON = (
    ROOT / "analysis_outputs/source_audit/c9_grey_black_over_slot_control/c9_grey_black_over_slot_control.json"
)
PAGE_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT = ROOT / "analysis_outputs/source_audit/c9_mirrored_header_glyph_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "c9_mirrored_header_glyph_gate.json"
OUT_MD = OUT / "c9_mirrored_header_glyph_gate.md"
SHEET = OUT / "c9_mirrored_header_glyph_gate_sheet.jpg"

LETTERS = "OVERDOSE"
MIN_SLOT_OVERLAP_PX = 4.0
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
    "reverse",
]
LAYOUT_TERMS = ["OVER", "DOSE", "OVERDOSE", "REVO", "ESOD"]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def compact(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", text).upper()


def term_hits(stream: str, terms: list[str]) -> list[str]:
    cstream = compact(stream)
    return [term for term in terms if compact(term) in cstream]


def find_header_glyphs(article: dict[str, Any], page_no: int) -> dict[str, Any]:
    page = next(page for page in article["pages"] if page["page"] == page_no)
    word = next(word for word in page["words"] if word.get("token") == "overdose")
    chars = []
    for char in page["chars"]:
        text = char.get("c", "")
        if text not in LETTERS:
            continue
        box = [float(v) for v in char["box"]]
        if box[0] >= word["box"][0] - 1 and box[2] <= word["box"][2] + 1 and abs(char["y"] - word["center"][1]) <= 6:
            chars.append({**char, "box": box})
    chars = sorted(chars, key=lambda row: row["box"][0])
    sequence = "".join(char["c"] for char in chars)
    if sequence != LETTERS:
        raise RuntimeError(f"page {page_no} header sequence mismatch: {sequence}")
    return {"page": page_no, "wordBox": [float(v) for v in word["box"]], "chars": chars}


def project_glyph_slots(header: dict[str, Any], c9_frame: list[float]) -> list[dict[str, Any]]:
    word_box = header["wordBox"]
    word_width = word_box[2] - word_box[0]
    c9_width = c9_frame[2] - c9_frame[0]
    slots = []
    for i, char in enumerate(header["chars"]):
        left_ratio = (char["box"][0] - word_box[0]) / word_width
        right_ratio = (char["box"][2] - word_box[0]) / word_width
        left = c9_frame[0] + left_ratio * c9_width
        right = c9_frame[0] + right_ratio * c9_width
        slots.append(
            {
                "index": i,
                "baseLetter": char["c"],
                "letter": char["c"],
                "left": left,
                "right": right,
                "width": right - left,
                "sourcePage": header["page"],
            }
        )
    return slots


def label_slots(slots: list[dict[str, Any]], reverse_labels: bool) -> list[dict[str, Any]]:
    letters = LETTERS[::-1] if reverse_labels else LETTERS
    return [{**slot, "letter": letters[slot["index"]], "reverseLabels": reverse_labels} for slot in slots]


def mirror_box_x(box: list[float], frame: list[float]) -> list[float]:
    return [frame[0] + frame[2] - box[2], box[1], frame[0] + frame[2] - box[0], box[3]]


def center_slot(box: list[float], slots: list[dict[str, Any]]) -> dict[str, Any]:
    cx = (float(box[0]) + float(box[2])) / 2
    for slot in slots:
        if slot["left"] <= cx < slot["right"] or slot["index"] == len(slots) - 1 and cx <= slot["right"]:
            return {**slot, "centerX": cx}
    return {**slots[-1], "centerX": cx}


def span_slots(box: list[float], slots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    left = float(box[0])
    right = float(box[2])
    out = []
    for slot in slots:
        overlap = max(0.0, min(right, slot["right"]) - max(left, slot["left"]))
        if overlap >= MIN_SLOT_OVERLAP_PX:
            out.append({**slot, "overlapPx": round(overlap, 2)})
    return out


def annotate(row: dict[str, Any], slots: list[dict[str, Any]], frame: list[float], mirror_geometry: bool) -> dict[str, Any]:
    box = [float(v) for v in row["box"]]
    if mirror_geometry:
        box = mirror_box_x(box, frame)
    center = center_slot(box, slots)
    spans = span_slots(box, slots)
    return {
        **row,
        "box": [round(v, 2) for v in box],
        "centerX": round(center["centerX"], 2),
        "centerSlotIndex": center["index"],
        "centerSlotLetter": center["letter"],
        "spanSlotIndexes": [slot["index"] for slot in spans],
        "spanSlotLetters": "".join(slot["letter"] for slot in spans),
        "spanSlotOverlapsPx": [slot["overlapPx"] for slot in spans],
    }


def stream_record(name: str, rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    value = "".join(row[field] for row in rows)
    return {
        "name": name,
        "stream": value,
        "targetOrder": [row.get("shortId") or row.get("id") for row in rows],
        "strictInstructionHits": term_hits(value, STRICT_INSTRUCTION_TERMS),
        "layoutTermHits": term_hits(value, LAYOUT_TERMS),
    }


def evaluate_variant(
    name: str,
    slots: list[dict[str, Any]],
    frame: list[float],
    active_rows: list[dict[str, Any]],
    control_rows: list[dict[str, Any]],
    mirror_geometry: bool,
) -> dict[str, Any]:
    active = [annotate(row, slots, frame, mirror_geometry) for row in active_rows]
    by_line = sorted(active, key=lambda row: (row["pageLine"], row["corridorIndex"]))
    by_x = sorted(active, key=lambda row: row["centerX"])
    black_by_x = [row for row in by_x if row["visualState"] == "K"]
    orange_by_x = [row for row in by_x if row["visualState"] == "Y"]
    control = [annotate(row, slots, frame, mirror_geometry) for row in control_rows]

    specs = [
        ("active_center_line_order", by_line, "centerSlotLetter"),
        ("active_center_x_order", by_x, "centerSlotLetter"),
        ("active_span_line_order", by_line, "spanSlotLetters"),
        ("active_span_x_order", by_x, "spanSlotLetters"),
        ("active_black_span_x_order", black_by_x, "spanSlotLetters"),
        ("active_orange_span_x_order", orange_by_x, "spanSlotLetters"),
        ("p75_control_span", control, "spanSlotLetters"),
    ]
    streams = [stream_record(f"{name}_{label}", rows, field) for label, rows, field in specs]
    return {
        "name": name,
        "mirrorGeometry": mirror_geometry,
        "reverseLabels": slots[0].get("reverseLabels", False),
        "slotLetters": "".join(slot["letter"] for slot in slots),
        "activeRows": active,
        "p75ControlRows": control,
        "streams": streams,
        "activeBlackSpan": next(row["stream"] for row in streams if row["name"].endswith("active_black_span_x_order")),
        "p75ControlSpan": next(row["stream"] for row in streams if row["name"].endswith("p75_control_span")),
        "strictInstructionHits": sorted({hit for stream in streams for hit in stream["strictInstructionHits"]}),
    }


def draw_sheet(result: dict[str, Any]) -> None:
    img = Image.open(PAGE_IMAGE).convert("RGB")
    crop = [180, 2050, 2320, 3050]
    scale = 0.46
    panel = img.crop(crop).resize((int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)))

    margin = 26
    header_h = 146
    row_h = 78
    sheet_w = margin * 2 + panel.size[0]
    sheet_h = header_h + panel.size[1] + margin + row_h * min(8, len(result["variants"])) + margin
    sheet = Image.new("RGB", (sheet_w, sheet_h), (12, 15, 20))
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    normal = font(15)
    small = font(12)

    draw.text((margin, 20), "C9 Mirrored Header Glyph Gate", fill=(240, 244, 248), font=title)
    draw.text(
        (margin, 56),
        "Tests reverse header letters and x-mirrored target/control boxes against actual p76/p78 OVERDOSE glyph slots.",
        fill=(180, 190, 202),
        font=normal,
    )
    summary = result["summary"]
    draw.text(
        (margin, 86),
        f"variants={summary['variantCount']} active_black_OVER={summary['activeBlackOverCount']} "
        f"active_black_REVO={summary['activeBlackRevoCount']} p75_matches={summary['p75ControlMatchesActiveBlackCount']} "
        f"strict_hits={summary['strictInstructionHitCount']}",
        fill=(180, 190, 202),
        font=small,
    )

    y0 = header_h
    sheet.paste(panel, (margin, y0))
    panel_draw = ImageDraw.Draw(sheet, "RGBA")
    for target in result["activeRows"]:
        box = target["box"]
        x0 = margin + (box[0] - crop[0]) * scale
        yb0 = y0 + (box[1] - crop[1]) * scale
        x1 = margin + (box[2] - crop[0]) * scale
        yb1 = y0 + (box[3] - crop[1]) * scale
        color = (255, 120, 0, 190) if target["visualState"] == "Y" else (20, 20, 20, 220)
        panel_draw.rectangle([x0, yb0, x1, yb1], outline=color, width=4)
        panel_draw.text((x0, max(y0, yb0 - 18)), target["shortId"], fill=color, font=small)

    y = y0 + panel.size[1] + margin
    for variant in result["variants"][:8]:
        label = variant["name"]
        line = (
            f"{label}: slots={variant['slotLetters']} active_black={variant['activeBlackSpan']} "
            f"p75={variant['p75ControlSpan']} strict={','.join(variant['strictInstructionHits']) or 'none'}"
        )
        fill = (250, 210, 140) if variant["activeBlackSpan"] == variant["p75ControlSpan"] else (210, 220, 230)
        draw.text((margin, y), line[:150], fill=fill, font=normal)
        y += row_h

    sheet.save(SHEET, quality=92)


def main() -> None:
    article = load_json(ARTICLE_JSON)
    c9_slot = load_json(C9_SLOT_JSON)
    grey_black = load_json(C9_GREY_BLACK_JSON)
    frame = [float(v) for v in c9_slot["c9Frame"]]
    active_rows = c9_slot["activeRows"]
    p75_control = [
        {
            "id": row["id"],
            "shortId": row["id"],
            "page": row["page"],
            "expected": row["expected"],
            "box": row["box"],
        }
        for row in grey_black["c9GreyBlackRows"]
        if row["id"] == "p75_grey_3"
    ]

    variants = []
    headers = [find_header_glyphs(article, 76), find_header_glyphs(article, 78)]
    for header in headers:
        base_slots = project_glyph_slots(header, frame)
        for reverse_labels in [False, True]:
            slots = label_slots(base_slots, reverse_labels)
            for mirror_geometry in [False, True]:
                name = (
                    f"p{header['page']}_"
                    f"{'reverse_labels' if reverse_labels else 'normal_labels'}_"
                    f"{'mirror_x_geometry' if mirror_geometry else 'original_geometry'}"
                )
                variants.append(evaluate_variant(name, slots, frame, active_rows, p75_control, mirror_geometry))

    active_black_over = [v["name"] for v in variants if v["activeBlackSpan"] == "OVER"]
    active_black_revo = [v["name"] for v in variants if v["activeBlackSpan"] == "REVO"]
    p75_control_over = [v["name"] for v in variants if v["p75ControlSpan"] == "OVER"]
    p75_control_revo = [v["name"] for v in variants if v["p75ControlSpan"] == "REVO"]
    p75_matches = [v["name"] for v in variants if v["activeBlackSpan"] == v["p75ControlSpan"]]
    strict_hits = sorted({hit for variant in variants for hit in variant["strictInstructionHits"]})

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "C9 mirrored header-glyph slot gate; no OCR, no extraction, no key derivation, no hashing",
        "inputs": {
            "article3dMap": rel(ARTICLE_JSON),
            "c9OverdoseLetterSlotGate": rel(C9_SLOT_JSON),
            "c9GreyBlackOverSlotControl": rel(C9_GREY_BLACK_JSON),
        },
        "c9Frame": frame,
        "activeRows": active_rows,
        "variants": variants,
        "summary": {
            "variantCount": len(variants),
            "activeBlackOverCount": len(active_black_over),
            "activeBlackRevoCount": len(active_black_revo),
            "p75ControlOverCount": len(p75_control_over),
            "p75ControlRevoCount": len(p75_control_revo),
            "p75ControlMatchesActiveBlackCount": len(p75_matches),
            "strictInstructionHitCount": len(strict_hits),
            "strictInstructionHits": strict_hits,
            "selectorUnlocked": False,
        },
        "assessment": [
            "Normal header labels reproduce active B4/G5 OVER and p75 control OVER.",
            "Reversed header labels or x-mirrored geometry turn the same relation into DOSE, ESOD, or REVO, not an instruction.",
            "Every active black OVER/REVO result is matched by the p75 grey control under the same variant.",
            "No mirrored slot variant produces strict unit/order instruction terms.",
        ],
        "decision": {
            "c9MirroredHeaderGlyphGate": "mirrored_header_glyph_no_selector",
            "selectorUnlocked": False,
            "nextMove": "Do not promote mirrored OVERDOSE header slots as a selector. Reopen only if a source/clue explicitly names mirrored header letters, glyph slots, or an 8-column reading order.",
        },
        "sheet": rel(SHEET),
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# C9 Mirrored Header Glyph Gate",
        "",
        "Scope: test mirror variants of the actual p76/p78 `OVERDOSE` header glyph slots against active O4/B4/G5/O5 and the p75 grey control. No OCR, extraction, hashing, seed/WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        "",
        "## Summary",
        "",
        f"- Variants tested: `{result['summary']['variantCount']}`.",
        f"- Active black `OVER` variants: `{result['summary']['activeBlackOverCount']}`.",
        f"- Active black `REVO` variants: `{result['summary']['activeBlackRevoCount']}`.",
        f"- p75 control `OVER` variants: `{result['summary']['p75ControlOverCount']}`.",
        f"- p75 control `REVO` variants: `{result['summary']['p75ControlRevoCount']}`.",
        f"- Variants where p75 control matches active black stream: `{result['summary']['p75ControlMatchesActiveBlackCount']}`.",
        f"- Strict instruction hits: `{result['summary']['strictInstructionHitCount']}`.",
        "",
        "## Variant Streams",
        "",
    ]
    for variant in variants:
        lines.append(
            f"- `{variant['name']}`: slots `{variant['slotLetters']}`, active black `{variant['activeBlackSpan']}`, p75 control `{variant['p75ControlSpan']}`, strict hits `{variant['strictInstructionHits']}`"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote mirrored OVERDOSE header glyph slots as a selector.",
            "- Mirroring header labels or C9 x-geometry only toggles the controlled B4/G5 signal among `OVER`, `DOSE`, `ESOD`, and `REVO`.",
            "- The p75 grey control matches the active black stream in every tested variant.",
            "- Reopen only if a new source/clue names mirrored header letters, glyph slots, or an 8-column reading order.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print(f"variants: {result['summary']['variantCount']}")
    print(f"activeBlack OVER/REVO: {len(active_black_over)}/{len(active_black_revo)}")
    print(f"p75 match count: {len(p75_matches)}")


if __name__ == "__main__":
    main()
