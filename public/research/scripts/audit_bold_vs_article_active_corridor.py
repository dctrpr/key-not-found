#!/usr/bin/env python3
"""Compare BOLD.docm and Article with Fonts.docm around the active p76 corridor.

The goal is source authority, not key derivation. DOCM files are inspected as
OOXML ZIP packages only; macros are never executed.
"""

from __future__ import annotations

import json
import re
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "analysis_outputs/docm_format_sources/bold_vs_article_active_corridor"
BOLD_DOCM = Path("private_inputs/Desktop/BOLD.docm")
ARTICLE_DOCM = Path("private_inputs/Desktop/Article with Fonts.docm")

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

ACTIVE_PHRASES = [
    {"id": "O4", "phrase": "buying the dip", "role": "active orange target"},
    {"id": "B4", "phrase": "$1 billion", "role": "active black target"},
    {"id": "G5", "phrase": "Volcano Bonds", "role": "active grey target"},
    {"id": "O5", "phrase": "shitcoiner at heart", "role": "active orange target"},
    {"id": "context", "phrase": "El Salvador", "role": "page-76 corridor context"},
    {"id": "context", "phrase": "International Monetary Fund", "role": "page-76 corridor context"},
    {"id": "context", "phrase": "IMF", "role": "page-76 corridor context"},
    {"id": "context", "phrase": "Nayib Bukele", "role": "page-76 corridor context"},
    {"id": "context", "phrase": "should sell", "role": "p78 source/target-adjacent context"},
    {"id": "context", "phrase": "future bitcoin earnings", "role": "p78 source/target-adjacent context"},
    {"id": "context", "phrase": "IMF loan", "role": "page-76 corridor context"},
    {"id": "context", "phrase": "Mike Novogratz", "role": "page-76 corridor context"},
    {"id": "context", "phrase": "trust that guy", "role": "page-76 corridor context"},
]

INSTRUCTION_TERMS = [
    "read",
    "take",
    "use",
    "select",
    "count",
    "line",
    "word",
    "letter",
    "first",
    "last",
    "left",
    "right",
    "edge",
    "font",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "encoded",
]


def attr(el: ET.Element | None, name: str) -> str | None:
    if el is None:
        return None
    return el.attrib.get(W + name)


def bool_prop(rpr: ET.Element | None, prop: str) -> bool:
    if rpr is None:
        return False
    el = rpr.find(W + prop)
    if el is None:
        return False
    val = attr(el, "val")
    return val not in {"0", "false", "False", "off"}


def text_from_run(run: ET.Element) -> str:
    parts: list[str] = []
    for child in run:
        if child.tag == W + "t":
            parts.append(child.text or "")
        elif child.tag == W + "tab":
            parts.append("\t")
        elif child.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def run_signature(rpr: ET.Element | None) -> dict:
    fonts = rpr.find(W + "rFonts") if rpr is not None else None
    color = rpr.find(W + "color") if rpr is not None else None
    highlight = rpr.find(W + "highlight") if rpr is not None else None
    shd = rpr.find(W + "shd") if rpr is not None else None
    style = rpr.find(W + "rStyle") if rpr is not None else None
    return {
        "bold": bool_prop(rpr, "b"),
        "italic": bool_prop(rpr, "i"),
        "underline": rpr.find(W + "u") is not None if rpr is not None else False,
        "strike": bool_prop(rpr, "strike") or bool_prop(rpr, "dstrike"),
        "fontAscii": attr(fonts, "ascii"),
        "fontHAnsi": attr(fonts, "hAnsi"),
        "color": attr(color, "val"),
        "highlight": attr(highlight, "val"),
        "shadeFill": attr(shd, "fill"),
        "style": attr(style, "val"),
    }


def display_font(run: dict) -> str:
    return run.get("fontAscii") or run.get("fontHAnsi") or "(none)"


