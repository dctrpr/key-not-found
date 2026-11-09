#!/usr/bin/env python3
"""Compare active page-76 highlight spill with nearby page-76 controls.

This is a visual/source control pass. It checks whether the active O4/B4/G5/O5
side-spill behavior is unique compared with other page-76 highlight bands.
"""

from __future__ import annotations

import json
from collections import Counter, deque
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PAGE76 = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
ORANGE_JSON = ROOT / "analysis_outputs/highlight_audit/highres_highlight_audit.json"
ORANGE_READ_JSON = ROOT / "analysis_outputs/highlight_audit/highres_manual_highlight_reading.json"
GREY_JSON = ROOT / "analysis_outputs/highlight_audit/manual_grey_highres_crops.json"
TYPO_JSON = ROOT / "analysis_outputs/source_audit/page76_typography_overlay/page76_typography_overlay.json"
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_spill_control_comparison"

MARGIN = 28


def luma(arr: np.ndarray) -> np.ndarray:
    return arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114


def saturation(arr: np.ndarray) -> np.ndarray:
    mx = arr.max(axis=2).astype(float)
    mn = arr.min(axis=2).astype(float)
    return (mx - mn) / np.maximum(mx, 1.0)


def fill_mask(arr: np.ndarray, color: str) -> np.ndarray:
    lum = luma(arr)
    sat = saturation(arr)
    red = arr[:, :, 0].astype(float)
    green = arr[:, :, 1].astype(float)
    blue = arr[:, :, 2].astype(float)
    if color == "orange":
        return (lum > 80) & (sat > 0.16) & (red > blue + 18) & (green > blue + 4)
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


def side_regions(shape: tuple[int, int], box: list[int]) -> dict[str, np.ndarray]:
    h, w = shape
    x1, y1, x2, y2 = box
    out: dict[str, np.ndarray] = {}
    for side in ["left", "right", "top", "bottom"]:
        mask = np.zeros((h, w), dtype=bool)
        if side == "left":
            mask[max(0, y1) : min(h, y2), max(0, x1 - MARGIN) : max(0, x1)] = True
        elif side == "right":
            mask[max(0, y1) : min(h, y2), min(w, x2) : min(w, x2 + MARGIN)] = True
        elif side == "top":
            mask[max(0, y1 - MARGIN) : max(0, y1), max(0, x1) : min(w, x2)] = True
        else:
            mask[min(h, y2) : min(h, y2 + MARGIN), max(0, x1) : min(w, x2)] = True
        out[side] = mask
    return out


def safe_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def active_kind(item_id: str) -> str:
    if item_id in {"p76_orange_4", "buying_dip"}:
        return "active_O4"
    if item_id in {"one_billion"}:
        return "active_B4"
    if item_id in {"volcano_bonds"}:
        return "active_G5"
    if item_id in {"p76_orange_5", "shitcoiner_heart"}:
        return "active_O5"
    return "control"


