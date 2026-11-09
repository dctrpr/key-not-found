#!/usr/bin/env python3
"""Test whether the page-76 line-offset pattern depends on line counting.

The current partial locator pattern was found using corrected page-76 line
indices. This checks alternate counting models:

- corrected lines including blank rows
- corrected nonblank lines only
- paragraph-local lines
- high-res highlight-row order

No key candidates are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "analysis_outputs/3d_article_map/canonical_char_model.json"
SELF_JSON = ROOT / "analysis_outputs/source_audit/page76_self_mirror/page76_self_mirror.json"
OUT = ROOT / "analysis_outputs/source_audit/page76_line_count_models"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "page76_line_count_models.json"
OUT_MD = OUT / "page76_line_count_models.md"

UNITS = [
    {"id": "O1", "kind": "orange", "index": 1, "line": 0, "label": "Get some toxicity / Open your heart to"},
    {"id": "O2", "kind": "orange", "index": 2, "line": 1, "label": "Bitcoin."},
    {"id": "B1", "kind": "grey", "index": 1, "line": 6, "label": "Gotta be this way... post-1971 fiat money"},
    {"id": "B2", "kind": "grey", "index": 2, "line": 7, "label": "nonsense"},
    {"id": "O3", "kind": "orange", "index": 3, "line": 13, "label": "by the rancid catnip of fiat money"},
    {"id": "B3", "kind": "grey", "index": 3, "line": 16, "label": "It's a stun gun to the genitals"},
    {"id": "O4", "kind": "orange", "index": 4, "line": 22, "label": "buying the dip"},
    {"id": "B4", "kind": "grey", "index": 4, "line": 25, "label": "$1 billion"},
    {"id": "B5", "kind": "grey", "index": 5, "line": 27, "label": "Volcano Bonds"},
    {"id": "O5", "kind": "orange", "index": 5, "line": 32, "label": "shitcoiner at heart"},
]


def load_lines() -> list[str]:
    data = json.loads(CANONICAL.read_text())
    page = next(page for page in data["pages"].values() if page.get("articlePage") == 76)
    return [line["text"].rstrip() for line in page["lines"]]


def line_units() -> dict[int, list[dict]]:
    out: dict[int, list[dict]] = {}
    for unit in UNITS:
        out.setdefault(unit["line"], []).append(unit)
    return out


def hit_row(unit: dict, target_line: int | None, lines: list[str], model: str) -> dict:
    by_line = line_units()
    if target_line is None or not (0 <= target_line < len(lines)):
        return {
            "model": model,
            "sourceId": unit["id"],
            "sourceIndex": unit["index"],
            "sourceLine": unit["line"],
            "targetLine": target_line,
            "targetText": "",
            "targetUnits": [],
            "hit": False,
        }
    targets = by_line.get(target_line, [])
    return {
        "model": model,
        "sourceId": unit["id"],
        "sourceIndex": unit["index"],
        "sourceLine": unit["line"],
        "targetLine": target_line,
        "targetText": lines[target_line],
        "targetUnits": [target["id"] for target in targets],
        "hit": bool(targets),
    }


def corrected_with_blanks(lines: list[str]) -> list[dict]:
    return [hit_row(unit, unit["line"] + unit["index"], lines, "corrected_with_blank_lines") for unit in UNITS]


def corrected_nonblank(lines: list[str]) -> list[dict]:
    nonblank = [i for i, text in enumerate(lines) if text.strip()]
    rank_for_line = {line: rank for rank, line in enumerate(nonblank)}
    line_for_rank = {rank: line for rank, line in enumerate(nonblank)}
    rows = []
    for unit in UNITS:
        rank = rank_for_line[unit["line"]]
        target_line = line_for_rank.get(rank + unit["index"])
        row = hit_row(unit, target_line, lines, "corrected_nonblank_lines")
        row["sourceNonblankRank"] = rank
        rows.append(row)
    return rows


def paragraph_ranges(lines: list[str]) -> list[list[int]]:
    paragraphs: list[list[int]] = []
    cur: list[int] = []
    for i, text in enumerate(lines):
        if text.strip():
            cur.append(i)
        elif cur:
            paragraphs.append(cur)
            cur = []
    if cur:
        paragraphs.append(cur)
    return paragraphs


def paragraph_local(lines: list[str]) -> list[dict]:
    ranges = paragraph_ranges(lines)
    paragraph_for_line = {}
    for pi, para in enumerate(ranges):
        for rank, line in enumerate(para):
            paragraph_for_line[line] = (pi, rank, para)
    rows = []
    for unit in UNITS:
        pi, rank, para = paragraph_for_line[unit["line"]]
        target_line = para[rank + unit["index"]] if rank + unit["index"] < len(para) else None
        row = hit_row(unit, target_line, lines, "paragraph_local_nonblank_lines")
        row["paragraphIndex"] = pi
        row["sourceParagraphRank"] = rank
        rows.append(row)
    return rows


def highlight_row_order() -> list[dict]:
    data = json.loads(SELF_JSON.read_text())
    items = data["items"]
    rows = []
    for item in sorted(items, key=lambda i: ((i["box"][1] + i["box"][3]) / 2, i["box"][0])):
        cy = (item["box"][1] + item["box"][3]) / 2
        if not rows or abs(rows[-1]["centerY"] - cy) > 25:
            rows.append({"row": len(rows), "centerY": cy, "items": []})
        rows[-1]["items"].append(item)
        rows[-1]["centerY"] = sum((i["box"][1] + i["box"][3]) / 2 for i in rows[-1]["items"]) / len(rows[-1]["items"])
    row_for_id = {}
    for row in rows:
        for item in row["items"]:
            row_for_id[item["id"]] = row["row"]
    row_items = {row["row"]: [item["id"] for item in row["items"]] for row in rows}
    out = []
    for unit in UNITS:
        source_row = row_for_id[unit["id"]]
        target_row = source_row + unit["index"]
        targets = row_items.get(target_row, [])
        out.append(
            {
                "model": "highres_highlight_row_order",
                "sourceId": unit["id"],
                "sourceIndex": unit["index"],
                "sourceHighlightRow": source_row,
                "targetHighlightRow": target_row,
                "targetUnits": targets,
                "hit": bool(targets),
            }
        )
    return out


def summarize(rows: list[dict]) -> dict:
    hits = [row for row in rows if row["hit"]]
    return {
        "hitCount": len(hits),
        "hits": [f"{row['sourceId']}->{','.join(row['targetUnits'])}" for row in hits],
    }


def main() -> None:
    lines = load_lines()
    models = {
        "corrected_with_blank_lines": corrected_with_blanks(lines),
        "corrected_nonblank_lines": corrected_nonblank(lines),
        "paragraph_local_nonblank_lines": paragraph_local(lines),
        "highres_highlight_row_order": highlight_row_order(),
    }
    summaries = {name: summarize(rows) for name, rows in models.items()}
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Compare page-76 line-counting models for the highlight-number offset pattern; no key derivation.",
        "summaries": summaries,
        "models": models,
        "assessment": [
            "The strongest partial pattern is the corrected-with-blank-lines model: O1->O2, B1->B2, O3->B3, B5->O5.",
            "The nonblank-line model loses O3->B3 because the blank row between the rancid-catnip line and the stun-gun line matters.",
            "Paragraph-local counting loses the cross-paragraph O3->B3 bridge.",
            "High-res highlight-row order produces a different set of hits and should not replace corrected text lines as the locator model.",
            "#2 and #4 still fail in the corrected line model; the complete line-offset rule remains closed.",
        ],
        "nextMove": "Treat corrected printed line layout, including blank rows, as the only line-counting model worth preserving. Keep looking for source/physical evidence that explains the #2/#4 gaps or chooses the extraction unit.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    md = [
        "# Page 76 Line-Count Models Audit",
        "",
        "Scope: compare line-counting models for the partial highlight-number offset pattern. No key candidates or hashing were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        "",
        "## Summary",
        "",
        "| model | hit count | hits |",
        "|---|---:|---|",
    ]
    for name, summary in summaries.items():
        md.append(f"| `{name}` | {summary['hitCount']} | `{', '.join(summary['hits'])}` |")

    md.extend(
        [
            "",
            "## Corrected With Blank Lines",
            "",
            "| source | target line | target units | target text |",
            "|---|---:|---|---|",
        ]
    )
    for row in models["corrected_with_blank_lines"]:
        targets = ",".join(row["targetUnits"]) or "-"
        text = row["targetText"].replace("|", "\\|")
        md.append(f"| {row['sourceId']} +{row['sourceIndex']} | {row['targetLine']} | {targets} | {text} |")

    md.extend(
        [
            "",
            "## Assessment",
            "",
            "- The partial pattern is most coherent only when using corrected printed line layout with blank rows preserved.",
            "- Removing blank rows breaks `O3 -> B3`; paragraph-local counting also breaks that cross-paragraph bridge.",
            "- High-res highlight-row order creates a different, less meaningful hit set, so it is not the right counting model.",
            "- The #2/#4 failures are not explained away by alternate line counting.",
            "- Next best move: preserve the corrected-with-blank-lines locator, but seek a source/provenance or physical-registration rule for the missing extraction unit.",
        ]
    )
    OUT_MD.write_text("\n".join(md) + "\n")
    print(OUT_MD)
    print(OUT_JSON)


if __name__ == "__main__":
    main()