def parse_doc(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        xml = zf.read("word/document.xml")

    root = ET.fromstring(xml)
    paragraphs = []
    runs = []
    full_parts = []
    abs_pos = 0
    for p_idx, p in enumerate(root.iter(W + "p")):
        p_start = abs_pos
        p_text_parts = []
        p_run_indexes = []
        for run in p.findall(W + "r"):
            text = text_from_run(run)
            if text == "":
                continue
            rpr = run.find(W + "rPr")
            rec = {
                "runIndex": len(runs),
                "paragraphIndex": p_idx,
                "start": abs_pos,
                "end": abs_pos + len(text),
                "text": text,
                **run_signature(rpr),
            }
            runs.append(rec)
            p_run_indexes.append(rec["runIndex"])
            p_text_parts.append(text)
            full_parts.append(text)
            abs_pos += len(text)
        para_text = "".join(p_text_parts)
        if p_run_indexes or para_text.strip():
            paragraphs.append(
                {
                    "paragraphIndex": p_idx,
                    "start": p_start,
                    "end": abs_pos,
                    "runIndexes": p_run_indexes,
                    "text": para_text,
                }
            )
        full_parts.append("\n")
        abs_pos += 1

    full_text = "".join(full_parts)
    return {
        "path": str(path),
        "exists": path.exists(),
        "hasVbaProject": "word/vbaProject.bin" in names,
        "hasVbaData": "word/vbaData.xml" in names,
        "packagePartCount": len(names),
        "paragraphCount": len(paragraphs),
        "runCount": len(runs),
        "charCount": len(full_text),
        "wordCount": len(re.findall(r"[A-Za-z0-9$]+(?:'[A-Za-z0-9]+)?", full_text)),
        "fullText": full_text,
        "paragraphs": paragraphs,
        "runs": runs,
    }


def normalize_with_map(text: str) -> tuple[str, list[int]]:
    chars = []
    mapping = []
    for idx, ch in enumerate(text):
        lower = ch.lower()
        if lower.isalnum() or lower == "$":
            chars.append(lower)
            mapping.append(idx)
    return "".join(chars), mapping


def phrase_locations(text: str, phrase: str) -> list[tuple[int, int]]:
    norm_text, mapping = normalize_with_map(text)
    norm_phrase, _ = normalize_with_map(phrase)
    if not norm_phrase:
        return []
    out = []
    start = 0
    while True:
        pos = norm_text.find(norm_phrase, start)
        if pos == -1:
            break
        raw_start = mapping[pos]
        raw_end = mapping[pos + len(norm_phrase) - 1] + 1
        out.append((raw_start, raw_end))
        start = pos + 1
    return out


def overlapping_runs(runs: list[dict], start: int, end: int) -> list[dict]:
    return [run for run in runs if run["start"] < end and run["end"] > start]


def paragraph_for(paragraphs: list[dict], start: int, end: int) -> int | None:
    for paragraph in paragraphs:
        if paragraph["start"] <= start and paragraph["end"] >= end:
            return paragraph["paragraphIndex"]
    for paragraph in paragraphs:
        if paragraph["start"] < end and paragraph["end"] > start:
            return paragraph["paragraphIndex"]
    return None


def compact_counts(counter: Counter) -> dict[str, int]:
    return {str(key): value for key, value in counter.most_common() if key not in {None, ""}}


def summarize_match(doc: dict, phrase: str, start: int, end: int) -> dict:
    runs = overlapping_runs(doc["runs"], start, end)
    fonts = Counter(display_font(run) for run in runs)
    highlights = Counter(run.get("highlight") or "(none)" for run in runs)
    shades = Counter(run.get("shadeFill") or "(none)" for run in runs)
    bold_chars = 0
    total_chars = 0
    for run in runs:
        overlap_start = max(start, run["start"])
        overlap_end = min(end, run["end"])
        overlap = max(0, overlap_end - overlap_start)
        total_chars += overlap
        if run.get("bold"):
            bold_chars += overlap
    snippet_start = max(0, start - 60)
    snippet_end = min(len(doc["fullText"]), end + 90)
    snippet = re.sub(r"\s+", " ", doc["fullText"][snippet_start:snippet_end]).strip()
    return {
        "phrase": phrase,
        "start": start,
        "end": end,
        "paragraphIndex": paragraph_for(doc["paragraphs"], start, end),
        "runIndexes": [run["runIndex"] for run in runs],
        "fontCounts": compact_counts(fonts),
        "highlightCounts": compact_counts(highlights),
        "shadeFillCounts": compact_counts(shades),
        "boldCharFraction": round(bold_chars / total_chars, 3) if total_chars else 0,
        "snippet": snippet,
    }


def instruction_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lower)]


