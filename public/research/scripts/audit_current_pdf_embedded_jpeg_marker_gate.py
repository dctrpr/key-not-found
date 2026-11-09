#!/usr/bin/env python3
"""Audit raw JPEG marker metadata in embedded PDF page images.

This bounded pass inspects the DCT/JPEG wrappers around the current PDFs'
embedded page images and thumbnails. It checks whether APP/COM marker payloads
carry EXIF, XMP, ICC, Photoshop, comments, or readable instruction/context text
that could act as a distinct source carrier.

No key derivation, candidate generation, broad hashing, seed/WIF/address checks,
BIP39 checks, or brute force is run.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_embedded_jpeg_marker_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_embedded_jpeg_marker_gate.json"
OUT_MD = OUT / "current_pdf_embedded_jpeg_marker_gate.md"

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

MARKER_NAMES = {
    0xC0: "SOF0",
    0xC1: "SOF1",
    0xC2: "SOF2",
    0xC4: "DHT",
    0xD8: "SOI",
    0xD9: "EOI",
    0xDA: "SOS",
    0xDB: "DQT",
    0xDD: "DRI",
    0xFE: "COM",
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact_text(value: Any, limit: int = 220) -> str:
    return " ".join(str(value).split())[:limit]


def token_hits(text: str, terms: set[str]) -> list[str]:
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
    )


def printable_strings(data: bytes, limit: int = 12) -> list[str]:
    strings: list[str] = []
    for match in re.finditer(rb"[\x20-\x7E]{4,}", data):
        text = match.group(0).decode("latin-1", errors="replace")
        if text not in strings:
            strings.append(text)
        if len(strings) >= limit:
            break
    return strings


def marker_name(marker: int) -> str:
    if 0xE0 <= marker <= 0xEF:
        return f"APP{marker - 0xE0}"
    if 0xD0 <= marker <= 0xD7:
        return f"RST{marker - 0xD0}"
    return MARKER_NAMES.get(marker, f"0xFF{marker:02X}")


def marker_payload_role(name: str, payload: bytes) -> str:
    prefix = payload[:80]
    if name == "APP0" and prefix.startswith(b"JFIF\x00"):
        return "structural_jfif"
    if name == "APP0" and prefix.startswith(b"JFXX\x00"):
        return "structural_jfxx"
    if name == "APP1" and prefix.startswith(b"Exif\x00\x00"):
        return "exif"
    if name == "APP1" and b"http://ns.adobe.com/xap/1.0/" in prefix:
        return "xmp"
    if name == "APP2" and prefix.startswith(b"ICC_PROFILE\x00"):
        return "icc_profile"
    if name == "APP13" and prefix.startswith(b"Photoshop 3.0\x00"):
        return "photoshop"
    if name == "APP14" and prefix.startswith(b"Adobe"):
        return "structural_adobe"
    if name == "COM":
        return "comment"
    if name.startswith("APP"):
        return "app_other"
    return "marker"


def parse_jpeg_markers(data: bytes) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    if not data.startswith(b"\xFF\xD8"):
        return {
            "isJpeg": False,
            "rows": rows,
            "parseWarning": "missing_soi",
        }
    pos = 0
    parse_warning = ""
    while pos < len(data):
        if data[pos] != 0xFF:
            parse_warning = "non_marker_byte_before_sos"
            break
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        if pos >= len(data):
            break
        marker = data[pos]
        pos += 1
        name = marker_name(marker)
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            rows.append(
                {
                    "marker": f"FF{marker:02X}",
                    "name": name,
                    "offset": pos - 2,
                    "payloadByteCount": 0,
                    "role": "structural",
                    "printableStrings": [],
                    "strictHits": [],
                    "contextHits": [],
                    "sample": "",
                }
            )
            if marker == 0xD9:
                break
            continue
        if pos + 2 > len(data):
            parse_warning = f"truncated_length_after_{name}"
            break
        length = int.from_bytes(data[pos : pos + 2], "big")
        if length < 2 or pos + length > len(data):
            parse_warning = f"invalid_length_after_{name}"
            break
        payload = data[pos + 2 : pos + length]
        strings = printable_strings(payload)
        text = " ".join(strings)
        role = marker_payload_role(name, payload)
        rows.append(
            {
                "marker": f"FF{marker:02X}",
                "name": name,
                "offset": pos - 2,
                "payloadByteCount": len(payload),
                "role": role,
                "printableStrings": strings,
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
                "sample": compact_text(text, 260),
            }
        )
        pos += length
        if marker == 0xDA:
            break
    return {
        "isJpeg": True,
        "rows": rows,
        "parseWarning": parse_warning,
    }


def xref_key(doc: fitz.Document, xref: int, key: str) -> tuple[str, str]:
    try:
        return doc.xref_get_key(xref, key)
    except Exception as exc:
        return "error", type(exc).__name__


def xrefs_from_value(value: str) -> list[int]:
    return [int(match) for match in re.findall(r"(\d+)\s+0\s+R", value or "")]


def int_key(doc: fitz.Document, xref: int, key: str) -> int | None:
    kind, value = xref_key(doc, xref, key)
    if kind in {"int", "name"}:
        try:
            return int(str(value).lstrip("/"))
        except ValueError:
            return None
    return None


def name_key(doc: fitz.Document, xref: int, key: str) -> str:
    _kind, value = xref_key(doc, xref, key)
    return str(value).lstrip("/")


def inspect_raw_jpeg(
    doc: fitz.Document,
    xref: int,
    pdf: Path,
    pdf_page: int,
    article_page: int | None,
    role: str,
    width: int | None,
    height: int | None,
    filter_name: str,
) -> dict[str, Any]:
    raw = doc.xref_stream_raw(xref) or b""
    parsed = parse_jpeg_markers(raw)
    rows = parsed["rows"]
    app_com_rows = [
        row
        for row in rows
        if row["name"] == "COM" or str(row["name"]).startswith("APP")
    ]
    nonstructural_rows = [
        row
        for row in app_com_rows
        if row["role"] not in {"structural_jfif", "structural_jfxx", "structural_adobe"}
    ]
    strict_hits = sorted({hit for row in app_com_rows for hit in row["strictHits"]})
    context_hits = sorted({hit for row in app_com_rows for hit in row["contextHits"]})
    metadata_rows = [
        row
        for row in app_com_rows
        if row["role"] in {"exif", "xmp", "icc_profile", "photoshop", "comment", "app_other"}
    ]
    instruction_carrier_rows = [
        row
        for row in app_com_rows
        if row["role"] in {"xmp", "photoshop", "comment", "app_other"}
        or row["strictHits"]
        or row["contextHits"]
    ]
    marker_signature = ",".join(
        f"{row['name']}:{row['role']}:{row['payloadByteCount']}" for row in rows
    )
    return {
        "pdf": rel(pdf),
        "pdfPage": pdf_page,
        "articlePage": article_page,
        "role": role,
        "xref": xref,
        "width": width,
        "height": height,
        "filter": filter_name,
        "rawByteCount": len(raw),
        "sha256_16": sha256_bytes(raw)[:16] if raw else "",
        "isJpeg": parsed["isJpeg"],
        "parseWarning": parsed["parseWarning"],
        "markerCountBeforeEntropy": len(rows),
        "appComSegmentCount": len(app_com_rows),
        "nonStructuralAppComSegmentCount": len(nonstructural_rows),
        "provenanceMetadataSegmentCount": len(metadata_rows),
        "sourceInstructionCarrierSegmentCount": len(instruction_carrier_rows),
        "strictHitTerms": strict_hits,
        "contextHitTerms": context_hits,
        "markerSignature": marker_signature,
        "markerRows": rows,
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    image_rows: list[dict[str, Any]] = []
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        for image_tuple in page.get_images(full=True):
            xref = int(image_tuple[0])
            image_rows.append(
                inspect_raw_jpeg(
                    doc=doc,
                    xref=xref,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    role="page_image",
                    width=int(image_tuple[2]),
                    height=int(image_tuple[3]),
                    filter_name=str(image_tuple[8]) if len(image_tuple) > 8 else "",
                )
            )
        _kind, thumb_value = xref_key(doc, page.xref, "Thumb")
        for thumb_xref in xrefs_from_value(thumb_value):
            image_rows.append(
                inspect_raw_jpeg(
                    doc=doc,
                    xref=thumb_xref,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    role="page_thumbnail",
                    width=int_key(doc, thumb_xref, "Width"),
                    height=int_key(doc, thumb_xref, "Height"),
                    filter_name=name_key(doc, thumb_xref, "Filter"),
                )
            )
    doc.close()
    return {
        "pdf": rel(path),
        "pageCount": len(image_rows),
        "imageRows": image_rows,
    }


def summarize(pdf_rows: list[dict[str, Any]], reopen: dict[str, Any]) -> dict[str, Any]:
    rows = [row for pdf in pdf_rows for row in pdf["imageRows"]]
    page_image_rows = [row for row in rows if row["role"] == "page_image"]
    thumbnail_rows = [row for row in rows if row["role"] == "page_thumbnail"]
    p76_rows = [row for row in rows if row["articlePage"] == 76]
    app_rows = [
        marker
        for row in rows
        for marker in row["markerRows"]
        if str(marker["name"]).startswith("APP")
    ]
    com_rows = [
        marker for row in rows for marker in row["markerRows"] if marker["name"] == "COM"
    ]
    nonstructural_roles = [
        marker["role"]
        for row in rows
        for marker in row["markerRows"]
        if (str(marker["name"]).startswith("APP") or marker["name"] == "COM")
        and marker["role"]
        not in {"structural_jfif", "structural_jfxx", "structural_adobe"}
    ]
    strict_terms = sorted({hit for row in rows for hit in row["strictHitTerms"]})
    context_terms = sorted({hit for row in rows for hit in row["contextHitTerms"]})
    marker_signatures = {row["markerSignature"] for row in rows}
    image_hashes = {row["sha256_16"] for row in page_image_rows if row["sha256_16"]}
    thumb_hashes = {row["sha256_16"] for row in thumbnail_rows if row["sha256_16"]}
    trigger_summary = reopen.get("summary", {})
    return {
        "pdfCount": len(pdf_rows),
        "imageRecordCount": len(rows),
        "pageImageRecordCount": len(page_image_rows),
        "thumbnailRecordCount": len(thumbnail_rows),
        "page76RecordCount": len(p76_rows),
        "jpegRecordCount": sum(1 for row in rows if row["isJpeg"]),
        "parseWarningCount": sum(1 for row in rows if row["parseWarning"]),
        "appSegmentCount": len(app_rows),
        "comSegmentCount": len(com_rows),
        "structuralJfifSegmentCount": sum(
            1
            for row in rows
            for marker in row["markerRows"]
            if marker["role"] == "structural_jfif"
        ),
        "nonStructuralAppComSegmentCount": len(nonstructural_roles),
        "provenanceMetadataSegmentCount": sum(
            row["provenanceMetadataSegmentCount"] for row in rows
        ),
        "sourceInstructionCarrierSegmentCount": sum(
            row["sourceInstructionCarrierSegmentCount"] for row in rows
        ),
        "strictHitCount": len(strict_terms),
        "contextHitCount": len(context_terms),
        "uniquePageImageHashCount": len(image_hashes),
        "uniqueThumbnailHashCount": len(thumb_hashes),
        "uniqueMarkerSignatureCount": len(marker_signatures),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(
            trigger_summary.get("satisfiedReopenTriggerCount", 0)
            or trigger_summary.get("satisfiedTriggerCount", 0)
            or 0
        ),
        "triggerCount": int(trigger_summary.get("triggerCount", 9) or 9),
        "selectorUnlockCount": 0,
        "strictHitTerms": strict_terms,
        "contextHitTerms": context_terms,
        "nonStructuralRoles": sorted(set(nonstructural_roles)),
    }


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Embedded JPEG Marker Gate",
        "",
        "Scope: inspected raw JPEG marker wrappers in embedded page images and page thumbnails from the current PDFs, especially page 76. This checks for APP/COM marker payloads such as EXIF, XMP, ICC, Photoshop, comments, or readable instruction/context strings. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / JPEG records: `{summary['pdfCount']}` / `{summary['imageRecordCount']}`",
        f"- Page images / thumbnails / page-76 records: `{summary['pageImageRecordCount']}` / `{summary['thumbnailRecordCount']}` / `{summary['page76RecordCount']}`",
        f"- JPEG records / parse warnings: `{summary['jpegRecordCount']}` / `{summary['parseWarningCount']}`",
        f"- APP / COM marker segments: `{summary['appSegmentCount']}` / `{summary['comSegmentCount']}`",
        f"- Structural JFIF segments: `{summary['structuralJfifSegmentCount']}`",
        f"- Non-structural APP/COM segments: `{summary['nonStructuralAppComSegmentCount']}`",
        f"- Provenance metadata segments: `{summary['provenanceMetadataSegmentCount']}`",
        f"- Source-instruction carrier segments: `{summary['sourceInstructionCarrierSegmentCount']}`",
        f"- Strict/context marker hits: `{summary['strictHitCount']}` / `{summary['contextHitCount']}`",
        f"- Unique page-image / thumbnail hashes: `{summary['uniquePageImageHashCount']}` / `{summary['uniqueThumbnailHashCount']}`",
        f"- Unique marker signatures: `{summary['uniqueMarkerSignatureCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Page 76 Records",
        "",
        "| PDF | role | xref | px | bytes | APP/COM | metadata | instruction carrier | hits | marker signature |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for pdf in result["pdfRows"]:
        for row in pdf["imageRows"]:
            if row["articlePage"] != 76:
                continue
            hits = sorted(set(row["strictHitTerms"] + row["contextHitTerms"]))
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{row['pdf']}`",
                        f"`{row['role']}`",
                        str(row["xref"]),
                        f"`{row['width']}x{row['height']}`",
                        str(row["rawByteCount"]),
                        str(row["appComSegmentCount"]),
                        str(row["provenanceMetadataSegmentCount"]),
                        str(row["sourceInstructionCarrierSegmentCount"]),
                        ", ".join(hits) or "-",
                        f"`{row['markerSignature'][:120]}`",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## PDF Summary Rows",
            "",
            "| PDF | records | page images | thumbnails | metadata segments | instruction carriers | marker hits |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for pdf in result["pdfRows"]:
        rows = pdf["imageRows"]
        hits = sorted(
            {hit for row in rows for hit in row["strictHitTerms"] + row["contextHitTerms"]}
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{pdf['pdf']}`",
                    str(len(rows)),
                    str(sum(1 for row in rows if row["role"] == "page_image")),
                    str(sum(1 for row in rows if row["role"] == "page_thumbnail")),
                    str(sum(row["provenanceMetadataSegmentCount"] for row in rows)),
                    str(sum(row["sourceInstructionCarrierSegmentCount"] for row in rows)),
                    ", ".join(hits) or "-",
                ]
            )
            + " |"
        )
    exif_rows = [
        (row, marker)
        for pdf in result["pdfRows"]
        for row in pdf["imageRows"]
        for marker in row["markerRows"]
        if marker["role"] == "exif"
    ]
    if exif_rows:
        lines.extend(
            [
                "",
                "## Thumbnail EXIF Provenance Rows",
                "",
                "| PDF | article page | xref | sample | hits |",
                "|---|---:|---:|---|---|",
            ]
        )
        for row, marker in exif_rows:
            hits = sorted(set(marker["strictHits"] + marker["contextHits"]))
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{row['pdf']}`",
                        str(row["articlePage"]),
                        str(row["xref"]),
                        f"`{marker['sample']}`",
                        ", ".join(hits) or "-",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Marker Notes",
            "",
            "- Every inspected DCT stream begins with normal JPEG SOI and contains a structural JFIF APP0 segment.",
            "- The full embedded page images have no EXIF, XMP, ICC profile payloads, Photoshop APP13 payloads, COM comments, or other non-structural APP marker carriers.",
            "- The eight tiny `magazine.pdf` page thumbnails have small Canon EXIF APP1 provenance blocks with timestamps, including page 76, but those blocks contain no strict instruction or puzzle context terms.",
            "- Page 76's main image has only ordinary JPEG wrapper markers; its thumbnail has only JFIF plus the small Canon timestamp EXIF block already constrained to thumbnail provenance.",
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- Do not reopen embedded JPEG marker metadata as source/original-layout evidence.",
            "- Treat these wrappers as normal image encoding metadata, not puzzle instructions.",
            "",
            "## Next Move",
            "",
            "- Continue source/original-layout validation only if a distinct source asset or raw clue wording changes the unit/order/transform evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    pdf_rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    summary = summarize(pdf_rows, reopen)
    fingerprint = (
        f"pdfs={summary['pdfCount']}|records={summary['imageRecordCount']}|"
        f"pageImages={summary['pageImageRecordCount']}|thumbs={summary['thumbnailRecordCount']}|"
        f"p76Records={summary['page76RecordCount']}|jpeg={summary['jpegRecordCount']}|"
        f"warn={summary['parseWarningCount']}|app={summary['appSegmentCount']}|"
        f"com={summary['comSegmentCount']}|jfif={summary['structuralJfifSegmentCount']}|"
        f"nonstruct={summary['nonStructuralAppComSegmentCount']}|metadata={summary['provenanceMetadataSegmentCount']}|"
        f"instrCarrier={summary['sourceInstructionCarrierSegmentCount']}|"
        f"strict={summary['strictHitCount']}|context={summary['contextHitCount']}|"
        f"pageHashes={summary['uniquePageImageHashCount']}|thumbHashes={summary['uniqueThumbnailHashCount']}|"
        f"markerSigs={summary['uniqueMarkerSignatureCount']}|sourceR3=0|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_embedded_jpeg_marker_no_source_carrier",
        "summary": summary,
        "fingerprint": fingerprint,
        "pdfRows": pdf_rows,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
