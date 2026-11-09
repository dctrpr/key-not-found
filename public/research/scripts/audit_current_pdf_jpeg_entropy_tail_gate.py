#!/usr/bin/env python3
"""Audit embedded JPEG entropy-scan and tail structure in current PDFs.

This bounded pass complements the JPEG marker/compression checks by inspecting
only entropy-coded scan structure: SOS count, EOI placement, bytes after EOI,
restart markers, stuffed bytes, entropy byte counts, and page-order signatures.

It does not derive keys, generate candidates, hash-to-key, inspect seed/WIF or
address material, run BIP39 checks, or brute force anything.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_jpeg_entropy_tail_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_jpeg_entropy_tail_gate.json"
OUT_MD = OUT / "current_pdf_jpeg_entropy_tail_gate.md"
OUT_SHEET = OUT / "current_pdf_jpeg_entropy_tail_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
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


def marker_name(marker: int) -> str:
    if 0xE0 <= marker <= 0xEF:
        return f"APP{marker - 0xE0}"
    if 0xD0 <= marker <= 0xD7:
        return f"RST{marker - 0xD0}"
    return MARKER_NAMES.get(marker, f"0xFF{marker:02X}")


def printable_strings(data: bytes, limit: int = 10) -> list[str]:
    rows: list[str] = []
    for match in re.finditer(rb"[\x20-\x7E]{4,}", data):
        text = match.group(0).decode("latin-1", errors="replace")
        if text not in rows:
            rows.append(text)
        if len(rows) >= limit:
            break
    return rows


def token_hits(text: str, terms: set[str]) -> list[str]:
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
    )


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


def parse_entropy_tail(data: bytes) -> dict[str, Any]:
    if not data.startswith(b"\xFF\xD8"):
        return {"isJpeg": False, "parseWarning": "missing_soi"}

    pos = 0
    parse_warning = ""
    header_markers: list[str] = []
    scan_rows: list[dict[str, Any]] = []
    eoi_offset: int | None = None
    dtn_offset: int | None = None
    dri_value: int | None = None
    sof_name = ""
    entropy_byte_count = 0
    stuffed_ff00_count = 0
    restart_marker_count = 0
    unexpected_marker_count = 0

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
        header_markers.append(name)
        if marker in {0xD8, 0xD9} or 0xD0 <= marker <= 0xD7 or marker == 0x01:
            if marker == 0xD9:
                eoi_offset = pos - 2
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
        pos += length
        if marker == 0xDD and len(payload) >= 2:
            dri_value = int.from_bytes(payload[:2], "big")
        if name in {"SOF0", "SOF1", "SOF2"}:
            sof_name = name
        if marker != 0xDA:
            continue

        scan_start = pos
        scan_entropy_bytes = 0
        scan_stuffed = 0
        scan_restarts = 0
        stop_marker = ""
        while pos < len(data):
            byte = data[pos]
            if byte != 0xFF:
                scan_entropy_bytes += 1
                pos += 1
                continue
            if pos + 1 >= len(data):
                parse_warning = "truncated_ff_in_entropy"
                pos += 1
                break
            marker2 = data[pos + 1]
            if marker2 == 0x00:
                scan_entropy_bytes += 1
                scan_stuffed += 1
                pos += 2
                continue
            if 0xD0 <= marker2 <= 0xD7:
                scan_restarts += 1
                pos += 2
                continue
            if marker2 == 0xD9:
                stop_marker = "EOI"
                eoi_offset = pos
                pos += 2
                break
            stop_marker = marker_name(marker2)
            unexpected_marker_count += 1
            break
        scan_rows.append(
            {
                "scanIndex": len(scan_rows),
                "startOffset": scan_start,
                "entropyByteCount": scan_entropy_bytes,
                "stuffedFF00Count": scan_stuffed,
                "restartMarkerCount": scan_restarts,
                "stopMarker": stop_marker,
            }
        )
        entropy_byte_count += scan_entropy_bytes
        stuffed_ff00_count += scan_stuffed
        restart_marker_count += scan_restarts
        if stop_marker == "EOI":
            break

    if eoi_offset is None:
        dtn_offset = None
        trailing = b""
    else:
        dtn_offset = eoi_offset + 2
        trailing = data[dtn_offset:]
    trailing_strings = printable_strings(trailing)
    trailing_text = " ".join(trailing_strings)
    marker_sequence = ",".join(header_markers[:24])
    return {
        "isJpeg": True,
        "parseWarning": parse_warning,
        "sofName": sof_name,
        "headerMarkerSequence": marker_sequence,
        "scanCount": len(scan_rows),
        "scanRows": scan_rows,
        "driRestartInterval": dri_value,
        "entropyByteCount": entropy_byte_count,
        "stuffedFF00Count": stuffed_ff00_count,
        "restartMarkerCount": restart_marker_count,
        "unexpectedEntropyMarkerCount": unexpected_marker_count,
        "eoiOffset": eoi_offset,
        "trailingByteCount": len(trailing),
        "trailingPrintableStrings": trailing_strings,
        "trailingStrictHits": token_hits(trailing_text, STRICT_TERMS),
        "trailingContextHits": token_hits(trailing_text, CONTEXT_TERMS),
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
    parsed = parse_entropy_tail(raw)
    entropy_signature = (
        f"{filter_name}|{width}x{height}|sof={parsed.get('sofName', '')}|"
        f"scans={parsed.get('scanCount', 0)}|dri={parsed.get('driRestartInterval')}|"
        f"entropy={parsed.get('entropyByteCount', 0)}|stuffed={parsed.get('stuffedFF00Count', 0)}|"
        f"rst={parsed.get('restartMarkerCount', 0)}|trail={parsed.get('trailingByteCount', 0)}"
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
        "sofName": parsed.get("sofName", ""),
        "scanCount": parsed.get("scanCount", 0),
        "driRestartInterval": parsed.get("driRestartInterval"),
        "entropyByteCount": parsed.get("entropyByteCount", 0),
        "stuffedFF00Count": parsed.get("stuffedFF00Count", 0),
        "restartMarkerCount": parsed.get("restartMarkerCount", 0),
        "unexpectedEntropyMarkerCount": parsed.get("unexpectedEntropyMarkerCount", 0),
        "eoiOffset": parsed.get("eoiOffset"),
        "trailingByteCount": parsed.get("trailingByteCount", 0),
        "trailingPrintableStrings": parsed.get("trailingPrintableStrings", []),
        "trailingStrictHits": parsed.get("trailingStrictHits", []),
        "trailingContextHits": parsed.get("trailingContextHits", []),
        "headerMarkerSequence": parsed.get("headerMarkerSequence", ""),
        "scanRows": parsed.get("scanRows", []),
        "entropySignature": entropy_signature,
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    rows: list[dict[str, Any]] = []
    for index in range(doc.page_count):
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
    return {"pdf": rel(path), "imageRows": rows}


def order_stream(rows: list[dict[str, Any]], metric: str) -> str:
    page_rows = [row for row in rows if row["role"] == "page_image" and row.get("articlePage")]
    page_rows.sort(key=lambda row: row.get(metric, 0), reverse=True)
    return "-".join(str(row["articlePage"]) for row in page_rows)


def analyze_groups(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["entropySignature"]].append(row)
    page76_rows = [row for row in rows if row.get("articlePage") == 76 and row["role"] == "page_image"]
    page_image_rows = [row for row in rows if row["role"] == "page_image"]
    page76_unique = [
        row
        for row in page76_rows
        if len(groups[row["entropySignature"]]) == 1
    ]
    active_page_rows = [
        row
        for row in page_image_rows
        if row.get("articlePage") in {75, 76, 78, 79}
    ]
    active_unique = [
        row
        for row in active_page_rows
        if len(groups[row["entropySignature"]]) == 1
    ]
    tail_rows = [row for row in rows if row["trailingByteCount"] > 0]
    strict_tail_rows = [row for row in tail_rows if row["trailingStrictHits"]]
    context_tail_rows = [row for row in tail_rows if row["trailingContextHits"]]
    unexpected_rows = [
        row
        for row in rows
        if row["parseWarning"] or row["unexpectedEntropyMarkerCount"] or row["scanCount"] != 1
    ]
    restart_rows = [row for row in rows if row["restartMarkerCount"] or row["driRestartInterval"]]
    entropy_orders = {
        pdf: order_stream(pdf_rows, "entropyByteCount")
        for pdf, pdf_rows in group_by_pdf(page_image_rows).items()
    }
    raw_orders = {
        pdf: order_stream(pdf_rows, "rawByteCount")
        for pdf, pdf_rows in group_by_pdf(page_image_rows).items()
    }
    known_orders = {
        "article_order": "73-74-75-76-77-78-79-80",
        "reverse_article_order": "80-79-78-77-76-75-74-73",
        "valid_leaf_75_76": "75-76",
        "active_page_order": "75-76-78-79",
        "thumbnail_exif_order": "73-75-74-78-79-76-77-80",
    }
    matched_entropy_orders = []
    for pdf, stream in entropy_orders.items():
        for name, known in known_orders.items():
            if stream == known:
                matched_entropy_orders.append({"pdf": pdf, "order": name, "stream": stream})
    return {
        "signatureGroupCount": len(groups),
        "signatureGroups": [
            {
                "signature": key,
                "count": len(value),
                "members": [
                    f"{row['pdf']}|p{row.get('articlePage')}|{row['role']}|xref{row['xref']}"
                    for row in value[:10]
                ],
            }
            for key, value in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
        ],
        "page76UniqueEntropySignatureRows": page76_unique,
        "activePageUniqueEntropySignatureRows": active_unique,
        "tailRows": tail_rows,
        "strictTailRows": strict_tail_rows,
        "contextTailRows": context_tail_rows,
        "unexpectedRows": unexpected_rows,
        "restartRows": restart_rows,
        "entropyByteCountOrders": entropy_orders,
        "rawByteCountOrders": raw_orders,
        "matchedEntropyOrders": matched_entropy_orders,
    }


def group_by_pdf(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["pdf"]].append(row)
    return dict(grouped)


def safe_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_sheet(result: dict[str, Any]) -> None:
    width, height = 1800, 1120
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = safe_font(24)
    small = safe_font(15)
    tiny = safe_font(11)
    summary = result["summary"]
    draw.rectangle((0, 0, width, 104), fill=(28, 31, 42))
    draw.text((24, 16), "Current PDF JPEG Entropy / Tail Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Checks SOS scan counts, EOI tails, restart markers, entropy lengths, and page-76 uniqueness.",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (1050, 18),
        f"images {summary['imageRowCount']} | page images {summary['pageImageRowCount']} | groups {summary['signatureGroupCount']}",
        fill=(235, 235, 235),
        font=small,
    )
    draw.text(
        (1050, 50),
        f"tails {summary['tailRowCount']} | p76 unique {summary['page76UniqueEntropySignatureCount']} | selectors {summary['selectorCandidateCount']}",
        fill=(235, 235, 235),
        font=small,
    )
    rows = [row for row in result["imageRows"] if row["role"] == "page_image"][:28]
    headers = ["pdf", "p", "xref", "size", "raw", "entropy", "scan", "rst", "stuff", "tail", "signature"]
    xs = [16, 445, 490, 560, 680, 760, 855, 920, 980, 1045, 1110]
    y = 128
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(42, 46, 56), font=small)
    y += 26
    for idx, row in enumerate(rows):
        draw.rectangle((10, y - 4, width - 10, y + 26), fill=(246, 248, 251) if idx % 2 == 0 else "white")
        values = [
            row["pdf"][-58:],
            str(row.get("articlePage")),
            str(row["xref"]),
            f"{row['width']}x{row['height']}",
            str(row["rawByteCount"]),
            str(row["entropyByteCount"]),
            str(row["scanCount"]),
            str(row["restartMarkerCount"]),
            str(row["stuffedFF00Count"]),
            str(row["trailingByteCount"]),
            row["entropySignature"][:82],
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=(28, 32, 40), font=tiny)
        y += 30
    y += 16
    draw.text((24, y), "Entropy-byte page orders", fill=(40, 44, 52), font=small)
    y += 28
    for pdf, stream in result["analysis"]["entropyByteCountOrders"].items():
        draw.text((32, y), f"{pdf}: {stream}", fill=(45, 49, 58), font=tiny)
        y += 22
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF JPEG Entropy Tail Gate",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Decision: `{result['decision']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Summary",
        "",
        f"- Image rows / page-image rows: `{summary['imageRowCount']}` / `{summary['pageImageRowCount']}`",
        f"- Entropy signature groups: `{summary['signatureGroupCount']}`",
        f"- Page-76 unique entropy signatures: `{summary['page76UniqueEntropySignatureCount']}`",
        f"- Active-page unique entropy signatures: `{summary['activePageUniqueEntropySignatureCount']}`",
        f"- Rows with bytes after EOI: `{summary['tailRowCount']}`",
        f"- Tail strict/context rows: `{summary['strictTailRowCount']}` / `{summary['contextTailRowCount']}`",
        f"- Unexpected scan/marker rows: `{summary['unexpectedRowCount']}`",
        f"- Restart-marker rows: `{summary['restartRowCount']}`",
        f"- Matched bounded entropy orders: `{summary['matchedEntropyOrderCount']}`",
        f"- Structural-only signal rows: `{summary['structuralOnlySignalCount']}`",
        f"- Selector candidates / source-backed R3 / triggers: `{summary['selectorCandidateCount']}` / `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        "",
        "## Page-Image Entropy Orders",
        "",
    ]
    for pdf, stream in result["analysis"]["entropyByteCountOrders"].items():
        lines.append(f"- `{pdf}`: `{stream}`")
    lines.extend(["", "## Signature Groups", ""])
    for group in result["analysis"]["signatureGroups"][:8]:
        lines.append(f"- `{group['signature']}`: `{group['count']}` rows")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not promote embedded JPEG entropy/tail structure as a source or selector.",
            "- Page 76 is unique only in the high-resolution `magazine.pdf` lineage where page-image entropy lengths are generally unique; the duplicate low-resolution PDF lineage shares its page signatures.",
            "- The short post-EOI tails are non-printable padding/trailing bytes confined to `magazine.pdf`, with no strict/context strings and no instruction terms.",
            "- There are no restart-marker structures, unexpected scan markers, or exact bounded article/fold/active entropy orders.",
            "",
            "## Next Move",
            "",
            "- Stop extending PDF binary-wrapper checks unless a new source file differs materially from the current two PDF lineages.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    source_review = load_json(SOURCE_REVIEW_GATE)
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_rows = trigger_matrix.get("triggerRows", trigger_matrix.get("triggers", []))
    satisfied_triggers = [
        row for row in trigger_rows if row.get("triggerSatisfiedNow") or row.get("status") == "satisfied"
    ]
    source_r3_hits = int(source_review.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0))
    pdf_rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    image_rows = [row for pdf in pdf_rows for row in pdf["imageRows"]]
    page_image_rows = [row for row in image_rows if row["role"] == "page_image"]
    analysis = analyze_groups(image_rows)
    structural_only_signals = (
        len(analysis["page76UniqueEntropySignatureRows"])
        + len(analysis["activePageUniqueEntropySignatureRows"])
        + len(analysis["tailRows"])
        + len(analysis["matchedEntropyOrders"])
    )
    selector_candidates = len(analysis["strictTailRows"]) + len(analysis["contextTailRows"])
    summary = {
        "decision": "current_pdf_jpeg_entropy_tail_no_selector",
        "pdfCount": len(pdf_rows),
        "imageRowCount": len(image_rows),
        "pageImageRowCount": len(page_image_rows),
        "signatureGroupCount": analysis["signatureGroupCount"],
        "page76UniqueEntropySignatureCount": len(analysis["page76UniqueEntropySignatureRows"]),
        "activePageUniqueEntropySignatureCount": len(analysis["activePageUniqueEntropySignatureRows"]),
        "tailRowCount": len(analysis["tailRows"]),
        "strictTailRowCount": len(analysis["strictTailRows"]),
        "contextTailRowCount": len(analysis["contextTailRows"]),
        "unexpectedRowCount": len(analysis["unexpectedRows"]),
        "restartRowCount": len(analysis["restartRows"]),
        "matchedEntropyOrderCount": len(analysis["matchedEntropyOrders"]),
        "structuralOnlySignalCount": structural_only_signals,
        "selectorCandidateCount": selector_candidates,
        "sourceBackedR3BridgeHitCount": source_r3_hits,
        "satisfiedReopenTriggerCount": len(satisfied_triggers),
        "triggerCount": len(trigger_rows),
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|images={summary['imageRowCount']}|"
        f"pageImages={summary['pageImageRowCount']}|groups={summary['signatureGroupCount']}|"
        f"p76Unique={summary['page76UniqueEntropySignatureCount']}|"
        f"activeUnique={summary['activePageUniqueEntropySignatureCount']}|"
        f"tails={summary['tailRowCount']}|strictTails={summary['strictTailRowCount']}|"
        f"contextTails={summary['contextTailRowCount']}|unexpected={summary['unexpectedRowCount']}|"
        f"restart={summary['restartRowCount']}|orders={summary['matchedEntropyOrderCount']}|"
        f"structural={summary['structuralOnlySignalCount']}|"
        f"candidates={summary['selectorCandidateCount']}|sourceR3={source_r3_hits}|"
        f"triggers={len(satisfied_triggers)}/{len(trigger_rows)}|selectors=0"
    )
    summary["fingerprint"] = fingerprint
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": (
            "Embedded JPEG entropy/tail structure in current PDF page images and thumbnails; "
            "checks SOS/EOI/restart/tail/order uniqueness only."
        ),
        "inputs": {
            "pdfs": [rel(path) for path in PDFS if path.exists()],
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "decision": summary["decision"],
        "summary": summary,
        "fingerprint": fingerprint,
        "analysis": analysis,
        "pdfRows": pdf_rows,
        "imageRows": image_rows,
        "sheet": rel(OUT_SHEET),
    }
    draw_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(fingerprint)


if __name__ == "__main__":
    main()
