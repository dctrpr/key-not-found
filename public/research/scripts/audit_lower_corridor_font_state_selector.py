#!/usr/bin/env python3
"""Phrase-level font-state audit for the page-76 lower corridor.

This pass checks only the corridor repeatedly selected by the mirror/frame
system. It asks whether Typeka, Typeka Mix, Typeka-bold, and highlight states
choose a readable unit/order inside that corridor.

No key derivation is performed.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
EDGE_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_edge_reconciliation/p78_graphic_edge_reconciliation.json"

OUT = ROOT / "analysis_outputs/docm_format_sources/lower_corridor_font_state_selector"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "lower_corridor_font_state_selector.json"
OUT_MD = OUT / "lower_corridor_font_state_selector.md"

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
    "dip",
]


PHRASES = [
    {"id": "O4", "label": "buying the dip", "pattern": r"buying\s+the\s+dip"},
    {"id": "bukele", "label": "President Nayib Bukele", "pattern": r"President\s+Nayib\s+Bukele"},
    {"id": "B4_text", "label": "$1 billion", "pattern": re.escape("$1 billion")},
    {"id": "should_sell", "label": "should sell", "pattern": r"should\s+sell"},
    {"id": "earnings", "label": "earnings", "pattern": r"earnings"},
    {"id": "G5", "label": "Volcano Bonds", "pattern": r"Volcano\s+Bonds"},
    {"id": "pay_imf", "label": "pay off the IMF", "pattern": r"pay\s+off\s+the\s+IMF"},
    {"id": "IMF_loan", "label": "IMF loan", "pattern": r"IMF\s+loan"},
    {"id": "tagged_mike", "label": "I tagged Mike", "pattern": r"I\s+tagged\s+Mike"},
    {"id": "could_sell", "label": "could sell", "pattern": r"could\s+sell"},
    {"id": "trust_guy", "label": "trust that guy", "pattern": r"trust\s+that\s+guy"},
    {"id": "O5", "label": "shitcoiner at heart", "pattern": r"shitcoiner\s+at\s+heart"},
]


def variant_for_run(run: dict) -> str:
    font = run.get("fontAscii") or run.get("fontHAnsi") or ""
    if "Typeka Mix" in font:
        return "MIX"
    if "Typeka" in font and run.get("bold"):
        return "TYPEKA_BOLD"
    if "Typeka" in font:
        return "TYPEKA"
    return font or "OTHER"


def style_code(run: dict) -> str:
    highlight = (run.get("highlight") or "").lower()
    variant = variant_for_run(run)
    if highlight == "yellow":
        return "Y"
    if highlight == "black":
        return "K"
    if variant == "MIX":
        return "M"
    if variant == "TYPEKA_BOLD":
        return "B"
    if variant == "TYPEKA":
        return "R"
    return "O"


def compress(seq: list[str]) -> str:
    out = []
    prev = None
    for item in seq:
        if item != prev:
            out.append(item)
            prev = item
    return "".join(out)


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%]+(?:'[A-Za-z]+)?", text)


def initials(text: str) -> str:
    return "".join(w[0] for w in words(text) if w)


def lasts(text: str) -> str:
    return "".join(w[-1] for w in words(text) if w)


def hits(value: str) -> list[str]:
    lower = value.lower()
    return [term for term in INSTRUCTION_TERMS if term in lower]


def main() -> None:
    runs = json.loads(RUNS_JSON.read_text())
    # Use the run-concatenated text as the search surface. The exported plain
    # text inserts line breaks that drift from run offsets, while this surface
    # preserves exact run order for font-state attribution.
    cursor = 0
    run_rows = []
    parts = []
    for run in runs:
        part = run["text"]
        run_rows.append({**run, "concatStart": cursor, "concatEnd": cursor + len(part)})
        parts.append(part)
        cursor += len(part)
    text = "".join(parts)
    edge_data = json.loads(EDGE_JSON.read_text())
    edge_by_id = {row["id"]: row for row in edge_data["records"]}

    phrase_rows = []
    for phrase in PHRASES:
        match = re.search(phrase["pattern"], text, flags=re.I)
        if not match:
            phrase_rows.append({**phrase, "found": False})
            continue
        start, end = match.span()
        overlapping = [run for run in run_rows if run["concatEnd"] > start and run["concatStart"] < end]
        char_styles = []
        char_variants = []
        for idx in range(start, end):
            run = next((r for r in overlapping if r["concatStart"] <= idx < r["concatEnd"]), None)
            if run:
                char_styles.append(style_code(run))
                char_variants.append(variant_for_run(run))
        style_counts = Counter(char_styles)
        variant_counts = Counter(char_variants)
        highlight_counts = Counter((run.get("highlight") or "none") for run in overlapping)
        dominant_style = style_counts.most_common(1)[0][0] if style_counts else "-"
        edge = edge_by_id.get(phrase["id"], {})
        phrase_rows.append(
            {
                **phrase,
                "found": True,
                "start": start,
                "end": end,
                "matchedText": text[start:end],
                "words": words(text[start:end]),
                "wordInitials": initials(text[start:end]),
                "wordLasts": lasts(text[start:end]),
                "styleCounts": dict(style_counts),
                "variantCounts": dict(variant_counts),
                "highlightCounts": dict(highlight_counts),
                "styleRun": compress(char_styles),
                "dominantStyle": dominant_style,
                "runIndices": [run["runIndex"] for run in overlapping],
                "runTexts": [run["text"] for run in overlapping],
                "edgeOverlap": edge.get("overlapFracOfCandidate"),
                "edgeContacts": edge.get("edgeContacts", []),
            }
        )

    found_rows = [row for row in phrase_rows if row.get("found")]
    frame_rows = [
        row
        for row in found_rows
        if row["id"] in edge_by_id
        and (
            (edge_by_id[row["id"]].get("overlapFracOfCandidate") or 0) > 0
            or edge_by_id[row["id"]].get("edgeContacts")
        )
    ]
    highlighted_or_mix_rows = [
        row for row in found_rows if row["dominantStyle"] in {"Y", "K", "M"} or "M" in row["styleRun"]
    ]
    streams = {
        "corridorDominantStyles": "".join(row["dominantStyle"] for row in found_rows),
        "corridorStyleRuns": "|".join(row["styleRun"] for row in found_rows),
        "corridorInitials": "".join(row["wordInitials"][:1] for row in found_rows),
        "corridorLasts": "".join(row["wordLasts"][-1:] for row in found_rows),
        "frameDominantStyles": "".join(row["dominantStyle"] for row in frame_rows),
        "frameInitials": "".join(row["wordInitials"][:1] for row in frame_rows),
        "frameLasts": "".join(row["wordLasts"][-1:] for row in frame_rows),
        "highlightMixDominantStyles": "".join(row["dominantStyle"] for row in highlighted_or_mix_rows),
        "highlightMixInitials": "".join(row["wordInitials"][:1] for row in highlighted_or_mix_rows),
        "highlightMixLasts": "".join(row["wordLasts"][-1:] for row in highlighted_or_mix_rows),
    }
    stream_hits = {name: hits(value) for name, value in streams.items()}

    assessment = [
        "The lower corridor has a real visual/font pattern, but it follows visible formatting: yellow/black highlights, regular prose, Typeka Mix names/phrases, then O5.",
        "The p78-frame-touched phrase stream mixes regular text, black highlight, Typeka Mix, and yellow highlight; it does not collapse to a readable instruction or a clear first/last/middle selector.",
        "Typeka Mix in this corridor marks semantic names/phrases (`Mike`, `trust that guy`) rather than a clean ordered alphabetic stream.",
        "This keeps Typeka as a formatting witness, not a final selector, unless a new external rule names which font state to read.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "phrase-level Typeka/font-state selector audit for page-76 lower corridor; no key derivation",
        "phrases": phrase_rows,
        "streams": streams,
        "streamInstructionHits": stream_hits,
        "assessment": assessment,
        "nextMove": "Do not rerun Typeka initials/lengths locally. Reopen font states only if a source clue specifies a font state or if a new source registration picks exact phrase units.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Lower Corridor Font-State Selector",
        "",
        "Scope: phrase-level Typeka/font-state audit for the page-76 lower corridor selected by p78 frame/marks. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
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
            "## Phrase Ledger",
            "",
            "| id | phrase | style | style run | variants | highlights | p78 frame relation |",
            "|---|---|---:|---|---|---|---|",
        ]
    )
    for row in phrase_rows:
        if not row.get("found"):
            lines.append(f"| {row['id']} | {row['label']} | - | not found | - | - | - |")
            continue
        relation = []
        if row.get("edgeOverlap") is not None:
            relation.append(f"overlap `{row['edgeOverlap']}`")
        for edge in row.get("edgeContacts", []):
            relation.append(f"{edge.get('edge')} {edge.get('relation')}")
        relation_text = "; ".join(relation) if relation else "-"
        lines.append(
            f"| {row['id']} | {row['label']} | `{row['dominantStyle']}` | `{row['styleRun']}` | `{row['variantCounts']}` | `{row['highlightCounts']}` | {relation_text} |"
        )

    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print("frameDominantStyles", streams["frameDominantStyles"], "hits", stream_hits["frameDominantStyles"])
    print("frameInitials", streams["frameInitials"], "hits", stream_hits["frameInitials"])


if __name__ == "__main__":
    main()
