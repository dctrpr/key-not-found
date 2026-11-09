#!/usr/bin/env python3
"""Audit shifted paper-texture duplex registration in the current scan.

This bounded pass is a guardrail for the fixed paper-texture duplex gate. It
masks foreground ink/highlight, keeps only paper/background texture, applies the
physical horizontal mirror, and allows a small global page shift. It asks
whether scan slip rescues leaf-pair paper/fiber registration before any text
extraction is considered.

No OCR-to-key extraction, candidate generation, hashing-to-key, seed/WIF/address
checks, BIP39 checks, or brute force is run.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis_outputs/source_audit/current_scan_paper_texture_shift_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_paper_texture_shift_gate.json"
OUT_MD = OUT / "current_scan_paper_texture_shift_gate.md"
OUT_SHEET = OUT / "current_scan_paper_texture_shift_gate_sheet.jpg"

REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAGES = [75, 76, 77, 78, 79, 80]
PHYSICAL_PAIRS = [(75, 76), (77, 78), (79, 80)]
CONTROL_PAIRS = [(75, 78), (75, 80), (76, 77), (76, 79), (77, 80), (78, 79)]
PHYSICAL_TRANSFORM = "hmirror"
SHIFT_VALUES = list(range(-32, 33, 8))
SMALL_SHIFT_LIMIT = 16
SAMPLE_WIDTH = 424
SAMPLE_HEIGHT = 544
MIN_VALID_PIXELS = 5000


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def safe_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size)
            except OSError:
                pass
    return ImageFont.load_default()


def load_page(page: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    path = Path(str(PAGE_TEMPLATE).format(page=page))
    image = Image.open(path).convert("RGB").resize((SAMPLE_WIDTH, SAMPLE_HEIGHT), Image.Resampling.LANCZOS)
    gray = image.convert("L")
    blur = gray.filter(ImageFilter.GaussianBlur(radius=7))
    highpass = np.asarray(gray, dtype=np.float32) - np.asarray(blur, dtype=np.float32)
    rgb = np.asarray(image, dtype=np.float32)
    luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    saturation = rgb.max(axis=2) - rgb.min(axis=2)
    background = (luma > 172.0) & (saturation < 46.0)
    edge_margin = 10
    interior = np.zeros_like(background, dtype=bool)
    interior[edge_margin:-edge_margin, edge_margin:-edge_margin] = True
    background &= interior
    return np.asarray(image, dtype=np.uint8), highpass, background


def hmirror(arr: np.ndarray) -> np.ndarray:
    return np.fliplr(arr)


def shifted_overlap(
    a_hp: np.ndarray,
    a_bg: np.ndarray,
    b_hp: np.ndarray,
    b_bg: np.ndarray,
    dx: int,
    dy: int,
) -> tuple[int, float, float | None]:
    h, w = a_hp.shape
    if dx >= 0:
        ax0, ax1 = dx, w
        bx0, bx1 = 0, w - dx
    else:
        ax0, ax1 = 0, w + dx
        bx0, bx1 = -dx, w
    if dy >= 0:
        ay0, ay1 = dy, h
        by0, by1 = 0, h - dy
    else:
        ay0, ay1 = 0, h + dy
        by0, by1 = -dy, h

    if ax1 <= ax0 or ay1 <= ay0 or bx1 <= bx0 or by1 <= by0:
        return 0, 0.0, None

    a_crop = a_hp[ay0:ay1, ax0:ax1]
    b_crop = b_hp[by0:by1, bx0:bx1]
    a_mask = a_bg[ay0:ay1, ax0:ax1]
    b_mask = b_bg[by0:by1, bx0:bx1]
    mask = a_mask & b_mask
    valid = int(mask.sum())
    union = a_mask | b_mask
    background_iou = float(mask.sum() / union.sum()) if int(union.sum()) else 0.0
    if valid < MIN_VALID_PIXELS:
        return valid, background_iou, None

    av = a_crop[mask].astype(np.float32)
    bv = b_crop[mask].astype(np.float32)
    av -= float(av.mean())
    bv -= float(bv.mean())
    denom = float(np.sqrt(np.sum(av * av) * np.sum(bv * bv)))
    if denom <= 1e-9:
        return valid, background_iou, None
    return valid, background_iou, float(np.sum(av * bv) / denom)


def inspect_pair(
    page_a: int,
    page_b: int,
    class_name: str,
    pages: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    a_hp = pages[page_a]["highpass"]
    a_bg = pages[page_a]["background"]
    b_hp = hmirror(pages[page_b]["highpass"])
    b_bg = hmirror(pages[page_b]["background"])
    for dy in SHIFT_VALUES:
        for dx in SHIFT_VALUES:
            valid, bg_iou, corr = shifted_overlap(a_hp, a_bg, b_hp, b_bg, dx, dy)
            rows.append(
                {
                    "pair": f"{page_a}/{page_b}",
                    "pageA": page_a,
                    "pageB": page_b,
                    "class": class_name,
                    "transform": PHYSICAL_TRANSFORM,
                    "dx": dx,
                    "dy": dy,
                    "chebyshevShiftPx": max(abs(dx), abs(dy)),
                    "manhattanShiftPx": abs(dx) + abs(dy),
                    "validPixelCount": valid,
                    "backgroundIou": round(bg_iou, 6),
                    "paperTextureCorrelation": None if corr is None else round(corr, 6),
                    "isZeroShift": dx == 0 and dy == 0,
                    "isSmallShift": max(abs(dx), abs(dy)) <= SMALL_SHIFT_LIMIT,
                    "isPhysicalLeaf": class_name == "physical_leaf",
                }
            )
    return rows


def add_rank_rows(rows: list[dict[str, Any]]) -> None:
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_pair.setdefault(row["pair"], []).append(row)
    for pair_rows in by_pair.values():
        ranked = sorted(
            pair_rows,
            key=lambda item: -999.0
            if item["paperTextureCorrelation"] is None
            else float(item["paperTextureCorrelation"]),
            reverse=True,
        )
        best = ranked[0]
        for index, row in enumerate(ranked, start=1):
            row["rankWithinPair"] = index
            row["pairBestDx"] = best["dx"]
            row["pairBestDy"] = best["dy"]
            row["pairBestChebyshevShiftPx"] = best["chebyshevShiftPx"]
            row["pairBestCorrelation"] = best["paperTextureCorrelation"]
            row["pairBestBackgroundIou"] = best["backgroundIou"]


def best_rows_by_pair(rows: list[dict[str, Any]], class_name: str) -> list[dict[str, Any]]:
    best: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in sorted(rows, key=lambda item: (item["pair"], item["rankWithinPair"])):
        if row["class"] == class_name and row["rankWithinPair"] == 1 and row["pair"] not in seen:
            best.append(row)
            seen.add(row["pair"])
    return best


def summarize(rows: list[dict[str, Any]], triggers: dict[str, Any]) -> dict[str, Any]:
    add_rank_rows(rows)
    physical_best = best_rows_by_pair(rows, "physical_leaf")
    control_best = best_rows_by_pair(rows, "control_pair")
    control_best_corrs = [
        float(row["paperTextureCorrelation"])
        for row in control_best
        if row["paperTextureCorrelation"] is not None
    ]
    control_best_p95 = float(np.percentile(control_best_corrs, 95)) if control_best_corrs else 0.0
    max_physical_best = max(
        [float(row["paperTextureCorrelation"]) for row in physical_best if row["paperTextureCorrelation"] is not None],
        default=0.0,
    )
    max_control_best = max(control_best_corrs, default=0.0)
    physical_above_control_p95 = sum(
        1
        for row in physical_best
        if row["paperTextureCorrelation"] is not None
        and float(row["paperTextureCorrelation"]) > control_best_p95
    )
    physical_small_shift_best = sum(1 for row in physical_best if row["chebyshevShiftPx"] <= SMALL_SHIFT_LIMIT)
    physical_zero_shift_rows = [
        row for row in rows if row["class"] == "physical_leaf" and row["isZeroShift"]
    ]
    zero_shift_above_control_p95 = sum(
        1
        for row in physical_zero_shift_rows
        if row["paperTextureCorrelation"] is not None
        and float(row["paperTextureCorrelation"]) > control_best_p95
    )
    source_r3 = int(triggers.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(triggers.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(triggers.get("summary", {}).get("triggerCount") or 0)
    selector = bool(
        source_r3 > 0
        and physical_above_control_p95 == len(PHYSICAL_PAIRS)
        and physical_small_shift_best == len(PHYSICAL_PAIRS)
    )
    physical_best_shifts = {
        row["pair"]: {
            "dx": row["dx"],
            "dy": row["dy"],
            "chebyshevShiftPx": row["chebyshevShiftPx"],
            "paperTextureCorrelation": row["paperTextureCorrelation"],
            "backgroundIou": row["backgroundIou"],
        }
        for row in physical_best
    }
    control_best_shifts = {
        row["pair"]: {
            "dx": row["dx"],
            "dy": row["dy"],
            "chebyshevShiftPx": row["chebyshevShiftPx"],
            "paperTextureCorrelation": row["paperTextureCorrelation"],
        }
        for row in control_best
    }
    fingerprint = (
        f"pairs={len(PHYSICAL_PAIRS) + len(CONTROL_PAIRS)}|shifts={len(SHIFT_VALUES) ** 2}|"
        f"rows={len(rows)}|physAboveControlP95={physical_above_control_p95}/{len(PHYSICAL_PAIRS)}|"
        f"physSmallShiftBest={physical_small_shift_best}/{len(PHYSICAL_PAIRS)}|"
        f"zeroShiftAboveControlP95={zero_shift_above_control_p95}/{len(PHYSICAL_PAIRS)}|"
        f"physBestMax={max_physical_best:.4f}|controlBestMax={max_control_best:.4f}|"
        f"controlBestP95={control_best_p95:.4f}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={int(selector)}"
    )
    return {
        "physicalPairCount": len(PHYSICAL_PAIRS),
        "controlPairCount": len(CONTROL_PAIRS),
        "shiftCount": len(SHIFT_VALUES) ** 2,
        "shiftGrid": SHIFT_VALUES,
        "rowCount": len(rows),
        "physicalBestAboveControlBestP95Count": physical_above_control_p95,
        "physicalBestAtSmallShiftCount": physical_small_shift_best,
        "physicalZeroShiftAboveControlBestP95Count": zero_shift_above_control_p95,
        "controlBestCorrelationP95": round(control_best_p95, 6),
        "maxPhysicalBestCorrelation": round(max_physical_best, 6),
        "maxControlBestCorrelation": round(max_control_best, 6),
        "physicalBestShifts": physical_best_shifts,
        "controlBestShifts": control_best_shifts,
        "paperTextureShiftSelectorCandidate": selector,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "paperTextureShiftFingerprint": fingerprint,
    }


def make_sheet(pages: dict[int, dict[str, Any]], rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    panel_w, panel_h = 212, 272
    gap = 20
    header_h = 102
    row_h = 28
    canvas_w = panel_w * 3 + gap * 4
    canvas_h = header_h + panel_h * 2 + gap * 3 + row_h * 13
    canvas = Image.new("RGB", (canvas_w, canvas_h), (244, 244, 240))
    draw = ImageDraw.Draw(canvas)
    title = safe_font(22, True)
    font = safe_font(15)
    small = safe_font(12)
    draw.text((20, 16), "Paper Texture Shift Gate", fill=(25, 25, 25), font=title)
    draw.text(
        (20, 48),
        "Masked paper/background texture. Horizontal mirror plus small global shifts.",
        fill=(70, 70, 70),
        font=font,
    )
    draw.text((20, 72), summary["paperTextureShiftFingerprint"], fill=(70, 70, 70), font=small)

    for idx, page in enumerate(PAGES):
        x = gap + (idx % 3) * (panel_w + gap)
        y = header_h + (idx // 3) * (panel_h + gap)
        img = Image.fromarray(pages[page]["image"]).resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        mask = Image.fromarray((pages[page]["background"].astype(np.uint8) * 255)).resize((panel_w, panel_h), Image.Resampling.NEAREST)
        tint = Image.new("RGB", (panel_w, panel_h), (70, 160, 230))
        img = Image.blend(img, Image.composite(tint, img, mask), 0.35)
        canvas.paste(img, (x, y))
        draw.rectangle([x, y, x + panel_w, y + panel_h], outline=(60, 60, 60), width=1)
        draw.text((x + 8, y + 8), f"page {page}", fill=(10, 10, 10), font=font)

    table_y = header_h + panel_h * 2 + gap * 3
    draw.text((20, table_y), "Physical leaf best shifted rows", fill=(25, 25, 25), font=font)
    table_y += 26
    headers = ["pair", "dx", "dy", "shift", "corr", "bg IoU"]
    xs = [20, 95, 145, 195, 260, 350]
    for x, header in zip(xs, headers):
        draw.text((x, table_y), header, fill=(80, 80, 80), font=small)
    table_y += row_h
    for row in best_rows_by_pair(rows, "physical_leaf"):
        values = [
            row["pair"],
            row["dx"],
            row["dy"],
            row["chebyshevShiftPx"],
            row["paperTextureCorrelation"],
            row["backgroundIou"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, table_y), str(value), fill=(20, 20, 20), font=small)
        table_y += row_h

    table_y += 8
    draw.text((20, table_y), "Control best p95", fill=(80, 80, 80), font=small)
    draw.text((145, table_y), str(summary["controlBestCorrelationP95"]), fill=(20, 20, 20), font=small)
    canvas.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current Scan Paper Texture Shift Gate",
        "",
        "Scope: paper/background-only duplex registration check for current upright page rasters. Foreground text and highlight ink are masked out, then the physical horizontal mirror is allowed a small global shift. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Physical leaf pairs / control pairs: `{summary['physicalPairCount']}` / `{summary['controlPairCount']}`",
        f"- Shift grid: `{summary['shiftGrid'][0]}..{summary['shiftGrid'][-1]}` px in 8 px steps (`{summary['shiftCount']}` shifts per pair)",
        f"- Shift rows: `{summary['rowCount']}`",
        f"- Physical best above control-best p95 rows: `{summary['physicalBestAboveControlBestP95Count']}/{summary['physicalPairCount']}`",
        f"- Physical best at <= {SMALL_SHIFT_LIMIT}px rows: `{summary['physicalBestAtSmallShiftCount']}/{summary['physicalPairCount']}`",
        f"- Physical zero-shift above control-best p95 rows: `{summary['physicalZeroShiftAboveControlBestP95Count']}/{summary['physicalPairCount']}`",
        f"- Physical best max correlation: `{summary['maxPhysicalBestCorrelation']}`",
        f"- Control best max / p95 correlation: `{summary['maxControlBestCorrelation']}` / `{summary['controlBestCorrelationP95']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['paperTextureShiftFingerprint']}`",
        "",
        "## Physical Best Rows",
        "",
        "| pair | dx | dy | shift | corr | bg IoU |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in best_rows_by_pair(result["rows"], "physical_leaf"):
        lines.append(
            f"| `{row['pair']}` | `{row['dx']}` | `{row['dy']}` | `{row['chebyshevShiftPx']}` | `{row['paperTextureCorrelation']}` | `{row['backgroundIou']}` |"
        )
    lines.extend(
        [
            "",
            "## Physical Zero-Shift Rows",
            "",
            "| pair | corr | rank | pair best dx | pair best dy |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in result["rows"]:
        if row["class"] == "physical_leaf" and row["isZeroShift"]:
            lines.append(
                f"| `{row['pair']}` | `{row['paperTextureCorrelation']}` | `{row['rankWithinPair']}` | `{row['pairBestDx']}` | `{row['pairBestDy']}` |"
            )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- `{result['decision']}`.",
            f"- Reason: {result['reason']}",
            f"- Next move: {result['nextMove']}",
            "",
            f"Sheet: `{result['sheet']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    triggers = load_json(REOPEN_TRIGGER_MATRIX)
    pages: dict[int, dict[str, Any]] = {}
    for page in PAGES:
        image, highpass, background = load_page(page)
        pages[page] = {"image": image, "highpass": highpass, "background": background}

    rows: list[dict[str, Any]] = []
    for a, b in PHYSICAL_PAIRS:
        rows.extend(inspect_pair(a, b, "physical_leaf", pages))
    for a, b in CONTROL_PAIRS:
        rows.extend(inspect_pair(a, b, "control_pair", pages))
    summary = summarize(rows, triggers)

    decision = "paper_texture_shift_not_a_selector"
    reason = (
        "Allowing small global shifts after the physical mirror does not produce a source-backed, "
        "all-physical leaf registration rule that separates from shifted controls."
    )
    next_move = (
        "Keep paper/fiber duplex registration closed for the current scan, including small global shift rescue. "
        "Reopen only with a new physical/original-layout source or raw clue wording that names side, mirror, "
        "paper texture, shift/registration, unit, and read order."
    )
    if summary["paperTextureShiftSelectorCandidate"]:
        decision = "paper_texture_shift_requires_source_review"
        reason = "A source-backed shifted paper-texture condition appeared; review manually before any extraction."
        next_move = "Inspect shifted paper texture alignment against the source-reopen gate."

    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "current-scan paper/background texture shifted duplex registration; no extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "pages": [rel(Path(str(PAGE_TEMPLATE).format(page=page))) for page in PAGES],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "physicalPairs": [list(pair) for pair in PHYSICAL_PAIRS],
            "controlPairs": [list(pair) for pair in CONTROL_PAIRS],
            "transform": PHYSICAL_TRANSFORM,
            "shiftGrid": SHIFT_VALUES,
            "smallShiftLimitPx": SMALL_SHIFT_LIMIT,
        },
        "pageSummaries": [
            {
                "page": page,
                "backgroundShare": round(float(pages[page]["background"].mean()), 6),
                "highpassStd": round(float(np.std(pages[page]["highpass"][pages[page]["background"]])), 6),
            }
            for page in PAGES
        ],
        "rows": rows,
        "summary": summary,
        "decision": decision,
        "reason": reason,
        "nextMove": next_move,
        "sheet": rel(OUT_SHEET),
    }
    make_sheet(pages, rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(summary["paperTextureShiftFingerprint"])


if __name__ == "__main__":
    main()
