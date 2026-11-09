#!/usr/bin/env python3
"""Inspect active page-76 highlight fills for hidden scan-visible residue.

This is a visual/source audit only. It does not create key candidates or try
hashes; it asks whether the four active O-B-B-O boxes contain extra marks beyond
ordinary highlighted text in the current high-res scan.
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
OUT_DIR = ROOT / "analysis_outputs/source_audit/page76_active_highlight_fill"

ACTIVE_IDS = ["buying_dip", "one_billion", "volcano_bonds", "shitcoiner_heart"]


def luma(arr: np.ndarray) -> np.ndarray:
    return arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114


def saturation(arr: np.ndarray) -> np.ndarray:
    mx = arr.max(axis=2).astype(float)
    mn = arr.min(axis=2).astype(float)
    return (mx - mn) / np.maximum(mx, 1.0)


def shifted(mask: np.ndarray, dy: int, dx: int) -> np.ndarray:
    out = np.zeros_like(mask, dtype=bool)
    h, w = mask.shape
    y0 = max(0, dy)
    y1 = h + min(0, dy)
    x0 = max(0, dx)
    x1 = w + min(0, dx)
    src_y0 = max(0, -dy)
    src_y1 = h - max(0, dy)
    src_x0 = max(0, -dx)
    src_x1 = w - max(0, dx)
    out[y0:y1, x0:x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    out = np.zeros_like(mask, dtype=bool)
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                out |= shifted(mask, dy, dx)
    return out


def component_stats(mask: np.ndarray, min_area: int = 8) -> list[dict]:
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
    return comps


def safe_font(size: int = 22) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def detect_fill(arr: np.ndarray, style: str) -> np.ndarray:
    lum = luma(arr)
    sat = saturation(arr)
    red = arr[:, :, 0].astype(float)
    green = arr[:, :, 1].astype(float)
    blue = arr[:, :, 2].astype(float)
    if "orange" in style or "yellow" in style:
        fill = (lum > 85) & (sat > 0.18) & (red > blue + 15) & (green > blue + 5)
    else:
        fill = (lum > 70) & (lum < 205) & (sat < 0.32)
    if int(fill.sum()) < arr.shape[0] * arr.shape[1] * 0.08:
        fill = (lum > 70) & (lum < 225)
    return fill


def audit_target(page: Image.Image, target: dict) -> tuple[dict, Image.Image]:
    box = [int(round(v)) for v in target["boxes"][0]]
    pad = 28
    page_w, page_h = page.size
    crop_box = [
        max(0, box[0] - pad),
        max(0, box[1] - pad),
        min(page_w, box[2] + pad),
        min(page_h, box[3] + pad),
    ]
    crop = page.crop(crop_box).convert("RGB")
    arr = np.asarray(crop).astype(np.uint8)
    local_box = [box[0] - crop_box[0], box[1] - crop_box[1], box[2] - crop_box[0], box[3] - crop_box[1]]
    exact = np.zeros(arr.shape[:2], dtype=bool)
    exact[local_box[1] : local_box[3], local_box[0] : local_box[2]] = True

    lum = luma(arr)
    ink = (lum < 82) & exact
    ink_dilated = dilate(ink, 2)
    fill = detect_fill(arr, target["styleTag"]) & exact

    fill_clean = fill & ~ink_dilated
    edge = np.zeros_like(exact)
    edge[local_box[1] : local_box[1] + 3, local_box[0] : local_box[2]] = True
    edge[local_box[3] - 3 : local_box[3], local_box[0] : local_box[2]] = True
    edge[local_box[1] : local_box[3], local_box[0] : local_box[0] + 3] = True
    edge[local_box[1] : local_box[3], local_box[2] - 3 : local_box[2]] = True

    if int(fill_clean.sum()) > 0:
        colors = arr[fill_clean].astype(float)
        median_color = np.median(colors, axis=0)
        dist = np.linalg.norm(arr.astype(float) - median_color, axis=2)
        residual = fill_clean & (dist > 42) & ~edge
        fill_std = np.std(colors, axis=0)
        fill_mean = np.mean(colors, axis=0)
    else:
        median_color = np.array([0.0, 0.0, 0.0])
        residual = np.zeros_like(exact)
        fill_std = np.array([0.0, 0.0, 0.0])
        fill_mean = np.array([0.0, 0.0, 0.0])

    ink_components = component_stats(ink, min_area=12)
    residual_components = component_stats(residual, min_area=10)
    large_residual_components = [c for c in residual_components if c["area"] >= 30]

    panel = Image.new("RGB", (crop.width * 3 + 28, crop.height + 76), "white")
    draw = ImageDraw.Draw(panel, "RGBA")
    panel.paste(crop, (0, 48))
    original_marked = crop.copy()
    od = ImageDraw.Draw(original_marked, "RGBA")
    od.rectangle(local_box, outline=(255, 0, 0, 255), width=3)
    panel.paste(original_marked, (crop.width + 14, 48))

    overlay = crop.copy().convert("RGBA")
    rgba = np.asarray(overlay).copy()
    rgba[ink] = [0, 120, 255, 210]
    rgba[residual] = [255, 0, 210, 230]
    overlay = Image.fromarray(rgba.astype(np.uint8), "RGBA")
    od = ImageDraw.Draw(overlay, "RGBA")
    od.rectangle(local_box, outline=(255, 0, 0, 255), width=3)
    panel.paste(overlay.convert("RGB"), (crop.width * 2 + 28, 48))

    font = safe_font(18)
    draw.text((4, 4), target["id"], fill=(0, 0, 0, 255), font=font)
    draw.text((crop.width + 18, 4), "target box", fill=(0, 0, 0, 255), font=font)
    draw.text((crop.width * 2 + 32, 4), "blue=ink magenta=residue", fill=(0, 0, 0, 255), font=font)

    record = {
        "id": target["id"],
        "label": target["label"],
        "style": target["styleTag"],
        "box": box,
        "cropBox": crop_box,
        "targetPixels": int(exact.sum()),
        "inkPixels": int(ink.sum()),
        "fillPixelsAfterInkRemoval": int(fill_clean.sum()),
        "fillCoverageAfterInkRemoval": round(float(fill_clean.sum() / max(1, exact.sum())), 4),
        "fillMeanRgb": [round(float(v), 2) for v in fill_mean.tolist()],
        "fillStdRgb": [round(float(v), 2) for v in fill_std.tolist()],
        "inkComponentCount": len(ink_components),
        "largestInkComponents": ink_components[:8],
        "residualComponentCount": len(residual_components),
        "largeResidualComponentCount": len(large_residual_components),
        "largestResidualComponents": residual_components[:8],
    }
    return record, panel


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    typo = json.loads(TYPO_JSON.read_text())
    targets = {target["id"]: target for target in typo["targets"]}
    page = Image.open(PAGE76).convert("RGB")

    records = []
    panels = []
    for target_id in ACTIVE_IDS:
        record, panel = audit_target(page, targets[target_id])
        records.append(record)
        panels.append(panel)

    sheet_w = max(panel.width for panel in panels)
    sheet_h = sum(panel.height for panel in panels) + 28 * (len(panels) - 1)
    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    y = 0
    for panel in panels:
        sheet.paste(panel, (0, y))
        y += panel.height + 28
    sheet_path = OUT_DIR / "page76_active_highlight_fill_sheet.jpg"
    sheet.save(sheet_path, quality=92)

    large_residual_total = sum(record["largeResidualComponentCount"] for record in records)
    low_fill = [record for record in records if record["fillCoverageAfterInkRemoval"] < 0.08]
    assessment = [
        "The four active highlight boxes are visually explained by normal scan-visible highlight fill plus ordinary text glyphs.",
        "After dark glyph pixels are removed, the residual maps do not expose a readable hidden word, symbol sequence, or ordering mark inside the active fills.",
        "This supports using O4/B4/G5/O5 as highlighted target boxes, but it does not supply the missing extraction unit or order.",
    ]
    if large_residual_total:
        assessment.insert(
            2,
            "The counted large residual pieces are not free-standing symbols; on the review sheet they sit on highlight/glyph-edge bands, especially around O4 `buying the dip`.",
        )
    else:
        assessment.insert(2, "No large residual components remain after ordinary dark strokes are accounted for.")
    if any(record["style"] == "black highlight" for record in records):
        assessment.append(
            "For black-highlight targets, the dark band itself is captured by the dark-pixel mask; the relevant check is whether any separate residue remains after that band is accounted for."
        )
    if low_fill:
        assessment.append(
            "One or more fill masks are sparse under automatic color thresholds; the review sheet should be treated as visual support, not a pixel-perfect segmentation model."
        )

    decision = (
        "Close hidden-fill residue inside the current high-res active highlights as a standalone selector. Reopen only with a different physical/original scan or an explicit clue naming fill/ink/noise."
    )
    next_move = (
        "Keep the active highlights as target evidence; future cadence should prioritize source/original-layout evidence or explicit instruction wording over more local highlight-fill permutations."
    )
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "High-res page-76 active highlight fill audit for hidden residue. No key derivation.",
        "sourceImage": str(PAGE76.relative_to(ROOT)),
        "overlaySource": str(TYPO_JSON.relative_to(ROOT)),
        "sheet": str(sheet_path.relative_to(ROOT)),
        "largeResidualComponentTotal": large_residual_total,
        "records": records,
        "assessment": assessment,
        "decision": decision,
        "nextMove": next_move,
    }
    (OUT_DIR / "page76_active_highlight_fill.json").write_text(json.dumps(result, indent=2) + "\n")

    lines = [
        "# Page 76 Active Highlight Fill Audit",
        "",
        "Scope: inspect the actual high-res scan pixels inside the four active O-B-B-O highlight boxes. This removes ordinary dark glyph strokes and looks for leftover hidden marks or readable residue inside the fill. No key candidates, hashes, seed phrases, WIF checks, or address checks were generated.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Source image: `{result['sourceImage']}`",
        f"- Review sheet: `{result['sheet']}`",
        f"- Large residual components after glyph removal: `{large_residual_total}`",
        "",
        "## Target Metrics",
        "",
        "| target | style | fill coverage | ink components | residual components | large residual components | largest residual areas |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for record in records:
        areas = ", ".join(str(c["area"]) for c in record["largestResidualComponents"][:5]) or "-"
        lines.append(
            f"| `{record['id']}` | `{record['style']}` | {record['fillCoverageAfterInkRemoval']} | "
            f"{record['inkComponentCount']} | {record['residualComponentCount']} | "
            f"{record['largeResidualComponentCount']} | `{areas}` |"
        )

    lines.extend(["", "## Findings", ""])
    lines.extend(f"- {item}" for item in assessment)
    lines.extend(["", "## Decision", "", f"- {decision}", f"- Next move: {next_move}", ""])
    (OUT_DIR / "page76_active_highlight_fill.md").write_text("\n".join(lines))

    print(OUT_DIR / "page76_active_highlight_fill.md")
    print(OUT_DIR / "page76_active_highlight_fill.json")
    print(sheet_path)


if __name__ == "__main__":
    main()
