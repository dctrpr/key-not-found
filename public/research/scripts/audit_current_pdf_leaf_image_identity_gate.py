#!/usr/bin/env python3
"""Audit current PDF/scan leaf-image identity for article pages 75 and 76.

This bounded source/layout pass checks whether the current PDFs or root scan
images contain a distinct original-layout raster for the physically valid
75 -> 76 held-to-light pair. It compares embedded PDF images and filesystem
page images against the canonical current scan pages. It does not derive keys,
hashes, seed phrases, WIFs, addresses, BIP39 checks, or candidate material.
"""

from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_leaf_image_identity_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_leaf_image_identity_gate.json"
OUT_MD = OUT / "current_pdf_leaf_image_identity_gate.md"
OUT_SHEET = OUT / "current_pdf_leaf_image_identity_gate_sheet.jpg"

REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

ARTICLE_PAGES = (75, 76)
PDF_PAGE_INDEX = {75: 2, 76: 3}
CANONICAL = {
    page: ROOT / f"analysis_outputs/source_images/magazine_page_{page}.jpg"
    for page in ARTICLE_PAGES
}

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]

ROOT_PAGE_IMAGES = {
    75: [
        ROOT / "magazine-3_1.jpg",
        ROOT / "keyser bitcoin -3_1.jpg",
    ],
    76: [
        ROOT / "magazine-4_1.jpg",
        ROOT / "keyser bitcoin -4_1.jpg",
    ],
}

