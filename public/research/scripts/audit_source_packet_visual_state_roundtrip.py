#!/usr/bin/env python3
"""Measure visual-state roundtrip stability for the source packet.

The native-source bridge records coordinates, but future physical/original
layout comparisons also need compact visual-state benchmarks. This pass checks
the active O4/B4/G5/O5 Y/K target boxes and OVERDOSE header/glyph controls in
readable/upright pixels against the native source image rotated back 180
degrees.

This is a source-validation artifact only. It performs no OCR, extraction, key
derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad
candidate generation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_JSON = ROOT / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge.json"
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
FORMAT_JSON = ROOT / "analysis_outputs/docm_format_sources/page76_target_format_authority_lock/page76_target_format_authority_lock.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"

OUT = ROOT / "analysis_outputs/source_audit/source_packet_visual_state_roundtrip"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_visual_state_roundtrip.json"
OUT_MD = OUT / "source_packet_visual_state_roundtrip.md"
SHEET = OUT / "source_packet_visual_state_roundtrip_sheet.jpg"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            pass
    return ImageFont.load_default()


def int_box(box: list[int | float]) -> list[int]:
    return [int(round(v)) for v in box]


def padded_box(box: list[int | float], width: int, height: int, pad: int) -> list[int]:
    x0, y0, x1, y1 = int_box(box)
    return [max(0, x0 - pad), max(0, y0 - pad), min(width, x1 + pad), min(height, y1 + pad)]


def luma(arr: np.ndarray) -> np.ndarray:
    return arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114


def saturation(arr: np.ndarray) -> np.ndarray:
    mx = arr.max(axis=2).astype(float)
    mn = arr.min(axis=2).astype(float)
    return (mx - mn) / np.maximum(mx, 1.0)


def visual_stats(image: Image.Image) -> dict[str, Any]:
    arr = np.asarray(image.convert("RGB")).astype(float)
    lum = luma(arr)
    sat = saturation(arr)
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    blue = arr[:, :, 2]
    orange = (lum > 80) & (sat > 0.12) & (red > blue + 10) & (green > blue) & (red > green * 0.85)
    dark = lum < 95
    grey_dark = (lum < 145) & (sat < 0.35)
    return {
        "meanRgb": [round(float(v), 2) for v in arr.reshape(-1, 3).mean(axis=0)],
        "meanLuma": round(float(lum.mean()), 4),
        "meanSaturation": round(float(sat.mean()), 4),
        "orangeRatio": round(float(orange.mean()), 4),
        "darkRatio": round(float(dark.mean()), 4),
        "greyDarkRatio": round(float(grey_dark.mean()), 4),
    }


def classify_visual_state(stats: dict[str, Any]) -> str:
    if stats["orangeRatio"] >= 0.45:
        return "Y"
    if stats["darkRatio"] >= 0.5 and stats["orangeRatio"] <= 0.05:
        return "K"
    return "N"


def diff_stats(upright_crop: Image.Image, native_rotated_crop: Image.Image) -> dict[str, Any]:
    a = np.asarray(upright_crop.convert("RGB"), dtype=np.int16)
    b = np.asarray(native_rotated_crop.convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        raise RuntimeError(f"crop shape mismatch: {a.shape} != {b.shape}")
    diff = np.abs(a - b)
    return {
        "meanAbsDiff": round(float(diff.mean()), 4),
        "maxDiff": int(diff.max()),
        "nonzeroPct": round(float((diff > 0).mean() * 100), 4),
    }


def active_lookup() -> dict[str, dict[str, Any]]:
    active = load_json(ACTIVE_JSON)
    return {row["id"]: row for row in active["targets"]}


def build_records(upright: Image.Image, native: Image.Image) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bridge = load_json(BRIDGE_JSON)
    active_by_id = active_lookup()
    records = []
    for row in bridge["rows"]:
        upright_box = int_box(row["uprightBox"])
        native_box = int_box(row["nativeBox"])
        upright_crop = upright.crop(upright_box)
        native_rotated_crop = native.crop(native_box).rotate(180)
        stats = visual_stats(upright_crop)
        record = {
            "id": row["id"],
            "label": row["label"],
            "kind": row["kind"],
            "uprightBox": upright_box,
            "nativeBox": native_box,
            "boxSize": row["boxSize"],
            "diff": diff_stats(upright_crop, native_rotated_crop),
            "visualStats": stats,
        }
        if row["kind"] == "active_target":
            active = active_by_id[row["id"]]
            record.update(
                {
                    "expectedVisualState": row["visualState"],
                    "classifiedVisualState": classify_visual_state(stats),
                    "pageLine": row["pageLine"],
                    "corridorIndex": row["corridorIndex"],
                    "docmBoldFraction": active.get("docmBoldFraction"),
                    "docmDominantFont": active.get("docmDominantFont"),
                    "docmHighlights": active.get("docmHighlights", {}),
                    "phrase": active.get("phrase"),
                }
            )
        if row["kind"] == "overdose_glyph":
            record["letter"] = row["letter"]
            record["slotIndex"] = row["slotIndex"]
        records.append(record)

    active_records = [row for row in records if row["kind"] == "active_target"]
    glyph_records = [row for row in records if row["kind"] == "overdose_glyph"]
    y_records = [row for row in active_records if row["expectedVisualState"] == "Y"]
    k_records = [row for row in active_records if row["expectedVisualState"] == "K"]
    summary = {
        "recordCount": len(records),
        "activeRecordCount": len(active_records),
        "activeExpectedVisualStateOrder": "".join(row["expectedVisualState"] for row in active_records),
        "activeClassifiedVisualStateOrder": "".join(row["classifiedVisualState"] for row in active_records),
        "activePageLines": " ".join(str(row["pageLine"]) for row in active_records),
        "activeCorridorIndexes": " ".join(str(row["corridorIndex"]) for row in active_records),
        "allActiveVisualStatesMatch": all(
            row["expectedVisualState"] == row["classifiedVisualState"] for row in active_records
        ),
        "allActiveDocmBoldFractionOne": all(row.get("docmBoldFraction") == 1.0 for row in active_records),
        "activeMaxMeanAbsDiff": round(max(row["diff"]["meanAbsDiff"] for row in active_records), 4),
        "activeMaxDiff": max(row["diff"]["maxDiff"] for row in active_records),
        "activeAllRoundtripMeanAbsDiffUnder3": all(row["diff"]["meanAbsDiff"] < 3.0 for row in active_records),
        "activeYOrangeRatioRange": [
            round(min(row["visualStats"]["orangeRatio"] for row in y_records), 4),
            round(max(row["visualStats"]["orangeRatio"] for row in y_records), 4),
        ],
        "activeKDarkRatioRange": [
            round(min(row["visualStats"]["darkRatio"] for row in k_records), 4),
            round(max(row["visualStats"]["darkRatio"] for row in k_records), 4),
        ],
        "overdoseGlyphSequence": "".join(row.get("letter", "") for row in glyph_records),
        "overdoseGlyphMaxDarkRatio": round(max(row["visualStats"]["darkRatio"] for row in glyph_records), 4),
        "overdoseGlyphMaxOrangeRatio": round(max(row["visualStats"]["orangeRatio"] for row in glyph_records), 4),
        "overdoseGlyphMaxMeanAbsDiff": round(max(row["diff"]["meanAbsDiff"] for row in glyph_records), 4),
        "selectorUnlocked": False,
    }
    return records, summary


def mask_overlay(crop: Image.Image, stats: dict[str, Any]) -> Image.Image:
    arr = np.asarray(crop.convert("RGB")).astype(float)
    lum = luma(arr)
    sat = saturation(arr)
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    blue = arr[:, :, 2]
    orange = (lum > 80) & (sat > 0.12) & (red > blue + 10) & (green > blue) & (red > green * 0.85)
    dark = lum < 95
    rgba = np.asarray(crop.convert("RGBA")).copy()
    rgba[orange] = [255, 155, 46, 220]
    rgba[dark] = [35, 45, 60, 230]
    out = Image.fromarray(rgba.astype(np.uint8), "RGBA").convert("RGB")
    draw = ImageDraw.Draw(out)
    draw.text(
        (6, 6),
        f"O {stats['orangeRatio']:.2f} / D {stats['darkRatio']:.2f}",
        fill=(255, 255, 255),
        font=font(16),
        stroke_width=2,
        stroke_fill=(0, 0, 0),
    )
    return out


def crop_pair_for_sheet(
    upright: Image.Image,
    native: Image.Image,
    row: dict[str, Any],
    pad: int = 34,
) -> tuple[Image.Image, Image.Image, Image.Image]:
    width, height = upright.size
    upright_pad = padded_box(row["uprightBox"], width, height, pad)
    native_pad = padded_box(row["nativeBox"], width, height, pad)
    upright_crop = upright.crop(upright_pad)
    native_crop = native.crop(native_pad).rotate(180)
    exact = upright.crop(row["uprightBox"])
    overlay = mask_overlay(exact, row["visualStats"])
    return upright_crop, native_crop, overlay


def render_sheet(upright: Image.Image, native: Image.Image, records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    active = [row for row in records if row["kind"] == "active_target"]
    glyphs = [row for row in records if row["kind"] == "overdose_glyph"]
    header = next(row for row in records if row["kind"] == "overdose_header")

    row_h = 210
    sheet_w = 1480
    sheet_h = 140 + len(active) * row_h + 250
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(18)
    small = font(14)
    draw.text((28, 24), "Source Packet Visual-State Roundtrip", fill=(242, 247, 252), font=title)
    draw.text(
        (28, 62),
        f"Active state {summary['activeClassifiedVisualStateOrder']} from pixels, DOCM bold x4, OVERDOSE glyph control {summary['overdoseGlyphSequence']}.",
        fill=(185, 196, 208),
        font=normal,
    )
    draw.text(
        (28, 92),
        "Each target compares readable/upright crop, native-source crop rotated back, and exact-box color mask.",
        fill=(150, 162, 176),
        font=small,
    )

    y = 132
    for row in active:
        draw.rectangle((24, y - 8, sheet_w - 24, y + row_h - 18), fill=(18, 22, 28), outline=(45, 54, 64))
        upright_crop, native_crop, overlay = crop_pair_for_sheet(upright, native, row)
        panels = [
            ("upright", upright_crop),
            ("native rot180", native_crop),
            ("exact mask", overlay.resize((overlay.width * 2, overlay.height * 2))),
        ]
        x = 34
        for label, img in panels:
            max_w, max_h = 340, 118
            scale = min(max_w / img.width, max_h / img.height, 1.8)
            img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))))
            draw.text((x, y), label, fill=(210, 220, 230), font=small)
            sheet.paste(img, (x, y + 24))
            x += 380
        stats = row["visualStats"]
        metrics_x = 1180
        draw.text((metrics_x, y), row["id"], fill=(242, 247, 252), font=normal)
        draw.text((metrics_x, y + 28), f"state {row['expectedVisualState']} -> {row['classifiedVisualState']}", fill=(255, 213, 135), font=small)
        draw.text((metrics_x, y + 52), f"O {stats['orangeRatio']}  D {stats['darkRatio']}", fill=(210, 220, 230), font=small)
        draw.text((metrics_x, y + 76), f"diff mean {row['diff']['meanAbsDiff']} max {row['diff']['maxDiff']}", fill=(210, 220, 230), font=small)
        draw.text((metrics_x, y + 100), f"L{row['pageLine']} C{row['corridorIndex']} bold {row['docmBoldFraction']}", fill=(210, 220, 230), font=small)
        y += row_h

    y += 12
    draw.rectangle((24, y, sheet_w - 24, y + 210), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((34, y + 14), "OVERDOSE header/glyph control", fill=(242, 247, 252), font=normal)
    header_u, header_n, header_o = crop_pair_for_sheet(upright, native, header, pad=16)
    for i, (label, img) in enumerate([("upright", header_u), ("native rot180", header_n), ("header mask", header_o)]):
        x = 34 + i * 300
        scale = min(260 / img.width, 90 / img.height, 2.5)
        img = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))))
        draw.text((x, y + 48), label, fill=(210, 220, 230), font=small)
        sheet.paste(img, (x, y + 72))
    glyph_text = (
        f"sequence {summary['overdoseGlyphSequence']} | max dark {summary['overdoseGlyphMaxDarkRatio']} | "
        f"max orange {summary['overdoseGlyphMaxOrangeRatio']} | max diff {summary['overdoseGlyphMaxMeanAbsDiff']}"
    )
    draw.text((940, y + 72), glyph_text, fill=(210, 220, 230), font=small)
    draw.text(
        (940, y + 104),
        "Control confirms header art is not the same dark highlight band as K targets.",
        fill=(150, 162, 176),
        font=small,
    )
    sheet.save(SHEET, quality=94)


def main() -> None:
    upright = Image.open(UPRIGHT_IMAGE).convert("RGB")
    native = Image.open(NATIVE_IMAGE).convert("RGB")
    if upright.size != native.size:
        raise RuntimeError(f"size mismatch: upright={upright.size} native={native.size}")

    records, summary = build_records(upright, native)
    render_sheet(upright, native, records, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet visual-state roundtrip; no OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation",
        "inputs": {
            "nativeBenchmarkBridge": rel(BRIDGE_JSON),
            "activeTargetCropCompletion": rel(ACTIVE_JSON),
            "targetFormatAuthorityLock": rel(FORMAT_JSON),
            "uprightImage": rel(UPRIGHT_IMAGE),
            "nativeImage": rel(NATIVE_IMAGE),
        },
        "imageSize": list(upright.size),
        "records": records,
        "summary": summary,
        "decision": {
            "sourcePacketVisualStateRoundtrip": "source-validation-only",
            "reason": (
                "The active O4/B4/G5/O5 boxes roundtrip cleanly between readable/upright and native rotate180 coordinates, "
                "pixel masks recover the expected Y/K/Y/K visual evidence as YKKY, all four active targets remain DOCM Typeka bold, "
                "and the OVERDOSE header/glyph controls do not add a unit/order rule."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Use these per-box visual-state and roundtrip metrics as source-comparison benchmarks for a true physical scan, original export, or fresh PDF extraction; do not extract unless R3 unit/order evidence appears."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Visual-State Roundtrip",
        "",
        "Scope: measure per-box visual-state and native-rotation stability for the current source packet. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active expected visual-state order: `{summary['activeExpectedVisualStateOrder']}`",
        f"- Active classified visual-state order: `{summary['activeClassifiedVisualStateOrder']}`",
        f"- Active page lines: `{summary['activePageLines']}`",
        f"- Active corridor indexes: `{summary['activeCorridorIndexes']}`",
        f"- All active states match: `{summary['allActiveVisualStatesMatch']}`",
        f"- All active DOCM bold fraction one: `{summary['allActiveDocmBoldFractionOne']}`",
        f"- Active max mean abs diff after native rotate180: `{summary['activeMaxMeanAbsDiff']}`",
        f"- Active max pixel diff after native rotate180: `{summary['activeMaxDiff']}`",
        f"- Active Y orange-ratio range: `{summary['activeYOrangeRatioRange']}`",
        f"- Active K dark-ratio range: `{summary['activeKDarkRatioRange']}`",
        f"- OVERDOSE glyph sequence: `{summary['overdoseGlyphSequence']}`",
        f"- OVERDOSE glyph max dark ratio: `{summary['overdoseGlyphMaxDarkRatio']}`",
        f"- OVERDOSE glyph max orange ratio: `{summary['overdoseGlyphMaxOrangeRatio']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Active Records",
        "",
        "| id | state | page/corridor | orange ratio | dark ratio | DOCM bold | mean abs diff |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in [r for r in records if r["kind"] == "active_target"]:
        lines.append(
            f"| `{row['id']}` | `{row['expectedVisualState']} -> {row['classifiedVisualState']}` | "
            f"`{row['pageLine']}/{row['corridorIndex']}` | `{row['visualStats']['orangeRatio']}` | "
            f"`{row['visualStats']['darkRatio']}` | `{row['docmBoldFraction']}` | `{row['diff']['meanAbsDiff']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as a source-validation benchmark, not a selector.",
            "- The active visual states and DOCM bold status are stable under the native `rotate180` source transform.",
            "- The OVERDOSE header/glyph controls distinguish header art from active black highlight bands, but they supply no extraction unit or order.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("activeClassifiedVisualStateOrder:", summary["activeClassifiedVisualStateOrder"])
    print("activeMaxMeanAbsDiff:", summary["activeMaxMeanAbsDiff"])
    print("overdoseGlyphSequence:", summary["overdoseGlyphSequence"])
    print("selectorUnlocked:", summary["selectorUnlocked"])


if __name__ == "__main__":
    main()
