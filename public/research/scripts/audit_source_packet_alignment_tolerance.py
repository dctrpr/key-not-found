#!/usr/bin/env python3
"""Build an alignment tolerance benchmark for the source packet.

Future physical scans, original exports, or fresh PDF extractions will not land
on exactly the current crop coordinates. This bounded pass measures how much
the active O4/B4/G5/O5 boxes can be padded or shifted while preserving the
current Y/K visual-state evidence and native rotate180 roundtrip.

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
VISUAL_JSON = ROOT / "analysis_outputs/source_audit/source_packet_visual_state_roundtrip/source_packet_visual_state_roundtrip.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"

OUT = ROOT / "analysis_outputs/source_audit/source_packet_alignment_tolerance"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_alignment_tolerance.json"
OUT_MD = OUT / "source_packet_alignment_tolerance.md"
SHEET = OUT / "source_packet_alignment_tolerance_sheet.jpg"

PAD_VALUES = [-12, -8, -4, 0, 4, 8, 12, 16, 24, 32]
SHIFT_DELTAS = [4, 8, 12, 16, 24, 32, 48]


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


def in_bounds(box: list[int | float], width: int, height: int) -> bool:
    x0, y0, x1, y1 = int_box(box)
    return 0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height


def padded_box(box: list[int | float], pad: int) -> list[int]:
    x0, y0, x1, y1 = int_box(box)
    return [x0 - pad, y0 - pad, x1 + pad, y1 + pad]


def shifted_box(box: list[int | float], dx: int, dy: int) -> list[int]:
    x0, y0, x1, y1 = int_box(box)
    return [x0 + dx, y0 + dy, x1 + dx, y1 + dy]


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
    diff = np.abs(a - b)
    return {
        "meanAbsDiff": round(float(diff.mean()), 4),
        "maxDiff": int(diff.max()),
    }


def evaluate_variant(
    upright: Image.Image,
    native: Image.Image,
    base: dict[str, Any],
    box: list[int],
    variant: str,
    value: str | int,
) -> dict[str, Any]:
    width, height = upright.size
    native_box = rot180_box(box, width, height)
    upright_crop = upright.crop(box)
    native_crop = native.crop(native_box).rotate(180)
    stats = visual_stats(upright_crop)
    classified = classify_visual_state(stats)
    return {
        "targetId": base["id"],
        "variant": variant,
        "value": value,
        "uprightBox": box,
        "nativeBox": native_box,
        "expectedVisualState": base["visualState"],
        "classifiedVisualState": classified,
        "passesVisualState": classified == base["visualState"],
        "visualStats": stats,
        "diff": diff_stats(upright_crop, native_crop),
    }


def build_records(upright: Image.Image, native: Image.Image) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bridge = load_json(BRIDGE_JSON)
    width, height = upright.size
    active_rows = [row for row in bridge["rows"] if row["kind"] == "active_target"]
    control_rows = [row for row in bridge["rows"] if row["kind"] in {"overdose_header", "overdose_glyph"}]

    target_records = []
    for row in active_rows:
        base_box = int_box(row["uprightBox"])
        pad_results = []
        for pad in PAD_VALUES:
            box = padded_box(base_box, pad)
            if in_bounds(box, width, height):
                pad_results.append(evaluate_variant(upright, native, row, box, "pad", pad))
        shift_results = []
        for delta in SHIFT_DELTAS:
            for dx in (-delta, 0, delta):
                for dy in (-delta, 0, delta):
                    if dx == 0 and dy == 0:
                        continue
                    box = shifted_box(base_box, dx, dy)
                    if in_bounds(box, width, height):
                        shift_results.append(evaluate_variant(upright, native, row, box, "shift", f"{dx},{dy}"))
        target_records.append(
            {
                "id": row["id"],
                "label": row["label"],
                "expectedVisualState": row["visualState"],
                "pageLine": row.get("pageLine"),
                "corridorIndex": row.get("corridorIndex"),
                "baseBox": base_box,
                "padResults": pad_results,
                "shiftResults": shift_results,
                "maxOutwardPadAllPass": max(
                    [r["value"] for r in pad_results if isinstance(r["value"], int) and r["value"] >= 0 and r["passesVisualState"]],
                    default=None,
                ),
                "maxInsetPadAllPass": min(
                    [r["value"] for r in pad_results if isinstance(r["value"], int) and r["value"] <= 0 and r["passesVisualState"]],
                    default=None,
                ),
            }
        )

    shift_summary = []
    for delta in SHIFT_DELTAS:
        variant_records = [
            r
            for target in target_records
            for r in target["shiftResults"]
            if max(abs(int(str(r["value"]).split(",")[0])), abs(int(str(r["value"]).split(",")[1]))) == delta
        ]
        by_target = {}
        for target in target_records:
            rows = [
                r
                for r in target["shiftResults"]
                if max(abs(int(str(r["value"]).split(",")[0])), abs(int(str(r["value"]).split(",")[1]))) == delta
            ]
            by_target[target["id"]] = {
                "passCount": sum(1 for r in rows if r["passesVisualState"]),
                "total": len(rows),
            }
        shift_summary.append(
            {
                "delta": delta,
                "passCount": sum(1 for r in variant_records if r["passesVisualState"]),
                "total": len(variant_records),
                "allTargetsAllEightDirectionsPass": all(v["passCount"] == v["total"] == 8 for v in by_target.values()),
                "byTarget": by_target,
            }
        )

    pad_summary = []
    for pad in PAD_VALUES:
        rows = [r for target in target_records for r in target["padResults"] if r["value"] == pad]
        if rows:
            pad_summary.append(
                {
                    "pad": pad,
                    "passCount": sum(1 for r in rows if r["passesVisualState"]),
                    "total": len(rows),
                    "allTargetsPass": len(rows) == len(target_records)
                    and all(r["passesVisualState"] for r in rows),
                }
            )

    control_records = []
    for row in control_rows:
        box = int_box(row["uprightBox"])
        stats = visual_stats(upright.crop(box))
        control_records.append(
            {
                "id": row["id"],
                "kind": row["kind"],
                "letter": row.get("letter"),
                "classifiedVisualState": classify_visual_state(stats),
                "visualStats": stats,
            }
        )

    summary = {
        "activeTargetCount": len(target_records),
        "activeExpectedVisualStateOrder": "".join(row["expectedVisualState"] for row in target_records),
        "activePageLines": " ".join(str(row["pageLine"]) for row in target_records),
        "activeCorridorIndexes": " ".join(str(row["corridorIndex"]) for row in target_records),
        "commonOutwardPadAllTargetsPassPx": max(
            [row["pad"] for row in pad_summary if row["pad"] >= 0 and row["allTargetsPass"]],
            default=None,
        ),
        "commonInsetPadAllTargetsPassPx": min(
            [row["pad"] for row in pad_summary if row["pad"] <= 0 and row["allTargetsPass"]],
            default=None,
        ),
        "commonFullEightDirectionShiftAllTargetsPassPx": max(
            [row["delta"] for row in shift_summary if row["allTargetsAllEightDirectionsPass"]],
            default=None,
        ),
        "largestAnyTargetOutwardPadPassPx": max(
            [r["value"] for target in target_records for r in target["padResults"] if isinstance(r["value"], int) and r["value"] >= 0 and r["passesVisualState"]],
            default=None,
        ),
        "smallestFirstPadFailurePx": min(
            [r["value"] for target in target_records for r in target["padResults"] if isinstance(r["value"], int) and r["value"] >= 0 and not r["passesVisualState"]],
            default=None,
        ),
        "shiftSummary": shift_summary,
        "padSummary": pad_summary,
        "controlRecordCount": len(control_records),
        "overdoseControlClassifiedStates": "".join(row["classifiedVisualState"] for row in control_records),
        "overdoseControlMaxDarkRatio": round(max(row["visualStats"]["darkRatio"] for row in control_records), 4),
        "overdoseControlMaxOrangeRatio": round(max(row["visualStats"]["orangeRatio"] for row in control_records), 4),
        "maxVariantMeanAbsDiff": round(
            max(
                r["diff"]["meanAbsDiff"]
                for target in target_records
                for group in ("padResults", "shiftResults")
                for r in target[group]
            ),
            4,
        ),
        "selectorUnlocked": False,
    }
    return target_records + control_records, summary


def render_sheet(records: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    target_records = [row for row in records if "padResults" in row]
    sheet_w, sheet_h = 1560, 1040
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(17)
    small = font(13)
    mono = font(15)
    draw.text((28, 24), "Source Packet Alignment Tolerance", fill=(242, 247, 252), font=title)
    draw.text(
        (28, 62),
        f"Common pass: outward pad +{summary['commonOutwardPadAllTargetsPassPx']}px, inset {summary['commonInsetPadAllTargetsPassPx']}px, all-direction shift +/-{summary['commonFullEightDirectionShiftAllTargetsPassPx']}px.",
        fill=(185, 196, 208),
        font=normal,
    )
    draw.text(
        (28, 90),
        "Visual-state classifications only; no OCR or extraction. Red cells mark first tolerance failures.",
        fill=(150, 162, 176),
        font=small,
    )

    y = 134
    headers = [("target", 0), ("state", 250), ("pad pass/fail", 355), ("shift pass counts", 875), ("line/corr", 1320)]
    draw.rectangle((26, y, sheet_w - 26, y + 34), fill=(30, 35, 43))
    for label, xoff in headers:
        draw.text((38 + xoff, y + 9), label, fill=(238, 243, 248), font=small)
    y += 44

    for target in target_records:
        draw.rectangle((26, y - 8, sheet_w - 26, y + 138), fill=(18, 22, 28), outline=(45, 54, 64))
        draw.text((38, y), target["id"], fill=(242, 247, 252), font=normal)
        draw.text((288, y), target["expectedVisualState"], fill=(255, 213, 135), font=mono)
        x = 393
        for pad in PAD_VALUES:
            row = next((r for r in target["padResults"] if r["value"] == pad), None)
            passed = row["passesVisualState"] if row else False
            fill = (36, 72, 48) if passed else (92, 34, 36)
            draw.rectangle((x, y, x + 44, y + 34), fill=fill, outline=(63, 73, 84))
            draw.text((x + 6, y + 9), str(pad), fill=(238, 243, 248), font=small)
            x += 48
        x = 910
        for item in summary["shiftSummary"]:
            counts = item["byTarget"][target["id"]]
            passed = counts["passCount"] == counts["total"] == 8
            fill = (36, 72, 48) if passed else (92, 64, 34) if counts["passCount"] else (92, 34, 36)
            draw.rectangle((x, y, x + 56, y + 34), fill=fill, outline=(63, 73, 84))
            draw.text((x + 6, y + 9), f"{item['delta']}:{counts['passCount']}", fill=(238, 243, 248), font=small)
            x += 60
        draw.text((1358, y), f"L{target['pageLine']} / C{target['corridorIndex']}", fill=(210, 220, 230), font=mono)

        # Second row with compact ratios at exact, +4, first fail where available.
        exact = next(r for r in target["padResults"] if r["value"] == 0)
        first_fail = next((r for r in target["padResults"] if isinstance(r["value"], int) and r["value"] >= 0 and not r["passesVisualState"]), None)
        draw.text(
            (38, y + 48),
            f"exact O={exact['visualStats']['orangeRatio']} D={exact['visualStats']['darkRatio']} meanDiff={exact['diff']['meanAbsDiff']}",
            fill=(176, 186, 198),
            font=small,
        )
        if first_fail:
            draw.text(
                (38, y + 74),
                f"first outward pad fail +{first_fail['value']}px -> {first_fail['classifiedVisualState']} (O={first_fail['visualStats']['orangeRatio']} D={first_fail['visualStats']['darkRatio']})",
                fill=(255, 176, 122),
                font=small,
            )
        y += 156

    y += 18
    draw.rectangle((26, y, sheet_w - 26, y + 118), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((38, y + 16), "OVERDOSE header/glyph control", fill=(242, 247, 252), font=normal)
    draw.text(
        (38, y + 46),
        f"class stream {summary['overdoseControlClassifiedStates']} | max dark {summary['overdoseControlMaxDarkRatio']} | max orange {summary['overdoseControlMaxOrangeRatio']}",
        fill=(210, 220, 230),
        font=mono,
    )
    draw.text(
        (38, y + 76),
        "Controls remain non-K/non-active; the tolerance benchmark is for future source alignment, not extraction permission.",
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
    render_sheet(records, summary)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet active-box alignment tolerance; no OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation",
        "inputs": {
            "nativeBenchmarkBridge": rel(BRIDGE_JSON),
            "visualStateRoundtrip": rel(VISUAL_JSON),
            "uprightImage": rel(UPRIGHT_IMAGE),
            "nativeImage": rel(NATIVE_IMAGE),
        },
        "parameters": {
            "padValuesPx": PAD_VALUES,
            "shiftDeltasPx": SHIFT_DELTAS,
            "visualClassRules": {
                "Y": "orangeRatio >= 0.45",
                "K": "darkRatio >= 0.5 and orangeRatio <= 0.05",
            },
        },
        "imageSize": list(upright.size),
        "records": records,
        "summary": summary,
        "decision": {
            "sourcePacketAlignmentTolerance": "source-validation-only",
            "reason": (
                "The active boxes have a narrow common tolerance window: all targets survive +4px outward padding, -12px inset, and +/-4px all-direction shifts, "
                "but larger padding/shifts begin to break black-highlight and orange-highlight classification. This constrains future source matching and supplies no extraction unit/order."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "For any physical scan, original layout export, or fresh PDF extraction, first align to the native bridge and require the active boxes to meet these tolerance benchmarks; then require R3 unit/order evidence before extraction."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Alignment Tolerance",
        "",
        "Scope: measure how much the active O4/B4/G5/O5 boxes can be padded or shifted while preserving Y/K visual-state evidence and native rotate180 roundtrip. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active expected visual-state order: `{summary['activeExpectedVisualStateOrder']}`",
        f"- Active page lines: `{summary['activePageLines']}`",
        f"- Active corridor indexes: `{summary['activeCorridorIndexes']}`",
        f"- Common outward pad all targets pass: `+{summary['commonOutwardPadAllTargetsPassPx']}px`",
        f"- Common inset pad all targets pass: `{summary['commonInsetPadAllTargetsPassPx']}px`",
        f"- Common all-direction shift all targets pass: `±{summary['commonFullEightDirectionShiftAllTargetsPassPx']}px`",
        f"- Largest any-target outward pad pass: `+{summary['largestAnyTargetOutwardPadPassPx']}px`",
        f"- Smallest first outward pad failure: `+{summary['smallestFirstPadFailurePx']}px`",
        f"- Max variant mean abs diff after native rotate180: `{summary['maxVariantMeanAbsDiff']}`",
        f"- OVERDOSE control classified-state stream: `{summary['overdoseControlClassifiedStates']}`",
        f"- OVERDOSE control max dark ratio: `{summary['overdoseControlMaxDarkRatio']}`",
        f"- OVERDOSE control max orange ratio: `{summary['overdoseControlMaxOrangeRatio']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Target Tolerance",
        "",
        "| id | state | line/corridor | outward pass max | inset pass max | first outward fail |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in [r for r in records if "padResults" in r]:
        outward_passes = [r["value"] for r in row["padResults"] if isinstance(r["value"], int) and r["value"] >= 0 and r["passesVisualState"]]
        inset_passes = [r["value"] for r in row["padResults"] if isinstance(r["value"], int) and r["value"] <= 0 and r["passesVisualState"]]
        outward_fails = [r["value"] for r in row["padResults"] if isinstance(r["value"], int) and r["value"] >= 0 and not r["passesVisualState"]]
        lines.append(
            f"| `{row['id']}` | `{row['expectedVisualState']}` | `{row['pageLine']}/{row['corridorIndex']}` | "
            f"`+{max(outward_passes) if outward_passes else None}` | `{min(inset_passes) if inset_passes else None}` | "
            f"`+{min(outward_fails) if outward_fails else None}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as a source-alignment benchmark only.",
            "- Future source matches should be judged with narrow tolerance: common all-target pass is `+4px` outward padding and `±4px` full-direction shift.",
            "- Larger drift starts breaking visual-state classification, especially black-highlight boxes, so do not accept loose visual matches as source confirmation.",
            "- This supplies no extraction unit or order and does not reopen highlight, fold, or OVERDOSE selectors.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("commonOutwardPadAllTargetsPassPx:", summary["commonOutwardPadAllTargetsPassPx"])
    print("commonFullEightDirectionShiftAllTargetsPassPx:", summary["commonFullEightDirectionShiftAllTargetsPassPx"])
    print("overdoseControlClassifiedStates:", summary["overdoseControlClassifiedStates"])
    print("selectorUnlocked:", summary["selectorUnlocked"])


if __name__ == "__main__":
    main()
