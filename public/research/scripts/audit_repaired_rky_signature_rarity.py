#!/usr/bin/env python3
"""Audit how rare the repaired R-K-Y signature is in the DOCM style stream.

The repaired p78 frame exact-edge trio has styles R-K-Y:
regular `should sell`, black/grey `Volcano Bonds`, yellow/orange
`shitcoiner at heart`. This pass checks whether R-K-Y is rare as typography
or only rare once geometry chooses the three edge contacts.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FONT_AUDIT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"
REPAIRED_JSON = ROOT / "analysis_outputs/docm_format_sources/repaired_frame_font_contact_states/repaired_frame_font_contact_states.json"

OUT = ROOT / "analysis_outputs/docm_format_sources/repaired_rky_signature_rarity"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "repaired_rky_signature_rarity.json"
OUT_MD = OUT / "repaired_rky_signature_rarity.md"
OUT_SHEET = OUT / "repaired_rky_signature_rarity_sheet.jpg"

PAGES = [75, 76, 77, 78, 79]
TARGET = "RKY"


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def page_for_paragraph(paragraph: int, boundaries: list[dict]) -> int | None:
    for item in boundaries:
        if item["paragraphStart"] <= paragraph <= item["paragraphEnd"]:
            return item["page"]
    return None


def style_code(run: dict) -> str:
    highlight = (run.get("highlight") or "").lower()
    font = run.get("fontAscii") or run.get("fontHAnsi") or ""
    if highlight == "yellow":
        return "Y"
    if highlight == "black":
        return "K"
    if highlight == "cyan":
        return "C"
    if font == "Typeka Mix":
        return "M"
    if font == "Typeka" and run.get("bold"):
        return "B"
    if font == "Typeka":
        return "R"
    return "O"


def build_style_groups(runs: list[dict], boundaries: list[dict], page: int) -> list[dict]:
    groups = []
    current = None
    for run in runs:
        if page_for_paragraph(run["paragraphIndex"], boundaries) != page:
            continue
        text = run.get("text") or ""
        if not text.strip():
            continue
        code = style_code(run)
        if current is None or current["code"] != code:
            if current is not None:
                current["text"] = clean("".join(current.pop("parts")))
                groups.append(current)
            current = {
                "groupIndex": len(groups) + 1,
                "page": page,
                "code": code,
                "runStart": run["runIndex"],
                "runEnd": run["runIndex"],
                "parts": [],
            }
        current["runEnd"] = run["runIndex"]
        current["parts"].append(text)
    if current is not None:
        current["text"] = clean("".join(current.pop("parts")))
        groups.append(current)
    return groups


def trim(text: str, limit: int = 86) -> str:
    text = clean(text)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def adjacent_windows(groups: list[dict], target: str) -> list[dict]:
    out = []
    for idx in range(len(groups) - len(target) + 1):
        window = groups[idx : idx + len(target)]
        code = "".join(group["code"] for group in window)
        if code == target:
            out.append(
                {
                    "groupIndexes": [group["groupIndex"] for group in window],
                    "codes": code,
                    "texts": [trim(group["text"]) for group in window],
                    "runSpans": [[group["runStart"], group["runEnd"]] for group in window],
                }
            )
    return out


def skip_triples(groups: list[dict], target: str, sample_limit: int = 8) -> tuple[int, list[dict]]:
    count = 0
    examples = []
    for i in range(len(groups)):
        if groups[i]["code"] != target[0]:
            continue
        for j in range(i + 1, len(groups)):
            if groups[j]["code"] != target[1]:
                continue
            for k in range(j + 1, len(groups)):
                if groups[k]["code"] != target[2]:
                    continue
                count += 1
                if len(examples) < sample_limit:
                    window = [groups[i], groups[j], groups[k]]
                    examples.append(
                        {
                            "groupIndexes": [group["groupIndex"] for group in window],
                            "codes": target,
                            "texts": [trim(group["text"]) for group in window],
                            "runSpans": [[group["runStart"], group["runEnd"]] for group in window],
                        }
                    )
    return count, examples


def find_repaired_signature(repaired: dict) -> dict:
    summary = next(s for s in repaired["summaries"] if s["name"] == "g5_edge_touch_dx_minus_38")
    return {
        "scenario": summary["name"],
        "exactEdgeLabels": summary["streams"]["exactEdgeLabels"],
        "exactEdgeStyles": summary["streams"]["exactEdgeStyles"],
        "exactEdgeInitials": summary["streams"]["exactEdgeInitials"],
        "exactEdgeLasts": summary["streams"]["exactEdgeLasts"],
    }


def draw_sheet(page_records: list[dict], signature: dict) -> None:
    width = 1700
    row_h = 70
    height = 220 + row_h * (sum(max(1, len(r["adjacentRkyWindows"])) for r in page_records) + len(page_records))
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 26)
        font = ImageFont.truetype("Arial.ttf", 18)
        small = ImageFont.truetype("Arial.ttf", 16)
    except OSError:
        title_font = ImageFont.load_default()
        font = title_font
        small = title_font

    y = 26
    draw.text((24, y), "R-K-Y signature rarity in Article with Fonts.docm", fill=(20, 20, 20), font=title_font)
    y += 38
    draw.text((24, y), f"Repaired exact-edge trio: {signature['exactEdgeLabels']} | styles {signature['exactEdgeStyles']}", fill=(30, 30, 30), font=font)
    y += 42
    draw.text((24, y), "Adjacent R-K-Y windows are listed below. Skipped R-K-Y counts show how common the code becomes without geometry.", fill=(80, 80, 80), font=small)
    y += 46

    for record in page_records:
        draw.rectangle([20, y - 8, width - 20, y + 34], fill=(235, 235, 235))
        draw.text(
            (28, y),
            f"page {record['page']} style groups={record['groupCount']} adjacent RKY={record['adjacentRkyCount']} skipped RKY={record['skipRkyCount']} sequence={record['styleSequence']}",
            fill=(20, 20, 20),
            font=font,
        )
        y += 46
        if record["adjacentRkyWindows"]:
            for window in record["adjacentRkyWindows"]:
                draw.text((52, y), f"groups {window['groupIndexes']}: " + "  |  ".join(window["texts"]), fill=(20, 60, 120), font=small)
                y += row_h
        else:
            draw.text((52, y), "no adjacent R-K-Y window", fill=(120, 70, 40), font=small)
            y += row_h
    image.save(OUT_SHEET, quality=95)


def main() -> None:
    runs = json.loads(RUNS_JSON.read_text())
    boundaries = json.loads(FONT_AUDIT_JSON.read_text())["pageBoundariesByParagraph"]
    repaired = json.loads(REPAIRED_JSON.read_text())
    signature = find_repaired_signature(repaired)

    page_records = []
    all_adjacent = []
    total_skip = 0
    for page in PAGES:
        groups = build_style_groups(runs, boundaries, page)
        adjacent = adjacent_windows(groups, TARGET)
        skip_count, skip_examples = skip_triples(groups, TARGET)
        total_skip += skip_count
        all_adjacent.extend({"page": page, **item} for item in adjacent)
        page_records.append(
            {
                "page": page,
                "groupCount": len(groups),
                "styleSequence": "".join(group["code"] for group in groups),
                "styleCounts": dict(Counter(group["code"] for group in groups)),
                "adjacentRkyCount": len(adjacent),
                "adjacentRkyWindows": adjacent,
                "skipRkyCount": skip_count,
                "skipRkyExamples": skip_examples,
            }
        )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "rarity of repaired R-K-Y exact-edge style signature in DOCM style streams; no key derivation",
        "sourceReports": {
            "runs": str(RUNS_JSON.relative_to(ROOT)),
            "fontAudit": str(FONT_AUDIT_JSON.relative_to(ROOT)),
            "repairedFrameFontContacts": str(REPAIRED_JSON.relative_to(ROOT)),
        },
        "repairedSignature": signature,
        "pageRecords": page_records,
        "totals": {
            "adjacentRkyTotal": len(all_adjacent),
            "skipRkyTotal": total_skip,
            "pagesWithAdjacentRky": sorted({item["page"] for item in all_adjacent}),
        },
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": [
            "Adjacent R-K-Y appears only once in the DOCM page style streams, and not on page 76.",
            f"Allowing skipped/non-adjacent R-K-Y makes it common: `{total_skip}` ordered triples across pages 75-79, including `{next(r for r in page_records if r['page'] == 76)['skipRkyCount']}` on page 76.",
            "The repaired exact-edge R-K-Y therefore gets its specificity from p78-frame geometry, not from the font/style sequence alone.",
            "Do not use R-K-Y by itself as a font cipher. Keep it as a compact source-registration benchmark only when paired with the exact edge contacts `should sell | Volcano Bonds | shitcoiner at heart`.",
        ],
        "nextMove": "Source-side validation remains the highest-value path: compare any future higher-resolution Canva/original-layout/physical source against the exact-edge trio and M3/O5/G5 tri-contact signature.",
    }

    draw_sheet(page_records, signature)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Repaired R-K-Y Signature Rarity",
        "",
        "Scope: test whether the repaired exact-edge `R-K-Y` style signature is rare typography or only meaningful when selected by p78 geometry. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Repaired exact-edge trio: `{signature['exactEdgeLabels']}`",
        f"- Repaired style code: `{signature['exactEdgeStyles']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Page Counts",
        "",
        "| page | style groups | style sequence | adjacent RKY | skipped RKY triples |",
        "|---:|---:|---|---:|---:|",
    ]
    for record in page_records:
        lines.append(
            f"| {record['page']} | {record['groupCount']} | `{record['styleSequence']}` | {record['adjacentRkyCount']} | {record['skipRkyCount']} |"
        )

    lines.extend(["", "## Adjacent R-K-Y Windows", ""])
    if all_adjacent:
        for item in all_adjacent:
            lines.append(f"- page `{item['page']}`, groups `{item['groupIndexes']}`: " + " | ".join(f"`{text}`" for text in item["texts"]))
    else:
        lines.append("- none")

    lines.extend(["", "## Page-76 Skipped Examples", ""])
    p76 = next(record for record in page_records if record["page"] == 76)
    for item in p76["skipRkyExamples"]:
        lines.append(f"- groups `{item['groupIndexes']}`: " + " | ".join(f"`{text}`" for text in item["texts"]))

    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("adjacent RKY total:", result["totals"]["adjacentRkyTotal"])
    print("skipped RKY total:", result["totals"]["skipRkyTotal"])
    print("pages with adjacent RKY:", result["totals"]["pagesWithAdjacentRky"])


if __name__ == "__main__":
    main()
