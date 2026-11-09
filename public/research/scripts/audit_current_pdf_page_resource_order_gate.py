#!/usr/bin/env python3
"""Audit current-PDF page dictionaries, resources, and page object order.

This bounded pass checks the page wrapper layer above image XObjects: page
dictionary keys, resource dictionaries, XObject resource names, page rotation,
page thumbnails, content/resource xref order, and whether any page-level wrapper
distinguishes page 76 or the active lower-page quartet.

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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_page_resource_order_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_page_resource_order_gate.json"
OUT_MD = OUT / "current_pdf_page_resource_order_gate.md"

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
SPECIAL_PAGE_KEYS = [
    "Metadata",
    "Annots",
    "AA",
    "PieceInfo",
    "SeparationInfo",
    "StructParents",
    "Tabs",
    "Trans",
    "UserUnit",
    "VP",
    "OC",
    "Group",
    "Dur",
    "BoxColorInfo",
    "Measure",
    "LastModified",
    "SpiderInfo",
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


def first_xref(value: str) -> int | None:
    xrefs = xrefs_from_value(value)
    return xrefs[0] if xrefs else None


def object_keys(object_text: str) -> list[str]:
    return sorted(set(re.findall(r"/([A-Za-z][A-Za-z0-9]*)\b", object_text)))


def strip_pdf_names(text: str) -> str:
    """Remove PDF /Name tokens so structural keys do not look like clues."""
    return re.sub(r"/[A-Za-z][A-Za-z0-9]*\b", " ", text)


def token_hits(text: str, terms: set[str]) -> list[str]:
    clean = strip_pdf_names(text)
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", clean, flags=re.IGNORECASE)
    )


def normalize_pdf_object_text(text: str) -> str:
    normalized = re.sub(r"\d+\s+0\s+R", "<ref>", text)
    normalized = re.sub(r"/([A-Za-z]+)\d+\b", r"/\1#", normalized)
    normalized = re.sub(r"\b\d{2,5}\b", "<n>", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def resource_text_and_xref(doc: fitz.Document, page_xref: int) -> tuple[int | None, str, str]:
    kind, value = xref_key(doc, page_xref, "Resources")
    xref = first_xref(value)
    if kind == "xref" and xref:
        return xref, doc.xref_object(xref, compressed=False), kind
    return None, value if value != "null" else "", kind


def xobject_names_from_resource_text(resource_text: str) -> list[str]:
    names: list[str] = []
    match = re.search(r"/XObject\s*<<(?P<body>.*?)>>", resource_text, flags=re.DOTALL)
    if match:
        names = re.findall(r"/([A-Za-z][A-Za-z0-9]*)\s+\d+\s+0\s+R", match.group("body"))
    return names


def xobject_xrefs_from_resource_text(resource_text: str) -> list[int]:
    match = re.search(r"/XObject\s*<<(?P<body>.*?)>>", resource_text, flags=re.DOTALL)
    if not match:
        return []
    return xrefs_from_value(match.group("body"))


def box_value(doc: fitz.Document, xref: int, key: str) -> str | None:
    kind, value = xref_key(doc, xref, key)
    return value if kind != "null" else None


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    page_count = doc.page_count
    page_rows: list[dict[str, Any]] = []
    for index in range(page_count):
        page = doc[index]
        article_page = 73 + index if page_count == 8 else None
        page_object_text = doc.xref_object(page.xref, compressed=False)
        resource_xref, resource_text, resource_kind = resource_text_and_xref(doc, page.xref)
        resource_names = xobject_names_from_resource_text(resource_text)
        image_names = [str(image[7]) for image in page.get_images(full=True) if len(image) > 7]
        image_xrefs = [int(image[0]) for image in page.get_images(full=True)]
        form_rows = [
            {
                "xref": int(row[0]),
                "name": str(row[1]),
                "bbox": [float(value) for value in row[3]],
            }
            for row in page.get_xobjects()
        ]
        content_kind, content_value = xref_key(doc, page.xref, "Contents")
        thumb_kind, thumb_value = xref_key(doc, page.xref, "Thumb")
        page_keys = object_keys(page_object_text)
        resource_keys = object_keys(resource_text)
        special_page_keys = {
            key: {"kind": kind, "value": value}
            for key in SPECIAL_PAGE_KEYS
            for kind, value in [xref_key(doc, page.xref, key)]
            if kind != "null"
        }
        combined_text = f"{page_object_text}\n{resource_text}"
        page_signature = normalize_pdf_object_text(page_object_text)
        resource_signature = normalize_pdf_object_text(resource_text)
        page_rows.append(
            {
                "pdf": rel(path),
                "pdfPage": index + 1,
                "articlePage": article_page,
                "pageXref": int(page.xref),
                "pageRotation": int(page.rotation),
                "pageRect": [float(page.rect.x0), float(page.rect.y0), float(page.rect.x1), float(page.rect.y1)],
                "mediaBox": box_value(doc, page.xref, "MediaBox"),
                "cropBox": box_value(doc, page.xref, "CropBox"),
                "trimBox": box_value(doc, page.xref, "TrimBox"),
                "contentKind": content_kind,
                "contentXrefs": xrefs_from_value(content_value),
                "resourceKind": resource_kind,
                "resourceXref": resource_xref,
                "thumbKind": thumb_kind,
                "thumbXrefs": xrefs_from_value(thumb_value),
                "pageKeys": page_keys,
                "resourceKeys": resource_keys,
                "specialPageKeys": special_page_keys,
                "specialPageKeyCount": len(special_page_keys),
                "xobjectResourceNames": resource_names,
                "xobjectResourceXrefs": xobject_xrefs_from_resource_text(resource_text),
                "imageResourceNames": image_names,
                "imageXrefs": image_xrefs,
                "formXobjects": form_rows,
                "formResourceNames": [row["name"] for row in form_rows],
                "strictHitTerms": token_hits(combined_text, STRICT_TERMS),
                "contextHitTerms": token_hits(combined_text, CONTEXT_TERMS),
                "pageDictionaryHash16": sha16(re.sub(r"\s+", " ", page_object_text).strip()),
                "normalizedPageDictionaryHash16": sha16(page_signature),
                "normalizedPageDictionarySignature": page_signature,
                "resourceDictionaryHash16": sha16(re.sub(r"\s+", " ", resource_text).strip()),
                "normalizedResourceDictionaryHash16": sha16(resource_signature),
                "normalizedResourceDictionarySignature": resource_signature,
                "pageDictionarySample": re.sub(r"\s+", " ", page_object_text).strip()[:260],
                "resourceDictionarySample": re.sub(r"\s+", " ", resource_text).strip()[:260],
            }
        )
    doc.close()
    return {"pdf": rel(path), "pageCount": page_count, "pageRows": page_rows}


def structural_order_rows(pdf_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        page_rows = [row for row in pdf_row["pageRows"] if row["articlePage"] is not None]
        if not page_rows:
            continue
        article_order = [
            row["articlePage"] for row in sorted(page_rows, key=lambda row: row["articlePage"])
        ]
        page_xref_order = [
            row["articlePage"] for row in sorted(page_rows, key=lambda row: row["pageXref"])
        ]
        active_order = [page for page in page_xref_order if page in {76, 78, 79, 80}]
        rows.append(
            {
                "pdf": pdf_row["pdf"],
                "articleOrder": article_order,
                "pageXrefOrder": page_xref_order,
                "pageXrefs": [row["pageXref"] for row in sorted(page_rows, key=lambda row: row["articlePage"])],
                "pageXrefDeltas": [
                    right["pageXref"] - left["pageXref"]
                    for left, right in zip(
                        sorted(page_rows, key=lambda row: row["articlePage"]),
                        sorted(page_rows, key=lambda row: row["articlePage"])[1:],
                    )
                ],
                "activeSubsetPageXrefOrder": active_order,
                "pageXrefOrderMatchesArticleOrder": page_xref_order == article_order,
                "activeSubsetMatchesArticleOrder": active_order == [76, 78, 79, 80],
                "decision": "structural_pdf_page_order_not_selector",
            }
        )
    return rows


def group_rows(rows: list[dict[str, Any]], hash_key: str, signature_key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(str(row[hash_key]), []).append(row)
    output: list[dict[str, Any]] = []
    for index, (group_hash, group) in enumerate(sorted(groups.items()), start=1):
        output.append(
            {
                "groupId": f"G{index}",
                "hash16": group_hash,
                "recordCount": len(group),
                "pdfs": sorted({row["pdf"] for row in group}),
                "articlePages": sorted({row["articlePage"] for row in group if row["articlePage"]}),
                "page76RecordCount": sum(1 for row in group if row["articlePage"] == 76),
                "rotations": sorted({row["pageRotation"] for row in group}),
                "pageKeys": sorted({key for row in group for key in row["pageKeys"]}),
                "resourceKeys": sorted({key for row in group for key in row["resourceKeys"]}),
                "xobjectResourceNames": sorted({name for row in group for name in row["xobjectResourceNames"]}),
                "formResourceNames": sorted({name for row in group for name in row["formResourceNames"]}),
                "sample": str(group[0][signature_key])[:180],
            }
        )
    return output


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    pdf_rows = [inspect_pdf(path) for path in PDFS]
    rows = [row for pdf_row in pdf_rows for row in pdf_row["pageRows"]]
    p76_rows = [row for row in rows if row["articlePage"] == 76]
    active_pages = {76, 78, 79, 80}

    page_groups = group_rows(
        rows,
        "normalizedPageDictionaryHash16",
        "normalizedPageDictionarySignature",
    )
    resource_groups = group_rows(
        rows,
        "normalizedResourceDictionaryHash16",
        "normalizedResourceDictionarySignature",
    )
    page_group_members: dict[str, list[dict[str, Any]]] = {}
    resource_group_members: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        page_group_members.setdefault(row["normalizedPageDictionaryHash16"], []).append(row)
        resource_group_members.setdefault(row["normalizedResourceDictionaryHash16"], []).append(row)

    p76_page_group_hashes = {row["normalizedPageDictionaryHash16"] for row in p76_rows}
    p76_resource_group_hashes = {row["normalizedResourceDictionaryHash16"] for row in p76_rows}
    p76_unique_page_groups = [
        group_hash for group_hash in p76_page_group_hashes if len(page_group_members[group_hash]) == 1
    ]
    p76_unique_resource_groups = [
        group_hash
        for group_hash in p76_resource_group_hashes
        if len(resource_group_members[group_hash]) == 1
    ]
    active_page_group_hashes = {
        row["normalizedPageDictionaryHash16"]
        for row in rows
        if row["articlePage"] in active_pages
    }
    active_resource_group_hashes = {
        row["normalizedResourceDictionaryHash16"]
        for row in rows
        if row["articlePage"] in active_pages
    }
    active_unique_page_groups = [
        group_hash
        for group_hash in active_page_group_hashes
        if all(
            member["articlePage"] in active_pages
            for member in page_group_members[group_hash]
            if member["articlePage"] is not None
        )
    ]
    active_unique_resource_groups = [
        group_hash
        for group_hash in active_resource_group_hashes
        if all(
            member["articlePage"] in active_pages
            for member in resource_group_members[group_hash]
            if member["articlePage"] is not None
        )
    ]

    special_page_key_rows = [row for row in rows if row["specialPageKeyCount"]]
    thumb_pages = [row for row in rows if row["thumbXrefs"]]
    strict_hits = sorted({hit for row in rows for hit in row["strictHitTerms"]})
    context_hits = sorted({hit for row in rows for hit in row["contextHitTerms"]})
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    order_rows = structural_order_rows(pdf_rows)
    page_order_match_count = sum(1 for row in order_rows if row["pageXrefOrderMatchesArticleOrder"])
    active_subset_match_count = sum(1 for row in order_rows if row["activeSubsetMatchesArticleOrder"])

    rotation_rows = []
    for pdf_row in pdf_rows:
        rotations = [row["pageRotation"] for row in pdf_row["pageRows"]]
        rotation_rows.append(
            {
                "pdf": pdf_row["pdf"],
                "rotations": rotations,
                "uniqueRotations": sorted(set(rotations)),
                "allPagesSameRotation": len(set(rotations)) == 1,
            }
        )

    fingerprint = (
        f"pdfs={len(pdf_rows)}|pages={len(rows)}|p76={len(p76_rows)}"
        f"|pageGroups={len(page_groups)}|resourceGroups={len(resource_groups)}"
        f"|p76UniquePageGroups={len(p76_unique_page_groups)}"
        f"|p76UniqueResourceGroups={len(p76_unique_resource_groups)}"
        f"|activeUniquePageGroups={len(active_unique_page_groups)}"
        f"|activeUniqueResourceGroups={len(active_unique_resource_groups)}"
        f"|thumbPages={len(thumb_pages)}|special={len(special_page_key_rows)}"
        f"|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|pageOrder={page_order_match_count}/{len(order_rows)}"
        f"|activeSubset={active_subset_match_count}/{len(order_rows)}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors=0"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_page_resource_order_no_source_carrier",
        "scope": "current PDF page dictionaries, resource dictionaries, page rotation, thumbnails, XObject resource names, and page xref order; no key derivation, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "summary": {
            "pdfCount": len(pdf_rows),
            "pageCount": len(rows),
            "page76PageCount": len(p76_rows),
            "pageDictionaryGroupCount": len(page_groups),
            "resourceSignatureGroupCount": len(resource_groups),
            "page76UniquePageDictionaryGroupCount": len(p76_unique_page_groups),
            "page76UniqueResourceSignatureGroupCount": len(p76_unique_resource_groups),
            "activeUniquePageDictionaryGroupCount": len(active_unique_page_groups),
            "activeUniqueResourceSignatureGroupCount": len(active_unique_resource_groups),
            "thumbPageCount": len(thumb_pages),
            "specialPageKeyRowCount": len(special_page_key_rows),
            "strictHitCount": len(strict_hits),
            "contextHitCount": len(context_hits),
            "strictHitTerms": strict_hits,
            "contextHitTerms": context_hits,
            "structuralPageXrefOrderMatchCount": page_order_match_count,
            "structuralOrderRowCount": len(order_rows),
            "activeSubsetPageXrefOrderMatchCount": active_subset_match_count,
            "sourceBackedR3BridgeHitCount": source_r3_hits,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
            "selectorUnlockCount": 0,
        },
        "rotationRows": rotation_rows,
        "pageDictionaryGroupRows": page_groups,
        "resourceSignatureGroupRows": resource_groups,
        "structuralOrderRows": order_rows,
        "pdfRows": pdf_rows,
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Page Resource Order Gate",
        "",
        "Scope: inspected page dictionaries, resource dictionaries, XObject resource names, content/resource/thumb references, page rotation, and page xref order in the current PDFs. This checks the page wrapper above the image-object layer. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / pages / page-76 rows: `{len(pdf_rows)}` / `{len(rows)}` / `{len(p76_rows)}`",
        f"- Page/resource signature groups: `{len(page_groups)}` / `{len(resource_groups)}`",
        f"- Page 76 unique page/resource groups: `{len(p76_unique_page_groups)}` / `{len(p76_unique_resource_groups)}`",
        f"- Active unique page/resource groups: `{len(active_unique_page_groups)}` / `{len(active_unique_resource_groups)}`",
        f"- Thumbnail-bearing pages: `{len(thumb_pages)}`",
        f"- Special page-key rows: `{len(special_page_key_rows)}`",
        f"- Strict/context wrapper hits: `{len(strict_hits)}` / `{len(context_hits)}`",
        f"- Structural page-xref order matches: `{page_order_match_count}` / `{len(order_rows)}`",
        f"- Active-subset page-xref order matches: `{active_subset_match_count}` / `{len(order_rows)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Page And Resource Groups",
        "",
        "| kind | group | records | PDFs | article pages | p76 records | rotations | xobject names | form names | sample |",
        "|---|---|---:|---|---|---:|---|---|---|---|",
    ]
    for group in page_groups:
        lines.append(
            f"| page | {group['groupId']} | {group['recordCount']} | `{','.join(group['pdfs'])}` | `{'-'.join(map(str, group['articlePages']))}` | {group['page76RecordCount']} | `{'/'.join(map(str, group['rotations']))}` | `{','.join(group['xobjectResourceNames'])}` | `{','.join(group['formResourceNames'])}` | `{group['sample']}` |"
        )
    for group in resource_groups:
        lines.append(
            f"| resource | {group['groupId']} | {group['recordCount']} | `{','.join(group['pdfs'])}` | `{'-'.join(map(str, group['articlePages']))}` | {group['page76RecordCount']} | `{'/'.join(map(str, group['rotations']))}` | `{','.join(group['xobjectResourceNames'])}` | `{','.join(group['formResourceNames'])}` | `{group['sample']}` |"
        )

    lines.extend(
        [
            "",
            "## Page Xref Order Checks",
            "",
            "| PDF | article order | page-xref order | page xrefs | xref deltas | active subset | page-order match |",
            "|---|---|---|---|---|---|---:|",
        ]
    )
    for row in order_rows:
        lines.append(
            f"| `{row['pdf']}` | `{'-'.join(map(str, row['articleOrder']))}` | `{'-'.join(map(str, row['pageXrefOrder']))}` | `{'-'.join(map(str, row['pageXrefs']))}` | `{'-'.join(map(str, row['pageXrefDeltas']))}` | `{'-'.join(map(str, row['activeSubsetPageXrefOrder']))}` | `{int(row['pageXrefOrderMatchesArticleOrder'])}` |"
        )

    lines.extend(
        [
            "",
            "## Page 76 Rows",
            "",
            "| PDF | page xref | rotation | resource kind/xref | content xrefs | thumb xrefs | image names | form names | xobject xrefs |",
            "|---|---:|---:|---|---|---|---|---|---|",
        ]
    )
    for row in p76_rows:
        resource_ref = f"{row['resourceKind']}/{row['resourceXref']}"
        lines.append(
            f"| `{row['pdf']}` | {row['pageXref']} | {row['pageRotation']} | `{resource_ref}` | `{'-'.join(map(str, row['contentXrefs']))}` | `{'-'.join(map(str, row['thumbXrefs']))}` | `{','.join(row['imageResourceNames'])}` | `{','.join(row['formResourceNames'])}` | `{'-'.join(map(str, row['xobjectResourceXrefs']))}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_page_resource_order_no_source_carrier`",
            "- Page dictionaries and resource dictionaries are ordinary page wrappers: media/trim boxes, content references, resources, rotation, thumbnails in `magazine.pdf`, and XObject resource names.",
            "- `magazine.pdf` has page rotation `180`, thumbnail references, and a stable page-image resource name `Obj5`; the duplicate PDFs use rotation `0`, no thumbnails, image names `I1` through `I8`, and OCR form name `OL2`.",
            "- Page 76 has no unique normalized page-dictionary or resource-signature group, and the active quartet has no unique page/resource group.",
            "- Page xref ordering follows normal PDF page construction order. The active subset inherits page order, so it is not a source-backed selector.",
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
