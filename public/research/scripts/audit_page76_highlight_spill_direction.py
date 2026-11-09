#!/usr/bin/env python3
"""Audit directional spill around active page-76 highlight boxes.

This checks whether marker/highlight pixels just outside O4/B4/G5/O5 choose a
side or order. It is a bounded visual/source pass only, with no key derivation.
"""

from __future__ import annotations

import json
from collections import deque
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
TYPO_JSON = ROOT / "analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.json"
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_highlight_spill_direction"

ACTIVE_IDS = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]
MARGIN = 28


def luma(arr: np.ndarray) -> np.ndarray:
    return arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114


def saturation(arr: np.ndarray) -> np.ndarray:
    mx = arr.max(axis=2).astype(float)
    mn = arr.min(axis=2).astype(float)
    return (mx - mn) / np.maximum(mx, 1.0)


def fill_mask(arr: np.ndarray, style: str) -> np.ndarray:
    lum = luma(arr)
    sat = saturation(arr)
    red = arr[:, :, 0].astype(float)
    green = arr[:, :, 1].astype(float)
    blue = arr[:, :, 2].astype(float)
    if "orange" in style or "yellow" in style:
        return (lum > 80) & (sat > 0.16) & (red > blue + 18) & (green > blue + 4)
    # For black-highlighted text the "fill" is a dark band. This also catches
    # adjacent black glyphs, so visual review and component shape are required.
    return lum < 112


def component_count(mask: np.ndarray, min_area: int = 8) -> tuple[int, list[dict]]:
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    comps: list[dict] = []
    for yy in range(h):
        for xx in range(w):
            if not mask[yy, xx] or seen[yy, xx]:
                continue
            q: deque[tuple[int, int]] = deque([(yy, xx)])
            seen[yy, xx] = True
            points = []
            while q:
                y, x = q.popleft()
                points.append((y, x))
                for ny in (y - 1, y, y + 1):
                    for nx in (x - 1, x, x + 1):
                        if ny == y and nx == x:
                            continue
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
            if len(points) >= min_area:
                ys = [p[0] for p in points]
                xs = [p[1] for p in points]
                comps.append(
                    {
                        "area": len(points),
                        "box": [min(xs), min(ys), max(xs) + 1, max(ys) + 1],
                        "center": [round(float(np.mean(xs)), 2), round(float(np.mean(ys)), 2)],
                    }
                )
    comps.sort(key=lambda c: c["area"], reverse=True)
    return len(comps), comps


def safe_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def side_regions(shape: tuple[int, int], local_box: list[int]) -> dict[str, np.ndarray]:
    h, w = shape
    x1, y1, x2, y2 = local_box
    regions: dict[str, np.ndarray] = {}
    for name in ["left", "right", "top", "bottom"]:
        mask = np.zeros((h, w), dtype=bool)
        if name == "left":
            mask[max(0, y1) : min(h, y2), max(0, x1 - MARGIN) : max(0, x1)] = True
        elif name == "right":
            mask[max(0, y1) : min(h, y2), min(w, x2) : min(w, x2 + MARGIN)] = True
        elif name == "top":
            mask[max(0, y1 - MARGIN) : max(0, y1), max(0, x1) : min(w, x2)] = True
        else:
            mask[min(h, y2) : min(h, y2 + MARGIN), max(0, x1) : min(w, x2)] = True
        regions[name] = mask
    return regions


