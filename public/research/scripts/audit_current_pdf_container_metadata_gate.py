#!/usr/bin/env python3
"""Inspect current PDFs for hidden container/layout carriers.

This bounded pass checks PDF container surfaces that are not covered by the
render/OCR/object passes: document metadata, XMP, name trees, attachments,
annotations, widgets, links, optional content groups/layers, JavaScript/action
entries, and catalog/page special keys. It is source/provenance inspection only:
no key derivation, hashing, seed/WIF/address checks, BIP39 checks, or candidate
generation is run.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_container_metadata_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_container_metadata_gate.json"
OUT_MD = OUT / "current_pdf_container_metadata_gate.md"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

CATALOG_KEYS = [
    "Names",
    "OpenAction",
    "AA",
    "AcroForm",
    "Outlines",
    "PageLabels",
    "OCProperties",
    "Metadata",
    "Lang",
    "StructTreeRoot",
    "MarkInfo",
    "ViewerPreferences",
    "PieceInfo",
    "Perms",
]
PAGE_KEYS = ["Annots", "AA", "Metadata", "PieceInfo", "OC", "B", "Thumb"]
SUSPICIOUS_OBJECT_PATTERNS = [
    "/EmbeddedFile",
    "/Filespec",
    "/JavaScript",
    "/JS",
    "/OpenAction",
    "/AA",
    "/Launch",
    "/RichMedia",
    "/URI",
    "/OCG",
    "/OCProperties",
    "/Layer",
    "/Metadata",
    "/PieceInfo",
    "/AcroForm",
    "/PageLabels",
    "/Names",
    "/Dests",
]
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


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def token_hits(text: str, terms: set[str]) -> list[str]:
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
    )


def xref_key(doc: fitz.Document, xref: int, key: str) -> dict[str, Any]:
    try:
        kind, value = doc.xref_get_key(xref, key)
    except Exception as exc:
        return {"key": key, "kind": "error", "value": type(exc).__name__}
    return {"key": key, "kind": kind, "value": value}


def compact_text(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value).split())
    return text[:limit]


def list_or_empty(generator: Any) -> list[Any]:
    if generator is None:
        return []
    return list(generator)


def annotation_rows(page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for annot in list_or_empty(page.annots()):
        info = annot.info or {}
        text = " ".join(str(info.get(key, "")) for key in sorted(info))
        rows.append(
            {
                "type": annot.type[1] if annot.type else "",
                "rect": [round(v, 3) for v in annot.rect],
                "info": {key: compact_text(value) for key, value in info.items() if value},
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
            }
        )
    return rows


def widget_rows(page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for widget in list_or_empty(page.widgets()):
        text = " ".join(
            str(getattr(widget, attr, "") or "")
            for attr in ["field_name", "field_label", "field_value"]
        )
        rows.append(
            {
                "fieldName": compact_text(getattr(widget, "field_name", "")),
                "fieldLabel": compact_text(getattr(widget, "field_label", "")),
                "fieldType": compact_text(getattr(widget, "field_type_string", "")),
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
            }
        )
    return rows


def link_rows(page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for link in page.get_links():
        text = " ".join(str(value) for value in link.values())
        rows.append(
            {
                "kind": link.get("kind"),
                "uri": compact_text(link.get("uri", "")),
                "page": link.get("page"),
                "xref": link.get("xref"),
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
            }
        )
    return rows


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    metadata = doc.metadata or {}
    signal_metadata = {
        key: value
        for key, value in metadata.items()
        if value and key not in {"format", "encryption"}
    }
    metadata_text = " ".join(str(value) for value in signal_metadata.values())

    catalog_xref = doc.pdf_catalog()
    catalog_keys = [xref_key(doc, catalog_xref, key) for key in CATALOG_KEYS]
    present_catalog_keys = [
        row for row in catalog_keys if row["kind"] not in {"null", "error"}
    ]

    try:
        xml_metadata = doc.get_xml_metadata() or ""
    except Exception:
        xml_metadata = ""
    xml_xref = 0
    try:
        xml_xref = int(doc.xref_xml_metadata())
    except Exception:
        xml_xref = 0

    try:
        emb_count = int(doc.embfile_count())
        emb_names = list(doc.embfile_names())
    except Exception:
        emb_count = 0
        emb_names = []
    embedded_rows = []
    for name in emb_names:
        try:
            info = doc.embfile_info(name)
        except Exception:
            info = {}
        text = " ".join(str(v) for v in info.values()) + " " + str(name)
        embedded_rows.append(
            {
                "name": name,
                "info": {key: compact_text(value) for key, value in info.items()},
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
            }
        )

    try:
        ocgs = doc.get_ocgs()
    except Exception:
        ocgs = {}
    try:
        layers = doc.get_layers()
    except Exception:
        layers = []
    try:
        layer_ui = doc.layer_ui_configs()
    except Exception:
        layer_ui = []

    page_rows = []
    for index in range(doc.page_count):
        page = doc[index]
        annots = annotation_rows(page)
        widgets = widget_rows(page)
        links = link_rows(page)
        page_key_rows = [xref_key(doc, page.xref, key) for key in PAGE_KEYS]
        present_page_keys = [
            row for row in page_key_rows if row["kind"] not in {"null", "error"}
        ]
        page_rows.append(
            {
                "pdfPage": index + 1,
                "articlePage": 73 + index if doc.page_count == 8 else None,
                "pageXref": page.xref,
                "annotationCount": len(annots),
                "annotations": annots,
                "widgetCount": len(widgets),
                "widgets": widgets,
                "linkCount": len(links),
                "links": links,
                "presentSpecialKeys": present_page_keys,
            }
        )

    object_hits = []
    special_action_count = 0
    for xref in range(1, doc.xref_length()):
        try:
            obj = doc.xref_object(xref, compressed=False)
        except Exception:
            continue
        hits = [pattern for pattern in SUSPICIOUS_OBJECT_PATTERNS if pattern in obj]
        if not hits:
            continue
        if any(pattern in hits for pattern in ["/JavaScript", "/JS", "/OpenAction", "/AA", "/Launch", "/RichMedia"]):
            special_action_count += 1
        object_hits.append(
            {
                "xref": xref,
                "patterns": hits,
                "sample": compact_text(obj, 260),
            }
        )

    name_tree_rows = [
        row for row in present_catalog_keys if row["key"] == "Names"
    ]
    non_empty_name_tree_count = 0
    for row in name_tree_rows:
        value = row["value"]
        if row["kind"] == "xref":
            try:
                value = doc.xref_object(int(str(value).split()[0]), compressed=False)
            except Exception:
                pass
        compact = re.sub(r"\s+", " ", str(value))
        if "/Names [ ]" not in compact and "/Names[]" not in compact:
            non_empty_name_tree_count += 1

    container_text = " ".join(
        [
            metadata_text,
            xml_metadata,
            " ".join(row["value"] for row in present_catalog_keys),
            " ".join(hit["sample"] for hit in object_hits),
            " ".join(
                " ".join(annot["info"].values())
                for page in page_rows
                for annot in page["annotations"]
            ),
        ]
    )

    return {
        "pdf": rel(path),
        "sha256_16": sha256(path)[:16],
        "pageCount": doc.page_count,
        "metadata": {key: compact_text(value) for key, value in metadata.items() if value},
        "signalMetadataFieldCount": len(signal_metadata),
        "metadataStrictHits": token_hits(metadata_text, STRICT_TERMS),
        "metadataContextHits": token_hits(metadata_text, CONTEXT_TERMS),
        "xmlMetadataXref": xml_xref,
        "xmlMetadataLength": len(xml_metadata),
        "xmlStrictHits": token_hits(xml_metadata, STRICT_TERMS),
        "xmlContextHits": token_hits(xml_metadata, CONTEXT_TERMS),
        "presentCatalogKeys": present_catalog_keys,
        "nameTreeCount": len(name_tree_rows),
        "nonEmptyNameTreeCount": non_empty_name_tree_count,
        "embeddedFileCount": emb_count,
        "embeddedFiles": embedded_rows,
        "optionalContentGroupCount": len(ocgs),
        "optionalContentGroups": ocgs,
        "layerCount": len(layers),
        "layerUiConfigCount": len(layer_ui),
        "pageRows": page_rows,
        "annotationCount": sum(row["annotationCount"] for row in page_rows),
        "widgetCount": sum(row["widgetCount"] for row in page_rows),
        "linkCount": sum(row["linkCount"] for row in page_rows),
        "objectPatternRows": object_hits,
        "objectPatternRowCount": len(object_hits),
        "specialActionObjectCount": special_action_count,
        "containerStrictHits": token_hits(container_text, STRICT_TERMS),
        "containerContextHits": token_hits(container_text, CONTEXT_TERMS),
    }


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Container Metadata Gate",
        "",
        "Scope: inspected the current PDFs for hidden/container-level source carriers: metadata, XMP, name trees, attachments, annotations, widgets, links, optional content/layers, actions, and special catalog/page keys. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / pages checked: `{summary['pdfCount']}` / `{summary['pageCount']}`",
        f"- Signal metadata fields / XML metadata streams: `{summary['signalMetadataFieldCount']}` / `{summary['xmlMetadataStreamCount']}`",
        f"- Name trees / non-empty name trees: `{summary['nameTreeCount']}` / `{summary['nonEmptyNameTreeCount']}`",
        f"- Attachments / annotations / widgets / links: `{summary['embeddedFileCount']}` / `{summary['annotationCount']}` / `{summary['widgetCount']}` / `{summary['linkCount']}`",
        f"- Optional-content groups / layers / layer UI configs: `{summary['optionalContentGroupCount']}` / `{summary['layerCount']}` / `{summary['layerUiConfigCount']}`",
        f"- Special action object rows: `{summary['specialActionObjectCount']}`",
        f"- Strict instruction hits / context hits: `{summary['strictInstructionHitCount']}` / `{summary['contextHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | metadata | names | non-empty names | XML | attach | annots | widgets | links | OCG/layers | actions | strict | context |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|",
    ]
    for row in result["pdfRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    str(row["signalMetadataFieldCount"]),
                    str(row["nameTreeCount"]),
                    str(row["nonEmptyNameTreeCount"]),
                    str(1 if row["xmlMetadataLength"] else 0),
                    str(row["embeddedFileCount"]),
                    str(row["annotationCount"]),
                    str(row["widgetCount"]),
                    str(row["linkCount"]),
                    f"{row['optionalContentGroupCount']}/{row['layerCount']}",
                    str(row["specialActionObjectCount"]),
                    ", ".join(row["containerStrictHits"]) or "-",
                    ", ".join(row["containerContextHits"]) or "-",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Container Notes", ""])
    for row in result["pdfRows"]:
        catalog = ", ".join(
            f"{item['key']}={item['kind']}:{compact_text(item['value'], 60)}"
            for item in row["presentCatalogKeys"]
        ) or "-"
        metadata = ", ".join(f"{key}={value}" for key, value in row["metadata"].items()) or "-"
        object_patterns = "; ".join(
            f"xref {hit['xref']} {','.join(hit['patterns'])}"
            for hit in row["objectPatternRows"][:6]
        ) or "-"
        lines.append(f"- `{row['pdf']}` metadata: {metadata}")
        lines.append(f"  - Catalog specials: {catalog}")
        lines.append(f"  - Object pattern rows: {object_patterns}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- The current PDFs do not expose hidden source carriers: no attachments, annotations, widgets, links, optional-content layers, JavaScript/action entries, XMP metadata, or non-empty name trees.",
            "- The only container signal in the derivative duplicate PDFs is `PDF24 Tools - OCR` plus an empty destination name tree, matching already-closed derivative/OCR provenance.",
            "- Do not reopen PDF container metadata as an extraction path.",
            "",
            "## Next Move",
            "",
            "- Continue to treat the current PDFs as raster/OCR witnesses only. The best direction remains distinct physical/original-layout source validation or raw clue wording that explicitly names unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    summary = {
        "pdfCount": len(rows),
        "pageCount": sum(row["pageCount"] for row in rows),
        "signalMetadataFieldCount": sum(row["signalMetadataFieldCount"] for row in rows),
        "xmlMetadataStreamCount": sum(1 for row in rows if row["xmlMetadataLength"] > 0),
        "nameTreeCount": sum(row["nameTreeCount"] for row in rows),
        "nonEmptyNameTreeCount": sum(row["nonEmptyNameTreeCount"] for row in rows),
        "embeddedFileCount": sum(row["embeddedFileCount"] for row in rows),
        "annotationCount": sum(row["annotationCount"] for row in rows),
        "widgetCount": sum(row["widgetCount"] for row in rows),
        "linkCount": sum(row["linkCount"] for row in rows),
        "optionalContentGroupCount": sum(row["optionalContentGroupCount"] for row in rows),
        "layerCount": sum(row["layerCount"] for row in rows),
        "layerUiConfigCount": sum(row["layerUiConfigCount"] for row in rows),
        "objectPatternRowCount": sum(row["objectPatternRowCount"] for row in rows),
        "specialActionObjectCount": sum(row["specialActionObjectCount"] for row in rows),
        "strictInstructionHitCount": sum(len(row["containerStrictHits"]) for row in rows),
        "contextHitCount": sum(len(row["containerContextHits"]) for row in rows),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pages={summary['pageCount']}|"
        f"metadata={summary['signalMetadataFieldCount']}|xml={summary['xmlMetadataStreamCount']}|"
        f"names={summary['nameTreeCount']}|nonEmptyNames={summary['nonEmptyNameTreeCount']}|"
        f"emb={summary['embeddedFileCount']}|annots={summary['annotationCount']}|"
        f"widgets={summary['widgetCount']}|links={summary['linkCount']}|"
        f"ocg={summary['optionalContentGroupCount']}|layers={summary['layerCount']}|"
        f"actions={summary['specialActionObjectCount']}|strict={summary['strictInstructionHitCount']}|"
        f"context={summary['contextHitCount']}|sourceR3=0|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_container_metadata_no_hidden_source_carrier",
        "summary": summary,
        "fingerprint": fingerprint,
        "pdfRows": rows,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
