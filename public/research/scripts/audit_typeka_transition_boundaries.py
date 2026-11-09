#!/usr/bin/env python3
"""Audit Typeka font-change boundaries around the active page-76 corridor."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs" / "docm_format_sources" / "typeka_transition_boundaries"

RUNS_JSON = ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json"
FONT_AUDIT_JSON = ROOT / "analysis_outputs/docm_format_sources/docm_font_layer_audit.json"
COMPARISON_JSON = ROOT / "analysis_outputs/comparison_articles/overdose_style_uniqueness/overdose_style_uniqueness.json"

INSTRUCTION_TERMS = {
    "read",
    "take",
    "fold",
    "mirror",
    "reverse",
    "left",
    "right",
    "top",
    "bottom",
    "inside",
    "outside",
    "word",
    "letter",
    "line",
    "key",
    "private",
    "seed",
    "wif",
    "address",
    "index",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$]+", text)


def first_token(text: str) -> str:
    parts = words(text)
    return parts[0] if parts else ""


def last_token(text: str) -> str:
    parts = words(text)
    return parts[-1] if parts else ""


def first_char(text: str) -> str:
    match = re.search(r"[A-Za-z0-9$]", text)
    return match.group(0) if match else ""


def last_char(text: str) -> str:
    chars = re.findall(r"[A-Za-z0-9$]", text)
    return chars[-1] if chars else ""


def instruction_hits(text: str) -> list[str]:
    tokens = set(re.findall(r"[a-z]+", text.lower()))
    return sorted(tokens & INSTRUCTION_TERMS)


def font_name(run: dict[str, Any]) -> str:
    return run.get("fontAscii") or run.get("fontHAnsi") or ""


def font_variant(run: dict[str, Any]) -> str:
    font = font_name(run).lower()
    if "typeka mix" in font:
        return "M"
    if "typeka" in font and run.get("bold"):
        return "B"
    if "typeka" in font:
        return "R"
    return "O"


def visual_state(run: dict[str, Any]) -> str:
    variant = font_variant(run)
    highlight = (run.get("highlight") or "").lower()
    if variant == "M":
        return "M"
    if variant == "B" and highlight == "yellow":
        return "Y"
    if variant == "B" and highlight == "black":
        return "K"
    return variant


def run_page(run: dict[str, Any], bounds: list[dict[str, int]]) -> int | None:
    paragraph = run["paragraphIndex"]
    for bound in bounds:
        if bound["paragraphStart"] <= paragraph <= bound["paragraphEnd"]:
            return bound["page"]
    return None


def collapse_segments(runs: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    segments: list[dict[str, Any]] = []
    for run in runs:
        text = norm_text(run.get("text", ""))
        if not text:
            continue
        code = font_variant(run) if key == "fontVariant" else visual_state(run)
        if segments and segments[-1]["code"] == code and segments[-1]["paragraphEnd"] + 1 >= run["paragraphIndex"]:
            segments[-1]["text"] = norm_text(segments[-1]["text"] + " " + text)
            segments[-1]["runEnd"] = run["runIndex"]
            segments[-1]["paragraphEnd"] = run["paragraphIndex"]
        else:
            segments.append(
                {
                    "code": code,
                    "text": text,
                    "runStart": run["runIndex"],
                    "runEnd": run["runIndex"],
                    "paragraphStart": run["paragraphIndex"],
                    "paragraphEnd": run["paragraphIndex"],
                    "page": run["page"],
                }
            )
    return segments


def boundary_records(segments: list[dict[str, Any]]) -> list[dict[str, str]]:
    records = []
    for left, right in zip(segments, segments[1:]):
        record = {
            "transition": f"{left['code']}>{right['code']}",
            "leftCode": left["code"],
            "rightCode": right["code"],
            "leftText": left["text"],
            "rightText": right["text"],
            "leftLastWord": last_token(left["text"]),
            "rightFirstWord": first_token(right["text"]),
            "leftLastChar": last_char(left["text"]),
            "rightFirstChar": first_char(right["text"]),
        }
        record["pair"] = record["leftLastChar"] + record["rightFirstChar"]
        records.append(record)
    return records


def streams_from_segments(segments: list[dict[str, Any]], boundaries: list[dict[str, str]]) -> dict[str, str]:
    non_regular = [seg for seg in segments if seg["code"] != "R"]
    highlight_or_mix = [seg for seg in segments if seg["code"] in {"Y", "K", "M"}]
    return {
        "path": "".join(seg["code"] for seg in segments),
        "transitions": " ".join(b["transition"] for b in boundaries),
        "entryInitials": "".join(first_char(seg["text"]) for seg in segments[1:]),
        "boundaryPairs": " ".join(b["pair"] for b in boundaries),
        "rightEntryWords": " | ".join(b["rightFirstWord"] for b in boundaries),
        "leftExitWords": " | ".join(b["leftLastWord"] for b in boundaries),
        "nonRegularInitials": "".join(first_char(seg["text"]) for seg in non_regular),
        "nonRegularWords": " | ".join(first_token(seg["text"]) for seg in non_regular),
        "highlightMixInitials": "".join(first_char(seg["text"]) for seg in highlight_or_mix),
        "highlightMixWords": " | ".join(first_token(seg["text"]) for seg in highlight_or_mix),
    }


def page_sequences(runs: list[dict[str, Any]], key: str) -> dict[str, str]:
    by_page: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        if run["page"] in {75, 76, 77, 78, 79}:
            by_page[run["page"]].append(run)
    return {str(page): "".join(seg["code"] for seg in collapse_segments(items, key)) for page, items in sorted(by_page.items())}


def count_subsequence(sequence: str, needle: str) -> int:
    if not needle:
        return 0
    count = start = 0
    while True:
        idx = sequence.find(needle, start)
        if idx == -1:
            return count
        count += 1
        start = idx + 1


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    runs = load_json(RUNS_JSON)
    font_audit = load_json(FONT_AUDIT_JSON)
    comparison = load_json(COMPARISON_JSON)
    bounds = font_audit["pageBoundariesByParagraph"]

    enriched = []
    for run in runs:
        item = dict(run)
        item["page"] = run_page(run, bounds)
        enriched.append(item)

    # The bounded corridor is the page-76 El Salvador/Bukele/IMF/Volcano passage
    # from "Don't believe me?" through O5 "shitcoiner at heart".
    focus_runs = [
        run
        for run in enriched
        if run.get("page") == 76 and 60 <= run["paragraphIndex"] <= 73 and norm_text(run.get("text", ""))
    ]

    audits = {}
    for key in ("fontVariant", "visualState"):
        segments = collapse_segments(focus_runs, key)
        boundaries = boundary_records(segments)
        streams = streams_from_segments(segments, boundaries)
        audits[key] = {
            "segments": segments,
            "boundaries": boundaries,
            "streams": streams,
            "instructionHits": {name: instruction_hits(value) for name, value in streams.items() if instruction_hits(value)},
        }

    page_paths = {
        "fontVariant": page_sequences(enriched, "fontVariant"),
        "visualState": page_sequences(enriched, "visualState"),
    }
    uniqueness = {}
    for key in ("fontVariant", "visualState"):
        needle = audits[key]["streams"]["path"]
        uniqueness[key] = {
            "focusPath": needle,
            "pageOccurrences": {
                page: count_subsequence(path, needle) for page, path in page_paths[key].items()
            },
            "pagePaths": page_paths[key],
        }

    variant_counts = Counter(font_variant(run) for run in focus_runs)
    visual_counts = Counter(visual_state(run) for run in focus_runs)

    comparison_note = {
        "comparisonFontMetadataAvailable": False,
        "reason": "Existing comparison PDFs are image-only in the OVERDOSE style audit, so Typeka font metadata cannot be extracted from them.",
        "sourceDecision": comparison.get("decision", ""),
    }

    assessment = [
        "Font-change boundaries in the page-76 El Salvador corridor are real and concentrated, but their left/right boundary characters and entry words do not spell an instruction.",
        "Ignoring highlights, the focus font-variant path is a unique page-76 sequence in the DOCM witness; this supports the corridor as deliberate formatting/provenance, not a solved selector.",
        "With highlights included, the visual-state path is also unique to page 76, but it follows visible emphasis: El Salvador, buying the dip, Bukele, $1 billion, Volcano Bonds, IMF, Mike/Novogratz, trust, and O5.",
        "The comparison Max PDFs cannot adjudicate Typeka because they are image-only locally; they can only downgrade broad OVERDOSE style, not supply a font-layer extraction rule.",
        "Do not use font-boundary initials, boundary pairs, or transition codes as key material without a new rule naming a boundary side, font state, or exact order.",
    ]

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bounded Typeka/font transition-boundary audit for page-76 corridor; no key derivation",
        "sources": {
            "runs": str(RUNS_JSON.relative_to(ROOT)),
            "fontAudit": str(FONT_AUDIT_JSON.relative_to(ROOT)),
            "comparisonStyle": str(COMPARISON_JSON.relative_to(ROOT)),
        },
        "focus": {
            "page": 76,
            "paragraphRange": [60, 73],
            "runRange": [focus_runs[0]["runIndex"], focus_runs[-1]["runIndex"]] if focus_runs else [],
            "textPreview": norm_text(" ".join(run["text"] for run in focus_runs)),
            "variantCounts": dict(variant_counts),
            "visualStateCounts": dict(visual_counts),
        },
        "fontVariantAudit": audits["fontVariant"],
        "visualStateAudit": audits["visualState"],
        "uniqueness": uniqueness,
        "comparisonNote": comparison_note,
        "assessment": assessment,
        "decision": "Keep Typeka/font transitions as source and corridor evidence only; they do not currently supply the missing extraction unit.",
        "nextMove": "Inspect whether the high-res visual highlight boundaries, not DOCM font boundaries, produce a manual side-specific unit at the G5/O5 five-line corridor.",
    }

    json_path = OUT_DIR / "typeka_transition_boundaries.json"
    json_path.write_text(json.dumps(result, indent=2))

    lines = [
        "# Typeka Transition Boundaries",
        "",
        "Scope: audit whether changes between Typeka regular, Typeka Mix, and Typeka bold identify a readable boundary selector in the active page-76 corridor. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Focus: page `{result['focus']['page']}`, paragraphs `{result['focus']['paragraphRange'][0]}-{result['focus']['paragraphRange'][1]}`, runs `{result['focus']['runRange'][0]}-{result['focus']['runRange'][1]}`",
        f"- Font variant counts: `{result['focus']['variantCounts']}`",
        f"- Visual state counts: `{result['focus']['visualStateCounts']}`",
        "",
        "## Font-Only Variant Audit",
        "",
        "- Codes: `R` Typeka regular, `M` Typeka Mix, `B` Typeka bold.",
    ]
    for name, value in audits["fontVariant"]["streams"].items():
        hits = instruction_hits(value)
        lines.append(f"- `{name}` hits={hits or 'none'}: `{value}`")
    lines.extend(["", "### Font-Only Segments", "", "| code | runs | text |", "|---|---|---|"])
    for seg in audits["fontVariant"]["segments"]:
        lines.append(f"| `{seg['code']}` | `{seg['runStart']}-{seg['runEnd']}` | `{seg['text']}` |")

    lines.extend(
        [
            "",
            "## Highlight-Aware Visual State Audit",
            "",
            "- Codes: `R` Typeka regular, `M` Typeka Mix, `B` Typeka bold, `K` black-highlighted bold, `Y` yellow-highlighted bold.",
        ]
    )
    for name, value in audits["visualState"]["streams"].items():
        hits = instruction_hits(value)
        lines.append(f"- `{name}` hits={hits or 'none'}: `{value}`")
    lines.extend(["", "### Visual-State Segments", "", "| code | runs | text |", "|---|---|---|"])
    for seg in audits["visualState"]["segments"]:
        lines.append(f"| `{seg['code']}` | `{seg['runStart']}-{seg['runEnd']}` | `{seg['text']}` |")

    lines.extend(["", "## Boundary Records", "", "| mode | transition | pair | left word | right word |", "|---|---|---|---|---|"])
    for mode in ("fontVariant", "visualState"):
        for rec in audits[mode]["boundaries"]:
            lines.append(
                f"| `{mode}` | `{rec['transition']}` | `{rec['pair']}` | `{rec['leftLastWord']}` | `{rec['rightFirstWord']}` |"
            )

    lines.extend(["", "## Uniqueness Inside DOCM Witness", "", "| mode | focus path | page occurrences |", "|---|---|---|"])
    for mode, data in uniqueness.items():
        lines.append(f"| `{mode}` | `{data['focusPath']}` | `{data['pageOccurrences']}` |")

    lines.extend(
        [
            "",
            "## Comparison Note",
            "",
            f"- Comparison font metadata available: `{comparison_note['comparisonFontMetadataAvailable']}`.",
            f"- Reason: {comparison_note['reason']}",
            "",
            "## Assessment",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- {result['decision']}",
            f"- Next move: {result['nextMove']}",
            "",
        ]
    )
    (OUT_DIR / "typeka_transition_boundaries.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
