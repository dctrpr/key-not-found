#!/usr/bin/env python3
"""Inventory the Canva-named p78/p79/p80 graphic spill alignment.

The live Canva note names a visual layer rather than article text:
`XX`, barbed wire, `SHIT`, and `FUCK ALL SHITCOINS` spills after
rotation/mirroring. This pass keeps the scope narrow: manually register the
obvious high-res graphic objects on pages 78-80, test simple mirror/rotation
relations, and decide whether this layer supplies a selector or only confirms
orientation/source-registration.

No keys, hashes, mnemonics, WIFs, or addresses are generated.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PAGE_DIR = ROOT / "analysis_outputs/3d_article_map"
OUT = ROOT / "analysis_outputs/source_audit/graphic_spill_alignment_inventory"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "graphic_spill_alignment_inventory.json"
OUT_MD = OUT / "graphic_spill_alignment_inventory.md"
OUT_SHEET = OUT / "graphic_spill_alignment_inventory_sheet.jpg"

PAGE_W = 2544
PAGE_H = 3264

# Approximate high-res boxes from manual inspection of the current best scan.
OBJECTS = {
    "p78": [
        {"id": "p78_x_left", "label": "left X beside FUCK graphic", "kind": "x", "box": [265, 2795, 370, 2898]},
        {"id": "p78_x_right", "label": "right X beside FUCK graphic", "kind": "x", "box": [1070, 2775, 1170, 2870]},
        {"id": "p78_fuck_spill", "label": "FUCK / black spill graphic", "kind": "spill", "box": [340, 2685, 985, 2905]},
        {"id": "p78_pullquote_blob", "label": "black pull-quote blob", "kind": "blob", "box": [345, 2775, 1110, 3135]},
    ],
    "p79": [
        {"id": "p79_wire_left_knot", "label": "barbed-wire left knot", "kind": "wire", "box": [55, 360, 190, 470]},
        {"id": "p79_wire_right_knot", "label": "barbed-wire right knot", "kind": "wire", "box": [455, 120, 650, 275]},
        {"id": "p79_wire_span", "label": "barbed-wire diagonal span", "kind": "wire-line", "box": [35, 0, 830, 500]},
        {"id": "p79_pill_1", "label": "pill 1", "kind": "pill", "box": [145, 2370, 200, 2448]},
        {"id": "p79_pill_2", "label": "pill 2", "kind": "pill", "box": [385, 2425, 460, 2482]},
        {"id": "p79_pill_3", "label": "pill 3", "kind": "pill", "box": [575, 2575, 640, 2645]},
        {"id": "p79_pill_4", "label": "pill 4", "kind": "pill", "box": [405, 2745, 470, 2818]},
        {"id": "p79_pill_5", "label": "pill 5", "kind": "pill", "box": [158, 2930, 210, 3005]},
        {"id": "p79_max_signature", "label": "MAX KEISER signature", "kind": "signature", "box": [930, 2790, 1460, 3175]},
    ],
    "p80": [
        {"id": "p80_cap_5_symptom", "label": "cap 5 SYMPTOM RELIEF", "kind": "package", "box": [1580, 655, 1985, 1085]},
        {"id": "p80_100_proof", "label": "100% Proof of Work Liquid", "kind": "package-text", "box": [970, 1845, 1395, 1990]},
        {"id": "p80_volume_16", "label": "16 FL OZ (473 mL)", "kind": "package-text", "box": [870, 2470, 1305, 2575]},
        {"id": "p80_symptoms", "label": "NAUSEA/HEARTBURN/INDIGESTION/UPSET STOMACH/SHITCOINS", "kind": "package-text", "box": [1470, 2315, 1910, 2625]},
        {"id": "p80_shitcoins", "label": "SHITCOINS", "kind": "package-text", "box": [1540, 2548, 1865, 2622]},
    ],
}


def center(box: list[float]) -> list[float]:
    return [(box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0]


def transform_point(point: list[float], mode: str) -> list[float]:
    x, y = point
    if mode == "identity":
        return [x, y]
    if mode == "hflip":
        return [PAGE_W - x, y]
    if mode == "vflip":
        return [x, PAGE_H - y]
    if mode == "rot180":
        return [PAGE_W - x, PAGE_H - y]
    raise ValueError(mode)


def transform_box(box: list[float], mode: str) -> list[float]:
    points = [
        transform_point([box[0], box[1]], mode),
        transform_point([box[2], box[1]], mode),
        transform_point([box[0], box[3]], mode),
        transform_point([box[2], box[3]], mode),
    ]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def distance(a: list[float], b: list[float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def line_angle(a: list[float], b: list[float]) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def angle_delta(a: float, b: float) -> float:
    delta = abs((a - b + 90) % 180 - 90)
    return delta


def point_line_distance(point: list[float], a: list[float], b: list[float]) -> float:
    x0, y0 = point
    x1, y1 = a
    x2, y2 = b
    denom = math.hypot(y2 - y1, x2 - x1)
    if denom == 0:
        return distance(point, a)
    return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / denom


def obj(page: str, ident: str) -> dict:
    return next(item for item in OBJECTS[page] if item["id"] == ident)


def nearest(source_point: list[float], targets: list[dict], limit: int = 4) -> list[dict]:
    rows = []
    for target in targets:
        rows.append(
            {
                "targetId": target["id"],
                "targetLabel": target["label"],
                "targetKind": target["kind"],
                "distancePx": round(distance(source_point, center(target["box"])), 1),
            }
        )
    return sorted(rows, key=lambda row: row["distancePx"])[:limit]


def analyze_p78_to_p79() -> dict:
    x_left = obj("p78", "p78_x_left")
    x_right = obj("p78", "p78_x_right")
    fuck = obj("p78", "p78_fuck_spill")
    wire_left = obj("p79", "p79_wire_left_knot")
    wire_right = obj("p79", "p79_wire_right_knot")
    wire_a = center(wire_left["box"])
    wire_b = center(wire_right["box"])
    wire_angle = line_angle(wire_a, wire_b)
    rows = []
    for mode in ["identity", "hflip", "vflip", "rot180"]:
        left = transform_point(center(x_left["box"]), mode)
        right = transform_point(center(x_right["box"]), mode)
        fuck_center = transform_point(center(fuck["box"]), mode)
        x_angle = line_angle(left, right)
        rows.append(
            {
                "mode": mode,
                "xPairAngleDeg": round(x_angle, 2),
                "wireAngleDeg": round(wire_angle, 2),
                "angleDeltaDeg": round(angle_delta(x_angle, wire_angle), 2),
                "leftXToWireLinePx": round(point_line_distance(left, wire_a, wire_b), 1),
                "rightXToWireLinePx": round(point_line_distance(right, wire_a, wire_b), 1),
                "fuckCenterToWireLinePx": round(point_line_distance(fuck_center, wire_a, wire_b), 1),
                "nearestP79ForLeftX": nearest(left, OBJECTS["p79"], 3),
                "nearestP79ForRightX": nearest(right, OBJECTS["p79"], 3),
                "nearestP79ForFuck": nearest(fuck_center, OBJECTS["p79"], 3),
            }
        )
    return {
        "wireLine": {
            "leftKnotCenter": wire_a,
            "rightKnotCenter": wire_b,
            "angleDeg": round(wire_angle, 2),
        },
        "rows": rows,
    }


def analyze_p80_to_p79() -> dict:
    rows = []
    for source_id in ["p80_symptoms", "p80_shitcoins", "p80_volume_16", "p80_cap_5_symptom"]:
        source = obj("p80", source_id)
        for mode in ["hflip", "rot180", "vflip"]:
            pt = transform_point(center(source["box"]), mode)
            rows.append(
                {
                    "sourceId": source_id,
                    "sourceLabel": source["label"],
                    "mode": mode,
                    "mappedCenter": [round(pt[0], 1), round(pt[1], 1)],
                    "nearestP79": nearest(pt, OBJECTS["p79"], 4),
                }
            )
    return {"rows": rows}


def draw_box(draw: ImageDraw.ImageDraw, box: list[float], label: str, color: tuple[int, int, int], offset=(0, 0)) -> None:
    ox, oy = offset
    b = [box[0] + ox, box[1] + oy, box[2] + ox, box[3] + oy]
    draw.rectangle(b, outline=color, width=6)
    draw.text((b[0] + 8, b[1] + 8), label, fill=color)


def make_sheet() -> None:
    p79 = Image.open(PAGE_DIR / "page_79_upright.jpg").convert("RGB").resize((PAGE_W, PAGE_H))
    p78 = Image.open(PAGE_DIR / "page_78_upright.jpg").convert("RGB").resize((PAGE_W, PAGE_H))
    p80 = Image.open(PAGE_DIR / "page_80_upright.jpg").convert("RGB").resize((PAGE_W, PAGE_H))
    transforms = {
        "p78 vflip on p79": ImageOps.flip(p78),
        "p78 rot180 on p79": p78.transpose(Image.Transpose.ROTATE_180),
        "p78 hflip on p79": ImageOps.mirror(p78),
        "p80 hflip on p79": ImageOps.mirror(p80),
    }
    crops = {
        "p78 vflip on p79": (0, 0, 1500, 720),
        "p78 rot180 on p79": (0, 0, 2544, 900),
        "p78 hflip on p79": (0, 2200, 2544, 3264),
        "p80 hflip on p79": (0, 2100, 2200, 3264),
    }
    previews = []
    try:
        font = ImageFont.truetype("Arial.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    for title, transformed in transforms.items():
        blend = Image.blend(p79, transformed, 0.42).convert("RGB")
        draw = ImageDraw.Draw(blend)
        for item in OBJECTS["p79"]:
            if item["kind"] in {"wire", "wire-line", "pill", "signature"}:
                draw_box(draw, item["box"], item["id"].replace("p79_", ""), (0, 80, 255))
        if title.startswith("p78"):
            mode = "vflip" if "vflip" in title else ("rot180" if "rot180" in title else "hflip")
            for item in OBJECTS["p78"]:
                draw_box(draw, transform_box(item["box"], mode), item["id"].replace("p78_", ""), (240, 95, 0))
        else:
            for item in OBJECTS["p80"]:
                draw_box(draw, transform_box(item["box"], "hflip"), item["id"].replace("p80_", ""), (240, 95, 0))
        crop = blend.crop(crops[title])
        band = Image.new("RGB", (crop.width, crop.height + 58), "white")
        band.paste(crop, (0, 58))
        d = ImageDraw.Draw(band)
        d.text((18, 14), title, fill=(10, 10, 10), font=font)
        previews.append(band.resize((band.width // 2, band.height // 2)))

    width = max(p.width for p in previews)
    height = sum(p.height for p in previews) + 30 * (len(previews) - 1)
    sheet = Image.new("RGB", (width, height), "white")
    y = 0
    for preview in previews:
        sheet.paste(preview, (0, y))
        y += preview.height + 30
    sheet.save(OUT_SHEET, quality=94)


def main() -> None:
    p78_to_p79 = analyze_p78_to_p79()
    p80_to_p79 = analyze_p80_to_p79()
    make_sheet()

    best_x_wire = min(
        p78_to_p79["rows"],
        key=lambda row: max(row["leftXToWireLinePx"], row["rightXToWireLinePx"]),
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "p78/p79/p80 graphic spill alignment inventory; no key derivation",
        "manualObjectNote": "Object boxes are approximate visual annotations on the current high-res magazine scan.",
        "objects": OBJECTS,
        "p78ToP79": p78_to_p79,
        "p80ToP79": p80_to_p79,
        "sheet": str(OUT_SHEET.relative_to(ROOT)),
        "assessment": [
            "The obvious p78 `XX` pair does not become collinear with the p79 barbed-wire line under identity, hflip, vflip, or 180-degree rotation.",
            f"The best simple p78 transform for keeping both X marks near the p79 wire is `{best_x_wire['mode']}`, but its worst X-to-wire distance is {max(best_x_wire['leftXToWireLinePx'], best_x_wire['rightXToWireLinePx'])} px and the angle delta is {best_x_wire['angleDeltaDeg']} degrees.",
            "p80 `SHITCOINS` and symptom text continue to map only as broad package/provenance evidence under simple flips; they do not pick a page-79 or page-76 unit.",
            "This supports the Canva note as an orientation/source-registration warning, not as a solved selector in the current high-res scan.",
        ],
        "nextMove": "Do not derive key material from `XX`/wire/SHIT spill geometry in the current scan. Reopen this branch only with a higher-resolution Canva/original-layout/physical overlay, or if a new source rule names which graphic object pair is meant.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Graphic Spill Alignment Inventory",
        "",
        "Scope: inventory the Canva-named `XX` / barbed-wire / `SHIT`-spill graphic layer across pages 78-80. This is a visual registration pass only; no key derivation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "- Manual object boxes are approximate visual annotations on the current high-res magazine scan.",
        "",
        "## P78 `XX` / FUCK Graphic To P79 Barbed Wire",
        "",
        f"- P79 wire angle: `{p78_to_p79['wireLine']['angleDeg']}` degrees.",
        "",
        "| transform | X-pair angle | angle delta vs wire | left X to wire | right X to wire | FUCK center to wire | nearest left X | nearest right X |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in p78_to_p79["rows"]:
        nearest_left = row["nearestP79ForLeftX"][0]
        nearest_right = row["nearestP79ForRightX"][0]
        lines.append(
            f"| `{row['mode']}` | `{row['xPairAngleDeg']}` | `{row['angleDeltaDeg']}` | `{row['leftXToWireLinePx']}` | `{row['rightXToWireLinePx']}` | `{row['fuckCenterToWireLinePx']}` | "
            f"`{nearest_left['targetId']} {nearest_left['distancePx']}px` | `{nearest_right['targetId']} {nearest_right['distancePx']}px` |"
        )
    lines.extend(["", "## P80 Package / SHITCOINS To P79 Marks", "", "| source | transform | nearest p79 marks |", "|---|---|---|"])
    for row in p80_to_p79["rows"]:
        nearest_text = ", ".join(f"{item['targetId']}={item['distancePx']}px" for item in row["nearestP79"][:3])
        lines.append(f"| `{row['sourceId']}` | `{row['mode']}` | {nearest_text} |")
    lines.extend(["", "## Assessment", ""])
    for item in result["assessment"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_SHEET}")
    print("best p78 x/wire simple transform:", best_x_wire["mode"], "worst-distance", max(best_x_wire["leftXToWireLinePx"], best_x_wire["rightXToWireLinePx"]))


if __name__ == "__main__":
    main()
