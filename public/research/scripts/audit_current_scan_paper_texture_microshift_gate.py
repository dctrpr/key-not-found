#!/usr/bin/env python3
"""Audit small global shifts after physical mirror for paper texture.

This follows the fixed paper-texture duplex gate. It keeps only masked
paper/background texture, applies the physical horizontal mirror to the second
page, then searches a bounded +/-32 px global shift grid. The question is
whether a small scan misregistration rescues physical leaf-pair texture before
any text or highlight extraction is considered.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_paper_texture_microshift_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_paper_texture_microshift_gate.json"
OUT_MD = OUT / "current_scan_paper_texture_microshift_gate.md"
OUT_SHEET = OUT / "current_scan_paper_texture_microshift_gate_sheet.jpg"

REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
FIXED_DUPLEX = ROOT / (
    "analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate/"
    "current_scan_paper_texture_duplex_gate.json"
)
PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAGES = [75, 76, 77, 78, 79, 80]
PHYSICAL_PAIRS = [(75, 76), (77, 78), (79, 80)]
CONTROL_PAIRS = [(75, 78), (75, 80), (76, 77), (76, 79), (77, 80), (78, 79)]
SHIFT_VALUES = list(range(-32, 33, 8))
SAMPLE_WIDTH = 424
SAMPLE_HEIGHT = 544
MIN_VALID_PIXELS = 3500


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


def load_page(page: int) -> dict[str, Any]:
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
    return {
        "page": page,
        "image": np.asarray(image, dtype=np.uint8),
        "highpass": highpass,
        "background": background,
        "backgroundShare": round(float(background.mean()), 6),
    }


def hmirror(page: dict[str, Any]) -> dict[str, Any]:
    return {
        "highpass": np.fliplr(page["highpass"]),
        "background": np.fliplr(page["background"]),
    }


def shifted_overlap(
    a_hp: np.ndarray,
    a_bg: np.ndarray,
    b_hp: np.ndarray,
    b_bg: np.ndarray,
    dx: int,
    dy: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    h, w = a_hp.shape
    ax0 = max(0, dx)
    ax1 = min(w, w + dx)
    bx0 = max(0, -dx)
    bx1 = min(w, w - dx)
    ay0 = max(0, dy)
    ay1 = min(h, h + dy)
    by0 = max(0, -dy)
    by1 = min(h, h - dy)
    if ax1 <= ax0 or bx1 <= bx0 or ay1 <= ay0 or by1 <= by0:
        empty = np.array([], dtype=np.float32)
        return empty, empty, np.array([], dtype=bool)
    a_crop = a_hp[ay0:ay1, ax0:ax1]
    b_crop = b_hp[by0:by1, bx0:bx1]
    mask = a_bg[ay0:ay1, ax0:ax1] & b_bg[by0:by1, bx0:bx1]
    return a_crop, b_crop, mask


def corrcoef(a: np.ndarray, b: np.ndarray, mask: np.ndarray) -> float | None:
    if int(mask.sum()) < MIN_VALID_PIXELS:
        return None
    av = a[mask].astype(np.float32)
    bv = b[mask].astype(np.float32)
    av -= float(av.mean())
    bv -= float(bv.mean())
    denom = float(np.sqrt(np.sum(av * av) * np.sum(bv * bv)))
    if denom <= 1e-9:
        return None
    return float(np.sum(av * bv) / denom)


def inspect_pair(a: int, b: int, class_name: str, pages: dict[int, dict[str, Any]]) -> dict[str, Any]:
    page_a = pages[a]
    page_b = hmirror(pages[b])
    shift_rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for dy in SHIFT_VALUES:
        for dx in SHIFT_VALUES:
            a_crop, b_crop, mask = shifted_overlap(
                page_a["highpass"],
                page_a["background"],
                page_b["highpass"],
                page_b["background"],
                dx,
                dy,
            )
            corr = corrcoef(a_crop, b_crop, mask)
            row = {
                "dx": dx,
                "dy": dy,
                "validPixelCount": int(mask.sum()) if mask.size else 0,
                "paperTextureCorrelation": None if corr is None else round(corr, 6),
            }
            shift_rows.append(row)
            if corr is not None and (
                best is None or float(row["paperTextureCorrelation"]) > float(best["paperTextureCorrelation"])
            ):
                best = row
    zero_row = next(row for row in shift_rows if row["dx"] == 0 and row["dy"] == 0)
    if best is None:
        best = {"dx": None, "dy": None, "validPixelCount": 0, "paperTextureCorrelation": None}
    best_corr = best["paperTextureCorrelation"]
    zero_corr = zero_row["paperTextureCorrelation"]
    improvement = None
    if best_corr is not None and zero_corr is not None:
        improvement = round(float(best_corr) - float(zero_corr), 6)
    return {
        "pair": f"{a}/{b}",
        "pageA": a,
        "pageB": b,
        "class": class_name,
        "searchRadiusPx": max(abs(value) for value in SHIFT_VALUES),
        "shiftStepPx": SHIFT_VALUES[1] - SHIFT_VALUES[0],
        "shiftCount": len(shift_rows),
        "zeroShiftCorrelation": zero_corr,
        "bestShift": best,
        "bestVsZeroImprovement": improvement,
        "shiftRows": shift_rows,
    }


def summarize(pair_rows: list[dict[str, Any]], triggers: dict[str, Any], fixed: dict[str, Any]) -> dict[str, Any]:
    physical = [row for row in pair_rows if row["class"] == "physical_leaf"]
    controls = [row for row in pair_rows if row["class"] == "control_pair"]
    control_best = [
        float(row["bestShift"]["paperTextureCorrelation"])
        for row in controls
        if row["bestShift"]["paperTextureCorrelation"] is not None
    ]
    physical_best = [
        float(row["bestShift"]["paperTextureCorrelation"])
        for row in physical
        if row["bestShift"]["paperTextureCorrelation"] is not None
    ]
    control_p95 = float(np.percentile(control_best, 95)) if control_best else 0.0
    physical_above_p95 = sum(value > control_p95 for value in physical_best)
    physical_improved = sum(
        1
        for row in physical
        if row["bestVsZeroImprovement"] is not None
        and float(row["bestVsZeroImprovement"]) > 0.02
    )
    plausible_small_shift_count = sum(
        1
        for row in physical
        if row["bestShift"]["dx"] is not None
        and abs(int(row["bestShift"]["dx"])) <= 16
        and abs(int(row["bestShift"]["dy"])) <= 16
    )
    source_r3 = int(triggers.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(triggers.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(triggers.get("summary", {}).get("triggerCount") or 0)
    selector = bool(
        source_r3 > 0
        and physical_above_p95 == len(physical)
        and plausible_small_shift_count == len(physical)
    )
    max_physical = max(physical_best, default=0.0)
    max_control = max(control_best, default=0.0)
    fingerprint = (
        f"pairs={len(pair_rows)}|shifts={len(SHIFT_VALUES) ** 2}|"
        f"physAboveP95={physical_above_p95}/{len(physical)}|"
        f"physImproved={physical_improved}/{len(physical)}|"
        f"smallShift={plausible_small_shift_count}/{len(physical)}|"
        f"physMax={max_physical:.4f}|controlMax={max_control:.4f}|"
        f"controlP95={control_p95:.4f}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={int(selector)}"
    )
    return {
        "physicalPairCount": len(physical),
        "controlPairCount": len(controls),
        "shiftCountPerPair": len(SHIFT_VALUES) ** 2,
        "totalShiftRows": len(pair_rows) * (len(SHIFT_VALUES) ** 2),
        "shiftRadiusPx": max(abs(value) for value in SHIFT_VALUES),
        "shiftStepPx": SHIFT_VALUES[1] - SHIFT_VALUES[0],
        "physicalAboveControlP95Count": physical_above_p95,
        "physicalBestImprovementOverZeroCount": physical_improved,
        "physicalBestWithinSmallShiftCount": plausible_small_shift_count,
        "maxPhysicalBestCorrelation": round(max_physical, 6),
        "maxControlBestCorrelation": round(max_control, 6),
        "controlBestCorrelationP95": round(control_p95, 6),
        "fixedDuplexFingerprint": fixed.get("summary", {}).get("paperTextureDuplexFingerprint"),
        "paperTextureMicroshiftSelectorCandidate": selector,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "paperTextureMicroshiftFingerprint": fingerprint,
    }


def make_sheet(pages: dict[int, dict[str, Any]], pair_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    panel_w, panel_h = 212, 272
    gap = 18
    header_h = 96
    table_h = 230
    canvas_w = panel_w * 3 + gap * 4
    canvas_h = header_h + panel_h * 2 + gap * 3 + table_h
    canvas = Image.new("RGB", (canvas_w, canvas_h), (244, 244, 240))
    draw = ImageDraw.Draw(canvas)
    title = safe_font(22, True)
    font = safe_font(15)
    small = safe_font(12)
    draw.text((20, 16), "Paper Texture Microshift Gate", fill=(25, 25, 25), font=title)
    draw.text(
        (20, 48),
        "Horizontal mirror + bounded global shift. Blue overlay marks retained paper/background pixels.",
        fill=(70, 70, 70),
        font=font,
    )
    draw.text((20, 70), summary["paperTextureMicroshiftFingerprint"], fill=(70, 70, 70), font=small)

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

    y = header_h + panel_h * 2 + gap * 3
    draw.text((20, y), "Best hmirror+shift rows", fill=(25, 25, 25), font=font)
    y += 28
    headers = ["pair", "class", "best dx,dy", "zero", "best", "gain"]
    xs = [20, 85, 190, 300, 370, 455]
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill=(80, 80, 80), font=small)
    y += 24
    for row in pair_rows:
        best = row["bestShift"]
        vals = [
            row["pair"],
            "phys" if row["class"] == "physical_leaf" else "ctrl",
            f"{best['dx']},{best['dy']}",
            row["zeroShiftCorrelation"],
            best["paperTextureCorrelation"],
            row["bestVsZeroImprovement"],
        ]
        color = (20, 20, 20) if row["class"] == "physical_leaf" else (90, 90, 90)
        for x, val in zip(xs, vals):
            draw.text((x, y), str(val), fill=color, font=small)
        y += 21
    canvas.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current Scan Paper Texture Microshift Gate",
        "",
        "Scope: masked paper/background texture only. The second page is horizontally mirrored, then searched over a bounded +/-32 px global shift grid. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Physical leaf pairs / control pairs: `{summary['physicalPairCount']}` / `{summary['controlPairCount']}`",
        f"- Shift rows per pair / total shift rows: `{summary['shiftCountPerPair']}` / `{summary['totalShiftRows']}`",
        f"- Physical best above control p95 rows: `{summary['physicalAboveControlP95Count']}/{summary['physicalPairCount']}`",
        f"- Physical best improved over zero by >0.02 rows: `{summary['physicalBestImprovementOverZeroCount']}/{summary['physicalPairCount']}`",
        f"- Physical best within +/-16 px rows: `{summary['physicalBestWithinSmallShiftCount']}/{summary['physicalPairCount']}`",
        f"- Max physical/control best correlation: `{summary['maxPhysicalBestCorrelation']}` / `{summary['maxControlBestCorrelation']}`",
        f"- Control best-correlation p95: `{summary['controlBestCorrelationP95']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['paperTextureMicroshiftFingerprint']}`",
        "",
        "## Pair Rows",
        "",
        "| pair | class | zero corr | best corr | best dx | best dy | gain |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in result["pairRows"]:
        best = row["bestShift"]
        lines.append(
            f"| `{row['pair']}` | `{row['class']}` | `{row['zeroShiftCorrelation']}` | `{best['paperTextureCorrelation']}` | `{best['dx']}` | `{best['dy']}` | `{row['bestVsZeroImprovement']}` |"
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
    fixed = load_json(FIXED_DUPLEX)
    pages = {page: load_page(page) for page in PAGES}

    pair_rows: list[dict[str, Any]] = []
    for a, b in PHYSICAL_PAIRS:
        pair_rows.append(inspect_pair(a, b, "physical_leaf", pages))
    for a, b in CONTROL_PAIRS:
        pair_rows.append(inspect_pair(a, b, "control_pair", pages))
    summary = summarize(pair_rows, triggers, fixed)

    decision = "paper_texture_microshift_not_a_selector"
    reason = (
        "Bounded global shifts after physical mirror do not separate physical leaf pairs from controls, "
        "do not keep physical best shifts in a consistent small registration window, and still have no source-backed R3 trigger."
    )
    next_move = (
        "Keep paper-texture microshift rescue closed for the current scan. Reopen only with a distinct physical/original-layout "
        "source or raw clue wording that names side, mirror, paper texture, shift/registration, unit, and read order."
    )
    if summary["paperTextureMicroshiftSelectorCandidate"]:
        decision = "paper_texture_microshift_requires_source_review"
        reason = "A source-backed physical-mirror microshift condition beat controls; review manually before extraction."
        next_move = "Inspect the source-backed microshift evidence against the source-reopen packet."

    compact_pair_rows = []
    for row in pair_rows:
        compact = {key: value for key, value in row.items() if key != "shiftRows"}
        compact["sampleShiftRows"] = [
            item for item in row["shiftRows"] if item["dx"] in {-32, 0, 32} and item["dy"] in {-32, 0, 32}
        ]
        compact_pair_rows.append(compact)

    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "current-scan paper/background texture physical hmirror microshift rescue; no extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "pages": [rel(Path(str(PAGE_TEMPLATE).format(page=page))) for page in PAGES],
            "fixedDuplexGate": rel(FIXED_DUPLEX),
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "physicalPairs": [list(pair) for pair in PHYSICAL_PAIRS],
            "controlPairs": [list(pair) for pair in CONTROL_PAIRS],
            "shiftValues": SHIFT_VALUES,
        },
        "pageSummaries": [
            {
                "page": page,
                "backgroundShare": pages[page]["backgroundShare"],
                "highpassStd": round(float(np.std(pages[page]["highpass"][pages[page]["background"]])), 6),
            }
            for page in PAGES
        ],
        "pairRows": compact_pair_rows,
        "summary": summary,
        "decision": decision,
        "reason": reason,
        "nextMove": next_move,
        "sheet": rel(OUT_SHEET),
    }
    make_sheet(pages, compact_pair_rows, summary)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(build_markdown(result), encoding="utf-8")
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(f"Wrote {rel(OUT_SHEET)}")
    print(summary["paperTextureMicroshiftFingerprint"])


if __name__ == "__main__":
    main()
