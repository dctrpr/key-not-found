#!/usr/bin/env python3
"""Build a current-scan held-to-light simulator from the PDF page images.

This pass treats the existing Bitcoin Magazine PDF/page scan as the source
material, normalizes its extracted page images to the readable/upright frame,
and simulates front/back bleed-through by horizontally mirroring the back page.
It is visual/source geometry only: no OCR extraction, key derivation, hashing,
seed/WIF/address checks, or broad candidate generation.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_held_to_light_simulator"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_held_to_light_simulator.json"
OUT_MD = OUT / "current_scan_held_to_light_simulator.md"
OUT_SHEET = OUT / "current_scan_held_to_light_simulator_sheet.jpg"
OUT_HTML = OUT / "index.html"

ACTIVE_INDEX_SLOT = ROOT / (
    "analysis_outputs/source_audit/source_packet_active_index_slot_control/"
    "source_packet_active_index_slot_control.json"
)
SOURCE_REVIEW_GATE = ROOT / (
    "analysis_outputs/source_audit/source_packet_source_review_gate/"
    "source_packet_source_review_gate.json"
)
REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)

SOURCE_PAGE_TEMPLATE = ROOT / "analysis_outputs/source_images/magazine_page_{page}.jpg"
UPRIGHT_PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

SEARCH_SCALE = 0.25
SHIFT_RANGE_PX = range(-220, 221, 20)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def normalize_pdf_page(page: int) -> Image.Image:
    """Return PDF-extracted page image in readable/upright coordinates."""
    source = Image.open(SOURCE_PAGE_TEMPLATE.with_name(f"magazine_page_{page}.jpg")).convert("RGB")
    upright = Image.open(UPRIGHT_PAGE_TEMPLATE.with_name(f"page_{page}_upright.jpg")).convert("RGB")
    sample_size = (318, 408)
    source_sample = source.resize(sample_size)
    upright_sample = upright.resize(sample_size)
    same_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample, upright_sample)).mean)
    rot_diff = sum(ImageStat.Stat(ImageChops.difference(source_sample.rotate(180), upright_sample)).mean)
    return source.rotate(180) if rot_diff < same_diff else source


try:
    from PIL import ImageChops
except ImportError:  # pragma: no cover
    ImageChops = None


def page_feature_mask(img: Image.Image) -> np.ndarray:
    arr = np.asarray(img.convert("RGB"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mean = (r + g + b) / 3
    dark = mean < 178
    saturated_orange = (r > 125) & (g > 60) & (g < 210) & (b < 145) & (r > g + 15)
    grey_highlight = (mean < 215) & (np.abs(r - g) < 18) & (np.abs(g - b) < 18)
    return dark | saturated_orange | grey_highlight


def resize_mask(mask: np.ndarray, scale: float) -> np.ndarray:
    img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    size = (max(1, round(mask.shape[1] * scale)), max(1, round(mask.shape[0] * scale)))
    return np.asarray(img.resize(size, Image.Resampling.NEAREST)) > 0


def shift_mask(mask: np.ndarray, dx: int, dy: int) -> np.ndarray:
    out = np.zeros_like(mask)
    h, w = mask.shape
    src_x0 = max(0, -dx)
    src_x1 = min(w, w - dx)
    dst_x0 = max(0, dx)
    dst_x1 = min(w, w + dx)
    src_y0 = max(0, -dy)
    src_y1 = min(h, h - dy)
    dst_y0 = max(0, dy)
    dst_y1 = min(h, h + dy)
    if src_x1 > src_x0 and src_y1 > src_y0:
        out[dst_y0:dst_y1, dst_x0:dst_x1] = mask[src_y0:src_y1, src_x0:src_x1]
    return out


def box_mask(size: tuple[int, int], boxes: list[dict], scale: float = 1.0) -> np.ndarray:
    w, h = size
    mask = np.zeros((round(h * scale), round(w * scale)), dtype=bool)
    for item in boxes:
        x0, y0, x1, y1 = item["box"]
        sx0, sy0, sx1, sy1 = [round(v * scale) for v in (x0, y0, x1, y1)]
        mask[max(0, sy0):min(mask.shape[0], sy1), max(0, sx0):min(mask.shape[1], sx1)] = True
    return mask


def overlap_stats(src_mask: np.ndarray, target_mask: np.ndarray) -> dict:
    inter = np.logical_and(src_mask, target_mask).sum()
    union = np.logical_or(src_mask, target_mask).sum()
    src_total = src_mask.sum()
    target_total = target_mask.sum()
    return {
        "jaccard": float(inter / union) if union else 0.0,
        "overSource": float(inter / src_total) if src_total else 0.0,
        "overTarget": float(inter / target_total) if target_total else 0.0,
        "balanced": float((inter / src_total + inter / target_total) / 2) if src_total and target_total else 0.0,
    }


def active_box_coverages(mask: np.ndarray, boxes: list[dict]) -> dict:
    result = {}
    for box in boxes:
        x0, y0, x1, y1 = [round(v) for v in box["box"]]
        crop = mask[y0:y1, x0:x1]
        result[box["shortId"]] = {
            "label": box["phrase"],
            "coverage": float(crop.mean()) if crop.size else 0.0,
        }
    return result


def best_shift_for_global(src_small: np.ndarray, target_small: np.ndarray) -> dict:
    best = {"dx": 0, "dy": 0, "score": -1.0, "stats": {}}
    for dx in SHIFT_RANGE_PX:
        for dy in SHIFT_RANGE_PX:
            shifted = shift_mask(src_small, round(dx * SEARCH_SCALE), round(dy * SEARCH_SCALE))
            stats = overlap_stats(shifted, target_small)
            score = stats["balanced"]
            if score > best["score"]:
                best = {"dx": dx, "dy": dy, "score": score, "stats": stats}
    return best


def best_shift_for_active(src_small: np.ndarray, active_small: np.ndarray) -> dict:
    best = {"dx": 0, "dy": 0, "score": -1.0, "stats": {}}
    for dx in SHIFT_RANGE_PX:
        for dy in SHIFT_RANGE_PX:
            shifted = shift_mask(src_small, round(dx * SEARCH_SCALE), round(dy * SEARCH_SCALE))
            stats = overlap_stats(shifted, active_small)
            score = stats["overTarget"]
            if score > best["score"]:
                best = {"dx": dx, "dy": dy, "score": score, "stats": stats}
    return best


def transform_image(img: Image.Image, dx: int = 0, dy: int = 0) -> Image.Image:
    flipped = ImageOps.mirror(img)
    canvas = Image.new("RGB", img.size, "white")
    canvas.paste(flipped, (dx, dy))
    return canvas


def overlay_image(target: Image.Image, source_transformed: Image.Image, boxes: list[dict], title: str, path: Path) -> None:
    w, h = target.size
    out_w = 720
    out_h = round(out_w * h / w)
    base = target.convert("RGB").resize((out_w, out_h))
    back = source_transformed.convert("RGB").resize((out_w, out_h))
    blend = Image.blend(base, back, 0.42)
    draw = ImageDraw.Draw(blend, "RGBA")
    sx = out_w / w
    sy = out_h / h
    for box in boxes:
        x0, y0, x1, y1 = box["box"]
        rect = [x0 * sx, y0 * sy, x1 * sx, y1 * sy]
        draw.rectangle(rect, outline=(255, 0, 0, 230), width=3)
        draw.text((rect[0], max(0, rect[1] - 18)), box["shortId"], fill=(255, 0, 0, 255))
    draw.rectangle((0, 0, out_w, 34), fill=(0, 0, 0, 165))
    draw.text((10, 9), title, fill=(255, 255, 255, 255))
    blend.save(path, quality=90)


def draw_sheet(rows: list[dict], image_paths: list[Path]) -> None:
    thumb_w, thumb_h = 360, 462
    width, height = 1840, 1240
    sheet = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        title_font = ImageFont.truetype("Arial.ttf", 25)
        small = ImageFont.truetype("Arial.ttf", 15)
        tiny = ImageFont.truetype("Arial.ttf", 12)
    except OSError:
        title_font = ImageFont.load_default()
        small = ImageFont.load_default()
        tiny = ImageFont.load_default()
    draw.rectangle((0, 0, width, 96), fill=(25, 31, 42))
    draw.text((24, 18), "Current-Scan Held-To-Light Simulator", fill="white", font=title_font)
    draw.text((24, 56), "PDF page images normalized to readable/upright; back page is horizontally mirrored like bleed-through.", fill=(235, 235, 235), font=small)

    x, y = 24, 122
    for idx, path in enumerate(image_paths[:10]):
        img = Image.open(path).convert("RGB").resize((thumb_w, thumb_h))
        sheet.paste(img, (x, y))
        x += thumb_w + 18
        if x + thumb_w > width:
            x = 24
            y += thumb_h + 76

    y = 1050
    headers = ["pair", "mode", "dx", "dy", "global", "active", "O4", "B4", "G5", "O5"]
    xs = [24, 168, 330, 390, 458, 548, 638, 728, 818, 908]
    for tx, header in zip(xs, headers):
        draw.text((tx, y), header, fill=(70, 70, 70), font=tiny)
    y += 20
    for row in rows[:8]:
        cover = row.get("activeCoverageByBox", {})
        values = [
            row["pairId"],
            row["mode"],
            str(row["dx"]),
            str(row["dy"]),
            f"{row['globalBalanced']:.3f}",
            f"{row['activeOverTarget']:.3f}" if row["targetPage"] == 76 else "-",
            f"{cover.get('O4', {}).get('coverage', 0.0):.3f}" if cover else "-",
            f"{cover.get('B4', {}).get('coverage', 0.0):.3f}" if cover else "-",
            f"{cover.get('G5', {}).get('coverage', 0.0):.3f}" if cover else "-",
            f"{cover.get('O5', {}).get('coverage', 0.0):.3f}" if cover else "-",
        ]
        for tx, value in zip(xs, values):
            draw.text((tx, y), value, fill=(35, 35, 35), font=tiny)
        y += 20
    sheet.save(OUT_SHEET, quality=92)


def main() -> None:
    active = load_json(ACTIVE_INDEX_SLOT)
    review_gate = load_json(SOURCE_REVIEW_GATE)
    reopen = load_json(REOPEN_TRIGGER_MATRIX)
    active_boxes = [
        {
            "shortId": row["shortId"],
            "id": row["id"],
            "phrase": row["phrase"],
            "box": row["box"],
        }
        for row in active.get("activeRows", [])
    ]

    pages = {page: normalize_pdf_page(page) for page in range(75, 81)}
    masks = {page: page_feature_mask(img) for page, img in pages.items()}
    small_masks = {page: resize_mask(mask, SEARCH_SCALE) for page, mask in masks.items()}
    active_small = box_mask(pages[76].size, active_boxes, SEARCH_SCALE)

    pairs = [
        ("same_leaf_75_to_76", 75, 76, "valid same leaf into page 76"),
        ("same_leaf_76_to_75", 76, 75, "reverse same leaf"),
        ("same_leaf_77_to_78", 77, 78, "valid same leaf"),
        ("same_leaf_78_to_77", 78, 77, "reverse same leaf"),
        ("same_leaf_79_to_80", 79, 80, "valid same leaf"),
        ("same_leaf_80_to_79", 80, 79, "reverse same leaf"),
        ("nonphysical_78_to_76", 78, 76, "visual registration benchmark, not same leaf"),
        ("nonphysical_79_to_76", 79, 76, "visual registration benchmark, not same leaf"),
        ("facing_spread_78_to_79", 78, 79, "facing spread comparison"),
    ]

    rows = []
    image_paths = []
    for pair_id, source_page, target_page, topology in pairs:
        source_mask = np.fliplr(masks[source_page])
        source_small = np.fliplr(small_masks[source_page])
        target_small = small_masks[target_page]
        global_best = best_shift_for_global(source_small, target_small)
        modes = [
            ("natural_hflip", 0, 0),
            ("best_global_feature", global_best["dx"], global_best["dy"]),
        ]
        if target_page == 76:
            active_best = best_shift_for_active(source_small, active_small)
            modes.append(("best_page76_active_boxes", active_best["dx"], active_best["dy"]))

        for mode, dx, dy in modes:
            shifted = shift_mask(source_mask, dx, dy)
            global_stats = overlap_stats(resize_mask(shifted, SEARCH_SCALE), target_small)
            active_stats = overlap_stats(resize_mask(shifted, SEARCH_SCALE), active_small) if target_page == 76 else {}
            source_transformed = transform_image(pages[source_page], dx, dy)
            image_path = OUT / f"{pair_id}_{mode}.jpg"
            overlay_boxes = active_boxes if target_page == 76 else []
            overlay_image(
                pages[target_page],
                source_transformed,
                overlay_boxes,
                f"{pair_id} {mode} dx={dx} dy={dy}",
                image_path,
            )
            if mode in {"natural_hflip", "best_page76_active_boxes"}:
                image_paths.append(image_path)
            rows.append(
                {
                    "pairId": pair_id,
                    "topology": topology,
                    "sourcePage": source_page,
                    "targetPage": target_page,
                    "mode": mode,
                    "dx": dx,
                    "dy": dy,
                    "globalBalanced": global_stats["balanced"],
                    "globalJaccard": global_stats["jaccard"],
                    "activeOverTarget": active_stats.get("overTarget", 0.0),
                    "activeBalanced": active_stats.get("balanced", 0.0),
                    "activeCoverageByBox": active_box_coverages(shifted, active_boxes) if target_page == 76 else {},
                    "image": rel(image_path),
                }
            )

    page76_rows = [row for row in rows if row["targetPage"] == 76]
    natural_75 = next(row for row in rows if row["pairId"] == "same_leaf_75_to_76" and row["mode"] == "natural_hflip")
    best_same_leaf_75 = next(row for row in rows if row["pairId"] == "same_leaf_75_to_76" and row["mode"] == "best_page76_active_boxes")
    best_page76 = max(page76_rows, key=lambda row: row["activeOverTarget"])
    best_global = max(rows, key=lambda row: row["globalBalanced"])
    source_r3 = review_gate.get("summary", {}).get("sourceBackedR3BridgeHitCount", 0) or 0
    triggers = reopen.get("summary", {}).get("satisfiedTriggerCount", 0) or 0
    trigger_count = reopen.get("summary", {}).get("triggerCount", 0) or 0

    summary = {
        "pairCount": len(pairs),
        "modeRowCount": len(rows),
        "naturalSameLeaf75To76ActiveOverTarget": natural_75["activeOverTarget"],
        "bestSameLeaf75To76ActiveOverTarget": best_same_leaf_75["activeOverTarget"],
        "bestSameLeaf75To76Shift": f"{best_same_leaf_75['dx']},{best_same_leaf_75['dy']}",
        "bestPage76ActivePair": best_page76["pairId"],
        "bestPage76ActiveMode": best_page76["mode"],
        "bestPage76ActiveOverTarget": best_page76["activeOverTarget"],
        "bestPage76ActiveShift": f"{best_page76['dx']},{best_page76['dy']}",
        "bestGlobalPair": best_global["pairId"],
        "bestGlobalMode": best_global["mode"],
        "bestGlobalBalanced": best_global["globalBalanced"],
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": triggers,
        "triggerCount": trigger_count,
    }
    summary["heldToLightSimulatorFingerprint"] = (
        f"pairs={summary['pairCount']}|rows={summary['modeRowCount']}|"
        f"sameLeaf75natural={summary['naturalSameLeaf75To76ActiveOverTarget']:.4f}|"
        f"sameLeaf75best={summary['bestSameLeaf75To76ActiveOverTarget']:.4f}@{summary['bestSameLeaf75To76Shift']}|"
        f"bestP76={summary['bestPage76ActivePair']}:{summary['bestPage76ActiveMode']}:"
        f"{summary['bestPage76ActiveOverTarget']:.4f}@{summary['bestPage76ActiveShift']}|"
        f"bestGlobal={summary['bestGlobalPair']}:{summary['bestGlobalBalanced']:.4f}|"
        f"sourceR3={source_r3}|triggers={triggers}/{trigger_count}|selectors=0"
    )

    draw_sheet(rows, image_paths)

    html_images = [
        {
            "label": f"{row['pairId']} / {row['mode']}",
            "src": Path(row["image"]).name,
            "targetPage": row["targetPage"],
            "dx": row["dx"],
            "dy": row["dy"],
            "activeOverTarget": row["activeOverTarget"],
        }
        for row in rows
    ]
    html = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Current-Scan Held-To-Light Simulator</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#111;color:#eee}
header{padding:16px 22px;background:#1f2633}
main{display:grid;grid-template-columns:320px 1fr;gap:18px;padding:18px}
button{display:block;width:100%;margin:4px 0;padding:8px;border:0;background:#2f3a4d;color:#fff;text-align:left;cursor:pointer}
button:hover{background:#43516a}
img{max-width:100%;height:auto;border:1px solid #333}
.meta{font-size:13px;line-height:1.4;color:#ccc}
</style>
</head>
<body>
<header><h1>Current-Scan Held-To-Light Simulator</h1><div>Back pages are horizontally mirrored over PDF-extracted pages normalized to readable/upright orientation.</div></header>
<main><section id="buttons"></section><section><h2 id="label"></h2><img id="view"><p id="meta" class="meta"></p></section></main>
<script>
const images = __IMAGES__;
const buttons = document.getElementById('buttons');
const view = document.getElementById('view');
const label = document.getElementById('label');
const meta = document.getElementById('meta');
function show(i){
  const item = images[i];
  view.src = item.src;
  label.textContent = item.label;
  meta.textContent = `target page ${item.targetPage}; dx=${item.dx}, dy=${item.dy}; active page-76 coverage=${item.activeOverTarget.toFixed(4)}`;
}
images.forEach((item,i)=>{const b=document.createElement('button');b.textContent=item.label;b.onclick=()=>show(i);buttons.appendChild(b);});
show(0);
</script>
</body>
</html>
""".replace("__IMAGES__", json.dumps(html_images))
    OUT_HTML.write_text(html, encoding="utf-8")

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "current PDF/source-image held-to-light simulator; no extraction or candidate generation",
        "inputs": {
            "sourceImages": "analysis_outputs/source_images/magazine_page_75..80.jpg",
            "readableReference": "analysis_outputs/3d_article_map/page_75..80_upright.jpg",
            "activeIndexSlot": rel(ACTIVE_INDEX_SLOT),
            "sourceReviewGate": rel(SOURCE_REVIEW_GATE),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
        },
        "orientation": "PDF-extracted source_images are rotated 180 degrees into readable/upright coordinates before hold-to-light simulation.",
        "rows": rows,
        "summary": summary,
        "decision": {
            "currentScanHeldToLightSimulator": "simulator_created_no_current_selector_unlocked",
            "selectorUnlocked": False,
            "reason": (
                "The simulator makes the current scan usable for visual leaf/spread inspection, "
                "but the physically valid 75->76 same-leaf view does not naturally select the "
                "lower O4/B4/G5/O5 corridor. Forced active-box alignment remains a translation "
                "search, not source-backed unit/order evidence."
            ),
            "nextMove": (
                "Use the simulator for manual visual review and for testing any source clue that "
                "names a page pair or transform. Next automated pass should inspect the PDF object "
                "layout/layer assets for original embedded-image provenance rather than key material."
            ),
        },
        "sheet": rel(OUT_SHEET),
        "htmlSimulator": rel(OUT_HTML),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Current-Scan Held-To-Light Simulator",
        "",
        "Scope: built a visual held-to-light simulator from the existing Bitcoin Magazine PDF/page images. PDF-extracted `source_images` are rotated 180 degrees into readable/upright coordinates, then back pages are horizontally mirrored over target pages. No OCR extraction, key derivation, hashing, seed/WIF/address checks, or broad candidate generation was run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- HTML simulator: `{rel(OUT_HTML)}`",
        f"- Sheet: `{rel(OUT_SHEET)}`",
        f"- Pair/mode rows: `{len(pairs)}` / `{len(rows)}`",
        f"- Natural same-leaf 75->76 active coverage: `{natural_75['activeOverTarget']:.4f}`",
        f"- Best bounded same-leaf 75->76 active coverage: `{best_same_leaf_75['activeOverTarget']:.4f}` at dx/dy `{best_same_leaf_75['dx']},{best_same_leaf_75['dy']}`",
        f"- Best page-76 active overlay: `{best_page76['pairId']}` / `{best_page76['mode']}` at active coverage `{best_page76['activeOverTarget']:.4f}` with dx/dy `{best_page76['dx']},{best_page76['dy']}`",
        f"- Best global feature overlay: `{best_global['pairId']}` / `{best_global['mode']}` balanced `{best_global['globalBalanced']:.4f}`",
        f"- Source-backed R3 / satisfied triggers: `{source_r3}` / `{triggers}/{trigger_count}`",
        f"- Fingerprint: `{summary['heldToLightSimulatorFingerprint']}`",
        "",
        "## Page-76 Rows",
        "",
        "| pair | mode | dx | dy | active coverage | O4 | B4 | G5 | O5 | image |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in page76_rows:
        cover = row["activeCoverageByBox"]
        lines.append(
            "| {pair} | `{mode}` | {dx} | {dy} | {active:.4f} | {o4:.4f} | {b4:.4f} | {g5:.4f} | {o5:.4f} | `{image}` |".format(
                pair=row["pairId"],
                mode=row["mode"],
                dx=row["dx"],
                dy=row["dy"],
                active=row["activeOverTarget"],
                o4=cover.get("O4", {}).get("coverage", 0.0),
                b4=cover.get("B4", {}).get("coverage", 0.0),
                g5=cover.get("G5", {}).get("coverage", 0.0),
                o5=cover.get("O5", {}).get("coverage", 0.0),
                image=row["image"],
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']['currentScanHeldToLightSimulator']}`",
            f"- {result['decision']['reason']}",
            f"- {result['decision']['nextMove']}",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