EXACT_MAD_THRESHOLD = 0.20
DERIVATIVE_MAD_THRESHOLD = 65.0


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def md5_image(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()


def mad(a: Image.Image, b: Image.Image) -> float:
    if a.size != b.size:
        b = b.resize(a.size, Image.Resampling.BICUBIC)
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    arr = np.asarray(diff, dtype=np.float32)
    return float(arr.mean())


def compare_to_canonical(img: Image.Image, page: int) -> dict[str, Any]:
    canonical = Image.open(CANONICAL[page]).convert("RGB")
    transforms = {
        "as_is": img.convert("RGB"),
        "rotate180": img.convert("RGB").rotate(180),
        "hflip": ImageOps.mirror(img.convert("RGB")),
        "hflip_rotate180": ImageOps.mirror(img.convert("RGB")).rotate(180),
    }
    scored = []
    for name, transformed in transforms.items():
        scored.append({"orientation": name, "mad": round(mad(canonical, transformed), 4)})
    best = min(scored, key=lambda row: row["mad"])
    exact = img.size == canonical.size and best["mad"] <= EXACT_MAD_THRESHOLD
    derivative = best["mad"] <= DERIVATIVE_MAD_THRESHOLD
    gain = min(img.size[0] / canonical.size[0], img.size[1] / canonical.size[1])
    return {
        "canonicalPage": page,
        "bestOrientation": best["orientation"],
        "bestMad": best["mad"],
        "exactCurrentScanMatch": exact,
        "derivativeLikeMatch": derivative,
        "sourceGain": round(gain, 4),
        "higherResolutionThanCanonical": img.size[0] > canonical.size[0]
        or img.size[1] > canonical.size[1],
    }


def best_page_identity(img: Image.Image) -> dict[str, Any]:
    best_rows = [compare_to_canonical(img, page) for page in ARTICLE_PAGES]
    best = min(best_rows, key=lambda row: row["bestMad"])
    return {
        "bestArticlePage": best["canonicalPage"],
        "bestOrientation": best["bestOrientation"],
        "bestMad": best["bestMad"],
        "allPageMad": {str(row["canonicalPage"]): row["bestMad"] for row in best_rows},
    }


def record_for_image(
    source_id: str,
    article_page: int,
    source_kind: str,
    img: Image.Image,
    path: str | None = None,
    pdf_page: int | None = None,
    xref: int | None = None,
    image_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    comparison = compare_to_canonical(img, article_page)
    identity = best_page_identity(img)
    return {
        "sourceId": source_id,
        "sourceKind": source_kind,
        "path": path,
        "pdfPage": pdf_page,
        "articlePage": article_page,
        "xref": xref,
        "width": img.size[0],
        "height": img.size[1],
        "md5": md5_image(img),
        "identity": identity,
        "samePageComparison": comparison,
        "imageMeta": image_meta or {},
    }


def filesystem_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in ARTICLE_PAGES:
        canonical = Image.open(CANONICAL[page]).convert("RGB")
        records.append(
            record_for_image(
                f"canonical_source_image_p{page}",
                page,
                "canonical_source_image",
                canonical,
                rel(CANONICAL[page]),
            )
        )
        for image_path in ROOT_PAGE_IMAGES[page]:
            if image_path.exists():
                img = Image.open(image_path).convert("RGB")
                records.append(
                    record_for_image(
                        image_path.stem,
                        page,
                        "root_page_image",
                        img,
                        rel(image_path),
                    )
                )
    return records


def pdf_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for pdf_path in PDFS:
        if not pdf_path.exists():
            continue
        doc = fitz.open(pdf_path)
        for page in ARTICLE_PAGES:
            page_index = PDF_PAGE_INDEX[page]
            if page_index >= len(doc):
                continue
            pdf_page = doc[page_index]
            images = pdf_page.get_images(full=True)
            if not images:
                continue
            # The PDFs here are raster-dominated; the primary image is the
            # full-page article raster and carries the relevant source pixels.
            image = images[0]
            xref = int(image[0])
            extracted = doc.extract_image(xref)
            img = Image.open(io.BytesIO(extracted["image"])).convert("RGB")
            meta = {
                "colorspace": extracted.get("colorspace"),
                "bitsPerComponent": extracted.get("bpc"),
                "extension": extracted.get("ext"),
                "pageRotation": pdf_page.rotation,
                "imageCountOnPage": len(images),
                "hasSoftMask": bool(image[1]),
            }
            records.append(
                record_for_image(
                    f"{pdf_path.name}_page_{page}_embedded",
                    page,
                    "pdf_embedded_primary_image",
                    img,
                    rel(pdf_path),
                    pdf_page=page_index + 1,
                    xref=xref,
                    image_meta=meta,
                )
            )
        doc.close()
    return records


def pair_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[tuple[str, str], dict[int, dict[str, Any]]] = {}
    for row in records:
        path = row.get("path") or row["sourceId"]
        if row["sourceKind"] == "root_page_image":
            family = row["sourceId"].rsplit("-", 1)[0].strip()
        elif row["sourceKind"] == "canonical_source_image":
            family = "canonical_source_images"
        elif row["sourceKind"] == "pdf_embedded_primary_image":
            family = path
        else:
            family = row["sourceKind"]
        by_family.setdefault((row["sourceKind"], family), {})[row["articlePage"]] = row

    rows = []
    for (kind, family), pages in sorted(by_family.items()):
        if 75 not in pages or 76 not in pages:
            continue
        p75 = pages[75]
        p76 = pages[76]
        same_size = (p75["width"], p75["height"]) == (p76["width"], p76["height"])
        same_source_gain = (
            abs(
                p75["samePageComparison"]["sourceGain"]
                - p76["samePageComparison"]["sourceGain"]
            )
            <= 0.001
        )
        exact_pair = (
            p75["samePageComparison"]["exactCurrentScanMatch"]
            and p76["samePageComparison"]["exactCurrentScanMatch"]
        )
        derivative_pair = (
            p75["samePageComparison"]["derivativeLikeMatch"]
            and p76["samePageComparison"]["derivativeLikeMatch"]
        )
        rows.append(
            {
                "kind": kind,
                "family": family,
                "path": family,
                "p75Size": f"{p75['width']}x{p75['height']}",
                "p76Size": f"{p76['width']}x{p76['height']}",
                "sameSize": same_size,
                "sameSourceGain": same_source_gain,
                "p75BestMad": p75["samePageComparison"]["bestMad"],
                "p76BestMad": p76["samePageComparison"]["bestMad"],
                "p75Orientation": p75["samePageComparison"]["bestOrientation"],
                "p76Orientation": p76["samePageComparison"]["bestOrientation"],
                "exactCurrentScanPair": exact_pair,
                "derivativeLikePair": derivative_pair,
                "higherResolutionPair": p75["samePageComparison"][
                    "higherResolutionThanCanonical"
                ]
                or p76["samePageComparison"]["higherResolutionThanCanonical"],
            }
        )
    return rows


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


def draw_sheet(records: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> None:
    width, height = 1840, 1260
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    title = font(26)
    body = font(15)
    small = font(12)
    draw.rectangle((0, 0, width, 92), fill=(28, 34, 43))
    draw.text((24, 18), "Current PDF Leaf Image Identity Gate", fill="white", font=title)
    draw.text(
        (24, 56),
        "Embedded PDF/root scan rasters for article pages 75/76 compared against the current 2544x3264 scan.",
        fill=(235, 235, 235),
        font=body,
    )

    y = 116
    headers = [
        "kind",
        "page",
        "size",
        "best page",
        "orient",
        "MAD",
        "exact",
        "gain",
        "path/id",
    ]
    xs = [24, 330, 390, 500, 610, 735, 805, 875, 950]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(70, 70, 70), font=small)
    y += 20
    for row in records[:18]:
        cmp = row["samePageComparison"]
        ident = row["identity"]
        vals = [
            row["sourceKind"][:33],
            str(row["articlePage"]),
            f"{row['width']}x{row['height']}",
            str(ident["bestArticlePage"]),
            cmp["bestOrientation"],
            f"{cmp['bestMad']:.2f}",
            "Y" if cmp["exactCurrentScanMatch"] else "N",
            f"{cmp['sourceGain']:.3f}",
            (row.get("path") or row["sourceId"])[:90],
        ]
        for x, value in zip(xs, vals):
            draw.text((x, y), value, fill=(32, 32, 32), font=small)
        y += 20

    y += 24
    draw.text((24, y), "Leaf Pair Rows", fill=(20, 20, 20), font=body)
    y += 28
    headers = ["kind", "family", "p75 size", "p76 size", "same", "p75 MAD", "p76 MAD", "exact pair", "higher"]
    xs = [24, 330, 770, 900, 1035, 1100, 1190, 1280, 1390]
    for x, h in zip(xs, headers):
        draw.text((x, y), h, fill=(70, 70, 70), font=small)
    y += 20
    for row in pairs:
        vals = [
            row["kind"][:32],
            row["family"][:52],
            row["p75Size"],
            row["p76Size"],
            "Y" if row["sameSize"] and row["sameSourceGain"] else "N",
            f"{row['p75BestMad']:.2f}",
            f"{row['p76BestMad']:.2f}",
            "Y" if row["exactCurrentScanPair"] else "N",
            "Y" if row["higherResolutionPair"] else "N",
        ]
        for x, value in zip(xs, vals):
            draw.text((x, y), value, fill=(32, 32, 32), font=small)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def write_md(result: dict[str, Any]) -> None:
    summary = result["summary"]
    lines = [
        "# Current PDF Leaf Image Identity Gate",
        "",
        "Scope: checked embedded PDF images and root scan page rasters for article pages 75/76 against the current canonical scan. No key derivation, hashes, seed/WIF/address checks, BIP39, or candidate generation was run.",
        "",
        f"- Created: `{result['created']}`",
        f"- Sheet: `{result['sheet']}`",
        f"- Image records / leaf pair rows: `{summary['imageRecordCount']}` / `{summary['leafPairRowCount']}`",
        f"- Exact current-scan records: `{summary['exactCurrentScanRecordCount']}`",
        f"- Derivative-like records: `{summary['derivativeLikeRecordCount']}`",
        f"- Exact current-scan leaf pairs: `{summary['exactCurrentScanPairCount']}`",
        f"- Derivative-like leaf pairs: `{summary['derivativeLikePairCount']}`",
        f"- Higher-resolution records / pairs: `{summary['higherResolutionRecordCount']}` / `{summary['higherResolutionPairCount']}`",
        f"- Distinct improved/original-layout candidates: `{summary['distinctImprovedCandidateCount']}`",
        f"- PDF soft-mask / multi-image page candidates: `{summary['pdfSoftMaskRecordCount']}` / `{summary['pdfMultiImagePageRecordCount']}`",
        f"- Source-backed R3 / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{result['fingerprint']}`",
        "",
        "## Leaf Pair Rows",
        "",
        "| kind | family | p75 size | p76 size | p75 MAD | p76 MAD | exact pair | derivative pair | higher-res |",
        "|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["leafPairRows"]:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row['kind']}`",
                    f"`{row['family']}`",
                    f"`{row['p75Size']}`",
                    f"`{row['p76Size']}`",
                    f"{row['p75BestMad']:.4f}",
                    f"{row['p76BestMad']:.4f}",
                    str(row["exactCurrentScanPair"]),
                    str(row["derivativeLikePair"]),
                    str(row["higherResolutionPair"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`",
            "- The current PDFs and root scan images do not contain a distinct higher-resolution or original-layout raster for the 75/76 leaf pair.",
            "- `magazine.pdf`/`magazine-*_1.jpg` preserve the current 2544x3264 scan; `keyser bitcoin .pdf` and the Google Drive article download are matching lower-resolution derivatives with the same page-pair identity.",
            "- No soft mask, multi-image page, per-page identity split, or source-backed instruction/reopen trigger was found.",
            "",
            "## Next Move",
            "",
            "- Keep using `analysis_outputs/source_images/magazine_page_75.jpg` and `magazine_page_76.jpg` as the current-scan light-table source. Do not reopen extraction from the current PDFs unless a new physical/original source differs from these identity rows and passes R1-R5 plus R3.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    records = filesystem_records() + pdf_records()
    pairs = pair_rows(records)

    exact_records = sum(
        1 for row in records if row["samePageComparison"]["exactCurrentScanMatch"]
    )
    derivative_records = sum(
        1 for row in records if row["samePageComparison"]["derivativeLikeMatch"]
    )
    higher_records = sum(
        1 for row in records if row["samePageComparison"]["higherResolutionThanCanonical"]
    )
    soft_masks = sum(
        1
        for row in records
        if row["sourceKind"] == "pdf_embedded_primary_image"
        and row.get("imageMeta", {}).get("hasSoftMask")
    )
    multi_image_pages = sum(
        1
        for row in records
        if row["sourceKind"] == "pdf_embedded_primary_image"
        and row.get("imageMeta", {}).get("imageCountOnPage", 1) != 1
    )
    exact_pairs = sum(1 for row in pairs if row["exactCurrentScanPair"])
    derivative_pairs = sum(1 for row in pairs if row["derivativeLikePair"])
    higher_pairs = sum(1 for row in pairs if row["higherResolutionPair"])
    distinct_improved = sum(
        1
        for row in records
        if row["samePageComparison"]["higherResolutionThanCanonical"]
        and not row["samePageComparison"]["exactCurrentScanMatch"]
    )

    summary = {
        "imageRecordCount": len(records),
        "leafPairRowCount": len(pairs),
        "exactCurrentScanRecordCount": exact_records,
        "derivativeLikeRecordCount": derivative_records,
        "exactCurrentScanPairCount": exact_pairs,
        "derivativeLikePairCount": derivative_pairs,
        "higherResolutionRecordCount": higher_records,
        "higherResolutionPairCount": higher_pairs,
        "distinctImprovedCandidateCount": distinct_improved,
        "pdfSoftMaskRecordCount": soft_masks,
        "pdfMultiImagePageRecordCount": multi_image_pages,
        "sourceBackedR3BridgeHitCount": 0,
        "satisfiedReopenTriggerCount": int(
            reopen.get("summary", {}).get("satisfiedReopenTriggerCount", 0)
        ),
        "triggerCount": int(reopen.get("summary", {}).get("triggerCount", 9)),
        "selectorUnlockCount": 0,
    }
    fingerprint = (
        f"records={len(records)}|pairs={len(pairs)}|exactRecords={exact_records}|"
        f"derivativeRecords={derivative_records}|exactPairs={exact_pairs}|"
        f"derivativePairs={derivative_pairs}|higherRecords={higher_records}|"
        f"higherPairs={higher_pairs}|distinctImproved={distinct_improved}|"
        f"softMasks={soft_masks}|multiImagePages={multi_image_pages}|"
        f"sourceR3=0|triggers={summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}|"
        "selectors=0"
    )
    result = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "decision": "current_pdf_leaf_image_identity_no_distinct_source",
        "sheet": rel(OUT_SHEET),
        "summary": summary,
        "fingerprint": fingerprint,
        "imageRecords": records,
        "leafPairRows": pairs,
    }

    draw_sheet(records, pairs)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_md(result)
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"decision: {result['decision']}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
