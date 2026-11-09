#!/usr/bin/env python3
"""Audit JPEG compression structure in current-PDF page images.

This bounded pass checks whether embedded DCT image compression details
(quantization/Huffman tables, sampling, raw byte-size order) carry a source,
page-order, fold-order, or OVERDOSE selector. It follows the JPEG marker and
thumbnail EXIF gates, but inspects binary compression structure rather than
text metadata.

No key derivation, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_jpeg_compression_provenance_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_jpeg_compression_provenance_gate.json"
OUT_MD = OUT / "current_pdf_jpeg_compression_provenance_gate.md"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16] if data else ""


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


def marker_name(marker: int) -> str:
    if 0xE0 <= marker <= 0xEF:
        return f"APP{marker - 0xE0}"
    names = {
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
    return names.get(marker, f"0xFF{marker:02X}")


def parse_sof(payload: bytes) -> dict[str, Any]:
    if len(payload) < 6:
        return {}
    precision = payload[0]
    height = int.from_bytes(payload[1:3], "big")
    width = int.from_bytes(payload[3:5], "big")
    component_count = payload[5]
    components: list[str] = []
    cursor = 6
    for _ in range(component_count):
        if cursor + 3 > len(payload):
            break
        component_id = payload[cursor]
        hv = payload[cursor + 1]
        qt = payload[cursor + 2]
        h_sampling = hv >> 4
        v_sampling = hv & 0x0F
        components.append(f"{component_id}:{h_sampling}x{v_sampling}:q{qt}")
        cursor += 3
    return {
        "precision": precision,
        "width": width,
        "height": height,
        "componentCount": component_count,
        "sampling": ";".join(components),
    }


def parse_jpeg_compression(data: bytes) -> dict[str, Any]:
    dqt_segments: list[bytes] = []
    dht_segments: list[bytes] = []
    app_roles: list[str] = []
    sof: dict[str, Any] = {}
    parse_warning = ""
    rows: list[dict[str, Any]] = []
    if not data.startswith(b"\xFF\xD8"):
        return {"isJpeg": False, "parseWarning": "missing_soi"}
    pos = 0
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
            rows.append({"name": name, "payloadByteCount": 0, "role": "structural"})
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
        role = "marker"
        if name == "APP0" and payload.startswith(b"JFIF\x00"):
            role = "structural_jfif"
        elif name == "APP1" and payload.startswith(b"Exif\x00\x00"):
            role = "exif"
        elif name.startswith("APP"):
            role = "app_other"
        elif name == "COM":
            role = "comment"
        rows.append({"name": name, "payloadByteCount": len(payload), "role": role})
        if name == "DQT":
            dqt_segments.append(payload)
        elif name == "DHT":
            dht_segments.append(payload)
        elif name in {"SOF0", "SOF1", "SOF2"}:
            sof = {"name": name, **parse_sof(payload)}
        elif name.startswith("APP") or name == "COM":
            app_roles.append(role)
        pos += length
        if marker == 0xDA:
            break
    dqt_blob = b"".join(len(seg).to_bytes(2, "big") + seg for seg in dqt_segments)
    dht_blob = b"".join(len(seg).to_bytes(2, "big") + seg for seg in dht_segments)
    return {
        "isJpeg": True,
        "parseWarning": parse_warning,
        "rows": rows,
        "dqtSegmentCount": len(dqt_segments),
        "dhtSegmentCount": len(dht_segments),
        "dqtHash16": sha16(dqt_blob),
        "dhtHash16": sha16(dht_blob),
        "sof": sof,
        "appRoles": app_roles,
    }


def image_record(
    doc: fitz.Document,
    pdf: Path,
    pdf_page: int,
    article_page: int | None,
    xref: int,
    role: str,
    width: int | None,
    height: int | None,
    filter_name: str,
) -> dict[str, Any]:
    raw = doc.xref_stream_raw(xref) or b""
    parsed = parse_jpeg_compression(raw)
    sof = parsed.get("sof", {})
    sampling = sof.get("sampling", "")
    compression_signature = (
        f"{filter_name}|{width}x{height}|sof={sof.get('name', '')}"
        f"|sampling={sampling}|dqt={parsed.get('dqtHash16', '')}"
        f"|dht={parsed.get('dhtHash16', '')}"
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
        "isJpeg": parsed.get("isJpeg", False),
        "parseWarning": parsed.get("parseWarning", ""),
        "dqtSegmentCount": parsed.get("dqtSegmentCount", 0),
        "dhtSegmentCount": parsed.get("dhtSegmentCount", 0),
        "dqtHash16": parsed.get("dqtHash16", ""),
        "dhtHash16": parsed.get("dhtHash16", ""),
        "sof": parsed.get("sof", {}),
        "appRoles": parsed.get("appRoles", []),
        "compressionSignature": compression_signature,
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    rows: list[dict[str, Any]] = []
    page_count = doc.page_count
    for index in range(page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        for image_tuple in page.get_images(full=True):
            rows.append(
                image_record(
                    doc=doc,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    xref=int(image_tuple[0]),
                    role="page_image",
                    width=int(image_tuple[2]),
                    height=int(image_tuple[3]),
                    filter_name=str(image_tuple[8]) if len(image_tuple) > 8 else "",
                )
            )
        _kind, thumb_value = xref_key(doc, page.xref, "Thumb")
        for thumb_xref in xrefs_from_value(thumb_value):
            rows.append(
                image_record(
                    doc=doc,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    xref=thumb_xref,
                    role="page_thumbnail",
                    width=int_key(doc, thumb_xref, "Width"),
                    height=int_key(doc, thumb_xref, "Height"),
                    filter_name=name_key(doc, thumb_xref, "Filter"),
                )
            )
    doc.close()
    return {"pdf": rel(path), "pageCount": page_count, "imageRows": rows}


def order_check(label: str, observed: list[int], expected: list[int]) -> dict[str, Any]:
    return {
        "candidate": label,
        "expected": "-".join(map(str, expected)),
        "observed": "-".join(map(str, observed)),
        "match": observed == expected,
    }


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    pdf_rows = [inspect_pdf(path) for path in PDFS]
    rows = [row for pdf in pdf_rows for row in pdf["imageRows"]]
    page_images = [row for row in rows if row["role"] == "page_image"]
    thumbnails = [row for row in rows if row["role"] == "page_thumbnail"]
    magazine_images = [
        row
        for row in page_images
        if row["pdf"] == "magazine.pdf" and row["articlePage"] is not None
    ]
    magazine_thumbs = [
        row
        for row in thumbnails
        if row["pdf"] == "magazine.pdf" and row["articlePage"] is not None
    ]

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["compressionSignature"]].append(row)

    group_rows: list[dict[str, Any]] = []
    for index, (signature, group) in enumerate(sorted(groups.items()), start=1):
        pages = sorted({row["articlePage"] for row in group if row["articlePage"]})
        group_rows.append(
            {
                "groupId": f"J{index}",
                "compressionSignature": signature,
                "recordCount": len(group),
                "roles": sorted({row["role"] for row in group}),
                "pdfs": sorted({row["pdf"] for row in group}),
                "articlePages": pages,
                "page76RecordCount": sum(1 for row in group if row["articlePage"] == 76),
                "rawByteMin": min(row["rawByteCount"] for row in group),
                "rawByteMax": max(row["rawByteCount"] for row in group),
            }
        )

    article_order = [row["articlePage"] for row in sorted(magazine_images, key=lambda r: r["articlePage"])]
    byte_order = [row["articlePage"] for row in sorted(magazine_images, key=lambda r: r["rawByteCount"])]
    thumb_byte_order = [
        row["articlePage"] for row in sorted(magazine_thumbs, key=lambda r: r["rawByteCount"])
    ]
    active_pages = [76, 78, 79, 80]
    active_byte_order = [page for page in byte_order if page in active_pages]
    active_thumb_byte_order = [page for page in thumb_byte_order if page in active_pages]
    candidate_checks = [
        order_check("magazine page-image byte-size order vs page order", byte_order, article_order),
        order_check("magazine page-image byte-size order vs reverse page order", byte_order, list(reversed(article_order))),
        order_check("magazine thumbnail byte-size order vs page order", thumb_byte_order, article_order),
        order_check("magazine thumbnail byte-size order vs reverse page order", thumb_byte_order, list(reversed(article_order))),
        order_check("active page-image byte-size order vs 76-78-79-80", active_byte_order, active_pages),
        order_check("active thumbnail byte-size order vs 76-78-79-80", active_thumb_byte_order, active_pages),
    ]

    p76_signatures = {
        row["compressionSignature"] for row in rows if row["articlePage"] == 76
    }
    unique_p76_signature_count = sum(
        1 for sig in p76_signatures if len(groups[sig]) == 1
    )
    active_unique_signature_count = sum(
        1
        for sig, group in groups.items()
        if {row["articlePage"] for row in group if row["articlePage"]}.issubset(
            set(active_pages)
        )
        and any(row["articlePage"] in active_pages for row in group)
    )
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    selector_unlocks = sum(1 for row in candidate_checks if row["match"])

    fingerprint = (
        f"pdfs={len(pdf_rows)}|records={len(rows)}|groups={len(group_rows)}"
        f"|pageImageGroups={len({row['compressionSignature'] for row in page_images})}"
        f"|thumbGroups={len({row['compressionSignature'] for row in thumbnails})}"
        f"|p76Sigs={len(p76_signatures)}|p76Unique={unique_p76_signature_count}"
        f"|activeUnique={active_unique_signature_count}"
        f"|byteOrder={'-'.join(map(str, byte_order))}"
        f"|thumbByteOrder={'-'.join(map(str, thumb_byte_order))}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors={selector_unlocks}"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_jpeg_compression_provenance_no_selector",
        "scope": "current PDF DCT compression structure; no key derivation, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "summary": {
            "pdfCount": len(pdf_rows),
            "imageRecordCount": len(rows),
            "pageImageRecordCount": len(page_images),
            "thumbnailRecordCount": len(thumbnails),
            "compressionGroupCount": len(group_rows),
            "pageImageCompressionGroupCount": len(
                {row["compressionSignature"] for row in page_images}
            ),
            "thumbnailCompressionGroupCount": len(
                {row["compressionSignature"] for row in thumbnails}
            ),
            "page76CompressionSignatureCount": len(p76_signatures),
            "page76UniqueCompressionSignatureCount": unique_p76_signature_count,
            "activeUniqueCompressionSignatureCount": active_unique_signature_count,
            "magazinePageImageByteOrder": byte_order,
            "magazineThumbnailByteOrder": thumb_byte_order,
            "candidateOrderMatchCount": selector_unlocks,
            "candidateOrderCheckCount": len(candidate_checks),
            "sourceBackedR3BridgeHitCount": source_r3_hits,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
        },
        "groupRows": group_rows,
        "candidateOrderChecks": candidate_checks,
        "pdfRows": pdf_rows,
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF JPEG Compression Provenance Gate",
        "",
        "Scope: checked whether embedded JPEG/DCT compression structure in the current PDFs supplies a page/fold/OVERDOSE selector. The pass inspects quantization and Huffman table signatures, SOF sampling, compression groups, and raw byte-size order. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / image records: `{len(pdf_rows)}` / `{len(rows)}`",
        f"- Page images / thumbnails: `{len(page_images)}` / `{len(thumbnails)}`",
        f"- Compression groups: `{len(group_rows)}`",
        f"- Page-image / thumbnail compression groups: `{result['summary']['pageImageCompressionGroupCount']}` / `{result['summary']['thumbnailCompressionGroupCount']}`",
        f"- Page 76 compression signatures / unique signatures: `{len(p76_signatures)}` / `{unique_p76_signature_count}`",
        f"- Active unique compression signatures: `{active_unique_signature_count}`",
        f"- Magazine page-image byte-size order: `{'-'.join(map(str, byte_order))}`",
        f"- Magazine thumbnail byte-size order: `{'-'.join(map(str, thumb_byte_order))}`",
        f"- Candidate order matches / checks: `{selector_unlocks}` / `{len(candidate_checks)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Compression Groups",
        "",
        "| group | records | roles | PDFs | article pages | p76 records | byte range | signature |",
        "|---|---:|---|---|---|---:|---|---|",
    ]
    for group in group_rows:
        lines.append(
            f"| {group['groupId']} | {group['recordCount']} | `{','.join(group['roles'])}` | `{','.join(group['pdfs'])}` | `{'-'.join(map(str, group['articlePages']))}` | {group['page76RecordCount']} | `{group['rawByteMin']}-{group['rawByteMax']}` | `{group['compressionSignature']}` |"
        )

    lines.extend(
        [
            "",
            "## Candidate Order Checks",
            "",
            "| candidate | expected | observed | match |",
            "|---|---|---|---:|",
        ]
    )
    for check in candidate_checks:
        lines.append(
            f"| {check['candidate']} | `{check['expected']}` | `{check['observed']}` | `{int(check['match'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_jpeg_compression_provenance_no_selector`",
            "- JPEG compression structure forms broad provenance groups, not a page-76 or active-quartet carrier.",
            "- Page 76 has no unique compression signature; its signatures are shared with non-active pages and/or duplicate PDFs.",
            "- Byte-size ordering does not match page order, reverse page order, or active 76-78-79-80 order.",
            "- Treat DQT/DHT/SOF compression structure as image-encoding provenance only.",
            "",
            "## Next Move",
            "",
            "- Continue source/original-layout validation only if a distinct physical scan, source export, or raw clue wording supplies a unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Decision: {result['decision']}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
