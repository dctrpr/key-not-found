#!/usr/bin/env python3
"""Test bitcoin4.pdf as a low-res Issue 24 geometry witness.

bitcoin4.pdf turned out to be the same Issue 24 article, not an independent Max
comparison article. This audit asks whether its alternate crop/scan geometry
naturally repairs the p78 -> p76 G5/O5 registration problem.

No key derivation is performed.
"""

from __future__ import annotations

import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BEST_PDF = ROOT / "magazine.pdf"
BITCOIN4_PDF = Path("private_inputs/Desktop/bitcoin4.pdf")
P78_GRAPHIC_JSON = ROOT / "analysis_outputs/source_audit/p78_graphic_pullquote_reflection/p78_graphic_pullquote_reflection.json"
LOWER_MARKS_JSON = ROOT / "analysis_outputs/source_audit/lower_page76_mark_pointers.json"
MAP_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"

OUT = ROOT / "analysis_outputs/source_audit/bitcoin4_issue24_geometry_witness"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "bitcoin4_issue24_geometry_witness.json"
OUT_MD = OUT / "bitcoin4_issue24_geometry_witness.md"
OUT_OVERLAY = OUT / "bitcoin4_issue24_geometry_witness_overlay.jpg"


def extract_page_image(path: Path, page_index: int) -> Image.Image:
    doc = fitz.open(path)
    page = doc[page_index]
    images = page.get_images(full=True)
    if images:
        raw = doc.extract_image(images[0][0])["image"]
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        if page.rotation:
            img = img.rotate(-page.rotation, expand=True)
        return img
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


