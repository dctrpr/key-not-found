#!/usr/bin/env python3
"""Normalize active source-packet geometry inside the source frames.

This bounded pass turns O4/B4/G5/O5 geometry into frame-relative coordinates
inside the C9/Y-K frame and the reflected p78 frame. It also checks simple
C9-frame horizontal, vertical, and point mirrors against the active centers.

This is source-validation evidence only. It performs no OCR, extraction, key
derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad
candidate generation.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_JSON = ROOT / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge/source_packet_native_benchmark_bridge.json"
FINGERPRINT_JSON = ROOT / "analysis_outputs/source_audit/source_packet_geometric_fingerprint/source_packet_geometric_fingerprint.json"
ALIGNMENT_JSON = ROOT / "analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"

OUT = ROOT / "analysis_outputs/source_audit/source_packet_frame_normalized_geometry"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_frame_normalized_geometry.json"
OUT_MD = OUT / "source_packet_frame_normalized_geometry.md"
SHEET = OUT / "source_packet_frame_normalized_geometry_sheet.jpg"


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


def center(box: list[int | float]) -> list[float]:
    return [
        round((float(box[0]) + float(box[2])) / 2, 3),
        round((float(box[1]) + float(box[3])) / 2, 3),
    ]


def size(box: list[int | float]) -> list[float]:
    return [round(float(box[2]) - float(box[0]), 3), round(float(box[3]) - float(box[1]), 3)]


def normalized_point(point: list[float], frame: list[int | float]) -> list[float]:
    frame_size = size(frame)
    return [
        round((point[0] - float(frame[0])) / frame_size[0], 6),
        round((point[1] - float(frame[1])) / frame_size[1], 6),
    ]


def normalized_box(box: list[int | float], frame: list[int | float]) -> list[float]:
    frame_size = size(frame)
    return [
        round((float(box[0]) - float(frame[0])) / frame_size[0], 6),
        round((float(box[1]) - float(frame[1])) / frame_size[1], 6),
        round((float(box[2]) - float(frame[0])) / frame_size[0], 6),
        round((float(box[3]) - float(frame[1])) / frame_size[1], 6),
    ]


def full_inside(box: list[int | float], frame: list[int | float]) -> bool:
    return (
        float(frame[0]) <= float(box[0])
        and float(box[2]) <= float(frame[2])
        and float(frame[1]) <= float(box[1])
        and float(box[3]) <= float(frame[3])
    )


def intersection_area(a: list[int | float], b: list[int | float]) -> float:
    x0 = max(float(a[0]), float(b[0]))
    y0 = max(float(a[1]), float(b[1]))
    x1 = min(float(a[2]), float(b[2]))
    y1 = min(float(a[3]), float(b[3]))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return round((x1 - x0) * (y1 - y0), 6)


def box_area(box: list[int | float]) -> float:
    s = size(box)
    return round(s[0] * s[1], 6)


def distance(a: list[float], b: list[float]) -> float:
    return round(math.hypot(b[0] - a[0], b[1] - a[1]), 6)


def transform_point(point: list[float], frame: list[int | float], mode: str) -> list[float]:
    x0, y0, x1, y1 = [float(v) for v in frame]
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    if mode == "horizontal_mirror":
        return [round(2 * cx - point[0], 3), point[1]]
    if mode == "vertical_mirror":
        return [point[0], round(2 * cy - point[1], 3)]
    if mode == "point_mirror":
        return [round(2 * cx - point[0], 3), round(2 * cy - point[1], 3)]
    raise ValueError(mode)


def build_frame_records(active_rows: list[dict[str, Any]], frame: dict[str, Any]) -> list[dict[str, Any]]:
    frame_box = frame["uprightBox"]
    records = []
    for row in active_rows:
        box = row["uprightBox"]
        point = row["uprightCenter"]
        area = box_area(box)
        overlap = intersection_area(box, frame_box)
        records.append(
            {
                "id": row["id"],
                "visualState": row["visualState"],
                "pageLine": row["pageLine"],
                "corridorIndex": row["corridorIndex"],
                "center": point,
                "box": box,
                "normalizedCenter": normalized_point(point, frame_box),
                "normalizedBox": normalized_box(box, frame_box),
                "fullInsideFrame": full_inside(box, frame_box),
                "partialOverlapAreaPx": overlap,
                "partialOverlapFractionOfTarget": round(overlap / area, 6) if area else 0,
            }
        )
    return records


def mirror_records(active_rows: list[dict[str, Any]], frame: dict[str, Any], thresholds: list[int]) -> list[dict[str, Any]]:
    centers = {row["id"]: row["uprightCenter"] for row in active_rows}
    records = []
    for mode in ["horizontal_mirror", "vertical_mirror", "point_mirror"]:
        transformed_rows = []
        for row in active_rows:
            transformed = transform_point(row["uprightCenter"], frame["uprightBox"], mode)
            distances = [
                {
                    "id": target_id,
                    "distancePx": distance(transformed, target_center),
                }
                for target_id, target_center in centers.items()
            ]
            nearest = min(distances, key=lambda item: item["distancePx"])
            transformed_rows.append(
                {
                    "id": row["id"],
                    "transformedCenter": transformed,
                    "nearestActiveCenter": nearest["id"],
                    "nearestDistancePx": nearest["distancePx"],
                    "hitsByThreshold": {
                        str(threshold): nearest["distancePx"] <= threshold for threshold in thresholds
                    },
                }
            )
        records.append(
            {
                "mode": mode,
                "thresholdsPx": thresholds,
                "hitCountsByThreshold": {
                    str(threshold): sum(1 for row in transformed_rows if row["hitsByThreshold"][str(threshold)])
                    for threshold in thresholds
                },
                "allFourRehitByThreshold": {
                    str(threshold): all(row["hitsByThreshold"][str(threshold)] for row in transformed_rows)
                    for threshold in thresholds
                },
                "rows": transformed_rows,
            }
        )
    return records


def draw_overlay(
    image: Image.Image,
    active_rows: list[dict[str, Any]],
    c9_frame: dict[str, Any],
    reflected_frame: dict[str, Any],
) -> Image.Image:
    crop = [250, 2105, 2310, 3045]
    page = image.copy().convert("RGB")
    draw = ImageDraw.Draw(page)
    label_font = font(19)
    small = font(15)

    def rect(box: list[int | float], color: tuple[int, int, int], width: int = 5) -> None:
        draw.rectangle([int(round(v)) for v in box], outline=color, width=width)

    rect(c9_frame["uprightBox"], (83, 205, 255), 7)
    rect(reflected_frame["uprightBox"], (243, 225, 82), 6)
    draw.text((c9_frame["uprightBox"][0] + 10, c9_frame["uprightBox"][1] + 10), "C9/Y-K frame", fill=(83, 205, 255), font=label_font)
    draw.text((reflected_frame["uprightBox"][0] + 10, reflected_frame["uprightBox"][1] + 10), "reflected p78 frame", fill=(243, 225, 82), font=label_font)

    c9 = c9_frame["uprightBox"]
    cx = (c9[0] + c9[2]) / 2
    cy = (c9[1] + c9[3]) / 2
    draw.line([(cx, c9[1]), (cx, c9[3])], fill=(83, 205, 255), width=2)
    draw.line([(c9[0], cy), (c9[2], cy)], fill=(83, 205, 255), width=2)

    for index, row in enumerate(active_rows, start=1):
        box = row["uprightBox"]
        outline = (255, 166, 64) if row["visualState"] == "Y" else (245, 245, 245)
        rect(box, outline, 5)
        point = row["uprightCenter"]
        draw.ellipse((point[0] - 8, point[1] - 8, point[0] + 8, point[1] + 8), fill=(255, 70, 86))
        norm = normalized_point(point, c9)
        label = f"{index} {row['id']} ({norm[0]:.3f},{norm[1]:.3f})"
        draw.rectangle((box[0] - 4, box[1] - 30, box[0] + 360, box[1] - 5), fill=(12, 15, 20))
        draw.text((box[0], box[1] - 29), label, fill=outline, font=small)

    return page.crop(crop)


def render_sheet(
    image: Image.Image,
    active_rows: list[dict[str, Any]],
    c9_frame: dict[str, Any],
    reflected_frame: dict[str, Any],
    c9_records: list[dict[str, Any]],
    reflected_records: list[dict[str, Any]],
    mirrors: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    overlay = draw_overlay(image, active_rows, c9_frame, reflected_frame)
    scale = 1480 / overlay.width
    overlay = overlay.resize((1480, int(overlay.height * scale)))

    sheet = Image.new("RGB", (1560, 1320), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title = font(30)
    normal = font(18)
    small = font(14)
    mono = font(15)
    draw.text((28, 24), "Source Packet Frame-Normalized Geometry", fill=(242, 247, 252), font=title)
    draw.text(
        (28, 62),
        "Frame-relative coordinates for future source comparison; C9 mirror transforms tested as controls.",
        fill=(178, 190, 204),
        font=normal,
    )
    sheet.paste(overlay, (40, 104))

    y = 735
    draw.rectangle((28, y, 1532, y + 220), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 16), "C9/Y-K frame normalized active centers", fill=(242, 247, 252), font=normal)
    headers = [("id", 44), ("state", 310), ("line/corr", 405), ("norm center", 555), ("inside", 795), ("p78 overlap", 920)]
    for label, x in headers:
        draw.text((x, y + 52), label, fill=(144, 157, 173), font=small)
    for idx, row in enumerate(c9_records):
        yrow = y + 82 + idx * 30
        reflected = reflected_records[idx]
        draw.text((44, yrow), row["id"], fill=(235, 241, 247), font=mono)
        draw.text((310, yrow), row["visualState"], fill=(235, 241, 247), font=mono)
        draw.text((405, yrow), f"{row['pageLine']} / {row['corridorIndex']}", fill=(235, 241, 247), font=mono)
        draw.text((555, yrow), str(row["normalizedCenter"]), fill=(235, 241, 247), font=mono)
        draw.text((795, yrow), str(row["fullInsideFrame"]), fill=(235, 241, 247), font=mono)
        draw.text((920, yrow), f"{reflected['partialOverlapFractionOfTarget']}", fill=(235, 241, 247), font=mono)
    draw.text(
        (1120, y + 84),
        f"C9 full-inside count: {summary['c9ActiveFullInsideCount']} / 4",
        fill=(178, 190, 204),
        font=small,
    )
    draw.text(
        (1120, y + 112),
        f"Reflected p78 full-inside count: {summary['reflectedP78FullInsideCount']} / 4",
        fill=(178, 190, 204),
        font=small,
    )
    draw.text(
        (1120, y + 140),
        f"Reflected p78 partial ids: {summary['reflectedP78PartialOverlapIds']}",
        fill=(178, 190, 204),
        font=small,
    )

    y = 990
    draw.rectangle((28, y, 1532, y + 290), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 16), "C9 frame mirror controls", fill=(242, 247, 252), font=normal)
    for mode_index, mirror in enumerate(mirrors):
        x = 44 + mode_index * 480
        draw.text((x, y + 56), mirror["mode"], fill=(235, 241, 247), font=mono)
        draw.text((x, y + 84), f"hits <=4/25/50px: {mirror['hitCountsByThreshold']}", fill=(178, 190, 204), font=small)
        draw.text((x, y + 112), f"all-four: {mirror['allFourRehitByThreshold']}", fill=(178, 190, 204), font=small)
        for row_index, row in enumerate(mirror["rows"]):
            draw.text(
                (x, y + 146 + row_index * 26),
                f"{row['id']} -> {row['nearestActiveCenter']} d={row['nearestDistancePx']}",
                fill=(235, 241, 247),
                font=small,
            )
    draw.text(
        (44, y + 260),
        "Result: no simple C9 horizontal, vertical, or point mirror re-hits all four active centers under the alignment tolerance controls.",
        fill=(255, 181, 121),
        font=small,
    )
    sheet.save(SHEET, quality=94)


def main() -> None:
    bridge = load_json(BRIDGE_JSON)
    fingerprint = load_json(FINGERPRINT_JSON)
    alignment = load_json(ALIGNMENT_JSON)
    image = Image.open(UPRIGHT_IMAGE).convert("RGB")

    active_rows = [row for row in bridge["rows"] if row["kind"] == "active_target"]
    c9_frame = next(row for row in bridge["rows"] if row["id"] == "c9_yk_frame")
    reflected_frame = next(row for row in bridge["rows"] if row["id"] == "p78_reflected_frame_on_p76")
    for row in active_rows:
        row["uprightCenter"] = center(row["uprightBox"])

    c9_records = build_frame_records(active_rows, c9_frame)
    reflected_records = build_frame_records(active_rows, reflected_frame)
    thresholds = [4, 25, 50]
    mirrors = mirror_records(active_rows, c9_frame, thresholds)

    c9_norm_centers = [row["normalizedCenter"] for row in c9_records]
    reflected_norm_centers = [row["normalizedCenter"] for row in reflected_records]
    summary = {
        "activeOrder": [row["id"] for row in active_rows],
        "visualStateOrder": "".join(row["visualState"] for row in active_rows),
        "activePageLines": " ".join(str(row["pageLine"]) for row in active_rows),
        "activeCorridorIndexes": " ".join(str(row["corridorIndex"]) for row in active_rows),
        "c9FrameBox": c9_frame["uprightBox"],
        "c9NormalizedCenterStream": c9_norm_centers,
        "c9NormalizedBoxStream": [row["normalizedBox"] for row in c9_records],
        "c9ActiveFullInsideCount": sum(1 for row in c9_records if row["fullInsideFrame"]),
        "c9ActivePartialOverlapCount": sum(1 for row in c9_records if row["partialOverlapAreaPx"] > 0),
        "reflectedP78FrameBox": reflected_frame["uprightBox"],
        "reflectedP78NormalizedCenterStream": reflected_norm_centers,
        "reflectedP78FullInsideCount": sum(1 for row in reflected_records if row["fullInsideFrame"]),
        "reflectedP78PartialOverlapCount": sum(1 for row in reflected_records if row["partialOverlapAreaPx"] > 0),
        "reflectedP78PartialOverlapIds": [row["id"] for row in reflected_records if row["partialOverlapAreaPx"] > 0],
        "mirrorModes": [row["mode"] for row in mirrors],
        "mirrorHitCountsByThreshold": {row["mode"]: row["hitCountsByThreshold"] for row in mirrors},
        "mirrorAllFourRehitByThreshold": {row["mode"]: row["allFourRehitByThreshold"] for row in mirrors},
        "alignmentCommonShiftPx": alignment.get("summary", {}).get("commonFullEightDirectionShiftAllTargetsPassPx"),
        "sourceRegistrationFingerprint": fingerprint.get("summary", {}).get("sourceRegistrationFingerprint"),
        "selectorUnlocked": False,
    }
    summary["frameNormalizedFingerprint"] = (
        f"c9NormCenters={';'.join(f'{x:.3f},{y:.3f}' for x, y in c9_norm_centers)}"
        f"|c9Inside={summary['c9ActiveFullInsideCount']}/4"
        f"|p78Inside={summary['reflectedP78FullInsideCount']}/4"
        f"|p78Partial={','.join(summary['reflectedP78PartialOverlapIds']) or 'none'}"
        f"|mirrorAllFour4px="
        f"{','.join(mode for mode, vals in summary['mirrorAllFourRehitByThreshold'].items() if vals['4']) or 'none'}"
    )

    render_sheet(image, active_rows, c9_frame, reflected_frame, c9_records, reflected_records, mirrors, summary)

    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet frame-normalized geometry; no OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation",
        "inputs": {
            "nativeBenchmarkBridge": rel(BRIDGE_JSON),
            "geometricFingerprint": rel(FINGERPRINT_JSON),
            "alignmentTolerance": rel(ALIGNMENT_JSON),
            "uprightImage": rel(UPRIGHT_IMAGE),
        },
        "c9FrameRecords": c9_records,
        "reflectedP78FrameRecords": reflected_records,
        "c9MirrorControls": mirrors,
        "summary": summary,
        "decision": {
            "sourcePacketFrameNormalizedGeometry": "source-validation-only",
            "reason": (
                "The active quartet has a stable frame-relative C9/Y-K coordinate stream and is fully inside the C9 frame, "
                "but the reflected p78 frame contains zero full active targets and simple C9-frame mirrors re-hit no all-four active center set. "
                "This is useful for future source scaling/registration, not extraction."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Use the C9 frame-normalized coordinates together with the native bridge, geometric fingerprint, and tolerance window for future physical/original-layout comparison; keep extraction blocked until source/provenance R3 unit-order wording appears."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Frame-Normalized Geometry",
        "",
        "Scope: normalize O4/B4/G5/O5 geometry inside the C9/Y-K frame and reflected p78 frame, and test simple C9-frame mirror controls. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active order: `{' -> '.join(summary['activeOrder'])}`",
        f"- Visual-state order: `{summary['visualStateOrder']}`",
        f"- Active page lines: `{summary['activePageLines']}`",
        f"- Active corridor indexes: `{summary['activeCorridorIndexes']}`",
        f"- C9 frame: `{summary['c9FrameBox']}`",
        f"- C9 normalized center stream: `{summary['c9NormalizedCenterStream']}`",
        f"- C9 active full-inside count: `{summary['c9ActiveFullInsideCount']}/4`",
        f"- Reflected p78 frame: `{summary['reflectedP78FrameBox']}`",
        f"- Reflected p78 full-inside count: `{summary['reflectedP78FullInsideCount']}/4`",
        f"- Reflected p78 partial-overlap ids: `{summary['reflectedP78PartialOverlapIds']}`",
        f"- C9 mirror hit counts by threshold: `{summary['mirrorHitCountsByThreshold']}`",
        f"- C9 mirror all-four rehit by threshold: `{summary['mirrorAllFourRehitByThreshold']}`",
        f"- Frame-normalized fingerprint: `{summary['frameNormalizedFingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## C9 Normalized Active Centers",
        "",
        "| id | state | line/corridor | normalized center | full inside C9 | reflected p78 overlap fraction |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for c9_row, p78_row in zip(c9_records, reflected_records):
        lines.append(
            f"| `{c9_row['id']}` | `{c9_row['visualState']}` | `{c9_row['pageLine']}/{c9_row['corridorIndex']}` | "
            f"`{c9_row['normalizedCenter']}` | `{c9_row['fullInsideFrame']}` | `{p78_row['partialOverlapFractionOfTarget']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as source-validation/registration evidence only.",
            "- C9/Y-K frame-normalized coordinates are useful for future source scaling checks.",
            "- The reflected p78 frame alone has `0/4` full active target containment and only a partial O5 overlap.",
            "- Simple C9-frame horizontal, vertical, and point mirrors do not re-hit all four active centers under the current alignment-tolerance thresholds.",
            "- This does not reopen folded/mirrored 3D geometry, p78 frame, C9 frame, or OVERDOSE layout mechanics as selectors.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("frameNormalizedFingerprint:", summary["frameNormalizedFingerprint"])
    print("c9ActiveFullInsideCount:", summary["c9ActiveFullInsideCount"])
    print("reflectedP78FullInsideCount:", summary["reflectedP78FullInsideCount"])
    print("selectorUnlocked:", summary["selectorUnlocked"])


if __name__ == "__main__":
    main()
