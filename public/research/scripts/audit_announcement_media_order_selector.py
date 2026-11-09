#!/usr/bin/env python3
"""Audit announcement media order as a selector into the page-76 corridor.

The recovered announcement thread has seven true puzzle media images. This pass
tests whether their public order gives a usable ordering rule for the page-76
Bukele / IMF / volcano / G5-O5 corridor.

No key derivation is performed.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = ROOT / "analysis_outputs/external_clues/max_thread_media"
OUT = ROOT / "analysis_outputs/external_clues/announcement_media_order_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "announcement_media_order_selector.json"
OUT_MD = OUT / "announcement_media_order_selector.md"
OUT_SHEET = OUT / "announcement_media_order_selector_sheet.jpg"

INSTRUCTION_TERMS = [
    "read",
    "take",
    "word",
    "letter",
    "line",
    "left",
    "right",
    "mirror",
    "fold",
    "key",
    "private",
    "first",
    "last",
    "middle",
    "down",
    "up",
]


MEDIA = [
    {
        "order": 1,
        "file": "01_FqZGAb7aYAEdnKL.jpg",
        "subject": "Max holding OVERDOSE spread with Bukele",
        "tags": ["overdose", "bukele", "magazine", "president"],
        "matchedUnits": ["source_piece", "president_bukele"],
    },
    {
        "order": 2,
        "file": "02_FqZGH-oaAAcL8y5.jpg",
        "subject": "Max and Bukele at El Salvador presidential seal",
        "tags": ["bukele", "el_salvador", "president", "seal", "magazine"],
        "matchedUnits": ["president_el_salvador", "president_bukele"],
    },
    {
        "order": 3,
        "file": "03_FqZGH-takAInkt4.jpg",
        "subject": "Stacy Herbert portrait",
        "tags": ["stacy"],
        "matchedUnits": ["stacy_page79"],
    },
    {
        "order": 4,
        "file": "04_FqaB47TagAEbd2r.jpg",
        "subject": "Max and Bukele holding Bitcoin Magazine issue",
        "tags": ["bukele", "bitcoin_magazine", "source_piece"],
        "matchedUnits": ["source_piece", "president_bukele"],
    },
    {
        "order": 5,
        "file": "05_FqaYnkpaMAEuMC5.jpg",
        "subject": "Max/Stacy/driver in car, El Salvador context",
        "tags": ["stacy", "travel", "el_salvador"],
        "matchedUnits": ["stacy_page79", "president_el_salvador"],
    },
    {
        "order": 6,
        "file": "06_FqbSUHHWcAM05op.jpg",
        "subject": "Stacy in lava/El Salvador flag composite",
        "tags": ["stacy", "lava", "el_salvador", "volcano"],
        "matchedUnits": ["stacy_page79", "volcanoes"],
    },
    {
        "order": 7,
        "file": "07_Fqb_i__WYAE33V5.jpg",
        "subject": "Bitcoin symbols erupting from a volcano",
        "tags": ["bitcoin", "volcano", "volcano_bonds"],
        "matchedUnits": ["volcanoes", "volcano_bonds"],
    },
]


UNITS = {
    "source_piece": {"label": "Bitcoin Magazine / OVERDOSE source piece", "page": "source"},
    "president_el_salvador": {"label": "president of El Salvador", "page": 76},
    "president_bukele": {"label": "President Nayib Bukele", "page": 76},
    "buying_dip": {"label": "buying the dip", "page": 76},
    "volcanoes": {"label": "volcanoes to mine", "page": 76},
    "one_billion": {"label": "$1 billion", "page": 76},
    "volcano_bonds": {"label": "Volcano Bonds", "page": 76},
    "imf_loan": {"label": "IMF loan", "page": 76},
    "stacy_page79": {"label": "Stacy and I / article ending", "page": 79},
}

LOWER_CORRIDOR_EXPECTED = [
    "president_el_salvador",
    "buying_dip",
    "president_bukele",
    "volcanoes",
    "one_billion",
    "volcano_bonds",
    "imf_loan",
]


def hits(value: str) -> list[str]:
    low = value.lower()
    return [term for term in INSTRUCTION_TERMS if term in low]


def initials(labels: list[str]) -> str:
    out = []
    for label in labels:
        words = re.findall(r"[A-Za-z0-9$%]+", label)
        out.append(words[0][0] if words else "")
    return "".join(out)


def build_contact(rows: list[dict]) -> None:
    thumb_w, thumb_h = 260, 180
    row_h = 260
    width = 920
    height = row_h * len(rows)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font_big = ImageFont.truetype("Arial.ttf", 24)
        font = ImageFont.truetype("Arial.ttf", 18)
    except OSError:
        font_big = ImageFont.load_default()
        font = ImageFont.load_default()

    for i, row in enumerate(rows):
        y = i * row_h
        path = MEDIA_DIR / row["file"]
        im = Image.open(path).convert("RGB")
        thumb = ImageOps.contain(im, (thumb_w, thumb_h))
        sheet.paste(thumb, (20, y + 20))
        draw.text((300, y + 24), f"{row['order']}. {row['subject']}", fill=(0, 0, 0), font=font_big)
        draw.text((300, y + 62), f"file: {row['file']}  size: {row['imageSize'][0]}x{row['imageSize'][1]}", fill=(70, 70, 70), font=font)
        draw.text((300, y + 96), "tags: " + ", ".join(row["tags"]), fill=(30, 70, 130), font=font)
        unit_text = "units: " + " | ".join(UNITS[u]["label"] for u in row["matchedUnits"])
        draw.multiline_text((300, y + 126), unit_text, fill=(120, 50, 0), font=font, spacing=4)
        draw.line((0, y + row_h - 1, width, y + row_h - 1), fill=(220, 220, 220), width=1)

    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    rows = []
    for item in MEDIA:
        path = MEDIA_DIR / item["file"]
        im = Image.open(path)
        rows.append({**item, "imageSize": list(im.size)})

    build_contact(rows)

    ordered_units = []
    for row in rows:
        for unit in row["matchedUnits"]:
            ordered_units.append(unit)
    ordered_labels = [UNITS[u]["label"] for u in ordered_units]
    page76_units = [u for u in ordered_units if UNITS[u]["page"] == 76]
    page76_unique = []
    for unit in page76_units:
        if unit not in page76_unique:
            page76_unique.append(unit)
    page76_labels = [UNITS[u]["label"] for u in page76_units]
    page76_unique_labels = [UNITS[u]["label"] for u in page76_unique]
    missing_expected = [u for u in LOWER_CORRIDOR_EXPECTED if u not in page76_unique]
    repeated = {u: page76_units.count(u) for u in sorted(set(page76_units)) if page76_units.count(u) > 1}

    streams = {
        "mediaUnitLabels": " | ".join(ordered_labels),
        "mediaUnitInitials": initials(ordered_labels),
        "page76UnitLabels": " | ".join(page76_labels),
        "page76UnitInitials": initials(page76_labels),
        "page76UniqueLabels": " | ".join(page76_unique_labels),
        "page76UniqueInitials": initials(page76_unique_labels),
    }
    stream_hits = {name: hits(value) for name, value in streams.items()}
    assessment = [
        "The announcement media sequence strongly confirms the El Salvador/Bukele/volcano section, but it does not cover the full lower-corridor selector path.",
        "It misses or does not visually specify key local units like `buying the dip`, `$1 billion`, `IMF loan`, `should sell`, `could sell`, `trust that guy`, and O5 `shitcoiner at heart`.",
        "The image order is broad and thematic rather than a precise phrase order; the derived streams are not instruction-like.",
        "Keep the media sequence as target confirmation for page 76 and source provenance, not as the missing selector/order rule.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "announcement media order as page-76 corridor selector; no key derivation",
        "media": rows,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "page76UniqueUnits": page76_unique,
        "missingExpectedLowerCorridorUnits": missing_expected,
        "repeatedPage76Units": repeated,
        "contactSheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": assessment,
        "nextMove": "Close announcement media order as a selector. Use it only to keep page 76/Bukele/volcano as high-priority and continue looking for a source/physical registration rule.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Announcement Media Order Selector",
        "",
        "Scope: test whether the seven true announcement images, in public order, provide a selector/order for page 76. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Contact sheet: `{result['contactSheet']}`",
        "",
        "## Streams",
        "",
    ]
    for name, value in streams.items():
        hit_text = ", ".join(stream_hits[name]) if stream_hits[name] else "none"
        lines.append(f"- `{name}` hits={hit_text}: `{value}`")

    lines.extend(
        [
            "",
            "## Media Ledger",
            "",
            "| order | file | subject | matched units |",
            "|---:|---|---|---|",
        ]
    )
    for row in rows:
        units = " | ".join(UNITS[u]["label"] for u in row["matchedUnits"])
        lines.append(f"| {row['order']} | `{row['file']}` | {row['subject']} | {units} |")

    lines.extend(["", "## Coverage", ""])
    lines.append("- Unique page-76 units: `" + " | ".join(page76_unique_labels) + "`")
    lines.append("- Missing expected lower-corridor units: `" + " | ".join(UNITS[u]["label"] for u in missing_expected) + "`")
    lines.append("- Repeated page-76 units: `" + json.dumps(repeated, ensure_ascii=False) + "`")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("page76UniqueInitials", streams["page76UniqueInitials"], "hits", stream_hits["page76UniqueInitials"])
    print("missing", missing_expected)


if __name__ == "__main__":
    main()
