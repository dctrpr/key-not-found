#!/usr/bin/env python3
"""Audit background paper-texture duplex registration in the current scan.

This bounded pass masks foreground ink/highlight, keeps only paper/background
texture, and compares leaf-pair pages under fixed transforms. It asks whether
physical back-side mirror registration is supported by paper/fiber texture
before any text extraction is considered.

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
OUT = ROOT / "analysis_outputs/source_audit/current_scan_paper_texture_duplex_gate"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "current_scan_paper_texture_duplex_gate.json"
OUT_MD = OUT / "current_scan_paper_texture_duplex_gate.md"
OUT_SHEET = OUT / "current_scan_paper_texture_duplex_gate_sheet.jpg"

REOPEN_TRIGGER_MATRIX = ROOT / (
    "analysis_outputs/source_audit/source_packet_reopen_trigger_matrix/"
    "source_packet_reopen_trigger_matrix.json"
)
PAGE_TEMPLATE = ROOT / "analysis_outputs/3d_article_map/page_{page}_upright.jpg"

PAGES = [75, 76, 77, 78, 79, 80]
PHYSICAL_PAIRS = [(75, 76), (77, 78), (79, 80)]
CONTROL_PAIRS = [(75, 78), (75, 80), (76, 77), (76, 79), (77, 80), (78, 79)]
TRANSFORMS = ["identity", "hmirror", "vmirror", "rot180"]
PHYSICAL_TRANSFORM = "hmirror"
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
    # Background only: keep paper, shadows, and low-saturation print texture;
    # exclude dark letters and orange/black highlight regions.
    background = (luma > 172.0) & (saturation < 46.0)
    edge_margin = 10
    interior = np.zeros_like(background, dtype=bool)
    interior[edge_margin:-edge_margin, edge_margin:-edge_margin] = True
    background &= interior
    return np.asarray(image, dtype=np.uint8), highpass, background


def apply_transform(arr: np.ndarray, name: str) -> np.ndarray:
    if name == "identity":
        return arr
    if name == "hmirror":
        return np.fliplr(arr)
    if name == "vmirror":
        return np.flipud(arr)
    if name == "rot180":
        return np.flipud(np.fliplr(arr))
    raise ValueError(name)


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


def iou(a: np.ndarray, b: np.ndarray) -> float:
    union = a | b
    if int(union.sum()) == 0:
        return 0.0
    return float((a & b).sum() / union.sum())


def inspect_pair(
    page_a: int,
    page_b: int,
    class_name: str,
    pages: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    a_hp = pages[page_a]["highpass"]
    a_bg = pages[page_a]["background"]
    b_hp = pages[page_b]["highpass"]
    b_bg = pages[page_b]["background"]
    for transform in TRANSFORMS:
        tb_hp = apply_transform(b_hp, transform)
        tb_bg = apply_transform(b_bg, transform)
        mask = a_bg & tb_bg
        corr = corrcoef(a_hp, tb_hp, mask)
        rows.append(
            {
                "pair": f"{page_a}/{page_b}",
                "pageA": page_a,
                "pageB": page_b,
                "class": class_name,
                "transform": transform,
                "validPixelCount": int(mask.sum()),
                "backgroundIou": round(iou(a_bg, tb_bg), 6),
                "paperTextureCorrelation": None if corr is None else round(corr, 6),
                "isPhysicalMirror": class_name == "physical_leaf" and transform == PHYSICAL_TRANSFORM,
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
            key=lambda item: -999.0 if item["paperTextureCorrelation"] is None else float(item["paperTextureCorrelation"]),
            reverse=True,
        )
        best_corr = ranked[0]["paperTextureCorrelation"]
        best_transform = ranked[0]["transform"]
        for index, row in enumerate(ranked, start=1):
            row["rankWithinPair"] = index
            row["pairBestTransform"] = best_transform
            row["pairBestCorrelation"] = best_corr


def summarize(rows: list[dict[str, Any]], triggers: dict[str, Any]) -> dict[str, Any]:
    add_rank_rows(rows)
    physical_rows = [row for row in rows if row["class"] == "physical_leaf"]
    physical_mirror_rows = [row for row in physical_rows if row["transform"] == PHYSICAL_TRANSFORM]
    control_rows = [row for row in rows if row["class"] == "control_pair"]
    corr_values = [
        float(row["paperTextureCorrelation"])
        for row in control_rows
        if row["paperTextureCorrelation"] is not None
    ]
    control_p95 = float(np.percentile(corr_values, 95)) if corr_values else 0.0
    phys_best = sum(1 for row in physical_mirror_rows if row["rankWithinPair"] == 1)
    phys_above_control = sum(
        1
        for row in physical_mirror_rows
        if row["paperTextureCorrelation"] is not None
        and float(row["paperTextureCorrelation"]) > control_p95
    )
    physical_best_transforms = {
        row["pair"]: row["pairBestTransform"] for row in physical_mirror_rows
    }
    max_phys_corr = max(
        [float(row["paperTextureCorrelation"]) for row in physical_mirror_rows if row["paperTextureCorrelation"] is not None],
        default=0.0,
    )
    max_control_corr = max(
        [float(row["paperTextureCorrelation"]) for row in control_rows if row["paperTextureCorrelation"] is not None],
        default=0.0,
    )
    source_r3 = int(triggers.get("summary", {}).get("sourceBackedR3BridgeHitCount") or 0)
    satisfied = int(triggers.get("summary", {}).get("satisfiedTriggerCount") or 0)
    trigger_count = int(triggers.get("summary", {}).get("triggerCount") or 0)
    selector = bool(source_r3 > 0 and phys_best == len(PHYSICAL_PAIRS) and phys_above_control == len(PHYSICAL_PAIRS))
    fingerprint = (
        f"pairs={len(PHYSICAL_PAIRS) + len(CONTROL_PAIRS)}|rows={len(rows)}|"
        f"physMirrorBest={phys_best}/{len(PHYSICAL_PAIRS)}|"
        f"physAboveControlP95={phys_above_control}/{len(PHYSICAL_PAIRS)}|"
        f"physMax={max_phys_corr:.4f}|controlMax={max_control_corr:.4f}|"
        f"controlP95={control_p95:.4f}|sourceR3={source_r3}|"
        f"triggers={satisfied}/{trigger_count}|selectors={int(selector)}"
    )
    return {
        "physicalPairCount": len(PHYSICAL_PAIRS),
        "controlPairCount": len(CONTROL_PAIRS),
        "transformCount": len(TRANSFORMS),
        "rowCount": len(rows),
        "physicalMirrorBestPairCount": phys_best,
        "physicalMirrorAboveControlP95Count": phys_above_control,
        "controlCorrelationP95": round(control_p95, 6),
        "maxPhysicalMirrorCorrelation": round(max_phys_corr, 6),
        "maxControlCorrelation": round(max_control_corr, 6),
        "physicalPairBestTransforms": physical_best_transforms,
        "paperDuplexSelectorCandidate": selector,
        "sourceBackedR3BridgeHitCount": source_r3,
        "satisfiedReopenTriggerCount": satisfied,
        "triggerCount": trigger_count,
        "paperTextureDuplexFingerprint": fingerprint,
    }


def make_sheet(pages: dict[int, dict[str, Any]], rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    panel_w, panel_h = 212, 272
    gap = 20
    header_h = 92
    row_h = 28
    canvas_w = panel_w * 3 + gap * 4
    canvas_h = header_h + panel_h * 2 + gap * 3 + row_h * 12
    canvas = Image.new("RGB", (canvas_w, canvas_h), (244, 244, 240))
    draw = ImageDraw.Draw(canvas)
    title = safe_font(22, True)
    font = safe_font(15)
    small = safe_font(12)
    draw.text((20, 16), "Paper Texture Duplex Gate", fill=(25, 25, 25), font=title)
    draw.text(
        (20, 48),
        "Masked paper/background texture only. Physical leaf mirror is compared with controls.",
        fill=(70, 70, 70),
        font=font,
    )
    draw.text((20, 70), summary["paperTextureDuplexFingerprint"], fill=(70, 70, 70), font=small)

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
    draw.text((20, table_y), "Physical leaf rows", fill=(25, 25, 25), font=font)
    table_y += 26
    headers = ["pair", "best", "hmirror corr", "rank", "bg IoU"]
    xs = [20, 95, 170, 305, 365]
    for x, header in zip(xs, headers):
        draw.text((x, table_y), header, fill=(80, 80, 80), font=small)
    table_y += row_h
    physical_mirror_rows = [row for row in rows if row["class"] == "physical_leaf" and row["transform"] == PHYSICAL_TRANSFORM]
    for row in physical_mirror_rows:
        values = [
            row["pair"],
            row["pairBestTransform"],
            row["paperTextureCorrelation"],
            row["rankWithinPair"],
            row["backgroundIou"],
        ]
        for x, value in zip(xs, values):
            draw.text((x, table_y), str(value), fill=(20, 20, 20), font=small)
        table_y += row_h
    canvas.save(OUT_SHEET, quality=92)


def build_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Current Scan Paper Texture Duplex Gate",
        "",
        "Scope: paper/background-only duplex registration check for current upright page rasters. Foreground text and highlight ink are masked out, then high-pass paper texture is compared across fixed transforms. No OCR-to-key extraction, candidate generation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Physical leaf pairs / control pairs: `{summary['physicalPairCount']}` / `{summary['controlPairCount']}`",
        f"- Transform rows: `{summary['rowCount']}`",
        f"- Physical mirror best pair rows: `{summary['physicalMirrorBestPairCount']}/{summary['physicalPairCount']}`",
        f"- Physical mirror above control p95 rows: `{summary['physicalMirrorAboveControlP95Count']}/{summary['physicalPairCount']}`",
        f"- Physical mirror max correlation: `{summary['maxPhysicalMirrorCorrelation']}`",
        f"- Control max / p95 correlation: `{summary['maxControlCorrelation']}` / `{summary['controlCorrelationP95']}`",
        f"- Source-backed R3 hits / satisfied triggers: `{summary['sourceBackedR3BridgeHitCount']}` / `{summary['satisfiedReopenTriggerCount']}/{summary['triggerCount']}`",
        f"- Fingerprint: `{summary['paperTextureDuplexFingerprint']}`",
        "",
        "## Physical Leaf Rows",
        "",
        "| pair | transform | rank | corr | pair best | bg IoU |",
        "|---|---|---:|---:|---|---:|",
    ]
    for row in result["rows"]:
        if row["class"] != "physical_leaf":
            continue
        lines.append(
            f"| `{row['pair']}` | `{row['transform']}` | `{row['rankWithinPair']}` | `{row['paperTextureCorrelation']}` | `{row['pairBestTransform']}` | `{row['backgroundIou']}` |"
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

    decision = "paper_texture_duplex_not_a_selector"
    reason = (
        "Masked paper/background texture does not make the physical back-side mirror the best registration "
        "for all physical leaf pairs, does not beat controls consistently, and still has no source-backed R3 trigger."
    )
    next_move = (
        "Keep paper/fiber duplex registration closed for the current scan. Reopen only with a new physical/original-layout "
        "source that changes duplex registration, or raw clue wording that names paper texture, side, mirror, unit, and read order."
    )
    if summary["paperDuplexSelectorCandidate"]:
        decision = "paper_texture_duplex_requires_source_review"
        reason = "A source-backed all-physical mirror texture condition appeared; review manually before any extraction."
        next_move = "Inspect the source-backed paper texture alignment against the source-reopen gate."

    result = {
        "createdAt": datetime.now().replace(microsecond=0).isoformat(),
        "scope": "current-scan paper/background texture duplex registration; no extraction, candidate generation, broad hashing, seed/WIF/address checks, or brute force",
        "inputs": {
            "pages": [rel(Path(str(PAGE_TEMPLATE).format(page=page))) for page in PAGES],
            "reopenTriggerMatrix": rel(REOPEN_TRIGGER_MATRIX),
            "physicalPairs": [list(pair) for pair in PHYSICAL_PAIRS],
            "controlPairs": [list(pair) for pair in CONTROL_PAIRS],
            "transforms": TRANSFORMS,
            "physicalTransform": PHYSICAL_TRANSFORM,
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
    print(summary["paperTextureDuplexFingerprint"])


if __name__ == "__main__":
    main()
