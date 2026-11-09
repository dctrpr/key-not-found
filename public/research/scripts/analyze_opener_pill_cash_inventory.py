#!/usr/bin/env python3
"""Inventory the photographed OVERDOSE opener spread as a visual source layer.

This pass keeps the opener pages separate from the page-76 target-corridor
tests. It asks a narrow question: do the opener pills/cash marks provide a
simple count/order selector that can explain the already-known page-79 pill
fragments or page-76 corridor? No private-key candidates are generated here.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from extract_visual_masks import connected_components, masks_for_page
from highres_reflection_extract import orange_boxes, upright_image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis_outputs/source_audit/announcement_opening_spread"
OUT = ROOT / "analysis_outputs/source_audit/opener_pill_cash_inventory"
OUT.mkdir(parents=True, exist_ok=True)

P73 = SOURCE / "pdf_p73_opener_left.jpg"
P74 = SOURCE / "pdf_p74_opener_right.jpg"
OUT_JSON = OUT / "opener_pill_cash_inventory.json"
OUT_MD = OUT / "opener_pill_cash_inventory.md"
OUT_SHEET = OUT / "opener_pill_cash_inventory_sheet.jpg"


def box_center(box: tuple[int, int, int, int]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def box_area(box: tuple[int, int, int, int]) -> int:
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def classify_p73_orange_components(img: Image.Image) -> tuple[list[dict], list[dict]]:
    """Return likely capsule components and other orange components on opener p73."""
    mask = masks_for_page(img)["orange"]
    comps = connected_components(mask, min_area=80)
    capsules: list[dict] = []
    other: list[dict] = []
    for idx, comp in enumerate(comps, 1):
        box = tuple(int(v) for v in comp["box"])
        x1, y1, x2, y2 = box
        w = x2 - x1
        h = y2 - y1
        area = int(comp["area"])
        item = {
            "componentIndex": idx,
            "box": box,
            "center": tuple(round(v, 2) for v in box_center(box)),
            "width": int(w),
            "height": int(h),
            "maskArea": area,
            "boxArea": int(box_area(box)),
        }
        # Page-73 capsules are the only medium orange objects below the title
        # line. This deliberately excludes the orange OVERDOSE section label.
        is_capsule = (
            y1 > 1200
            and 35 <= w <= 180
            and 35 <= h <= 180
            and 1_000 <= area <= 13_000
            and x1 < img.width * 0.65
        )
        if is_capsule:
            capsules.append(item)
        else:
            other.append(item)
    capsules.sort(key=lambda c: (c["center"][1], c["center"][0]))
    for i, cap in enumerate(capsules, 1):
        cap["capsuleIndexTopToBottom"] = i
    return capsules, other


def p74_orange_components(img: Image.Image) -> list[dict]:
    mask = masks_for_page(img)["orange"]
    comps = connected_components(mask, min_area=80)
    rows = []
    for idx, comp in enumerate(comps, 1):
        box = tuple(int(v) for v in comp["box"])
        rows.append(
            {
                "componentIndex": idx,
                "box": box,
                "center": tuple(round(v, 2) for v in box_center(box)),
                "width": box[2] - box[0],
                "height": box[3] - box[1],
                "maskArea": int(comp["area"]),
            }
        )
    return rows


def p79_pill_fragments() -> tuple[list[dict], tuple[int, int]]:
    boxes, size = orange_boxes(79)
    fragments = []
    for i, box in enumerate(boxes, 1):
        if i < 6:
            continue
        fragments.append(
            {
                "orangeBoxIndex": i,
                "box": tuple(int(v) for v in box),
                "center": tuple(round(v, 2) for v in box_center(box)),
                "width": int(box[2] - box[0]),
                "height": int(box[3] - box[1]),
                "boxArea": int(box_area(box)),
            }
        )
    return fragments, size


def fit_p73_to_p79(capsules: list[dict], fragments: list[dict]) -> dict:
    if len(capsules) != len(fragments) or len(capsules) < 3:
        return {
            "available": False,
            "reason": "requires equal counts and at least three paired points",
        }
    a = np.array([c["center"] for c in capsules], dtype=float)
    b = np.array([f["center"] for f in fragments], dtype=float)

    design = np.column_stack([a, np.ones(len(a))])
    affine_coef, _, _, _ = np.linalg.lstsq(design, b, rcond=None)
    affine_pred = design @ affine_coef
    affine_res = np.linalg.norm(affine_pred - b, axis=1)

    ac = a - a.mean(axis=0)
    bc = b - b.mean(axis=0)
    u, singular_values, vt = np.linalg.svd(ac.T @ bc)
    rotation = u @ vt
    similarity_scale = float(singular_values.sum() / (ac**2).sum())
    similarity_pred = ac @ rotation * similarity_scale + b.mean(axis=0)
    similarity_res = np.linalg.norm(similarity_pred - b, axis=1)

    return {
        "available": True,
        "pairingRule": "top-to-bottom p73 capsule order paired with p79 orange box order 6-10",
        "affine": {
            "matrixRowsXYPrediction": [[round(float(v), 8) for v in row] for row in affine_coef.T.tolist()],
            "predictedCenters": [[round(float(v), 2) for v in row] for row in affine_pred.tolist()],
            "residualsPx": [round(float(v), 2) for v in affine_res.tolist()],
            "meanResidualPx": round(float(affine_res.mean()), 2),
            "maxResidualPx": round(float(affine_res.max()), 2),
        },
        "similarity": {
            "scale": round(similarity_scale, 6),
            "rotationMatrix": [[round(float(v), 6) for v in row] for row in rotation.tolist()],
            "predictedCenters": [[round(float(v), 2) for v in row] for row in similarity_pred.tolist()],
            "residualsPx": [round(float(v), 2) for v in similarity_res.tolist()],
            "meanResidualPx": round(float(similarity_res.mean()), 2),
            "maxResidualPx": round(float(similarity_res.max()), 2),
        },
    }


def draw_page(img: Image.Image, boxes: list[dict], label_key: str, color: tuple[int, int, int]) -> Image.Image:
    out = img.convert("RGB")
    draw = ImageDraw.Draw(out)
    for item in boxes:
        box = tuple(item["box"])
        label = str(item[label_key])
        draw.rectangle(box, outline=color, width=6)
        draw.text((box[0], max(0, box[1] - 30)), label, fill=color)
    return out


def make_contact_sheet(p73_img: Image.Image, p74_img: Image.Image, p79_img: Image.Image, capsules: list[dict], p79_fragments: list[dict]) -> None:
    p73_annotated = draw_page(p73_img, capsules, "capsuleIndexTopToBottom", (255, 90, 0))
    p79_annotated = draw_page(p79_img, p79_fragments, "orangeBoxIndex", (255, 90, 0))

    p73_crop = p73_annotated.crop((300, 1120, 1500, 2850))
    p74_crop = p74_img.crop((1550, 80, 2380, 330))
    p79_crop = p79_annotated.crop((0, 0, p79_img.width, p79_img.height))

    def thumb(img: Image.Image, max_size: tuple[int, int]) -> Image.Image:
        copy = img.copy()
        copy.thumbnail(max_size, Image.Resampling.LANCZOS)
        return copy

    items = [
        ("p73 opener capsules", thumb(p73_crop, (520, 720))),
        ("p74 orange opener label only", thumb(p74_crop, (520, 180))),
        ("p79 known orange boxes 6-10", thumb(p79_crop, (520, 720))),
    ]
    cell_w = 560
    cell_h = 790
    sheet = Image.new("RGB", (cell_w * len(items), cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    for i, (label, img) in enumerate(items):
        x = i * cell_w + 20
        y = 52
        draw.text((x, 20), label, fill=(0, 0, 0))
        sheet.paste(img, (x, y))
    sheet.save(OUT_SHEET, quality=93)


def main() -> None:
    p73_img = Image.open(P73).convert("RGB")
    p74_img = Image.open(P74).convert("RGB")
    p79_img = upright_image(79)

    p73_capsules, p73_other_orange = classify_p73_orange_components(p73_img)
    p74_orange = p74_orange_components(p74_img)
    p79_fragments, p79_size = p79_pill_fragments()
    p73_to_p79_fit = fit_p73_to_p79(p73_capsules, p79_fragments)
    make_contact_sheet(p73_img, p74_img, p79_img, p73_capsules, p79_fragments)

    capsule_centers = [c["center"] for c in p73_capsules]
    vertical_steps = []
    diagonal_steps = []
    for a, b in zip(capsule_centers, capsule_centers[1:]):
        vertical_steps.append(round(b[1] - a[1], 2))
        diagonal_steps.append((round(b[0] - a[0], 2), round(b[1] - a[1], 2)))

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "visual source-layer inventory only; no key derivation",
        "inputs": {
            "p73Opener": str(P73),
            "p74Opener": str(P74),
            "p79HighRes": "magazine.pdf article page 79 via highres_reflection_extract.upright_image",
        },
        "reviewSheet": str(OUT_SHEET),
        "p73CapsuleCount": len(p73_capsules),
        "p73CapsulesTopToBottom": p73_capsules,
        "p73OtherOrangeComponents": p73_other_orange,
        "p73CapsuleVerticalSteps": vertical_steps,
        "p73CapsuleDiagonalSteps": diagonal_steps,
        "p74OrangeComponents": p74_orange,
        "p79PillFragmentCount": len(p79_fragments),
        "p79PillFragmentsFromManualOrangeBoxes": p79_fragments,
        "p79ImageSize": p79_size,
        "p73CapsulesToP79FragmentsFit": p73_to_p79_fit,
        "assessment": [
            "The opener spread contains a clean page-73 five-capsule row, and page 79 contains five known orange pill fragments.",
            "The top-to-bottom p73 capsule row fits p79 orange boxes 6-10 as a scaled/rotated duplicate with about one pixel mean residual, so the page-79 fragments appear to reuse the opener capsule motif.",
            "This is strong source-layer linkage, but the duplicated five-count still does not define target region or extraction unit by itself.",
            "Keep p73/p79 capsule order active as provenance/orientation evidence; close capsule count alone as a direct selector.",
        ],
        "nextMove": "Use the recovered five-capsule order only as an ordering layer for an already-supported p79->p76 mirror rule; do not hash/count it directly.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")

    lines = [
        "# Opener Pill / Cash Inventory",
        "",
        "Scope: visual source-layer inventory only. This pass records the photographed `OVERDOSE` opener pills/cash/field motif and compares it with the known page-79 pill fragments. It does not generate private-key candidates.",
        "",
        f"- Review sheet: `{OUT_SHEET}`",
        f"- Page 73 capsules detected: `{len(p73_capsules)}`",
        f"- Page 79 known pill/orange fragments: `{len(p79_fragments)}`",
        f"- Page 74 orange components: `{len(p74_orange)}`",
        "",
        "## Page 73 Capsules",
        "",
    ]
    for cap in p73_capsules:
        lines.append(
            f"- O73-{cap['capsuleIndexTopToBottom']}: box={cap['box']} center={cap['center']} size={cap['width']}x{cap['height']} maskArea={cap['maskArea']}"
        )
    lines.extend(["", "## Page 79 Fragments", ""])
    for frag in p79_fragments:
        lines.append(
            f"- P79-{frag['orangeBoxIndex']}: box={frag['box']} center={frag['center']} size={frag['width']}x{frag['height']}"
        )
    lines.extend(
        [
            "",
            "## Assessment",
            "",
        "- The opener spread is real source/provenance evidence because Max's announcement photo foregrounds it.",
            "- Page 73 has a visually clean five-capsule sequence; page 79 also has five known orange pill fragments.",
            f"- Paired top-to-bottom, the p73 capsules fit p79 orange boxes 6-10 with affine mean residual `{p73_to_p79_fit['affine']['meanResidualPx'] if p73_to_p79_fit.get('available') else 'n/a'}` px and max residual `{p73_to_p79_fit['affine']['maxResidualPx'] if p73_to_p79_fit.get('available') else 'n/a'}` px.",
            "- That near-perfect fit means the page-79 fragments are very likely a scaled/rotated reuse of the opener capsule artwork, not five unrelated marks.",
            "- This gives a reliable five-item ordering layer, but it still does not define target region or extraction unit. It cannot yet select letters from page 76 by itself.",
            "- Close `opener capsule count alone` as a direct selector. Keep p73/p79 capsule order active only when a specific mirror/fold rule ties it to page 76.",
            "",
            "## Next Best Move",
            "",
            "- Use the five-capsule order as an ordering layer for a supported p79->p76 mirror operation, not as key material.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print(f"p73 capsules={len(p73_capsules)} p79 fragments={len(p79_fragments)} p74 orange={len(p74_orange)}")


if __name__ == "__main__":
    main()
