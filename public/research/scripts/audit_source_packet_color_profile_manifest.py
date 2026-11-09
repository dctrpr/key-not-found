#!/usr/bin/env python3
"""Build a color-profile manifest for the current source packet.

This bounded pass records active O4/B4/G5/O5 orange/black visual profiles and
OVERDOSE header/glyph controls as future source-comparison benchmarks.

It is not a selector. It performs no OCR, extraction, key derivation, hashing,
seed/WIF checks, address checks, BIP39 checks, or broad candidate generation.
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
VISUAL_JSON = ROOT / "analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip.json"
ALIGNMENT_JSON = ROOT / "analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"

OUT = ROOT / "analysis_outputs/source_audit/source_packet_color_profile_manifest"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_color_profile_manifest.json"
OUT_MD = OUT / "source_packet_color_profile_manifest.md"
SHEET = OUT / "source_packet_color_profile_manifest_sheet.jpg"


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


def rot180_box(box: list[int | float], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = int_box(box)
    return [width - x1, height - y1, width - x0, height - y0]


def luma(arr: np.ndarray) -> np.ndarray:
    return arr[:, :, 0] * 0.299 + arr[:, :, 1] * 0.587 + arr[:, :, 2] * 0.114


def saturation(arr: np.ndarray) -> np.ndarray:
    mx = arr.max(axis=2).astype(float)
    mn = arr.min(axis=2).astype(float)
    return (mx - mn) / np.maximum(mx, 1.0)


def crop_stats(image: Image.Image) -> dict[str, Any]:
    arr = np.asarray(image.convert("RGB"), dtype=float)
    lum = luma(arr)
    sat = saturation(arr)
    red = arr[:, :, 0]
    green = arr[:, :, 1]
    blue = arr[:, :, 2]
    orange = (lum > 80) & (sat > 0.12) & (red > blue + 10) & (green > blue) & (red > green * 0.85)
    dark = lum < 95
    grey_dark = (lum < 145) & (sat < 0.35)
    flat = arr.reshape(-1, 3)
    mean_rgb = [round(float(v), 3) for v in flat.mean(axis=0)]
    median_rgb = [round(float(v), 3) for v in np.median(flat, axis=0)]
    p10, p50, p90 = np.percentile(lum, [10, 50, 90])
    return {
        "meanRgb": mean_rgb,
        "medianRgb": median_rgb,
        "meanLuma": round(float(lum.mean()), 4),
        "medianLuma": round(float(p50), 4),
        "lumaP10": round(float(p10), 4),
        "lumaP90": round(float(p90), 4),
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


def diff_stats(a: Image.Image, b: Image.Image) -> dict[str, Any]:
    aa = np.asarray(a.convert("RGB"), dtype=np.int16)
    bb = np.asarray(b.convert("RGB"), dtype=np.int16)
    diff = np.abs(aa - bb)
    return {
        "meanAbsDiff": round(float(diff.mean()), 4),
        "maxDiff": int(diff.max()),
    }


def build_records(upright: Image.Image, native: Image.Image, bridge: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    width, height = upright.size
    for row in bridge["rows"]:
        if row["kind"] not in {"active_target", "overdose_header", "overdose_glyph"}:
            continue
        box = int_box(row["uprightBox"])
        native_box = row.get("nativeBox") or rot180_box(box, width, height)
        native_box = int_box(native_box)
        upright_crop = upright.crop(box)
        native_crop = native.crop(native_box).rotate(180)
        stats = crop_stats(upright_crop)
        native_stats = crop_stats(native_crop)
        records.append(
            {
                "id": row["id"],
                "label": row["label"],
                "kind": row["kind"],
                "letter": row.get("letter"),
                "slotIndex": row.get("slotIndex"),
                "expectedVisualState": row.get("visualState", "N"),
                "classifiedVisualState": classify_visual_state(stats),
                "uprightBox": box,
                "nativeBox": native_box,
                "stats": stats,
                "nativeRotatedStats": native_stats,
                "roundtripDiff": diff_stats(upright_crop, native_crop),
            }
        )
    return records


def range_or_none(values: list[float]) -> list[float] | None:
    if not values:
        return None
    return [round(min(values), 4), round(max(values), 4)]


def render_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    sheet = Image.new("RGB", (1560, 1120), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(18)
    small = font(14)
    mono = font(15)
    draw.text((28, 24), "Source Packet Color Profile Manifest", fill=(242, 247, 252), font=title)
    draw.text(
        (28, 62),
        "Active orange/black target profiles and OVERDOSE controls for future source matching only.",
        fill=(178, 190, 204),
        font=normal,
    )

    active = [row for row in records if row["kind"] == "active_target"]
    controls = [row for row in records if row["kind"] != "active_target"]
    y = 114
    draw.rectangle((28, y, 1532, y + 340), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 16), "Active target color profiles", fill=(242, 247, 252), font=normal)
    headers = [("id", 44), ("state", 310), ("mean RGB", 405), ("luma p10/50/90", 640), ("orange", 905), ("dark", 1020), ("native diff", 1135)]
    for label, x in headers:
        draw.text((x, y + 52), label, fill=(144, 157, 173), font=small)
    for idx, row in enumerate(active):
        row_y = y + 84 + idx * 60
        color = tuple(int(round(v)) for v in row["stats"]["medianRgb"])
        draw.rectangle((44, row_y, 84, row_y + 36), fill=color, outline=(75, 86, 98))
        draw.text((96, row_y + 9), row["id"], fill=(235, 241, 247), font=mono)
        draw.text((310, row_y + 9), row["classifiedVisualState"], fill=(235, 241, 247), font=mono)
        draw.text((405, row_y + 9), str(row["stats"]["meanRgb"]), fill=(235, 241, 247), font=mono)
        draw.text(
            (640, row_y + 9),
            f"{row['stats']['lumaP10']}/{row['stats']['medianLuma']}/{row['stats']['lumaP90']}",
            fill=(235, 241, 247),
            font=mono,
        )
        draw.text((905, row_y + 9), str(row["stats"]["orangeRatio"]), fill=(235, 241, 247), font=mono)
        draw.text((1020, row_y + 9), str(row["stats"]["darkRatio"]), fill=(235, 241, 247), font=mono)
        draw.text((1135, row_y + 9), str(row["roundtripDiff"]["meanAbsDiff"]), fill=(235, 241, 247), font=mono)

    y = 500
    draw.rectangle((28, y, 1532, y + 235), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 16), "OVERDOSE header/glyph controls", fill=(242, 247, 252), font=normal)
    x = 44
    for row in controls:
        color = tuple(int(round(v)) for v in row["stats"]["medianRgb"])
        draw.rectangle((x, y + 60, x + 54, y + 108), fill=color, outline=(75, 86, 98))
        label = row.get("letter") or "hdr"
        draw.text((x + 4, y + 116), str(label), fill=(235, 241, 247), font=small)
        draw.text((x + 4, y + 140), row["classifiedVisualState"], fill=(235, 241, 247), font=small)
        draw.text((x + 4, y + 164), str(row["stats"]["orangeRatio"]), fill=(178, 190, 204), font=small)
        x += 74
    draw.text(
        (820, y + 64),
        f"control classified stream: {summary['overdoseControlClassifiedStateStream']}",
        fill=(235, 241, 247),
        font=mono,
    )
    draw.text(
        (820, y + 96),
        f"max orange {summary['overdoseControlMaxOrangeRatio']} | max dark {summary['overdoseControlMaxDarkRatio']}",
        fill=(178, 190, 204),
        font=mono,
    )

    y = 780
    draw.rectangle((28, y, 1532, y + 285), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 16), "Separation margins", fill=(242, 247, 252), font=normal)
    rows = [
        ("active order", summary["activeOrder"]),
        ("state order", summary["activeVisualStateOrder"]),
        ("Y orange range", summary["activeYOrangeRatioRange"]),
        ("K dark range", summary["activeKDarkRatioRange"]),
        ("control orange max", summary["overdoseControlMaxOrangeRatio"]),
        ("control dark max", summary["overdoseControlMaxDarkRatio"]),
        ("min Y orange minus control orange", summary["minActiveYOrangeMinusMaxControlOrange"]),
        ("min K dark minus control dark", summary["minActiveKDarkMinusMaxControlDark"]),
        ("max native roundtrip mean diff", summary["maxNativeRoundtripMeanAbsDiff"]),
        ("fingerprint", summary["colorProfileFingerprint"]),
    ]
    for idx, (label, value) in enumerate(rows):
        x = 44 + (idx % 2) * 700
        row_y = y + 58 + (idx // 2) * 42
        draw.text((x, row_y), label, fill=(144, 157, 173), font=small)
        draw.text((x + 250, row_y), str(value), fill=(235, 241, 247), font=mono)
    draw.text(
        (44, y + 252),
        "Result: colors remain a source-matching benchmark only; OVERDOSE controls stay non-active and no extraction unit/order appears.",
        fill=(255, 181, 121),
        font=small,
    )
    sheet.save(SHEET, quality=94)


def main() -> None:
    bridge = load_json(BRIDGE_JSON)
    visual = load_json(VISUAL_JSON)
    alignment = load_json(ALIGNMENT_JSON)
    upright = Image.open(UPRIGHT_IMAGE).convert("RGB")
    native = Image.open(NATIVE_IMAGE).convert("RGB")
    if upright.size != native.size:
        raise RuntimeError(f"size mismatch: upright={upright.size} native={native.size}")

    records = build_records(upright, native, bridge)
    active = [row for row in records if row["kind"] == "active_target"]
    controls = [row for row in records if row["kind"] != "active_target"]
    active_y = [row for row in active if row["classifiedVisualState"] == "Y"]
    active_k = [row for row in active if row["classifiedVisualState"] == "K"]
    control_orange = [row["stats"]["orangeRatio"] for row in controls]
    control_dark = [row["stats"]["darkRatio"] for row in controls]
    active_y_orange = [row["stats"]["orangeRatio"] for row in active_y]
    active_k_dark = [row["stats"]["darkRatio"] for row in active_k]
    active_k_orange = [row["stats"]["orangeRatio"] for row in active_k]

    summary = {
        "recordCount": len(records),
        "activeRecordCount": len(active),
        "overdoseControlRecordCount": len(controls),
        "activeOrder": [row["id"] for row in active],
        "activeExpectedVisualStateOrder": "".join(row["expectedVisualState"] for row in active),
        "activeVisualStateOrder": "".join(row["classifiedVisualState"] for row in active),
        "activeAllStatesMatchExpected": all(row["expectedVisualState"] == row["classifiedVisualState"] for row in active),
        "activePageLines": bridge.get("summary", {}).get("activePageLines"),
        "activeCorridorIndexes": bridge.get("summary", {}).get("activeCorridorIndexes"),
        "activeYOrangeRatioRange": range_or_none(active_y_orange),
        "activeKDarkRatioRange": range_or_none(active_k_dark),
        "activeKOrangeRatioRange": range_or_none(active_k_orange),
        "overdoseControlClassifiedStateStream": "".join(row["classifiedVisualState"] for row in controls),
        "overdoseControlMaxOrangeRatio": round(max(control_orange), 4),
        "overdoseControlMaxDarkRatio": round(max(control_dark), 4),
        "overdoseGlyphSequence": "".join(row.get("letter") or "" for row in controls if row["kind"] == "overdose_glyph"),
        "minActiveYOrangeMinusMaxControlOrange": round(min(active_y_orange) - max(control_orange), 4),
        "minActiveKDarkMinusMaxControlDark": round(min(active_k_dark) - max(control_dark), 4),
        "maxActiveKOrangeRatio": round(max(active_k_orange), 4),
        "maxNativeRoundtripMeanAbsDiff": round(max(row["roundtripDiff"]["meanAbsDiff"] for row in records), 4),
        "visualRoundtripActiveMaxMeanAbsDiff": visual.get("summary", {}).get("activeMaxMeanAbsDiff"),
        "alignmentCommonOutwardPadAllTargetsPassPx": alignment.get("summary", {}).get("commonOutwardPadAllTargetsPassPx"),
        "alignmentCommonFullEightDirectionShiftAllTargetsPassPx": alignment.get("summary", {}).get(
            "commonFullEightDirectionShiftAllTargetsPassPx"
        ),
        "selectorUnlocked": False,
    }
    summary["colorProfileFingerprint"] = (
        f"states={summary['activeVisualStateOrder']}|Yorange={summary['activeYOrangeRatioRange'][0]}-{summary['activeYOrangeRatioRange'][1]}"
        f"|Kdark={summary['activeKDarkRatioRange'][0]}-{summary['activeKDarkRatioRange'][1]}"
        f"|KorangeMax={summary['maxActiveKOrangeRatio']}|ctrlOrangeMax={summary['overdoseControlMaxOrangeRatio']}"
        f"|ctrlDarkMax={summary['overdoseControlMaxDarkRatio']}|roundtripMeanMax={summary['maxNativeRoundtripMeanAbsDiff']}"
    )

    render_sheet(records, summary)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet color profile manifest; no OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation",
        "inputs": {
            "nativeBenchmarkBridge": rel(BRIDGE_JSON),
            "visualStateRoundtrip": rel(VISUAL_JSON),
            "alignmentTolerance": rel(ALIGNMENT_JSON),
            "uprightImage": rel(UPRIGHT_IMAGE),
            "nativeImage": rel(NATIVE_IMAGE),
        },
        "records": records,
        "summary": summary,
        "decision": {
            "sourcePacketColorProfileManifest": "source-validation-only",
            "reason": (
                "The active orange/black visual profile remains cleanly separated from OVERDOSE header/glyph controls and stable under native rotate180 comparison, "
                "but this records source-matching thresholds only and supplies no extraction unit or order."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Use this color profile with the native bridge, frame-normalized geometry, and alignment tolerance when comparing any physical scan, original export, or fresh PDF extraction; extraction remains blocked until source/provenance R3 unit-order wording appears."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Color Profile Manifest",
        "",
        "Scope: record active O4/B4/G5/O5 orange/black color profiles and OVERDOSE header/glyph controls for future source comparison. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active order: `{' -> '.join(summary['activeOrder'])}`",
        f"- Active visual-state order: `{summary['activeVisualStateOrder']}`",
        f"- Active page lines: `{summary['activePageLines']}`",
        f"- Active corridor indexes: `{summary['activeCorridorIndexes']}`",
        f"- Active Y orange-ratio range: `{summary['activeYOrangeRatioRange']}`",
        f"- Active K dark-ratio range: `{summary['activeKDarkRatioRange']}`",
        f"- Active K orange-ratio range: `{summary['activeKOrangeRatioRange']}`",
        f"- OVERDOSE control classified-state stream: `{summary['overdoseControlClassifiedStateStream']}`",
        f"- OVERDOSE control max orange ratio: `{summary['overdoseControlMaxOrangeRatio']}`",
        f"- OVERDOSE control max dark ratio: `{summary['overdoseControlMaxDarkRatio']}`",
        f"- Y/control orange separation margin: `{summary['minActiveYOrangeMinusMaxControlOrange']}`",
        f"- K/control dark separation margin: `{summary['minActiveKDarkMinusMaxControlDark']}`",
        f"- Max native rotate180 mean abs diff: `{summary['maxNativeRoundtripMeanAbsDiff']}`",
        f"- Color-profile fingerprint: `{summary['colorProfileFingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Active Profiles",
        "",
        "| id | expected | classified | mean RGB | median RGB | orange | dark | native mean diff |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in active:
        lines.append(
            f"| `{row['id']}` | `{row['expectedVisualState']}` | `{row['classifiedVisualState']}` | `{row['stats']['meanRgb']}` | "
            f"`{row['stats']['medianRgb']}` | `{row['stats']['orangeRatio']}` | `{row['stats']['darkRatio']}` | `{row['roundtripDiff']['meanAbsDiff']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as a source-validation color manifest only.",
            "- Active orange/black profiles remain visually separated from OVERDOSE controls under the current classification rules.",
            "- This does not reopen highlight-color, bold-letter, C9, OVERDOSE, or fold/mirror selectors.",
            "- Use it only to judge future source/original-layout visual matches; extraction remains blocked until R3 unit/order evidence appears.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("colorProfileFingerprint:", summary["colorProfileFingerprint"])
    print("overdoseControlClassifiedStateStream:", summary["overdoseControlClassifiedStateStream"])
    print("selectorUnlocked:", summary["selectorUnlocked"])


if __name__ == "__main__":
    main()
