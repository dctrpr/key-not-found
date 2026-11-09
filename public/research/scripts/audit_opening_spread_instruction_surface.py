#!/usr/bin/env python3
"""Audit the opening OVERDOSE spread as an instruction surface.

This is a bounded visual inventory. It does not OCR the page, derive keys, hash
text, or test addresses. It checks whether the opener pages 73-74 visibly name
an extraction unit/order, or whether they only supply provenance and motif
evidence for the later page-76/page-79 system.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PAGE73 = ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/issue24/page_01.jpg"
PAGE74 = ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/issue24/page_02.jpg"
OUT = ROOT / "analysis_outputs/source_audit/opening_spread_instruction_surface"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "opening_spread_instruction_surface.json"
OUT_MD = OUT / "opening_spread_instruction_surface.md"
OUT_SHEET = OUT / "opening_spread_instruction_surface_sheet.jpg"

INSTRUCTION_TERMS = {
    "read",
    "take",
    "use",
    "select",
    "choose",
    "fold",
    "mirror",
    "reverse",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "top",
    "bottom",
    "inside",
    "outside",
    "key",
    "private",
    "seed",
    "page",
    "number",
    "count",
    "dose",
    "capsule",
    "pill",
}

# Manually inventoried visible surfaces on the high-res opener spread.
# Boxes are approximate and used only for visual review crops.
SURFACES = [
    {
        "id": "p73_small_overdose",
        "page": 73,
        "kind": "label",
        "box": [210, 125, 410, 170],
        "text": "OVERDOSE",
    },
    {
        "id": "p73_large_overdose",
        "page": 73,
        "kind": "title",
        "box": [190, 330, 2230, 560],
        "text": "OVERDOSE",
    },
    {
        "id": "p73_with_max_keiser",
        "page": 73,
        "kind": "credit",
        "box": [300, 620, 810, 720],
        "text": "with Max Keiser",
    },
    {
        "id": "p73_vertical_footer",
        "page": 73,
        "kind": "footer",
        "box": [80, 1750, 140, 2920],
        "text": "Bitcoin Magazine | El Salvador",
    },
    {
        "id": "p73_page_number",
        "page": 73,
        "kind": "page_number",
        "box": [75, 3095, 145, 3165],
        "text": "73",
    },
    {
        "id": "p73_five_capsules",
        "page": 73,
        "kind": "capsule_sequence",
        "box": [650, 1110, 1080, 2610],
        "text": "five orange-white capsules",
        "count": 5,
        "order": "top-to-bottom on page 73",
    },
    {
        "id": "p74_small_overdose",
        "page": 74,
        "kind": "label",
        "box": [2160, 125, 2365, 170],
        "text": "OVERDOSE",
    },
    {
        "id": "p74_vertical_footer",
        "page": 74,
        "kind": "footer",
        "box": [2400, 1850, 2495, 2960],
        "text": "Bitcoin Magazine | El Salvador",
    },
    {
        "id": "p74_page_number",
        "page": 74,
        "kind": "page_number",
        "box": [2310, 3090, 2380, 3165],
        "text": "74",
    },
    {
        "id": "p74_max_and_money",
        "page": 74,
        "kind": "provenance_art",
        "box": [250, 900, 2160, 2920],
        "text": "Max Keiser with thrown dollar bills in El Salvador field",
    },
]


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def instruction_hits(text: str) -> list[str]:
    return sorted({w.lower() for w in words(text)} & INSTRUCTION_TERMS)


def source_for_page(page: int) -> Path:
    return PAGE73 if page == 73 else PAGE74


def make_sheet(records: list[dict]) -> None:
    crops = []
    for record in records:
        image = Image.open(source_for_page(record["page"])).convert("RGB")
        crop = image.crop(record["box"])
        crop.thumbnail((420, 220))
        crops.append((record, crop.copy()))

    width = 1380
    row_h = 280
    height = 90 + row_h * ((len(crops) + 2) // 3)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 18), "Opening spread instruction-surface audit: visible labels, page numbers, and capsule sequence", fill=(0, 0, 0))
    for idx, (record, crop) in enumerate(crops):
        row, col = divmod(idx, 3)
        x = 20 + col * 450
        y = 70 + row * row_h
        sheet.paste(crop, (x, y))
        draw.rectangle([x, y, x + crop.width, y + crop.height], outline=(220, 110, 0), width=3)
        label = f"{record['id']} p{record['page']} {record['kind']} | {record['text']}"
        if len(label) > 72:
            label = label[:69] + "..."
        draw.text((x, y + crop.height + 8), label, fill=(0, 0, 0))
        hits = ",".join(record["instructionHits"]) or "none"
        draw.text((x, y + crop.height + 28), f"instruction hits: {hits}", fill=(80, 80, 80))
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    records = []
    for surface in SURFACES:
        record = dict(surface)
        record["instructionHits"] = instruction_hits(surface["text"])
        record["initials"] = "".join(w[0] for w in words(surface["text"]))
        record["lasts"] = "".join(w[-1] for w in words(surface["text"]))
        records.append(record)

    visible_text = " | ".join(r["text"] for r in records)
    visible_text_no_repeats = " | ".join(dict.fromkeys(r["text"] for r in records))
    streams = {
        "visibleText": visible_text,
        "visibleTextNoRepeats": visible_text_no_repeats,
        "initialsBySurface": "".join(r["initials"] for r in records),
        "lastsBySurface": "".join(r["lasts"] for r in records),
        "pageNumbers": "73 74",
        "capsuleCount": "5",
        "pagePlusCapsule": "73 74 5",
    }
    stream_hits = {name: instruction_hits(value) for name, value in streams.items()}

    make_sheet(records)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "opening spread visible instruction-surface inventory; no key derivation",
        "inputs": {
            "page73": str(PAGE73.relative_to(ROOT)),
            "page74": str(PAGE74.relative_to(ROOT)),
        },
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "records": records,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": [
            "The opener visibly establishes OVERDOSE, Max Keiser, Bitcoin Magazine, El Salvador, page numbers 73/74, five capsules, field/money imagery, and provenance.",
            "The only instruction-term hits are generic/provenance terms already visible as labels or object types: page, capsule, Bitcoin, and number/count via the manually recorded object classes.",
            "No visible opener text names a unit/order such as take/read/select word/letter/line, nor does it mention mirror/fold/key/private.",
            "The five-capsule sequence remains useful as provenance/order evidence, but previous endpoint mapping showed it does not tightly select page-76 units under the current scan.",
        ],
        "decision": {
            "openerAsStandaloneSelector": "closed_current_scan",
            "openerAsProvenance": "keep",
            "nextMove": "Use opener only to validate future source/original-layout evidence or a clue explicitly naming capsules/page numbers; do not derive key material from opener labels alone.",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Opening Spread Instruction Surface",
        "",
        "Scope: inventory the visible text/objects on opener pages 73-74 and ask whether that layer names an extraction unit/order. No OCR extraction, key derivation, hashing, seed checking, WIF checking, or address checking was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Review sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Visible Surface Inventory",
        "",
        "| id | page | kind | text/count | instruction hits |",
        "|---|---:|---|---|---|",
    ]
    for r in records:
        text = r["text"]
        if "count" in r:
            text = f"{text}; count={r['count']}; order={r['order']}"
        hits = ", ".join(r["instructionHits"]) or "-"
        lines.append(f"| `{r['id']}` | `{r['page']}` | `{r['kind']}` | {text} | {hits} |")

    lines.extend(["", "## Streams", "", "| stream | value | instruction hits |", "|---|---|---|"])
    for name, value in streams.items():
        hits = ", ".join(stream_hits[name]) or "-"
        display = value if len(value) < 160 else value[:157] + "..."
        lines.append(f"| `{name}` | `{display}` | {hits} |")

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "- The opener visibly confirms the provenance layer: `OVERDOSE`, `with Max Keiser`, `Bitcoin Magazine | El Salvador`, page numbers `73/74`, dollar imagery, and a five-capsule motif.",
            "- It does not visibly state a procedural extraction rule such as read/take/select word/letter/line, mirror, fold, key, or private.",
            "- The five-capsule motif remains a real Issue 24 ordering/provenance feature, but the existing endpoint mapping only reconfirmed O5 and did not name a unit.",
            "",
            "## Decision",
            "",
            "- Close the opening spread as a standalone selector under the current scan.",
            "- Keep opener pages 73-74 as provenance/source-validation evidence for any future physical/original-layout source.",
            "- Reopen only if a future clue explicitly names capsules, opener pages, page numbers, or the opening spread as the extraction surface.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("openerAsStandaloneSelector:", result["decision"]["openerAsStandaloneSelector"])


if __name__ == "__main__":
    main()
