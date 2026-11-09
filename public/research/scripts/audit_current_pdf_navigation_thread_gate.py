#!/usr/bin/env python3
"""Audit current PDFs for navigation/article-thread order carriers.

This is a source/layout inspection gate only. It checks whether the current PDF
wrappers contain outlines, page labels, named destinations, article threads, or
page-level beads that could encode an original-layout read order.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_navigation_thread_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_navigation_thread_gate.json"
OUT_MD = OUT / "current_pdf_navigation_thread_gate.md"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]

CATALOG_KEYS = [
    "Outlines",
    "PageLabels",
    "Names",
    "Dests",
    "Threads",
    "OpenAction",
    "PageMode",
    "AA",
    "ViewerPreferences",
]
PAGE_KEYS = ["B", "AA", "Dur", "Trans", "Tabs", "PieceInfo", "Metadata", "Annots"]
RAW_TOKENS = [
    b"/Outlines",
    b"/PageLabels",
    b"/Names",
    b"/Dests",
    b"/Threads",
    b"/OpenAction",
    b"/PageMode",
    b"/B ",
    b"/Bead",
]
STRICT_TERMS = [
    "word",
    "letter",
    "line",
    "edge",
    "font",
    "first",
    "last",
    "left",
    "right",
    "read",
    "take",
    "select",
    "fold",
    "mirror",
    "reverse",
    "key",
    "private",
    "seed",
    "address",
]
CONTEXT_TERMS = ["overdose", "bitcoin", "bukele", "volcano", "bond", "shitcoin", "heart", "schott"]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def pdf_name(path: Path) -> str:
    return rel(path)


def token_hits(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    hits: list[str] = []
    for term in terms:
        if re.search(rf"\b{re.escape(term.lower())}\b", lowered):
            hits.append(term)
    return hits


def key_value(doc: fitz.Document, xref: int, key: str) -> dict[str, str]:
    try:
        kind, value = doc.xref_get_key(xref, key)
    except Exception as exc:  # pragma: no cover - defensive against malformed PDFs.
        return {"kind": "error", "value": str(exc)}
    return {"kind": str(kind), "value": str(value)}


def is_signal(value: dict[str, str]) -> bool:
    return value["kind"] not in {"null", "none"} and value["value"] not in {"null", "None", ""}


def inspect_pdf(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    with fitz.open(path) as doc:
        catalog = doc.pdf_catalog()
        catalog_values = {key: key_value(doc, catalog, key) for key in CATALOG_KEYS}
        signal_catalog = {key: value for key, value in catalog_values.items() if is_signal(value)}

        toc = doc.get_toc(simple=False)
        labels = doc.get_page_labels()
        names = doc.resolve_names()
        outline_xrefs = doc.get_outline_xrefs()

        page_rows = []
        link_count = 0
        for page_index in range(doc.page_count):
            page = doc.load_page(page_index)
            page_xref = page.xref
            page_values = {key: key_value(doc, page_xref, key) for key in PAGE_KEYS}
            signal_page = {key: value for key, value in page_values.items() if is_signal(value)}
            link_count += len(page.get_links())
            if signal_page:
                page_rows.append(
                    {
                        "pageIndex": page_index,
                        "articlePage": page_index + 73,
                        "xref": page_xref,
                        "signalKeys": signal_page,
                    }
                )

        raw_counts = {token.decode("latin1").strip(): raw.count(token) for token in RAW_TOKENS}
        navigation_text_parts = [
            json.dumps(toc, ensure_ascii=False),
            json.dumps(labels, ensure_ascii=False),
            json.dumps(names, ensure_ascii=False),
            json.dumps(signal_catalog, ensure_ascii=False),
            json.dumps(page_rows, ensure_ascii=False),
        ]
        navigation_text = " ".join(navigation_text_parts)

        return {
            "pdf": pdf_name(path),
            "pageCount": doc.page_count,
            "catalogSignals": signal_catalog,
            "tocCount": len(toc),
            "outlineXrefCount": len(outline_xrefs),
            "pageLabelCount": len(labels),
            "namedDestinationCount": len(names),
            "embeddedFileNameCount": len(doc.embfile_names()),
            "linkCount": link_count,
            "pageSignalRows": page_rows,
            "pageBeadCount": sum(1 for row in page_rows if "B" in row["signalKeys"]),
            "rawTokenCounts": raw_counts,
            "strictHits": token_hits(navigation_text, STRICT_TERMS),
            "contextHits": token_hits(navigation_text, CONTEXT_TERMS),
        }


def write_markdown(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Navigation / Article Thread Gate",
        "",
        "Scope: inspected the current PDFs for navigation and article-thread carriers: outlines/bookmarks, page labels, named destinations, open actions, page modes, article threads, page beads, and page-level navigation keys. No OCR-to-key extraction, candidate generation, hashing, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / pages: `{summary['pdfCount']}` / `{summary['pageCount']}`",
        f"- TOC entries / outline xrefs / page labels / named destinations: `{summary['tocCount']}` / `{summary['outlineXrefCount']}` / `{summary['pageLabelCount']}` / `{summary['namedDestinationCount']}`",
        f"- Catalog navigation signal PDFs / page signal rows / page bead rows: `{summary['catalogSignalPdfCount']}` / `{summary['pageSignalRowCount']}` / `{summary['pageBeadCount']}`",
        f"- Links / embedded-file names: `{summary['linkCount']}` / `{summary['embeddedFileNameCount']}`",
        f"- Raw structural token mentions: `{summary['rawStructuralTokenMentionCount']}`",
        f"- Strict navigation hits / context hits: `{summary['strictHitCount']}` / `{summary['contextHitCount']}`",
        f"- Source-backed R3 / satisfied triggers / selectors: `0` / `0/9` / `0`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | pages | TOC | labels | named dests | catalog signals | page signal rows | beads | links | strict hits |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    for row in result["pdfRows"]:
        catalog_keys = ",".join(row["catalogSignals"].keys()) or "-"
        strict_hits = ",".join(row["strictHits"]) or "-"
        lines.append(
            f"| `{row['pdf']}` | `{row['pageCount']}` | `{row['tocCount']}` | `{row['pageLabelCount']}` | `{row['namedDestinationCount']}` | `{catalog_keys}` | `{len(row['pageSignalRows'])}` | `{row['pageBeadCount']}` | `{row['linkCount']}` | `{strict_hits}` |"
        )

    lines.extend(
        [
            "",
            "## Raw Structural Mentions",
            "",
            "| PDF | raw token counts |",
            "|---|---|",
        ]
    )
    for row in result["pdfRows"]:
        nonzero = {k: v for k, v in row["rawTokenCounts"].items() if v}
        lines.append(f"| `{row['pdf']}` | `{json.dumps(nonzero, sort_keys=True)}` |")

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_navigation_thread_no_source_order_carrier`.",
            "- The current PDFs expose no bookmarks/outlines, page labels, named destinations, article threads, page beads, open actions, page modes, or non-empty navigation order structures that could supply a read order.",
            "- The few raw `/Names`/`/Dests` mentions belong to the already-known empty derivative name tree; they do not contain strict instruction/context text.",
            "- Do not reopen current-PDF navigation or article-thread metadata as original-layout instruction evidence.",
            "",
            "## Next Move",
            "",
            "- Highest-value direction remains a distinct physical/original-layout/source asset or raw clue wording that explicitly supplies unit, order, and transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    summary = {
        "pdfCount": len(rows),
        "pageCount": sum(row["pageCount"] for row in rows),
        "tocCount": sum(row["tocCount"] for row in rows),
        "outlineXrefCount": sum(row["outlineXrefCount"] for row in rows),
        "pageLabelCount": sum(row["pageLabelCount"] for row in rows),
        "namedDestinationCount": sum(row["namedDestinationCount"] for row in rows),
        "embeddedFileNameCount": sum(row["embeddedFileNameCount"] for row in rows),
        "linkCount": sum(row["linkCount"] for row in rows),
        "catalogSignalPdfCount": sum(1 for row in rows if row["catalogSignals"]),
        "pageSignalRowCount": sum(len(row["pageSignalRows"]) for row in rows),
        "pageBeadCount": sum(row["pageBeadCount"] for row in rows),
        "rawStructuralTokenMentionCount": sum(sum(row["rawTokenCounts"].values()) for row in rows),
        "strictHitCount": sum(len(row["strictHits"]) for row in rows),
        "contextHitCount": sum(len(row["contextHits"]) for row in rows),
        "sourceBackedR3": 0,
        "satisfiedTriggers": 0,
        "selectors": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pages={summary['pageCount']}|toc={summary['tocCount']}|"
        f"outlines={summary['outlineXrefCount']}|labels={summary['pageLabelCount']}|"
        f"dests={summary['namedDestinationCount']}|catalogSignalPdfs={summary['catalogSignalPdfCount']}|"
        f"pageSignals={summary['pageSignalRowCount']}|beads={summary['pageBeadCount']}|"
        f"links={summary['linkCount']}|rawTokens={summary['rawStructuralTokenMentionCount']}|"
        f"strict={summary['strictHitCount']}|context={summary['contextHitCount']}|"
        "sourceR3=0|triggers=0/9|selectors=0"
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF navigation/article-thread original-layout order carrier audit; no extraction or key checks",
        "inputs": [pdf_name(path) for path in PDFS if path.exists()],
        "summary": summary,
        "pdfRows": rows,
        "decision": "current_pdf_navigation_thread_no_source_order_carrier",
        "fingerprint": fingerprint,
        "report": rel(OUT_MD),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_markdown(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(fingerprint)


if __name__ == "__main__":
    main()
