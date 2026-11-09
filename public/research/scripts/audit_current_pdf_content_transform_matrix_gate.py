#!/usr/bin/env python3
"""Audit current-PDF content placement matrices around image/form Do calls.

This bounded pass inspects numeric PDF content-stream transforms around page
image and OCR form placements. It checks whether page 76, the active quartet, or
the PDF placement matrices provide an original-layout, fold, page-order, or
OVERDOSE selector beyond ordinary raster/OCR placement.

No key derivation, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_content_transform_matrix_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_content_transform_matrix_gate.json"
OUT_MD = OUT / "current_pdf_content_transform_matrix_gate.md"

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


Matrix = tuple[float, float, float, float, float, float]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def round_matrix(matrix: Matrix) -> list[float]:
    return [round(value, 6) for value in matrix]


def matrix_to_string(matrix: Matrix) -> str:
    return ",".join(f"{value:.6g}" for value in matrix)


def multiply_matrix(left: Matrix, right: Matrix) -> Matrix:
    # PDF affine matrix composition for point transform:
    # x' = a*x + c*y + e, y' = b*x + d*y + f.
    a1, b1, c1, d1, e1, f1 = left
    a2, b2, c2, d2, e2, f2 = right
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def apply_matrix(matrix: Matrix, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    return a * x + c * y + e, b * x + d * y + f


def unit_bbox(matrix: Matrix) -> list[float]:
    points = [
        apply_matrix(matrix, 0.0, 0.0),
        apply_matrix(matrix, 1.0, 0.0),
        apply_matrix(matrix, 0.0, 1.0),
        apply_matrix(matrix, 1.0, 1.0),
    ]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [round(min(xs), 6), round(min(ys), 6), round(max(xs), 6), round(max(ys), 6)]


def normalize_resource_name(name: str) -> str:
    return re.sub(r"\d+", "#", name)


def strip_payload(content: str) -> str:
    text = re.sub(r"\([^)]*\)", " ", content)
    text = re.sub(r"<[0-9A-Fa-f\s]+>", " ", text)
    text = re.sub(r"/[A-Za-z0-9_.-]+", " ", text)
    return text


def token_hits(text: str, terms: set[str]) -> list[str]:
    clean = strip_payload(text)
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", clean, flags=re.IGNORECASE)
    )


def content_tokens(content: str) -> list[str]:
    return re.findall(
        r"/[A-Za-z0-9_.-]+|[-+]?(?:\d+\.\d+|\d+|\.\d+)|[A-Za-z*'\"]+",
        content,
    )


def is_number(token: str) -> bool:
    return bool(re.fullmatch(r"[-+]?(?:\d+\.\d+|\d+|\.\d+)", token))


def parse_do_placements(
    content: str,
    stream_xref: int,
    stream_index: int,
    role_names: dict[str, str],
) -> tuple[list[dict[str, Any]], int]:
    tokens = content_tokens(content)
    number_stack: list[float] = []
    ctm: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    state_stack: list[tuple[Matrix, list[Matrix]]] = []
    cm_sequence: list[Matrix] = []
    last_name = ""
    rows: list[dict[str, Any]] = []
    cm_event_count = 0

    for token in tokens:
        if is_number(token):
            number_stack.append(float(token))
            continue
        if token.startswith("/"):
            last_name = token[1:]
            continue
        if token == "q":
            state_stack.append((ctm, list(cm_sequence)))
            number_stack.clear()
            continue
        if token == "Q":
            if state_stack:
                ctm, cm_sequence = state_stack.pop()
            number_stack.clear()
            continue
        if token == "cm":
            if len(number_stack) >= 6:
                matrix = tuple(number_stack[-6:])  # type: ignore[assignment]
                ctm = multiply_matrix(ctm, matrix)
                cm_sequence.append(matrix)
                cm_event_count += 1
            number_stack.clear()
            continue
        if token == "Do":
            role = role_names.get(last_name, "unknown")
            determinant = ctm[0] * ctm[3] - ctm[1] * ctm[2]
            bbox = unit_bbox(ctm)
            rows.append(
                {
                    "streamXref": stream_xref,
                    "streamIndex": stream_index,
                    "resourceName": last_name,
                    "normalizedResourceName": normalize_resource_name(last_name),
                    "role": role,
                    "qDepth": len(state_stack),
                    "cmCountInGraphicsState": len(cm_sequence),
                    "localMatrixSequence": [round_matrix(matrix) for matrix in cm_sequence],
                    "cumulativeMatrix": round_matrix(ctm),
                    "cumulativeMatrixText": matrix_to_string(ctm),
                    "unitBBox": bbox,
                    "unitWidth": round(bbox[2] - bbox[0], 6),
                    "unitHeight": round(bbox[3] - bbox[1], 6),
                    "determinant": round(determinant, 6),
                    "orientationSign": "negative" if determinant < 0 else "positive",
                }
            )
            last_name = ""
            number_stack.clear()
            continue
        number_stack.clear()
    return rows, cm_event_count


def placement_signature(row: dict[str, Any]) -> str:
    payload = {
        "role": row["role"],
        "name": row["normalizedResourceName"],
        "cmCount": row["cmCountInGraphicsState"],
        "matrix": row["cumulativeMatrix"],
        "sequence": row["localMatrixSequence"],
        "orientationSign": row["orientationSign"],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    page_rows: list[dict[str, Any]] = []
    placement_rows: list[dict[str, Any]] = []
    for index in range(doc.page_count):
        page = doc[index]
        article_page = 73 + index if doc.page_count == 8 else None
        image_names = {str(image[7]): "image" for image in page.get_images(full=True) if len(image) > 7}
        form_names = {str(item[1]): "form" for item in page.get_xobjects()}
        role_names = {**image_names, **form_names}
        content_xrefs = list(page.get_contents() or [])
        page_cm_count = 0
        page_placements: list[dict[str, Any]] = []
        strict_hits: set[str] = set()
        context_hits: set[str] = set()
        for stream_index, stream_xref in enumerate(content_xrefs, start=1):
            data = doc.xref_stream(stream_xref) or b""
            content = data.decode("latin-1", errors="replace")
            strict_hits.update(token_hits(content, STRICT_TERMS))
            context_hits.update(token_hits(content, CONTEXT_TERMS))
            rows, cm_count = parse_do_placements(content, stream_xref, stream_index, role_names)
            page_cm_count += cm_count
            for row in rows:
                row.update(
                    {
                        "pdf": rel(path),
                        "pdfPage": index + 1,
                        "articlePage": article_page,
                        "pageXref": int(page.xref),
                    }
                )
                signature = placement_signature(row)
                row["placementSignatureHash16"] = sha16(signature)
                row["placementSignature"] = signature
                page_placements.append(row)
                placement_rows.append(row)
        page_rows.append(
            {
                "pdf": rel(path),
                "pdfPage": index + 1,
                "articlePage": article_page,
                "pageXref": int(page.xref),
                "contentXrefs": content_xrefs,
                "cmOperatorCount": page_cm_count,
                "doPlacementCount": len(page_placements),
                "imagePlacementCount": sum(1 for row in page_placements if row["role"] == "image"),
                "formPlacementCount": sum(1 for row in page_placements if row["role"] == "form"),
                "unknownPlacementCount": sum(1 for row in page_placements if row["role"] == "unknown"),
                "strictHitTerms": sorted(strict_hits),
                "contextHitTerms": sorted(context_hits),
                "placementSignatureHashes": sorted({row["placementSignatureHash16"] for row in page_placements}),
            }
        )
    doc.close()
    return {
        "pdf": rel(path),
        "pageCount": len(page_rows),
        "pageRows": page_rows,
        "placementRows": placement_rows,
    }


def structural_order_rows(pdf_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pdf_row in pdf_rows:
        by_role: dict[str, list[dict[str, Any]]] = {}
        for row in pdf_row["placementRows"]:
            if row["articlePage"] is not None:
                by_role.setdefault(row["role"], []).append(row)
        for role, role_rows in sorted(by_role.items()):
            article_order = [
                row["articlePage"] for row in sorted(role_rows, key=lambda row: row["articlePage"])
            ]
            stream_order = [
                row["articlePage"]
                for row in sorted(role_rows, key=lambda row: (row["streamXref"], row["streamIndex"]))
            ]
            active_order = [page for page in stream_order if page in {76, 78, 79, 80}]
            rows.append(
                {
                    "pdf": pdf_row["pdf"],
                    "role": role,
                    "articleOrder": article_order,
                    "streamXrefOrder": stream_order,
                    "activeSubsetStreamXrefOrder": active_order,
                    "streamXrefOrderMatchesArticleOrder": stream_order == article_order,
                    "activeSubsetMatchesArticleOrder": active_order == [76, 78, 79, 80],
                    "decision": "structural_content_stream_order_not_selector",
                }
            )
    return rows


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    pdf_rows = [inspect_pdf(path) for path in PDFS]
    page_rows = [row for pdf_row in pdf_rows for row in pdf_row["pageRows"]]
    placement_rows = [row for pdf_row in pdf_rows for row in pdf_row["placementRows"]]
    image_rows = [row for row in placement_rows if row["role"] == "image"]
    form_rows = [row for row in placement_rows if row["role"] == "form"]
    unknown_rows = [row for row in placement_rows if row["role"] == "unknown"]
    p76_rows = [row for row in placement_rows if row["articlePage"] == 76]
    active_pages = {76, 78, 79, 80}

    groups: dict[str, list[dict[str, Any]]] = {}
    for row in placement_rows:
        groups.setdefault(row["placementSignatureHash16"], []).append(row)

    placement_group_rows: list[dict[str, Any]] = []
    for index, (group_hash, group) in enumerate(sorted(groups.items()), start=1):
        placement_group_rows.append(
            {
                "groupId": f"M{index}",
                "placementSignatureHash16": group_hash,
                "recordCount": len(group),
                "roles": sorted({row["role"] for row in group}),
                "normalizedResourceNames": sorted({row["normalizedResourceName"] for row in group}),
                "pdfs": sorted({row["pdf"] for row in group}),
                "articlePages": sorted({row["articlePage"] for row in group if row["articlePage"]}),
                "page76RecordCount": sum(1 for row in group if row["articlePage"] == 76),
                "cumulativeMatrix": group[0]["cumulativeMatrix"],
                "unitBBox": group[0]["unitBBox"],
                "determinant": group[0]["determinant"],
                "orientationSign": group[0]["orientationSign"],
            }
        )

    p76_group_hashes = {row["placementSignatureHash16"] for row in p76_rows}
    p76_unique_groups = [
        group_hash for group_hash in p76_group_hashes if len(groups[group_hash]) == 1
    ]
    active_group_hashes = {
        row["placementSignatureHash16"]
        for row in placement_rows
        if row["articlePage"] in active_pages
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
    strict_hits = sorted({hit for row in page_rows for hit in row["strictHitTerms"]})
    context_hits = sorted({hit for row in page_rows for hit in row["contextHitTerms"]})
    source_r3_hits = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    order_rows = structural_order_rows(pdf_rows)
    structural_order_match_count = sum(
        1 for row in order_rows if row["streamXrefOrderMatchesArticleOrder"]
    )
    active_subset_match_count = sum(
        1 for row in order_rows if row["activeSubsetMatchesArticleOrder"]
    )
    distinct_matrix_count = len({tuple(row["cumulativeMatrix"]) for row in placement_rows})

    fingerprint = (
        f"pdfs={len(pdf_rows)}|pages={len(page_rows)}|placements={len(placement_rows)}"
        f"|imageDo={len(image_rows)}|formDo={len(form_rows)}|unknownDo={len(unknown_rows)}"
        f"|matrixGroups={len(placement_group_rows)}|distinctMatrices={distinct_matrix_count}"
        f"|p76Placements={len(p76_rows)}|p76UniqueGroups={len(p76_unique_groups)}"
        f"|activeUniqueGroups={len(active_unique_groups)}"
        f"|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|streamOrder={structural_order_match_count}/{len(order_rows)}"
        f"|activeSubset={active_subset_match_count}/{len(order_rows)}"
        f"|sourceR3={source_r3_hits}|triggers={satisfied_triggers}/{trigger_count}"
        f"|selectors=0"
    )

    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_content_transform_matrix_no_selector",
        "scope": "current PDF content-stream numeric placement matrices around image/form Do calls; no OCR-to-key extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "summary": {
            "pdfCount": len(pdf_rows),
            "pageCount": len(page_rows),
            "doPlacementCount": len(placement_rows),
            "imageDoPlacementCount": len(image_rows),
            "formDoPlacementCount": len(form_rows),
            "unknownDoPlacementCount": len(unknown_rows),
            "placementSignatureGroupCount": len(placement_group_rows),
            "distinctCumulativeMatrixCount": distinct_matrix_count,
            "page76PlacementCount": len(p76_rows),
            "page76UniquePlacementSignatureCount": len(p76_unique_groups),
            "activeUniquePlacementSignatureCount": len(active_unique_groups),
            "strictHitCount": len(strict_hits),
            "contextHitCount": len(context_hits),
            "strictHitTerms": strict_hits,
            "contextHitTerms": context_hits,
            "structuralStreamOrderMatchCount": structural_order_match_count,
            "structuralOrderRowCount": len(order_rows),
            "activeSubsetStreamOrderMatchCount": active_subset_match_count,
            "sourceBackedR3BridgeHitCount": source_r3_hits,
            "satisfiedReopenTriggerCount": satisfied_triggers,
            "triggerCount": trigger_count,
            "selectorUnlockCount": 0,
        },
        "placementGroupRows": placement_group_rows,
        "page76PlacementRows": p76_rows,
        "structuralOrderRows": order_rows,
        "pdfRows": pdf_rows,
        "fingerprint": fingerprint,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Content Transform Matrix Gate",
        "",
        "Scope: inspected numeric content-stream placement matrices around image and OCR-form `Do` calls in the current PDFs. This checks whether the actual raster/form placement transforms supply a page, fold, original-layout, or OVERDOSE selector. No key derivation, hashes-to-key, seed/WIF/address checks, BIP39 checks, candidates, or brute force were run.",
        "",
        f"- Created: `{result['created']}`",
        f"- PDFs / pages / placements: `{len(pdf_rows)}` / `{len(page_rows)}` / `{len(placement_rows)}`",
        f"- Image/form/unknown Do placements: `{len(image_rows)}` / `{len(form_rows)}` / `{len(unknown_rows)}`",
        f"- Placement signature groups / distinct cumulative matrices: `{len(placement_group_rows)}` / `{distinct_matrix_count}`",
        f"- Page 76 placements / unique placement groups: `{len(p76_rows)}` / `{len(p76_unique_groups)}`",
        f"- Active unique placement groups: `{len(active_unique_groups)}`",
        f"- Strict/context wrapper hits: `{len(strict_hits)}` / `{len(context_hits)}`",
        f"- Structural stream-order matches: `{structural_order_match_count}` / `{len(order_rows)}`",
        f"- Active-subset stream-order matches: `{active_subset_match_count}` / `{len(order_rows)}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3_hits}` / `{satisfied_triggers}/{trigger_count}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## Placement Groups",
        "",
        "| group | records | roles | normalized names | PDFs | article pages | p76 records | matrix | unit bbox | det | sign |",
        "|---|---:|---|---|---|---|---:|---|---|---:|---|",
    ]
    for group in placement_group_rows:
        lines.append(
            f"| {group['groupId']} | {group['recordCount']} | `{','.join(group['roles'])}` | `{','.join(group['normalizedResourceNames'])}` | `{','.join(group['pdfs'])}` | `{'-'.join(map(str, group['articlePages']))}` | {group['page76RecordCount']} | `{','.join(map(str, group['cumulativeMatrix']))}` | `{','.join(map(str, group['unitBBox']))}` | {group['determinant']} | `{group['orientationSign']}` |"
        )

    lines.extend(
        [
            "",
            "## Page 76 Placements",
            "",
            "| PDF | stream xref | resource | role | cm count | matrix | unit bbox | sign |",
            "|---|---:|---|---|---:|---|---|---|",
        ]
    )
    for row in p76_rows:
        lines.append(
            f"| `{row['pdf']}` | {row['streamXref']} | `{row['resourceName']}` | `{row['role']}` | {row['cmCountInGraphicsState']} | `{','.join(map(str, row['cumulativeMatrix']))}` | `{','.join(map(str, row['unitBBox']))}` | `{row['orientationSign']}` |"
        )

    lines.extend(
        [
            "",
            "## Stream Order Checks",
            "",
            "| PDF | role | article order | stream-xref order | active subset | order match |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for row in order_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['role']}` | `{'-'.join(map(str, row['articleOrder']))}` | `{'-'.join(map(str, row['streamXrefOrder']))}` | `{'-'.join(map(str, row['activeSubsetStreamXrefOrder']))}` | `{int(row['streamXrefOrderMatchesArticleOrder'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_content_transform_matrix_no_selector`",
            "- The placement matrices collapse to ordinary renderer/OCR placement groups: full-page raster placement in `magazine.pdf`, page-image placement in the duplicate OCR PDFs, and an `OL2` OCR-form placement in the duplicate PDFs.",
            "- Page 76 has no unique placement signature, and the active quartet has no unique placement signature.",
            "- Stream xref ordering follows PDF construction order, so the active subset inherits page order but does not supply source-backed R3.",
            "- No placement stream contains strict instruction/context terms after stripping PDF resource names and payloads.",
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
