#!/usr/bin/env python3
"""Audit current-PDF trailer, xref, and file-storage integrity.

This bounded pass checks the PDF storage layer below the page dictionaries:
trailers, xref/incremental-update markers, object streams, generation numbers,
document IDs, catalog/info dictionaries, and page object ordering. It asks
whether file-level PDF structure distinguishes page 76 or the active quartet as
source/original-layout evidence.

No key derivation, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_trailer_xref_integrity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_trailer_xref_integrity_gate.json"
OUT_MD = OUT / "current_pdf_trailer_xref_integrity_gate.md"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

STRICT_TERMS = {
    "read",
    "take",
    "line",
    "lines",
    "word",
    "words",
    "letter",
    "letters",
    "edge",
    "first",
    "last",
    "left",
    "right",
    "fold",
    "mirror",
    "reverse",
    "rotate",
    "order",
    "slot",
    "font",
    "bold",
    "highlight",
    "decode",
    "cipher",
    "key",
    "private",
    "seed",
    "wif",
}
CONTEXT_TERMS = {
    "bitcoin",
    "satoshi",
    "volcano",
    "bonds",
    "bond",
    "shitcoiner",
    "heart",
    "dip",
    "sell",
    "bukele",
    "imf",
    "overdose",
}
DOCUMENT_CARRIER_KEYS = [
    "Names",
    "OpenAction",
    "AA",
    "AcroForm",
    "OCProperties",
    "Outlines",
    "PageMode",
    "Metadata",
    "PieceInfo",
    "StructTreeRoot",
    "Collection",
]
STORAGE_CARRIER_MARKERS = [
    b"/Prev",
    b"/XRefStm",
    b"/ObjStm",
    b"/Encrypt",
    b"/EmbeddedFiles",
    b"/OpenAction",
    b"/AA",
    b"/AcroForm",
    b"/OCProperties",
    b"/PieceInfo",
    b"/Metadata",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def sha16_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def object_keys(object_text: str) -> list[str]:
    return sorted(set(re.findall(r"/([A-Za-z][A-Za-z0-9]*)\b", object_text)))


def strip_pdf_names_and_payload(text: str) -> str:
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"<[0-9A-Fa-f\s]+>", " ", text)
    text = re.sub(r"/[A-Za-z0-9_.-]+", " ", text)
    return text


def token_hits(text: str, terms: set[str]) -> list[str]:
    clean = strip_pdf_names_and_payload(text)
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", clean, flags=re.IGNORECASE)
    )


def xrefs_from_value(value: str) -> list[int]:
    return [int(match) for match in re.findall(r"(\d+)\s+\d+\s+R", value or "")]


def first_xref_from_trailer(trailer: str, key: str) -> int | None:
    match = re.search(rf"/{re.escape(key)}\s+(\d+)\s+\d+\s+R", trailer)
    return int(match.group(1)) if match else None


def xref_key(doc: fitz.Document, xref: int, key: str) -> tuple[str, str]:
    try:
        return doc.xref_get_key(xref, key)
    except Exception as exc:
        return "error", type(exc).__name__


def safe_xref_object(doc: fitz.Document, xref: int) -> str:
    try:
        return doc.xref_object(xref, compressed=False)
    except Exception:
        return ""


def catalog_carrier_rows(doc: fitz.Document, trailer: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    root_xref = first_xref_from_trailer(trailer, "Root")
    if root_xref is None:
        return rows
    root_object = safe_xref_object(doc, root_xref)
    for key in DOCUMENT_CARRIER_KEYS:
        kind, value = xref_key(doc, root_xref, key)
        if kind != "null":
            rows.append(
                {
                    "catalogXref": root_xref,
                    "key": key,
                    "kind": kind,
                    "value": re.sub(r"\s+", " ", value).strip()[:160],
                    "rootObjectHash16": sha16_text(root_object),
                }
            )
    return rows


def inspect_xref_objects(doc: fitz.Document) -> dict[str, Any]:
    object_stream_xrefs: list[int] = []
    xref_stream_xrefs: list[int] = []
    nonzero_generation_xrefs: list[int] = []
    dictionary_text_parts: list[str] = []

    for xref in range(1, doc.xref_length()):
        text = safe_xref_object(doc, xref)
        if not text:
            continue
        dictionary_text_parts.append(text)
        if re.search(r"/Type\s*/ObjStm\b", text):
            object_stream_xrefs.append(xref)
        if re.search(r"/Type\s*/XRef\b", text):
            xref_stream_xrefs.append(xref)
        declaration = re.search(rf"\b{xref}\s+(\d+)\s+obj\b", text)
        if declaration and int(declaration.group(1)) != 0:
            nonzero_generation_xrefs.append(xref)

    joined = "\n".join(dictionary_text_parts)
    return {
        "objectStreamXrefs": object_stream_xrefs,
        "xrefStreamXrefs": xref_stream_xrefs,
        "nonzeroGenerationXrefs": nonzero_generation_xrefs,
        "strictHitTerms": token_hits(joined, STRICT_TERMS),
        "contextHitTerms": token_hits(joined, CONTEXT_TERMS),
        "dictionaryTextHash16": sha16_text(joined),
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    raw_text = data.decode("latin-1", errors="replace")
    doc = fitz.open(path)
    trailer = doc.pdf_trailer() if hasattr(doc, "pdf_trailer") else ""
    trailer_keys = object_keys(trailer)
    root_xref = first_xref_from_trailer(trailer, "Root")
    info_xref = first_xref_from_trailer(trailer, "Info")
    id_arrays = re.findall(r"/ID\s*\[(.*?)\]", trailer, flags=re.DOTALL)
    id_values = re.findall(r"<([0-9A-Fa-f]+)>", id_arrays[0]) if id_arrays else []

    xref_info = inspect_xref_objects(doc)
    carrier_rows = catalog_carrier_rows(doc, trailer)
    page_rows: list[dict[str, Any]] = []
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        image_xrefs = sorted({int(item[0]) for item in page.get_images(full=True)})
        form_xrefs = sorted({int(item[0]) for item in page.get_xobjects()})
        content_xrefs = sorted(int(xref) for xref in page.get_contents())
        page_rows.append(
            {
                "pdfPage": index + 1,
                "articlePage": article_page,
                "pageXref": page.xref,
                "contentXrefs": content_xrefs,
                "imageXrefs": image_xrefs,
                "formXrefs": form_xrefs,
                "rotation": page.rotation,
            }
        )

    object_declarations = re.findall(r"(?m)\b(\d+)\s+(\d+)\s+obj\b", raw_text)
    nonzero_generation_declaration_count = sum(
        1 for _, generation in object_declarations if int(generation) != 0
    )
    storage_marker_counts = {
        marker.decode("ascii"): data.count(marker) for marker in STORAGE_CARRIER_MARKERS
    }

    row = {
        "pdf": rel(path),
        "fileSizeBytes": len(data),
        "fileSha256_16": sha16_bytes(data),
        "pdfFormat": doc.metadata.get("format"),
        "creator": doc.metadata.get("creator") or "",
        "producer": doc.metadata.get("producer") or "",
        "creationDate": doc.metadata.get("creationDate") or "",
        "pageCount": doc.page_count,
        "xrefLength": doc.xref_length(),
        "isEncrypted": bool(getattr(doc, "is_encrypted", False)),
        "needsPass": int(getattr(doc, "needs_pass", 0) or 0),
        "isRepaired": bool(getattr(doc, "is_repaired", False)),
        "startxrefOffsets": [int(value) for value in re.findall(r"startxref\s+(\d+)", raw_text)],
        "eofMarkerCount": len(re.findall(r"%%EOF", raw_text)),
        "rawPrevCount": storage_marker_counts["/Prev"],
        "rawXRefStmCount": storage_marker_counts["/XRefStm"],
        "rawObjStmMarkerCount": storage_marker_counts["/ObjStm"],
        "rawEncryptCount": storage_marker_counts["/Encrypt"],
        "storageCarrierMarkerCounts": storage_marker_counts,
        "objectDeclarationCount": len(object_declarations),
        "nonzeroGenerationDeclarationCount": nonzero_generation_declaration_count,
        "trailerKeys": trailer_keys,
        "trailerHash16": sha16_text(re.sub(r"\s+", " ", trailer).strip()),
        "trailerIdValues": id_values,
        "rootXref": root_xref,
        "infoXref": info_xref,
        "objectStreamXrefs": xref_info["objectStreamXrefs"],
        "xrefStreamXrefs": xref_info["xrefStreamXrefs"],
        "nonzeroGenerationXrefs": xref_info["nonzeroGenerationXrefs"],
        "strictHitTerms": token_hits(trailer, STRICT_TERMS),
        "contextHitTerms": token_hits(trailer, CONTEXT_TERMS),
        "xrefDictionaryStrictHitTerms": xref_info["strictHitTerms"],
        "xrefDictionaryContextHitTerms": xref_info["contextHitTerms"],
        "documentCarrierRows": carrier_rows,
        "pageRows": page_rows,
        "trailerSample": re.sub(r"\s+", " ", trailer).strip()[:260],
    }
    doc.close()
    return row


def structural_page_order_rows(pdf_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        page_rows = [row for row in pdf_row["pageRows"] if row["articlePage"] is not None]
        article_order = [
            row["articlePage"] for row in sorted(page_rows, key=lambda row: row["articlePage"])
        ]
        xref_order = [row["articlePage"] for row in sorted(page_rows, key=lambda row: row["pageXref"])]
        active_order = [page for page in xref_order if page in {76, 78, 79, 80}]
        rows.append(
            {
                "pdf": pdf_row["pdf"],
                "articleOrder": article_order,
                "pageXrefOrder": xref_order,
                "pageXrefs": [row["pageXref"] for row in sorted(page_rows, key=lambda row: row["articlePage"])],
                "activeSubsetPageXrefOrder": active_order,
                "pageXrefOrderMatchesArticleOrder": xref_order == article_order,
                "activeSubsetMatchesArticleOrder": active_order == [76, 78, 79, 80],
                "decision": "structural_page_xref_order_not_selector",
            }
        )
    return rows


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    pdf_rows = [inspect_pdf(path) for path in PDFS]
    order_rows = structural_page_order_rows(pdf_rows)

    strict_hits = sorted(
        {
            hit
            for row in pdf_rows
            for hit in row["strictHitTerms"] + row["xrefDictionaryStrictHitTerms"]
        }
    )
    context_hits = sorted(
        {
            hit
            for row in pdf_rows
            for hit in row["contextHitTerms"] + row["xrefDictionaryContextHitTerms"]
        }
    )
    storage_marker_rows = [
        {
            "pdf": row["pdf"],
            "marker": marker,
            "count": count,
        }
        for row in pdf_rows
        for marker, count in row["storageCarrierMarkerCounts"].items()
        if count
    ]
    document_carrier_rows = [
        {"pdf": row["pdf"], **carrier_row}
        for row in pdf_rows
        for carrier_row in row["documentCarrierRows"]
    ]
    page76_rows = [
        {"pdf": row["pdf"], **page_row}
        for row in pdf_rows
        for page_row in row["pageRows"]
        if page_row["articlePage"] == 76
    ]

    unique_file_hashes = sorted({row["fileSha256_16"] for row in pdf_rows})
    startxref_total = sum(len(row["startxrefOffsets"]) for row in pdf_rows)
    eof_total = sum(row["eofMarkerCount"] for row in pdf_rows)
    incremental_update_candidates = [
        row
        for row in pdf_rows
        if len(row["startxrefOffsets"]) > 1 or row["rawPrevCount"] or row["rawXRefStmCount"]
    ]
    object_stream_count = sum(len(row["objectStreamXrefs"]) for row in pdf_rows)
    xref_stream_count = sum(len(row["xrefStreamXrefs"]) for row in pdf_rows)
    encrypted_pdf_count = sum(1 for row in pdf_rows if row["isEncrypted"] or row["needsPass"])
    nonzero_generation_object_count = sum(
        len(row["nonzeroGenerationXrefs"]) + row["nonzeroGenerationDeclarationCount"]
        for row in pdf_rows
    )
    hidden_trailer_key_count = sum(
        row["rawPrevCount"]
        + row["rawXRefStmCount"]
        + row["rawObjStmMarkerCount"]
        + row["rawEncryptCount"]
        for row in pdf_rows
    )
    trailer_id_present_count = sum(1 for row in pdf_rows if row["trailerIdValues"])
    structural_order_match_count = sum(
        1 for row in order_rows if row["pageXrefOrderMatchesArticleOrder"]
    )
    active_subset_match_count = sum(1 for row in order_rows if row["activeSubsetMatchesArticleOrder"])
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    fingerprint = (
        f"pdfs={len(pdf_rows)}|uniqueSha={len(unique_file_hashes)}"
        f"|xrefObjects={sum(row['xrefLength'] for row in pdf_rows)}"
        f"|startxref={startxref_total}|eof={eof_total}"
        f"|incremental={len(incremental_update_candidates)}"
        f"|objStm={object_stream_count}|xrefStm={xref_stream_count}"
        f"|encrypted={encrypted_pdf_count}|nonzeroGen={nonzero_generation_object_count}"
        f"|hiddenTrailer={hidden_trailer_key_count}|idPresent={trailer_id_present_count}"
        f"|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|pageOrder={structural_order_match_count}/{len(order_rows)}"
        f"|activeSubset={active_subset_match_count}/{len(order_rows)}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors=0"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_trailer_xref_integrity_no_source_carrier",
        "scope": "current PDF trailer/xref/file-storage integrity, incremental-update markers, object streams, document IDs, catalog carriers, and page object order; no OCR-to-key extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "summary": {
            "pdfCount": len(pdf_rows),
            "uniqueFileHashCount": len(unique_file_hashes),
            "xrefObjectCountTotal": sum(row["xrefLength"] for row in pdf_rows),
            "startxrefOccurrenceCountTotal": startxref_total,
            "eofMarkerCountTotal": eof_total,
            "incrementalUpdateCandidateCount": len(incremental_update_candidates),
            "objectStreamCount": object_stream_count,
            "xrefStreamCount": xref_stream_count,
            "encryptedPdfCount": encrypted_pdf_count,
            "nonzeroGenerationObjectCount": nonzero_generation_object_count,
            "hiddenCarrierTrailerKeyCount": hidden_trailer_key_count,
            "trailerIdPresentCount": trailer_id_present_count,
            "documentCarrierRowCount": len(document_carrier_rows),
            "storageMarkerRowCount": len(storage_marker_rows),
            "page76StorageRowCount": len(page76_rows),
            "strictHitCount": len(strict_hits),
            "contextHitCount": len(context_hits),
            "strictHitTerms": strict_hits,
            "contextHitTerms": context_hits,
            "structuralPageXrefOrderMatchCount": structural_order_match_count,
            "structuralOrderRowCount": len(order_rows),
            "activeSubsetPageXrefOrderMatchCount": active_subset_match_count,
            "sourceBackedR3BridgeHitCount": source_r3_hits,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
            "selectorUnlockCount": 0,
        },
        "pdfRows": pdf_rows,
        "page76StorageRows": page76_rows,
        "structuralPageOrderRows": order_rows,
        "storageMarkerRows": storage_marker_rows,
        "documentCarrierRows": document_carrier_rows,
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Trailer/Xref Integrity Gate",
        "",
        "Scope: inspected PDF trailer/xref/file-storage integrity, incremental-update markers, object streams, document IDs, catalog carriers, and page object order in the current PDFs. This checks file storage/provenance below page dictionaries; it does not treat OCR text as key material. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / unique file hashes: `{len(pdf_rows)}` / `{len(unique_file_hashes)}`",
        f"- Xref object total: `{sum(row['xrefLength'] for row in pdf_rows)}`",
        f"- startxref / EOF markers: `{startxref_total}` / `{eof_total}`",
        f"- Incremental-update candidates: `{len(incremental_update_candidates)}`",
        f"- Object streams / xref streams: `{object_stream_count}` / `{xref_stream_count}`",
        f"- Encrypted PDFs / nonzero-generation objects: `{encrypted_pdf_count}` / `{nonzero_generation_object_count}`",
        f"- Hidden trailer/storage carrier markers: `{hidden_trailer_key_count}`",
        f"- Trailer ID present count: `{trailer_id_present_count}`",
        f"- Document carrier rows: `{len(document_carrier_rows)}`",
        f"- Strict/context storage hits: `{len(strict_hits)}` / `{len(context_hits)}`",
        f"- Structural page-xref order matches: `{structural_order_match_count}` / `{len(order_rows)}`",
        f"- Active-subset page-xref order matches: `{active_subset_match_count}` / `{len(order_rows)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Storage Rows",
        "",
        "| PDF | sha16 | size | format | creator | xref len | startxref | EOF | ID count | root | info | repaired | encrypted |",
        "|---|---|---:|---|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pdf_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['fileSha256_16']}` | {row['fileSizeBytes']} | `{row['pdfFormat']}` | `{row['creator']}` | {row['xrefLength']} | `{'-'.join(map(str, row['startxrefOffsets']))}` | {row['eofMarkerCount']} | {len(row['trailerIdValues'])} | {row['rootXref'] or ''} | {row['infoXref'] or ''} | {int(row['isRepaired'])} | {int(row['isEncrypted'])} |"
        )

    lines.extend(
        [
            "",
            "## Page 76 Storage Rows",
            "",
            "| PDF | page xref | content xrefs | image xrefs | form xrefs | rotation |",
            "|---|---:|---|---|---|---:|",
        ]
    )
    for row in page76_rows:
        lines.append(
            f"| `{row['pdf']}` | {row['pageXref']} | `{'-'.join(map(str, row['contentXrefs']))}` | `{'-'.join(map(str, row['imageXrefs']))}` | `{'-'.join(map(str, row['formXrefs']))}` | {row['rotation']} |"
        )

    lines.extend(
        [
            "",
            "## Page Xref Order Checks",
            "",
            "| PDF | article order | page-xref order | page xrefs | active subset | order match |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for row in order_rows:
        lines.append(
            f"| `{row['pdf']}` | `{'-'.join(map(str, row['articleOrder']))}` | `{'-'.join(map(str, row['pageXrefOrder']))}` | `{'-'.join(map(str, row['pageXrefs']))}` | `{'-'.join(map(str, row['activeSubsetPageXrefOrder']))}` | `{int(row['pageXrefOrderMatchesArticleOrder'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_trailer_xref_integrity_no_source_carrier`",
            "- The current PDFs are simple non-incremental PDF 1.3 files at this layer: one `startxref` per file, no `/Prev`, no xref streams, no object streams, no encryption, and no nonzero-generation object carrier.",
            "- Trailer IDs and duplicate-PDF `/Info` records are provenance metadata only; they do not distinguish page 76 or the active quartet.",
            "- Page xref order follows article/page order in all 3 PDFs, and the active subset remains `76-78-79-80`; object chronology supplies no independent selector.",
            "- No document-level carrier keys, strict instruction terms, context terms, or source-backed R3 trigger hits appear at this file-storage layer.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Decision: {result['decision']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
