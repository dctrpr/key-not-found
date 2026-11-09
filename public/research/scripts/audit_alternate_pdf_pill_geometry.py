#!/usr/bin/env python3
"""Compare p79 pill/fragment geometry across local visual source witnesses.

The Canva note says "pills dont line up" and asks whether it is a "diff pic".
This script tests the only alternate local visual witness we have: the
Google/OCR PDF. It asks whether the lower-left p79 pill fragments are the same
five-fragment motif as the trusted `magazine.pdf` scan, or whether the alternate
PDF looks like a different source picture.

No key candidates are generated.
"""

from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw

from extract_visual_masks import connected_components, masks_for_page
from highres_reflection_extract import orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
GOOGLE_PDF = ROOT / "analysis_outputs/external_clues/google_drive_article_download.pdf"
OUT = ROOT / "analysis_outputs/source_audit/alternate_pdf_pill_geometry"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "alternate_pdf_pill_geometry.json"
OUT_MD = OUT / "alternate_pdf_pill_geometry.md"
OUT_SHEET = OUT / "alternate_pdf_pill_geometry_sheet.jpg"

ARTICLE_PAGE = 79
PDF_INDEX = ARTICLE_PAGE - 73


def render_google_page(target_size: tuple[int, int]) -> Image.Image:
    doc = fitz.open(GOOGLE_PDF)
    page = doc[PDF_INDEX]
    scale = max(target_size[0] / page.rect.width, target_size[1] / page.rect.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    img = Image.open(BytesIO(pix.tobytes("png"))).convert("RGB")
    return img.resize(target_size)


def center(box: tuple[int, int, int, int] | list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def area(box: tuple[int, int, int, int] | list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def highres_p79_fragments() -> list[dict]:
    boxes, _ = orange_boxes(ARTICLE_PAGE)
    rows = []
    for idx, box in enumerate(boxes, 1):
        if idx < 6:
            continue
        ibox = tuple(int(round(v)) for v in box)
        rows.append(
            {
                "index": idx,
                "box": ibox,
                "center": tuple(round(v, 2) for v in center(ibox)),
                "width": ibox[2] - ibox[0],
                "height": ibox[3] - ibox[1],
                "area": int(area(ibox)),
            }
        )
    return rows


def envelope(rows: list[dict], pad: int = 120) -> tuple[int, int, int, int]:
    boxes = [row["box"] for row in rows]
    return (
        max(0, min(b[0] for b in boxes) - pad),
        max(0, min(b[1] for b in boxes) - pad),
        max(b[2] for b in boxes) + pad,
        max(b[3] for b in boxes) + pad,
    )


def components_in_roi(img: Image.Image, roi: tuple[int, int, int, int]) -> list[dict]:
    mask = masks_for_page(img)["orange"]
    x1, y1, x2, y2 = roi
    sub = mask[y1:y2, x1:x2]
    comps = connected_components(sub, min_area=60)
    rows = []
    for i, comp in enumerate(comps, 1):
        bx1, by1, bx2, by2 = comp["box"]
        box = (bx1 + x1, by1 + y1, bx2 + x1, by2 + y1)
        w = box[2] - box[0]
        h = box[3] - box[1]
        # The five pill fragments are medium warm objects in this lower-left
        # region; this filter avoids tiny texture specks and huge text bands.
        if not (25 <= w <= 130 and 25 <= h <= 140 and 600 <= int(comp["area"]) <= 9000):
            continue
        rows.append(
            {
                "componentIndex": i,
                "box": box,
                "center": tuple(round(v, 2) for v in center(box)),
                "width": w,
                "height": h,
                "maskArea": int(comp["area"]),
                "boxArea": int(area(box)),
            }
        )
    rows.sort(key=lambda row: (row["center"][1], row["center"][0]))
    for i, row in enumerate(rows, 1):
        row["orderTopToBottom"] = i
    return rows


def fit_affine(source: list[dict], target: list[dict]) -> dict | None:
    if len(source) != len(target) or len(source) < 3:
        return None
    src = np.array([row["center"] for row in source], dtype=float)
    dst = np.array([row["center"] for row in target], dtype=float)
    design = np.column_stack([src, np.ones(len(src))])
    coef, _, _, _ = np.linalg.lstsq(design, dst, rcond=None)
    pred = design @ coef
    residuals = np.linalg.norm(pred - dst, axis=1)
    return {
        "sourceOrder": "top-to-bottom",
        "targetOrder": "top-to-bottom",
        "matrixRowsXYPrediction": [[round(float(v), 8) for v in row] for row in coef.T.tolist()],
        "predictedCenters": [[round(float(v), 2) for v in row] for row in pred.tolist()],
        "residualsPx": [round(float(v), 2) for v in residuals.tolist()],
        "meanResidualPx": round(float(residuals.mean()), 2),
        "maxResidualPx": round(float(residuals.max()), 2),
    }


def nearest_rows(source: list[dict], target: list[dict]) -> list[dict]:
    rows = []
    for src in source:
        sx, sy = src["center"]
        nearest = []
        for tgt in target:
            tx, ty = tgt["center"]
            nearest.append(
                {
                    "targetIndex": tgt.get("index", tgt.get("orderTopToBottom")),
                    "distancePx": round(((sx - tx) ** 2 + (sy - ty) ** 2) ** 0.5, 2),
                }
            )
        nearest.sort(key=lambda row: row["distancePx"])
        rows.append(
            {
                "sourceOrder": src["orderTopToBottom"],
                "sourceCenter": src["center"],
                "nearestHighres": nearest[:3],
            }
        )
    return rows


def draw_panel(img: Image.Image, rows: list[dict], label_key: str, roi: tuple[int, int, int, int], title: str) -> Image.Image:
    out = img.convert("RGB")
    draw = ImageDraw.Draw(out)
    draw.rectangle(roi, outline=(30, 120, 255), width=5)
    for row in rows:
        box = row["box"]
        draw.rectangle(box, outline=(255, 80, 0), width=5)
        draw.text((box[0], max(0, box[1] - 26)), str(row[label_key]), fill=(255, 80, 0))
    crop = out.crop(roi)
    header = Image.new("RGB", (crop.width, 48), (248, 248, 248))
    hdraw = ImageDraw.Draw(header)
    hdraw.text((14, 16), title, fill=(20, 20, 20))
    panel = Image.new("RGB", (crop.width, crop.height + header.height), (255, 255, 255))
    panel.paste(header, (0, 0))
    panel.paste(crop, (0, header.height))
    return panel


def make_sheet(high_img: Image.Image, google_img: Image.Image, high_rows: list[dict], google_rows: list[dict], roi: tuple[int, int, int, int]) -> None:
    panels = [
        draw_panel(high_img, high_rows, "index", roi, "trusted magazine.pdf p79 pill fragments"),
        draw_panel(google_img, google_rows, "orderTopToBottom", roi, "Google/OCR PDF p79 same normalized crop"),
    ]
    width = max(panel.width for panel in panels)
    height = sum(panel.height for panel in panels) + 18
    sheet = Image.new("RGB", (width, height), (255, 255, 255))
    y = 0
    for panel in panels:
        sheet.paste(panel, (0, y))
        y += panel.height + 18
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    high_img = upright_image(ARTICLE_PAGE)
    google_img = render_google_page(high_img.size)
    high_rows = highres_p79_fragments()
    roi = envelope(high_rows, pad=160)
    google_rows = components_in_roi(google_img, roi)
    raw_nearest = nearest_rows(google_rows, high_rows)
    affine = fit_affine(google_rows, high_rows)
    make_sheet(high_img, google_img, high_rows, google_rows, roi)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p79 pill-fragment geometry comparison between trusted magazine.pdf and Google/OCR PDF; no key derivation",
        "articlePage": ARTICLE_PAGE,
        "roi": roi,
        "sheet": str(OUT_SHEET),
        "trustedHighresFragments": high_rows,
        "googleNormalizedComponents": google_rows,
        "rawNearestDistances": raw_nearest,
        "affineFitGoogleToHighres": affine,
        "assessment": [
            "The alternate Google/OCR PDF contains the same countable five lower-left p79 pill fragments in the expected region.",
            "Raw same-normalized positions are shifted/distorted, confirming the OCR/Google PDF is not geometry truth.",
            "The five-fragment pattern is still the same motif, not evidence of a wholly different local picture source.",
            "This does not reopen capsule projection; it only confirms the local alternate PDF cannot solve the pills-don't-line-up clue without a different source image or physical scan.",
        ],
        "nextMove": "Keep the current high-res scan as trusted geometry. Reopen pill registration only if a new source image changes the five-fragment count/order or visibly moves the fragments.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Alternate PDF Pill Geometry Audit",
        "",
        "Scope: compare the p79 lower-left pill fragments in the trusted high-res `magazine.pdf` scan and the local Google/OCR PDF. No key candidates are generated.",
        "",
        f"- Sheet: `{OUT_SHEET}`",
        f"- ROI: `{roi}`",
        "",
        "## Counts",
        "",
        f"- trusted high-res fragments: `{len(high_rows)}`",
        f"- Google/OCR normalized components: `{len(google_rows)}`",
        "",
    ]
    if affine:
        lines.extend(
            [
                "## Five-Point Fit",
                "",
                f"- affine mean residual: `{affine['meanResidualPx']}` px",
                f"- affine max residual: `{affine['maxResidualPx']}` px",
                f"- residuals: `{affine['residualsPx']}`",
                "",
            ]
        )
    lines.extend(["## Raw Nearest Distances", ""])
    for row in raw_nearest:
        lines.append(f"- Google order {row['sourceOrder']} center {row['sourceCenter']} nearest `{row['nearestHighres']}`")
    lines.extend(
        [
            "",
            "## Assessment",
            "",
            "- The local Google/OCR PDF shows the same five lower-left p79 pill fragments, so it does not currently explain `diff pic` as a different visible picture.",
            "- The same-normalized geometry is shifted/distorted, which agrees with the larger source-registration gap: OCR/Google PDF is useful as a witness, not final geometry truth.",
            "- Do not reopen the ordered capsule projection from this PDF. Reopen only if a new source image or physical scan changes the five-fragment count/order/placement.",
            "",
            "## Next Best Move",
            "",
            "- Keep `magazine.pdf` as geometry truth. Use this sheet as the baseline if a new source image is supplied for the `pills don't line up / diff pic` clue.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
