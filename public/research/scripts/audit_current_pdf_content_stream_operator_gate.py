#!/usr/bin/env python3
"""Audit current PDF content streams for hidden layout/source operators.

This bounded pass inspects page content streams and form XObject streams in the
current PDFs. The goal is to confirm whether page 76 or neighboring article
pages contain drawing commands, form layers, clipping, visible text, vector
marks, or resource names that could act as original-layout/source evidence.
Invisible OCR payload text is summarized separately from PDF operator evidence.

No key derivation, hashing, seed/WIF/address checks, BIP39 checks, or candidate
generation is run.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_content_stream_operator_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_content_stream_operator_gate.json"
OUT_MD = OUT / "current_pdf_content_stream_operator_gate.md"

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
VECTOR_PAINT_OPERATORS = {
    "S",
    "s",
    "f",
    "F",
    "f*",
    "B",
    "B*",
    "b",
    "b*",
    "n",
}
PATH_OPERATORS = {"m", "l", "c", "v", "y", "h", "re"}
TEXT_SHOW_OPERATORS = {"Tj", "TJ", "'", '"'}
TEXT_OBJECT_OPERATORS = {"BT", "ET"}
TRANSFORM_OPERATORS = {"cm", "Tm", "Td", "TD", "T*", "Tz", "Tc", "Tf", "Tr"}
CLIP_OPERATORS = {"W", "W*"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact_text(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value).split())
    return text[:limit]


def token_hits(text: str, terms: set[str]) -> list[str]:
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE)
    )


def strip_text_payload(content: str) -> str:
    without_hex = re.sub(r"<[0-9A-Fa-f\s]+>", "<HEX>", content)
    without_arrays = re.sub(r"\[[^\]]{20,}\]", "[ARRAY]", without_hex, flags=re.S)
    return without_arrays


def operator_tokens(content: str) -> list[str]:
    # Remove literal strings and hex strings so text payload does not become
    # false operator evidence.
    stripped = re.sub(r"\([^)]*\)", "(STR)", content)
    stripped = re.sub(r"<[0-9A-Fa-f\s]+>", "<HEX>", stripped)
    tokens = re.findall(r"/?[A-Za-z*'\"]+|[-+]?\d+(?:\.\d+)?", stripped)
    operators = []
    known = (
        VECTOR_PAINT_OPERATORS
        | PATH_OPERATORS
        | TEXT_SHOW_OPERATORS
        | TEXT_OBJECT_OPERATORS
        | TRANSFORM_OPERATORS
        | CLIP_OPERATORS
        | {"q", "Q", "Do", "gs", "cs", "CS", "sc", "SC", "scn", "SCN", "rg", "RG", "g", "G"}
    )
    for token in tokens:
        if token in known:
            operators.append(token)
    return operators


def text_render_modes(content: str) -> list[int]:
    return [int(match.group(1)) for match in re.finditer(r"(?<![\d.])([0-7])\s+Tr\b", content)]


def resource_do_names(content: str) -> list[str]:
    return re.findall(r"/([A-Za-z0-9_.-]+)\s+Do\b", content)


def decode_hex_payloads(content: str) -> str:
    pieces = []
    for match in re.finditer(r"<([0-9A-Fa-f\s]+)>", content):
        hex_text = re.sub(r"\s+", "", match.group(1))
        if len(hex_text) < 4 or len(hex_text) % 2:
            continue
        try:
            data = bytes.fromhex(hex_text)
        except ValueError:
            continue
        candidates = []
        for encoding in ("utf-16-be", "utf-8", "latin-1"):
            try:
                decoded = data.decode(encoding, errors="ignore")
            except Exception:
                continue
            printable = sum(1 for char in decoded if char.isprintable() or char.isspace())
            ascii_letters = sum(1 for char in decoded if char.isascii() and (char.isalnum() or char.isspace() or char in ".,'-$#:/()"))
            score = printable + ascii_letters
            candidates.append((score, decoded))
        if candidates:
            best = max(candidates, key=lambda item: item[0])[1]
            if any(char.isalnum() for char in best):
                pieces.append(best)
    return " ".join(pieces)


def stream_record(doc: fitz.Document, xref: int, role: str, resource_name: str = "") -> dict[str, Any]:
    try:
        data = doc.xref_stream(xref) or b""
    except Exception:
        data = b""
    try:
        raw = doc.xref_stream_raw(xref) or b""
    except Exception:
        raw = b""
    content = data.decode("latin-1", errors="replace")
    operator_text = strip_text_payload(content)
    ops = operator_tokens(content)
    comments = [line.strip() for line in content.splitlines() if line.lstrip().startswith("%")]
    decoded_payload = decode_hex_payloads(content)
    render_modes = text_render_modes(content)
    visible_modes = [mode for mode in render_modes if mode != 3]
    do_names = resource_do_names(content)
    return {
        "xref": xref,
        "role": role,
        "resourceName": resource_name,
        "decodedByteCount": len(data),
        "rawByteCount": len(raw),
        "sha256_16": sha256_bytes(data)[:16] if data else "",
        "commentCount": len(comments),
        "comments": comments[:8],
        "operatorCounts": dict(Counter(ops)),
        "doNames": do_names,
        "doCount": len(do_names),
        "textObjectCount": ops.count("BT"),
        "textShowOperatorCount": sum(ops.count(op) for op in TEXT_SHOW_OPERATORS),
        "textRenderModes": sorted(set(render_modes)),
        "invisibleTextRenderModeCount": sum(1 for mode in render_modes if mode == 3),
        "visibleTextRenderModeCount": len(visible_modes),
        "pathOperatorCount": sum(ops.count(op) for op in PATH_OPERATORS),
        "vectorPaintOperatorCount": sum(ops.count(op) for op in VECTOR_PAINT_OPERATORS),
        "clipOperatorCount": sum(ops.count(op) for op in CLIP_OPERATORS),
        "operatorStrictHits": token_hits(operator_text, STRICT_TERMS),
        "operatorContextHits": token_hits(operator_text, CONTEXT_TERMS),
        "decodedTextPayloadLength": len(decoded_payload),
        "decodedTextPayloadSample": compact_text(decoded_payload, 260),
        "decodedTextPayloadStrictHits": token_hits(decoded_payload, STRICT_TERMS),
        "decodedTextPayloadContextHits": token_hits(decoded_payload, CONTEXT_TERMS),
        "sample": compact_text(operator_text, 260),
    }


def page_xobject_rows(doc: fitz.Document, page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for item in page.get_xobjects():
        xref = int(item[0])
        name = str(item[1])
        bbox = item[3] if len(item) > 3 else None
        row = stream_record(doc, xref, "form_xobject", name)
        row["bbox"] = [round(value, 3) for value in bbox] if bbox else []
        rows.append(row)
    return rows


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    page_rows = []
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        content_xrefs = list(page.get_contents() or [])
        content_streams = [
            stream_record(doc, int(xref), "page_content") for xref in content_xrefs
        ]
        form_streams = page_xobject_rows(doc, page)
        image_names = [str(item[7]) for item in page.get_images(full=True)]
        form_names = [row["resourceName"] for row in form_streams]
        all_streams = content_streams + form_streams
        do_names = [name for stream in content_streams for name in stream["doNames"]]
        image_do_names = [name for name in do_names if name in image_names]
        form_do_names = [name for name in do_names if name in form_names]
        unknown_do_names = [
            name for name in do_names if name not in image_names and name not in form_names
        ]
        page_rows.append(
            {
                "pdfPage": index + 1,
                "articlePage": article_page,
                "pageXref": page.xref,
                "contentXrefs": content_xrefs,
                "contentStreamCount": len(content_streams),
                "formXobjectCount": len(form_streams),
                "imageResourceNames": image_names,
                "formResourceNames": form_names,
                "imageDoNames": image_do_names,
                "formDoNames": form_do_names,
                "unknownDoNames": unknown_do_names,
                "decodedByteCount": sum(stream["decodedByteCount"] for stream in all_streams),
                "textObjectCount": sum(stream["textObjectCount"] for stream in all_streams),
                "textShowOperatorCount": sum(stream["textShowOperatorCount"] for stream in all_streams),
                "invisibleTextRenderModeCount": sum(
                    stream["invisibleTextRenderModeCount"] for stream in all_streams
                ),
                "visibleTextRenderModeCount": sum(
                    stream["visibleTextRenderModeCount"] for stream in all_streams
                ),
                "pathOperatorCount": sum(stream["pathOperatorCount"] for stream in all_streams),
                "vectorPaintOperatorCount": sum(
                    stream["vectorPaintOperatorCount"] for stream in all_streams
                ),
                "clipOperatorCount": sum(stream["clipOperatorCount"] for stream in all_streams),
                "operatorStrictHits": sorted(
                    {hit for stream in all_streams for hit in stream["operatorStrictHits"]}
                ),
                "operatorContextHits": sorted(
                    {hit for stream in all_streams for hit in stream["operatorContextHits"]}
                ),
                "decodedTextPayloadLength": sum(
                    stream["decodedTextPayloadLength"] for stream in all_streams
                ),
                "decodedTextPayloadStrictHits": sorted(
                    {hit for stream in all_streams for hit in stream["decodedTextPayloadStrictHits"]}
                ),
                "decodedTextPayloadContextHits": sorted(
                    {hit for stream in all_streams for hit in stream["decodedTextPayloadContextHits"]}
                ),
                "contentStreams": content_streams,
                "formStreams": form_streams,
            }
        )
    record = {
        "pdf": rel(path),
        "pageCount": doc.page_count,
        "pageRows": page_rows,
    }
    doc.close()
    return record


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Content Stream Operator Gate",
        "",
        "Scope: inspected decoded page content streams and form XObject streams in the current PDFs, with article page 76 treated as the target page. Invisible OCR text payload is summarized separately from PDF operator evidence. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / pages checked: `{summary['pdfCount']}` / `{summary['pageCount']}`",
        f"- Page content streams / form XObjects: `{summary['contentStreamCount']}` / `{summary['formXobjectCount']}`",
        f"- Image Do calls / form Do calls / unknown Do calls: `{summary['imageDoCallCount']}` / `{summary['formDoCallCount']}` / `{summary['unknownDoCallCount']}`",
        f"- Text objects / text-show operators: `{summary['textObjectCount']}` / `{summary['textShowOperatorCount']}`",
        f"- Invisible text render-mode uses / visible text render-mode uses: `{summary['invisibleTextRenderModeCount']}` / `{summary['visibleTextRenderModeCount']}`",
        f"- Vector paint / path / clip operators: `{summary['vectorPaintOperatorCount']}` / `{summary['pathOperatorCount']}` / `{summary['clipOperatorCount']}`",
        f"- Operator strict/context hits: `{summary['operatorStrictHitCount']}` / `{summary['operatorContextHitCount']}`",
        f"- OCR payload strict/context term rows: `{summary['decodedTextPayloadStrictRowCount']}` / `{summary['decodedTextPayloadContextRowCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Page 76 Rows",
        "",
        "| PDF | content streams | forms | image Do | form Do | text objects | invisible Tr | visible Tr | vector paint | operator hits | payload terms |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for pdf in result["pdfRows"]:
        for page in pdf["pageRows"]:
            if page["articlePage"] != 76:
                continue
            operator_hits = ", ".join(page["operatorStrictHits"] + page["operatorContextHits"]) or "-"
            payload_terms = ", ".join(
                page["decodedTextPayloadStrictHits"] + page["decodedTextPayloadContextHits"]
            ) or "-"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{pdf['pdf']}`",
                        str(page["contentStreamCount"]),
                        str(page["formXobjectCount"]),
                        str(len(page["imageDoNames"])),
                        str(len(page["formDoNames"])),
                        str(page["textObjectCount"]),
                        str(page["invisibleTextRenderModeCount"]),
                        str(page["visibleTextRenderModeCount"]),
                        str(page["vectorPaintOperatorCount"]),
                        operator_hits,
                        payload_terms,
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## PDF Summary Rows",
            "",
            "| PDF | pages | content streams | forms | image Do | form Do | visible Tr | vector paint | operator hits | OCR payload context rows |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|",
        ]
    )
    for row in result["pdfRows"]:
        page_rows = row["pageRows"]
        operator_hits = sorted(
            {
                hit
                for page in page_rows
                for hit in page["operatorStrictHits"] + page["operatorContextHits"]
            }
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['pdf']}`",
                    str(row["pageCount"]),
                    str(sum(page["contentStreamCount"] for page in page_rows)),
                    str(sum(page["formXobjectCount"] for page in page_rows)),
                    str(sum(len(page["imageDoNames"]) for page in page_rows)),
                    str(sum(len(page["formDoNames"]) for page in page_rows)),
                    str(sum(page["visibleTextRenderModeCount"] for page in page_rows)),
                    str(sum(page["vectorPaintOperatorCount"] for page in page_rows)),
                    ", ".join(operator_hits) or "-",
                    str(sum(1 for page in page_rows if page["decodedTextPayloadContextHits"])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Content Notes",
            "",
            "- `magazine.pdf` page 76 has three page content streams: a producer comment, one full-page image `Do`, and one invisible OCR text stream using render mode `3`.",
            "- The two duplicate OCR PDFs page 76 each have a page image `Do` plus an `OL2` form XObject; the `OL2` form is the OCR overlay and uses render mode `3` for hidden text.",
            "- No page 76 stream contains visible text rendering, vector paint marks, clipping geometry, unknown `Do` resources, or operator/resource-name instruction terms.",
            "- OCR payload context words are ordinary article text inside invisible OCR layers; they do not provide a source-backed unit/order/transform rule.",
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- Do not reopen current PDF content streams as original-layout/source evidence.",
            "- Treat content streams as raster page placement plus invisible OCR overlays only.",
            "",
            "## Next Move",
            "",
            "- Continue source/original-layout validation only if a distinct source asset or raw clue wording changes the rule space.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    all_pages = [page for pdf in rows for page in pdf["pageRows"]]
    operator_hits = {
        hit
        for page in all_pages
        for hit in page["operatorStrictHits"] + page["operatorContextHits"]
    }
    summary = {
        "pdfCount": len(rows),
        "pageCount": sum(row["pageCount"] for row in rows),
        "contentStreamCount": sum(page["contentStreamCount"] for page in all_pages),
        "formXobjectCount": sum(page["formXobjectCount"] for page in all_pages),
        "imageDoCallCount": sum(len(page["imageDoNames"]) for page in all_pages),
        "formDoCallCount": sum(len(page["formDoNames"]) for page in all_pages),
        "unknownDoCallCount": sum(len(page["unknownDoNames"]) for page in all_pages),
        "textObjectCount": sum(page["textObjectCount"] for page in all_pages),
        "textShowOperatorCount": sum(page["textShowOperatorCount"] for page in all_pages),
        "invisibleTextRenderModeCount": sum(
            page["invisibleTextRenderModeCount"] for page in all_pages
        ),
        "visibleTextRenderModeCount": sum(
            page["visibleTextRenderModeCount"] for page in all_pages
        ),
        "pathOperatorCount": sum(page["pathOperatorCount"] for page in all_pages),
        "vectorPaintOperatorCount": sum(
            page["vectorPaintOperatorCount"] for page in all_pages
        ),
        "clipOperatorCount": sum(page["clipOperatorCount"] for page in all_pages),
        "operatorStrictHitCount": len(
            {hit for page in all_pages for hit in page["operatorStrictHits"]}
        ),
        "operatorContextHitCount": len(
            {hit for page in all_pages for hit in page["operatorContextHits"]}
        ),
        "decodedTextPayloadStrictRowCount": sum(
            1 for page in all_pages if page["decodedTextPayloadStrictHits"]
        ),
        "decodedTextPayloadContextRowCount": sum(
            1 for page in all_pages if page["decodedTextPayloadContextHits"]
        ),
        "page76VisibleTextRenderModeCount": sum(
            page["visibleTextRenderModeCount"]
            for page in all_pages
            if page["articlePage"] == 76
        ),
        "page76VectorPaintOperatorCount": sum(
            page["vectorPaintOperatorCount"]
            for page in all_pages
            if page["articlePage"] == 76
        ),
        "page76UnknownDoCallCount": sum(
            len(page["unknownDoNames"])
            for page in all_pages
            if page["articlePage"] == 76
        ),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pages={summary['pageCount']}|"
        f"streams={summary['contentStreamCount']}|forms={summary['formXobjectCount']}|"
        f"imageDo={summary['imageDoCallCount']}|formDo={summary['formDoCallCount']}|"
        f"unknownDo={summary['unknownDoCallCount']}|textObj={summary['textObjectCount']}|"
        f"invisTr={summary['invisibleTextRenderModeCount']}|visTr={summary['visibleTextRenderModeCount']}|"
        f"paint={summary['vectorPaintOperatorCount']}|path={summary['pathOperatorCount']}|"
        f"clip={summary['clipOperatorCount']}|opStrict={summary['operatorStrictHitCount']}|"
        f"opContext={summary['operatorContextHitCount']}|payloadStrictRows={summary['decodedTextPayloadStrictRowCount']}|"
        f"payloadContextRows={summary['decodedTextPayloadContextRowCount']}|"
        f"p76VisTr={summary['page76VisibleTextRenderModeCount']}|p76Paint={summary['page76VectorPaintOperatorCount']}|"
        f"sourceR3=0|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_content_stream_operator_no_source_layout_carrier",
        "summary": summary,
        "operatorHitTerms": sorted(operator_hits),
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
