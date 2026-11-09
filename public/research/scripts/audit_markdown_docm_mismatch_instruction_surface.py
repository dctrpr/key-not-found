#!/usr/bin/env python3
"""Audit Markdown-bold versus DOCM formatting mismatch streams.

This pass tests whether the user-visible Markdown bold layer, especially in the
page-76 lower corridor, produces an instruction-like stream after alignment to
the DOCM font/highlight witness. It does not run extraction, hashing, key
derivation, WIF/Base58 scans, OCR, or address checks.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/docm_format_sources/markdown_docm_mismatch_instruction_surface"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "markdown_docm_mismatch_instruction_surface.json"
OUT_MD = OUT / "markdown_docm_mismatch_instruction_surface.md"
SHEET = OUT / "markdown_docm_mismatch_instruction_surface_sheet.jpg"

INPUTS = {
    "markdown": ROOT / "analysis_outputs/3d_article_map/user_markdown_transcript.md",
    "docm_text": ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_text.txt",
    "docm_runs": ROOT / "analysis_outputs/docm_format_sources/article_with_fonts_runs.json",
    "manual_bold": ROOT
    / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.json",
    "format_lock": ROOT
    / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json",
}

INSTRUCTION_TERMS = [
    "read",
    "take",
    "select",
    "word",
    "letter",
    "line",
    "page",
    "font",
    "bold",
    "mix",
    "typeka",
    "mirror",
    "fold",
    "reverse",
    "right",
    "left",
    "first",
    "last",
    "down",
    "up",
    "edge",
    "key",
    "private",
    "seed",
    "address",
    "order",
    "index",
]

CORRIDOR_START_PHRASE = "Don't believe me?"
CORRIDOR_END_PHRASE = "Maybe because he's a shitcoiner at heart."


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


def clean_markdown_text(text: str) -> str:
    text = text.replace("\\.", ".")
    text = text.replace("\\)", ")")
    text = text.replace("\\(", "(")
    text = text.replace("\\%", "%")
    return text


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    mapping: list[int] = []
    for idx, ch in enumerate(text):
        if ch.isalnum():
            chars.append(ch.lower())
            mapping.append(idx)
    return "".join(chars), mapping


def normalize(text: str) -> str:
    return normalize_with_map(text)[0]


def extract_markdown_bold_spans(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    i = 0
    open_start: int | None = None
    while i < len(text) - 1:
        if text[i : i + 2] == "**" and (i == 0 or text[i - 1] != "\\"):
            if open_start is None:
                open_start = i + 2
            else:
                raw = text[open_start:i]
                spans.append(
                    {
                        "order": len(spans) + 1,
                        "markdownStart": open_start,
                        "markdownEnd": i,
                        "text": clean_markdown_text(raw),
                        "norm": normalize(clean_markdown_text(raw)),
                    }
                )
                open_start = None
            i += 2
        else:
            i += 1
    return [span for span in spans if span["norm"]]


def overlap(a0: int, a1: int, b0: int, b1: int) -> int:
    return max(0, min(a1, b1) - max(a0, b0))


def run_stats(start: int, end: int, runs: list[dict[str, Any]]) -> dict[str, Any]:
    total = max(1, end - start)
    fonts: dict[str, int] = {}
    highlights: dict[str, int] = {}
    bold_chars = 0
    for run in runs:
        ov = overlap(start, end, int(run.get("start", 0)), int(run.get("end", 0)))
        if not ov:
            continue
        font_name = run.get("fontAscii") or run.get("fontHAnsi") or "unknown"
        fonts[font_name] = fonts.get(font_name, 0) + ov
        highlight = run.get("highlight") or "none"
        highlights[highlight] = highlights.get(highlight, 0) + ov
        if run.get("bold"):
            bold_chars += ov
    dominant_font = max(fonts.items(), key=lambda item: item[1])[0] if fonts else None
    dominant_highlight = max(highlights.items(), key=lambda item: item[1])[0] if highlights else None
    return {
        "length": total,
        "fonts": fonts,
        "dominantFont": dominant_font,
        "highlights": highlights,
        "dominantHighlight": dominant_highlight,
        "boldFraction": round(bold_chars / total, 3),
        "mixFraction": round(sum(count for name, count in fonts.items() if "Mix" in name) / total, 3),
        "highlightFraction": round(sum(count for name, count in highlights.items() if name != "none") / total, 3),
    }


def reconstruct_run_text(runs: list[dict[str, Any]]) -> str:
    max_end = max(int(run.get("end", 0)) for run in runs)
    chars = [" "] * max_end
    for run in runs:
        start = int(run.get("start", 0))
        for offset, ch in enumerate(run.get("text", "")):
            idx = start + offset
            if idx < max_end:
                chars[idx] = ch
    return "".join(chars)


def find_instruction_hits(text: str) -> list[str]:
    haystack = re.sub(r"[^a-z0-9]+", " ", text.lower())
    hits = []
    for term in INSTRUCTION_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", haystack):
            hits.append(term)
    return hits


def group_stream(spans: list[dict[str, Any]]) -> str:
    return " ".join(re.sub(r"\s+", " ", span["text"]).strip() for span in spans)


def build_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1620, 1040
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    normal = font(17)
    small = font(13)
    mono = font(15)

    draw.text((margin, margin), "Markdown vs DOCM Mismatch Surface", fill=(244, 247, 250), font=title_font)
    draw.text(
        (margin, margin + 45),
        "Sequentially aligns Markdown bold spans to DOCM text and checks whether mismatch streams contain instruction terms.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("markdown bold spans", result["summary"]["markdownBoldSpanCount"]),
        ("aligned", result["summary"]["alignedCount"]),
        ("corridor spans", result["summary"]["corridorMarkdownBoldSpanCount"]),
        ("markdown-only", result["summary"]["corridorMarkdownOnlySpanCount"]),
        ("docm-only targets", result["summary"]["corridorDocmOnlyActiveTargetCount"]),
        ("instruction hits", result["summary"]["totalInstructionHitCount"]),
    ]
    x = margin
    for label, value in chips:
        draw.rectangle((x, y, x + 230, y + 48), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 8), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 24), str(value), fill=(232, 239, 246), font=mono)
        x += 248

    y += 80
    draw.rectangle((margin, y, sheet_w - margin, y + 96), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Corridor Markdown-only stream", fill=(255, 219, 137), font=normal)
    stream = result["streams"]["corridorMarkdownOnlyStream"]
    draw.text((margin + 14, y + 44), stream[:180] or "(empty)", fill=(255, 219, 137), font=small)
    draw.text(
        (margin + 14, y + 68),
        f"instruction hits: {result['instructionHits']['corridorMarkdownOnlyStream']}",
        fill=(255, 219, 137),
        font=small,
    )

    y += 126
    headers = [("span", 12), ("DOCM font", 470), ("bold", 650), ("highlight", 750), ("reason", 930)]
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["corridorMarkdownRows"][:12]:
        fill = (31, 24, 16) if row["classification"] == "markdown_only_not_docm_bold" else (18, 22, 28)
        draw.rectangle((margin, y, sheet_w - margin, y + 54), fill=fill, outline=(48, 58, 70))
        draw.text((margin + 12, y + 9), row["text"][:56], fill=(238, 243, 248), font=small)
        draw.text((margin + 470, y + 9), str(row["dominantFont"]), fill=(210, 222, 236), font=small)
        draw.text((margin + 650, y + 9), str(row["boldFraction"]), fill=(210, 222, 236), font=mono)
        draw.text((margin + 750, y + 9), str(row["dominantHighlight"]), fill=(210, 222, 236), font=small)
        draw.text((margin + 930, y + 9), row["classification"], fill=(176, 186, 198), font=small)
        y += 58

    y += 16
    draw.rectangle((margin, y, sheet_w - margin, y + 118), fill=(20, 24, 30), outline=(50, 58, 70))
    draw.text((margin + 14, y + 14), "DOCM-bold active targets missed by Markdown bold", fill=(230, 235, 242), font=normal)
    missed = ", ".join(row["phrase"] for row in result["corridorDocmOnlyActiveTargets"]) or "none"
    draw.text((margin + 14, y + 48), missed, fill=(230, 235, 242), font=normal)
    draw.text(
        (margin + 14, y + 80),
        "Decision: mismatch streams are formatting-noise/context evidence only; they do not provide R3 unit/order.",
        fill=(176, 186, 198),
        font=normal,
    )

    sheet.save(SHEET, quality=94)


def main() -> None:
    markdown = INPUTS["markdown"].read_text(encoding="utf-8")
    runs = load_json(INPUTS["docm_runs"])
    docm_file_text = INPUTS["docm_text"].read_text(encoding="utf-8")
    docm_text = reconstruct_run_text(runs)
    manual = load_json(INPUTS["manual_bold"])
    format_lock = load_json(INPUTS["format_lock"])

    docm_norm, docm_map = normalize_with_map(docm_text)
    spans = extract_markdown_bold_spans(markdown)

    pointer = 0
    aligned: list[dict[str, Any]] = []
    unaligned: list[dict[str, Any]] = []
    for span in spans:
        idx = docm_norm.find(span["norm"], pointer)
        if idx < 0:
            idx = docm_norm.find(span["norm"])
        if idx < 0:
            unaligned.append(span)
            continue
        start = docm_map[idx]
        end = docm_map[idx + len(span["norm"]) - 1] + 1
        stats = run_stats(start, end, runs)
        row = {
            **span,
            "docmStart": start,
            "docmEnd": end,
            **stats,
        }
        aligned.append(row)
        pointer = idx + len(span["norm"])

    corridor_start = docm_text.find(CORRIDOR_START_PHRASE)
    corridor_end_start = docm_text.find(CORRIDOR_END_PHRASE)
    corridor_end = corridor_end_start + len(CORRIDOR_END_PHRASE)
    if corridor_start < 0 or corridor_end_start < 0:
        raise RuntimeError("could not locate page-76 corridor in DOCM text")

    corridor_spans = [
        row for row in aligned if overlap(row["docmStart"], row["docmEnd"], corridor_start, corridor_end)
    ]
    for row in corridor_spans:
        if row["boldFraction"] < 0.5 and row["highlightFraction"] < 0.5:
            row["classification"] = "markdown_only_not_docm_bold"
        elif row["highlightFraction"] >= 0.5:
            row["classification"] = "visual_highlight_or_docm_highlight"
        elif row["boldFraction"] >= 0.5:
            row["classification"] = "docm_bold_aligned"
        else:
            row["classification"] = "mixed"

    markdown_only = [row for row in corridor_spans if row["classification"] == "markdown_only_not_docm_bold"]
    highlighted_aligned = [row for row in corridor_spans if row["classification"] == "visual_highlight_or_docm_highlight"]

    manual_rows = manual.get("rows", [])
    corridor_docm_only_targets = [
        {
            "id": row.get("id"),
            "phrase": row.get("phrase"),
            "role": row.get("role"),
            "docmBoldFraction": row.get("docm", {}).get("boldFraction"),
            "docmHighlights": row.get("docm", {}).get("highlights"),
            "markdownBoldFraction": row.get("markdown", {}).get("boldFraction"),
        }
        for row in manual_rows
        if row.get("id") in {"one_billion", "volcano_bonds"}
        and row.get("docm", {}).get("boldFraction", 0) >= 0.9
        and row.get("markdown", {}).get("boldFraction", 0) < 0.1
    ]

    streams = {
        "corridorMarkdownOnlyStream": group_stream(markdown_only),
        "corridorHighlightedAlignedStream": group_stream(highlighted_aligned),
        "corridorDocmOnlyActiveTargetStream": " ".join(row["phrase"] for row in corridor_docm_only_targets),
    }
    instruction_hits = {name: find_instruction_hits(value) for name, value in streams.items()}

    summary = {
        "markdownBoldSpanCount": len(spans),
        "alignedCount": len(aligned),
        "unalignedCount": len(unaligned),
        "corridorWindow": {
            "start": corridor_start,
            "end": corridor_end,
            "startPhrase": CORRIDOR_START_PHRASE,
            "endPhrase": CORRIDOR_END_PHRASE,
        },
        "corridorMarkdownBoldSpanCount": len(corridor_spans),
        "corridorMarkdownOnlySpanCount": len(markdown_only),
        "corridorHighlightedAlignedSpanCount": len(highlighted_aligned),
        "corridorDocmOnlyActiveTargetCount": len(corridor_docm_only_targets),
        "totalInstructionHitCount": sum(len(value) for value in instruction_hits.values()),
        "formatLockDecision": format_lock.get("decision"),
        "activeVisualStateOrder": format_lock.get("summary", {}).get("activeVisualStateOrder"),
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Markdown-bold vs DOCM formatting mismatch instruction-surface audit; no extraction, no key derivation, no hashing, no OCR, no address checks",
        "inputs": {name: rel(path) for name, path in INPUTS.items()},
        "summary": summary,
        "docmTextAlignment": {
            "runReconstructedLength": len(docm_text),
            "fileTextLength": len(docm_file_text),
            "using": "run_reconstructed_text_for_font_offset_alignment",
        },
        "corridorMarkdownRows": [
            {
                "order": row["order"],
                "text": re.sub(r"\s+", " ", row["text"]).strip(),
                "docmStart": row["docmStart"],
                "docmEnd": row["docmEnd"],
                "dominantFont": row["dominantFont"],
                "boldFraction": row["boldFraction"],
                "mixFraction": row["mixFraction"],
                "dominantHighlight": row["dominantHighlight"],
                "highlightFraction": row["highlightFraction"],
                "classification": row["classification"],
            }
            for row in corridor_spans
        ],
        "corridorDocmOnlyActiveTargets": corridor_docm_only_targets,
        "streams": streams,
        "instructionHits": instruction_hits,
        "unalignedMarkdownSpans": [
            {"order": row["order"], "text": re.sub(r"\s+", " ", row["text"]).strip()}
            for row in unaligned[:20]
        ],
        "sheet": rel(SHEET),
        "decision": "markdown_docm_mismatch_no_r3_instruction",
        "nextMove": "Keep Markdown bold as an annotation/transcript layer and DOCM/high-res as format authority. Do not use mismatch streams unless a new source clue explicitly names Markdown-vs-font mismatch as the unit.",
    }

    build_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Markdown-DOCM Mismatch Instruction Surface",
        "",
        "Scope: align user Markdown bold spans to DOCM font/highlight runs and test the page-76 corridor mismatch streams for instruction-like wording. No extraction, key derivation, hashing, WIF/Base58 scanning, seed generation, OCR extraction, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Markdown bold spans: `{summary['markdownBoldSpanCount']}`",
        f"- Aligned to DOCM text: `{summary['alignedCount']}`",
        f"- Unaligned: `{summary['unalignedCount']}`",
        f"- Page-76 corridor Markdown bold spans: `{summary['corridorMarkdownBoldSpanCount']}`",
        f"- Corridor Markdown-only/not-DOCM-bold spans: `{summary['corridorMarkdownOnlySpanCount']}`",
        f"- Corridor DOCM-only active targets: `{summary['corridorDocmOnlyActiveTargetCount']}`",
        f"- Total instruction-term hits in tested mismatch streams: `{summary['totalInstructionHitCount']}`",
        "",
        "## Corridor Streams",
        "",
    ]
    for name, value in streams.items():
        lines.append(f"- `{name}`: `{value}`")
        lines.append(f"  - instruction hits: `{instruction_hits[name]}`")

    lines.extend(
        [
            "",
            "## Corridor Markdown Rows",
            "",
            "| order | text | DOCM font | bold | highlight | classification |",
            "|---:|---|---|---:|---|---|",
        ]
    )
    for row in result["corridorMarkdownRows"]:
        lines.append(
            f"| {row['order']} | `{row['text']}` | `{row['dominantFont']}` | `{row['boldFraction']}` | `{row['dominantHighlight']}` | `{row['classification']}` |"
        )

    lines.extend(["", "## DOCM-Only Active Targets", ""])
    for row in corridor_docm_only_targets:
        lines.append(
            f"- `{row['phrase']}`: DOCM bold `{row['docmBoldFraction']}`, DOCM highlights `{row['docmHighlights']}`, Markdown bold `{row['markdownBoldFraction']}`"
        )
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))
    print("instructionHits:", json.dumps(instruction_hits, ensure_ascii=False))


if __name__ == "__main__":
    main()
