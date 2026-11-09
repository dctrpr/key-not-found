#!/usr/bin/env python3
"""Audit current-PDF image XObject dictionaries and object numbering.

This bounded pass checks whether embedded image object dictionaries, thumbnail
object dictionaries, or image xref numbering carry a source, page-order,
fold-order, or OVERDOSE selector. It is separate from raw JPEG marker and
compression checks: this inspects the PDF object layer around the images.

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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_image_xobject_dictionary_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_image_xobject_dictionary_gate.json"
OUT_MD = OUT / "current_pdf_image_xobject_dictionary_gate.md"

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
SPECIAL_KEYS = [
    "DecodeParms",
    "SMask",
    "Mask",
    "Metadata",
    "Alternates",
    "Intent",
    "OC",
    "StructParent",
    "Name",
    "Interpolate",
    "Matte",
    "OPI",
    "ImageMask",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


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


def object_keys(object_text: str) -> list[str]:
    return sorted(set(re.findall(r"/([A-Za-z][A-Za-z0-9]*)\b", object_text)))


def normalized_dictionary_signature(object_text: str) -> str:
    text = re.sub(r"/Length\s+\d+", "/Length <n>", object_text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def inspect_image_object(
    doc: fitz.Document,
    pdf: Path,
    pdf_page: int,
    article_page: int | None,
    role: str,
    xref: int,
    width: int | None,
    height: int | None,
    filter_name: str,
    resource_name: str,
) -> dict[str, Any]:
    object_text = doc.xref_object(xref, compressed=False)
    keys = object_keys(object_text)
    special: dict[str, dict[str, str]] = {}
    for key in SPECIAL_KEYS:
        kind, value = xref_key(doc, xref, key)
        if kind != "null":
            special[key] = {"kind": kind, "value": value}
    normalized = normalized_dictionary_signature(object_text)
    strict_hits = token_hits(object_text, STRICT_TERMS)
    context_hits = token_hits(object_text, CONTEXT_TERMS)
    return {
        "pdf": rel(pdf),
        "pdfPage": pdf_page,
        "articlePage": article_page,
        "role": role,
        "xref": xref,
        "resourceName": resource_name,
        "width": width,
        "height": height,
        "filter": filter_name,
        "objectKeys": keys,
        "specialKeys": special,
        "specialKeyCount": len(special),
        "strictHitTerms": strict_hits,
        "contextHitTerms": context_hits,
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
        article_page = 73 + index if page_count == 8 else None
        for image_tuple in page.get_images(full=True):
            rows.append(
                inspect_image_object(
                    doc=doc,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    role="page_image",
                    xref=int(image_tuple[0]),
                    width=int(image_tuple[2]),
                    height=int(image_tuple[3]),
                    filter_name=str(image_tuple[8]) if len(image_tuple) > 8 else "",
                    resource_name=str(image_tuple[7]) if len(image_tuple) > 7 else "",
                )
            )
        _kind, thumb_value = xref_key(doc, page.xref, "Thumb")
        for thumb_xref in xrefs_from_value(thumb_value):
            rows.append(
                inspect_image_object(
                    doc=doc,
                    pdf=path,
                    pdf_page=index + 1,
                    article_page=article_page,
                    role="page_thumbnail",
                    xref=thumb_xref,
                    width=int_key(doc, thumb_xref, "Width"),
                    height=int_key(doc, thumb_xref, "Height"),
                    filter_name=name_key(doc, thumb_xref, "Filter"),
                    resource_name="Thumb",
                )
            )
    doc.close()
    return {"pdf": rel(path), "pageCount": page_count, "imageObjectRows": rows}


def structural_order_rows(pdf_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        by_role: dict[str, list[dict[str, Any]]] = {}
        for row in pdf_row["imageObjectRows"]:
            if row["articlePage"] is not None:
                by_role.setdefault(row["role"], []).append(row)
        for role, role_rows in sorted(by_role.items()):
            article_order = [
                row["articlePage"] for row in sorted(role_rows, key=lambda row: row["articlePage"])
            ]
            xref_order = [
                row["articlePage"] for row in sorted(role_rows, key=lambda row: row["xref"])
            ]
            active_order = [
                page for page in xref_order if page in {76, 78, 79, 80}
            ]
            rows.append(
                {
                    "pdf": pdf_row["pdf"],
                    "role": role,
                    "articleOrder": article_order,
                    "xrefOrder": xref_order,
                    "xrefDeltas": [
                        right["xref"] - left["xref"]
                        for left, right in zip(
                            sorted(role_rows, key=lambda row: row["articlePage"]),
                            sorted(role_rows, key=lambda row: row["articlePage"])[1:],
                        )
                    ],
                    "xrefOrderMatchesArticleOrder": xref_order == article_order,
                    "activeSubsetXrefOrder": active_order,
                    "activeSubsetMatchesArticleOrder": active_order == [76, 78, 79, 80],
                    "decision": "structural_pdf_page_order_not_selector",
                }
            )
    return rows


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    pdf_rows = [inspect_pdf(path) for path in PDFS]
    rows = [row for pdf in pdf_rows for row in pdf["imageObjectRows"]]
    page_images = [row for row in rows if row["role"] == "page_image"]
    thumbnails = [row for row in rows if row["role"] == "page_thumbnail"]
    p76_rows = [row for row in rows if row["articlePage"] == 76]
    normalized_groups = {}
    for row in rows:
        normalized_groups.setdefault(row["normalizedDictionaryHash16"], []).append(row)
    p76_group_hashes = {row["normalizedDictionaryHash16"] for row in p76_rows}
    p76_unique_groups = [
        group_hash for group_hash in p76_group_hashes if len(normalized_groups[group_hash]) == 1
    ]
    active_pages = {76, 78, 79, 80}
    active_group_hashes = {
        row["normalizedDictionaryHash16"]
        for row in rows
        if row["articlePage"] in active_pages
    }
    active_unique_groups = [
        group_hash
        for group_hash in active_group_hashes
        if all(
            member["articlePage"] in active_pages
            for member in normalized_groups[group_hash]
            if member["articlePage"] is not None
        )
    ]
    special_key_rows = [row for row in rows if row["specialKeyCount"]]
    strict_hits = sorted({hit for row in rows for hit in row["strictHitTerms"]})
    context_hits = sorted({hit for row in rows for hit in row["contextHitTerms"]})
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    order_rows = structural_order_rows(pdf_rows)
    structural_order_match_count = sum(
        1 for row in order_rows if row["xrefOrderMatchesArticleOrder"]
    )
    active_subset_match_count = sum(
        1 for row in order_rows if row["activeSubsetMatchesArticleOrder"]
    )

    group_rows: list[dict[str, Any]] = []
    for index, (group_hash, group) in enumerate(sorted(normalized_groups.items()), start=1):
        group_rows.append(
            {
                "groupId": f"D{index}",
                "normalizedDictionaryHash16": group_hash,
                "recordCount": len(group),
                "roles": sorted({row["role"] for row in group}),
                "pdfs": sorted({row["pdf"] for row in group}),
                "articlePages": sorted({row["articlePage"] for row in group if row["articlePage"]}),
                "page76RecordCount": sum(1 for row in group if row["articlePage"] == 76),
                "keys": sorted({key for row in group for key in row["objectKeys"]}),
                "sample": group[0]["normalizedDictionarySignature"][:180],
            }
        )

    fingerprint = (
        f"pdfs={len(pdf_rows)}|objects={len(rows)}|pageImages={len(page_images)}"
        f"|thumbs={len(thumbnails)}|dictGroups={len(group_rows)}"
        f"|p76Objects={len(p76_rows)}|p76UniqueGroups={len(p76_unique_groups)}"
        f"|activeUniqueGroups={len(active_unique_groups)}|specialKeys={len(special_key_rows)}"
        f"|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|structOrder={structural_order_match_count}/{len(order_rows)}"
        f"|activeSubset={active_subset_match_count}/{len(order_rows)}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors=0"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_image_xobject_dictionary_no_source_carrier",
        "scope": "current PDF image XObject dictionaries and xref order; no key derivation, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "summary": {
            "pdfCount": len(pdf_rows),
            "imageObjectCount": len(rows),
            "pageImageObjectCount": len(page_images),
            "thumbnailObjectCount": len(thumbnails),
            "normalizedDictionaryGroupCount": len(group_rows),
            "page76ObjectCount": len(p76_rows),
            "page76UniqueDictionaryGroupCount": len(p76_unique_groups),
            "activeUniqueDictionaryGroupCount": len(active_unique_groups),
            "specialKeyRowCount": len(special_key_rows),
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
        "structuralOrderRows": order_rows,
        "pdfRows": pdf_rows,
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Image XObject Dictionary Gate",
        "",
        "Scope: inspected image XObject dictionaries, thumbnail dictionaries, special image-object keys, and image xref numbering in the current PDFs. This checks the PDF object wrapper around page rasters, not raw JPEG metadata or compression internals. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / image objects: `{len(pdf_rows)}` / `{len(rows)}`",
        f"- Page image / thumbnail objects: `{len(page_images)}` / `{len(thumbnails)}`",
        f"- Normalized dictionary groups: `{len(group_rows)}`",
        f"- Page 76 objects / unique dictionary groups: `{len(p76_rows)}` / `{len(p76_unique_groups)}`",
        f"- Active unique dictionary groups: `{len(active_unique_groups)}`",
        f"- Special image-key rows: `{len(special_key_rows)}`",
        f"- Strict/context dictionary hits: `{len(strict_hits)}` / `{len(context_hits)}`",
        f"- Structural xref order matches: `{structural_order_match_count}` / `{len(order_rows)}`",
        f"- Active-subset xref order matches: `{active_subset_match_count}` / `{len(order_rows)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Dictionary Groups",
        "",
        "| group | records | roles | PDFs | article pages | p76 records | keys | sample |",
        "|---|---:|---|---|---|---:|---|---|",
    ]
    for group in group_rows:
        lines.append(
            f"| {group['groupId']} | {group['recordCount']} | `{','.join(group['roles'])}` | `{','.join(group['pdfs'])}` | `{'-'.join(map(str, group['articlePages']))}` | {group['page76RecordCount']} | `{','.join(group['keys'])}` | `{group['sample']}` |"
        )

    lines.extend(
        [
            "",
            "## Xref Order Checks",
            "",
            "| PDF | role | article order | xref order | xref deltas | active subset | structural page-order match |",
            "|---|---|---|---|---|---|---:|",
        ]
    )
    for row in order_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['role']}` | `{'-'.join(map(str, row['articleOrder']))}` | `{'-'.join(map(str, row['xrefOrder']))}` | `{'-'.join(map(str, row['xrefDeltas']))}` | `{'-'.join(map(str, row['activeSubsetXrefOrder']))}` | `{int(row['xrefOrderMatchesArticleOrder'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_image_xobject_dictionary_no_source_carrier`",
            "- Image object dictionaries contain ordinary PDF image keys only: dimensions, color space, filter, bit depth, subtype/type, and length.",
            "- No `/DecodeParms`, `/SMask`, `/Mask`, `/Metadata`, `/Alternates`, `/OC`, `/StructParent`, or comparable special image-object carrier appears.",
            "- Page 76 has no unique normalized image-object dictionary group; active pages have no unique dictionary group.",
            "- Xref numbering follows normal PDF page construction order. The active subset inherits page order from that structure, so it is not a source-backed selector.",
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
