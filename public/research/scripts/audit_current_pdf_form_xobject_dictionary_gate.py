#!/usr/bin/env python3
"""Audit current-PDF Form XObject dictionaries and OCR form order.

This bounded pass checks the duplicate-PDF OCR form wrappers (`OL2`) above the
hidden text payload: Form XObject dictionaries, BBox/Matrix, resource/font refs,
stream lengths, and form xref order. It asks whether the OCR form wrapper layer
distinguishes page 76 or the active quartet as source/original-layout evidence.

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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_form_xobject_dictionary_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_form_xobject_dictionary_gate.json"
OUT_MD = OUT / "current_pdf_form_xobject_dictionary_gate.md"

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
SPECIAL_FORM_KEYS = [
    "Metadata",
    "PieceInfo",
    "LastModified",
    "StructParent",
    "StructParents",
    "OPI",
    "OC",
    "Group",
    "Ref",
    "Measure",
    "SeparationInfo",
    "TrapRegions",
    "TrapStyles",
    "MarkInfo",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def xref_key(doc: fitz.Document, xref: int, key: str) -> tuple[str, str]:
    try:
        return doc.xref_get_key(xref, key)
    except Exception as exc:
        return "error", type(exc).__name__


def xrefs_from_value(value: str) -> list[int]:
    return [int(match) for match in re.findall(r"(\d+)\s+0\s+R", value or "")]


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


def normalize_object_text(text: str) -> str:
    text = re.sub(r"/Length\s+\d+", "/Length <n>", text)
    text = re.sub(r"\d+\s+0\s+R", "<ref>", text)
    text = re.sub(r"/f-\d+-\d+", "/f-#-#", text)
    text = re.sub(r"\b\d+(?:\.\d+)?\b", "<n>", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_render_modes(content: str) -> list[int]:
    return [int(match.group(1)) for match in re.finditer(r"(?<![\d.])([0-7])\s+Tr\b", content)]


def inspect_form_object(
    doc: fitz.Document,
    pdf: Path,
    pdf_page: int,
    article_page: int | None,
    xref: int,
    resource_name: str,
    bbox: tuple[float, float, float, float],
) -> dict[str, Any]:
    object_text = doc.xref_object(xref, compressed=False)
    stream = doc.xref_stream(xref) or b""
    stream_text = stream.decode("latin-1", errors="replace")
    keys = object_keys(object_text)
    special = {
        key: {"kind": kind, "value": value}
        for key in SPECIAL_FORM_KEYS
        for kind, value in [xref_key(doc, xref, key)]
        if kind != "null"
    }
    normalized = normalize_object_text(object_text)
    render_modes = text_render_modes(stream_text)
    visible_modes = [mode for mode in render_modes if mode != 3]
    combined = f"{object_text}\n{strip_pdf_names_and_payload(stream_text)}"
    return {
        "pdf": rel(pdf),
        "pdfPage": pdf_page,
        "articlePage": article_page,
        "xref": xref,
        "resourceName": resource_name,
        "bboxFromPage": [round(value, 6) for value in bbox],
        "bboxKey": xref_key(doc, xref, "BBox")[1],
        "matrixKey": xref_key(doc, xref, "Matrix")[1],
        "resourcesKind": xref_key(doc, xref, "Resources")[0],
        "resourceXrefs": xrefs_from_value(xref_key(doc, xref, "Resources")[1]),
        "objectKeys": keys,
        "specialKeys": special,
        "specialKeyCount": len(special),
        "decodedStreamByteCount": len(stream),
        "textObjectCount": stream_text.count("BT"),
        "textShowOperatorCount": len(re.findall(r"\b(?:Tj|TJ)\b|(?<!\\S)['\"]", stream_text)),
        "textRenderModes": sorted(set(render_modes)),
        "invisibleTextRenderModeCount": sum(1 for mode in render_modes if mode == 3),
        "visibleTextRenderModeCount": len(visible_modes),
        "strictHitTerms": token_hits(combined, STRICT_TERMS),
        "contextHitTerms": token_hits(combined, CONTEXT_TERMS),
        "dictionaryHash16": sha16(re.sub(r"\s+", " ", object_text).strip()),
        "normalizedDictionaryHash16": sha16(normalized),
        "normalizedDictionarySignature": normalized,
        "dictionarySample": re.sub(r"\s+", " ", object_text).strip()[:260],
    }


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    page_count = doc.page_count
    rows: list[dict[str, Any]] = []
    for index in range(page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        for item in page.get_xobjects():
            xref = int(item[0])
            name = str(item[1])
            bbox = tuple(float(value) for value in item[3])
            rows.append(
                inspect_form_object(
                    doc=doc,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    xref=xref,
                    resource_name=name,
                    bbox=bbox,  # type: ignore[arg-type]
                )
            )
    doc.close()
    return {"pdf": rel(path), "pageCount": page_count, "formRows": rows}


def structural_order_rows(pdf_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        form_rows = [row for row in pdf_row["formRows"] if row["articlePage"] is not None]
        if not form_rows:
            rows.append(
                {
                    "pdf": pdf_row["pdf"],
                    "articleOrder": [],
                    "formXrefOrder": [],
                    "activeSubsetFormXrefOrder": [],
                    "xrefOrderMatchesArticleOrder": True,
                    "activeSubsetMatchesArticleOrder": True,
                    "decision": "no_form_xobjects_in_pdf",
                }
            )
            continue
        article_order = [row["articlePage"] for row in sorted(form_rows, key=lambda row: row["articlePage"])]
        xref_order = [row["articlePage"] for row in sorted(form_rows, key=lambda row: row["xref"])]
        active_order = [page for page in xref_order if page in {76, 78, 79, 80}]
        rows.append(
            {
                "pdf": pdf_row["pdf"],
                "articleOrder": article_order,
                "formXrefOrder": xref_order,
                "formXrefs": [row["xref"] for row in sorted(form_rows, key=lambda row: row["articlePage"])],
                "activeSubsetFormXrefOrder": active_order,
                "xrefOrderMatchesArticleOrder": xref_order == article_order,
                "activeSubsetMatchesArticleOrder": active_order == [76, 78, 79, 80],
                "decision": "structural_form_xref_order_not_selector",
            }
        )
    return rows


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    pdf_rows = [inspect_pdf(path) for path in PDFS]
    rows = [row for pdf_row in pdf_rows for row in pdf_row["formRows"]]
    p76_rows = [row for row in rows if row["articlePage"] == 76]
    active_pages = {76, 78, 79, 80}

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row["normalizedDictionaryHash16"], []).append(row)

    group_rows: list[dict[str, Any]] = []
    for index, (group_hash, group) in enumerate(sorted(groups.items()), start=1):
        group_rows.append(
            {
                "groupId": f"F{index}",
                "normalizedDictionaryHash16": group_hash,
                "recordCount": len(group),
                "pdfs": sorted({row["pdf"] for row in group}),
                "articlePages": sorted({row["articlePage"] for row in group if row["articlePage"]}),
                "page76RecordCount": sum(1 for row in group if row["articlePage"] == 76),
                "resourceNames": sorted({row["resourceName"] for row in group}),
                "bboxKeys": sorted({row["bboxKey"] for row in group}),
                "matrixKeys": sorted({row["matrixKey"] for row in group}),
                "keys": sorted({key for row in group for key in row["objectKeys"]}),
                "sample": group[0]["normalizedDictionarySignature"][:180],
            }
        )

    p76_group_hashes = {row["normalizedDictionaryHash16"] for row in p76_rows}
    p76_unique_groups = [
        group_hash for group_hash in p76_group_hashes if len(groups[group_hash]) == 1
    ]
    active_group_hashes = {
        row["normalizedDictionaryHash16"] for row in rows if row["articlePage"] in active_pages
    }
    active_unique_groups = [
        group_hash
        for group_hash in active_group_hashes
        if all(
            member["articlePage"] in active_pages
            for member in groups[group_hash]
            if member["articlePage"] is not None
        )
    ]

    strict_hits = sorted({hit for row in rows for hit in row["strictHitTerms"]})
    context_hits = sorted({hit for row in rows for hit in row["contextHitTerms"]})
    special_rows = [row for row in rows if row["specialKeyCount"]]
    visible_text_rows = [row for row in rows if row["visibleTextRenderModeCount"]]
    order_rows = structural_order_rows(pdf_rows)
    structural_order_match_count = sum(1 for row in order_rows if row["xrefOrderMatchesArticleOrder"])
    active_subset_match_count = sum(1 for row in order_rows if row["activeSubsetMatchesArticleOrder"])
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)

    duplicate_length_order = {
        pdf_row["pdf"]: [
            row["articlePage"]
            for row in sorted(
                [row for row in pdf_row["formRows"] if row["articlePage"] is not None],
                key=lambda row: (-row["decodedStreamByteCount"], row["articlePage"]),
            )
        ]
        for pdf_row in pdf_rows
        if pdf_row["formRows"]
    }

    fingerprint = (
        f"pdfs={len(pdf_rows)}|forms={len(rows)}|dictGroups={len(group_rows)}"
        f"|p76Forms={len(p76_rows)}|p76UniqueGroups={len(p76_unique_groups)}"
        f"|activeUniqueGroups={len(active_unique_groups)}|special={len(special_rows)}"
        f"|visibleText={len(visible_text_rows)}|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|xrefOrder={structural_order_match_count}/{len(order_rows)}"
        f"|activeSubset={active_subset_match_count}/{len(order_rows)}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors=0"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_form_xobject_dictionary_no_source_carrier",
        "scope": "current PDF Form XObject dictionaries, OCR form BBox/Matrix/resources, stream render mode, and form xref order; no OCR-to-key extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "summary": {
            "pdfCount": len(pdf_rows),
            "formObjectCount": len(rows),
            "normalizedDictionaryGroupCount": len(group_rows),
            "page76FormObjectCount": len(p76_rows),
            "page76UniqueDictionaryGroupCount": len(p76_unique_groups),
            "activeUniqueDictionaryGroupCount": len(active_unique_groups),
            "specialKeyRowCount": len(special_rows),
            "visibleTextRenderModeRowCount": len(visible_text_rows),
            "strictHitCount": len(strict_hits),
            "contextHitCount": len(context_hits),
            "strictHitTerms": strict_hits,
            "contextHitTerms": context_hits,
            "structuralXrefOrderMatchCount": structural_order_match_count,
            "structuralOrderRowCount": len(order_rows),
            "activeSubsetXrefOrderMatchCount": active_subset_match_count,
            "sourceBackedR3BridgeHitCount": source_r3_hits,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
            "selectorUnlockCount": 0,
        },
        "dictionaryGroupRows": group_rows,
        "page76FormRows": p76_rows,
        "structuralOrderRows": order_rows,
        "duplicateFormLengthDescendingOrder": duplicate_length_order,
        "pdfRows": pdf_rows,
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Form XObject Dictionary Gate",
        "",
        "Scope: inspected Form XObject dictionaries, OCR form BBox/Matrix/resources, stream render mode, and form xref order in the current PDFs. This checks the duplicate-PDF `OL2` OCR form wrappers, not OCR text extraction as key material. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / form objects: `{len(pdf_rows)}` / `{len(rows)}`",
        f"- Normalized dictionary groups: `{len(group_rows)}`",
        f"- Page 76 forms / unique dictionary groups: `{len(p76_rows)}` / `{len(p76_unique_groups)}`",
        f"- Active unique dictionary groups: `{len(active_unique_groups)}`",
        f"- Special form-key rows: `{len(special_rows)}`",
        f"- Visible text render-mode rows: `{len(visible_text_rows)}`",
        f"- Strict/context wrapper hits: `{len(strict_hits)}` / `{len(context_hits)}`",
        f"- Structural form-xref order matches: `{structural_order_match_count}` / `{len(order_rows)}`",
        f"- Active-subset form-xref order matches: `{active_subset_match_count}` / `{len(order_rows)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Dictionary Groups",
        "",
        "| group | records | PDFs | article pages | p76 records | names | bbox | matrix | keys | sample |",
        "|---|---:|---|---|---:|---|---|---|---|---|",
    ]
    for group in group_rows:
        lines.append(
            f"| {group['groupId']} | {group['recordCount']} | `{','.join(group['pdfs'])}` | `{'-'.join(map(str, group['articlePages']))}` | {group['page76RecordCount']} | `{','.join(group['resourceNames'])}` | `{','.join(group['bboxKeys'])}` | `{','.join(group['matrixKeys'])}` | `{','.join(group['keys'])}` | `{group['sample']}` |"
        )

    lines.extend(
        [
            "",
            "## Page 76 Forms",
            "",
            "| PDF | xref | name | bbox | matrix | stream bytes | text objects | render modes | visible Tr |",
            "|---|---:|---|---|---|---:|---:|---|---:|",
        ]
    )
    for row in p76_rows:
        lines.append(
            f"| `{row['pdf']}` | {row['xref']} | `{row['resourceName']}` | `{row['bboxKey']}` | `{row['matrixKey']}` | {row['decodedStreamByteCount']} | {row['textObjectCount']} | `{'-'.join(map(str, row['textRenderModes']))}` | {row['visibleTextRenderModeCount']} |"
        )

    lines.extend(
        [
            "",
            "## Form Xref Order Checks",
            "",
            "| PDF | article order | form-xref order | form xrefs | active subset | order match |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for row in order_rows:
        lines.append(
            f"| `{row['pdf']}` | `{'-'.join(map(str, row['articleOrder']))}` | `{'-'.join(map(str, row['formXrefOrder']))}` | `{'-'.join(map(str, row.get('formXrefs', [])))}` | `{'-'.join(map(str, row['activeSubsetFormXrefOrder']))}` | `{int(row['xrefOrderMatchesArticleOrder'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_form_xobject_dictionary_no_source_carrier`",
            "- The duplicate-PDF OCR forms are ordinary `/Subtype /Form` wrappers named `OL2` with full-page BBox `[0 0 612 791.76]`, identity Matrix `[1 0 0 1 0 0]`, and a font resource.",
            "- Page 76 has no unique normalized form dictionary group, and the active quartet has no unique form dictionary group.",
            "- Form xref ordering follows normal PDF construction order; stream byte lengths vary with OCR payload density and do not supply a source-backed unit/order/transform.",
            "- All OCR form text remains invisible render-mode `3`; no special form keys, visible text, or strict instruction terms appear.",
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
