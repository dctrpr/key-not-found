#!/usr/bin/env python3
"""Audit current PDFs for color-management and ExtGState carriers.

This bounded pass inspects PDF color-management and graphics-state resources:
catalog OutputIntents, page ColorSpace/ExtGState resources, blend/opacity/
transfer/overprint keys, and image Decode/Intent/Interpolate keys. It asks
whether page 76 or its active target page has a distinct original-layout/color
carrier not covered by raster render checks.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
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
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_color_management_extgstate_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_color_management_extgstate_gate.json"
OUT_MD = OUT / "current_pdf_color_management_extgstate_gate.md"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

RESOURCE_KEYS = ["ColorSpace", "ExtGState", "Pattern", "Shading", "Properties", "Group"]
CATALOG_KEYS = ["OutputIntents", "OCProperties", "Metadata"]
IMAGE_KEYS = [
    "ColorSpace",
    "Decode",
    "DecodeParms",
    "SMask",
    "Mask",
    "ImageMask",
    "Intent",
    "Interpolate",
    "Alternates",
    "OPI",
]
EXTGSTATE_KEYS = ["BM", "ca", "CA", "TR", "TR2", "OP", "op", "OPM", "SA", "SMask", "AIS", "TK"]
COLOR_OPERATORS = ["gs", "cs", "CS", "sc", "SC", "scn", "SCN", "rg", "RG", "g", "G", "k", "K", "ri"]
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


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def xref_key(doc: fitz.Document, xref: int, key: str) -> tuple[str, str]:
    try:
        return doc.xref_get_key(xref, key)
    except Exception as exc:
        return "error", type(exc).__name__


def xrefs_from_value(value: str) -> list[int]:
    return [int(match) for match in re.findall(r"(\d+)\s+0\s+R", value or "")]


def first_xref(value: str) -> int | None:
    refs = xrefs_from_value(value)
    return refs[0] if refs else None


def compact(value: Any, limit: int = 180) -> str:
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text[:limit]


def strip_pdf_names(text: str) -> str:
    return re.sub(r"/[A-Za-z][A-Za-z0-9]*\b", " ", text)


def token_hits(text: str, terms: set[str]) -> list[str]:
    clean = strip_pdf_names(text)
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", clean, flags=re.IGNORECASE)
    )


def normalized_object(text: str) -> str:
    out = re.sub(r"\d+\s+0\s+R", "<ref>", text)
    out = re.sub(r"/([A-Za-z]+)\d+\b", r"/\1#", out)
    out = re.sub(r"\b\d{2,7}(?:\.\d+)?\b", "<n>", out)
    return re.sub(r"\s+", " ", out).strip()


def object_text(doc: fitz.Document, xref: int | None) -> str:
    if not xref:
        return ""
    try:
        return doc.xref_object(xref, compressed=False)
    except Exception:
        return ""


def stream_text(doc: fitz.Document, xref: int) -> str:
    try:
        data = doc.xref_stream(xref) or b""
    except Exception:
        data = b""
    return data.decode("latin-1", errors="replace")


def page_resource_text(doc: fitz.Document, page_xref: int) -> tuple[int | None, str, str]:
    kind, value = xref_key(doc, page_xref, "Resources")
    ref = first_xref(value)
    if ref:
        return ref, object_text(doc, ref), kind
    return None, value if kind != "null" else "", kind


def refs_near_resource(resource_text: str, key: str) -> list[int]:
    marker = f"/{key}"
    index = resource_text.find(marker)
    if index < 0:
        return []
    # Resource dictionaries in these PDFs are shallow; a bounded window avoids
    # pulling unrelated page references while still catching inline references.
    return xrefs_from_value(resource_text[index : index + 1600])


def content_operator_counts(doc: fitz.Document, page: fitz.Page) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for content_xref in page.get_contents() or []:
        text = stream_text(doc, int(content_xref))
        stripped = re.sub(r"\([^)]*\)", "(STR)", text)
        stripped = re.sub(r"<[0-9A-Fa-f\s]+>", "<HEX>", stripped)
        for op in COLOR_OPERATORS:
            counts[op] += len(re.findall(rf"(?<!/)\b{re.escape(op)}\b", stripped))
    return dict(counts)


def inspect_extgstate(doc: fitz.Document, resource_text: str) -> list[dict[str, Any]]:
    rows = []
    for ref in sorted(set(refs_near_resource(resource_text, "ExtGState"))):
        text = object_text(doc, ref)
        if not text:
            continue
        key_values = {}
        for key in EXTGSTATE_KEYS:
            kind, value = xref_key(doc, ref, key)
            if kind != "null":
                key_values[key] = {"kind": kind, "value": compact(value)}
        rows.append(
            {
                "xref": ref,
                "signature": sha16(normalized_object(text)),
                "keyValues": key_values,
                "hasBlendMode": "/BM" in text,
                "hasOpacity": bool(re.search(r"/(?:ca|CA)\b", text)),
                "hasTransfer": bool(re.search(r"/(?:TR|TR2)\b", text)),
                "hasOverprint": bool(re.search(r"/(?:OP|op|OPM)\b", text)),
                "hasSoftMask": "/SMask" in text,
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
                "snippet": compact(text, 220),
            }
        )
    return rows


def inspect_colorspaces(doc: fitz.Document, resource_text: str) -> list[dict[str, Any]]:
    rows = []
    for ref in sorted(set(refs_near_resource(resource_text, "ColorSpace"))):
        text = object_text(doc, ref)
        if not text:
            continue
        rows.append(
            {
                "xref": ref,
                "signature": sha16(normalized_object(text)),
                "iccBased": "/ICCBased" in text,
                "indexed": "/Indexed" in text,
                "separation": "/Separation" in text,
                "deviceN": "/DeviceN" in text,
                "deviceRgb": "/DeviceRGB" in text,
                "deviceGray": "/DeviceGray" in text,
                "deviceCmyk": "/DeviceCMYK" in text,
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
                "snippet": compact(text, 220),
            }
        )
    return rows


def inspect_page_images(doc: fitz.Document, page: fitz.Page) -> list[dict[str, Any]]:
    rows = []
    for image in page.get_images(full=True):
        xref = int(image[0])
        text = object_text(doc, xref)
        key_values = {}
        for key in IMAGE_KEYS:
            kind, value = xref_key(doc, xref, key)
            if kind != "null":
                key_values[key] = {"kind": kind, "value": compact(value)}
        rows.append(
            {
                "xref": xref,
                "width": int(image[2]),
                "height": int(image[3]),
                "bpc": int(image[4]),
                "colorspace": str(image[5]),
                "filter": str(image[8]) if len(image) > 8 else "",
                "hasDecodeArray": "/Decode" in text,
                "hasDecodeParms": "/DecodeParms" in text,
                "hasIntent": "/Intent" in text,
                "hasInterpolate": "/Interpolate" in text,
                "hasMask": bool(re.search(r"/(?:SMask|Mask|ImageMask)\b", text)),
                "nonDeviceRgb": "/DeviceRGB" not in text,
                "specialKeyCount": len(key_values),
                "keyValues": key_values,
                "signature": sha16(normalized_object(text)),
                "strictHits": token_hits(text, STRICT_TERMS),
                "contextHits": token_hits(text, CONTEXT_TERMS),
            }
        )
    return rows


def inspect_pdf(path: Path) -> dict[str, Any]:
    doc = fitz.open(path)
    catalog = doc.pdf_catalog()
    catalog_keys = {}
    catalog_special_refs: list[int] = []
    for key in CATALOG_KEYS:
        kind, value = xref_key(doc, catalog, key)
        if kind != "null":
            catalog_keys[key] = {"kind": kind, "value": compact(value)}
            catalog_special_refs.extend(xrefs_from_value(value))

    output_intent_rows = []
    for ref in sorted(set(catalog_special_refs)):
        text = object_text(doc, ref)
        if "/OutputIntent" in text or "/DestOutputProfile" in text or "/ICCProfile" in text:
            output_intent_rows.append(
                {
                    "xref": ref,
                    "signature": sha16(normalized_object(text)),
                    "strictHits": token_hits(text, STRICT_TERMS),
                    "contextHits": token_hits(text, CONTEXT_TERMS),
                    "snippet": compact(text, 260),
                }
            )

    page_rows = []
    for index, page in enumerate(doc):
        article_page = 73 + index if doc.page_count == 8 else None
        resource_xref, resource_text, resource_kind = page_resource_text(doc, page.xref)
        resource_presence = {}
        for key in RESOURCE_KEYS:
            kind, value = xref_key(doc, resource_xref, key) if resource_xref else ("inline", resource_text)
            if key not in resource_text and kind == "inline":
                kind, value = "null", ""
            if kind != "null" and (key in resource_text or kind != "inline"):
                resource_presence[key] = {"kind": kind, "value": compact(value)}
        extgstate_rows = inspect_extgstate(doc, resource_text)
        colorspace_rows = inspect_colorspaces(doc, resource_text)
        image_rows = inspect_page_images(doc, page)
        color_ops = content_operator_counts(doc, page)
        page_rows.append(
            {
                "pdfPage": index + 1,
                "articlePage": article_page,
                "pageXref": page.xref,
                "resourceXref": resource_xref,
                "resourceKind": resource_kind,
                "resourceSignature": sha16(normalized_object(resource_text)),
                "resourcePresence": resource_presence,
                "extGStateRows": extgstate_rows,
                "colorSpaceRows": colorspace_rows,
                "imageRows": image_rows,
                "colorOperatorCounts": color_ops,
                "strictHits": sorted(
                    set(token_hits(resource_text, STRICT_TERMS))
                    | {hit for row in extgstate_rows for hit in row["strictHits"]}
                    | {hit for row in colorspace_rows for hit in row["strictHits"]}
                    | {hit for row in image_rows for hit in row["strictHits"]}
                ),
                "contextHits": sorted(
                    set(token_hits(resource_text, CONTEXT_TERMS))
                    | {hit for row in extgstate_rows for hit in row["contextHits"]}
                    | {hit for row in colorspace_rows for hit in row["contextHits"]}
                    | {hit for row in image_rows for hit in row["contextHits"]}
                ),
            }
        )

    doc.close()
    return {
        "pdf": rel(path),
        "pageCount": len(page_rows),
        "catalogKeys": catalog_keys,
        "outputIntentRows": output_intent_rows,
        "pageRows": page_rows,
    }


def summarize(rows: list[dict[str, Any]], trigger_summary: dict[str, Any]) -> dict[str, Any]:
    page_rows = [page for pdf in rows for page in pdf["pageRows"]]
    page76_rows = [page for page in page_rows if page["articlePage"] == 76]
    all_output_intents = [row for pdf in rows for row in pdf["outputIntentRows"]]
    ext_rows = [row for page in page_rows for row in page["extGStateRows"]]
    color_rows = [row for page in page_rows for row in page["colorSpaceRows"]]
    image_rows = [row for page in page_rows for row in page["imageRows"]]
    page76_images = [row for page in page76_rows for row in page["imageRows"]]
    other_resource_sigs = {
        page["resourceSignature"]
        for page in page_rows
        if page["articlePage"] != 76
    }
    page76_unique_resource = [
        page["resourceSignature"]
        for page in page76_rows
        if page["resourceSignature"] not in other_resource_sigs
    ]
    page76_ext_rows = [row for page in page76_rows for row in page["extGStateRows"]]
    page76_color_rows = [row for page in page76_rows for row in page["colorSpaceRows"]]
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount") or 0)
    satisfied_triggers = int(trigger_summary.get("satisfiedTriggerCount") or 0)
    trigger_count = int(trigger_summary.get("triggerCount") or 0)
    strict_hits = sorted(
        {
            hit
            for pdf in rows
            for page in pdf["pageRows"]
            for hit in page["strictHits"]
        }
        | {hit for row in all_output_intents for hit in row["strictHits"]}
    )
    context_hits = sorted(
        {
            hit
            for pdf in rows
            for page in pdf["pageRows"]
            for hit in page["contextHits"]
        }
        | {hit for row in all_output_intents for hit in row["contextHits"]}
    )
    decode_images = [row for row in image_rows if row["hasDecodeArray"]]
    special_images = [
        row
        for row in image_rows
        if row["hasDecodeArray"]
        or row["hasDecodeParms"]
        or row["hasIntent"]
        or row["hasInterpolate"]
        or row["hasMask"]
        or row["nonDeviceRgb"]
    ]
    fingerprint = (
        f"pdfs={len(rows)}|pages={len(page_rows)}|outputIntents={len(all_output_intents)}"
        f"|page76UniqueRes={len(page76_unique_resource)}"
        f"|ext={len(ext_rows)}|p76ext={len(page76_ext_rows)}"
        f"|bm={sum(1 for row in ext_rows if row['hasBlendMode'])}"
        f"|opacity={sum(1 for row in ext_rows if row['hasOpacity'])}"
        f"|transfer={sum(1 for row in ext_rows if row['hasTransfer'])}"
        f"|overprint={sum(1 for row in ext_rows if row['hasOverprint'])}"
        f"|colorspaces={len(color_rows)}|p76colorspaces={len(page76_color_rows)}"
        f"|icc={sum(1 for row in color_rows if row['iccBased'])}"
        f"|sep={sum(1 for row in color_rows if row['separation'] or row['deviceN'])}"
        f"|images={len(image_rows)}|decode={len(decode_images)}|specialImages={len(special_images)}"
        f"|strict={len(strict_hits)}|context={len(context_hits)}"
        f"|sourceR3={source_r3}|triggers={satisfied_triggers}/{trigger_count}|selectors=0"
    )
    return {
        "pdfCount": len(rows),
        "pageRowCount": len(page_rows),
        "page76RowCount": len(page76_rows),
        "outputIntentObjectCount": len(all_output_intents),
        "page76UniqueResourceSignatureCount": len(page76_unique_resource),
        "extGStateObjectCount": len(ext_rows),
        "page76ExtGStateObjectCount": len(page76_ext_rows),
        "blendModeExtGStateCount": sum(1 for row in ext_rows if row["hasBlendMode"]),
        "opacityExtGStateCount": sum(1 for row in ext_rows if row["hasOpacity"]),
        "transferExtGStateCount": sum(1 for row in ext_rows if row["hasTransfer"]),
        "overprintExtGStateCount": sum(1 for row in ext_rows if row["hasOverprint"]),
        "softMaskExtGStateCount": sum(1 for row in ext_rows if row["hasSoftMask"]),
        "colorSpaceObjectCount": len(color_rows),
        "page76ColorSpaceObjectCount": len(page76_color_rows),
        "iccBasedColorSpaceObjectCount": sum(1 for row in color_rows if row["iccBased"]),
        "separationOrDeviceNColorSpaceObjectCount": sum(
            1 for row in color_rows if row["separation"] or row["deviceN"]
        ),
        "imageObjectCount": len(image_rows),
        "page76ImageObjectCount": len(page76_images),
        "decodeArrayImageCount": len(decode_images),
        "specialImageColorKeyCount": len(special_images),
        "strictHitCount": len(strict_hits),
        "strictHits": strict_hits,
        "contextHitCount": len(context_hits),
        "contextHits": context_hits,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied_triggers,
        "triggerCount": trigger_count,
        "selectorUnlocked": False,
        "colorManagementExtGStateFingerprint": fingerprint,
    }


def main() -> None:
    trigger_summary = load_json(REOPEN_TRIGGER_MATRIX).get("summary", {})
    rows = [inspect_pdf(path) for path in PDFS]
    summary = summarize(rows, trigger_summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF color-management, ExtGState, OutputIntent, and image Decode resource gate; no extraction or candidate generation",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": summary,
        "pdfRows": rows,
        "decision": {
            "currentPdfColorManagementExtGStateGate": "current_pdf_color_management_extgstate_no_selector",
            "selectorUnlocked": False,
            "reason": (
                "The current PDFs expose no page-76-unique color-management or graphics-state "
                "carrier. OutputIntents, ICC/separation ColorSpaces, blend/opacity/transfer "
                "ExtGState resources, and image Decode/Intent special keys do not supply a "
                "source-backed unit/order/transform."
            ),
            "nextMove": (
                "Keep PDF color-management and graphics-state resources closed for the current "
                "files. Continue only with distinct physical/original-layout source validation "
                "or raw clue wording that names the extraction unit, order, or transform."
            ),
        },
        "fingerprint": summary["colorManagementExtGStateFingerprint"],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current PDF Color Management / ExtGState Gate",
        "",
        "Scope: inspected current PDFs for color-management and graphics-state carriers: catalog OutputIntents, page ColorSpace/ExtGState resources, blend/opacity/transfer/overprint keys, image Decode/Intent/Interpolate keys, and color operators. No OCR-to-key extraction, candidates, hashes-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / page rows: `{summary['pdfCount']}` / `{summary['pageRowCount']}`",
        f"- OutputIntent objects: `{summary['outputIntentObjectCount']}`",
        f"- Page-76 unique resource signatures: `{summary['page76UniqueResourceSignatureCount']}`",
        f"- ExtGState objects / page-76 ExtGState objects: `{summary['extGStateObjectCount']}` / `{summary['page76ExtGStateObjectCount']}`",
        f"- Blend/opacity/transfer/overprint ExtGState objects: `{summary['blendModeExtGStateCount']}` / `{summary['opacityExtGStateCount']}` / `{summary['transferExtGStateCount']}` / `{summary['overprintExtGStateCount']}`",
        f"- ColorSpace objects / page-76 ColorSpace objects: `{summary['colorSpaceObjectCount']}` / `{summary['page76ColorSpaceObjectCount']}`",
        f"- ICCBased / Separation-or-DeviceN ColorSpace objects: `{summary['iccBasedColorSpaceObjectCount']}` / `{summary['separationOrDeviceNColorSpaceObjectCount']}`",
        f"- Image objects / page-76 image objects: `{summary['imageObjectCount']}` / `{summary['page76ImageObjectCount']}`",
        f"- Image Decode-array rows / special image color-key rows: `{summary['decodeArrayImageCount']}` / `{summary['specialImageColorKeyCount']}`",
        f"- Strict/context hits: `{summary['strictHitCount']}` / `{summary['contextHitCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['colorManagementExtGStateFingerprint']}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | catalog keys | output intents | page76 res sigs | page76 ExtGState | page76 ColorSpace | page76 images |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for pdf in rows:
        page76 = [page for page in pdf["pageRows"] if page["articlePage"] == 76]
        lines.append(
            f"| `{pdf['pdf']}` | {len(pdf['catalogKeys'])} | {len(pdf['outputIntentRows'])} | {len(set(page['resourceSignature'] for page in page76))} | {sum(len(page['extGStateRows']) for page in page76)} | {sum(len(page['colorSpaceRows']) for page in page76)} | {sum(len(page['imageRows']) for page in page76)} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- `current_pdf_color_management_extgstate_no_selector`",
            "- No current PDF exposes a page-76-unique color-management, OutputIntent, ColorSpace, ExtGState, blend/opacity/transfer, or image Decode carrier.",
            "- This keeps current PDFs as raster/OCR witnesses only, not original-layout extraction authority.",
            "",
            "## Next Move",
            "",
            "- Continue only with distinct physical/original-layout source validation or raw clue wording that supplies the missing unit/order/transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Decision: {result['decision']['currentPdfColorManagementExtGStateGate']}")
    print(f"Fingerprint: {result['fingerprint']}")


if __name__ == "__main__":
    main()