def audit_doc(name: str, path: Path) -> dict:
    doc = parse_doc(path)
    phrase_rows = []
    for entry in ACTIVE_PHRASES:
        locations = phrase_locations(doc["fullText"], entry["phrase"])
        matches = [summarize_match(doc, entry["phrase"], start, end) for start, end in locations]
        phrase_rows.append(
            {
                "id": entry["id"],
                "phrase": entry["phrase"],
                "role": entry["role"],
                "present": bool(matches),
                "matchCount": len(matches),
                "matches": matches,
            }
        )

    fonts = Counter(display_font(run) for run in doc["runs"])
    highlights = Counter(run.get("highlight") or "(none)" for run in doc["runs"])
    bold_runs = [run for run in doc["runs"] if run.get("bold")]
    text_hits = instruction_hits(doc["fullText"])
    active_present = [row["phrase"] for row in phrase_rows if row["id"] in {"O4", "B4", "G5", "O5"} and row["present"]]
    context_present = [row["phrase"] for row in phrase_rows if row["id"] == "context" and row["present"]]

    return {
        "name": name,
        "path": doc["path"],
        "hasVbaProject": doc["hasVbaProject"],
        "hasVbaData": doc["hasVbaData"],
        "packagePartCount": doc["packagePartCount"],
        "paragraphCount": doc["paragraphCount"],
        "runCount": doc["runCount"],
        "charCount": doc["charCount"],
        "wordCount": doc["wordCount"],
        "fontRunCounts": compact_counts(fonts),
        "highlightRunCounts": compact_counts(highlights),
        "boldRunCount": len(bold_runs),
        "instructionTermsInFullText": text_hits,
        "activePresent": active_present,
        "contextPresent": context_present,
        "phraseRows": phrase_rows,
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    docs = {
        "BOLD.docm": audit_doc("BOLD.docm", BOLD_DOCM),
        "Article with Fonts.docm": audit_doc("Article with Fonts.docm", ARTICLE_DOCM),
    }

    bold = docs["BOLD.docm"]
    article = docs["Article with Fonts.docm"]
    all_active = {"buying the dip", "$1 billion", "Volcano Bonds", "shitcoiner at heart"}
    bold_active_complete = set(bold["activePresent"]) == all_active
    article_active_complete = set(article["activePresent"]) == all_active

    assessment = [
        "Article with Fonts.docm contains all four locked active units and the surrounding El Salvador/IMF/Bukele/Novogratz corridor, so it remains the best Word-level formatting witness for the page-76 target cluster.",
        "BOLD.docm does not improve original-source authority because it contains an embedded VBA project and remains tied to the unrecovered word-list highlighting workflow already seen in the macro audit.",
        "BOLD.docm is useful only as a generated-markup witness. Any phrase or bold state found there must be confirmed against Article with Fonts.docm or the high-res magazine scan before it can drive extraction.",
        "No instruction-bearing phrase is introduced by the BOLD-vs-Article comparison; the visible instruction-like terms are ordinary article prose such as `sell`, not `read/take/line/word/letter/mirror/key` selector language.",
    ]
    if not bold_active_complete:
        assessment.insert(
            1,
            "BOLD.docm does not cover the full O4/B4/G5/O5 active set, so it cannot be the primary source for active-corridor extraction.",
        )
    else:
        assessment.insert(
            1,
            "BOLD.docm covers the active set, but its macro provenance means that agreement can only support transcription, not prove puzzle intent.",
        )

    decision = (
        "Keep Article with Fonts.docm as the trusted DOCM formatting witness; keep BOLD.docm on the generated-artifact branch unless the missing `otrobip.txt` source list is recovered."
    )
    next_move = (
        "Return to high-res magazine geometry and page-76 corridor ordering; use BOLD.docm only for sanity checks, not as a selector."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "BOLD.docm vs Article with Fonts.docm active page-76 corridor witness comparison. No key derivation.",
        "sources": {
            "bold": str(BOLD_DOCM),
            "articleWithFonts": str(ARTICLE_DOCM),
            "macroAudit": str((ROOT / "analysis_outputs/docm_format_sources/bold_docm_macro_audit.md").relative_to(ROOT)),
            "typekaManualBoldAudit": str(
                (
                    ROOT
                    / "analysis_outputs/docm_format_sources/typeka_manual_bold_disambiguation/typeka_manual_bold_disambiguation.md"
                ).relative_to(ROOT)
            ),
        },
        "activeSetComplete": {
            "BOLD.docm": bold_active_complete,
            "Article with Fonts.docm": article_active_complete,
        },
        "documents": docs,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "bold_vs_article_active_corridor.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# BOLD vs Article Active Corridor",
        "",
        "Scope: compare `BOLD.docm` and `Article with Fonts.docm` only around the locked page-76 active corridor. DOCM files were inspected as zipped Word packages; no macros were executed, and no key candidates were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- `BOLD.docm` active set complete: `{bold_active_complete}`",
        f"- `Article with Fonts.docm` active set complete: `{article_active_complete}`",
        "",
        "## Document Summary",
        "",
        "| document | macros | paragraphs | runs | words | fonts | highlights | active present | corridor context present |",
        "|---|---:|---:|---:|---:|---|---|---|---|",
    ]
    for name, doc in docs.items():
        fonts = ", ".join(f"{font}:{count}" for font, count in doc["fontRunCounts"].items()) or "-"
        highlights = ", ".join(f"{highlight}:{count}" for highlight, count in doc["highlightRunCounts"].items()) or "-"
        lines.append(
            f"| `{name}` | `{doc['hasVbaProject']}` | {doc['paragraphCount']} | {doc['runCount']} | "
            f"{doc['wordCount']} | `{fonts}` | `{highlights}` | `{', '.join(doc['activePresent']) or '-'}` | "
            f"`{', '.join(doc['contextPresent']) or '-'}` |"
        )

    lines.extend(["", "## Phrase Witnesses", "", "| phrase | role | BOLD.docm | Article with Fonts.docm |", "|---|---|---|---|"])
    for entry in ACTIVE_PHRASES:
        cells = []
        for doc in [bold, article]:
            row = next(item for item in doc["phraseRows"] if item["phrase"] == entry["phrase"])
            if not row["present"]:
                cells.append("absent")
                continue
            first = row["matches"][0]
            fonts = ", ".join(f"{font}:{count}" for font, count in first["fontCounts"].items()) or "-"
            highlights = ", ".join(f"{hi}:{count}" for hi, count in first["highlightCounts"].items()) or "-"
            cells.append(
                f"present para `{first['paragraphIndex']}`, fonts `{fonts}`, highlights `{highlights}`, bold `{first['boldCharFraction']}`"
            )
        lines.append(f"| `{entry['phrase']}` | {entry['role']} | {cells[0]} | {cells[1]} |")

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "bold_vs_article_active_corridor.md").write_text("\n".join(lines))

    print(OUT_DIR / "bold_vs_article_active_corridor.md")
    print(OUT_DIR / "bold_vs_article_active_corridor.json")


if __name__ == "__main__":
    main()
