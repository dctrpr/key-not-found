#!/usr/bin/env python3
"""Audit public clue words/numbers as simple selectors into page 76.

The original public text says a "private Bitcoin key" is "encoded in this
piece" and "for 20 BTC"; the follow-up clue names Schott's "Mirror writing"
paper. This pass checks whether those public words/numbers provide a low
parameter index rule into the already-confirmed page-76 corridor.

No private-key candidates, hashes, seed phrases, WIF checks, or address checks
are generated.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
CORRIDOR_JSON = ROOT / "analysis_outputs/3d_article_map/page76_line_level_corridor.json"
OUT = ROOT / "analysis_outputs/source_audit/public_clue_index_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "public_clue_index_selector.json"
OUT_MD = OUT / "public_clue_index_selector.md"
OUT_IMG = OUT / "public_clue_index_selector_sheet.jpg"

INSTRUCTION_TERMS = {
    "read",
    "take",
    "use",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "line",
    "word",
    "letter",
    "key",
    "private",
    "seed",
    "wif",
    "address",
    "down",
    "up",
    "above",
    "below",
    "next",
    "previous",
    "before",
    "after",
}

CLUE_TERMS = [
    {"source": "announcement", "term": "hid", "value": None},
    {"source": "announcement", "term": "private", "value": None},
    {"source": "announcement", "term": "Bitcoin", "value": None},
    {"source": "announcement", "term": "key", "value": None},
    {"source": "announcement", "term": "encoded", "value": None},
    {"source": "announcement", "term": "piece", "value": None},
    {"source": "announcement", "term": "wrote", "value": None},
    {"source": "announcement", "term": "BitcoinMagazine", "value": None},
    {"source": "announcement", "term": "President", "value": None},
    {"source": "announcement", "term": "Nobody", "value": None},
    {"source": "announcement", "term": "figured", "value": None},
    {"source": "announcement", "term": "out", "value": None},
    {"source": "announcement", "term": "yet", "value": None},
    {"source": "announcement", "term": "20", "value": 20},
    {"source": "announcement", "term": "BTC", "value": 3},
    {"source": "schott_title", "term": "Mirror", "value": None},
    {"source": "schott_title", "term": "writing", "value": None},
    {"source": "schott_title", "term": "neurological", "value": None},
    {"source": "schott_title", "term": "reflections", "value": None},
    {"source": "schott_title", "term": "unusual", "value": None},
    {"source": "schott_title", "term": "phenomenon", "value": None},
]


def clean_letters(text: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9]", text))


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text)


def load_page76() -> dict:
    data = json.loads(CANONICAL.read_text())
    return next(page for page in data["pages"].values() if page.get("articlePage") == 76)


def load_corridor() -> list[dict]:
    data = json.loads(CORRIDOR_JSON.read_text())
    return data["records"]


def corridor_words(records: list[dict]) -> list[dict]:
    out = []
    for record in records:
        for word in tokens(record["text"]):
            out.append(
                {
                    "text": word,
                    "lineIndex": record["lineIndex"],
                    "corridorIndex": record["corridorIndex"],
                    "highlights": record.get("highlights", []),
                }
            )
    return out


def page_words(page: dict) -> list[dict]:
    return [
        {
            "text": w["text"],
            "lineIndex": w["lineIndex"],
            "wordIndex": w["wordIndex"],
            "hasBold": w.get("hasBold", False),
            "partialBold": w.get("partialBold", False),
            "allBold": w.get("allBold", False),
        }
        for w in page["words"]
    ]


def term_rows() -> list[dict]:
    rows = []
    for i, term in enumerate(CLUE_TERMS, 1):
        letters = clean_letters(term["term"])
        rows.append(
            {
                "order": i,
                "source": term["source"],
                "term": term["term"],
                "letterLength": len(letters),
                "numericValue": term["value"],
                "indexValue": term["value"] if term["value"] is not None else len(letters),
            }
        )
    return rows


def pick_1based(items: list, index: int) -> dict | None:
    if 1 <= index <= len(items):
        return items[index - 1]
    return None


def pick_mod_1based(items: list, index: int) -> tuple[dict | None, int | None]:
    if not items:
        return None, None
    normalized = ((index - 1) % len(items)) + 1
    return items[normalized - 1], normalized


def scan_hits(text: str) -> list[str]:
    found = set(re.findall(r"[a-z0-9]+", text.lower()))
    return sorted(found & INSTRUCTION_TERMS)


def word_text(item: dict | None) -> str:
    return item["text"] if item else ""


def line_text(item: dict | None) -> str:
    return item["text"] if item else ""


def build_rows() -> tuple[list[dict], dict]:
    page = load_page76()
    records = load_corridor()
    cwords = corridor_words(records)
    pwords = page_words(page)
    page_lines = [{"lineIndex": row["lineIndex"], "text": row["text"].strip()} for row in page["lines"]]
    corridor_lines = [{"lineIndex": row["lineIndex"], "corridorIndex": row["corridorIndex"], "text": row["text"]} for row in records]
    g5_o5_lines = [row for row in corridor_lines if 27 <= row["lineIndex"] <= 32]

    rows = []
    for term in term_rows():
        idx = term["indexValue"]
        letter_idx = term["letterLength"]
        page_word = pick_1based(pwords, idx)
        corridor_word = pick_1based(cwords, idx)
        corridor_line = pick_1based(corridor_lines, idx)
        g5_line, g5_mod = pick_mod_1based(g5_o5_lines, idx)
        page_line = pick_1based(page_lines, idx)
        letter_corridor_word = pick_1based(cwords, letter_idx)
        rows.append(
            {
                **term,
                "page76WordByIndex": word_text(page_word),
                "page76WordLine": page_word["lineIndex"] if page_word else None,
                "corridorWordByIndex": word_text(corridor_word),
                "corridorWordLine": corridor_word["lineIndex"] if corridor_word else None,
                "corridorLineByIndex": line_text(corridor_line),
                "corridorLineIndex": corridor_line["lineIndex"] if corridor_line else None,
                "page76LineByIndex": line_text(page_line),
                "page76LineIndex": page_line["lineIndex"] if page_line else None,
                "g5o5LineByModulo": line_text(g5_line),
                "g5o5ModuloIndex": g5_mod,
                "g5o5LineIndex": g5_line["lineIndex"] if g5_line else None,
                "corridorWordByLetterLength": word_text(letter_corridor_word),
                "corridorWordByLetterLengthLine": letter_corridor_word["lineIndex"] if letter_corridor_word else None,
            }
        )

    streams = {
        "termInitials": "".join(row["term"][0] for row in rows if row["term"]),
        "indexValues": " ".join(str(row["indexValue"]) for row in rows),
        "page76WordsByIndex": " ".join(row["page76WordByIndex"] for row in rows if row["page76WordByIndex"]),
        "corridorWordsByIndex": " ".join(row["corridorWordByIndex"] for row in rows if row["corridorWordByIndex"]),
        "corridorWordsByLetterLength": " ".join(row["corridorWordByLetterLength"] for row in rows if row["corridorWordByLetterLength"]),
        "corridorLineInitialsByIndex": "".join((row["corridorLineByIndex"][:1] or "") for row in rows if row["corridorLineByIndex"]),
        "page76LineInitialsByIndex": "".join((row["page76LineByIndex"][:1] or "") for row in rows if row["page76LineByIndex"]),
        "g5o5ModuloLineInitials": "".join((row["g5o5LineByModulo"][:1] or "") for row in rows if row["g5o5LineByModulo"]),
        "g5o5ModuloLastWords": " ".join((tokens(row["g5o5LineByModulo"])[-1] if tokens(row["g5o5LineByModulo"]) else "") for row in rows if row["g5o5LineByModulo"]),
    }
    meta = {
        "pageWordCount": len(pwords),
        "pageLineCount": len(page_lines),
        "corridorWordCount": len(cwords),
        "corridorLineCount": len(corridor_lines),
        "g5o5LineCount": len(g5_o5_lines),
        "streams": streams,
        "streamInstructionHits": {name: scan_hits(value) for name, value in streams.items()},
    }
    return rows, meta


def draw_sheet(rows: list[dict], meta: dict) -> None:
    width = 1900
    row_h = 44
    height = 180 + row_h * (len(rows) + 1) + 210
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("Arial Bold.ttf", 28)
        font = ImageFont.truetype("Arial.ttf", 20)
        small = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        title_font = ImageFont.load_default()
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    draw.text((40, 28), "Public clue index selector audit", fill=(20, 20, 20), font=title_font)
    draw.text((40, 66), "Clue-word lengths and numeric values tested against page 76 and the confirmed corridor.", fill=(80, 80, 80), font=small)
    draw.text((40, 98), f"corridor words={meta['corridorWordCount']} corridor lines={meta['corridorLineCount']} G5/O5 lines={meta['g5o5LineCount']}", fill=(80, 80, 80), font=small)

    headers = ["term", "idx", "p76 word", "corridor word", "corridor line", "G5/O5 mod line"]
    xs = [40, 300, 380, 610, 860, 1380]
    y = 145
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(20, 20, 20), font=font)
    y += 34
    draw.line((40, y, width - 40, y), fill=(180, 180, 180), width=2)
    y += 10
    for row in rows:
        draw.text((xs[0], y), row["term"], fill=(20, 20, 20), font=small)
        draw.text((xs[1], y), str(row["indexValue"]), fill=(20, 20, 20), font=small)
        draw.text((xs[2], y), row["page76WordByIndex"][:20], fill=(70, 70, 70), font=small)
        draw.text((xs[3], y), row["corridorWordByIndex"][:22], fill=(70, 70, 70), font=small)
        draw.text((xs[4], y), (row["corridorLineByIndex"] or "-")[:56], fill=(70, 70, 70), font=small)
        draw.text((xs[5], y), (row["g5o5LineByModulo"] or "-")[:48], fill=(70, 70, 70), font=small)
        y += row_h

    y += 28
    draw.text((40, y), "Streams", fill=(20, 20, 20), font=font)
    y += 34
    for name in ["page76WordsByIndex", "corridorWordsByIndex", "g5o5ModuloLineInitials", "g5o5ModuloLastWords"]:
        value = meta["streams"][name]
        hits = meta["streamInstructionHits"][name]
        draw.text((40, y), f"{name}: {value[:150]} | hits={hits or 'none'}", fill=(50, 50, 50), font=small)
        y += 30

    img.save(OUT_IMG, quality=94)


def main() -> None:
    rows, meta = build_rows()
    draw_sheet(rows, meta)

    assessment = [
        "Public clue word lengths and the explicit numeric values `20` and `BTC=3` do not provide a clean selector into page 76.",
        "Direct index streams select ordinary article words, not procedural language such as read/take/word/letter/key.",
        "Modulo indexing into the G5/O5 six-line interval just cycles through the already-known lower corridor and does not add order.",
        "This closes public-clue word/number indexing as a standalone local selector.",
        "The public clue remains useful only for target type (`private Bitcoin key`), source (`piece`), value (`20 BTC`), and operation family (`mirror writing`).",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "public clue word/number index selector into page 76; no key derivation",
        "inputs": {
            "canonical": str(CANONICAL),
            "corridor": str(CORRIDOR_JSON),
        },
        "sheet": str(OUT_IMG),
        "clueRows": rows,
        **meta,
        "assessment": assessment,
        "nextMove": "Do not continue public-clue indexing without new wording. Use the public clue only as constraints: source article, mirror-writing operation, and private-key target type.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Public Clue Index Selector",
        "",
        "Scope: test whether the public clue words and numbers provide a simple index into page 76 or the confirmed page-76 corridor. No private-key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{OUT_IMG}`",
        "",
        "## Streams",
        "",
    ]
    for name, value in meta["streams"].items():
        hits = meta["streamInstructionHits"][name]
        md.append(f"- `{name}`: `{value}`; instruction hits: `{hits or 'none'}`")
    md.extend(
        [
            "",
            "## Rows",
            "",
            "| clue term | index | page-76 word | corridor word | corridor line | G5/O5 modulo line |",
            "|---|---:|---|---|---|---|",
        ]
    )
    for row in rows:
        md.append(
            f"| `{row['term']}` | `{row['indexValue']}` | `{row['page76WordByIndex'] or '-'}` | `{row['corridorWordByIndex'] or '-'}` | `{row['corridorLineByIndex'] or '-'}` | `{row['g5o5LineByModulo'] or '-'}` |"
        )
    md.extend(["", "## Assessment", ""])
    md.extend(f"- {item}" for item in assessment)
    md.extend(
        [
            "",
            "## Next Best Move",
            "",
            "- Keep the public clue as constraint language only. The missing selector still has to come from source/visual provenance, a better physical/source image, or an original layout/Canva asset.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_IMG}")
    print(f"corridorWordsByIndex={meta['streams']['corridorWordsByIndex']}")
    print(f"hits={meta['streamInstructionHits']}")


if __name__ == "__main__":
    main()
