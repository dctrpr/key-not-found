#!/usr/bin/env python3
"""Check whether page-80 package regions align to page-76 anchors.

This is a bounded geometry audit over simple existing mirror/fold transforms:
identity, horizontal mirror, vertical mirror, and 180-degree rotation. It tests
page-80 package/highlight regions against the four trusted page-76 anchors.
No OCR extraction, key derivation, hashing, or address checks are performed.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from analyze_front_back_leaf_box_registration import orange_items
from highres_reflection_extract import ensure_highres_sources, upright_image


ROOT = Path(__file__).resolve().parents[1]
ANCHORS = ROOT / "analysis_outputs/source_audit/page76_anchor_adjacency_units/page76_anchor_adjacency_units.json"
P80_CHOICE = ROOT / "analysis_outputs/source_audit/p80_four_anchor_choice/p80_four_anchor_choice.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/p80_to_p76_anchor_geometry"
OUT_JSON = OUT_DIR / "p80_to_p76_anchor_geometry.json"
OUT_MD = OUT_DIR / "p80_to_p76_anchor_geometry.md"
OUT_IMG = OUT_DIR / "p80_to_p76_anchor_geometry_sheet.jpg"


TRANSFORMS = ["identity", "hflip", "vflip", "rotate180"]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def transform_box(box: list[float], width: int, height: int, transform: str) -> list[float]:
    x1, y1, x2, y2 = box
    if transform == "identity":
        return [x1, y1, x2, y2]
    if transform == "hflip":
        return [width - x2, y1, width - x1, y2]
    if transform == "vflip":
        return [x1, height - y2, x2, height - y1]
    if transform == "rotate180":
        return [width - x2, height - y2, width - x1, height - y1]
    raise ValueError(transform)


def area(box: list[float]) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a: list[float], b: list[float]) -> list[float] | None:
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])
    if x2 <= x1 or y2 <= y1:
        return None
    return [x1, y1, x2, y2]


def center(box: list[float]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def dist(a: list[float], b: list[float]) -> float:
    ax, ay = center(a)
    bx, by = center(b)
    return ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5


def load_anchors() -> list[dict[str, Any]]:
    data = json.loads(ANCHORS.read_text(encoding="utf-8"))
    out = []
    for record in data["anchors"]:
        out.append(
            {
                "id": record["id"],
                "label": record["label"],
                "color": record["color"],
                "box": record["box"],
            }
        )
    return out


def package_items() -> list[dict[str, Any]]:
    # The existing p79/p80 drilldown established p80 O1 and O2 as the package labels.
    keep = {1, 2}
    return [item for item in orange_items(80) if item["index"] in keep]


def draw_sheet(anchors: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    p76 = upright_image(76).convert("RGBA")
    crop = (360, 2108, 2544, 3218)
    panels = []
    for transform in TRANSFORMS:
        base = p76.copy()
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for anchor in anchors:
            outline = (255, 135, 0, 255) if anchor["color"] == "orange" else (10, 20, 30, 255)
            draw.rectangle(tuple(anchor["box"]), outline=outline, width=6)
            draw.text((anchor["box"][0], max(0, anchor["box"][1] - 26)), anchor["label"], fill=outline)
        for row in rows:
            if row["transform"] != transform:
                continue
            box = row["mappedBox"]
            color = (90, 40, 190, 210) if row["sourceIndex"] == 1 else (30, 130, 220, 210)
            draw.rectangle(tuple(box), outline=color, width=5)
            draw.text((box[0], max(0, box[1] - 26)), f"p80 O{row['sourceIndex']}", fill=color)
        composed = Image.alpha_composite(base, overlay).convert("RGB")
        panel = composed.crop(crop)
        header = Image.new("RGB", (panel.width, 48), (248, 249, 252))
        hdraw = ImageDraw.Draw(header)
        hdraw.text((16, 14), transform, font=font(18, True), fill=(20, 28, 38))
        combined = Image.new("RGB", (panel.width, panel.height + header.height), "white")
        combined.paste(header, (0, 0))
        combined.paste(panel, (0, header.height))
        panels.append(combined)
    sheet_w = max(panel.width for panel in panels) * 2 + 24
    sheet_h = max(panel.height for panel in panels[:2]) + max(panel.height for panel in panels[2:]) + 24
    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    positions = [(0, 0), (panels[0].width + 24, 0), (0, panels[0].height + 24), (panels[2].width + 24, panels[0].height + 24)]
    for panel, pos in zip(panels, positions):
        sheet.paste(panel, pos)
    sheet.save(OUT_IMG, quality=94)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_highres_sources()
    p80 = upright_image(80)
    anchors = load_anchors()
    items = package_items()
    rows: list[dict[str, Any]] = []
    for item in items:
        for transform in TRANSFORMS:
            mapped = transform_box(item["box"], p80.width, p80.height, transform)
            checks = []
            for anchor in anchors:
                inter = intersection(mapped, anchor["box"])
                inter_area = area(inter) if inter else 0.0
                checks.append(
                    {
                        "anchorId": anchor["id"],
                        "anchor": anchor["label"],
                        "intersectionArea": round(inter_area, 2),
                        "intersectionOverAnchor": round(inter_area / area(anchor["box"]), 4) if area(anchor["box"]) else 0,
                        "intersectionOverMapped": round(inter_area / area(mapped), 4) if area(mapped) else 0,
                        "centerDistance": round(dist(mapped, anchor["box"]), 2),
                    }
                )
            checks.sort(key=lambda row: (-row["intersectionArea"], row["centerDistance"]))
            rows.append(
                {
                    "sourceIndex": item["index"],
                    "sourceLabel": item["label"],
                    "sourceBox": item["box"],
                    "transform": transform,
                    "mappedBox": [round(v, 2) for v in mapped],
                    "bestAnchor": checks[0],
                    "allAnchors": checks,
                }
            )
    draw_sheet(anchors, rows)

    positive = [
        row
        for row in rows
        if row["bestAnchor"]["intersectionOverAnchor"] >= 0.1 or row["bestAnchor"]["intersectionOverMapped"] >= 0.1
    ]
    near = sorted(rows, key=lambda row: row["bestAnchor"]["centerDistance"])[:4]
    p80_choice = json.loads(P80_CHOICE.read_text(encoding="utf-8"))
    assessment = [
        "No page-80 package label maps directly onto the four page-76 anchors under identity, hflip, vflip, or 180-degree rotation.",
        "The closest center-distance cases are still broad package-box placements, not narrow anchor overlaps.",
        "This supports keeping p80 as theme/count corroboration only; it does not physically choose the OBBO anchors in the current scan.",
        "Reopen p80 geometry only if a new physical/source image changes page registration or gives an explicit fold axis.",
    ]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "simple p80 package-label to p76 four-anchor geometry audit; identity/hflip/vflip/rotate180 only; no key derivation",
        "sources": {
            "anchorAdjacency": str(ANCHORS.relative_to(ROOT)),
            "p80Choice": str(P80_CHOICE.relative_to(ROOT)),
        },
        "sheet": str(OUT_IMG.relative_to(ROOT)),
        "anchors": anchors,
        "p80ChoiceDecision": p80_choice.get("decision"),
        "rows": rows,
        "positiveOverlapRows": positive,
        "nearestRows": near,
        "assessment": assessment,
        "decision": "Keep p80 package geometry closed for the current scan; no tested mirror/fold transform selects the four page-76 anchors.",
        "nextMove": "Move back to the page-76/p78-p79 corridor itself: test whether M3/M4 standalone marks choose anchor order within OBBO.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# P80 to Page-76 Anchor Geometry Audit",
        "",
        "Scope: simple p80 package-label to p76 four-anchor geometry audit using identity, hflip, vflip, and 180-degree rotation. No key derivation, hashing, seed checks, WIF checks, address checks, or broad brute force were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Nearest Cases",
        "",
        "| p80 label | transform | nearest anchor | center distance | overlap/anchor | overlap/mapped |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in near:
        best = row["bestAnchor"]
        lines.append(
            f"| `O{row['sourceIndex']}: {row['sourceLabel']}` | `{row['transform']}` | `{best['anchor']}` | "
            f"`{best['centerDistance']}` | `{best['intersectionOverAnchor']}` | `{best['intersectionOverMapped']}` |"
        )
    lines.extend(["", "## Positive Overlap Rows", ""])
    if positive:
        for row in positive:
            best = row["bestAnchor"]
            lines.append(f"- `O{row['sourceIndex']}` / `{row['transform']}` -> `{best['anchor']}` overlap anchor `{best['intersectionOverAnchor']}` mapped `{best['intersectionOverMapped']}`")
    else:
        lines.append("- None at the 10% overlap threshold.")
    lines.extend(["", "## Assessment", ""])
    for item in assessment:
        lines.append(f"- {item}")
    lines.extend(["", "## Decision", "", f"- {result['decision']}", "", "## Next Move", "", f"- {result['nextMove']}"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_IMG}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
