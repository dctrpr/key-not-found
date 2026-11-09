#!/usr/bin/env python3
"""Audit whether the p78 frame phrase is supported by outside clue text.

The p78 frame-order pass produced a coherent article-context path:
``should sell | Volcano Bonds | shitcoiner at heart``.  This script checks
whether that path is echoed by source/public clue files, or whether it only
exists inside the article and our derived reports.  It does not generate keys,
hash text, or test addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/should_sell_volcano_source_clues"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "should_sell_volcano_source_clues.json"
OUT_MD = OUT / "should_sell_volcano_source_clues.md"


SOURCE_LIKE_FILES = {
    "article_text": [
        "full_article_corrected.txt",
    ],
    "original_public_clues": [
        "analysis_outputs/source_audit/thread_1632068898169450497.html",
        "analysis_outputs/external_clues/original_clue_provenance.md",
        "analysis_outputs/external_clues/original_clue_provenance.json",
        "analysis_outputs/external_clues/canva_source_inspection.md",
        "analysis_outputs/external_clues/canva_source_inspection.json",
        "analysis_outputs/external_clues/schott_instruction_distillation.md",
        "analysis_outputs/external_clues/schott_instruction_distillation.json",
    ],
    "derived_external_inventory": [
        "analysis_outputs/external_clues/source_clue_inventory.md",
        "analysis_outputs/external_clues/source_clue_inventory.json",
        "analysis_outputs/external_clues/external_clue_coverage_audit.md",
        "analysis_outputs/external_clues/external_clue_coverage_audit.json",
        "analysis_outputs/external_clues/max_thread_media/recovered_thread_media_report.md",
        "analysis_outputs/external_clues/max_thread_media/media_sequence_article_mapping.md",
        "analysis_outputs/external_clues/canva_thumbnail_export_audit.md",
        "analysis_outputs/external_clues/canva_thumbnail_export_audit.json",
        "analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.md",
        "analysis_outputs/source_audit/announcement_opening_spread/announcement_opening_spread_audit.json",
    ],
    "p78_graphic_reports": [
        "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.md",
        "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json",
        "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.md",
        "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json",
        "analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.md",
        "analysis_outputs/source_audit/p78_frame_order_read/p78_frame_order_read.json",
    ],
}


TERM_GROUPS = {
    "frame_phrase": [
        "should sell",
        "Volcano Bonds",
        "shitcoiner at heart",
        "should sell Volcano Bonds",
    ],
    "lower_corridor_context": [
        "buying the dip",
        "Nayib Bukele",
        "Bukele",
        "IMF loan",
        "International Monetary Fund",
        "$1 billion",
        "Mike Novogratz",
        "Novogratz",
    ],
    "public_instruction_terms": [
        "private",
        "key",
        "encoded",
        "20 BTC",
        "mirror writing",
        "mirror",
        "fold",
        "read",
        "take",
        "line",
        "word",
        "letter",
        "left",
        "right",
    ],
    "canva_source_gap_terms": [
        "pills dont line up",
        "diff pic",
        "#0",
        "WEB BROWSER PDF VIEWER",
        "XX",
        "BARBED",
        "SHIT",
        "FUCK ALL SHITCOINS",
    ],
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def term_pattern(term: str) -> re.Pattern[str]:
    if re.search(r"^[A-Za-z0-9 ]+$", term):
        # Plain word/phrase. Use loose whitespace, case-insensitive.
        parts = [re.escape(part) for part in term.split()]
        return re.compile(r"\b" + r"\s+".join(parts) + r"\b", re.I)
    return re.compile(re.escape(term), re.I)


def make_snippet(text: str, start: int, end: int, radius: int = 70) -> str:
    lo = max(0, start - radius)
    hi = min(len(text), end + radius)
    snippet = text[lo:hi].replace("\n", " ")
    snippet = re.sub(r"\s+", " ", snippet).strip()
    return snippet


def scan_file(path: Path) -> dict:
    text = read_text(path)
    hits_by_group: dict[str, dict[str, list[dict]]] = {}
    total_hits = 0
    for group, terms in TERM_GROUPS.items():
        group_hits: dict[str, list[dict]] = {}
        for term in terms:
            pattern = term_pattern(term)
            matches = []
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                matches.append(
                    {
                        "line": line,
                        "match": match.group(0),
                        "snippet": make_snippet(text, match.start(), match.end()),
                    }
                )
            if matches:
                group_hits[term] = matches
                total_hits += len(matches)
        if group_hits:
            hits_by_group[group] = group_hits
    return {
        "path": rel(path),
        "exists": True,
        "totalHits": total_hits,
        "hitsByGroup": hits_by_group,
    }


def scan_all() -> dict[str, list[dict]]:
    categories: dict[str, list[dict]] = {}
    for category, path_strings in SOURCE_LIKE_FILES.items():
        rows = []
        for path_string in path_strings:
            path = ROOT / path_string
            if path.exists():
                rows.append(scan_file(path))
            else:
                rows.append(
                    {
                        "path": path_string,
                        "exists": False,
                        "totalHits": 0,
                        "hitsByGroup": {},
                    }
                )
        categories[category] = rows
    return categories


def files_with_term(categories: dict[str, list[dict]], term: str) -> list[dict]:
    rows = []
    for category, files in categories.items():
        for file_row in files:
            for group, hits in file_row["hitsByGroup"].items():
                if term in hits:
                    rows.append(
                        {
                            "category": category,
                            "path": file_row["path"],
                            "count": len(hits[term]),
                            "firstLine": hits[term][0]["line"],
                            "firstSnippet": hits[term][0]["snippet"],
                        }
                    )
    return rows


def group_counts(categories: dict[str, list[dict]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for category, files in categories.items():
        counts[category] = {}
        for file_row in files:
            for group, hits_by_term in file_row["hitsByGroup"].items():
                counts[category].setdefault(group, 0)
                counts[category][group] += sum(len(items) for items in hits_by_term.values())
    return counts


def main() -> None:
    categories = scan_all()
    term_index = {term: files_with_term(categories, term) for terms in TERM_GROUPS.values() for term in terms}

    original_public = categories["original_public_clues"]
    original_has_should_sell = any(
        "should sell" in file_row.get("hitsByGroup", {}).get("frame_phrase", {})
        for file_row in original_public
    )
    original_has_volcano_bonds = any(
        "Volcano Bonds" in file_row.get("hitsByGroup", {}).get("frame_phrase", {})
        for file_row in original_public
    )
    original_has_shitcoiner_heart = any(
        "shitcoiner at heart" in file_row.get("hitsByGroup", {}).get("frame_phrase", {})
        for file_row in original_public
    )
    p78_graphic_text = "The economy of love is infinitely more efficient than hate and war."

    assessment = [
        "`should sell` appears in the article text and in our p78-frame reports, not in original public clue text.",
        "`Volcano Bonds` appears in article-derived inventories and media mappings because the recovered media point to the Bukele/volcano corridor; it is not present as an outside instruction in the original tweet, Schott clue, or Canva note text.",
        "`shitcoiner at heart` is article-local plus derived-analysis language; it is not an outside clue phrase.",
        "The p78 graphic layer text is `The economy of love is infinitely more efficient than hate and war.`; it does not contain `sell`, `Volcano Bonds`, or a word/letter extraction instruction.",
        "The only original public instruction language remains the announcement (`private Bitcoin key encoded... 20 BTC`) and the Schott mirror-writing pointer.",
    ]
    conclusion = (
        "Close `should sell Volcano Bonds` as a direct external/source instruction. "
        "Keep it as article-context frame evidence for the page-76 G5/O5 target pair."
    )
    next_move = (
        "Return to the missing extraction-unit problem: either a new source/physical/Canva view must add the rule, "
        "or the next local pass should inspect original visual labels around the p78 graphic/page-76 lower corridor, not text hashes."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "outside-source support audit for `should sell | Volcano Bonds | shitcoiner at heart`; no key derivation",
        "termGroups": TERM_GROUPS,
        "categoryCounts": group_counts(categories),
        "termIndex": term_index,
        "sourceSignal": {
            "originalPublicCluesContainShouldSell": original_has_should_sell,
            "originalPublicCluesContainVolcanoBonds": original_has_volcano_bonds,
            "originalPublicCluesContainShitcoinerAtHeart": original_has_shitcoiner_heart,
            "p78GraphicText": p78_graphic_text,
        },
        "categories": categories,
        "assessment": assessment,
        "conclusion": conclusion,
        "nextMove": next_move,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Should Sell / Volcano Source-Clue Audit",
        "",
        "Scope: test whether the p78 frame phrase `should sell | Volcano Bonds | shitcoiner at heart` is supported by outside/public clue text. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- JSON: `{rel(OUT_JSON)}`",
        "",
        "## Source Signal",
        "",
        f"- Original public clues contain `should sell`: `{original_has_should_sell}`",
        f"- Original public clues contain `Volcano Bonds`: `{original_has_volcano_bonds}`",
        f"- Original public clues contain `shitcoiner at heart`: `{original_has_shitcoiner_heart}`",
        f"- p78 graphic text: `{p78_graphic_text}`",
        "",
        "## Term Index",
        "",
    ]
    for term in ["should sell", "Volcano Bonds", "shitcoiner at heart", "should sell Volcano Bonds"]:
        rows = term_index[term]
        lines.append(f"### `{term}`")
        if not rows:
            lines.append("")
            lines.append("- No local hit.")
            lines.append("")
            continue
        lines.append("")
        for row in rows:
            lines.append(
                f"- `{row['category']}` `{row['path']}` line `{row['firstLine']}` count `{row['count']}`: {row['firstSnippet']}"
            )
        lines.append("")

    lines.extend(
        [
            "## Category Counts",
            "",
            "| category | frame phrase hits | lower corridor hits | public instruction hits | Canva/source-gap hits |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    counts = result["categoryCounts"]
    for category in SOURCE_LIKE_FILES:
        row = counts.get(category, {})
        lines.append(
            f"| `{category}` | {row.get('frame_phrase', 0)} | {row.get('lower_corridor_context', 0)} | {row.get('public_instruction_terms', 0)} | {row.get('canva_source_gap_terms', 0)} |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Conclusion", "", f"- {conclusion}", "", "## Next Move", "", f"- {next_move}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(conclusion)


if __name__ == "__main__":
    main()
