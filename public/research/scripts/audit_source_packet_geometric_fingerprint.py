#!/usr/bin/env python3
"""Build a geometric fingerprint for the active source packet.

This bounded pass records the O4/B4/G5/O5 active quartet as source-registration
geometry: boxes, centers, page/corridor gaps, pairwise distances, motion signs,
native rotate180 roundtrip checks, and OVERDOSE header placement context.

It is not a selector. It performs no OCR, extraction, key derivation, hashing,
seed/WIF checks, address checks, BIP39 checks, or broad candidate generation.
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
ALIGNMENT_JSON = ROOT / "analysis_outputs/source_audit/source_packet_alignment_tolerance/source_packet_alignment_tolerance.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"

OUT = ROOT / "analysis_outputs/source_audit/source_packet_geometric_fingerprint"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_geometric_fingerprint.json"
OUT_MD = OUT / "source_packet_geometric_fingerprint.md"
SHEET = OUT / "source_packet_geometric_fingerprint_sheet.jpg"


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
    return [
        round(float(box[2]) - float(box[0]), 3),
        round(float(box[3]) - float(box[1]), 3),
    ]


def bbox(rows: list[dict[str, Any]], key: str = "uprightBox") -> list[float]:
    return [
        min(float(row[key][0]) for row in rows),
        min(float(row[key][1]) for row in rows),
        max(float(row[key][2]) for row in rows),
        max(float(row[key][3]) for row in rows),
    ]


def rounded_box(box: list[int | float]) -> list[int | float]:
    rounded = [round(float(v), 3) for v in box]
    if all(abs(v - round(v)) < 0.001 for v in rounded):
        return [int(round(v)) for v in rounded]
    return rounded


def sign(value: float) -> str:
    if value > 0:
        return "+"
    if value < 0:
        return "-"
    return "0"


def angle_deg(dx: float, dy: float) -> float:
    return round(math.degrees(math.atan2(dy, dx)), 3)


def distance(a: list[float], b: list[float]) -> float:
    return round(math.hypot(b[0] - a[0], b[1] - a[1]), 3)


def native_center_to_upright(native_center: list[float], width: int, height: int) -> list[float]:
    return [round(width - native_center[0], 3), round(height - native_center[1], 3)]


def native_box_to_upright(native_box: list[int | float], width: int, height: int) -> list[float]:
    x0, y0, x1, y1 = [float(v) for v in native_box]
    return [round(width - x1, 3), round(height - y1, 3), round(width - x0, 3), round(height - y0, 3)]


def build_pairwise(active_rows: list[dict[str, Any]], width: int, height: int) -> list[dict[str, Any]]:
    diag = math.hypot(width, height)
    records = []
    for i, left in enumerate(active_rows):
        for j, right in enumerate(active_rows[i + 1 :], start=i + 1):
            left_center = left["uprightCenter"]
            right_center = right["uprightCenter"]
            dx = round(right_center[0] - left_center[0], 3)
            dy = round(right_center[1] - left_center[1], 3)
            dist = distance(left_center, right_center)
            records.append(
                {
                    "from": left["id"],
                    "to": right["id"],
                    "orderIndexPair": [i, j],
                    "visualPair": left["visualState"] + right["visualState"],
                    "lineGap": int(right["pageLine"] - left["pageLine"]),
                    "corridorGap": int(right["corridorIndex"] - left["corridorIndex"]),
                    "dx": dx,
                    "dy": dy,
                    "dxSign": sign(dx),
                    "dySign": sign(dy),
                    "distancePx": dist,
                    "distancePageDiagonalRatio": round(dist / diag, 6),
                    "angleDegreesImageYDown": angle_deg(dx, dy),
                }
            )
    return records


def build_rows(bridge: dict[str, Any], width: int, height: int) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    active_rows = []
    header_row = {}
    glyph_rows = []
    for row in bridge["rows"]:
        if row["kind"] == "active_target":
            upright_center = center(row["uprightBox"])
            native_center = center(row["nativeBox"])
            roundtrip_center = native_center_to_upright(native_center, width, height)
            roundtrip_box = native_box_to_upright(row["nativeBox"], width, height)
            active_rows.append(
                {
                    "id": row["id"],
                    "label": row["label"],
                    "visualState": row["visualState"],
                    "pageLine": row["pageLine"],
                    "corridorIndex": row["corridorIndex"],
                    "uprightBox": rounded_box(row["uprightBox"]),
                    "nativeBox": rounded_box(row["nativeBox"]),
                    "uprightCenter": upright_center,
                    "nativeCenter": native_center,
                    "boxSize": size(row["uprightBox"]),
                    "roundtripUprightCenterFromNative": roundtrip_center,
                    "roundtripUprightBoxFromNative": rounded_box(roundtrip_box),
                    "roundtripCenterErrorPx": round(distance(upright_center, roundtrip_center), 6),
                    "roundtripBoxMaxErrorPx": round(
                        max(abs(float(a) - float(b)) for a, b in zip(row["uprightBox"], roundtrip_box)),
                        6,
                    ),
                }
            )
        elif row["kind"] == "overdose_header":
            header_row = row
        elif row["kind"] == "overdose_glyph":
            glyph_rows.append(row)
    glyph_rows = sorted(glyph_rows, key=lambda item: item.get("slotIndex", 0))
    return active_rows, header_row, glyph_rows


def draw_page_panel(
    image: Image.Image,
    active_rows: list[dict[str, Any]],
    title: str,
    crop: list[int],
) -> Image.Image:
    page = image.copy().convert("RGB")
    draw = ImageDraw.Draw(page)
    title_font = font(26)
    label_font = font(18)
    small_font = font(14)
    centers = [row["uprightCenter"] for row in active_rows]

    for start, end in zip(centers, centers[1:]):
        draw.line([tuple(start), tuple(end)], fill=(93, 210, 255), width=5)
    for index, row in enumerate(active_rows, start=1):
        box = row["uprightBox"]
        color = (255, 155, 46) if row["visualState"] == "Y" else (20, 20, 24)
        outline = (255, 210, 128) if row["visualState"] == "Y" else (245, 245, 245)
        draw.rectangle(box, outline=outline, width=5)
        cx, cy = row["uprightCenter"]
        draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(93, 210, 255), outline=(0, 0, 0), width=2)
        label = f"{index} {row['id']} L{row['pageLine']} C{row['corridorIndex']} {row['visualState']}"
        tx = int(box[0])
        ty = int(max(0, box[1] - 32))
        draw.rectangle((tx - 4, ty - 3, tx + 360, ty + 22), fill=(12, 15, 20))
        draw.text((tx, ty), label, fill=outline, font=small_font)
        if row["visualState"] == "K":
            draw.rectangle((box[0] + 5, box[1] + 5, box[0] + 34, box[1] + 25), fill=color)

    cropped = page.crop(crop)
    banner = Image.new("RGB", (cropped.width, cropped.height + 52), (10, 13, 18))
    banner_draw = ImageDraw.Draw(banner)
    banner_draw.text((16, 12), title, fill=(241, 246, 251), font=title_font)
    banner.paste(cropped, (0, 52))
    return banner


def render_sheet(
    upright: Image.Image,
    native: Image.Image,
    active_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    pairwise: list[dict[str, Any]],
) -> None:
    crop = [330, 2100, 1875, 3060]
    upright_panel = draw_page_panel(upright, active_rows, "Readable/upright active quartet", crop)
    native_panel = draw_page_panel(native.rotate(180), active_rows, "Native source rotated back", crop)

    panel_w = 720
    panels = []
    for panel in (upright_panel, native_panel):
        scale = panel_w / panel.width
        panels.append(panel.resize((panel_w, int(panel.height * scale))))

    table_w = 1510
    sheet_w = 1560
    sheet_h = 1180
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    title_font = font(30)
    normal = font(18)
    small = font(14)
    mono = font(15)

    draw.text((28, 24), "Source Packet Geometric Fingerprint", fill=(242, 247, 252), font=title_font)
    draw.text(
        (28, 62),
        "Source-registration evidence only: active quartet shape, gaps, native roundtrip, and OVERDOSE layout context.",
        fill=(178, 190, 204),
        font=normal,
    )
    sheet.paste(panels[0], (28, 112))
    sheet.paste(panels[1], (812, 112))

    y = 705
    draw.rectangle((28, y, 28 + table_w, y + 178), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 18), "Active quartet fingerprint", fill=(242, 247, 252), font=normal)
    rows = [
        ("visual order", summary["visualStateOrder"]),
        ("page lines", summary["activePageLines"]),
        ("corridors", summary["activeCorridorIndexes"]),
        ("line gaps", summary["pageLineGaps"]),
        ("corridor gaps", summary["corridorGaps"]),
        ("dx/dy signs", f"{summary['dxSignStream']} / {summary['dySignStream']}"),
        ("cluster box", summary["clusterBox"]),
        ("native roundtrip max", f"{summary['maxNativeRoundtripCenterErrorPx']} px center / {summary['maxNativeRoundtripBoxErrorPx']} px box"),
    ]
    for index, (label, value) in enumerate(rows):
        x = 44 + (index % 4) * 365
        row_y = y + 56 + (index // 4) * 54
        draw.text((x, row_y), label, fill=(144, 157, 173), font=small)
        draw.text((x, row_y + 20), str(value), fill=(235, 241, 247), font=mono)

    y = 910
    draw.rectangle((28, y, 28 + table_w, y + 230), fill=(18, 22, 28), outline=(45, 54, 64))
    draw.text((44, y + 16), "Pairwise distances in active order", fill=(242, 247, 252), font=normal)
    headers = [("pair", 44), ("vis", 340), ("line/corr gap", 430), ("dx,dy", 620), ("dist", 820), ("angle", 965)]
    for label, x in headers:
        draw.text((x, y + 52), label, fill=(144, 157, 173), font=small)
    for idx, row in enumerate(pairwise[:6]):
        row_y = y + 78 + idx * 24
        draw.text((44, row_y), f"{row['from']} -> {row['to']}", fill=(235, 241, 247), font=mono)
        draw.text((340, row_y), row["visualPair"], fill=(235, 241, 247), font=mono)
        draw.text((430, row_y), f"{row['lineGap']} / {row['corridorGap']}", fill=(235, 241, 247), font=mono)
        draw.text((620, row_y), f"{row['dx']}, {row['dy']}", fill=(235, 241, 247), font=mono)
        draw.text((820, row_y), str(row["distancePx"]), fill=(235, 241, 247), font=mono)
        draw.text((965, row_y), str(row["angleDegreesImageYDown"]), fill=(235, 241, 247), font=mono)

    draw.text(
        (1080, y + 78),
        f"OVERDOSE header to cluster centroid: dx {summary['overdoseHeaderToClusterCentroid']['dx']}, dy {summary['overdoseHeaderToClusterCentroid']['dy']}, dist {summary['overdoseHeaderToClusterCentroid']['distancePx']}.",
        fill=(178, 190, 204),
        font=small,
    )
    draw.text(
        (1080, y + 110),
        "No selector unlocked; this sheet is for future source/original-layout comparison.",
        fill=(255, 181, 121),
        font=small,
    )
    sheet.save(SHEET, quality=94)


def main() -> None:
    bridge = load_json(BRIDGE_JSON)
    alignment = load_json(ALIGNMENT_JSON)
    upright = Image.open(UPRIGHT_IMAGE).convert("RGB")
    native = Image.open(NATIVE_IMAGE).convert("RGB")
    if upright.size != native.size:
        raise RuntimeError(f"size mismatch: upright={upright.size} native={native.size}")

    width, height = upright.size
    active_rows, header_row, glyph_rows = build_rows(bridge, width, height)
    if len(active_rows) != 4:
        raise RuntimeError(f"expected 4 active rows, found {len(active_rows)}")
    if not header_row:
        raise RuntimeError("missing OVERDOSE header row from native benchmark bridge")

    pairwise = build_pairwise(active_rows, width, height)
    active_centers = [row["uprightCenter"] for row in active_rows]
    cluster_box = bbox(active_rows)
    cluster_size = size(cluster_box)
    cluster_centroid = [
        round(sum(point[0] for point in active_centers) / len(active_centers), 3),
        round(sum(point[1] for point in active_centers) / len(active_centers), 3),
    ]
    page_lines = [row["pageLine"] for row in active_rows]
    corridors = [row["corridorIndex"] for row in active_rows]
    page_line_gaps = [b - a for a, b in zip(page_lines, page_lines[1:])]
    corridor_gaps = [b - a for a, b in zip(corridors, corridors[1:])]
    dx_signs = "".join(sign(b[0] - a[0]) for a, b in zip(active_centers, active_centers[1:]))
    dy_signs = "".join(sign(b[1] - a[1]) for a, b in zip(active_centers, active_centers[1:]))
    visual_order = "".join(row["visualState"] for row in active_rows)

    c9_frame = next(row for row in bridge["rows"] if row["id"] == "c9_yk_frame")
    c9_size = size(c9_frame["uprightBox"])
    cluster_area = cluster_size[0] * cluster_size[1]
    c9_area = c9_size[0] * c9_size[1]
    header_center = center(header_row["uprightBox"])
    header_dx = round(cluster_centroid[0] - header_center[0], 3)
    header_dy = round(cluster_centroid[1] - header_center[1], 3)
    header_distance = round(math.hypot(header_dx, header_dy), 3)

    summary = {
        "activeOrder": [row["id"] for row in active_rows],
        "visualStateOrder": visual_order,
        "activePageLines": " ".join(str(value) for value in page_lines),
        "activeCorridorIndexes": " ".join(str(value) for value in corridors),
        "pageLineGaps": page_line_gaps,
        "corridorGaps": corridor_gaps,
        "dxSignStream": dx_signs,
        "dySignStream": dy_signs,
        "clusterBox": rounded_box(cluster_box),
        "clusterSize": rounded_box([0, 0, cluster_size[0], cluster_size[1]])[2:],
        "clusterCentroid": cluster_centroid,
        "clusterAspectWidthOverHeight": round(cluster_size[0] / cluster_size[1], 6),
        "clusterAreaPx": int(round(cluster_area)),
        "c9FrameBox": rounded_box(c9_frame["uprightBox"]),
        "c9FrameCoverageWidthRatio": round(cluster_size[0] / c9_size[0], 6),
        "c9FrameCoverageHeightRatio": round(cluster_size[1] / c9_size[1], 6),
        "c9FrameCoverageAreaRatio": round(cluster_area / c9_area, 6),
        "maxNativeRoundtripCenterErrorPx": round(max(row["roundtripCenterErrorPx"] for row in active_rows), 6),
        "maxNativeRoundtripBoxErrorPx": round(max(row["roundtripBoxMaxErrorPx"] for row in active_rows), 6),
        "pairwiseRecordCount": len(pairwise),
        "overdoseHeaderGlyphSequence": "".join(row.get("letter", "") for row in glyph_rows),
        "overdoseHeaderGlyphSlotCount": len(glyph_rows),
        "overdoseHeaderCenter": header_center,
        "overdoseHeaderToClusterCentroid": {
            "dx": header_dx,
            "dy": header_dy,
            "distancePx": header_distance,
            "angleDegreesImageYDown": angle_deg(header_dx, header_dy),
        },
        "alignmentCommonOutwardPadAllTargetsPassPx": alignment.get("summary", {}).get("commonOutwardPadAllTargetsPassPx"),
        "alignmentCommonFullEightDirectionShiftAllTargetsPassPx": alignment.get("summary", {}).get(
            "commonFullEightDirectionShiftAllTargetsPassPx"
        ),
        "selectorUnlocked": False,
    }
    summary["sourceRegistrationFingerprint"] = (
        f"order={'/'.join(summary['activeOrder'])}|states={visual_order}|lines={summary['activePageLines'].replace(' ', '-')}"
        f"|corr={summary['activeCorridorIndexes'].replace(' ', '-')}|lineGaps={'-'.join(map(str, page_line_gaps))}"
        f"|corrGaps={'-'.join(map(str, corridor_gaps))}|dxSigns={dx_signs}|dySigns={dy_signs}"
        f"|cluster={summary['clusterSize'][0]}x{summary['clusterSize'][1]}|nativeRoundtripCenter={summary['maxNativeRoundtripCenterErrorPx']}"
    )

    render_sheet(upright, native, active_rows, summary, pairwise)
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet active-quartet geometric fingerprint; no OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation",
        "inputs": {
            "nativeBenchmarkBridge": rel(BRIDGE_JSON),
            "alignmentTolerance": rel(ALIGNMENT_JSON),
            "uprightImage": rel(UPRIGHT_IMAGE),
            "nativeImage": rel(NATIVE_IMAGE),
        },
        "imageSize": list(upright.size),
        "activeRows": active_rows,
        "pairwise": pairwise,
        "summary": summary,
        "decision": {
            "sourcePacketGeometricFingerprint": "source-validation-only",
            "reason": (
                "The active quartet now has a compact geometric fingerprint in readable/upright and native rotate180 coordinates. "
                "It stabilizes future source/original-layout comparison, but supplies no extraction unit, order rule, or selector permission."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Use this fingerprint with the native bridge and alignment tolerance when comparing a physical scan, original export, or fresh PDF extraction; extraction remains blocked until R3 unit/order wording appears."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Geometric Fingerprint",
        "",
        "Scope: record O4/B4/G5/O5 active-quartet geometry for future source/original-layout comparison. No OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, BIP39 checks, or broad candidate generation were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Active order: `{' -> '.join(summary['activeOrder'])}`",
        f"- Visual-state order: `{summary['visualStateOrder']}`",
        f"- Page lines: `{summary['activePageLines']}`",
        f"- Corridor indexes: `{summary['activeCorridorIndexes']}`",
        f"- Page-line gaps: `{summary['pageLineGaps']}`",
        f"- Corridor gaps: `{summary['corridorGaps']}`",
        f"- Center-step signs: dx `{summary['dxSignStream']}`, dy `{summary['dySignStream']}`",
        f"- Cluster box: `{summary['clusterBox']}`",
        f"- Cluster size: `{summary['clusterSize']}`",
        f"- Cluster centroid: `{summary['clusterCentroid']}`",
        f"- Native rotate180 max center roundtrip error: `{summary['maxNativeRoundtripCenterErrorPx']}px`",
        f"- Native rotate180 max box roundtrip error: `{summary['maxNativeRoundtripBoxErrorPx']}px`",
        f"- OVERDOSE header glyph sequence: `{summary['overdoseHeaderGlyphSequence']}`",
        f"- OVERDOSE header-to-cluster centroid vector: `{summary['overdoseHeaderToClusterCentroid']}`",
        f"- Registration fingerprint: `{summary['sourceRegistrationFingerprint']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Pairwise Geometry",
        "",
        "| from | to | visual | line gap | corridor gap | dx | dy | distance px | angle image-y-down |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in pairwise:
        lines.append(
            f"| `{row['from']}` | `{row['to']}` | `{row['visualPair']}` | `{row['lineGap']}` | `{row['corridorGap']}` | "
            f"`{row['dx']}` | `{row['dy']}` | `{row['distancePx']}` | `{row['angleDegreesImageYDown']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as a source-validation fingerprint only.",
            "- It does not reopen folded/mirrored 3D geometry, bold-letter, highlight, or OVERDOSE layout selectors.",
            "- It gives future source comparison a stable geometry target: order, gaps, center-step signs, cluster size, and native rotate180 roundtrip.",
            "- Extraction remains blocked until source/provenance wording supplies R3 unit/order evidence.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("sourceRegistrationFingerprint:", summary["sourceRegistrationFingerprint"])
    print("maxNativeRoundtripCenterErrorPx:", summary["maxNativeRoundtripCenterErrorPx"])
    print("selectorUnlocked:", summary["selectorUnlocked"])


if __name__ == "__main__":
    main()
