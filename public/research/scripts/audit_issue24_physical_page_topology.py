#!/usr/bin/env python3
"""Document Issue 24 page topology from the locked best scan."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/issue24"
OUT_DIR = ROOT / "analysis_outputs/source_audit/issue24_physical_page_topology"
OUT_MD = OUT_DIR / "issue24_physical_page_topology.md"
OUT_JSON = OUT_DIR / "issue24_physical_page_topology.json"
OUT_SHEET = OUT_DIR / "issue24_physical_page_topology_sheet.jpg"


PDF_TO_INTERNAL = {i: 72 + i for i in range(1, 9)}
ARTICLE_PAGES = {75, 76, 77, 78, 79, 80}


def side_for_page(page: int) -> str:
    return "recto/right/odd" if page % 2 else "verso/left/even"


def page_path(pdf_page: int) -> Path:
    return IMG_DIR / f"page_{pdf_page:02d}.jpg"


def thumb(pdf_page: int, width: int = 210) -> Image.Image:
    im = Image.open(page_path(pdf_page)).convert("RGB")
    h = int(im.height * (width / im.width))
    return im.resize((width, h), Image.Resampling.LANCZOS)


def draw_sheet(rows: list[dict]) -> None:
    thumb_w = 190
    gap = 28
    margin = 24
    row_h = 310
    max_pages = max(len(row["pdfPages"]) for row in rows)
    width = max(1320, margin * 2 + max_pages * thumb_w + (max_pages - 1) * gap)
    height = margin * 2 + 90 + row_h * len(rows)
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    y = margin
    draw.text(
        (margin, y),
        "Issue 24 physical page topology from locked best scan: leaves vs facing spreads",
        fill=(0, 0, 0),
    )
    y += 50
    for row in rows:
        draw.text((margin, y), row["title"], fill=(0, 0, 0))
        draw.text((margin + 380, y), row["note"], fill=(80, 80, 80))
        y += 26
        x = margin
        for pdf_page in row["pdfPages"]:
            t = thumb(pdf_page, thumb_w)
            sheet.paste(t, (x, y))
            internal = PDF_TO_INTERNAL[pdf_page]
            label = f"PDF {pdf_page} / page {internal}"
            if internal in ARTICLE_PAGES:
                label += " article"
            else:
                label += " opener"
            draw.rectangle((x, y, x + t.width, y + t.height), outline=(180, 120, 0), width=3)
            draw.text((x, y + t.height + 8), label, fill=(0, 0, 0))
            draw.text((x, y + t.height + 28), side_for_page(internal), fill=(80, 80, 80))
            x += thumb_w + gap
        y += row_h
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    page_rows = []
    for pdf_page, internal in PDF_TO_INTERNAL.items():
        page_rows.append(
            {
                "pdfPage": pdf_page,
                "internalPage": internal,
                "role": "article" if internal in ARTICLE_PAGES else "opener",
                "side": side_for_page(internal),
                "image": str(page_path(pdf_page).relative_to(ROOT)),
            }
        )

    leaves = [
        {"name": "opener leaf", "internalPages": [73, 74], "pdfPages": [1, 2]},
        {"name": "article leaf 1", "internalPages": [75, 76], "pdfPages": [3, 4]},
        {"name": "article leaf 2", "internalPages": [77, 78], "pdfPages": [5, 6]},
        {"name": "article leaf 3", "internalPages": [79, 80], "pdfPages": [7, 8]},
    ]
    facing_spreads = [
        {"name": "entry spread", "internalPages": [74, 75], "pdfPages": [2, 3]},
        {"name": "article spread 1", "internalPages": [76, 77], "pdfPages": [4, 5]},
        {"name": "article spread 2", "internalPages": [78, 79], "pdfPages": [6, 7]},
    ]

    tested_signal_pairs = [
        {
            "pair": "78 -> 76",
            "topology": "not same leaf and not facing spread",
            "meaning": "visual/registration signal only under current scan, not literal magazine leaf physics",
        },
        {
            "pair": "79 -> 76",
            "topology": "not same leaf and not facing spread",
            "meaning": "visual/registration signal only under current scan, not literal magazine leaf physics",
        },
        {
            "pair": "75 <-> 76",
            "topology": "same physical leaf",
            "meaning": "valid hold-to-light pair, but prior refined leaf tests did not reproduce the lower p76 corridor",
        },
        {
            "pair": "77 <-> 78",
            "topology": "same physical leaf",
            "meaning": "valid hold-to-light pair; supports checking only with new physical/source evidence",
        },
        {
            "pair": "78 <-> 79",
            "topology": "facing spread",
            "meaning": "valid facing-spread pair; useful for visual registration, not front/back bleed-through",
        },
    ]

    sheet_rows = [
        {
            "title": "Locked PDF order",
            "note": "PDF pages 1-8 correspond to magazine pages 73-80.",
            "pdfPages": list(range(1, 9)),
        },
        {
            "title": "Physical leaves",
            "note": "Odd/even consecutive pages are opposite sides of one leaf.",
            "pdfPages": [1, 2, 3, 4, 5, 6, 7, 8],
        },
        {
            "title": "Facing spread candidates",
            "note": "Even/odd adjacent pages face each other: 74/75, 76/77, 78/79.",
            "pdfPages": [2, 3, 4, 5, 6, 7],
        },
    ]
    draw_sheet(sheet_rows)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "physical page topology guardrail for Issue 24 pages 73-80; no key derivation",
        "pageRows": page_rows,
        "physicalLeaves": leaves,
        "facingSpreads": facing_spreads,
        "testedSignalPairs": tested_signal_pairs,
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": [
            "Normal magazine pagination makes 73/74, 75/76, 77/78, and 79/80 front/back leaf pairs.",
            "Facing spreads in the available article window are 74/75, 76/77, and 78/79.",
            "The strongest current p78/p79 -> p76 page-76 signals are therefore not literal same-leaf hold-to-light or facing-spread folds under the current scan.",
            "This does not invalidate the mirror/highlight system; it says the current strong p76 corridor is a visual/registration clue unless a new physical/original-layout source changes the transform.",
        ],
        "decision": {
            "pageTopologyGuardrail": "recorded",
            "literalLeafPhysicsFor78Or79To76": "closed_current_scan",
            "nextMove": "Use same-leaf physics only for 75/76, 77/78, and 79/80; treat 78/79->76 signals as registration/orientation evidence until a new physical/source transform appears.",
        },
    }

    OUT_JSON.write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Issue 24 Physical Page Topology",
        "",
        "Scope: record the physical page/leaf topology implied by the locked best scan. No key derivation, hashing, seed checking, WIF checking, address checking, OCR extraction, or broad brute force was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Review sheet: `{OUT_SHEET.relative_to(ROOT)}`",
        "",
        "## Page Order",
        "",
        "| PDF page | magazine page | role | side |",
        "|---:|---:|---|---|",
    ]
    for row in page_rows:
        lines.append(
            f"| `{row['pdfPage']}` | `{row['internalPage']}` | `{row['role']}` | `{row['side']}` |"
        )

    lines += ["", "## Physical Leaves", "", "| leaf | magazine pages | PDF pages |", "|---|---|---|"]
    for leaf in leaves:
        lines.append(
            f"| `{leaf['name']}` | `{leaf['internalPages'][0]}/{leaf['internalPages'][1]}` | `{leaf['pdfPages'][0]}/{leaf['pdfPages'][1]}` |"
        )

    lines += ["", "## Facing Spreads", "", "| spread | magazine pages | PDF pages |", "|---|---|---|"]
    for spread in facing_spreads:
        lines.append(
            f"| `{spread['name']}` | `{spread['internalPages'][0]}/{spread['internalPages'][1]}` | `{spread['pdfPages'][0]}/{spread['pdfPages'][1]}` |"
        )

    lines += ["", "## Pair Classification", "", "| pair | topology | meaning |", "|---|---|---|"]
    for pair in tested_signal_pairs:
        lines.append(f"| `{pair['pair']}` | `{pair['topology']}` | {pair['meaning']} |")

    lines += [
        "",
        "## Findings",
        "",
        "- Same-leaf hold-to-light candidates are `73/74`, `75/76`, `77/78`, and `79/80`.",
        "- Facing-spread candidates inside this scan are `74/75`, `76/77`, and `78/79`.",
        "- The repeatedly strong `78 -> 76` and `79 -> 76` page-76 signals are not literal same-leaf or facing-spread relations under normal magazine pagination.",
        "- That keeps page 76 important, but classifies the 78/79 -> 76 behavior as visual registration/orientation evidence under the current scan, not proof of physical bleed-through.",
        "",
        "## Decision",
        "",
        "- Close literal leaf-physics interpretation for `78/79 -> 76` under the current scan.",
        "- Keep the topology as a guardrail: future physical/source transforms must say which physical pair they use before extracting text.",
        "",
    ]
    OUT_MD.write_text("\n".join(lines))
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("literalLeafPhysicsFor78Or79To76: closed_current_scan")


if __name__ == "__main__":
    main()