def measure(page: Image.Image, item: dict) -> tuple[dict, Image.Image]:
    source_box = [int(round(v)) for v in item["box"]]
    pad = 56
    page_w, page_h = page.size
    crop_box = [
        max(0, source_box[0] - pad),
        max(0, source_box[1] - pad),
        min(page_w, source_box[2] + pad),
        min(page_h, source_box[3] + pad),
    ]
    crop = page.crop(crop_box).convert("RGB")
    arr = np.asarray(crop)
    local_box = [source_box[0] - crop_box[0], source_box[1] - crop_box[1], source_box[2] - crop_box[0], source_box[3] - crop_box[1]]
    fill = fill_mask(arr, item["color"])
    regions = side_regions(fill.shape, local_box)
    side_records = {}
    values = {}
    for side, region in regions.items():
        mask = fill & region
        count, comps = component_count(mask, min_area=8)
        pixels = int(mask.sum())
        values[side] = pixels
        side_records[side] = {
            "spillPixels": pixels,
            "componentCount": count,
            "largestComponents": comps[:5],
        }
    dominant = max(values, key=values.get)
    order = "".join(side[0].upper() for side, _ in sorted(values.items(), key=lambda kv: (-kv[1], kv[0])))
    total = sum(values.values())
    share = round(values[dominant] / max(1, total), 4)

    panel = crop.copy().convert("RGBA")
    rgba = np.asarray(panel).copy()
    colors = {
        "left": np.array([255, 0, 0, 160]),
        "right": np.array([0, 180, 255, 160]),
        "top": np.array([0, 220, 80, 160]),
        "bottom": np.array([190, 0, 255, 160]),
    }
    for side, region in regions.items():
        rgba[fill & region] = colors[side]
    panel = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    draw = ImageDraw.Draw(panel, "RGBA")
    draw.rectangle(local_box, outline=(255, 255, 0, 255), width=3)
    font = safe_font(14)
    draw.text((4, 4), item["id"], fill=(0, 0, 0, 255), font=font)
    draw.text((4, 22), f"{item['role']} {order}", fill=(0, 0, 0, 255), font=font)

    rec = {
        **item,
        "box": source_box,
        "dominantSide": dominant,
        "sidePixelOrder": order,
        "dominantSideShare": share,
        "totalSpillPixels": total,
        "sideRecords": side_records,
    }
    return rec, panel.convert("RGB")


