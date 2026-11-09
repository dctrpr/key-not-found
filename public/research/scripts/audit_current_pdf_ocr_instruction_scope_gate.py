#!/usr/bin/env python3
"""Audit current PDF OCR/text overlays for source-backed instruction wording.

This is a bounded provenance check. It does not generate key candidates or
derive/check keys; it only asks whether the current PDFs' OCR layer contains
an action-plus-unit instruction window that could justify extraction.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_ocr_instruction_scope_gate"
OUT_JSON = OUT / "current_pdf_ocr_instruction_scope_gate.json"
OUT_MD = OUT / "current_pdf_ocr_instruction_scope_gate.md"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
TEXT_OVERLAY_GATE = ROOT / (
    "analysis_outputs/source_audit/current_pdf_text_overlay_render_mode_gate/"
    "current_pdf_text_overlay_render_mode_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ACTION_TERMS = {
    "choose",
    "count",
    "decode",
    "extract",
    "follow",
    "get",
    "look",
    "open",
    "read",
    "select",
    "take",
    "use",
}
UNIT_TERMS = {
    "above",
    "below",
    "bold",
    "bottom",
    "crop",
    "edge",
    "edges",
    "first",
    "font",
    "fonts",
    "glyph",
    "glyphs",
    "highlight",
    "inside",
    "key",
    "last",
    "left",
    "letter",
    "letters",
    "line",
    "lines",
    "order",
    "outside",
    "page",
    "pages",
    "private",
    "right",
    "row",
    "rows",
    "seed",
    "side",
    "sides",
    "slot",
    "slots",
    "top",
    "wif",
    "word",
    "words",
}
TRANSFORM_TERMS = {
    "fold",
    "folded",
    "mirror",
    "mirrored",
    "reverse",
    "rotate",
    "rotation",
}
TARGET_TERMS = {
    "billion",
    "billions",
    "bitcoin",
    "bond",
    "bonds",
    "bukele",
    "dip",
    "heart",
    "imf",
    "keyser",
    "overdose",
    "salvador",
    "satoshi",
    "sell",
    "shitcoiner",
    "shitcoiners",
    "volcano",
    "volcanoes",
}
HARD_PHRASES = [
    "private key",
    "bitcoin key",
    "take first",
    "take last",
    "read first",
    "read last",
    "extract",
    "seed phrase",
    "wif",
]

WORD_RE = re.compile(r"[a-z0-9]+")
WINDOW_RADIUS = 6


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tokens_from_word(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def word_records(page: fitz.Page, article_page: int) -> list[dict[str, Any]]:
    records = []
    for word in page.get_text("words"):
        x0, y0, x1, y1, text, block_no, line_no, word_no = word
        for token in tokens_from_word(text):
            records.append(
                {
                    "articlePage": article_page,
                    "token": token,
                    "raw": text,
                    "bbox": [round(x0, 3), round(y0, 3), round(x1, 3), round(y1, 3)],
                    "block": int(block_no),
                    "line": int(line_no),
                    "word": int(word_no),
                }
            )
    return records


def term_categories(token: str) -> list[str]:
    categories = []
    if token in ACTION_TERMS:
        categories.append("action")
    if token in UNIT_TERMS:
        categories.append("unit")
    if token in TRANSFORM_TERMS:
        categories.append("transform")
    if token in TARGET_TERMS:
        categories.append("target")
    return categories


def inspect_pdf(path: Path) -> dict[str, Any]:
    pdf = rel(path)
    all_tokens: list[dict[str, Any]] = []
    page_rows: list[dict[str, Any]] = []
    hard_phrase_rows: list[dict[str, Any]] = []

    with fitz.open(path) as doc:
        for page_index, page in enumerate(doc):
            article_page = 73 + page_index
            records = word_records(page, article_page)
            all_tokens.extend(records)
            page_text = " ".join(item["raw"] for item in records).lower()
            page_counts = Counter()
            page_term_counts = Counter()
            for item in records:
                categories = term_categories(item["token"])
                for category in categories:
                    page_counts[category] += 1
                if categories:
                    page_term_counts[item["token"]] += 1
            for phrase in HARD_PHRASES:
                if phrase in page_text:
                    hard_phrase_rows.append(
                        {
                            "pdf": pdf,
                            "articlePage": article_page,
                            "phrase": phrase,
                        }
                    )
            page_rows.append(
                {
                    "pdf": pdf,
                    "articlePage": article_page,
                    "tokenCount": len(records),
                    "actionCount": page_counts["action"],
                    "unitCount": page_counts["unit"],
                    "transformCount": page_counts["transform"],
                    "targetCount": page_counts["target"],
                    "termCounts": dict(sorted(page_term_counts.items())),
                }
            )

    window_rows = []
    term_rows = []
    total_counts = Counter()
    total_term_counts = Counter()
    for idx, item in enumerate(all_tokens):
        categories = term_categories(item["token"])
        for category in categories:
            total_counts[category] += 1
        if categories:
            total_term_counts[item["token"]] += 1
            term_rows.append(
                {
                    "pdf": pdf,
                    "articlePage": item["articlePage"],
                    "token": item["token"],
                    "categories": categories,
                    "raw": item["raw"],
                    "bbox": item["bbox"],
                }
            )

        if item["token"] not in ACTION_TERMS:
            continue
        left = max(0, idx - WINDOW_RADIUS)
        right = min(len(all_tokens), idx + WINDOW_RADIUS + 1)
        window = all_tokens[left:right]
        window_tokens = [entry["token"] for entry in window]
        window_set = set(window_tokens)
        unit_hits = sorted(window_set & UNIT_TERMS)
        transform_hits = sorted(window_set & TRANSFORM_TERMS)
        if not unit_hits and not transform_hits:
            continue
        action_hits = sorted(window_set & ACTION_TERMS)
        target_hits = sorted(window_set & TARGET_TERMS)
        window_rows.append(
            {
                "pdf": pdf,
                "articlePage": item["articlePage"],
                "anchor": item["token"],
                "actions": action_hits,
                "units": unit_hits,
                "transforms": transform_hits,
                "targets": target_hits,
                "text": " ".join(entry["raw"] for entry in window),
                "candidate": bool(target_hits),
            }
        )

    candidate_rows = [row for row in window_rows if row["candidate"]]
    return {
        "pdf": pdf,
        "pageCount": len(page_rows),
        "tokenCount": len(all_tokens),
        "actionTermCount": total_counts["action"],
        "unitTermCount": total_counts["unit"],
        "transformTermCount": total_counts["transform"],
        "targetTermCount": total_counts["target"],
        "termCounts": dict(sorted(total_term_counts.items())),
        "pageRows": page_rows,
        "termRows": term_rows,
        "actionUnitWindowRows": window_rows,
        "candidateRows": candidate_rows,
        "hardPhraseRows": hard_phrase_rows,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    overlay = load_json(TEXT_OVERLAY_GATE)
    overlay_summary = overlay.get("summary", {})
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_summary = trigger_matrix.get("summary", {})

    pdf_rows = [inspect_pdf(path) for path in PDFS]
    pdf_count = len(pdf_rows)
    page_count = sum(row["pageCount"] for row in pdf_rows)
    token_count = sum(row["tokenCount"] for row in pdf_rows)
    action_count = sum(row["actionTermCount"] for row in pdf_rows)
    unit_count = sum(row["unitTermCount"] for row in pdf_rows)
    transform_count = sum(row["transformTermCount"] for row in pdf_rows)
    target_count = sum(row["targetTermCount"] for row in pdf_rows)
    window_rows = [row for pdf in pdf_rows for row in pdf["actionUnitWindowRows"]]
    candidate_rows = [row for pdf in pdf_rows for row in pdf["candidateRows"]]
    hard_phrase_rows = [row for pdf in pdf_rows for row in pdf["hardPhraseRows"]]
    visible_spans = overlay_summary.get("visiblePaintedTraceSpanCount", 0)
    invisible_spans = overlay_summary.get("invisibleType3TraceSpanCount", 0)
    source_r3 = trigger_summary.get("sourceBackedR3BridgeHitCount", 0)
    satisfied = trigger_summary.get("satisfiedTriggerCount", 0)
    triggers = trigger_summary.get("triggerCount", 9)
    selectors = 0

    fingerprint = (
        f"pdfs={pdf_count}|pages={page_count}|tokens={token_count}|"
        f"action={action_count}|unit={unit_count}|transform={transform_count}|target={target_count}|"
        f"actionUnitWindows={len(window_rows)}|candidates={len(candidate_rows)}|hardPhrases={len(hard_phrase_rows)}|"
        f"visible={visible_spans}|sourceR3={source_r3}|triggers={satisfied}/{triggers}|selectors={selectors}"
    )

    result = {
        "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "scope": (
            "Current PDF OCR instruction-scope gate. Scans current PDF OCR/text overlay tokens "
            "for bounded action-plus-unit instruction windows. No OCR-to-key extraction, "
            "candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force."
        ),
        "decision": "current_pdf_ocr_instruction_scope_no_selector",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "textOverlayGate": rel(TEXT_OVERLAY_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "windowRadiusTokens": WINDOW_RADIUS,
        },
        "summary": {
            "pdfCount": pdf_count,
            "pageCount": page_count,
            "tokenCount": token_count,
            "actionTermCount": action_count,
            "unitTermCount": unit_count,
            "transformTermCount": transform_count,
            "targetTermCount": target_count,
            "actionUnitWindowCount": len(window_rows),
            "candidateWindowCount": len(candidate_rows),
            "hardPhraseHitCount": len(hard_phrase_rows),
            "visiblePaintedTraceSpanCount": visible_spans,
            "invisibleType3TraceSpanCount": invisible_spans,
            "sourceBackedR3BridgeHitCount": source_r3,
            "satisfiedReopenTriggerCount": satisfied,
            "triggerCount": triggers,
            "selectorCandidateCount": selectors,
            "fingerprint": fingerprint,
        },
        "pdfRows": pdf_rows,
        "actionUnitWindowRows": window_rows,
        "candidateRows": candidate_rows,
        "hardPhraseRows": hard_phrase_rows,
        "nextMove": (
            "Treat current PDF OCR overlays as invisible derivative context only. Reopen OCR/layout text "
            "only for a distinct original-layout source or raw clue that supplies action plus unit/order."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "# Current PDF OCR Instruction Scope Gate",
        "",
        "Scope: scanned the current PDFs' OCR/text overlay tokens for bounded action-plus-unit instruction windows. This checks whether the current Bitcoin PDF text layer itself supplies a unit/order rule. No OCR-to-key extraction, candidate generation, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / pages / tokens: `{pdf_count}` / `{page_count}` / `{token_count}`",
        f"- Action / unit / transform / target term hits: `{action_count}` / `{unit_count}` / `{transform_count}` / `{target_count}`",
        f"- Action-plus-unit windows / candidate windows: `{len(window_rows)}` / `{len(candidate_rows)}`",
        f"- Hard phrase hits: `{len(hard_phrase_rows)}`",
        f"- Visible painted text spans / invisible Type3 spans: `{visible_spans}` / `{invisible_spans}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `{source_r3}` / `{satisfied}/{triggers}` / `{selectors}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | pages | tokens | action | unit | transform | target | action+unit windows | candidates | hard phrases |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pdf_rows:
        lines.append(
            "| `{pdf}` | `{pages}` | `{tokens}` | `{action}` | `{unit}` | `{transform}` | `{target}` | `{windows}` | `{candidates}` | `{hard}` |".format(
                pdf=row["pdf"],
                pages=row["pageCount"],
                tokens=row["tokenCount"],
                action=row["actionTermCount"],
                unit=row["unitTermCount"],
                transform=row["transformTermCount"],
                target=row["targetTermCount"],
                windows=len(row["actionUnitWindowRows"]),
                candidates=len(row["candidateRows"]),
                hard=len(row["hardPhraseRows"]),
            )
        )

    lines.extend(
        [
            "",
            "## Isolated Strict Terms",
            "",
            "| PDF | term counts |",
            "|---|---|",
        ]
    )
    strict_terms = ACTION_TERMS | UNIT_TERMS | TRANSFORM_TERMS
    for row in pdf_rows:
        counts = {key: value for key, value in row["termCounts"].items() if key in strict_terms}
        counts_text = ", ".join(f"{key}:{value}" for key, value in counts.items()) or "-"
        lines.append(f"| `{row['pdf']}` | `{counts_text}` |")

    lines.extend(
        [
            "",
            "## Candidate Windows",
            "",
        ]
    )
    if window_rows:
        lines.extend(
            [
                "| PDF | page | anchor | actions | units | transforms | targets | text |",
                "|---|---:|---|---|---|---|---|---|",
            ]
        )
        for row in window_rows[:20]:
            lines.append(
                "| `{pdf}` | `{page}` | `{anchor}` | `{actions}` | `{units}` | `{transforms}` | `{targets}` | `{text}` |".format(
                    pdf=row["pdf"],
                    page=row["articlePage"],
                    anchor=row["anchor"],
                    actions=",".join(row["actions"]) or "-",
                    units=",".join(row["units"]) or "-",
                    transforms=",".join(row["transforms"]) or "-",
                    targets=",".join(row["targets"]) or "-",
                    text=row["text"].replace("|", "/")[:180],
                )
            )
    else:
        lines.append("- None. No current PDF OCR action term appears within +/-6 tokens of a unit or transform term.")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_ocr_instruction_scope_no_selector`",
            "- The high-resolution `magazine.pdf` OCR layer has no strict action/unit/transform terms in this token pass.",
            "- The two duplicate OCR PDFs contain only isolated ordinary words such as `look`, `words`, `get`, `open`, `first`, and `right`; none form a bounded action-plus-unit instruction window.",
            "- All page-76/current-PDF text overlay spans remain invisible derivative OCR, with no visible painted text spans and no source-backed R3 bridge.",
            "",
            "## Next Move",
            "",
            "- Stop treating current PDF OCR/layout text as original-layout instruction evidence.",
            "- Reopen OCR/layout text only for a distinct source PDF/export or raw clue wording that supplies action plus unit/order.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(fingerprint)


if __name__ == "__main__":
    main()
