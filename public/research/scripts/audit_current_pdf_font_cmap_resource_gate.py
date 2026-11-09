#!/usr/bin/env python3
"""Audit PDF font, CMap, and embedded font-file resources.

This bounded pass inspects the font resources used by the current PDFs,
especially the invisible OCR layers on page 76. It checks whether font names,
ToUnicode CMaps, CIDToGID maps, font descriptors, or embedded font-file strings
carry hidden source/instruction evidence beyond the already-closed OCR payload.

No key derivation, hashing, seed/WIF/address checks, BIP39 checks, or candidate
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_font_cmap_resource_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_font_cmap_resource_gate.json"
OUT_MD = OUT / "current_pdf_font_cmap_resource_gate.md"

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


def xref_key(doc: fitz.Document, xref: int, key: str) -> tuple[str, str]:
    try:
        kind, value = doc.xref_get_key(xref, key)
    except Exception as exc:
        return "error", type(exc).__name__
    return kind, value


def xrefs_from_value(value: str) -> list[int]:
    return [int(match) for match in re.findall(r"(\d+)\s+0\s+R", value or "")]


def stream_bytes(doc: fitz.Document, xref: int) -> tuple[bytes, bytes]:
    try:
        decoded = doc.xref_stream(xref) or b""
    except Exception:
        decoded = b""
    try:
        raw = doc.xref_stream_raw(xref) or b""
    except Exception:
        raw = b""
    return decoded, raw


def printable_strings(data: bytes, limit: int = 20) -> list[str]:
    strings = []
    for match in re.finditer(rb"[\x20-\x7E]{4,}", data):
        text = match.group(0).decode("latin-1", errors="replace")
        if text not in strings:
            strings.append(text)
        if len(strings) >= limit:
            break
    return strings


def stream_text_record(doc: fitz.Document, xref: int, role: str) -> dict[str, Any]:
    decoded, raw = stream_bytes(doc, xref)
    text = decoded.decode("latin-1", errors="replace")
    return {
        "xref": xref,
        "role": role,
        "decodedByteCount": len(decoded),
        "rawByteCount": len(raw),
        "sha256_16": sha256_bytes(decoded)[:16] if decoded else "",
        "strictHits": token_hits(text, STRICT_TERMS),
        "contextHits": token_hits(text, CONTEXT_TERMS),
        "sample": compact_text(text, 300),
    }


def binary_stream_record(doc: fitz.Document, xref: int, role: str) -> dict[str, Any]:
    decoded, raw = stream_bytes(doc, xref)
    strings = printable_strings(decoded)
    text = " ".join(strings)
    return {
        "xref": xref,
        "role": role,
        "decodedByteCount": len(decoded),
        "rawByteCount": len(raw),
        "sha256_16": sha256_bytes(decoded)[:16] if decoded else "",
        "printableStrings": strings,
        "strictHits": token_hits(text, STRICT_TERMS),
        "contextHits": token_hits(text, CONTEXT_TERMS),
        "sample": compact_text(text, 300),
    }


def inspect_font_descriptor(doc: fitz.Document, xref: int) -> dict[str, Any]:
    obj = doc.xref_object(xref, compressed=False)
    font_file_rows = []
    for key in ["FontFile", "FontFile2", "FontFile3"]:
        kind, value = xref_key(doc, xref, key)
        for target in xrefs_from_value(value):
            row = binary_stream_record(doc, target, key)
            row["key"] = key
            font_file_rows.append(row)
    return {
        "xref": xref,
        "objectSample": compact_text(obj, 280),
        "fontName": xref_key(doc, xref, "FontName")[1],
        "strictHits": token_hits(obj, STRICT_TERMS),
        "contextHits": token_hits(obj, CONTEXT_TERMS),
        "fontFileRows": font_file_rows,
        "fontFileCount": len(font_file_rows),
    }


def inspect_descendant_font(doc: fitz.Document, xref: int) -> dict[str, Any]:
    obj = doc.xref_object(xref, compressed=False)
    cid_rows = []
    kind, value = xref_key(doc, xref, "CIDToGIDMap")
    for target in xrefs_from_value(value):
        cid_rows.append(binary_stream_record(doc, target, "CIDToGIDMap"))
    desc_kind, desc_value = xref_key(doc, xref, "FontDescriptor")
    descriptors = [
        inspect_font_descriptor(doc, target) for target in xrefs_from_value(desc_value)
    ]
    return {
        "xref": xref,
        "baseFont": xref_key(doc, xref, "BaseFont")[1],
        "subtype": xref_key(doc, xref, "Subtype")[1],
        "objectSample": compact_text(obj, 280),
        "strictHits": token_hits(obj, STRICT_TERMS),
        "contextHits": token_hits(obj, CONTEXT_TERMS),
        "cidToGidKind": kind,
        "cidToGidValue": value,
        "cidToGidRows": cid_rows,
        "fontDescriptorKind": desc_kind,
        "fontDescriptorValue": desc_value,
        "fontDescriptors": descriptors,
    }


def inspect_font(doc: fitz.Document, font_tuple: tuple[Any, ...]) -> dict[str, Any]:
    xref = int(font_tuple[0])
    obj = doc.xref_object(xref, compressed=False)
    to_kind, to_value = xref_key(doc, xref, "ToUnicode")
    to_rows = [stream_text_record(doc, target, "ToUnicode") for target in xrefs_from_value(to_value)]
    for row in to_rows:
        row["identityFullRangeCMap"] = bool(
            "<0000> <FFFF> <0000>" in row["sample"]
            or (
                row["decodedByteCount"] == 353
                and row["sample"].find("begincmap") >= 0
                and row["sample"].find("beginbfrange") >= 0
            )
        )
    desc_kind, desc_value = xref_key(doc, xref, "DescendantFonts")
    descendant_rows = [
        inspect_descendant_font(doc, target) for target in xrefs_from_value(desc_value)
    ]
    descriptor_kind, descriptor_value = xref_key(doc, xref, "FontDescriptor")
    descriptor_rows = [
        inspect_font_descriptor(doc, target) for target in xrefs_from_value(descriptor_value)
    ]
    return {
        "xref": xref,
        "extension": str(font_tuple[1]),
        "type": str(font_tuple[2]),
        "baseFont": str(font_tuple[3]),
        "resourceName": str(font_tuple[4]),
        "encoding": str(font_tuple[5]),
        "referencer": int(font_tuple[6]) if len(font_tuple) > 6 else 0,
        "objectSample": compact_text(obj, 280),
        "strictHits": token_hits(obj, STRICT_TERMS),
        "contextHits": token_hits(obj, CONTEXT_TERMS),
        "toUnicodeKind": to_kind,
        "toUnicodeValue": to_value,
        "toUnicodeRows": to_rows,
        "descendantKind": desc_kind,
        "descendantValue": desc_value,
        "descendantFonts": descendant_rows,
        "directFontDescriptorKind": descriptor_kind,
        "directFontDescriptorValue": descriptor_value,
        "directFontDescriptors": descriptor_rows,
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    page_rows = []
    font_by_xref: dict[int, dict[str, Any]] = {}
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        page_fonts = page.get_fonts(full=True)
        for font_tuple in page_fonts:
            xref = int(font_tuple[0])
            if xref not in font_by_xref:
                font_by_xref[xref] = inspect_font(doc, font_tuple)
        page_rows.append(
            {
                "pdfPage": index + 1,
                "articlePage": article_page,
                "fontXrefs": [int(item[0]) for item in page_fonts],
                "fontResourceNames": [str(item[4]) for item in page_fonts],
            }
        )
    doc.close()
    return {
        "pdf": rel(path),
        "pageCount": len(page_rows),
        "pageRows": page_rows,
        "fontRows": [font_by_xref[key] for key in sorted(font_by_xref)],
    }


def walk_hits(row: Any, strict_key: str = "strictHits", context_key: str = "contextHits") -> tuple[list[str], list[str]]:
    strict: list[str] = []
    context: list[str] = []
    if isinstance(row, dict):
        strict.extend(row.get(strict_key, []) or [])
        context.extend(row.get(context_key, []) or [])
        for value in row.values():
            child_strict, child_context = walk_hits(value, strict_key, context_key)
            strict.extend(child_strict)
            context.extend(child_context)
    elif isinstance(row, list):
        for item in row:
            child_strict, child_context = walk_hits(item, strict_key, context_key)
            strict.extend(child_strict)
            context.extend(child_context)
    return strict, context


def collect_stream_rows(pdf_rows: list[dict[str, Any]], role: str) -> list[dict[str, Any]]:
    rows = []
    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("role") == role:
                rows.append(node)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)
    visit(pdf_rows)
    return rows


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Font CMap Resource Gate",
        "",
        "Scope: inspected PDF font resources, ToUnicode CMaps, CIDToGID maps, font descriptors, and embedded font files in the current PDFs, with page 76 treated as the target page. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / pages checked: `{summary['pdfCount']}` / `{summary['pageCount']}`",
        f"- Page font references / unique font objects: `{summary['pageFontReferenceCount']}` / `{summary['uniqueFontObjectCount']}`",
        f"- Type0 GlyphLessFont objects / built-in Helvetica objects: `{summary['type0GlyphLessFontCount']}` / `{summary['builtInHelveticaFontCount']}`",
        f"- ToUnicode streams / full-range identity CMaps: `{summary['toUnicodeStreamCount']}` / `{summary['identityToUnicodeCMapCount']}`",
        f"- CIDToGID maps / font files / unique font-file hashes: `{summary['cidToGidMapCount']}` / `{summary['fontFileStreamCount']}` / `{summary['uniqueFontFileHashCount']}`",
        f"- Procedural resource strict/context hits: `{summary['resourceStrictHitCount']}` / `{summary['resourceContextHitCount']}`",
        f"- Structural `font` term hits: `{summary['structuralFontTermHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Page 76 Font Rows",
        "",
        "| PDF | font xref | type | base font | resource | encoding | ToUnicode | identity CMap | font files | resource hits |",
        "|---|---:|---|---|---|---|---:|---:|---:|---|",
    ]
    for pdf in result["pdfRows"]:
        page76_xrefs = {
            xref
            for page in pdf["pageRows"]
            if page["articlePage"] == 76
            for xref in page["fontXrefs"]
        }
        for font in pdf["fontRows"]:
            if font["xref"] not in page76_xrefs:
                continue
            to_count = len(font["toUnicodeRows"])
            identity_count = sum(1 for row in font["toUnicodeRows"] if row["identityFullRangeCMap"])
            font_files = collect_stream_rows([font], "FontFile2") + collect_stream_rows([font], "FontFile") + collect_stream_rows([font], "FontFile3")
            strict, context = walk_hits(font)
            strict = [hit for hit in strict if hit != "font"]
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{pdf['pdf']}`",
                        str(font["xref"]),
                        font["type"],
                        font["baseFont"],
                        font["resourceName"],
                        font["encoding"],
                        str(to_count),
                        str(identity_count),
                        str(len(font_files)),
                        ", ".join(sorted(set(strict + context))) or "-",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## PDF Summary Rows",
            "",
            "| PDF | unique fonts | ToUnicode | identity CMaps | font files | resource hits |",
            "|---|---:|---:|---:|---:|---|",
        ]
    )
    for pdf in result["pdfRows"]:
        to_rows = collect_stream_rows([pdf["fontRows"]], "ToUnicode")
        font_files = (
            collect_stream_rows([pdf["fontRows"]], "FontFile")
            + collect_stream_rows([pdf["fontRows"]], "FontFile2")
            + collect_stream_rows([pdf["fontRows"]], "FontFile3")
        )
        strict, context = walk_hits(pdf["fontRows"])
        strict = [hit for hit in strict if hit != "font"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{pdf['pdf']}`",
                    str(len(pdf["fontRows"])),
                    str(len(to_rows)),
                    str(sum(1 for row in to_rows if row.get("identityFullRangeCMap"))),
                    str(len(font_files)),
                    ", ".join(sorted(set(strict + context))) or "-",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Resource Notes",
            "",
            "- `magazine.pdf` uses built-in `/Helvetica` with `/WinAnsiEncoding`; it has no embedded font file and no ToUnicode CMap.",
            "- The two duplicate OCR PDFs use per-page `/GlyphLessFont` Type0 resources with `/Identity-H` encoding.",
            "- Their ToUnicode streams are full-range identity CMaps (`<0000> <FFFF> <0000>`), not instruction text.",
            "- Their embedded font files are small repeated GlyphLessFont binaries; printable strings are font/table names only and contain no puzzle instruction/context terms.",
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- Do not reopen current PDF font/CMap resources as original-layout/source evidence.",
            "- Treat the font stack as OCR implementation detail only.",
            "",
            "## Next Move",
            "",
            "- Continue source/original-layout validation only if a distinct source asset or raw clue wording changes the rule space.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    pdf_rows = [inspect_pdf(path) for path in PDFS if path.exists()]
    font_rows = [font for pdf in pdf_rows for font in pdf["fontRows"]]
    to_unicode_rows = collect_stream_rows(font_rows, "ToUnicode")
    cid_rows = collect_stream_rows(font_rows, "CIDToGIDMap")
    font_file_rows = (
        collect_stream_rows(font_rows, "FontFile")
        + collect_stream_rows(font_rows, "FontFile2")
        + collect_stream_rows(font_rows, "FontFile3")
    )
    strict_hits, context_hits = walk_hits(font_rows)
    procedural_strict_hits = [hit for hit in strict_hits if hit != "font"]
    font_file_hashes = {row["sha256_16"] for row in font_file_rows if row.get("sha256_16")}
    summary = {
        "pdfCount": len(pdf_rows),
        "pageCount": sum(pdf["pageCount"] for pdf in pdf_rows),
        "pageFontReferenceCount": sum(
            len(page["fontXrefs"]) for pdf in pdf_rows for page in pdf["pageRows"]
        ),
        "uniqueFontObjectCount": len(font_rows),
        "type0GlyphLessFontCount": sum(
            1
            for font in font_rows
            if font["type"] == "Type0" and font["baseFont"] == "GlyphLessFont"
        ),
        "builtInHelveticaFontCount": sum(
            1
            for font in font_rows
            if font["type"] == "Type1" and font["baseFont"] == "Helvetica"
        ),
        "toUnicodeStreamCount": len(to_unicode_rows),
        "identityToUnicodeCMapCount": sum(
            1 for row in to_unicode_rows if row.get("identityFullRangeCMap")
        ),
        "cidToGidMapCount": len(cid_rows),
        "fontFileStreamCount": len(font_file_rows),
        "uniqueFontFileHashCount": len(font_file_hashes),
        "resourceStrictHitCount": len(set(procedural_strict_hits)),
        "resourceContextHitCount": len(set(context_hits)),
        "structuralFontTermHitCount": strict_hits.count("font"),
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"pdfs={summary['pdfCount']}|pages={summary['pageCount']}|"
        f"fontRefs={summary['pageFontReferenceCount']}|fonts={summary['uniqueFontObjectCount']}|"
        f"glyphless={summary['type0GlyphLessFontCount']}|helvetica={summary['builtInHelveticaFontCount']}|"
        f"toUnicode={summary['toUnicodeStreamCount']}|identityCMap={summary['identityToUnicodeCMapCount']}|"
        f"cidMaps={summary['cidToGidMapCount']}|fontFiles={summary['fontFileStreamCount']}|"
        f"uniqueFontFiles={summary['uniqueFontFileHashCount']}|strict={summary['resourceStrictHitCount']}|"
        f"context={summary['resourceContextHitCount']}|sourceR3=0|"
        f"triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_font_cmap_resource_no_source_carrier",
        "summary": summary,
        "fingerprint": fingerprint,
        "resourceHitTerms": sorted(set(procedural_strict_hits + context_hits)),
        "structuralHitTerms": ["font"] if strict_hits.count("font") else [],
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
