#!/usr/bin/env python3
"""Check whether active target punctuation/enclosure supplies the missing selector.

This bounded pass focuses on exact text mechanics around O4/B4/G5/O5:
quotes, dollar sign, and terminal punctuation. It inspects source-authority
text and correction records only. It does not derive keys, hash text, generate
seeds, scan WIF/Base58, OCR pages, or check addresses.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/plain_text_transcript/active_line_unit_reconciliation/active_line_unit_reconciliation.json"
TEXT_LOCK_JSON = ROOT / "analysis_outputs/plain_text_transcript/page76_target_text_authority_lock/page76_target_text_authority_lock.json"
FORMAT_LOCK_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
CORRECTION_JSON = ROOT / "analysis_outputs/plain_text_transcript/correction_selector_impact/correction_selector_impact.json"
OUT = ROOT / "analysis_outputs/plain_text_transcript/active_punctuation_enclosure_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "active_punctuation_enclosure_gate.json"
OUT_MD = OUT / "active_punctuation_enclosure_gate.md"
SHEET = OUT / "active_punctuation_enclosure_gate_sheet.jpg"

QUOTE_CHARS = {'"', "'", "\u201c", "\u201d", "\u2018", "\u2019"}
PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)
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


def load_json(path: Path) -> dict[str, Any]:
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


def instruction_hits(text: str) -> list[str]:
    lower = text.lower()
    return [term for term in INSTRUCTION_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)]


def first_alnum(text: str) -> str:
    match = re.search(r"[A-Za-z0-9$]", text)
    return match.group(0) if match else "-"


def last_alnum(text: str) -> str:
    match = re.search(r"[A-Za-z0-9$](?!.*[A-Za-z0-9$])", text)
    return match.group(0) if match else "-"


def punct_run_left(line: str, start: int) -> str:
    i = start - 1
    while i >= 0 and line[i].isspace():
        i -= 1
    chars = []
    while i >= 0 and PUNCT_RE.match(line[i]):
        chars.append(line[i])
        i -= 1
    return "".join(reversed(chars)) or "-"


def punct_run_right(line: str, end: int) -> str:
    i = end
    while i < len(line) and line[i].isspace():
        i += 1
    chars = []
    while i < len(line) and PUNCT_RE.match(line[i]):
        chars.append(line[i])
        i += 1
    return "".join(chars) or "-"


def find_phrase(line: str, phrase: str) -> tuple[int, int]:
    idx = line.lower().find(phrase.lower())
    if idx < 0:
        raise RuntimeError(f"phrase {phrase!r} not found in line {line!r}")
    return idx, idx + len(phrase)


def classify_context(record: dict[str, Any]) -> dict[str, Any]:
    line = record["canonicalLine"]
    phrase = record["label"]
    start, end = find_phrase(line, phrase)
    left_run = punct_run_left(line, start)
    right_run = punct_run_right(line, end)
    has_left_quote = any(ch in QUOTE_CHARS for ch in left_run)
    has_right_quote = any(ch in QUOTE_CHARS for ch in right_run)
    has_terminal_period = "." in right_run
    has_dollar = "$" in phrase

    classes = []
    if has_left_quote or has_right_quote:
        classes.append("quote")
    if has_dollar:
        classes.append("dollar")
    if has_terminal_period:
        classes.append("period")
    if not classes:
        classes.append("plain")

    if has_dollar:
        selector_pick = first_alnum(phrase)
        selector_rule = "dollar amount: first visible character"
    elif has_left_quote and has_right_quote and has_terminal_period:
        selector_pick = f"{first_alnum(phrase)}{last_alnum(phrase)}"
        selector_rule = "quoted with terminal punctuation: phrase edges"
    elif has_left_quote and has_right_quote:
        selector_pick = f"{first_alnum(phrase)}{last_alnum(phrase)}"
        selector_rule = "quoted phrase: phrase edges"
    elif has_terminal_period:
        selector_pick = last_alnum(phrase)
        selector_rule = "terminal punctuation: last character"
    else:
        selector_pick = first_alnum(phrase)
        selector_rule = "plain phrase: first character"

    return {
        "order": record["order"],
        "id": record["id"],
        "label": phrase,
        "visualState": record["visualState"],
        "pageLine": record["pageLine"],
        "corridorIndex": record["corridorIndex"],
        "canonicalLine": line,
        "leftRun": left_run,
        "rightRun": right_run,
        "hasLeftQuote": has_left_quote,
        "hasRightQuote": has_right_quote,
        "hasTerminalPeriod": has_terminal_period,
        "hasDollar": has_dollar,
        "class": "+".join(classes),
        "classInitial": "".join(part[0].upper() for part in classes),
        "phraseFirst": first_alnum(phrase),
        "phraseLast": last_alnum(phrase),
        "selectorPick": selector_pick,
        "selectorRule": selector_rule,
    }


def draw_sheet(result: dict[str, Any]) -> None:
    sheet_w, sheet_h = 1680, 980
    margin = 30
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title = font(34)
    normal = font(18)
    small = font(14)
    mono = font(14)

    draw.text((margin, margin), "Active Punctuation / Enclosure Gate", fill=(244, 247, 250), font=title)
    draw.text(
        (margin, margin + 46),
        "Checks whether quotes, dollar sign, or terminal punctuation around O4/B4/G5/O5 provide a readable selector.",
        fill=(176, 186, 198),
        font=normal,
    )

    y = margin + 92
    chips = [
        ("classes", result["summary"]["classStream"]),
        ("class initials", result["summary"]["classInitialStream"]),
        ("selector stream", result["summary"]["selectorPickStream"]),
        ("instruction hits", result["summary"]["instructionHitCount"]),
    ]
    widths = [390, 280, 360, 300]
    x = margin
    for (label, value), width in zip(chips, widths):
        draw.rectangle((x, y, x + width, y + 58), fill=(24, 30, 38), outline=(48, 57, 68))
        draw.text((x + 12, y + 9), label, fill=(129, 143, 158), font=small)
        draw.text((x + 12, y + 31), str(value)[:42], fill=(232, 239, 246), font=mono)
        x += width + 20

    y += 90
    draw.rectangle((margin, y, sheet_w - margin, y + 108), fill=(37, 30, 18), outline=(90, 70, 32))
    draw.text((margin + 14, y + 14), "Decision", fill=(255, 219, 137), font=normal)
    draw.text(
        (margin + 14, y + 46),
        "Active punctuation locks exact wording, but does not name a word/letter/order rule.",
        fill=(255, 219, 137),
        font=normal,
    )
    draw.text(
        (margin + 14, y + 76),
        "The correction layer restores O4/G5 punctuation/quotes; it does not add extraction permission.",
        fill=(255, 219, 137),
        font=normal,
    )

    y += 140
    draw.text((margin, y), "Active Contexts", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("target", 12), ("line", 300), ("class", 370), ("left", 600), ("right", 710), ("pick", 830), ("rule", 930)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["punctuationContexts"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 44), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 12), row["id"], fill=(176, 186, 198), font=small)
        draw.text((margin + 300, y + 12), str(row["pageLine"]), fill=(232, 239, 246), font=mono)
        draw.text((margin + 370, y + 12), row["class"], fill=(232, 239, 246), font=small)
        draw.text((margin + 600, y + 12), row["leftRun"], fill=(176, 186, 198), font=mono)
        draw.text((margin + 710, y + 12), row["rightRun"], fill=(176, 186, 198), font=mono)
        draw.text((margin + 830, y + 12), row["selectorPick"], fill=(232, 239, 246), font=mono)
        draw.text((margin + 930, y + 12), row["selectorRule"][:72], fill=(176, 186, 198), font=small)
        y += 48

    y += 24
    draw.text((margin, y), "Active Correction Rows", fill=(238, 243, 248), font=normal)
    y += 34
    draw.rectangle((margin, y, sheet_w - margin, y + 34), fill=(30, 35, 43))
    headers = [("index", 12), ("raw", 90), ("fixed", 520), ("selector?", 1110), ("targets", 1230)]
    for label, xoff in headers:
        draw.text((margin + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 38
    for row in result["activeCorridorCorrections"]:
        draw.rectangle((margin, y, sheet_w - margin, y + 46), fill=(18, 22, 28), outline=(48, 58, 70))
        draw.text((margin + 12, y + 13), str(row["index"]), fill=(176, 186, 198), font=mono)
        draw.text((margin + 90, y + 13), row["raw"][:52], fill=(176, 186, 198), font=small)
        draw.text((margin + 520, y + 13), row["fixed"][:70], fill=(232, 239, 246), font=small)
        draw.text((margin + 1110, y + 13), str(row["addsSelectorPermission"]), fill=(232, 239, 246), font=mono)
        draw.text((margin + 1230, y + 13), ",".join(row.get("activePhraseHitsFixed", [])), fill=(176, 186, 198), font=small)
        y += 50

    sheet.save(SHEET, quality=94)


def main() -> None:
    active = load_json(ACTIVE_JSON)
    text_lock = load_json(TEXT_LOCK_JSON)
    format_lock = load_json(FORMAT_LOCK_JSON)
    correction = load_json(CORRECTION_JSON)

    active_records = active.get("records", [])
    contexts = [classify_context(row) for row in active_records]
    active_corrections = [
        row for row in correction.get("rows", []) if row.get("affectsActiveCorridor")
    ]
    punctuation_corrections = [
        row for row in active_corrections if any(token in " ".join(row.get("addedTokens", []) + row.get("removedTokens", [])) for token in ['"', "\u201c", "\u201d", ".", "$", "-"])
    ]

    class_stream = " | ".join(row["class"] for row in contexts)
    class_initial_stream = " ".join(row["classInitial"] for row in contexts)
    selector_pick_stream = " ".join(row["selectorPick"] for row in contexts)
    phrase_edge_stream = " ".join(f"{row['phraseFirst']}{row['phraseLast']}" for row in contexts)
    boundary_run_stream = " ".join(f"{row['leftRun']}/{row['rightRun']}" for row in contexts)
    all_stream_text = " ".join([class_stream, class_initial_stream, selector_pick_stream, phrase_edge_stream, boundary_run_stream])
    hits = instruction_hits(all_stream_text)

    summary = {
        "activeTargetCount": len(contexts),
        "classStream": class_stream,
        "classInitialStream": class_initial_stream,
        "selectorPickStream": selector_pick_stream,
        "phraseEdgeStream": phrase_edge_stream,
        "boundaryRunStream": boundary_run_stream,
        "activePageLines": " ".join(str(row.get("pageLine")) for row in active_records),
        "activeCorridorIndexes": " ".join(str(row.get("corridorIndex")) for row in active_records),
        "activeVisualStateOrder": "".join(row.get("visualState", "") for row in active_records),
        "activeCorridorCorrectionCount": len(active_corrections),
        "activePunctuationCorrectionCount": len(punctuation_corrections),
        "instructionHitCount": len(hits),
        "instructionHits": hits,
        "selectorUnlocked": False,
    }

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "active punctuation/enclosure gate; no extraction, no key derivation, no hashing, no seed/WIF/address checks",
        "inputs": {
            "activeLineUnitReconciliation": rel(ACTIVE_JSON),
            "targetTextAuthorityLock": rel(TEXT_LOCK_JSON),
            "targetFormatAuthorityLock": rel(FORMAT_LOCK_JSON),
            "correctionSelectorImpact": rel(CORRECTION_JSON),
        },
        "summary": summary,
        "punctuationContexts": contexts,
        "activeCorridorCorrections": active_corrections,
        "sourceContext": {
            "textAuthorityDecision": text_lock.get("decision"),
            "formatAuthorityDecision": format_lock.get("decision"),
            "selectorPermissionCorrectionCount": correction.get("selectorPermissionCorrectionCount"),
        },
        "assessment": [
            "The active quartet has a real punctuation/enclosure pattern: O4 is quoted with terminal punctuation, B4 is a dollar amount, G5 is quoted, and O5 has terminal punctuation.",
            "That pattern is exact-text authority, not an extraction rule: the class stream and simple punctuation-directed edge picks contain no instruction terms.",
            "The correction layer matters for source fidelity because it moves O4 punctuation inside the quote and restores quoted `Volcano Bonds`, but those corrections add no selector permission.",
            "This closes punctuation/enclosure as a current-scan active quartet selector while preserving it as a source-comparison guardrail.",
        ],
        "decision": "active_punctuation_enclosure_is_text_authority_not_selector",
        "sheet": rel(SHEET),
        "nextMove": "Use active punctuation/enclosure only to validate exact source text in future scans/layout exports; reopen it as selector evidence only if raw clue wording names quote, dollar, punctuation, first/last, or edge extraction.",
    }

    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Active Punctuation / Enclosure Gate",
        "",
        "Scope: inspect quotes, dollar sign, and terminal punctuation around locked O4/B4/G5/O5 targets. No extraction, hashing, BIP39, WIF/Base58 scanning, seed generation, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{rel(SHEET)}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Summary",
        "",
        f"- Class stream: `{summary['classStream']}`.",
        f"- Class initials: `{summary['classInitialStream']}`.",
        f"- Punctuation-directed edge stream: `{summary['selectorPickStream']}`.",
        f"- Phrase edge stream: `{summary['phraseEdgeStream']}`.",
        f"- Active punctuation corrections: `{summary['activePunctuationCorrectionCount']}`.",
        f"- Instruction hit count: `{summary['instructionHitCount']}`.",
        "",
        "## Active Contexts",
        "",
        "| order | id | line | corridor | class | left run | right run | pick | rule |",
        "|---:|---|---:|---:|---|---|---|---|---|",
    ]
    for row in contexts:
        lines.append(
            f"| {row['order']} | `{row['id']}` | {row['pageLine']} | {row['corridorIndex']} | `{row['class']}` | `{row['leftRun']}` | `{row['rightRun']}` | `{row['selectorPick']}` | {row['selectorRule']} |"
        )

    lines.extend(["", "## Active Correction Rows", "", "| index | raw | fixed | targets | adds selector permission |", "|---:|---|---|---|---:|"])
    for row in active_corrections:
        lines.append(
            f"| {row['index']} | `{row['raw']}` | `{row['fixed']}` | `{','.join(row.get('activePhraseHitsFixed', [])) or '-'}` | `{row.get('addsSelectorPermission')}` |"
        )

    lines.extend(["", "## Assessment", ""])
    lines.extend(f"- {item}" for item in result["assessment"])
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("summary:", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
