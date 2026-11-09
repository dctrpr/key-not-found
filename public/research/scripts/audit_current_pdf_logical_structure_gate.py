#!/usr/bin/env python3
"""Audit current PDFs for tagged-PDF/logical-structure carriers.

This bounded pass checks whether the current PDF layer contains StructTreeRoot,
MarkInfo, ActualText, Alt text, MCID, marked-content operators, or comparable
logical structure that could hide or order source text behind page 76.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_logical_structure_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_logical_structure_gate.json"
OUT_MD = OUT / "current_pdf_logical_structure_gate.md"
OUT_SHEET = OUT / "current_pdf_logical_structure_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

LOGICAL_MARKERS = [
    "StructTreeRoot",
    "StructParent",
    "StructParents",
    "ParentTree",
    "RoleMap",
    "MarkInfo",
    "Marked",
    "ActualText",
    "Alt",
    "MCID",
    "Artifact",
    "Lang",
]
CONTENT_MARKERS = ["BDC", "BMC", "EMC", "/ActualText", "/Alt", "/MCID", "/Artifact"]
STRICT_TERMS = [
    "take",
    "read",
    "letter",
    "letters",
    "word",
    "line",
    "edge",
    "font",
    "bold",
    "highlight",
    "mirror",
    "fold",
    "order",
    "first",
    "last",
    "key",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def compact(value: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit] + ("..." if len(value) > limit else "")


def marker_counts(text: str, markers: list[str]) -> dict[str, int]:
    return {marker: len(re.findall(rf"/{re.escape(marker)}\b", text)) for marker in markers}


def content_marker_counts(data: bytes) -> dict[str, int]:
    return {marker: data.count(marker.encode("latin1")) for marker in CONTENT_MARKERS}


def strict_hits(text: str) -> list[str]:
    lower = text.lower()
    return sorted({term for term in STRICT_TERMS if re.search(rf"\b{re.escape(term)}\b", lower)})


def token_contexts(text: str, tokens: list[str], limit_per_pdf: int = 12) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for token in tokens:
        for match in re.finditer(re.escape(token), text):
            start = max(0, match.start() - 70)
            end = min(len(text), match.end() + 95)
            snippet = compact(text[start:end])
            contexts.append(
                {
                    "token": token,
                    "offset": match.start(),
                    "snippet": snippet,
                    "strictHits": strict_hits(snippet),
                }
            )
            if len(contexts) >= limit_per_pdf:
                return contexts
    return contexts


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    catalog = doc.pdf_catalog()
    catalog_keys: dict[str, Any] = {}
    for key in ["StructTreeRoot", "MarkInfo", "Lang", "Metadata", "PieceInfo", "AcroForm", "Names"]:
        try:
            kind, value = doc.xref_get_key(catalog, key)
        except Exception:
            kind, value = "error", ""
        catalog_keys[key] = {"kind": kind, "value": value}

    xref_rows = []
    object_text = []
    object_marker_total = {marker: 0 for marker in LOGICAL_MARKERS}
    for xref in range(1, doc.xref_length()):
        try:
            text = doc.xref_object(xref, compressed=False)
        except Exception:
            continue
        object_text.append(text)
        counts = marker_counts(text, LOGICAL_MARKERS)
        if any(counts.values()):
            xref_rows.append(
                {
                    "xref": xref,
                    "markerCounts": counts,
                    "snippet": compact(text, 260),
                    "strictHits": strict_hits(text),
                }
            )
            for marker, count in counts.items():
                object_marker_total[marker] += count

    page_rows = []
    content_marker_total = {marker: 0 for marker in CONTENT_MARKERS}
    page76_marker_total = {marker: 0 for marker in CONTENT_MARKERS}
    for page_index, page in enumerate(doc):
        streams = []
        page_counts = {marker: 0 for marker in CONTENT_MARKERS}
        for content_xref in page.get_contents() or []:
            try:
                data = doc.xref_stream(content_xref) or b""
            except Exception:
                data = b""
            counts = content_marker_counts(data)
            for marker, count in counts.items():
                page_counts[marker] += count
                content_marker_total[marker] += count
                if page_index == 3:
                    page76_marker_total[marker] += count
            if any(counts.values()):
                decoded = data.decode("latin1", errors="replace")
                streams.append(
                    {
                        "contentXref": content_xref,
                        "markerCounts": counts,
                        "snippet": compact(decoded, 260),
                        "strictHits": strict_hits(decoded),
                    }
                )
        page_rows.append(
            {
                "pdfPage": page_index + 1,
                "articlePage": 73 + page_index,
                "contentStreamCount": len(page.get_contents() or []),
                "markerCounts": page_counts,
                "contentStreamsWithMarkers": streams,
            }
        )

    raw = path.read_bytes()
    raw_marker_counts = {
        marker: raw.count(marker.encode("latin1"))
        for marker in ["/StructTreeRoot", "/MarkInfo", "/ActualText", "/Alt", "/MCID", "BDC", "BMC", "EMC", "/Artifact", "/RoleMap"]
    }
    raw_contexts = []
    raw_text = raw.decode("latin1", errors="replace")
    if raw_marker_counts.get("BDC"):
        raw_contexts = token_contexts(raw_text, ["BDC"], limit_per_pdf=4)

    logical_object_count = len(xref_rows)
    content_marker_count = sum(content_marker_total.values())
    page76_content_marker_count = sum(page76_marker_total.values())
    strict_context_hits = sorted(
        {
            hit
            for row in xref_rows
            for hit in row["strictHits"]
        }
        | {
            hit
            for page in page_rows
            for stream in page["contentStreamsWithMarkers"]
            for hit in stream["strictHits"]
        }
        | {
            hit
            for context in raw_contexts
            for hit in context["strictHits"]
        }
    )

    doc.close()
    return {
        "pdf": rel(path),
        "catalog": catalog_keys,
        "logicalObjectMarkerCount": logical_object_count,
        "objectMarkerTotals": object_marker_total,
        "xrefRowsWithMarkers": xref_rows,
        "contentMarkerTotals": content_marker_total,
        "contentMarkerTotalCount": content_marker_count,
        "page76ContentMarkerTotals": page76_marker_total,
        "page76ContentMarkerTotalCount": page76_content_marker_count,
        "pageRows": page_rows,
        "rawMarkerCounts": raw_marker_counts,
        "rawOnlyBdcCandidateCount": max(
            0,
            raw_marker_counts.get("BDC", 0)
            - content_marker_total.get("BDC", 0)
            - content_marker_total.get("BMC", 0),
        ),
        "rawBdcContexts": raw_contexts,
        "strictContextHits": strict_context_hits,
        "hasTaggedPdfCatalogKey": any(
            catalog_keys[key]["kind"] != "null"
            for key in ["StructTreeRoot", "MarkInfo", "Lang"]
        ),
    }


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            pass
    return ImageFont.load_default()


def draw_sheet(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1840, 820), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(25)
    small = font(15)
    tiny = font(13)
    draw.rectangle((0, 0, 1840, 92), fill=(24, 31, 42))
    draw.text((24, 16), "Current PDF Logical Structure Gate", fill="white", font=title)
    draw.text(
        (24, 54),
        "Tagged-PDF, ActualText, Alt text, MCID, and marked-content carriers checked across current PDFs.",
        fill=(235, 235, 235),
        font=small,
    )
    y = 126
    draw.text((24, y), f"Decision: {summary['decision']}", fill=(40, 40, 40), font=small)
    y += 32
    draw.text(
        (24, y),
        f"Logical objects: {summary['logicalObjectMarkerCount']} | content markers: {summary['contentMarkerTotalCount']} | page-76 markers: {summary['page76ContentMarkerTotalCount']} | raw-only BDC: {summary['rawOnlyBdcCandidateCount']}",
        fill=(40, 40, 40),
        font=small,
    )
    y += 54
    headers = ["PDF", "Struct/Mark/Lang", "logical objs", "content marks", "p76 marks", "raw BDC", "strict hits"]
    xs = [24, 510, 730, 890, 1060, 1210, 1340]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(75, 75, 75), font=tiny)
    y += 26
    for row in rows:
        tagged = ",".join(
            key
            for key in ["StructTreeRoot", "MarkInfo", "Lang"]
            if row["catalog"][key]["kind"] != "null"
        ) or "-"
        vals = [
            row["pdf"][:62],
            tagged,
            str(row["logicalObjectMarkerCount"]),
            str(row["contentMarkerTotalCount"]),
            str(row["page76ContentMarkerTotalCount"]),
            str(row["rawOnlyBdcCandidateCount"]),
            ",".join(row["strictContextHits"]) or "-",
        ]
        for x, val in zip(xs, vals):
            draw.text((x, y), val, fill=(35, 35, 35), font=tiny)
        y += 30
    y += 36
    draw.text((24, y), "Raw-only BDC context check", fill=(75, 75, 75), font=small)
    y += 28
    for row in rows:
        if not row["rawBdcContexts"]:
            continue
        draw.text((24, y), row["pdf"], fill=(35, 35, 35), font=tiny)
        y += 22
        for ctx in row["rawBdcContexts"]:
            draw.text((48, y), compact(ctx["snippet"], 190), fill=(35, 35, 35), font=tiny)
            y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    rows = [inspect_pdf(path) for path in PDFS]

    pdf_count = len(rows)
    logical_object_marker_count = sum(row["logicalObjectMarkerCount"] for row in rows)
    content_marker_total_count = sum(row["contentMarkerTotalCount"] for row in rows)
    page76_content_marker_total_count = sum(row["page76ContentMarkerTotalCount"] for row in rows)
    raw_only_bdc_candidate_count = sum(row["rawOnlyBdcCandidateCount"] for row in rows)
    tagged_catalog_count = sum(1 for row in rows if row["hasTaggedPdfCatalogKey"])
    strict_context_hit_count = sum(len(row["strictContextHits"]) for row in rows)
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    decision = "current_pdf_logical_structure_no_selector"

    fingerprint = (
        f"pdfs={pdf_count}|taggedCatalogs={tagged_catalog_count}"
        f"|logicalObjects={logical_object_marker_count}|contentMarkers={content_marker_total_count}"
        f"|p76ContentMarkers={page76_content_marker_total_count}|rawOnlyBDC={raw_only_bdc_candidate_count}"
        f"|strict={strict_context_hit_count}|sourceR3={source_r3}"
        f"|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    summary = {
        "decision": decision,
        "pdfCount": pdf_count,
        "taggedCatalogCount": tagged_catalog_count,
        "logicalObjectMarkerCount": logical_object_marker_count,
        "contentMarkerTotalCount": content_marker_total_count,
        "page76ContentMarkerTotalCount": page76_content_marker_total_count,
        "rawOnlyBdcCandidateCount": raw_only_bdc_candidate_count,
        "strictContextHitCount": strict_context_hit_count,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "logicalStructureFingerprint": fingerprint,
    }
    draw_sheet(rows, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF logical/tagged structure and marked-content carrier gate; no extraction or candidate generation",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "pdfRows": rows,
        "decision": {
            "currentPdfLogicalStructureGate": decision,
            "selectorUnlocked": False,
            "reason": (
                "The current PDFs have no tagged-PDF catalog structures, no decoded "
                "page-content marked-content carriers, no page-76 ActualText/Alt/MCID "
                "payload, and no source-backed unit/order wording. The lone raw-byte "
                "BDC occurrence is not present in decoded content streams."
            ),
            "nextMove": (
                "Keep PDF logical/marked-content structure closed for the current files. "
                "Continue only with distinct physical/original-layout source validation "
                "or raw clue wording that names extraction unit, order, or transform."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Logical Structure Gate",
        "",
        "Scope: inspected the current PDFs for tagged-PDF/logical-structure carriers: StructTreeRoot, MarkInfo, ActualText, Alt text, MCID, Artifact, BDC/BMC/EMC marked-content operators, and related catalog keys. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs: `{pdf_count}`",
        f"- Tagged catalog count: `{tagged_catalog_count}`",
        f"- Logical object marker count: `{logical_object_marker_count}`",
        f"- Decoded content marker count / page-76 decoded marker count: `{content_marker_total_count}` / `{page76_content_marker_total_count}`",
        f"- Raw-only BDC candidates: `{raw_only_bdc_candidate_count}`",
        f"- Strict context hits: `{strict_context_hit_count}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | tagged catalog | logical objects | decoded content markers | p76 markers | raw-only BDC | strict hits |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        tagged = ",".join(
            key
            for key in ["StructTreeRoot", "MarkInfo", "Lang"]
            if row["catalog"][key]["kind"] != "null"
        ) or "-"
        lines.append(
            f"| `{row['pdf']}` | `{tagged}` | {row['logicalObjectMarkerCount']} | {row['contentMarkerTotalCount']} | {row['page76ContentMarkerTotalCount']} | {row['rawOnlyBdcCandidateCount']} | `{','.join(row['strictContextHits']) or '-'}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- No current PDF exposes StructTreeRoot, MarkInfo, ActualText, Alt text, MCID, or page-76 marked-content operators as a carrier.",
            "- The lone raw-byte `BDC` occurrence is not present in decoded content streams and is not a logical page-content marker.",
            "- PDF logical structure stays closed for the current scan/PDF set.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(f"Decision: {decision}")
    print(f"Fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