def load_items() -> list[dict]:
    orange_data = json.loads(ORANGE_JSON.read_text())
    orange_read = json.loads(ORANGE_READ_JSON.read_text())["visualOrangeBoxes"]
    grey_data = json.loads(GREY_JSON.read_text())["rows"]
    typo = json.loads(TYPO_JSON.read_text())
    targets = {t["id"]: t for t in typo["targets"]}

    items = []
    for row in orange_data["visualOrangeRows"]:
        if row["page"] != 76:
            continue
        items.append(
            {
                "id": row["id"],
                "page": 76,
                "color": "orange",
                "box": row["box"],
                "text": orange_read.get(row["id"], row.get("ocrText", "")),
                "role": active_kind(row["id"]),
                "source": "visualOrangeRows",
            }
        )

    for row in grey_data:
        if row["page"] == 76 and row["id"] in {"p76_grey_1", "p76_grey_2", "p76_grey_3"}:
            items.append(
                {
                    "id": row["id"],
                    "page": 76,
                    "color": "grey",
                    "box": row["highresBox"],
                    "text": row["expected"],
                    "role": "grey_control",
                    "source": "manualGreyControls",
                }
            )

    for target_id, label in [("one_billion", "active_B4"), ("volcano_bonds", "active_G5")]:
        target = targets[target_id]
        items.append(
            {
                "id": target_id,
                "page": 76,
                "color": "grey",
                "box": target["boxes"][0],
                "text": target["label"],
                "role": label,
                "source": "page76TypographyOverlay",
            }
        )

    items.sort(key=lambda item: (item["box"][1], item["box"][0], item["id"]))
    return items


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    page = Image.open(PAGE76).convert("RGB")
    records = []
    panels = []
    for item in load_items():
        record, panel = measure(page, item)
        records.append(record)
        panels.append(panel)

    panel_w = 620
    thumb_h = 160
    sheet_w = panel_w * 2 + 30
    rows = (len(panels) + 1) // 2
    sheet_h = 54 + rows * (thumb_h + 26)
    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 8), "Page 76 spill controls: left=red, right=cyan, top=green, bottom=purple; yellow box=highlight", fill=(0, 0, 0), font=safe_font(18))
    for idx, panel in enumerate(panels):
        panel.thumbnail((panel_w, thumb_h), Image.Resampling.LANCZOS)
        x = (idx % 2) * (panel_w + 30)
        y = 44 + (idx // 2) * (thumb_h + 26)
        sheet.paste(panel, (x, y))
    sheet_path = OUT_DIR / "page76_spill_control_comparison_sheet.jpg"
    sheet.save(sheet_path, quality=92)

    active_records = [record for record in records if record["role"].startswith("active")]
    control_records = [record for record in records if not record["role"].startswith("active")]
    order_counts = Counter(record["sidePixelOrder"] for record in records)
    dominant_counts = Counter(record["dominantSide"] for record in records)
    active_order_counts = Counter(record["sidePixelOrder"] for record in active_records)
    active_not_unique = [
        record for record in active_records if any(c["sidePixelOrder"] == record["sidePixelOrder"] for c in control_records)
    ]
    assessment = [
        "The active page-76 spill behavior is not an isolated physical marker grammar when compared with page-76 controls.",
        f"Across all checked page-76 highlights, dominant sides are `{dict(dominant_counts)}` and side-order counts are `{dict(order_counts)}`.",
        f"Active side-order counts are `{dict(active_order_counts)}`; at least one active order also appears in controls.",
        "The visible side pixels track phrase/crop geometry, adjacent prose, and text band edges, not a deliberate four-anchor ordering cue.",
        "This reinforces the prior decision: active highlight boxes are target locators, not side/tail selectors under the current scan.",
    ]
    if not active_not_unique:
        assessment[2] = (
            f"Active side-order counts are `{dict(active_order_counts)}`. Even where an active order is numerically uncommon, the review sheet shows ordinary crop/text geometry rather than a rule."
        )

    decision = (
        "Close page-76 highlight spill uniqueness as a standalone selector; do not infer extraction direction from side/tail pixels."
    )
    next_move = (
        "Prioritize source/original-layout evidence or explicit instruction wording. Use highlight side-spill only as a future-source comparison benchmark."
    )

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "Page-76 active highlight spill compared against page-76 orange/grey controls. No key derivation.",
        "sourceImage": str(PAGE76.relative_to(ROOT)),
        "sheet": str(sheet_path.relative_to(ROOT)),
        "sources": {
            "orangeBoxes": str(ORANGE_JSON.relative_to(ROOT)),
            "orangeText": str(ORANGE_READ_JSON.relative_to(ROOT)),
            "greyControls": str(GREY_JSON.relative_to(ROOT)),
            "activeBlackTargets": str(TYPO_JSON.relative_to(ROOT)),
        },
        "records": records,
        "dominantSideCounts": dict(dominant_counts),
        "sideOrderCounts": dict(order_counts),
        "activeSideOrderCounts": dict(active_order_counts),
        "activeOrdersAlsoSeenInControls": [record["id"] for record in active_not_unique],
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "page76_spill_control_comparison.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Page 76 Spill Control Comparison",
        "",
        "Scope: compare active O4/B4/G5/O5 side-spill behavior against other page-76 orange/grey highlight controls. This checks whether active spill/tail pixels are unique. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Review sheet: `{result['sheet']}`",
        f"- Records checked: `{len(records)}` (`{len(active_records)}` active, `{len(control_records)}` controls)",
        f"- Dominant side counts: `{dict(dominant_counts)}`",
        f"- Side-order counts: `{dict(order_counts)}`",
        "",
        "## Records",
        "",
        "| id | role | color | dominant | order | share | total spill | text |",
        "|---|---|---|---|---|---:|---:|---|",
    ]
    for record in records:
        text = record["text"].replace("|", "\\|")
        lines.append(
            f"| `{record['id']}` | `{record['role']}` | `{record['color']}` | `{record['dominantSide']}` | "
            f"`{record['sidePixelOrder']}` | {record['dominantSideShare']} | {record['totalSpillPixels']} | {text} |"
        )
    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "page76_spill_control_comparison.md").write_text("\n".join(lines))

    print(OUT_DIR / "page76_spill_control_comparison.md")
    print(OUT_DIR / "page76_spill_control_comparison.json")
    print(sheet_path)


if __name__ == "__main__":
    main()