def orange_components(img: Image.Image) -> list[dict[str, Any]]:
    arr = np.asarray(img.convert("RGB")).astype(np.int16)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    mask = (r > 150) & (g > 65) & (g < 230) & (b < 170) & ((r - b) > 45) & ((r - g) > -40)
    h, w = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    comps: list[dict[str, Any]] = []
    ys, xs = np.nonzero(mask)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if visited[sy, sx]:
            continue
        stack = [(sy, sx)]
        visited[sy, sx] = True
        area = 0
        x0 = x1 = sx
        y0 = y1 = sy
        while stack:
            y, x = stack.pop()
            area += 1
            x0 = min(x0, x)
            x1 = max(x1, x)
            y0 = min(y0, y)
            y1 = max(y1, y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True
                    stack.append((ny, nx))
        if area > 150:
            comps.append(
                {
                    "area": area,
                    "box": [x0, y0, x1 + 1, y1 + 1],
                    "width": x1 - x0 + 1,
                    "height": y1 - y0 + 1,
                }
            )
    comps.sort(key=lambda c: (c["box"][1], c["box"][0]))
    return comps


def article_orange_bands(comps: list[dict[str, Any]], page_kind: str, width: int) -> list[list[float]]:
    if page_kind == "p76":
        filtered = [
            c
            for c in comps
            if c["area"] > 2500
            and c["width"] > 100
            and c["height"] < 90
            and c["box"][1] > 200
            and c["box"][0] < width * 0.95
        ]
        return [c["box"] for c in filtered[:5]]
    if page_kind == "p78":
        filtered = [
            c
            for c in comps
            if c["area"] > 5000
            and c["width"] > 150
            and c["height"] < 90
            and 650 < c["box"][1] < 2100
            and c["box"][0] < width * 0.95
        ]
        return [c["box"] for c in filtered[:5]]
    raise ValueError(page_kind)


def fit_axis_aligned_affine(high_boxes: list[list[float]], low_boxes: list[list[float]]) -> dict[str, Any]:
    if len(high_boxes) != len(low_boxes) or len(high_boxes) < 2:
        raise ValueError("Need matched high/low boxes")
    high_x: list[float] = []
    low_x: list[float] = []
    high_y: list[float] = []
    low_y: list[float] = []
    for hi, lo in zip(high_boxes, low_boxes):
        high_x.extend([hi[0], hi[2]])
        low_x.extend([lo[0], lo[2]])
        high_y.extend([hi[1], hi[3]])
        low_y.extend([lo[1], lo[3]])
    ax, bx = np.polyfit(high_x, low_x, 1)
    ay, by = np.polyfit(high_y, low_y, 1)
    residuals = []
    for hi, lo in zip(high_boxes, low_boxes):
        pred = transform_box(hi, {"ax": ax, "bx": bx, "ay": ay, "by": by})
        residuals.extend(abs(pred[i] - lo[i]) for i in range(4))
    return {
        "ax": float(ax),
        "bx": float(bx),
        "ay": float(ay),
        "by": float(by),
        "meanAbsResidualPx": round(float(np.mean(residuals)), 3),
        "maxAbsResidualPx": round(float(np.max(residuals)), 3),
        "matchedHighBoxes": high_boxes,
        "matchedLowBoxes": low_boxes,
    }


def transform_box(box: list[float], t: dict[str, float]) -> list[float]:
    return [
        t["ax"] * box[0] + t["bx"],
        t["ay"] * box[1] + t["by"],
        t["ax"] * box[2] + t["bx"],
        t["ay"] * box[3] + t["by"],
    ]


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> tuple[float, list[float] | None]:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return 0.0, None
    box = [x1, y1, x2, y2]
    return area(box), box


def gap(a: list[float], b: list[float]) -> tuple[float, float]:
    horizontal = max(b[0] - a[2], a[0] - b[2], 0.0)
    vertical = max(b[1] - a[3], a[1] - b[3], 0.0)
    return horizontal, vertical


def target_record(frame: list[float], target: list[float]) -> dict[str, Any]:
    overlap, inter = intersection(frame, target)
    hgap, vgap = gap(frame, target)
    return {
        "targetBox": [round(v, 3) for v in target],
        "intersection": [round(v, 3) for v in inter] if inter else None,
        "overlapArea": round(overlap, 3),
        "overlapVsTarget": round(overlap / max(1.0, area(target)), 5),
        "horizontalGapPx": round(hgap, 3),
        "verticalGapPx": round(vgap, 3),
    }


def load_highres_targets() -> dict[str, list[float]]:
    data = json.loads(MAP_JSON.read_text())
    page76 = next(p for p in data["pages"] if p["page"] == 76)
    o5 = next(h for h in page76["highlights"] if h["id"] == "p76_orange_5")
    lower = json.loads(LOWER_MARKS_JSON.read_text())
    g5 = next(item for item in lower["analyses"] if "Volcano Bonds" in item.get("note", ""))
    return {
        "O5": [float(v) for v in o5["box"]],
        "G5": [float(v) for v in g5["box"]],
    }


def draw_overlay(img: Image.Image, frame: list[float], targets: dict[str, list[float]]) -> None:
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()

    def rect(box: list[float], color: tuple[int, int, int], label: str) -> None:
        b = [round(v) for v in box]
        draw.rectangle(b, outline=color, width=5)
        x, y = b[0], max(0, b[1] - 28)
        tb = draw.textbbox((x, y), label, font=font)
        draw.rectangle([tb[0] - 3, tb[1] - 3, tb[2] + 3, tb[3] + 3], fill="white")
        draw.text((x, y), label, fill=color, font=font)

    rect(targets["G5"], (0, 90, 255), "bitcoin4 mapped G5")
    rect(targets["O5"], (255, 120, 0), "bitcoin4 mapped O5")
    rect(frame, (255, 0, 0), "bitcoin4 p78 frame reflected")
    img.save(OUT_OVERLAY, quality=95)


def main() -> None:
    if not BITCOIN4_PDF.exists():
        raise FileNotFoundError(BITCOIN4_PDF)

    # Article pages: PDF page 4 is article p76, page 6 is article p78.
    best_p76 = extract_page_image(BEST_PDF, 3)
    best_p78 = extract_page_image(BEST_PDF, 5)
    low_p76 = extract_page_image(BITCOIN4_PDF, 3)
    low_p78 = extract_page_image(BITCOIN4_PDF, 5)

    best_p76_bands = article_orange_bands(orange_components(best_p76), "p76", best_p76.width)
    low_p76_bands = article_orange_bands(orange_components(low_p76), "p76", low_p76.width)
    best_p78_bands = article_orange_bands(orange_components(best_p78), "p78", best_p78.width)
    low_p78_bands = article_orange_bands(orange_components(low_p78), "p78", low_p78.width)

    p76_transform = fit_axis_aligned_affine(best_p76_bands, low_p76_bands)
    p78_transform = fit_axis_aligned_affine(best_p78_bands, low_p78_bands)

    graphic = json.loads(P78_GRAPHIC_JSON.read_text())
    p78_box_high = [float(v) for v in graphic["p78GraphicBox"]]
    p78_box_low = transform_box(p78_box_high, p78_transform)
    reflected_low = [low_p76.width - p78_box_low[2], p78_box_low[1], low_p76.width - p78_box_low[0], p78_box_low[3]]

    high_targets = load_highres_targets()
    low_targets = {name: transform_box(box, p76_transform) for name, box in high_targets.items()}
    low_records = {name: target_record(reflected_low, box) for name, box in low_targets.items()}

    # Baseline: a simple same-page-size scale of the high-res current frame.
    sx = low_p76.width / best_p76.width
    sy = low_p76.height / best_p76.height
    high_reflected_frame = [float(v) for v in graphic["reflectedBoxOnP76"]]
    scaled_frame = [high_reflected_frame[0] * sx, high_reflected_frame[1] * sy, high_reflected_frame[2] * sx, high_reflected_frame[3] * sy]
    scaled_targets = {
        name: [box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy] for name, box in high_targets.items()
    }
    scaled_records = {name: target_record(scaled_frame, box) for name, box in scaled_targets.items()}

    overlay = low_p76.copy()
    draw_overlay(overlay, reflected_low, low_targets)

    decision = (
        "bitcoin4.pdf does not repair the p78 -> p76 G5/O5 registration. In its own low-res geometry, "
        "the reflected p78 frame still clips O5, but it sits farther from trusted G5 than the current best scan."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "bitcoin4.pdf low-res Issue 24 geometry witness; no key derivation",
        "sources": {
            "best": str(BEST_PDF),
            "bitcoin4": str(BITCOIN4_PDF),
            "bestPageSize": [best_p76.width, best_p76.height],
            "bitcoin4PageSize": [low_p76.width, low_p76.height],
        },
        "matchedOrangeBands": {
            "p76Best": best_p76_bands,
            "p76Bitcoin4": low_p76_bands,
            "p78Best": best_p78_bands,
            "p78Bitcoin4": low_p78_bands,
        },
        "transforms": {"p76": p76_transform, "p78": p78_transform},
        "bitcoin4NaturalGeometry": {
            "p78BoxMappedToBitcoin4": [round(v, 3) for v in p78_box_low],
            "reflectedFrameOnBitcoin4P76": [round(v, 3) for v in reflected_low],
            "targets": {k: [round(v, 3) for v in box] for k, box in low_targets.items()},
            "records": low_records,
        },
        "simpleScaledHighresBaseline": {
            "scale": [round(sx, 6), round(sy, 6)],
            "frame": [round(v, 3) for v in scaled_frame],
            "records": scaled_records,
        },
        "overlay": str(OUT_OVERLAY),
        "decision": decision,
        "nextMove": "Keep bitcoin4.pdf as a source-fidelity witness only. Do not use it as geometry truth unless a separate rule explains why G5 should be ignored or re-registered.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# bitcoin4 Issue 24 Geometry Witness",
        "",
        "Scope: test whether `bitcoin4.pdf`, now identified as a low-res Issue 24 witness, naturally fixes the p78-to-p76 G5/O5 registration gap. No key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Overlay: `{OUT_OVERLAY}`",
        f"- Best scan page size: `{result['sources']['bestPageSize']}`",
        f"- bitcoin4 page size: `{result['sources']['bitcoin4PageSize']}`",
        "",
        "## Registration Fit",
        "",
        f"- p76 orange-band affine residual: mean `{p76_transform['meanAbsResidualPx']}px`, max `{p76_transform['maxAbsResidualPx']}px`.",
        f"- p78 orange-band affine residual: mean `{p78_transform['meanAbsResidualPx']}px`, max `{p78_transform['maxAbsResidualPx']}px`.",
        "",
        "## p78 Frame Result In bitcoin4 Geometry",
        "",
        f"- Reflected frame on bitcoin4 p76: `{result['bitcoin4NaturalGeometry']['reflectedFrameOnBitcoin4P76']}`",
        f"- O5 overlapVsTarget: `{low_records['O5']['overlapVsTarget']}`, gap `{low_records['O5']['horizontalGapPx']}x{low_records['O5']['verticalGapPx']}px`.",
        f"- G5 overlapVsTarget: `{low_records['G5']['overlapVsTarget']}`, gap `{low_records['G5']['horizontalGapPx']}x{low_records['G5']['verticalGapPx']}px`.",
        "",
        "## Scaled High-Res Baseline",
        "",
        f"- Simple scaled O5 overlapVsTarget: `{scaled_records['O5']['overlapVsTarget']}`.",
        f"- Simple scaled G5 overlapVsTarget: `{scaled_records['G5']['overlapVsTarget']}`, horizontal gap `{scaled_records['G5']['horizontalGapPx']}px`.",
        "",
        "## Decision",
        "",
        f"- {decision}",
        "",
        "## Next Move",
        "",
        f"- {result['nextMove']}",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_OVERLAY}")


if __name__ == "__main__":
    main()
