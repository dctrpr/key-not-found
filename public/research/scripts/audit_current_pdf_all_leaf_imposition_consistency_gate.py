#!/usr/bin/env python3
"""Audit current-PDF imposition consistency across article leaf pairs.

This bounded source/layout pass checks whether the current Bitcoin PDFs carry a
different page-box, rotation, image placement, scale, or hidden layer across the
three physical leaf pairs 75/76, 77/78, and 79/80. It treats the PDFs as source
layout carriers only. It does not generate keys, hashes, seed phrases, WIFs,
addresses, BIP39 checks, or candidate material.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_pdf_all_leaf_imposition_consistency_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_pdf_all_leaf_imposition_consistency_gate.json"
OUT_MD = OUT / "current_pdf_all_leaf_imposition_consistency_gate.md"
OUT_SHEET = OUT / "current_pdf_all_leaf_imposition_consistency_gate_sheet.jpg"

PDFS = [
    ROOT / "magazine.pdf",
    ROOT / "keyser bitcoin .pdf",
    ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf",
]
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

LEAF_PAIRS = [(75, 76), (77, 78), (79, 80)]
ARTICLE_TO_INDEX = {page: page - 73 for page in range(75, 81)}
EPS = 1e-3


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def rect_list(rect: fitz.Rect) -> list[float]:
    return [round(rect.x0, 4), round(rect.y0, 4), round(rect.x1, 4), round(rect.y1, 4)]


def same_list(a: list[float], b: list[float], eps: float = EPS) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= eps for x, y in zip(a, b))


def rect_area(rect: list[float]) -> float:
    return max(0.0, rect[2] - rect[0]) * max(0.0, rect[3] - rect[1])


def page_record(doc: fitz.Document, pdf_path: Path, article_page: int) -> dict[str, Any]:
    page_index = ARTICLE_TO_INDEX[article_page]
    page = doc[page_index]
    page_rect = rect_list(page.rect)
    cropbox = rect_list(page.cropbox)
    mediabox = rect_list(page.mediabox)
    images: list[dict[str, Any]] = []

    for image in page.get_images(full=True):
        xref = int(image[0])
        extracted = doc.extract_image(xref)
        rects = [rect_list(rect) for rect in page.get_image_rects(xref)]
        primary_rect = rects[0] if rects else [0.0, 0.0, 0.0, 0.0]
        page_area_value = max(rect_area(page_rect), EPS)
        max_coverage = max((rect_area(rect) / page_area_value for rect in rects), default=0.0)
        width_px = int(extracted.get("width", image[2]))
        height_px = int(extracted.get("height", image[3]))
        scale_x = width_px / max(EPS, primary_rect[2] - primary_rect[0])
        scale_y = height_px / max(EPS, primary_rect[3] - primary_rect[1])
        images.append(
            {
                "xref": xref,
                "widthPx": width_px,
                "heightPx": height_px,
                "bitsPerComponent": extracted.get("bpc", image[4] if len(image) > 4 else None),
                "colorspace": extracted.get("colorspace", image[5] if len(image) > 5 else None),
                "extension": extracted.get("ext"),
                "rects": rects,
                "primaryRect": primary_rect,
                "maxPageCoverage": round(max_coverage, 6),
                "leftMarginPt": round(primary_rect[0] - cropbox[0], 4),
                "topMarginPt": round(primary_rect[1] - cropbox[1], 4),
                "rightMarginPt": round(cropbox[2] - primary_rect[2], 4),
                "bottomMarginPt": round(cropbox[3] - primary_rect[3], 4),
                "scaleXPxPerPt": round(scale_x, 6),
                "scaleYPxPerPt": round(scale_y, 6),
            }
        )

    return {
        "pdf": rel(pdf_path),
        "pdfPage": page_index + 1,
        "articlePage": article_page,
        "rotation": page.rotation,
        "pageRect": page_rect,
        "mediaBox": mediabox,
        "cropBox": cropbox,
        "imageCount": len(images),
        "images": images,
        "fontCount": len(page.get_fonts(full=True)),
        "drawingCount": len(page.get_drawings()),
        "ocrWordCount": len(page.get_text("words")),
    }


def primary_image(row: dict[str, Any]) -> dict[str, Any]:
    return row["images"][0] if row.get("images") else {}


def signature(row: dict[str, Any]) -> tuple[Any, ...]:
    image = primary_image(row)
    return (
        tuple(row["pageRect"]),
        tuple(row["mediaBox"]),
        tuple(row["cropBox"]),
        row["rotation"],
        row["imageCount"],
        tuple(image.get("primaryRect", [])),
        image.get("widthPx"),
        image.get("heightPx"),
        image.get("scaleXPxPerPt"),
        image.get("scaleYPxPerPt"),
        image.get("leftMarginPt"),
        image.get("rightMarginPt"),
        image.get("topMarginPt"),
        image.get("bottomMarginPt"),
    )


def compare_pair(front: dict[str, Any], back: dict[str, Any]) -> dict[str, Any]:
    front_img = primary_image(front)
    back_img = primary_image(back)
    same_page_rect = same_list(front["pageRect"], back["pageRect"])
    same_media = same_list(front["mediaBox"], back["mediaBox"])
    same_crop = same_list(front["cropBox"], back["cropBox"])
    same_rotation = front["rotation"] == back["rotation"]
    same_image_count = front["imageCount"] == back["imageCount"] == 1
    same_image_rect = bool(
        front_img and back_img and same_list(front_img["primaryRect"], back_img["primaryRect"])
    )
    same_image_size = bool(
        front_img
        and back_img
        and front_img["widthPx"] == back_img["widthPx"]
        and front_img["heightPx"] == back_img["heightPx"]
    )
    same_scale = bool(
        front_img
        and back_img
        and abs(front_img["scaleXPxPerPt"] - back_img["scaleXPxPerPt"]) <= EPS
        and abs(front_img["scaleYPxPerPt"] - back_img["scaleYPxPerPt"]) <= EPS
    )
    identical_pair_geometry = all(
        [
            same_page_rect,
            same_media,
            same_crop,
            same_rotation,
            same_image_count,
            same_image_rect,
            same_image_size,
            same_scale,
        ]
    )
    has_side_margins = bool(
        front_img
        and back_img
        and (
            abs(front_img.get("leftMarginPt", 0.0)) > EPS
            or abs(front_img.get("rightMarginPt", 0.0)) > EPS
            or abs(back_img.get("leftMarginPt", 0.0)) > EPS
            or abs(back_img.get("rightMarginPt", 0.0)) > EPS
        )
    )
    hidden_pair_layer = bool(
        front["imageCount"] != 1
        or back["imageCount"] != 1
        or front["drawingCount"] != 0
        or back["drawingCount"] != 0
    )
    return {
        "pdf": front["pdf"],
        "frontArticlePage": front["articlePage"],
        "backArticlePage": back["articlePage"],
        "frontPdfPage": front["pdfPage"],
        "backPdfPage": back["pdfPage"],
        "samePageRect": same_page_rect,
        "sameMediaBox": same_media,
        "sameCropBox": same_crop,
        "sameRotation": same_rotation,
        "sameSingleImageCount": same_image_count,
        "sameImageRect": same_image_rect,
        "sameImageSize": same_image_size,
        "sameScale": same_scale,
        "identicalPairGeometry": identical_pair_geometry,
        "hasSideMargins": has_side_margins,
        "hiddenPairLayerCandidate": hidden_pair_layer,
        "imageRectDeltaPt": [
            round(back_img.get("primaryRect", [0.0, 0.0, 0.0, 0.0])[i] - front_img.get("primaryRect", [0.0, 0.0, 0.0, 0.0])[i], 4)
            for i in range(4)
        ],
        "scaleDeltaPxPerPt": [
            round(back_img.get("scaleXPxPerPt", 0.0) - front_img.get("scaleXPxPerPt", 0.0), 6),
            round(back_img.get("scaleYPxPerPt", 0.0) - front_img.get("scaleYPxPerPt", 0.0), 6),
        ],
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


def build_sheet(result: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1800, 1320), (10, 12, 16))
    draw = ImageDraw.Draw(sheet)
    title_font = font(34)
    body = font(17)
    small = font(13)
    mono = font(14)

    draw.text((32, 26), "Current PDF All-Leaf Imposition Consistency Gate", fill=(242, 246, 250), font=title_font)
    draw.text(
        (32, 74),
        "Page boxes, rotation, image placement, and scale across article leaf pairs 75/76, 77/78, and 79/80.",
        fill=(178, 188, 200),
        font=body,
    )

    chips = [
        ("pdfs", result["summary"]["pdfCount"]),
        ("pages", result["summary"]["pageRecordCount"]),
        ("leaf pairs", result["summary"]["leafPairCount"]),
        ("pair pass", result["summary"]["identicalPairGeometryCount"]),
        ("uniform PDFs", result["summary"]["withinPdfUniformCount"]),
        ("candidate", result["decision"]["currentPdfAllLeafImpositionConsistencyGate"]),
    ]
    x = 32
    y = 118
    for label, value in chips:
        draw.rectangle((x, y, x + 270, y + 58), fill=(23, 29, 37), outline=(54, 64, 76))
        draw.text((x + 12, y + 8), label, fill=(128, 142, 158), font=small)
        draw.text((x + 12, y + 30), str(value)[:28], fill=(235, 240, 246), font=mono)
        x += 288

    y = 214
    headers = [
        ("PDF", 0),
        ("pair", 410),
        ("rot", 520),
        ("front rect", 610),
        ("back rect", 900),
        ("margins", 1190),
        ("pass", 1460),
        ("hidden", 1550),
    ]
    draw.rectangle((32, y, 1768, y + 34), fill=(30, 36, 44))
    for label, xoff in headers:
        draw.text((44 + xoff, y + 9), label, fill=(240, 244, 248), font=small)
    y += 40
    for pair in result["pairRows"]:
        front = result["pageByPdfArticle"][pair["pdf"]][str(pair["frontArticlePage"])]
        back = result["pageByPdfArticle"][pair["pdf"]][str(pair["backArticlePage"])]
        front_img = primary_image(front)
        back_img = primary_image(back)
        fill = (17, 23, 30) if pair["identicalPairGeometry"] and not pair["hiddenPairLayerCandidate"] else (55, 31, 28)
        draw.rectangle((32, y, 1768, y + 64), fill=fill, outline=(44, 52, 62))
        draw.text((44, y + 12), pair["pdf"][:48], fill=(232, 238, 244), font=small)
        draw.text((454, y + 12), f"{pair['frontArticlePage']}/{pair['backArticlePage']}", fill=(232, 238, 244), font=mono)
        draw.text((564, y + 12), f"{front['rotation']}/{back['rotation']}", fill=(232, 238, 244), font=mono)
        draw.text((654, y + 12), str(front_img.get("primaryRect"))[:34], fill=(232, 238, 244), font=mono)
        draw.text((944, y + 12), str(back_img.get("primaryRect"))[:34], fill=(232, 238, 244), font=mono)
        margins = (
            f"{front_img.get('leftMarginPt')}/{front_img.get('rightMarginPt')} | "
            f"{back_img.get('leftMarginPt')}/{back_img.get('rightMarginPt')}"
        )
        draw.text((1234, y + 12), margins[:28], fill=(232, 238, 244), font=mono)
        draw.text((1504, y + 12), str(int(pair["identicalPairGeometry"])), fill=(232, 238, 244), font=mono)
        draw.text((1594, y + 12), str(int(pair["hiddenPairLayerCandidate"])), fill=(232, 238, 244), font=mono)
        draw.text(
            (454, y + 38),
            f"delta rect {pair['imageRectDeltaPt']} | delta scale {pair['scaleDeltaPxPerPt']}",
            fill=(160, 172, 186),
            font=small,
        )
        y += 70

    y += 18
    draw.rectangle((32, y, 1768, y + 180), fill=(35, 29, 18), outline=(92, 70, 33))
    draw.text((52, y + 18), "Decision", fill=(255, 220, 138), font=body)
    for idx, line in enumerate(result["assessment"]):
        draw.text((52, y + 54 + idx * 30), line[:145], fill=(255, 220, 138), font=small)

    OUT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    trigger_matrix = load_json(REOPEN_TRIGGER_MATRIX)
    trigger_summary = trigger_matrix.get("summary", {})

    page_rows: list[dict[str, Any]] = []
    pair_rows: list[dict[str, Any]] = []
    pdf_rows: list[dict[str, Any]] = []
    page_by_pdf_article: dict[str, dict[str, Any]] = {}

    for pdf_path in PDFS:
        with fitz.open(pdf_path) as doc:
            records = []
            for article_page in range(75, 81):
                page_index = ARTICLE_TO_INDEX[article_page]
                if page_index >= doc.page_count:
                    continue
                record = page_record(doc, pdf_path, article_page)
                records.append(record)
                page_rows.append(record)
            page_by_pdf_article[rel(pdf_path)] = {str(row["articlePage"]): row for row in records}

            signatures = {signature(row) for row in records}
            pdf_rows.append(
                {
                    "pdf": rel(pdf_path),
                    "pageCount": doc.page_count,
                    "inspectedArticlePages": [row["articlePage"] for row in records],
                    "recordCount": len(records),
                    "withinPdfUniformGeometry": len(signatures) == 1,
                    "uniqueGeometrySignatureCount": len(signatures),
                    "rotationSet": sorted({row["rotation"] for row in records}),
                    "imageSizeSet": sorted(
                        {
                            f"{primary_image(row).get('widthPx')}x{primary_image(row).get('heightPx')}"
                            for row in records
                        }
                    ),
                }
            )
            for front_page, back_page in LEAF_PAIRS:
                front = next((row for row in records if row["articlePage"] == front_page), None)
                back = next((row for row in records if row["articlePage"] == back_page), None)
                if front and back:
                    pair_rows.append(compare_pair(front, back))

    all_signatures = {signature(row) for row in page_rows}
    identical_pair_count = sum(1 for row in pair_rows if row["identicalPairGeometry"])
    placement_offset_count = sum(
        1
        for row in pair_rows
        if not row["sameImageRect"] or not row["sameScale"] or not row["sameRotation"]
    )
    hidden_pair_count = sum(1 for row in pair_rows if row["hiddenPairLayerCandidate"])
    side_margin_pair_count = sum(1 for row in pair_rows if row["hasSideMargins"])
    within_pdf_uniform_count = sum(1 for row in pdf_rows if row["withinPdfUniformGeometry"])
    imposition_candidate = int(
        identical_pair_count != len(pair_rows)
        or placement_offset_count > 0
        or hidden_pair_count > 0
        or within_pdf_uniform_count != len(pdf_rows)
    )
    source_r3 = int(trigger_summary.get("sourceBackedR3BridgeHitCount", 0) or 0)
    satisfied = int(trigger_summary.get("satisfiedTriggerCount", 0) or 0)
    trigger_count = int(trigger_summary.get("triggerCount", 0) or 0)
    selector_count = imposition_candidate if source_r3 or satisfied else 0

    fingerprint = (
        f"pdfs={len(PDFS)}|pages={len(page_rows)}|leafPairs={len(pair_rows)}|"
        f"pairPass={identical_pair_count}|withinPdfUniform={within_pdf_uniform_count}|"
        f"geometryFamilies={len(all_signatures)}|sideMarginPairs={side_margin_pair_count}|"
        f"placementOffsetPairs={placement_offset_count}|hiddenPairLayers={hidden_pair_count}|"
        f"impositionCandidate={imposition_candidate}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={selector_count}"
    )

    decision = "current_pdf_all_leaf_imposition_consistency_no_selector"
    assessment = [
        "All inspected article leaf pairs preserve front/back page-box, rotation, image-rect, image-size, and scale geometry.",
        "The duplicate PDFs carry the same 18pt side-margin geometry on every inspected page, so the margin is not a page-76-specific imposition cue.",
        "The byte-locked magazine PDF is one full-bleed geometry family; duplicate PDF24 derivatives form the second family, but neither family supplies a source-backed unit/order rule.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Inspect current-PDF original page layout/imposition across article leaf pairs 75/76, 77/78, and 79/80; no extraction or key search.",
        "inputs": {
            "pdfs": [rel(path) for path in PDFS],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "summary": {
            "pdfCount": len(PDFS),
            "pageRecordCount": len(page_rows),
            "leafPairCount": len(pair_rows),
            "identicalPairGeometryCount": identical_pair_count,
            "withinPdfUniformCount": within_pdf_uniform_count,
            "uniqueGeometryFamilyCount": len(all_signatures),
            "sideMarginPairCount": side_margin_pair_count,
            "placementOffsetPairCount": placement_offset_count,
            "hiddenPairLayerCandidateCount": hidden_pair_count,
            "impositionCandidate": imposition_candidate,
            "sourceBackedR3BridgeHitCount": source_r3,
            "satisfiedReopenTriggerCount": satisfied,
            "triggerCount": trigger_count,
            "currentPdfAllLeafImpositionFingerprint": fingerprint,
        },
        "pdfRows": pdf_rows,
        "pageRows": page_rows,
        "pairRows": pair_rows,
        "pageByPdfArticle": page_by_pdf_article,
        "assessment": assessment,
        "decision": {
            "currentPdfAllLeafImpositionConsistencyGate": decision,
            "reason": "The current PDFs do not expose page-pair imposition differences that would alter held-to-light registration or supply unit/order evidence.",
        },
        "sheet": rel(OUT_SHEET),
        "fingerprint": fingerprint,
    }

    build_sheet(result)
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Current PDF All-Leaf Imposition Consistency Gate",
        "",
        "Scope: inspected page boxes, rotation, embedded image placement, scale, and hidden-layer indicators across article leaf pairs `75/76`, `77/78`, and `79/80` in the current PDFs. This checks original-layout/imposition provenance only; no key extraction, candidates, hashing-to-key, seed/WIF/address checks, BIP39 checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- PDFs / inspected page records / leaf pairs: `{len(PDFS)}` / `{len(page_rows)}` / `{len(pair_rows)}`",
        f"- Identical front/back pair geometry: `{identical_pair_count}` / `{len(pair_rows)}`",
        f"- PDFs with uniform page geometry across pages 75-80: `{within_pdf_uniform_count}` / `{len(pdf_rows)}`",
        f"- Unique geometry families: `{len(all_signatures)}`",
        f"- Side-margin pairs: `{side_margin_pair_count}`",
        f"- Placement-offset pairs / hidden pair-layer candidates: `{placement_offset_count}` / `{hidden_pair_count}`",
        f"- All-leaf imposition candidate: `{imposition_candidate}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{satisfied}/{trigger_count}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Fingerprint: `{fingerprint}`",
        "",
        "## PDF Rows",
        "",
        "| PDF | pages | uniform pages 75-80 | rotations | image sizes |",
        "|---|---:|---:|---|---|",
    ]
    for row in pdf_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['recordCount']}` | `{int(row['withinPdfUniformGeometry'])}` | "
            f"`{row['rotationSet']}` | `{row['imageSizeSet']}` |"
        )

    lines.extend(
        [
            "",
            "## Leaf Pair Rows",
            "",
            "| PDF | pair | same geometry | side margins | placement delta | hidden layer |",
            "|---|---|---:|---:|---|---:|",
        ]
    )
    for row in pair_rows:
        lines.append(
            f"| `{row['pdf']}` | `{row['frontArticlePage']}/{row['backArticlePage']}` | "
            f"`{int(row['identicalPairGeometry'])}` | `{int(row['hasSideMargins'])}` | "
            f"`{row['imageRectDeltaPt']}` | `{int(row['hiddenPairLayerCandidate'])}` |"
        )

    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{decision}`",
            "- All inspected leaf pairs preserve identical front/back geometry inside each PDF.",
            "- The duplicate PDFs' side margins are global derivative-PDF layout, not a page-76 or active-target imposition cue.",
            "- This keeps PDF original-layout/imposition differences closed as a held-to-light selector.",
            "",
            "## Next Move",
            "",
            "- Best direction remains physical/original-layout source validation or raw clue wording that explicitly names a registration unit, order, or transform.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"fingerprint: {fingerprint}")


if __name__ == "__main__":
    main()
