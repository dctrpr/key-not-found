#!/usr/bin/env python3
"""Build a native-source coordinate bridge for the current source packet.

The investigation's working geometry is readable/upright, while the native
source_images extraction is 180 degrees rotated. This bounded pass packages the
current source-comparison benchmarks in both coordinate systems:

- locked active O4/B4/G5/O5 target boxes
- the C9/Y-K frame and reflected p78 frame on page 76
- the page-76 OVERDOSE header word and its measured glyph boxes

This is a future-source registration artifact only. It performs no OCR,
extraction, key derivation, hashing, seed/WIF checks, address checks, or broad
candidate generation.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_JSON = ROOT / "analysis_outputs/source_audit/page76_active_target_crop_completion/page76_active_target_crop_completion.json"
PRIORITY_JSON = ROOT / "analysis_outputs/source_audit/page76_priority_crop_pack/page76_priority_crop_pack.json"
C9_FRAME_JSON = ROOT / "analysis_outputs/source_audit/c9_frame_overdose_page_control/c9_frame_overdose_page_control.json"
C9_GLYPH_JSON = ROOT / "analysis_outputs/source_audit/c9_header_glyph_slot_gate/c9_header_glyph_slot_gate.json"
ARTICLE_JSON = ROOT / "analysis_outputs/3d_article_map/article_3d_map_data.json"
UPRIGHT_IMAGE = ROOT / "analysis_outputs/3d_article_map/page_76_upright.jpg"
NATIVE_IMAGE = ROOT / "analysis_outputs/source_images/magazine_page_76.jpg"

OUT = ROOT / "analysis_outputs/source_audit/source_packet_native_benchmark_bridge"
OUT.mkdir(parents=True, exist_ok=True)
OUT_JSON = OUT / "source_packet_native_benchmark_bridge.json"
OUT_MD = OUT / "source_packet_native_benchmark_bridge.md"
SHEET = OUT / "source_packet_native_benchmark_bridge_sheet.jpg"

OVERDOSE = "OVERDOSE"


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


def rot180_box(box: list[int | float], width: int, height: int) -> list[int]:
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    return [width - x1, height - y1, width - x0, height - y0]


def box_center(box: list[int | float]) -> list[float]:
    return [round((float(box[0]) + float(box[2])) / 2, 3), round((float(box[1]) + float(box[3])) / 2, 3)]


def box_size(box: list[int | float]) -> list[int]:
    return [int(round(float(box[2]) - float(box[0]))), int(round(float(box[3]) - float(box[1])))]


def in_bounds(box: list[int | float], width: int, height: int) -> bool:
    return 0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height


def find_header_geometry(article: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    page = next(row for row in article["pages"] if row["page"] == 76)
    word = next(row for row in page["words"] if row.get("token") == "overdose")
    chars = []
    for char in page["chars"]:
        if char.get("c") not in set(OVERDOSE):
            continue
        box = [float(v) for v in char["box"]]
        if box[0] >= word["box"][0] - 1 and box[2] <= word["box"][2] + 1 and abs(float(char["y"]) - word["center"][1]) <= 6:
            chars.append(
                {
                    "id": f"overdose_glyph_{len(chars) + 1}_{char['c']}",
                    "label": f"OVERDOSE glyph {len(chars) + 1} {char['c']}",
                    "kind": "overdose_glyph",
                    "uprightBox": [round(v, 2) for v in box],
                    "letter": char["c"],
                    "slotIndex": len(chars),
                }
            )
    chars = sorted(chars, key=lambda row: row["uprightBox"][0])
    sequence = "".join(row["letter"] for row in chars)
    if sequence != OVERDOSE:
        raise RuntimeError(f"page-76 OVERDOSE glyph sequence mismatch: {sequence}")
    header = {
        "id": "p76_overdose_header",
        "label": "p76 OVERDOSE header word",
        "kind": "overdose_header",
        "uprightBox": [round(float(v), 2) for v in word["box"]],
        "text": word["text"],
        "center": [round(float(v), 2) for v in word["center"]],
    }
    return header, chars


def build_rows(width: int, height: int) -> list[dict[str, Any]]:
    active = load_json(ACTIVE_JSON)
    priority = load_json(PRIORITY_JSON)
    c9_frame = load_json(C9_FRAME_JSON)
    article = load_json(ARTICLE_JSON)
    header, glyphs = find_header_geometry(article)

    rows: list[dict[str, Any]] = []
    for target in active["targets"]:
        rows.append(
            {
                "id": target["id"],
                "label": target["label"],
                "kind": "active_target",
                "visualState": target["visualState"],
                "pageLine": target["pageLine"],
                "corridorIndex": target["corridorIndex"],
                "uprightBox": [int(round(v)) for v in target["box"]],
            }
        )
    rows.append(
        {
            "id": "c9_yk_frame",
            "label": "C9/Y-K full frame",
            "kind": "source_frame",
            "uprightBox": [int(round(v)) for v in c9_frame["c9Frame"]],
            "xMirrorInvariant": c9_frame.get("mirrorCheck", {}).get("xMirrorInvariant"),
        }
    )
    rows.append(
        {
            "id": "p78_reflected_frame_on_p76",
            "label": "reflected p78 frame on p76",
            "kind": "source_frame",
            "uprightBox": [int(round(v)) for v in priority["reflectedP78FrameOnP76"]],
        }
    )
    rows.append(header)
    rows.extend(glyphs)

    for row in rows:
        row["nativeBox"] = rot180_box(row["uprightBox"], width, height)
        row["uprightCenter"] = box_center(row["uprightBox"])
        row["nativeCenter"] = box_center(row["nativeBox"])
        row["boxSize"] = box_size(row["uprightBox"])
        row["uprightInBounds"] = in_bounds(row["uprightBox"], width, height)
        row["nativeInBounds"] = in_bounds(row["nativeBox"], width, height)
    return rows


def draw_overlay(image: Image.Image, rows: list[dict[str, Any]], coord_key: str, title: str, box_filter: set[str]) -> Image.Image:
    img = image.copy().convert("RGB")
    draw = ImageDraw.Draw(img)
    title_font = font(32)
    label_font = font(20)
    palette = {
        "active_target": "#ff9b2e",
        "source_frame": "#64d6ff",
        "overdose_header": "#f4e45c",
        "overdose_glyph": "#ffffff",
    }
    draw.rectangle([24, 22, 940, 78], fill=(12, 15, 20))
    draw.text((42, 34), title, fill=(241, 246, 251), font=title_font)
    for row in rows:
        if row["kind"] not in box_filter:
            continue
        box = row[coord_key]
        color = palette.get(row["kind"], "#ffffff")
        width = 6 if row["kind"] == "source_frame" else 4
        draw.rectangle(box, outline=color, width=width)
        if row["kind"] != "overdose_glyph":
            draw.text((box[0], max(0, box[1] - 25)), row["id"], fill=color, font=label_font)
    return img


def render_sheet(upright: Image.Image, native: Image.Image, rows: list[dict[str, Any]]) -> None:
    native_rot180 = native.rotate(180)
    lower_crop = [250, 2050, 2315, 3065]
    header_crop = [2050, 110, 2350, 230]
    header_crop_native = rot180_box(header_crop, upright.width, upright.height)
    lower_crop_native = rot180_box(lower_crop, upright.width, upright.height)

    lower_filter = {"active_target", "source_frame"}
    header_filter = {"overdose_header", "overdose_glyph"}
    panels = [
        (
            "upright lower benchmarks",
            draw_overlay(upright, rows, "uprightBox", "readable/upright lower benchmarks", lower_filter).crop(lower_crop),
        ),
        (
            "native lower rotated back",
            draw_overlay(native, rows, "nativeBox", "native lower benchmarks", lower_filter).crop(lower_crop_native).rotate(180),
        ),
        (
            "upright OVERDOSE glyphs",
            draw_overlay(upright, rows, "uprightBox", "readable/upright OVERDOSE", header_filter).crop(header_crop),
        ),
        (
            "native OVERDOSE rotated back",
            draw_overlay(native, rows, "nativeBox", "native OVERDOSE", header_filter).crop(header_crop_native).rotate(180),
        ),
    ]

    margin = 26
    gap = 20
    label_h = 34
    panel_w = 620
    rendered = []
    for label, image in panels:
        scale = min(panel_w / image.width, 1.0)
        rendered.append((label, image.resize((int(image.width * scale), int(image.height * scale)))))
    columns = 2
    rows_count = 2
    cell_h = max(img.height for _, img in rendered[:2]) + label_h
    header_cell_h = max(img.height for _, img in rendered[2:]) + label_h
    sheet_w = margin * 2 + columns * panel_w + gap
    sheet_h = margin * 2 + cell_h + header_cell_h + gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 13, 18))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    for i, (label, image) in enumerate(rendered):
        col = i % columns
        row = i // columns
        x = margin + col * (panel_w + gap)
        y = margin + (cell_h + gap) * row if row == 0 else margin + cell_h + gap
        draw.text((x, y), label, fill=(238, 242, 247), font=label_font)
        sheet.paste(image, (x, y + label_h))
    sheet.save(SHEET, quality=94)


def diff_summary(upright: Image.Image, native: Image.Image) -> dict[str, Any]:
    direct = np.asarray(ImageChops.difference(upright, native), dtype=np.uint8)
    rot = np.asarray(ImageChops.difference(upright, native.rotate(180)), dtype=np.uint8)
    return {
        "directMeanAbsDiff": round(float(direct.mean()), 4),
        "directMaxDiff": int(direct.max()),
        "rot180MeanAbsDiff": round(float(rot.mean()), 4),
        "rot180MaxDiff": int(rot.max()),
        "rot180NonzeroPct": round(float((rot > 0).mean() * 100), 4),
    }


def main() -> None:
    upright = Image.open(UPRIGHT_IMAGE).convert("RGB")
    native = Image.open(NATIVE_IMAGE).convert("RGB")
    if upright.size != native.size:
        raise RuntimeError(f"size mismatch: upright={upright.size} native={native.size}")
    width, height = upright.size
    rows = build_rows(width, height)
    render_sheet(upright, native, rows)

    c9_glyph = load_json(C9_GLYPH_JSON)
    active_rows = [row for row in rows if row["kind"] == "active_target"]
    frame_rows = [row for row in rows if row["kind"] == "source_frame"]
    glyph_rows = [row for row in rows if row["kind"] == "overdose_glyph"]
    result = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "scope": "source-packet native coordinate benchmark bridge; no OCR, extraction, key derivation, hashing, seed/WIF checks, address checks, or broad candidate generation",
        "inputs": {
            "activeTargets": rel(ACTIVE_JSON),
            "priorityCropPack": rel(PRIORITY_JSON),
            "c9FrameOverdosePageControl": rel(C9_FRAME_JSON),
            "c9HeaderGlyphSlotGate": rel(C9_GLYPH_JSON),
            "article3dMap": rel(ARTICLE_JSON),
            "uprightImage": rel(UPRIGHT_IMAGE),
            "nativeImage": rel(NATIVE_IMAGE),
        },
        "transform": "rotate180",
        "imageSize": [width, height],
        "imageDiff": diff_summary(upright, native),
        "rows": rows,
        "summary": {
            "benchmarkBoxCount": len(rows),
            "activeTargetCount": len(active_rows),
            "sourceFrameCount": len(frame_rows),
            "overdoseGlyphBoxCount": len(glyph_rows),
            "allUprightBoxesInBounds": all(row["uprightInBounds"] for row in rows),
            "allNativeBoxesInBounds": all(row["nativeInBounds"] for row in rows),
            "activePageLines": " ".join(str(row["pageLine"]) for row in active_rows),
            "activeCorridorIndexes": " ".join(str(row["corridorIndex"]) for row in active_rows),
            "activeVisualStateOrder": "".join(row["visualState"] for row in active_rows),
            "c9FrameXMirrorInvariant": next(
                (row.get("xMirrorInvariant") for row in frame_rows if row["id"] == "c9_yk_frame"),
                None,
            ),
            "headerGlyphSequence": "".join(row["letter"] for row in glyph_rows),
            "headerGlyphMaxEdgeDeltaVsEqualSlotPx": c9_glyph.get("summary", {}).get(
                "maxAbsEdgeDeltaVsEqualSlotPx"
            ),
            "selectorUnlocked": False,
        },
        "decision": {
            "sourcePacketNativeBenchmarkBridge": "source-registration-only",
            "reason": (
                "The active quartet, C9/Y-K frame, reflected p78 frame, and OVERDOSE header glyph boxes all have clean native-source coordinates after rotate180, "
                "but this adds only future source-comparison scaffolding, not an extraction unit or order."
            ),
        },
        "sheet": rel(SHEET),
        "nextMove": (
            "Use this bridge when comparing any physical scan, original layout export, or fresh PDF extraction: first normalize orientation, then require R3 unit/order wording before any selector/key test."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Source Packet Native Benchmark Bridge",
        "",
        "Scope: package the active page-76 source-comparison benchmarks in both readable/upright and native source coordinates. No OCR, extraction, key derivation, hashing, WIF, seed, address, BIP39, or broad brute-force checks were run.",
        "",
        f"- Created: `{result['createdAt']}`",
        f"- Transform: `{result['transform']}`",
        f"- Image size: `{width}x{height}`",
        f"- Native rotated 180 vs upright mean abs diff: `{result['imageDiff']['rot180MeanAbsDiff']}`; max diff `{result['imageDiff']['rot180MaxDiff']}`; nonzero `{result['imageDiff']['rot180NonzeroPct']}%`",
        f"- Direct native vs upright mean abs diff: `{result['imageDiff']['directMeanAbsDiff']}`; max diff `{result['imageDiff']['directMaxDiff']}`",
        f"- Benchmark boxes: `{result['summary']['benchmarkBoxCount']}`",
        f"- Active page lines: `{result['summary']['activePageLines']}`",
        f"- Active corridor indexes: `{result['summary']['activeCorridorIndexes']}`",
        f"- Active visual-state order: `{result['summary']['activeVisualStateOrder']}`",
        f"- C9 frame x-mirror invariant: `{result['summary']['c9FrameXMirrorInvariant']}`",
        f"- OVERDOSE glyph sequence: `{result['summary']['headerGlyphSequence']}`",
        f"- Header glyph max edge delta vs equal slots: `{result['summary']['headerGlyphMaxEdgeDeltaVsEqualSlotPx']}` px",
        f"- All native boxes in bounds: `{result['summary']['allNativeBoxesInBounds']}`",
        f"- Sheet: `{result['sheet']}`",
        "",
        "## Coordinate Rows",
        "",
        "| id | kind | upright box | native source box | size |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['id']}` | `{row['kind']}` | `{row['uprightBox']}` | `{row['nativeBox']}` | `{row['boxSize']}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Keep this as source-registration scaffolding only.",
            "- The bridge makes future physical/original-layout comparisons less ambiguous, but it does not supply a selector, unit, or order.",
            "- Any future source match still needs R3 wording or equivalent source evidence before extraction resumes.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {SHEET}")
    print("benchmarkBoxCount:", result["summary"]["benchmarkBoxCount"])
    print("activePageLines:", result["summary"]["activePageLines"])
    print("headerGlyphSequence:", result["summary"]["headerGlyphSequence"])
    print("selectorUnlocked:", result["summary"]["selectorUnlocked"])


if __name__ == "__main__":
    main()
