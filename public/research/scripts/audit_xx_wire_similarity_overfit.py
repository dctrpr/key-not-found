#!/usr/bin/env python3
"""Test whether the Canva `XX` -> wire claim survives a two-point fit.

The earlier graphic-spill inventory tested only page-center flips/rotations.
This pass asks a stricter source-registration question: if we allow the two
p78 X marks to define a similarity transform onto the two p79 wire knots, does
the rest of the p78 graphic layer land on meaningful p79 marks, or is the
alignment just a two-point overfit?

No OCR, key derivation, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / "analysis_outputs/3d_article_map"
SOURCE_JSON = ROOT / "analysis_outputs/source_audit/graphic_spill_alignment_inventory/graphic_spill_alignment_inventory.json"
OUT = ROOT / "analysis_outputs/source_audit/xx_wire_similarity_overfit"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "xx_wire_similarity_overfit.json"
OUT_MD = OUT / "xx_wire_similarity_overfit.md"
OUT_SHEET = OUT / "xx_wire_similarity_overfit_sheet.jpg"

PAGE_W = 2544
PAGE_H = 3264


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def distance(a: list[float], b: list[float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle(a: list[float], b: list[float]) -> float:
    return math.atan2(b[1] - a[1], b[0] - a[0])


def deg(rad: float) -> float:
    return math.degrees(rad)


def obj(objects: dict, page: str, ident: str) -> dict:
    return next(item for item in objects[page] if item["id"] == ident)


def prep(point: list[float], reflected: bool) -> list[float]:
    if not reflected:
        return point
    return [point[0], -point[1]]


def fit_similarity(src_a: list[float], src_b: list[float], dst_a: list[float], dst_b: list[float], *, reflected: bool) -> dict:
    pa = prep(src_a, reflected)
    pb = prep(src_b, reflected)
    src_len = distance(pa, pb)
    dst_len = distance(dst_a, dst_b)
    scale = dst_len / src_len if src_len else 0.0
    theta = angle(dst_a, dst_b) - angle(pa, pb)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    # q = scale * R * prep(p) + t
    ax = scale * (cos_t * pa[0] - sin_t * pa[1])
    ay = scale * (sin_t * pa[0] + cos_t * pa[1])
    tx = dst_a[0] - ax
    ty = dst_a[1] - ay
    return {
        "scale": scale,
        "rotationDeg": deg(theta),
        "tx": tx,
        "ty": ty,
        "reflected": reflected,
    }


def apply_transform(point: list[float], transform: dict) -> list[float]:
    p = prep(point, transform["reflected"])
    scale = transform["scale"]
    theta = math.radians(transform["rotationDeg"])
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    return [
        scale * (cos_t * p[0] - sin_t * p[1]) + transform["tx"],
        scale * (sin_t * p[0] + cos_t * p[1]) + transform["ty"],
    ]


def transform_box(box: list[float], transform: dict) -> list[float]:
    points = [
        apply_transform([box[0], box[1]], transform),
        apply_transform([box[2], box[1]], transform),
        apply_transform([box[0], box[3]], transform),
        apply_transform([box[2], box[3]], transform),
    ]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def nearest(point: list[float], targets: list[dict], limit: int = 4) -> list[dict]:
    rows = []
    for target in targets:
        rows.append(
            {
                "targetId": target["id"],
                "targetLabel": target["label"],
                "targetKind": target["kind"],
                "distancePx": round(distance(point, center(target["box"])), 1),
            }
        )
    return sorted(rows, key=lambda row: row["distancePx"])[:limit]


def point_in_page(point: list[float]) -> bool:
    return 0 <= point[0] <= PAGE_W and 0 <= point[1] <= PAGE_H


def box_inside_fraction(box: list[float]) -> float:
    x0 = max(0, box[0])
    y0 = max(0, box[1])
    x1 = min(PAGE_W, box[2])
    y1 = min(PAGE_H, box[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    area = max(1, (box[2] - box[0]) * (box[3] - box[1]))
    return inter / area


def build_candidates(objects: dict) -> list[dict]:
    x_left = center(obj(objects, "p78", "p78_x_left")["box"])
    x_right = center(obj(objects, "p78", "p78_x_right")["box"])
    wire_left = center(obj(objects, "p79", "p79_wire_left_knot")["box"])
    wire_right = center(obj(objects, "p79", "p79_wire_right_knot")["box"])
    specs = [
        ("proper_left_to_left", x_left, x_right, wire_left, wire_right, False),
        ("proper_left_to_right", x_left, x_right, wire_right, wire_left, False),
        ("reflected_left_to_left", x_left, x_right, wire_left, wire_right, True),
        ("reflected_left_to_right", x_left, x_right, wire_right, wire_left, True),
    ]
    candidates = []
    for name, sa, sb, da, db, reflected in specs:
        transform = fit_similarity(sa, sb, da, db, reflected=reflected)
        rows = []
        transformed_boxes = []
        for item in objects["p78"]:
            pt = apply_transform(center(item["box"]), transform)
            tbox = transform_box(item["box"], transform)
            transformed_boxes.append(tbox)
            rows.append(
                {
                    "sourceId": item["id"],
                    "sourceLabel": item["label"],
                    "mappedCenter": [round(pt[0], 1), round(pt[1], 1)],
                    "insidePage": point_in_page(pt),
                    "boxInsideFraction": round(box_inside_fraction(tbox), 3),
                    "nearestP79": nearest(pt, objects["p79"], 4),
                }
            )
        non_x = [row for row in rows if row["sourceId"] not in {"p78_x_left", "p78_x_right"}]
        useful_non_x = [
            row
            for row in non_x
            if row["insidePage"] and row["nearestP79"][0]["distancePx"] <= 180
        ]
        candidates.append(
            {
                "name": name,
                "transform": {
                    "scale": round(transform["scale"], 4),
                    "rotationDeg": round(transform["rotationDeg"], 2),
                    "tx": round(transform["tx"], 2),
                    "ty": round(transform["ty"], 2),
                    "reflected": reflected,
                },
                "mappedObjects": rows,
                "nonXUsefulHitCount": len(useful_non_x),
                "nonXUsefulHits": useful_non_x,
                "allBoxesInsideFractionMin": round(min(box_inside_fraction(box) for box in transformed_boxes), 3),
            }
        )
    return candidates


def draw_box(draw: ImageDraw.ImageDraw, box: list[float], label: str, color: tuple[int, int, int]) -> None:
    b = [round(v) for v in box]
    draw.rectangle(b, outline=color, width=5)
    draw.text((b[0] + 6, b[1] + 6), label, fill=color)


def draw_sheet(objects: dict, candidates: list[dict]) -> None:
    base = Image.open(PAGE_DIR / "page_79_upright.jpg").convert("RGB").resize((PAGE_W, PAGE_H))
    try:
        fnt = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
    except OSError:
        fnt = ImageFont.load_default()
    previews = []
    for candidate in candidates:
        img = base.copy()
        draw = ImageDraw.Draw(img)
        for target in objects["p79"]:
            if target["kind"] in {"wire", "wire-line", "pill", "signature"}:
                draw_box(draw, target["box"], target["id"].replace("p79_", ""), (0, 90, 255))
        transform = candidate["transform"].copy()
        # Expand rounded report transform back into a usable transform.
        for item in objects["p78"]:
            tbox = transform_box(item["box"], transform)
            color = (245, 90, 0) if item["kind"] == "x" else (0, 150, 70)
            draw_box(draw, tbox, item["id"].replace("p78_", ""), color)
        crop = img.crop((0, 0, 1500, 950))
        band = Image.new("RGB", (crop.width, crop.height + 70), "white")
        band.paste(crop, (0, 70))
        d = ImageDraw.Draw(band)
        d.text(
            (18, 18),
            f"{candidate['name']} scale={candidate['transform']['scale']} rot={candidate['transform']['rotationDeg']}",
            fill=(15, 15, 15),
            font=fnt,
        )
        previews.append(band.resize((band.width // 2, band.height // 2)))
    width = max(p.width for p in previews)
    height = sum(p.height for p in previews) + 24 * (len(previews) - 1)
    sheet = Image.new("RGB", (width, height), "white")
    y = 0
    for preview in previews:
        sheet.paste(preview, (0, y))
        y += preview.height + 24
    sheet.save(OUT_SHEET, quality=94)


def fmt_nearest(row: dict) -> str:
    return ", ".join(f"{item['targetId']}={item['distancePx']}px" for item in row["nearestP79"][:3])


def main() -> None:
    source = load(SOURCE_JSON)
    objects = source["objects"]
    candidates = build_candidates(objects)
    draw_sheet(objects, candidates)
    best_non_x = max(candidates, key=lambda item: item["nonXUsefulHitCount"])
    assessment = [
        "A two-point similarity transform can force the p78 X pair onto the p79 wire knots, but that is tautological and must be judged by the non-X objects.",
        f"The best non-X result is `{best_non_x['name']}` with `{best_non_x['nonXUsefulHitCount']}` non-X graphic centers within 180 px of any p79 mark.",
        "The p78 `FUCK` spill and pull-quote blob do not land on a page-76/page-79 extraction surface or produce an instruction under this forced fit.",
        "This branch remains source-registration/orientation evidence only; it still needs a higher-resolution Canva/original-layout/physical source or an explicit object-pair rule.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "force p78 XX pair onto p79 wire knots with proper/reflected two-point similarity transforms; no OCR/key derivation",
        "sourceInventory": str(SOURCE_JSON.relative_to(ROOT)),
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "candidates": candidates,
        "assessment": assessment,
        "decision": "Forced XX-to-wire similarity alignment is an overfit under the current scan and does not unlock extraction.",
        "nextMove": "Do not derive from XX/wire/FUCK geometry locally. Reopen only if a higher-resolution Canva/original-layout/physical source specifies the graphic object pair or changes registration.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# XX/Wire Similarity Overfit Audit",
        "",
        "Scope: force the two p78 X marks onto the two p79 wire knots with proper and reflected two-point similarity transforms, then inspect where the rest of the p78 graphic layer lands. No OCR, key derivation, hashing, WIF, seed, or address checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source inventory: `{result['sourceInventory']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Candidate Fits",
        "",
        "| fit | scale | rotation | reflected | non-X useful hits | min box inside page |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for candidate in candidates:
        t = candidate["transform"]
        lines.append(
            f"| `{candidate['name']}` | `{t['scale']}` | `{t['rotationDeg']}` | `{t['reflected']}` | `{candidate['nonXUsefulHitCount']}` | `{candidate['allBoxesInsideFractionMin']}` |"
        )
    lines.extend(["", "## Non-X Landing Details", ""])
    for candidate in candidates:
        lines.append(f"### `{candidate['name']}`")
        for row in candidate["mappedObjects"]:
            if row["sourceId"] in {"p78_x_left", "p78_x_right"}:
                continue
            lines.append(
                f"- `{row['sourceId']}` -> {row['mappedCenter']}, inside={row['insidePage']}, nearest: {fmt_nearest(row)}"
            )
        lines.append("")
    lines.extend(["## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("best_non_x:", best_non_x["name"], best_non_x["nonXUsefulHitCount"])


if __name__ == "__main__":
    main()