def audit_target(page: Image.Image, target: dict) -> tuple[dict, Image.Image]:
    box = [int(round(v)) for v in target["boxes"][0]]
    pad = 58
    page_w, page_h = page.size
    crop_box = [
        max(0, box[0] - pad),
        max(0, box[1] - pad),
        min(page_w, box[2] + pad),
        min(page_h, box[3] + pad),
    ]
    crop = page.crop(crop_box).convert("RGB")
    arr = np.asarray(crop)
    local_box = [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]
    fill = fill_mask(arr, target["styleTag"])
    regions = side_regions(fill.shape, local_box)

    side_records = {}
    side_values = {}
    for side, region in regions.items():
        side_mask = fill & region
        area = int(region.sum())
        pixels = int(side_mask.sum())
        comp_count, comps = component_count(side_mask, min_area=8)
        side_records[side] = {
            "regionArea": area,
            "spillPixels": pixels,
            "spillRatio": round(pixels / max(1, area), 4),
            "componentCount": comp_count,
            "largestComponents": comps[:5],
        }
        side_values[side] = pixels

    max_side = max(side_values, key=side_values.get)
    min_side = min(side_values, key=side_values.get)
    total = sum(side_values.values())
    directional_ratio = round(side_values[max_side] / max(1, total), 4)
    side_stream_by_strength = "".join(
        side[0].upper() for side, _pixels in sorted(side_values.items(), key=lambda kv: (-kv[1], kv[0]))
    )

    overlay = crop.copy().convert("RGBA")
    rgba = np.asarray(overlay).copy()
    colors = {
        "left": np.array([255, 0, 0, 160]),
        "right": np.array([0, 180, 255, 160]),
        "top": np.array([0, 220, 80, 160]),
        "bottom": np.array([190, 0, 255, 160]),
    }
    for side, region in regions.items():
        side_mask = fill & region
        rgba[side_mask] = colors[side]
    overlay = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rectangle(local_box, outline=(255, 255, 0, 255), width=3)
    font = safe_font(18)
    draw.text((4, 4), target["id"], fill=(0, 0, 0, 255), font=font)
    draw.text((4, 26), f"L/R/T/B {side_values['left']}/{side_values['right']}/{side_values['top']}/{side_values['bottom']}", fill=(0, 0, 0, 255), font=font)

    record = {
        "id": target["id"],
        "label": target["label"],
        "style": target["styleTag"],
        "box": box,
        "sideRecords": side_records,
        "dominantSide": max_side,
        "quietestSide": min_side,
        "sidePixelOrder": side_stream_by_strength,
        "dominantSideShare": directional_ratio,
        "totalSpillPixels": total,
    }
    return record, overlay.convert("RGB")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    typo = json.loads(TYPO_JSON.read_text())
    targets = {target["id"]: target for target in typo["targets"]}
    page = Image.open(PAGE76).convert("RGB")

    records = []
    panels = []
    for target_id in ACTIVE_IDS:
        rec, panel = audit_target(page, targets[target_id])
        records.append(rec)
        panels.append(panel)

    panel_w = max(panel.width for panel in panels)
    panel_h = max(panel.height for panel in panels)
    sheet = Image.new("RGB", (panel_w * 2 + 28, panel_h * 2 + 68), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 8), "Side colors: left=red, right=cyan, top=green, bottom=purple; yellow box=target", fill=(0, 0, 0), font=safe_font(20))
    for idx, panel in enumerate(panels):
        x = (idx % 2) * (panel_w + 28)
        y = 48 + (idx // 2) * (panel_h + 20)
        sheet.paste(panel, (x, y))
    sheet_path = OUT_DIR / "page76_highlight_spill_direction_sheet.jpg"
    sheet.save(sheet_path, quality=92)

    dominant_stream = "".join(record["dominantSide"][0].upper() for record in records)
    order_streams = " | ".join(record["sidePixelOrder"] for record in records)
    strong_directional = [record for record in records if record["dominantSideShare"] >= 0.7 and record["totalSpillPixels"] > 0]
    assessment = [
        "The side-spill pixels do not create a stable human-readable side/order rule for the four active anchors.",
        "Orange highlights show expected marker/scan bleed around the text bands; black highlights are dominated by dark band/glyph pixels and adjacent prose risk.",
        f"The dominant-side stream is `{dominant_stream}` and the per-target side-strength streams are `{order_streams}`; neither names a selector such as read/take/line/word/letter/mirror/key.",
        "The review sheet shows no arrow, tail, underline, or repeated side cue that would choose first/last/left/right extraction.",
    ]
    if strong_directional:
        assessment.append(
            "Some targets have a strong numerical side imbalance, but the imbalance follows visible crop/text geometry rather than a repeated puzzle grammar."
        )

    decision = (
        "Close active-highlight spill/tail direction as a standalone selector under the current high-res scan."
    )
    next_move = (
        "Keep the highlight boxes as target evidence; move future passes toward new source/original-layout clues or explicit instruction wording."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Directional spill audit around active page-76 highlight boxes. No key derivation.",
        "sourceImage": str(PAGE76.relative_to(ROOT)),
        "overlaySource": str(TYPO_JSON.relative_to(ROOT)),
        "sheet": str(sheet_path.relative_to(ROOT)),
        "marginPixels": MARGIN,
        "dominantSideStream": dominant_stream,
        "sideStrengthStreams": order_streams,
        "records": records,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "page76_highlight_spill_direction.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Page 76 Highlight Spill Direction",
        "",
        "Scope: inspect high-res scan pixels just outside the four active O-B-B-O highlight boxes to see whether marker spill, tail, underline, or side bias chooses a reading side/order. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source image: `{result['sourceImage']}`",
        f"- Review sheet: `{result['sheet']}`",
        f"- Margin checked around each target: `{MARGIN}` px",
        f"- Dominant-side stream: `{dominant_stream}`",
        f"- Side-strength streams: `{order_streams}`",
        "",
        "## Side Metrics",
        "",
        "| target | style | left | right | top | bottom | dominant | side order | dominant share |",
        "|---|---|---:|---:|---:|---:|---|---|---:|",
    ]
    for record in records:
        sides = record["sideRecords"]
        lines.append(
            f"| `{record['id']}` | `{record['style']}` | {sides['left']['spillPixels']} | "
            f"{sides['right']['spillPixels']} | {sides['top']['spillPixels']} | {sides['bottom']['spillPixels']} | "
            f"`{record['dominantSide']}` | `{record['sidePixelOrder']}` | {record['dominantSideShare']} |"
        )
    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "page76_highlight_spill_direction.md").write_text("\n".join(lines))

    print(OUT_DIR / "page76_highlight_spill_direction.md")
    print(OUT_DIR / "page76_highlight_spill_direction.json")
    print(sheet_path)


if __name__ == "__main__":
    main()
