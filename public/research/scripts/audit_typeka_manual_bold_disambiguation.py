#!/usr/bin/env python3
"""Disambiguate manual bold markup from DOCM Typeka/font states.

This pass is intentionally narrow: it checks only active lower page-76 corridor
phrases. It does not generate keys or candidate strings.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation"
OUT_JSON = OUT / "typeka_manual_bold_disambiguation.json"
OUT_MD = OUT / "typeka_manual_bold_disambiguation.md"

RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
MARKDOWN = ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md"

TARGETS = [
    {"id": "el_salvador", "phrase": "El Salvador", "role": "Typeka Mix nearby anchor"},
    {"id": "buying_dip", "phrase": "buying the dip", "role": "orange highlight phrase"},
    {"id": "one_billion", "phrase": "$1 billion", "role": "grey highlight / money phrase"},
    {"id": "should_sell", "phrase": "should sell", "role": "p78-frame source anchor"},
    {"id": "future_bitcoin_earnings", "phrase": "future bitcoin earnings", "role": "source band"},
    {"id": "volcano_bonds", "phrase": "Volcano Bonds", "role": "G5 target"},
    {"id": "imf_loan", "phrase": "IMF loan", "role": "G5 neighbor"},
    {"id": "tagged_mike", "phrase": "I tagged Mike", "role": "lower corridor anchor"},
    {"id": "novogratz", "phrase": "Novogratz", "role": "Typeka Mix nearby anchor"},
    {"id": "trust_that_guy", "phrase": "I don't really trust that guy", "role": "Typeka Mix local phrase"},
    {"id": "shitcoiner_heart", "phrase": "shitcoiner at heart", "role": "O5 target"},
]


def normalize(text: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\\.": ".",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip().lower()


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    mapping: list[int] = []
    previous_space = False
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
    }
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            i += 1
            ch = text[i]
        ch = replacements.get(ch, ch)
        if ch.isspace():
            if chars and not previous_space:
                chars.append(" ")
                mapping.append(i)
            previous_space = True
        else:
            chars.append(ch.lower())
            mapping.append(i)
            previous_space = False
        i += 1
    if chars and chars[-1] == " ":
        chars.pop()
        mapping.pop()
    return "".join(chars), mapping


def parse_markdown_bold(text: str) -> tuple[str, list[bool]]:
    clean: list[str] = []
    bold_flags: list[bool] = []
    bold = False
    i = 0
    while i < len(text):
        if text.startswith("**", i):
            bold = not bold
            i += 2
            continue
        if text[i] == "\\" and i + 1 < len(text):
            i += 1
        clean.append(text[i])
        bold_flags.append(bold)
        i += 1
    return "".join(clean), bold_flags


def find_span(text: str, phrase: str) -> tuple[int, int] | None:
    norm_text, mapping = normalize_with_map(text)
    norm_phrase = normalize(phrase)
    idx = norm_text.find(norm_phrase)
    if idx < 0:
        return None
    start = mapping[idx]
    end = mapping[idx + len(norm_phrase) - 1] + 1
    return start, end


def overlaps(a0: int, a1: int, b0: int, b1: int) -> int:
    return max(0, min(a1, b1) - max(a0, b0))


def run_state_for_span(runs: list[dict[str, Any]], start: int, end: int) -> dict[str, Any]:
    pieces = []
    total = max(1, end - start)
    font_counter: Counter[str] = Counter()
    highlight_counter: Counter[str] = Counter()
    bold_chars = 0
    mix_chars = 0
    for run in runs:
        ov = overlaps(start, end, int(run["start"]), int(run["end"]))
        if not ov:
            continue
        font = run.get("fontAscii") or run.get("fontHAnsi") or "UNKNOWN"
        highlight = run.get("highlight") or "none"
        font_counter[font] += ov
        highlight_counter[highlight] += ov
        if run.get("bold"):
            bold_chars += ov
        if font == "Typeka Mix":
            mix_chars += ov
        pieces.append(
            {
                "runIndex": run.get("runIndex"),
                "text": run.get("text", ""),
                "overlapChars": ov,
                "font": font,
                "bold": bool(run.get("bold")),
                "highlight": highlight,
            }
        )
    return {
        "span": [start, end],
        "dominantFont": font_counter.most_common(1)[0][0] if font_counter else None,
        "fonts": dict(font_counter),
        "highlights": dict(highlight_counter),
        "boldFraction": round(bold_chars / total, 3),
        "mixFraction": round(mix_chars / total, 3),
        "pieces": pieces,
    }


def markdown_state_for_span(clean_md: str, bold_flags: list[bool], phrase: str) -> dict[str, Any]:
    span = find_span(clean_md, phrase)
    if span is None:
        return {"present": False}
    start, end = span
    flags = bold_flags[start:end]
    return {
        "present": True,
        "span": [start, end],
        "boldFraction": round(sum(1 for flag in flags if flag) / max(1, len(flags)), 3),
    }


def positioned_run_text(runs: list[dict[str, Any]]) -> str:
    """Build text in the same coordinate space as run start/end offsets."""
    size = max(int(run["end"]) for run in runs)
    chars = [" "] * size
    for run in runs:
        start = int(run["start"])
        for offset, ch in enumerate(run.get("text", "")):
            pos = start + offset
            if 0 <= pos < size:
                chars[pos] = ch
    return "".join(chars)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    runs = json.loads(RUNS_JSON.read_text())
    docm_text = positioned_run_text(runs)
    markdown_text = MARKDOWN.read_text(encoding="utf-8")
    clean_md, md_bold_flags = parse_markdown_bold(markdown_text)

    rows = []
    disagreements = []
    for target in TARGETS:
        docm_span = find_span(docm_text, target["phrase"])
        if docm_span is None:
            docm_state = {"present": False}
        else:
            docm_state = {"present": True, **run_state_for_span(runs, *docm_span)}
        md_state = markdown_state_for_span(clean_md, md_bold_flags, target["phrase"])
        row = {**target, "docm": docm_state, "markdown": md_state}
        if docm_state.get("present") and md_state.get("present"):
            docm_boldish = docm_state.get("boldFraction", 0) >= 0.5
            md_boldish = md_state.get("boldFraction", 0) >= 0.5
            docm_mixish = docm_state.get("mixFraction", 0) >= 0.5
            if docm_boldish != md_boldish or docm_mixish:
                disagreements.append(
                    {
                        "id": target["id"],
                        "phrase": target["phrase"],
                        "docmBoldFraction": docm_state.get("boldFraction"),
                        "docmMixFraction": docm_state.get("mixFraction"),
                        "markdownBoldFraction": md_state.get("boldFraction"),
                        "reason": (
                            "Typeka Mix is a font-family state, not Word bold"
                            if docm_mixish
                            else "Markdown bold markup disagrees with DOCM bold property"
                        ),
                    }
                )
        rows.append(row)

    mix_targets = [row["id"] for row in rows if row["docm"].get("mixFraction", 0) >= 0.5]
    markdown_only_bold = [
        row["id"]
        for row in rows
        if row["markdown"].get("boldFraction", 0) >= 0.5 and row["docm"].get("boldFraction", 0) < 0.5
    ]
    docm_only_bold = [
        row["id"]
        for row in rows
        if row["docm"].get("boldFraction", 0) >= 0.5 and row["markdown"].get("boldFraction", 0) < 0.5
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active lower page-76 corridor Typeka/manual-bold disambiguation; no key derivation",
        "rows": rows,
        "summary": {
            "targets": len(rows),
            "docmTypekaMixDominantTargets": mix_targets,
            "markdownOnlyBoldTargets": markdown_only_bold,
            "docmOnlyBoldTargets": docm_only_bold,
            "disagreementCount": len(disagreements),
        },
        "disagreements": disagreements,
        "assessment": [
            "Manual Markdown bold markup is not a source-faithful substitute for DOCM font states.",
            "Typeka Mix appears as a font-family/provenance state around El Salvador, Mike, Novogratz, and trust-that-guy, not as Word bold.",
            "The active G5/O5 extraction pair remains DOCM-bold/highlighted Typeka, while nearby Typeka Mix is contextual styling rather than a clean selector.",
        ],
        "decision": "Use Article with Fonts.docm for font labels; treat old manual bold/partial-bold annotations as descriptive notes only.",
        "nextMove": "Do not reopen manual-bold extraction unless a new clue explicitly names font, Typeka, Mix, bold, or a specific selected word/line.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Typeka / Manual Bold Disambiguation",
        "",
        "Scope: active lower page-76 corridor only. This compares the DOCM font/bold/highlight witness against the user Markdown bold markup. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        "## Summary",
        "",
        f"- Targets checked: `{len(rows)}`.",
        f"- Dominant Typeka Mix targets in DOCM: `{', '.join(mix_targets) or 'none'}`.",
        f"- Markdown-bold but not DOCM-bold targets: `{', '.join(markdown_only_bold) or 'none'}`.",
        f"- DOCM-bold but not Markdown-bold targets: `{', '.join(docm_only_bold) or 'none'}`.",
        f"- Disagreement count: `{len(disagreements)}`.",
        "",
        "## Active Corridor Rows",
        "",
        "| id | phrase | DOCM dominant font | DOCM bold | DOCM Typeka Mix | DOCM highlights | Markdown bold |",
        "| --- | --- | --- | ---: | ---: | --- | ---: |",
    ]
    for row in rows:
        docm = row["docm"]
        md = row["markdown"]
        highlights = ", ".join(f"{k}:{v}" for k, v in docm.get("highlights", {}).items()) if docm.get("present") else "missing"
        lines.append(
            f"| `{row['id']}` | `{row['phrase']}` | `{docm.get('dominantFont')}` | "
            f"`{docm.get('boldFraction')}` | `{docm.get('mixFraction')}` | {highlights} | `{md.get('boldFraction')}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `Article with Fonts.docm` is the formatting witness for Typeka, Typeka Mix, bold, and highlight labels.",
            "- Manual Markdown bold should be treated as a user annotation layer, not as original puzzle typography.",
            "- Typeka Mix remains contextual/provenance evidence unless a new clue explicitly names font state or a stronger geometry selector first chooses exact units.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_JSON}")
    print("disagreements", len(disagreements))


if __name__ == "__main__":
    main()
