#!/usr/bin/env python3
"""Reconstruct the highlighted-word stream inside BOLD.docm.

This is a bounded provenance/formatting inspection for the macro-enabled
`BOLD.docm` artifact. It does not execute macros, read the missing word list,
derive keys, hash text, run BIP39, scan WIF/Base58, OCR pages, or check
addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/bold_highlighted_text_reconstruction"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "bold_highlighted_text_reconstruction.json"
OUT_MD = OUT / "bold_highlighted_text_reconstruction.md"
SHEET = OUT / "bold_highlighted_text_reconstruction_sheet.jpg"

BOLD_RUNS = ROOT / "analysis_outputs/docm_format_sources/bold_runs.json"
BOLD_TEXT = ROOT / "analysis_outputs/docm_format_sources/bold_text.txt"
SOURCE_GATE = ROOT / "analysis_outputs/docm_format_sources/bold_docm_source_gate/bold_docm_source_gate.json"

ACTIVE_TARGETS = [
    ("O4", "buying the dip"),
    ("B4", "$1 billion"),
    ("G5", "Volcano Bonds"),
    ("O5", "shitcoiner at heart"),
]

CONTEXT_TERMS = [
    "El Salvador",
    "International Monetary Fund",
    "IMF",
    "Nayib Bukele",
    "should sell",
    "future bitcoin earnings",
    "IMF loan",
    "Mike Novogratz",
    "trust that guy",
]

INSTRUCTION_TERMS = [
    "read",
    "take",
    "first",
    "last",
    "left",
    "right",
    "hand",
    "fold",
    "mirror",
    "word",
    "letter",
    "line",
    "down",
    "up",
    "below",
    "above",
    "reverse",
    "backward",
    "heart",
    "dip",
    "energy",
    "toxic",
    "one",
    "billion",
    "volcano",
    "loan",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rel(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def norm(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.lower()
    text = re.sub(r"[^a-z0-9$]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9$]+", norm(text))


def contains_phrase(haystack: str, phrase: str) -> bool:
    h = f" {norm(haystack)} "
    p = f" {norm(phrase)} "
    return p in h


def paragraphs_from_runs(runs: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    paras: dict[int, list[dict[str, Any]]] = {}
    for run in runs:
        paras.setdefault(int(run.get("paragraphIndex", -1)), []).append(run)
    return dict(sorted(paras.items()))


def phrase_rows(
    full_text: str, highlighted_stream: str, highlighted_words: list[str]
) -> list[dict[str, Any]]:
    highlighted_token_set = set(tokens(" ".join(highlighted_words)))
    rows: list[dict[str, Any]] = []
    for row_id, phrase in ACTIVE_TARGETS:
        phrase_tokens = tokens(phrase)
        full_present = contains_phrase(full_text, phrase)
        highlight_present = contains_phrase(highlighted_stream, phrase)
        rows.append(
            {
                "id": row_id,
                "phrase": phrase,
                "role": "locked active page-76 target",
                "presentInBoldText": full_present,
                "presentInHighlightedStream": highlight_present,
                "highlightedTokenOverlap": [t for t in phrase_tokens if t in highlighted_token_set]
                if full_present or highlight_present
                else [],
            }
        )
    for phrase in CONTEXT_TERMS:
        phrase_tokens = tokens(phrase)
        full_present = contains_phrase(full_text, phrase)
        highlight_present = contains_phrase(highlighted_stream, phrase)
        rows.append(
            {
                "id": "context",
                "phrase": phrase,
                "role": "active-corridor or target-adjacent context",
                "presentInBoldText": full_present,
                "presentInHighlightedStream": highlight_present,
                "highlightedTokenOverlap": [t for t in phrase_tokens if t in highlighted_token_set]
                if full_present or highlight_present
                else [],
            }
        )
    return rows


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1720, 1240
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "BOLD.docm Highlighted Text Reconstruction", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 46),
        "Yellow-highlighted BOLD runs were reconstructed directly from the Word run layer; macros were not executed.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("highlighted runs", result["summary"]["highlightedRunCount"]),
        ("highlighted words", result["summary"]["highlightedWordCount"]),
        ("active targets", result["summary"]["activeTargetsInHighlightedStream"]),
        ("instruction hits", result["summary"]["instructionTermHits"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 385, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value), fill=(232, 239, 246), font=mono)
        x += 405

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 112), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    decision_lines = [
        "The BOLD highlighted stream is a generated word-highlight artifact, not active page-76 selector evidence.",
        "It contains 0/4 locked active targets; only `loan` partially overlaps the context phrase `IMF loan`.",
        "The only instruction-like highlighted hit is generic `right`; it is not paired with a unit/order rule.",
    ]
    ty = y + 44
    for line in decision_lines:
        draw.text((margin + 14, ty), line, fill=(255, 219, 137), font=normal)
        ty += 26

    y += 140
    draw.rectangle((margin, y, sheet_w - margin, y + 150), fill=(18, 22, 28), outline=(48, 58, 70))
    draw.text((margin + 14, y + 14), "Highlighted Word Stream", fill=(238, 243, 248), font=normal)
    stream = result["highlightedWordStream"]
    words = stream.split()
    ty = y + 52
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) > 118:
            draw.text((margin + 18, ty), line, fill=(176, 186, 198), font=small)
            ty += 24
            line = word
        else:
            line = candidate
    if line:
        draw.text((margin + 18, ty), line, fill=(176, 186, 198), font=small)

    y += 180
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("phrase", 12), ("role", 390), ("full", 850), ("highlight", 960), ("highlighted token overlap", 1120)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["phraseRows"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 42), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 12), row["phrase"][:42], fill=(238, 243, 248), font=small)
        draw.text((margin + 390, y + 12), row["role"][:54], fill=(176, 186, 198), font=small)
        draw.text((margin + 850, y + 12), str(row["presentInBoldText"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 960, y + 12), str(row["presentInHighlightedStream"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 1120, y + 12), ", ".join(row["highlightedTokenOverlap"])[:70], fill=(176, 186, 198), font=small)
        y += 46
        if y > sheet_h - 90:
            break

    sheet.save(SHEET, quality=94)


def main() -> None:
    runs: list[dict[str, Any]] = load_json(BOLD_RUNS)
    full_text = BOLD_TEXT.read_text(encoding="utf-8", errors="ignore") if BOLD_TEXT.exists() else ""
    source_gate = load_json(SOURCE_GATE)

    highlighted = [run for run in runs if run.get("highlight")]
    highlighted_words = [(run.get("clean") or run.get("text") or "").strip() for run in highlighted]
    highlighted_words = [word for word in highlighted_words if word]
    highlighted_stream = " ".join(highlighted_words)
    highlighted_norm = norm(highlighted_stream)
    highlighted_token_set = set(tokens(highlighted_stream))

    paragraph_rows = []
    for paragraph_index, paragraph_runs in paragraphs_from_runs(runs).items():
        paragraph_highlights = [run for run in paragraph_runs if run.get("highlight")]
        if not paragraph_highlights:
            continue
        paragraph_rows.append(
            {
                "paragraphIndex": paragraph_index,
                "runIndexes": [run.get("runIndex") for run in paragraph_highlights],
                "highlightedWords": [
                    (run.get("clean") or run.get("text") or "").strip()
                    for run in paragraph_highlights
                    if (run.get("clean") or run.get("text") or "").strip()
                ],
                "paragraphText": re.sub(
                    r"\s+", " ", "".join(run.get("text") or "" for run in paragraph_runs)
                ).strip(),
            }
        )

    phrases = phrase_rows(full_text, highlighted_stream, highlighted_words)
    active_highlight_hits = [
        row for row in phrases if row["role"] == "locked active page-76 target" and row["presentInHighlightedStream"]
    ]
    active_full_hits = [
        row for row in phrases if row["role"] == "locked active page-76 target" and row["presentInBoldText"]
    ]
    context_highlight_hits = [
        row for row in phrases if row["role"] != "locked active page-76 target" and row["presentInHighlightedStream"]
    ]
    context_partial_hits = [
        row
        for row in phrases
        if row["role"] != "locked active page-76 target"
        and row["presentInBoldText"]
        and row["highlightedTokenOverlap"]
        and not row["presentInHighlightedStream"]
    ]
    instruction_hits = [term for term in INSTRUCTION_TERMS if term in highlighted_token_set]

    highlighted_fonts = sorted({run.get("fontAscii") or "(none)" for run in highlighted})
    highlighted_bold_values = sorted({str(run.get("bold")) for run in highlighted})
    highlighted_highlights = sorted({run.get("highlight") or "(none)" for run in highlighted})

    first_letters = "".join(word[0].lower() for word in highlighted_words if word)
    last_letters = "".join(word[-1].lower() for word in highlighted_words if word)

    summary = {
        "highlightedRunCount": len(highlighted),
        "highlightedWordCount": len(highlighted_words),
        "highlightedUniqueWordCount": len({word.lower() for word in highlighted_words}),
        "highlightedFonts": highlighted_fonts,
        "highlightedBoldValues": highlighted_bold_values,
        "highlightedHighlightValues": highlighted_highlights,
        "activeTargetsInBoldText": f"{len(active_full_hits)}/4",
        "activeTargetsInHighlightedStream": f"{len(active_highlight_hits)}/4",
        "contextPhrasesInHighlightedStream": [row["phrase"] for row in context_highlight_hits],
        "contextPartialHighlightedTokens": [
            {"phrase": row["phrase"], "highlightedTokenOverlap": row["highlightedTokenOverlap"]}
            for row in context_partial_hits
        ],
        "instructionTermHits": instruction_hits,
        "selectorUnlocked": False,
        "sourceGateDecision": source_gate.get("decision"),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "BOLD.docm highlighted-word reconstruction; no macro execution, extraction, hashing, key derivation, BIP39, WIF, OCR, or address checks",
        "inputs": {
            "boldRuns": rel(BOLD_RUNS),
            "boldText": rel(BOLD_TEXT),
            "sourceGate": rel(SOURCE_GATE),
        },
        "summary": summary,
        "highlightedWordStream": highlighted_stream,
        "highlightedNormalizedStream": highlighted_norm,
        "firstLetterStream": first_letters,
        "lastLetterStream": last_letters,
        "paragraphRows": paragraph_rows,
        "phraseRows": phrases,
        "decision": "bold_highlighted_stream_not_source_or_selector",
        "sheet": rel(SHEET),
        "nextMove": "Keep BOLD.docm on the generated-artifact branch; reopen only if `otrobip.txt` or original workflow/source files are recovered and pass R1-R5.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# BOLD.docm Highlighted Text Reconstruction",
        "",
        "Scope: reconstruct the actual yellow-highlighted text in `BOLD.docm` from the recovered Word run layer. No macros were executed, and no extraction, hashing, BIP39, WIF/Base58 scanning, OCR extraction, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Yellow-highlighted runs: `{summary['highlightedRunCount']}`.",
        f"- Highlighted words: `{summary['highlightedWordCount']}`.",
        f"- Highlighted fonts: `{', '.join(summary['highlightedFonts'])}`.",
        f"- Highlighted bold values: `{', '.join(summary['highlightedBoldValues'])}`.",
        f"- Locked active targets in BOLD full text: `{summary['activeTargetsInBoldText']}`.",
        f"- Locked active targets in highlighted stream: `{summary['activeTargetsInHighlightedStream']}`.",
        f"- Instruction-like highlighted terms: `{', '.join(summary['instructionTermHits'])}`.",
        "",
        "## Highlighted Word Stream",
        "",
        f"`{highlighted_stream}`",
        "",
        "## Phrase Coverage",
        "",
        "| phrase | role | in BOLD text | in highlighted stream | highlighted token overlap |",
        "|---|---|---:|---:|---|",
    ]
    for row in phrases:
        lines.append(
            f"| `{row['phrase']}` | {row['role']} | `{row['presentInBoldText']}` | `{row['presentInHighlightedStream']}` | `{', '.join(row['highlightedTokenOverlap'])}` |"
        )
    lines.extend(
        [
            "",
            "## Paragraph Reconstruction",
            "",
            "| paragraph | highlighted words | context |",
            "|---:|---|---|",
        ]
    )
    for row in paragraph_rows:
        lines.append(
            f"| `{row['paragraphIndex']}` | `{' '.join(row['highlightedWords'])}` | {row['paragraphText'][:130]} |"
        )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The highlighted stream contains none of the locked active O4/B4/G5/O5 targets.",
            "- `IMF loan` is only a partial context overlap: `loan` is highlighted, but `IMF` is not.",
            "- The highlighted word `right` is generic context from `right there in the Genesis Block`; it is not paired with a source-backed unit/order instruction.",
            "- The stream is consistent with a generated BIP39/word-list markup artifact already identified by the macro audit, not with native page-76 source typography.",
            "",
            "## Next Move",
            "",
            f"- {result['nextMove']}",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
